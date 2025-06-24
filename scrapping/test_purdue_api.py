import requests
import json
import os

def test_purdue_api():
    """Test the Purdue GenAI API with a simple request"""
    
    # API configuration
    api_key = "sk-e94c63484a45419fb5703b29fd18e687"
    
    # Try different possible endpoints
    endpoints = [
        "https://genai.rcac.purdue.edu/api/chat/completions",
        "https://genai.rcac.purdue.edu/api/v1/chat/completions",
        "https://genai.rcac.purdue.edu/api/completions"
    ]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Simple test payload
    payload = {
        "model": "llama3.1:latest",
        "messages": [
            {
                "role": "user",
                "content": "Hello! Can you respond with just 'API is working'?"
            }
        ],
        "max_tokens": 50,
        "temperature": 0.1
    }
    
    print("🔍 Testing Purdue GenAI API...")
    print(f"🔑 API Key: {api_key[:10]}...{api_key[-4:]}")
    print(f"🤖 Model: {payload['model']}")
    print("-" * 50)
    
    for i, base_url in enumerate(endpoints, 1):
        print(f"\n🧪 Test {i}: {base_url}")
        
        try:
            print("📤 Sending request...")
            response = requests.post(base_url, headers=headers, json=payload, timeout=60)
            
            print(f"📥 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ SUCCESS! API is working!")
                result = response.json()
                print(f"🤖 Response: {json.dumps(result, indent=2)}")
                
                # Extract the actual response content
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
                    print(f"💬 AI Response: {content}")
                return True
                
            else:
                print(f"❌ ERROR: {response.status_code}")
                print(f"📄 Error Response: {response.text[:200]}...")
                
        except requests.exceptions.Timeout:
            print(f"⏰ TIMEOUT: Request timed out after 60 seconds")
        except requests.exceptions.ConnectionError as e:
            print(f"🔌 CONNECTION ERROR: {e}")
        except requests.exceptions.RequestException as e:
            print(f"❌ NETWORK ERROR: {e}")
        except json.JSONDecodeError as e:
            print(f"❌ JSON PARSE ERROR: {e}")
            print(f"📄 Raw Response: {response.text[:200]}...")
        except Exception as e:
            print(f"❌ UNEXPECTED ERROR: {e}")
    
    print("\n❌ All endpoints failed. API may be down or endpoint incorrect.")
    return False

def test_connectivity():
    """Test basic connectivity to the domain"""
    print("\n🌐 Testing basic connectivity...")
    
    try:
        # Test basic HTTP connectivity
        response = requests.get("https://genai.rcac.purdue.edu", timeout=10)
        print(f"✅ Basic connectivity: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Connectivity failed: {e}")
        return False

if __name__ == "__main__":
    # First test basic connectivity
    if test_connectivity():
        # Then test the API
        test_purdue_api()
    else:
        print("❌ Cannot reach the server. Check your internet connection.") 