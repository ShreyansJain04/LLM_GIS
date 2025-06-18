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
    set_llm_provider, explain_concept, generate_example, generate_summary
)
from interactive_session import InteractiveSession
from enhanced_memory import EnhancedMemorySystem
from llm_providers import llm_manager

app = FastAPI(title="AI Tutoring System API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
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

# Global storage for active sessions (in production, use Redis or similar)
active_sessions = {}

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 