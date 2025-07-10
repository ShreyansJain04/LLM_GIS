#!/usr/bin/env python3
"""
Quick OpenAI API Test Script
Tests basic OpenAI API functionality including chat completions.
"""

import os
import openai
from openai import OpenAI
import json
import sys
import getpass

# ========================================
# CONFIGURATION - Put your API key here
# ========================================
# OPENAI_API_KEY = "YOUR_API_KEY_HERE"  # Put your OpenAI API key here (e.g., "sk-your-key-here")
OPENAI_API_KEY = "YOUR_API_KEY_HERE"
def get_api_key():
    """Get OpenAI API key from code, environment, or user input."""
    
    # Priority 1: Check if API key is set in the code
    if OPENAI_API_KEY and OPENAI_API_KEY.strip():
        print("✅ Found OpenAI API key in code configuration")
        return OPENAI_API_KEY.strip()
    
    # Priority 2: Check if API key is set in environment
    env_api_key = os.getenv('OPENAI_API_KEY')
    if env_api_key:
        print("✅ Found OpenAI API key in environment variable")
        return env_api_key
    
    # Priority 3: If not found, prompt user to enter it
    print("⚠️  No OpenAI API key found!")
    print("You can:")
    print("1. Add it to the OPENAI_API_KEY variable in this script")
    print("2. Set it as environment variable: export OPENAI_API_KEY='your-key'")
    print("3. Enter it now (it won't be saved)")
    print()
    
    try:
        api_key = getpass.getpass("🔑 Enter your OpenAI API key: ").strip()
        if not api_key:
            print("❌ No API key provided!")
            return None
        
        # Basic validation - OpenAI keys start with 'sk-'
        if not api_key.startswith('sk-'):
            print("⚠️  Warning: OpenAI API keys typically start with 'sk-'")
            confirm = input("Continue anyway? (y/N): ").strip().lower()
            if confirm != 'y':
                return None
        
        print("✅ API key received")
        return api_key
        
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        return None

def test_openai_api():
    """Test OpenAI API connection and basic functionality."""
    
    # Get API key
    api_key = get_api_key()
    if not api_key:
        return False
    
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)
        print("✅ OpenAI client initialized successfully")
        
        # Test 1: List available models
        print("\n🔍 Testing model listing...")
        try:
            models = client.models.list()
            gpt_models = [model.id for model in models.data if 'gpt' in model.id.lower()]
            print(f"✅ Found {len(gpt_models)} GPT models")
            print(f"Available GPT models: {gpt_models}")  # Show first 5
        except Exception as e:
            print(f"❌ Failed to list models: {e}")
            return False
        
        # Test 2: Simple chat completion
        print("\n💬 Testing chat completion...")
        try:
            response = client.chat.completions.create(
                model="gpt-4o-2024-08-06",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say 'Hello, OpenAI API is working!' in a creative way."}
                ],
                max_tokens=100,
                temperature=0.7
            )
            
            message = response.choices[0].message.content
            print(f"✅ Chat completion successful!")
            print(f"Response: {message}")
            
            # Display usage stats
            usage = response.usage
            print(f"📊 Usage - Prompt tokens: {usage.prompt_tokens}, "
                  f"Completion tokens: {usage.completion_tokens}, "
                  f"Total tokens: {usage.total_tokens}")
            
        except Exception as e:
            print(f"❌ Chat completion failed: {e}")
            return False
        
        # Test 3: Test with different model (if available)
        print("\n🚀 Testing with GPT-4 (if available)...")
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "user", "content": "What's 2+2? Answer briefly."}
                ],
                max_tokens=50
            )
            print(f"✅ GPT-4 test successful: {response.choices[0].message.content}")
        except Exception as e:
            print(f"⚠️  GPT-4 test failed (might not have access): {e}")
        
        print("\n🎉 OpenAI API tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API test failed: {e}")
        return False

def check_environment():
    """Check if required packages are installed."""
    try:
        import openai
        print(f"✅ OpenAI package version: {openai.__version__}")
    except ImportError:
        print("❌ OpenAI package not installed!")
        print("Install it with: pip install openai")
        return False
    return True

if __name__ == "__main__":
    print("🧪 OpenAI API Test Script")
    print("=" * 40)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Run tests
    success = test_openai_api()
    
    if success:
        print("\n✅ All tests passed! OpenAI API is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Check your API key and internet connection.")
        sys.exit(1) 