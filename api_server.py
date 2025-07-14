"""FastAPI backend server for the AI Tutoring System."""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any, Union
import asyncio
from datetime import datetime

# Import existing modules
from memory import load_user, save_user, get_weak_areas, get_recommended_review_topics, get_performance_summary, record_learning_session
from planner import PlannerAgent
from domain_expert import (
    generate_question, check_answer, show_available_sources, get_llm_info, 
    set_llm_provider, explain_concept, generate_example, generate_summary,
    query_domain_expert, retrieve_context_with_citations, generate_hint
)
from interactive_session import InteractiveSession, Command
from enhanced_memory import EnhancedMemorySystem
from llm_providers import llm_manager

app = FastAPI(title="AI Tutoring System API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://10.165.77.250:3000",  # Server IP
        "*"  # Allow all origins for development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class UserCreate(BaseModel):
    username: str

class QuestionRequest(BaseModel):
    topic: str
    previous_questions: List[str] = []
    difficulty: str = "medium"
    question_type: str = "conceptual"

class Question(BaseModel):
    text: str
    type: str
    options: Optional[List[str]] = []
    correct_option: Optional[int] = 0
    explanation: Optional[str] = ""

class AnswerRequest(BaseModel):
    question: Question
    answer: str

class LearningSessionRequest(BaseModel):
    username: str
    topic: str
    subtopics_performance: List[Dict[str, Any]]
    final_score: float
    mastery_level: str

class ConceptRequest(BaseModel):
    topic: str
    detail_level: str = "standard"

class ExampleRequest(BaseModel):
    topic: str
    difficulty: str = "medium"

class LLMProviderRequest(BaseModel):
    provider: str

class APIKeyRequest(BaseModel):
    provider: str
    api_key: str

class ChatMessage(BaseModel):
    message: str
    username: str
    context: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    citations: Optional[List[str]] = None
    suggestions: Optional[List[str]] = None
    context: Optional[str] = None

class CommandRequest(BaseModel):
    command: str
    args: Optional[str] = ""
    username: str
    topic: Optional[str] = None

# Review session models
class ReviewSessionRequest(BaseModel):
    username: str
    mode: str  # 'adaptive', 'intensive', 'spaced', 'quick', 'flashcards'
    topics: Optional[List[str]] = []
    adaptive: bool = False

class ReviewAnswerRequest(BaseModel):
    question_id: Any
    answer: str
    time_spent: Optional[int] = None
    
    def __init__(self, **data):
        print(f"DEBUG: ReviewAnswerRequest.__init__ called with data: {data}")
        super().__init__(**data)

class FlashcardReviewRequest(BaseModel):
    session_id: str
    card_id: str
    quality: int  # 0-5 rating
    time_spent: Optional[int] = None

class SessionState(BaseModel):
    session_id: str
    mode: str
    current_topic: Optional[str] = None
    difficulty: str = "medium"
    consecutive_correct: int = 0
    consecutive_wrong: int = 0
    total_questions: int = 0
    total_correct: int = 0
    session_state: str = "active"  # active, paused, completed
    performance: List[Dict[str, Any]] = []
    focus_areas: List[Dict[str, Any]] = []
    due_items: List[Dict[str, Any]] = []

# Global storage for active sessions (in production, use Redis or similar)
active_sessions = {}
chat_histories = {}  # Store chat histories per user
review_sessions = {}  # Store review sessions

@app.get("/")
async def root():
    return {"message": "AI Tutoring System API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/test-enhanced-memory/{username}")
async def test_enhanced_memory(username: str):
    """Test endpoint to check if EnhancedMemorySystem works."""
    try:
        print(f"Testing EnhancedMemorySystem for user: {username}")
        enhanced_memory = EnhancedMemorySystem(username)
        print("EnhancedMemorySystem created successfully")
        
        insights = enhanced_memory.get_insights()
        print(f"Insights received: {type(insights)}")
        
        return {
            "success": True,
            "message": "EnhancedMemorySystem works",
            "insights_type": str(type(insights))
        }
    except Exception as e:
        print(f"Error testing EnhancedMemorySystem: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "message": "EnhancedMemorySystem failed"
        }

# User management endpoints
@app.post("/api/users/create")
async def create_user(user: UserCreate):
    """Create a new user profile."""
    try:
        profile = load_user(user.username)
        agent = PlannerAgent(user.username)
        suggested_mode = agent.suggest_mode()
        
        return {
            "username": user.username,
            "profile": profile,
            "suggested_mode": suggested_mode,
            "success": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/users/{username}/profile")
async def get_user_profile(username: str):
    """Get user profile and performance data."""
    try:
        profile = load_user(username)
        performance = get_performance_summary(username)
        weak_areas = get_weak_areas(username)
        recommended_topics = get_recommended_review_topics(username, limit=5)
        
        return {
            "profile": profile,
            "performance": performance,
            "weak_areas": weak_areas,
            "recommended_topics": recommended_topics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/users/{username}/insights")
async def get_user_insights(username: str):
    """Get detailed learning insights and analytics."""
    try:
        enhanced_memory = EnhancedMemorySystem(username)
        insights = enhanced_memory.get_insights()
        return insights
    except Exception as e:
        print(f"Error getting user insights: {e}")
        import traceback
        traceback.print_exc()
        # Return basic structure if enhanced memory fails
        return {
            "personalized_recommendations": {
                "focus_areas": [],
                "spaced_repetition_schedule": []
            },
            "performance_summary": {
                "total_topics_studied": 0,
                "topics_mastered": 0,
                "weak_areas_count": 0
            }
        }

# Learning content endpoints
@app.post("/api/content/explain")
async def explain_concept_endpoint(request: ConceptRequest):
    """Get explanation for a concept."""
    try:
        explanation = explain_concept(request.topic, request.detail_level)
        return {"explanation": explanation, "topic": request.topic}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/content/example")
async def generate_example_endpoint(request: ExampleRequest):
    """Generate an example for a topic."""
    try:
        example = generate_example(request.topic, request.difficulty)
        return {"example": example, "topic": request.topic}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/content/question")
async def generate_question_endpoint(request: QuestionRequest):
    """Generate a question for a topic."""
    try:
        question = generate_question(
            request.topic, 
            request.previous_questions,
            request.difficulty,
            request.question_type
        )
        return {"question": question, "topic": request.topic}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/content/check-answer")
async def check_answer_endpoint(request: AnswerRequest):
    """Check if an answer is correct."""
    try:
        print(f"Received question: {request.question}")
        print(f"Received answer: {request.answer}")
        print(f"Question type: {type(request.question)}")
        print(f"Answer type: {type(request.answer)}")
        # Convert Question model to dict for check_answer function
        question_dict = request.question.dict()
        correct, feedback = check_answer(question_dict, request.answer)
        return {"correct": correct, "feedback": feedback}
    except Exception as e:
        print(f"Error in check_answer_endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/content/summary/{topic}")
async def get_summary(topic: str, length: str = "medium"):
    """Get a summary of a topic."""
    try:
        summary = generate_summary(topic, length)
        return {"summary": summary, "topic": topic}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Learning session endpoints
@app.get("/api/learning/{username}/plan/{topic}")
async def get_learning_plan(username: str, topic: str):
    """Get a learning plan for a topic."""
    try:
        agent = PlannerAgent(username)
        plan = agent.build_learning_plan(topic)
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/learning/record-session")
async def record_session(request: LearningSessionRequest):
    """Record a learning session."""
    try:
        record_learning_session(
            request.username,
            request.topic,
            request.subtopics_performance,
            request.final_score,
            request.mastery_level
        )
        return {"success": True, "message": "Session recorded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Interactive session endpoints
@app.post("/api/sessions/{username}/start/{topic}")
async def start_interactive_session(username: str, topic: str):
    """Start an interactive learning session."""
    try:
        session_id = f"{username}_{topic}_{datetime.now().timestamp()}"
        session = InteractiveSession(username, topic)
        active_sessions[session_id] = session
        
        # Get initial content
        plan = PlannerAgent(username).build_learning_plan(topic)
        
        return {
            "session_id": session_id,
            "topic": topic,
            "plan": plan,
            "status": "started"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sessions/{session_id}/status")
async def get_session_status(session_id: str):
    """Get the status of an interactive session."""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    return {
        "session_id": session_id,
        "username": session.username,
        "topic": session.topic,
        "status": "active"
    }

@app.delete("/api/sessions/{session_id}")
async def end_session(session_id: str):
    """End an interactive session."""
    if session_id in active_sessions:
        del active_sessions[session_id]
    return {"success": True, "message": "Session ended"}

# Document and source management
@app.get("/api/sources")
async def get_sources():
    """Get available document sources."""
    try:
        sources_info = show_available_sources()
        return {"sources": sources_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# LLM management endpoints
@app.get("/api/llm/providers")
async def get_llm_providers():
    """Get available LLM providers and their status."""
    try:
        providers = get_llm_info()
        return {"providers": providers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/llm/set-provider")
async def set_provider(request: LLMProviderRequest):
    """Set the active LLM provider."""
    try:
        success = set_llm_provider(request.provider)
        return {"success": success, "provider": request.provider}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/llm/add-key")
async def add_api_key(request: APIKeyRequest):
    """Add an API key for a provider."""
    try:
        llm_manager.add_api_key(request.provider, request.api_key)
        return {"success": True, "message": f"API key added for {request.provider}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/llm/test/{provider}")
async def test_provider(provider: str):
    """Test a specific LLM provider."""
    try:
        result = llm_manager.test_provider(provider)
        return {"success": result, "provider": provider}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Chat API endpoints
@app.post("/api/chat/message")
async def send_chat_message(message: ChatMessage):
    """Send a message to the chatbot and get a response."""
    try:
        # Initialize chat history for user if not exists
        if message.username not in chat_histories:
            chat_histories[message.username] = []
        
        # Get context from RAG system
        context, citations = retrieve_context_with_citations(message.message)
        
        # Generate response using domain expert
        response = query_domain_expert(
            f"You are a helpful AI tutor. Answer this question conversationally: {message.message}",
            context,
            citations
        )
        
        # Generate suggestions for follow-up questions
        suggestions = []
        if context:
            suggestion_prompt = f"Based on the topic '{message.message}', suggest 3 short follow-up questions a student might want to ask. Return as a simple list."
            suggestions_text = query_domain_expert(suggestion_prompt, context, citations, temperature=0.8)
            # Parse suggestions (simple implementation)
            suggestions = [s.strip('- ').strip() for s in suggestions_text.split('\n') if s.strip() and s.strip().startswith('-')][:3]
        
        # Store in chat history
        chat_histories[message.username].append({
            "type": "user",
            "message": message.message,
            "timestamp": datetime.now().isoformat()
        })
        chat_histories[message.username].append({
            "type": "assistant",
            "message": response,
            "citations": citations,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep chat history manageable (last 50 messages)
        if len(chat_histories[message.username]) > 50:
            chat_histories[message.username] = chat_histories[message.username][-50:]
        
        return ChatResponse(
            response=response,
            citations=citations,
            suggestions=suggestions,
            context=context[:200] + "..." if context and len(context) > 200 else context
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat/{username}/history")
async def get_chat_history(username: str, limit: int = 20):
    """Get chat history for a user."""
    try:
        history = chat_histories.get(username, [])
        # Return last 'limit' messages
        return {"history": history[-limit:] if limit > 0 else history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/chat/{username}/history")
async def clear_chat_history(username: str):
    """Clear chat history for a user."""
    try:
        if username in chat_histories:
            del chat_histories[username]
        return {"success": True, "message": "Chat history cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/command")
async def execute_chat_command(command_req: CommandRequest):
    """Execute interactive commands from chat interface."""
    try:
        # Parse command
        if not command_req.command.startswith('!'):
            return {"error": "Commands must start with !"}
        
        # Map command to response
        if command_req.command == "!help":
            help_text = """Available commands:
• !help - Show this help
• !explain <topic> - Get detailed explanation
• !example <topic> - Get an example
• !question <topic> - Generate a practice question
• !hint - Get a hint (use after asking a question)
• !sources - Show available documents
• !quiz <topic> - Start a quick quiz
• !progress - View your learning progress
• !difficulty <easy/medium/hard> - Set difficulty level"""
            return {"response": help_text, "type": "help"}
        
        elif command_req.command == "!explain":
            if not command_req.args:
                return {"error": "Please specify a topic to explain. Usage: !explain <topic>"}
            explanation = explain_concept(command_req.args, "standard")
            return {"response": explanation, "type": "explanation", "topic": command_req.args}
        
        elif command_req.command == "!example":
            if not command_req.args:
                return {"error": "Please specify a topic for example. Usage: !example <topic>"}
            example = generate_example(command_req.args, "medium")
            return {"response": example, "type": "example", "topic": command_req.args}
        
        elif command_req.command == "!question":
            if not command_req.args:
                return {"error": "Please specify a topic for question. Usage: !question <topic>"}
            question = generate_question(command_req.args, [], "medium", "conceptual")
            return {"response": question, "type": "question", "topic": command_req.args}
        
        elif command_req.command == "!hint":
            if not command_req.topic:
                return {"error": "No active question to provide hint for"}
            hint = generate_hint(f"question about {command_req.topic}", 2)
            return {"response": hint, "type": "hint"}
        
        elif command_req.command == "!sources":
            sources = show_available_sources()
            return {"response": sources, "type": "sources"}
        
        elif command_req.command == "!quiz":
            if not command_req.args:
                return {"error": "Please specify a topic for quiz. Usage: !quiz <topic>"}
            # Generate first question of a quiz
            question = generate_question(command_req.args, [], "medium", "conceptual")
            return {
                "response": f"Quiz started on {command_req.args}!\n\nQuestion 1: {question}",
                "type": "quiz_start",
                "topic": command_req.args,
                "question": question
            }
        
        elif command_req.command == "!progress":
            if not command_req.username:
                return {"error": "Username required for progress"}
            insights = EnhancedMemorySystem(command_req.username).get_insights()
            performance = insights['performance_summary']
            progress_text = f"""Your Learning Progress:
• Topics studied: {performance['topics_studied']}
• Average mastery: {performance['average_mastery']:.1%}
• Study streak: {performance['study_streak']} days
• Weak areas: {performance['weak_areas_count']}"""
            return {"response": progress_text, "type": "progress"}
        
        else:
            return {"error": f"Unknown command: {command_req.command}"}
    
    except Exception as e:
        return {"error": f"Command failed: {str(e)}"}

@app.post("/api/chat/quiz/answer")
async def submit_quiz_answer(request: AnswerRequest):
    """Submit answer for quiz question."""
    try:
        # Convert Question model to dict for check_answer function
        question_dict = request.question.dict()
        correct, feedback = check_answer(question_dict, request.answer)
        return {
            "correct": correct,
            "feedback": feedback,
            "type": "quiz_answer"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat/suggestions/{username}")
async def get_chat_suggestions(username: str):
    """Get personalized chat suggestions based on user's learning history."""
    try:
        # Get user's weak areas and recent topics
        weak_areas = get_weak_areas(username)
        profile = load_user(username)
        recent_topics = [session['topic'] for session in profile.get('history', [])[-3:]]
        
        suggestions = []
        
        # Add suggestions based on weak areas
        for area in weak_areas[:3]:
            suggestions.append(f"Help me understand {area}")
            suggestions.append(f"What are the key concepts in {area}?")
        
        # Add general learning suggestions
        suggestions.extend([
            "Explain the difference between similar concepts",
            "Give me a practical example",
            "Create a quiz for me",
            "Summarize what I've learned so far"
        ])
        
        return {"suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Review session endpoints
@app.post("/api/review/session/start")
async def start_review_session(request: ReviewSessionRequest):
    """Start a new review session with enhanced memory integration."""
    try:
        session_id = f"review_{request.username}_{datetime.now().isoformat()}"
        
        # Try to get enhanced memory insights, fallback to basic data if it fails
        try:
            enhanced_memory = EnhancedMemorySystem(request.username)
            insights = enhanced_memory.get_insights()
            recommendations = insights.get('personalized_recommendations', {})
            
            # Get performance summary
            summary = get_performance_summary(request.username)
            
            # Check for due spaced repetition items
            spaced_schedule = recommendations.get('spaced_repetition_schedule', [])
            due_items = [item for item in spaced_schedule if item.get('days_until_review', 0) <= 0]
            
            # Get focus areas from enhanced memory
            focus_areas = recommendations.get('focus_areas', [])
        except Exception as enhanced_error:
            print(f"Enhanced memory failed, using fallback: {enhanced_error}")
            # Fallback to basic data
            insights = {
                'personalized_recommendations': {
                    'focus_areas': [],
                    'spaced_repetition_schedule': []
                }
            }
            summary = {
                'total_topics_studied': 0,
                'topics_mastered': 0,
                'weak_areas_count': 0
            }
            due_items = []
            focus_areas = []
        
        # Create session state with all the data from main.py
        session_state = {
            "session_id": session_id,
            "username": request.username,
            "mode": request.mode,
            "current_topic": None,
            "difficulty": "medium",  # Will be adjusted based on past performance
            "consecutive_correct": 0,
            "consecutive_wrong": 0,
            "total_questions": 0,
            "total_correct": 0,
            "session_state": "active",
            "performance": [],
            "focus_areas": focus_areas,
            "due_items": due_items,
            "asked_questions": [],
            "started_at": datetime.now().isoformat(),
            "insights": insights,
            "summary": summary,
            "current_round": 0,
            "max_questions": 7 if request.mode == "adaptive" else 5,
            "adaptive": request.mode in ["adaptive", "intensive"]
        }
        
        active_sessions[session_id] = session_state
        
        return {
            "session_id": session_id,
            "mode": request.mode,
            "focus_areas": focus_areas,
            "due_items": due_items,
            "summary": summary,
            "message": f"Started {request.mode} review session"
        }
    except Exception as e:
        print(f"Error starting review session: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/review/adaptive")
async def start_adaptive_review(request: ReviewSessionRequest):
    """Start adaptive review session - AI adjusts difficulty based on performance."""
    try:
        session_id = f"adaptive_{request.username}_{datetime.now().isoformat()}"
        
        # Get enhanced memory insights
        try:
            enhanced_memory = EnhancedMemorySystem(request.username)
            insights = enhanced_memory.get_insights()
            recommendations = insights.get('personalized_recommendations', {})
            focus_areas = recommendations.get('focus_areas', [])
        except Exception as e:
            print(f"Enhanced memory failed: {e}")
            focus_areas = []
        
        if not focus_areas:
            # Fallback to default topics
            focus_areas = [
                {"topic": "GIS Basics", "subtopic": "Fundamentals", "priority_score": "high"},
                {"topic": "Coordinate Systems", "subtopic": "Projections", "priority_score": "medium"},
                {"topic": "Data Types", "subtopic": "Vector vs Raster", "priority_score": "medium"}
            ]
        
        session_state = {
            "session_id": session_id,
            "username": request.username,
            "mode": "adaptive",
            "current_topic": None,
            "difficulty": "medium",
            "consecutive_correct": 0,
            "consecutive_wrong": 0,
            "total_questions": 0,
            "total_correct": 0,
            "session_state": "active",
            "performance": [],
            "focus_areas": focus_areas,
            "asked_questions": [],
            "started_at": datetime.now().isoformat(),
            "current_round": 0,
            "max_questions": 7,
            "adaptive": True
        }
        
        active_sessions[session_id] = session_state
        
        return {
            "session_id": session_id,
            "mode": "adaptive",
            "focus_areas": focus_areas,
            "message": "Started adaptive review session"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/review/intensive")
async def start_intensive_review(request: ReviewSessionRequest):
    """Start intensive review session - Deep dive into specific weak areas."""
    try:
        session_id = f"intensive_{request.username}_{datetime.now().isoformat()}"
        
        # Get enhanced memory insights
        try:
            enhanced_memory = EnhancedMemorySystem(request.username)
            insights = enhanced_memory.get_insights()
            recommendations = insights.get('personalized_recommendations', {})
            focus_areas = recommendations.get('focus_areas', [])
        except Exception as e:
            print(f"Enhanced memory failed: {e}")
            focus_areas = []
        
        # Get highest priority area or use default
        if focus_areas:
            highest_priority = focus_areas[0]
            topic = highest_priority['topic']
        else:
            topic = "GIS Basics"
        
        # Set initial difficulty based on past performance
        try:
            profile = load_user(request.username)
            topic_mastery = profile.get('performance_data', {}).get(topic, {})
            avg_score = topic_mastery.get('average_score', 0.5)
            
            if avg_score >= 0.8:
                difficulty = "hard"
            elif avg_score >= 0.6:
                difficulty = "medium"
            else:
                difficulty = "easy"
        except:
            difficulty = "medium"
        
        session_state = {
            "session_id": session_id,
            "username": request.username,
            "mode": "intensive",
            "current_topic": topic,
            "difficulty": difficulty,
            "consecutive_correct": 0,
            "consecutive_wrong": 0,
            "total_questions": 0,
            "total_correct": 0,
            "session_state": "active",
            "performance": [],
            "focus_areas": focus_areas,
            "asked_questions": [],
            "started_at": datetime.now().isoformat(),
            "current_round": 0,
            "max_questions": 5,
            "adaptive": True
        }
        
        active_sessions[session_id] = session_state
        
        return {
            "session_id": session_id,
            "mode": "intensive",
            "topic": topic,
            "difficulty": difficulty,
            "focus_areas": focus_areas,
            "message": f"Started intensive review session on {topic}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/review/spaced")
async def start_spaced_review(request: ReviewSessionRequest):
    """Start spaced repetition review session."""
    try:
        session_id = f"spaced_{request.username}_{datetime.now().isoformat()}"
        
        # Get enhanced memory insights
        try:
            enhanced_memory = EnhancedMemorySystem(request.username)
            insights = enhanced_memory.get_insights()
            recommendations = insights.get('personalized_recommendations', {})
            spaced_schedule = recommendations.get('spaced_repetition_schedule', [])
            due_items = [item for item in spaced_schedule if item.get('days_until_review', 0) <= 0]
        except Exception as e:
            print(f"Enhanced memory failed: {e}")
            due_items = []
        
        if not due_items:
            # Fallback to default topics
            due_items = [
                {"topic": "GIS Basics", "subtopic": "Fundamentals", "days_until_review": 0, "priority": "high"},
                {"topic": "Coordinate Systems", "subtopic": "Projections", "days_until_review": 0, "priority": "medium"}
            ]
        
        session_state = {
            "session_id": session_id,
            "username": request.username,
            "mode": "spaced",
            "current_topic": None,
            "difficulty": "medium",
            "consecutive_correct": 0,
            "consecutive_wrong": 0,
            "total_questions": 0,
            "total_correct": 0,
            "session_state": "active",
            "performance": [],
            "due_items": due_items,
            "asked_questions": [],
            "started_at": datetime.now().isoformat(),
            "current_round": 0,
            "max_questions": len(due_items),
            "adaptive": False
        }
        
        active_sessions[session_id] = session_state
        
        return {
            "session_id": session_id,
            "mode": "spaced",
            "due_items": due_items,
            "message": f"Started spaced repetition review with {len(due_items)} due items"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/review/quick")
async def start_quick_review(request: ReviewSessionRequest):
    """Start quick review session - Rapid review of all weak areas."""
    try:
        session_id = f"quick_{request.username}_{datetime.now().isoformat()}"
        
        # Get enhanced memory insights
        try:
            enhanced_memory = EnhancedMemorySystem(request.username)
            insights = enhanced_memory.get_insights()
            recommendations = insights.get('personalized_recommendations', {})
            focus_areas = recommendations.get('focus_areas', [])
            weak_topics = [area['topic'] for area in focus_areas]
        except Exception as e:
            print(f"Enhanced memory failed: {e}")
            weak_topics = ["GIS Basics", "Coordinate Systems", "Data Types"]
        
        session_state = {
            "session_id": session_id,
            "username": request.username,
            "mode": "quick",
            "current_topic": None,
            "difficulty": "medium",
            "consecutive_correct": 0,
            "consecutive_wrong": 0,
            "total_questions": 0,
            "total_correct": 0,
            "session_state": "active",
            "performance": [],
            "focus_areas": focus_areas if 'focus_areas' in locals() else [],
            "weak_topics": weak_topics,
            "asked_questions": [],
            "started_at": datetime.now().isoformat(),
            "current_round": 0,
            "max_questions": min(5, len(weak_topics)),
            "adaptive": False
        }
        
        active_sessions[session_id] = session_state
        
        return {
            "session_id": session_id,
            "mode": "quick",
            "weak_topics": weak_topics,
            "message": f"Started quick review of {len(weak_topics)} weak areas"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/review/flashcards")
async def start_flashcard_review(request: ReviewSessionRequest):
    """Start flashcard review session."""
    try:
        session_id = f"flashcards_{request.username}_{datetime.now().isoformat()}"
        
        # Get enhanced memory insights
        try:
            enhanced_memory = EnhancedMemorySystem(request.username)
            insights = enhanced_memory.get_insights()
            recommendations = insights.get('personalized_recommendations', {})
            focus_areas = recommendations.get('focus_areas', [])
            topics = [area['topic'] for area in focus_areas]
        except Exception as e:
            print(f"Enhanced memory failed: {e}")
            topics = ["GIS Basics", "Coordinate Systems", "Data Types"]
        
        session_state = {
            "session_id": session_id,
            "username": request.username,
            "mode": "flashcards",
            "current_topic": None,
            "difficulty": "medium",
            "consecutive_correct": 0,
            "consecutive_wrong": 0,
            "total_questions": 0,
            "total_correct": 0,
            "session_state": "active",
            "performance": [],
            "topics": topics,
            "asked_questions": [],
            "started_at": datetime.now().isoformat(),
            "current_round": 0,
            "max_questions": 10,
            "adaptive": False
        }
        
        active_sessions[session_id] = session_state
        
        return {
            "session_id": session_id,
            "mode": "flashcards",
            "topics": topics,
            "message": f"Started flashcard review with {len(topics)} topics"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/review/session/{session_id}")
async def get_review_session(session_id: str):
    """Get current review session state."""
    try:
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = active_sessions[session_id]
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/review/session/{session_id}/pause")
async def pause_review_session(session_id: str):
    """Pause the review session."""
    try:
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        active_sessions[session_id]["session_state"] = "paused"
        active_sessions[session_id]["paused_at"] = datetime.now().isoformat()
        
        return {"message": "Session paused", "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/review/session/{session_id}/resume")
async def resume_review_session(session_id: str):
    """Resume the review session."""
    try:
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        active_sessions[session_id]["session_state"] = "active"
        if "paused_at" in active_sessions[session_id]:
            del active_sessions[session_id]["paused_at"]
        
        return {"message": "Session resumed", "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/review/session/{session_id}")
async def end_review_session(session_id: str):
    """End the review session and save results."""
    try:
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = active_sessions[session_id]
        session["session_state"] = "completed"
        session["completed_at"] = datetime.now().isoformat()
        
        # Calculate final results
        total_questions = session["total_questions"]
        total_correct = session["total_correct"]
        final_score = total_correct / total_questions if total_questions > 0 else 0
        
        # Determine mastery level based on difficulty and consistency
        high_difficulty_correct = sum(1 for perf in session["performance"] 
                                     if perf['correct'] and perf['difficulty'] in ['medium', 'hard'])
        
        if final_score >= 0.8 and high_difficulty_correct >= 2:
            mastery_level = 'mastered'
        elif final_score >= 0.6:
            mastery_level = 'intermediate'
        else:
            mastery_level = 'beginner'
        
        # Record the session with detailed performance data
        if session["performance"]:
            record_learning_session(
                username=session["username"],
                topic=f"{session['mode'].title()} Review Session",
                subtopics_performance=session["performance"],
                final_score=final_score,
                mastery_level=mastery_level
            )
        
        # Remove from active sessions
        del active_sessions[session_id]
        
        return {
            "message": "Session completed",
            "final_score": final_score,
            "mastery_level": mastery_level,
            "total_questions": total_questions,
            "total_correct": total_correct,
            "high_difficulty_correct": high_difficulty_correct
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/review/session/{session_id}/question")
async def get_next_question(session_id: str, topic: Optional[str] = None):
    """Get the next question for the review session with adaptive difficulty."""
    try:
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = active_sessions[session_id]
        session["current_round"] += 1
        
        # Determine topic and difficulty based on mode
        if session["mode"] == "adaptive":
            # Select topic based on priority and recent performance
            focus_areas = session["focus_areas"]
            if not focus_areas:
                # Fallback to default topics if no focus areas
                default_topics = ["GIS Basics", "Coordinate Systems", "Data Types", "Spatial Analysis"]
                topic = default_topics[session["current_round"] % len(default_topics)]
                session["current_topic"] = topic
            else:
                if session["current_round"] <= 3:
                    # First 3 questions: highest priority areas
                    current_area = focus_areas[min(session["current_round"]-1, len(focus_areas)-1)]
                else:
                    # Later questions: rotate through areas
                    current_area = focus_areas[(session["current_round"]-1) % len(focus_areas)]
                
                topic = current_area['topic']
                session["current_topic"] = topic
            
        elif session["mode"] == "intensive":
            if not topic:
                # Fallback to default topic for intensive mode
                topic = "GIS Basics"
            session["current_topic"] = topic
            
            # Set initial difficulty based on past performance
            profile = load_user(session["username"])
            topic_mastery = profile.get('performance_data', {}).get(topic, {})
            avg_score = topic_mastery.get('average_score', 0.5)
            
            if avg_score >= 0.8:
                session["difficulty"] = "hard"
            elif avg_score >= 0.6:
                session["difficulty"] = "medium"
            else:
                session["difficulty"] = "easy"
            
        elif session["mode"] == "spaced":
            # Use due items for spaced repetition
            due_items = session["due_items"]
            if not due_items:
                # Fallback to default topics if no due items
                default_topics = ["GIS Basics", "Coordinate Systems", "Data Types", "Spatial Analysis"]
                topic = default_topics[session["current_round"] % len(default_topics)]
                session["current_topic"] = topic
            else:
                current_item = due_items[session["total_questions"] % len(due_items)]
                topic = current_item["topic"]
                session["current_topic"] = topic
            
        elif session["mode"] == "quick":
            # Use weak topics for quick review
            weak_topics = [area["topic"] for area in session["focus_areas"]]
            if not weak_topics:
                # Fallback to default topics if no weak topics
                default_topics = ["GIS Basics", "Coordinate Systems", "Data Types", "Spatial Analysis"]
                topic = default_topics[session["current_round"] % len(default_topics)]
                session["current_topic"] = topic
            else:
                current_index = session["total_questions"] % len(weak_topics)
                topic = weak_topics[current_index]
                session["current_topic"] = topic
        
        # Generate question with current difficulty
        if not topic:
            raise HTTPException(status_code=400, detail="No topic available for question generation")
        
        # Extract question texts from asked_questions for generate_question
        previous_question_texts = []
        for q in session["asked_questions"]:
            if isinstance(q, dict) and "text" in q:
                previous_question_texts.append(q["text"])
            elif isinstance(q, str):
                previous_question_texts.append(q)
        
        question = generate_question(
            topic,
            previous_question_texts,
            session["difficulty"],
            "objective"
        )
        
        # Add to asked questions
        session["asked_questions"].append(question)
        
        return {
            "question": question,
            "topic": topic,
            "difficulty": session["difficulty"],
            "question_number": session["current_round"],
            "max_questions": session["max_questions"],
            "consecutive_correct": session["consecutive_correct"],
            "consecutive_wrong": session["consecutive_wrong"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/review/session/{session_id}/answer")
async def submit_review_answer(session_id: str, request: ReviewAnswerRequest):
    """Submit an answer for the current question with adaptive difficulty adjustment."""
    
    try:
        print(f"DEBUG: Received request for session {session_id}")
        print(f"DEBUG: Request data: {request.dict()}")
        
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = active_sessions[session_id]
        
        # Handle question_id - it could be a string or a question object
        if isinstance(request.question_id, dict):
            # If it's already a question object, use it directly
            question_dict = request.question_id
        else:
            # If it's a string, create a basic question dict
            question_dict = {
                "text": request.question_id.text,
                "type": "objective",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_option": 0,
                "explanation": "Question from review session."
            }
        
        correct, feedback = check_answer(question_dict, request.answer)
        
        # Update session state
        session["total_questions"] += 1
        if correct:
            session["total_correct"] += 1
            session["consecutive_correct"] += 1
            session["consecutive_wrong"] = 0
        else:
            session["consecutive_correct"] = 0
            session["consecutive_wrong"] += 1
        
        # Record performance with detailed data
        performance_entry = {
            'subtopic': f"{session['current_topic']} - Round {session['current_round']}",
            'question': question_dict.get('text', str(request.question_id)),
            'user_answer': request.answer,
            'correct': correct,
            'score': 1 if correct else 0,
            'feedback': feedback,
            'difficulty': session["difficulty"],
            'timestamp': datetime.now().isoformat(),
            'time_spent': request.time_spent
        }
        session["performance"].append(performance_entry)
        
        # Auto-create flashcard for correct answers at medium+ difficulty
        if correct and session["difficulty"] in ["medium", "hard"]:
            try:
                from flashcards import auto_create_flashcard_from_review
                auto_create_flashcard_from_review(
                    session["username"], 
                    session["current_topic"], 
                    str(question_dict.get('text', request.question_id)),
                    feedback.split('\n')[0] if '\n' in feedback else feedback,
                    session["difficulty"]
                )
            except ImportError:
                # Flashcard module not available, skip
                pass
        
        # Adaptive difficulty adjustment
        if session["adaptive"]:
            if session["consecutive_correct"] >= 2 and session["difficulty"] != "hard":
                if session["difficulty"] == "easy":
                    session["difficulty"] = "medium"
                elif session["difficulty"] == "medium":
                    session["difficulty"] = "hard"
                session["consecutive_correct"] = 0
            elif session["consecutive_wrong"] >= 2 and session["difficulty"] != "easy":
                if session["difficulty"] == "hard":
                    session["difficulty"] = "medium"
                elif session["difficulty"] == "medium":
                    session["difficulty"] = "easy"
                session["consecutive_wrong"] = 0
        
        return {
            "correct": correct,
            "feedback": feedback,
            "new_difficulty": session["difficulty"],
            "consecutive_correct": session["consecutive_correct"],
            "consecutive_wrong": session["consecutive_wrong"],
            "total_questions": session["total_questions"],
            "total_correct": session["total_correct"],
            "question_number": session["current_round"],
            "max_questions": session["max_questions"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 