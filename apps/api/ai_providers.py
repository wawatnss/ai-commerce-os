from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from openai import OpenAI
from anthropic import Anthropic
from config import settings


class AIProvider(ABC):
    """Abstract base class for AI providers"""
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> str:
        """Generate text from the AI provider"""
        pass
    
    @abstractmethod
    def get_usage(self) -> Dict[str, int]:
        """Get token usage information"""
        pass


class OpenAIProvider(AIProvider):
    """OpenAI provider implementation"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        self.client = OpenAI(api_key=api_key or settings.OPENAI_API_KEY)
        self.model = model
        self._usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        # Track usage
        self._usage["prompt_tokens"] += response.usage.prompt_tokens
        self._usage["completion_tokens"] += response.usage.completion_tokens
        self._usage["total_tokens"] += response.usage.total_tokens
        
        return response.choices[0].message.content
    
    def get_usage(self) -> Dict[str, int]:
        return self._usage.copy()


class AnthropicProvider(AIProvider):
    """Anthropic provider implementation"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-opus-20240229"):
        self.client = Anthropic(api_key=api_key or settings.ANTHROPIC_API_KEY)
        self.model = model
        self._usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> str:
        message = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )
        
        # Track usage
        self._usage["prompt_tokens"] += message.usage.input_tokens
        self._usage["completion_tokens"] += message.usage.output_tokens
        self._usage["total_tokens"] += message.usage.input_tokens + message.usage.output_tokens
        
        return message.content[0].text
    
    def get_usage(self) -> Dict[str, int]:
        return self._usage.copy()


class AIProviderFactory:
    """Factory for creating AI provider instances"""
    
    _providers: Dict[str, AIProvider] = {}
    
    @classmethod
    def get_provider(cls, provider_name: str, **kwargs) -> AIProvider:
        """Get or create an AI provider instance"""
        if provider_name not in cls._providers:
            if provider_name == "openai":
                cls._providers[provider_name] = OpenAIProvider(**kwargs)
            elif provider_name == "anthropic":
                cls._providers[provider_name] = AnthropicProvider(**kwargs)
            else:
                raise ValueError(f"Unknown provider: {provider_name}")
        return cls._providers[provider_name]
    
    @classmethod
    def clear_cache(cls):
        """Clear the provider cache"""
        cls._providers.clear()
