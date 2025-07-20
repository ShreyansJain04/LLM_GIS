#!/usr/bin/env python3
"""Test script for the review API endpoints."""

import requests
import json
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:8000"

def test_review_insights():
    """Test getting review insights."""
    print("Testing review insights endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/review/insights/Ha")
        if response.status_code == 200:
            data = response.json()
            print("✅ Review insights endpoint working")
            print(f"Focus areas: {len(data.get('focus_areas', []))}")
            print(f"Due items: {len(data.get('due_items', []))}")
            return data
        else:
            print(f"❌ Review insights failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Review insights error: {e}")
        return None

def test_start_review_session():
    """Test starting a review session."""
    print("\nTesting start review session endpoint...")
    try:
        payload = {
            "username": "Ha",
            "mode": "adaptive",
            "topics": [],
            "adaptive": True
        }
        response = requests.post(f"{BASE_URL}/api/review/session/start", json=payload)
        if response.status_code == 200:
            data = response.json()
            print("✅ Start review session working")
            print(f"Session ID: {data.get('session_id')}")
            print(f"Mode: {data.get('mode')}")
            return data.get('session_id')
        else:
            print(f"❌ Start review session failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Start review session error: {e}")
        return None

def test_get_next_question(session_id):
    """Test getting the next question."""
    print(f"\nTesting get next question for session {session_id}...")
    try:
        response = requests.post(f"{BASE_URL}/api/review/session/{session_id}/question")
        if response.status_code == 200:
            data = response.json()
            print("✅ Get next question working")
            print(f"Topic: {data.get('topic')}")
            print(f"Difficulty: {data.get('difficulty')}")
            return data.get('question')
        else:
            print(f"❌ Get next question failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Get next question error: {e}")
        return None

def test_submit_answer(session_id, question):
    """Test submitting an answer."""
    print(f"\nTesting submit answer for session {session_id}...")
    try:
        # Extract question text from the question object
        question_text = question.get('text', str(question)) if isinstance(question, dict) else str(question)
        
        payload = {
            "session_id": session_id,
            "question_id": question_text,
            "answer": "0",
            "time_spent": 30
        }
        response = requests.post(f"{BASE_URL}/api/review/session/{session_id}/answer", json=payload)
        if response.status_code == 200:
            data = response.json()
            print("✅ Submit answer working")
            print(f"Correct: {data.get('correct')}")
            print(f"New difficulty: {data.get('new_difficulty')}")
            return data
        else:
            print(f"❌ Submit answer failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Submit answer error: {e}")
        return None

def test_end_session(session_id):
    """Test ending the session."""
    print(f"\nTesting end session {session_id}...")
    try:
        response = requests.delete(f"{BASE_URL}/api/review/session/{session_id}")
        if response.status_code == 200:
            data = response.json()
            print("✅ End session working")
            print(f"Final score: {data.get('final_score')}")
            print(f"Mastery level: {data.get('mastery_level')}")
            return data
        else:
            print(f"❌ End session failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ End session error: {e}")
        return None

def main():
    """Run all tests."""
    print("🧪 Testing Review API Endpoints")
    print("=" * 50)
    
    # Test 1: Get review insights
    insights = test_review_insights()
    if not insights:
        print("❌ Cannot proceed without insights")
        return
    
    # Test 2: Start review session
    session_id = test_start_review_session()
    if not session_id:
        print("❌ Cannot proceed without session")
        return
    
    # Test 3: Get next question
    question = test_get_next_question(session_id)
    if not question:
        print("❌ Cannot proceed without question")
        return
    
    # Test 4: Submit answer
    result = test_submit_answer(session_id, question)
    if not result:
        print("❌ Cannot proceed without answer result")
        return
    
    # Test 5: End session
    final_result = test_end_session(session_id)
    if not final_result:
        print("❌ Cannot proceed without end session result")
        return
    
    print("\n🎉 All tests completed successfully!")
    print("=" * 50)

if __name__ == "__main__":
    main() 