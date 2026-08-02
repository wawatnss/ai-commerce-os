"""
Trend Intelligence Module

This module provides trend intelligence capabilities including:
- Data collection from multiple providers
- Trend scoring and analysis
- Caching and optimization
- REST API endpoints
"""

from .api.router import router

__all__ = ["router"]
