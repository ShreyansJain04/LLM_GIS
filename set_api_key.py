import os

def set_api_key():
    api_key = "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"
    
    # Set the environment variable
    os.environ["OPENAI_API_KEY"] = api_key
    
    # Also try to write to .env file
    try:
        with open(".env", "w") as f:
            f.write(f"OPENAI_API_KEY={api_key}\n")
        print("API key has been set in both environment variable and .env file")
    except Exception as e:
        print(f"Could not write to .env file: {e}")
        print("API key has been set in environment variable only")

if __name__ == "__main__":
    set_api_key() 