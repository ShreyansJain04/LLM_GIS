"""FastAPI backend server for the AI Tutoring System."""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
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
    previous_questions: Optional[List[str]] = []
    difficulty: str = "medium"
    question_type: str = "conceptual"

class AnswerRequest(BaseModel):
    question: str
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

# Global storage for active sessions (in production, use Redis or similar)
active_sessions = {}
chat_histories = {}  # Store chat histories per user

@app.get("/")
async def root():
    return {"message": "AI Tutoring System API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

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
        raise HTTPException(status_code=500, detail=str(e))

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
        correct, feedback = check_answer(request.question, request.answer)
        return {"correct": correct, "feedback": feedback}
    except Exception as e:
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
        correct, feedback = check_answer(request.question, request.answer)
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
        # Get user insights for personalized suggestions
        insights = EnhancedMemorySystem(username).get_insights()
        recommendations = insights.get('personalized_recommendations', {})
        
        suggestions = []
        
        # Add weak areas as suggestions
        weak_areas = recommendations.get('focus_areas', [])
        for area in weak_areas[:3]:
            suggestions.append(f"Help me understand {area['topic']}")
        
        # Add general learning suggestions
        suggestions.extend([
            "What should I study next?",
            "Show me my learning progress",
            "Give me a quick quiz",
            "Explain a concept I'm struggling with"
        ])
        
        return {"suggestions": suggestions[:6]}  # Limit to 6 suggestions
    except Exception as e:
        return {"suggestions": [
            "What should I study today?",
            "Help me with a specific topic",
            "Show me my progress",
            "Give me a practice question"
        ]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 