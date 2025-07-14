import requests
import json

# Test the fixed endpoint
url = "http://localhost:8000/api/review/session/adaptive_Ha_2025-07-14T01:55:47.047999/answer"

data = {
    "question_id": "What is GIS?",
    "answer": "0",
    "time_spent": 30
}

print("Testing fixed endpoint...")
print(f"Data: {json.dumps(data, indent=2)}")

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("Success! Response:")
        print(json.dumps(result, indent=2))
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Exception: {e}") 