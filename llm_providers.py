"""Multi-LLM Provider Support System."""
import os
import json
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
from pathlib import Path
import requests


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate a response from the LLM."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available."""
        pass
    
    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """Get information about the provider."""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI provider (GPT-4, GPT-3.5)."""
    
    def __init__(self, model: str = None, api_key: str = None):
        try:
            from openai import OpenAI
            self.client_class = OpenAI
        except ImportError:
            self.client_class = None
            
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY')
        self.model = model or os.environ.get('OPENAI_MODEL', 'gpt-4')
        self.client = None
        
        if self.api_key and self.client_class:
            self.client = self.client_class(api_key=self.api_key)
    
    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2000, **kwargs) -> str:
        """Generate response using OpenAI."""
        if not self.client:
            raise RuntimeError("OpenAI client not initialized")
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        return response.choices[0].message.content
    
    def is_available(self) -> bool:
        """Check if OpenAI is available."""
        return self.client is not None and self.api_key is not None
    
    def get_info(self) -> Dict[str, Any]:
        """Get OpenAI provider info."""
        return {
            "provider": "OpenAI",
            "model": self.model,
            "available": self.is_available(),
            "requires_api_key": True
        }


class DeepSeekProvider(LLMProvider):
    """DeepSeek provider."""
    
    def __init__(self, model: str = "deepseek-chat", api_key: str = None, base_url: str = None):
        self.api_key = api_key or os.environ.get('DEEPSEEK_API_KEY')
        self.model = model
        self.base_url = base_url or "https://api.deepseek.com/v1"
        
        # DeepSeek uses OpenAI-compatible API
        try:
            from openai import OpenAI
            if self.api_key:
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
            else:
                self.client = None
        except ImportError:
            self.client = None
    
    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2000, **kwargs) -> str:
        """Generate response using DeepSeek."""
        if not self.client:
            raise RuntimeError("DeepSeek client not initialized")
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        return response.choices[0].message.content
    
    def is_available(self) -> bool:
        """Check if DeepSeek is available."""
        return self.client is not None
    
    def get_info(self) -> Dict[str, Any]:
        """Get DeepSeek provider info."""
        return {
            "provider": "DeepSeek",
            "model": self.model,
            "available": self.is_available(),
            "requires_api_key": True,
            "base_url": self.base_url
        }


class OllamaProvider(LLMProvider):
    """Ollama provider for local models."""
    
    def __init__(self, model: str = "llama2", base_url: str = None):
        self.model = model
        self.base_url = base_url or "http://localhost:11434"
        
    def generate(self, prompt: str, temperature: float = 0.7, **kwargs) -> str:
        """Generate response using Ollama."""
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature,
            "stream": False,
            **kwargs
        }
        
        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()['response']
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ollama request failed: {e}")
    
    def is_available(self) -> bool:
        """Check if Ollama is available."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def list_models(self) -> List[str]:
        """List available Ollama models."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [model['name'] for model in models]
        except:
            pass
        return []
    
    def get_info(self) -> Dict[str, Any]:
        """Get Ollama provider info."""
        available_models = self.list_models() if self.is_available() else []
        return {
            "provider": "Ollama",
            "model": self.model,
            "available": self.is_available(),
            "requires_api_key": False,
            "base_url": self.base_url,
            "available_models": available_models
        }


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider."""
    
    def __init__(self, model: str = "claude-3-opus-20240229", api_key: str = None):
        try:
            import anthropic
            self.anthropic = anthropic
        except ImportError:
            self.anthropic = None
            
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        self.model = model
        self.client = None
        
        if self.api_key and self.anthropic:
            self.client = self.anthropic.Anthropic(api_key=self.api_key)
    
    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2000, **kwargs) -> str:
        """Generate response using Claude."""
        if not self.client:
            raise RuntimeError("Anthropic client not initialized")
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )
        
        return response.content[0].text
    
    def is_available(self) -> bool:
        """Check if Anthropic is available."""
        return self.client is not None
    
    def get_info(self) -> Dict[str, Any]:
        """Get Anthropic provider info."""
        return {
            "provider": "Anthropic",
            "model": self.model,
            "available": self.is_available(),
            "requires_api_key": True
        }


class GeminiProvider(LLMProvider):
    """Google Gemini provider."""
    
    def __init__(self, model: str = "gemini-pro", api_key: str = None):
        try:
            import google.generativeai as genai
            self.genai = genai
        except ImportError:
            self.genai = None
            
        self.api_key = api_key or os.environ.get('GOOGLE_API_KEY')
        self.model_name = model
        self.model = None
        
        if self.api_key and self.genai:
            self.genai.configure(api_key=self.api_key)
            self.model = self.genai.GenerativeModel(self.model_name)
    
    def generate(self, prompt: str, temperature: float = 0.7, **kwargs) -> str:
        """Generate response using Gemini."""
        if not self.model:
            raise RuntimeError("Gemini model not initialized")
        
        generation_config = {
            "temperature": temperature,
            "max_output_tokens": kwargs.get("max_tokens", 2000),
        }
        
        response = self.model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        return response.text
    
    def is_available(self) -> bool:
        """Check if Gemini is available."""
        return self.model is not None
    
    def get_info(self) -> Dict[str, Any]:
        """Get Gemini provider info."""
        return {
            "provider": "Google Gemini",
            "model": self.model_name,
            "available": self.is_available(),
            "requires_api_key": True
        }


