"""
Base Engine for Brand Builder

This module defines the abstract base class for brand generation engines.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class EngineResult(BaseModel):
    """Result of a brand engine execution."""
    engine_name: str = Field(..., description="Name of the engine")
    success: bool = Field(..., description="Whether the engine succeeded")
    data: Dict[str, Any] = Field(default_factory=dict, description="Generated data")
    confidence: float = Field(..., ge=0, le=100, description="Confidence in the result")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class BaseBrandEngine(ABC):
    """
    Abstract base class for brand generation engines.
    
    Each engine generates a specific part of the brand identity.
    Engines are independent and can be used in isolation or combined.
    """
    
    def __init__(self, ai_provider=None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the brand engine.
        
        Args:
            ai_provider: AI provider instance
            config: Optional engine configuration
        """
        self.ai_provider = ai_provider
        self.config = config or {}
        self.engine_name = self.__class__.__name__.replace("Engine", "")
    
    @abstractmethod
    async def generate(self, context: Dict[str, Any]) -> EngineResult:
        """
        Generate brand component using AI.
        
        Args:
            context: Context data (product info, audience, etc.)
            
        Returns:
            EngineResult with generated data
        """
        pass
    
    def get_name(self) -> str:
        """Get the engine name."""
        return self.engine_name
    
    def get_config(self) -> Dict[str, Any]:
        """Get the engine configuration."""
        return self.config


class EngineError(Exception):
    """Base exception for engine errors."""
    pass


class GenerationError(EngineError):
    """Raised when generation fails."""
    pass
