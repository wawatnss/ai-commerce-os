"""
Redis Cache for Supplier Intelligence

This module implements Redis caching for supplier intelligence data.
"""

import json
import redis
from typing import Optional, Any, List, Dict
from datetime import timedelta
from config import settings


class SupplierCache:
    """Redis cache manager for supplier intelligence data."""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        """Initialize the cache manager."""
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
    
    def get_evaluation(self, supplier_id: str, product_id: str) -> Optional[Dict]:
        """Get an evaluation from cache."""
        key = self._make_key("evaluation", supplier_id, product_id)
        return self.get(key)
    
    def set_evaluation(self, supplier_id: str, product_id: str, evaluation: Dict, ttl: Optional[int] = None) -> bool:
        """Cache an evaluation."""
        key = self._make_key("evaluation", supplier_id, product_id)
        return self.set(key, evaluation, ttl)
    
    def get_best_offers(self, product_id: str) -> Optional[List[Dict]]:
        """Get cached best offers."""
        key = self._make_key("best_offers", product_id)
        return self.get(key)
    
    def set_best_offers(self, product_id: str, offers: List[Dict], ttl: Optional[int] = None) -> bool:
        """Cache best offers."""
        key = self._make_key("best_offers", product_id)
        return self.set(key, offers, ttl or 300)  # 5 minutes default
    
    def invalidate_product(self, product_id: str) -> None:
        """Invalidate cache for a specific product."""
        self.delete_pattern("best_offers:" + product_id)
    
    def invalidate_all(self) -> None:
        """Invalidate all supplier intelligence cache."""
        self.delete_pattern("evaluation:*")
        self.delete_pattern("best_offers:*")
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete keys matching a pattern."""
        try:
            keys = self.redis.keys(pattern)
            if keys:
                return self.redis.delete(*keys)
            return 0
        except Exception:
            return 0
