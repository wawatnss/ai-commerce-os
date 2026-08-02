"""
Configuration for Trend Intelligence Module

This module provides configuration settings specific to trend intelligence operations.
"""

from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any


class TrendIntelligenceConfig(BaseSettings):
    """Configuration for trend intelligence module."""
    
    # Provider settings
    default_provider: str = "mock"
    collection_timeout: int = 300  # 5 minutes
    max_collection_items: int = 1000
    
    # Scoring settings
    default_score_weights: Dict[str, float] = {
        "popularity": 0.25,
        "growth": 0.25,
        "competition": 0.15,
        "opportunity": 0.20,
        "confidence": 0.15
    }
    
    # Cache settings
    cache_ttl_trends: int = 3600  # 1 hour
    cache_ttl_analytics: int = 300  # 5 minutes
    cache_ttl_collections: int = 1800  # 30 minutes
    
    # Cleanup settings
    auto_cleanup_enabled: bool = True
    cleanup_days: int = 30
    
    # Rate limiting
    max_collections_per_hour: int = 10
    
    class Config:
        env_prefix = "TREND_"
        env_file = ".env"


# Try to import from config, fallback to defaults
try:
    from config import settings
    redis_url = settings.REDIS_URL
except ImportError:
    redis_url = "redis://localhost:6379/0"

config = TrendIntelligenceConfig()
