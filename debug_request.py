import requests
import json

# Test the exact request that the frontend is sending
url = "http://localhost:8000/api/review/session/adaptive_Ha_2025-07-14T01:55:47.047999/answer"

# Simulate what the frontend is sending
data = {
    "question_id": "What is GIS?",
    "answer": "0",
    "time_spent": 30
}

print("=== Frontend Request ===")
print(f"URL: {url}")
print(f"Method: POST")
print(f"Data: {json.dumps(data, indent=2)}")

try:
    response = requests.post(url, json=data)
    print(f"\n=== Response ===")
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    
    if response.status_code == 422:
        error_data = response.json()
        print(f"\n=== Validation Error ===")
        print(json.dumps(error_data, indent=2))
        
        # Analyze the error
        for error in error_data.get('detail', []):
            print(f"\nError Type: {error.get('type')}")
            print(f"Location: {error.get('loc')}")
            print(f"Message: {error.get('msg')}")
            print(f"Input: {error.get('input')}")
    else:
        print(f"Response Body: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")

# Also test with different data structures
print("\n" + "="*50)
print("=== Testing Different Data Structures ===")

test_cases = [
    {
        "name": "Only required fields",
        "data": {
            "question_id": "What is GIS?",
            "answer": "0"
        }
    },
    {
        "name": "With time_spent",
        "data": {
            "question_id": "What is GIS?",
            "answer": "0",
            "time_spent": 30
        }
    },
    {
        "name": "Empty answer",
        "data": {
            "question_id": "What is GIS?",
            "answer": ""
        }
    }
]

for test_case in test_cases:
    print(f"\n--- {test_case['name']} ---")
    try:
        response = requests.post(url, json=test_case['data'])
        print(f"Status: {response.status_code}")
        if response.status_code == 422:
            error = response.json()
            print(f"Error: {error['detail'][0]['msg']}")
    except Exception as e:
        print(f"Error: {e}") 