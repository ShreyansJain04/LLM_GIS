import requests
import json

def test_model_formats():
    """Test different model name formats with the Purdue API"""
    
    api_key = "sk-e94c63484a45419fb5703b29fd18e687"
    base_url = "https://genai.rcac.purdue.edu/api/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Test different model name formats
    model_formats = [
        "llama3.1:latest",
        "llama3.1",
        "llama",
        "gpt-3.5-turbo",
        "gpt-4",
        "claude-3-sonnet"
    ]
    
    payload_template = {
        "messages": [
            {
                "role": "user",
                "content": "Hello! Just say 'working'."
            }
        ],
        "max_tokens": 10,
        "temperature": 0.1
    }
    
    print("🔍 Testing different model formats...")
    print("-" * 50)
    
    working_models = []
    
    for model in model_formats:
        print(f"\n🧪 Testing model: '{model}'")
        
        payload = payload_template.copy()
        payload["model"] = model
        
        try:
            response = requests.post(base_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                print(f"✅ SUCCESS with model: '{model}'")
                result = response.json()
                content = result['choices'][0]['message']['content']
                print(f"💬 Response: {content}")
                working_models.append(model)
            else:
                print(f"❌ FAILED: {response.status_code}")
                print(f"📄 Error: {response.text[:100]}...")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print(f"\n🎯 Working models: {working_models}")
    return working_models

if __name__ == "__main__":
    test_model_formats() 