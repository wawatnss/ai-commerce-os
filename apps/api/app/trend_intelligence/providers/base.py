"""
Base Provider Abstract Class

This module defines the abstract base class that all trend data providers must implement.
It ensures a consistent interface for collecting, normalizing, and validating trend data
from various sources.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class TrendItem(BaseModel):
    """
    Unified model for trend data from all providers.
    
    This model represents a normalized trend item that can come from any source.
    All providers must convert their source-specific data into this format.
    """
    id: str = Field(..., description="Unique identifier for the trend item")
    source: str = Field(..., description="Source provider name (e.g., 'google_trends', 'social_media')")
    product_name: str = Field(..., description="Name of the trending product or keyword")
    brand: Optional[str] = Field(None, description="Associated brand, if applicable")
    category: str = Field(..., description="Product category or niche")
    tags: List[str] = Field(default_factory=list, description="Relevant tags or keywords")
    popularity_score: float = Field(..., ge=0, le=100, description="Popularity score (0-100)")
    growth_score: float = Field(..., ge=0, le=100, description="Growth rate score (0-100)")
    competition_score: float = Field(..., ge=0, le=100, description="Competition level (0-100)")
    opportunity_score: float = Field(..., ge=0, le=100, description="Opportunity score (0-100)")
    confidence_score: float = Field(..., ge=0, le=100, description="Data confidence score (0-100)")
    detected_at: datetime = Field(default_factory=datetime.utcnow, description="When the trend was detected")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional provider-specific data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "trend_123",
                "source": "google_trends",
                "product_name": "wireless earbuds",
                "brand": None,
                "category": "electronics",
                "tags": ["audio", "wireless", "bluetooth"],
                "popularity_score": 85.5,
                "growth_score": 72.3,
                "competition_score": 45.0,
                "opportunity_score": 78.2,
                "confidence_score": 90.0,
                "detected_at": "2026-08-01T12:00:00Z",
                "metadata": {"region": "US", "timeframe": "7d"}
            }
        }


class BaseProvider(ABC):
    """
    Abstract base class for trend data providers.
    
    All trend data providers must inherit from this class and implement
    the required methods to ensure consistency across different sources.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the provider with configuration.
        
        Args:
            config: Provider-specific configuration dictionary
        """
        self.config = config or {}
        self.provider_name = self.__class__.__name__.replace("Provider", "").lower()
    
    @abstractmethod
    async def collect(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Collect raw trend data from the source.
        
        This method should fetch data from the provider's API or data source
        and return it in the provider's native format.
        
        Args:
            **kwargs: Provider-specific parameters for data collection
            
        Returns:
            List of dictionaries containing raw trend data
            
        Raises:
            ProviderError: If data collection fails
        """
        pass
    
    @abstractmethod
    def normalize(self, raw_data: List[Dict[str, Any]]) -> List[TrendItem]:
        """
        Normalize raw data into the unified TrendItem format.
        
        This method should convert provider-specific data into the standard
        TrendItem format, handling any necessary transformations.
        
        Args:
            raw_data: List of raw data dictionaries from collect()
            
        Returns:
            List of normalized TrendItem objects
            
        Raises:
            NormalizationError: If normalization fails
        """
        pass
    
    @abstractmethod
    def validate(self, trend_item: TrendItem) -> bool:
        """
        Validate a normalized TrendItem.
        
        This method should perform provider-specific validation to ensure
        the normalized data meets quality standards.
        
        Args:
            trend_item: The TrendItem to validate
            
        Returns:
            True if valid, False otherwise
        """
        pass
    
    async def fetch_and_normalize(self, **kwargs) -> List[TrendItem]:
        """
        Convenience method to collect, normalize, and validate data in one call.
        
        Args:
            **kwargs: Parameters passed to collect()
            
        Returns:
            List of validated TrendItem objects
        """
        raw_data = await self.collect(**kwargs)
        normalized_data = self.normalize(raw_data)
        
        # Filter out invalid items
        validated_data = [
            item for item in normalized_data
            if self.validate(item)
        ]
        
        return validated_data
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)
    
    def get_provider_name(self) -> str:
        """
        Get the provider name.
        
        Returns:
            Provider name string
        """
        return self.provider_name


class ProviderError(Exception):
    """Base exception for provider errors."""
    pass


class CollectionError(ProviderError):
    """Raised when data collection fails."""
    pass


class NormalizationError(ProviderError):
    """Raised when data normalization fails."""
    pass


class ValidationError(ProviderError):
    """Raised when data validation fails."""
    pass