class LLMManager:
    """Manager for multiple LLM providers."""
    
    def __init__(self, config_file: str = "llm_config.json"):
        self.config_file = Path(config_file)
        self.providers: Dict[str, LLMProvider] = {}
        self.active_provider: Optional[str] = None
        self._load_config()
        self._initialize_providers()
    
    def _load_config(self):
        """Load LLM configuration from file."""
        if self.config_file.exists():
            with self.config_file.open('r') as f:
                self.config = json.load(f)
        else:
            # Default configuration
            self.config = {
                "default_provider": "openai",
                "providers": {
                    "openai": {
                        "model": "gpt-4",
                        "enabled": True
                    },
                    "deepseek": {
                        "model": "deepseek-chat",
                        "enabled": True
                    },
                    "ollama": {
                        "model": "llama2",
                        "base_url": "http://localhost:11434",
                        "enabled": True
                    },
                    "anthropic": {
                        "model": "claude-3-opus-20240229",
                        "enabled": False
                    },
                    "gemini": {
                        "model": "gemini-pro",
                        "enabled": False
                    }
                }
            }
            self._save_config()
    
    def _save_config(self):
        """Save configuration to file."""
        with self.config_file.open('w') as f:
            json.dump(self.config, f, indent=2)
    
    def _initialize_providers(self):
        """Initialize enabled providers."""
        provider_classes = {
            "openai": OpenAIProvider,
            "deepseek": DeepSeekProvider,
            "ollama": OllamaProvider,
            "anthropic": AnthropicProvider,
            "gemini": GeminiProvider
        }
        
        for name, config in self.config["providers"].items():
            if config.get("enabled", False) and name in provider_classes:
                try:
                    provider_class = provider_classes[name]
                    # Pass config parameters to provider
                    provider = provider_class(**{k: v for k, v in config.items() if k != "enabled"})
                    
                    if provider.is_available():
                        self.providers[name] = provider
                        print(f"✅ Initialized {name} provider")
                    else:
                        print(f"❌ {name} provider not available (check API key or connection)")
                except Exception as e:
                    print(f"❌ Failed to initialize {name}: {e}")
        
        # Set default provider
        default = self.config.get("default_provider")
        if default in self.providers:
            self.active_provider = default
        elif self.providers:
            self.active_provider = next(iter(self.providers))
        
        if self.active_provider:
            print(f"\n🎯 Active provider: {self.active_provider}")
    
    def generate(self, prompt: str, provider: Optional[str] = None, **kwargs) -> str:
        """Generate response using specified or active provider."""
        provider_name = provider or self.active_provider
        
        if not provider_name:
            raise RuntimeError("No LLM provider available")
        
        if provider_name not in self.providers:
            raise ValueError(f"Provider '{provider_name}' not available")
        
        return self.providers[provider_name].generate(prompt, **kwargs)
    
    def set_active_provider(self, provider: str):
        """Set the active provider."""
        if provider not in self.providers:
            raise ValueError(f"Provider '{provider}' not available")
        
        self.active_provider = provider
        self.config["default_provider"] = provider
        self._save_config()
        print(f"Active provider set to: {provider}")
    
    def list_providers(self) -> Dict[str, Dict[str, Any]]:
        """List all available providers and their status."""
        all_providers = {}
        
        for name, provider in self.providers.items():
            all_providers[name] = provider.get_info()
            all_providers[name]["active"] = (name == self.active_provider)
        
        return all_providers
    
    def add_api_key(self, provider: str, api_key: str):
        """Add or update API key for a provider."""
        if provider == "openai":
            os.environ['OPENAI_API_KEY'] = api_key
        elif provider == "deepseek":
            os.environ['DEEPSEEK_API_KEY'] = api_key
        elif provider == "anthropic":
            os.environ['ANTHROPIC_API_KEY'] = api_key
        elif provider == "gemini":
            os.environ['GOOGLE_API_KEY'] = api_key
        
        # Reinitialize providers
        self._initialize_providers()
        print(f"API key updated for {provider}")
    
    def test_provider(self, provider: str) -> bool:
        """Test if a provider is working."""
        if provider not in self.providers:
            return False
        
        try:
            response = self.providers[provider].generate("Hello, please respond with 'OK'.")
            return bool(response)
        except Exception as e:
            print(f"Provider test failed for {provider}: {e}")
            return False


# Global LLM manager instance
llm_manager = LLMManager() 