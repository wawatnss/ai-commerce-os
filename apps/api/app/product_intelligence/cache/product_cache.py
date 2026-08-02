"""
Redis Cache for Product Intelligence

This module implements Redis caching for product intelligence reports.
"""

import json
import redis
from typing import Optional, Any, List, Dict
from datetime import timedelta
from config import settings


class ProductCache:
    """
    Redis cache manager for product intelligence data.
    """
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        """
        Initialize the cache manager.
        
        Args:
            redis_client: Optional Redis client
        """
        self.redis = redis_client or redis.from_url(
            settings.REDIS_URL,
            decode_responses=True
        )
        self.default_ttl = 3600  # 1 hour default TTL
    
    def _make_key(self, prefix: str, *parts: str) -> str:
        """Create a cache key."""
        return ":".join([prefix] + [str(p) for p in parts])
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        try:
            value = self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception:
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in cache."""
        try:
            ttl = ttl or self.default_ttl
            serialized = json.dumps(value)
            return self.redis.setex(key, ttl, serialized)
        except Exception:
            return False
    
    def delete(self, key: str) -> bool:
        """Delete a value from cache."""
        try:
            return bool(self.redis.delete(key))
        except Exception:
            return False
    
    def get_report(self, trend_id: str) -> Optional[Dict]:
        """Get a product report from cache."""
        key = self._make_key("product_report", trend_id)
        return self.get(key)
    
    def set_report(self, trend_id: str, report_data: Dict, ttl: Optional[int] = None) -> bool:
        """Cache a product report."""
        key = self._make_key("product_report", trend_id)
        return self.set(key, report_data, ttl)
    
    def get_top_products(self, limit: int, min_score: float) -> Optional[List[Dict]]:
        """Get cached top products."""
        key = self._make_key("top_products", limit, min_score)
        return self.get(key)
    
    def set_top_products(self, limit: int, min_score: float, products: List[Dict], ttl: Optional[int] = None) -> bool:
        """Cache top products."""
        key = self._make_key("top_products", limit, min_score)
        return self.set(key, products, ttl or 300)  # 5 minutes default
    
    def get_analytics(self) -> Optional[Dict]:
        """Get cached analytics."""
        key = self._make_key("product_analytics")
        return self.get(key)
    
    def set_analytics(self, analytics: Dict, ttl: Optional[int] = None) -> bool:
        """Cache analytics."""
        key = self._make_key("product_analytics")
        return self.set(key, analytics, ttl or 300)  # 5 minutes
    
    def invalidate_report(self, trend_id: str) -> None:
        """Invalidate cache for a specific report."""
        self.delete(self._make_key("product_report", trend_id))
        self.delete(self._make_key("top_products"))  # Invalidate top products cache
    
    def invalidate_all(self) -> None:
        """Invalidate all product intelligence cache."""
        self.delete_pattern("product_report:*")
        self.delete_pattern("top_products:*")
        self.delete(self._make_key("product_analytics"))
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete keys matching a pattern."""
        try:
            keys = self.redis.keys(pattern)
            if keys:
                return self.redis.delete(*keys)
            return 0
        except Exception:
            return 0
