import os
import getpass

def set_api_key():
    # Check if API key is already set in environment
    existing_key = os.environ.get("OPENAI_API_KEY")
    if existing_key:
        print("API key is already set in environment variable")
        return existing_key
    
    # Prompt user to enter their API key
    try:
        api_key = getpass.getpass("Enter your OpenAI API key (starts with sk-): ").strip()
        if not api_key:
            print("No API key provided!")
            return None
            
        if not api_key.startswith('sk-'):
            print("Warning: OpenAI API keys typically start with 'sk-'")
            confirm = input("Continue anyway? (y/N): ").strip().lower()
            if confirm != 'y':
                return None
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return None
    
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
    
    return api_key

if __name__ == "__main__":
    set_api_key() 