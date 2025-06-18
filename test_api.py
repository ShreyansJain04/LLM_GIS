import os
from dotenv import load_dotenv
from openai import OpenAI

def test_openai_connection():
    # Load environment variables
    load_dotenv()
    
    # Initialize the OpenAI client
    client = OpenAI()
    
    try:
        # Make a simple API call
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, this is a test message."}
            ]
        )
        print("✅ Successfully connected to OpenAI API")
        print(f"Response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"❌ Failed to connect to OpenAI API: {str(e)}")

if __name__ == "__main__":
    test_openai_connection()

api_key = os.getenv("OPENAI_API_KEY") 