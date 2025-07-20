#!/usr/bin/env python3
"""Test script to verify spaced repetition fixes."""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_spaced_repetition():
    """Test the spaced repetition system."""
    username = "test_user"
    
    print("🧪 Testing Spaced Repetition System")
    print("=" * 50)
    
    # 1. Start spaced repetition session
    print("1. Starting spaced repetition session...")
    response = requests.post(f"{BASE_URL}/api/review/spaced", json={
        "username": username,
        "mode": "spaced"
    })
    
    if response.status_code != 200:
        print(f"❌ Failed to start session: {response.status_code}")
        print(response.text)
        return False
    
    session_data = response.json()
    session_id = session_data["session_id"]
    print(f"✅ Session started: {session_id}")
    print(f"   Due items: {len(session_data.get('due_items', []))}")
    
    # 2. Get first question/item
    print("\n2. Getting first question/item...")
    response = requests.post(f"{BASE_URL}/api/review/session/{session_id}/question")
    
    if response.status_code != 200:
        print(f"❌ Failed to get question: {response.status_code}")
        print(response.text)
        return False
    
    question_data = response.json()
    print(f"✅ Got item: {question_data.get('type', 'unknown')}")
    print(f"   Topic: {question_data.get('topic', 'unknown')}")
    
    # 3. Submit answer
    print("\n3. Submitting answer...")
    if question_data.get('type') == 'flashcard':
        # Flashcard - submit quality rating
        answer_data = {
            "question_id": question_data.get('card', {}).get('id', 'test'),
            "answer": "4"  # Good recall
        }
    else:
        # Question - submit answer
        answer_data = {
            "question_id": question_data.get('question', {}),
            "answer": "test answer"
        }
    
    response = requests.post(f"{BASE_URL}/api/review/session/{session_id}/answer", json=answer_data)
    
    if response.status_code != 200:
        print(f"❌ Failed to submit answer: {response.status_code}")
        print(response.text)
        return False
    
    answer_response = response.json()
    print(f"✅ Answer submitted: {answer_response.get('correct', 'unknown')}")
    print(f"   Total questions: {answer_response.get('total_questions', 0)}")
    print(f"   Total correct: {answer_response.get('total_correct', 0)}")
    
    # 4. Get session status
    print("\n4. Checking session status...")
    response = requests.get(f"{BASE_URL}/api/review/session/{session_id}")
    
    if response.status_code != 200:
        print(f"❌ Failed to get session: {response.status_code}")
        print(response.text)
        return False
    
    session_status = response.json()
    print(f"✅ Session status: {session_status.get('session_state', 'unknown')}")
    print(f"   Remaining due items: {len(session_status.get('due_items', []))}")
    
    # 5. End session
    print("\n5. Ending session...")
    response = requests.delete(f"{BASE_URL}/api/review/session/{session_id}")
    
    if response.status_code != 200:
        print(f"❌ Failed to end session: {response.status_code}")
        print(response.text)
        return False
    
    print("✅ Session ended successfully")
    
    print("\n🎉 All tests passed!")
    return True

if __name__ == "__main__":
    try:
        success = test_spaced_repetition()
        if success:
            print("\n✅ Spaced repetition system is working correctly!")
        else:
            print("\n❌ Spaced repetition system has issues!")
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()