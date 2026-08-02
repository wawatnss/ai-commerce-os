"""
Provider Registry and Initialization

This module manages the registration and retrieval of trend data providers.
"""

from typing import Dict, Type, Optional, List
from .base import BaseProvider, TrendItem
from .mock_provider import MockProvider


class ProviderRegistry:
    """
    Registry for managing trend data providers.
    
    This class allows for dynamic registration and retrieval of providers,
    making it easy to add new data sources without modifying core logic.
    """
    
    def __init__(self):
        self._providers: Dict[str, Type[BaseProvider]] = {}
        self._instances: Dict[str, BaseProvider] = {}
    
    def register(self, provider_class: Type[BaseProvider], name: Optional[str] = None) -> None:
        """
        Register a provider class.
        
        Args:
            provider_class: The provider class to register
            name: Optional custom name (defaults to class name)
        """
        provider_name = name or provider_class.__name__.lower()
        self._providers[provider_name] = provider_class
    
    def unregister(self, name: str) -> None:
        """
        Unregister a provider.
        
        Args:
            name: Name of the provider to unregister
        """
        if name in self._providers:
            del self._providers[name]
        if name in self._instances:
            del self._instances[name]
    
    def get_provider(self, name: str, config: Optional[Dict] = None) -> BaseProvider:
        """
        Get a provider instance (cached or new).
        
        Args:
            name: Name of the provider
            config: Optional configuration for the provider
            
        Returns:
            Provider instance
            
        Raises:
            ValueError: If provider is not registered
        """
        if name not in self._providers:
            raise ValueError(f"Provider '{name}' is not registered")
        
        # Create new instance if config provided or not cached
        cache_key = f"{name}_{id(config) if config else 'default'}"
        
        if cache_key not in self._instances or config is not None:
            provider_class = self._providers[name]
            self._instances[cache_key] = provider_class(config)
        
        return self._instances[cache_key]
    
    def list_providers(self) -> List[str]:
        """
        List all registered provider names.
        
        Returns:
            List of provider names
        """
        return list(self._providers.keys())
    
    def is_registered(self, name: str) -> bool:
        """
        Check if a provider is registered.
        
        Args:
            name: Name of the provider
            
        Returns:
            True if registered, False otherwise
        """
        return name in self._providers


# Global registry instance
registry = ProviderRegistry()


def initialize_registry() -> None:
    """
    Initialize the registry with default providers.
    
    This function registers all available providers.
    Additional providers can be registered at runtime.
    """
    # Register built-in providers
    registry.register(MockProvider, "mock")
    
    # Future providers will be registered here:
    # registry.register(GoogleTrendsProvider, "google_trends")
    # registry.register(SocialMediaProvider, "social_media")
    # registry.register(EcommerceProvider, "ecommerce")


# Initialize on import
initialize_registry()


def get_registry() -> ProviderRegistry:
    """
    Get the global provider registry.
    
    Returns:
        ProviderRegistry instance
    """
    return registry


__all__ = [
    "BaseProvider",
    "TrendItem",
    "ProviderRegistry",
    "get_registry",
    "MockProvider",
    "CollectionError",
    "NormalizationError",
    "ValidationError",
]
