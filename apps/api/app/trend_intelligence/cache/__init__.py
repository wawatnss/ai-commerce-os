"""
Cache Module Initialization

Exports the Redis cache manager.
"""

from .redis_cache import TrendCache

__all__ = ["TrendCache"]
