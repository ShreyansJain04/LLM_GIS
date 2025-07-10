#!/usr/bin/env python3
"""Test script to debug LLM manager initialization."""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from llm_providers import llm_manager
    print("✅ LLM Manager imported successfully")
    
    print(f"\n📋 Available providers: {list(llm_manager.providers.keys())}")
    print(f"🎯 Active provider: {llm_manager.active_provider}")
    
    print("\n🔍 Provider details:")
    for name, provider in llm_manager.providers.items():
        print(f"  - {name}: {provider.get_info()}")
    
    print(f"\n📊 List providers result: {llm_manager.list_providers()}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 