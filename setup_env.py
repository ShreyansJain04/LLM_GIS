import os
from dotenv import load_dotenv

def setup_environment():
    # Create .env file if it doesn't exist
    env_path = ".env"
    if not os.path.exists(env_path):
        with open(env_path, "w") as f:
            f.write("OPENAI_API_KEY=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\n")
    
    # Load the environment variables
    load_dotenv()
    
    # Verify the API key is set
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print("✅ OpenAI API key is properly set in environment")
    else:
        print("❌ Failed to set OpenAI API key")

if __name__ == "__main__":
    setup_environment() 