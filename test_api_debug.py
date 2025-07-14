import requests
import json

# Test the API with debug logging
url = "http://localhost:8000/api/review/session/adaptive_Ha_2025-07-14T01:55:47.047999/answer"

data = {
    "question_id": "What is GIS?",
    "answer": "0",
    "time_spent": 30
}

print("Testing API with debug logging...")
print(f"URL: {url}")
print(f"Data: {json.dumps(data, indent=2)}")

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 422:
        error_data = response.json()
        print("Validation Error:")
        print(json.dumps(error_data, indent=2))
    else:
        print(f"Success! Response: {response.text}")
        
except Exception as e:
    print(f"Error: {e}") 