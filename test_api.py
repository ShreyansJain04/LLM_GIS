import requests
import json

# Test the check-answer endpoint
url = "http://localhost:8000/api/content/check-answer"

# Test data
test_data = {
    "question": {
        "text": "What is GIS?",
        "type": "objective",
        "options": ["Geographic Information System", "Global Information System", "Graphical Information System", "Geographic Intelligence System"],
        "correct_option": 0,
        "explanation": "GIS stands for Geographic Information System."
    },
    "answer": "0"
}

try:
    response = requests.post(url, json=test_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 422:
        print("Validation error details:")
        error_data = response.json()
        print(json.dumps(error_data, indent=2))
        
except Exception as e:
    print(f"Error: {e}") 