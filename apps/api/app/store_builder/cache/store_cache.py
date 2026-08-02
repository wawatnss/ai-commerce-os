"""
Redis Cache for Store Builder

This module implements Redis caching for store blueprints.
"""

import json
import redis
from typing import Optional, Any
from config import settings


class StoreCache:
    """Redis cache manager for store blueprints."""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        """Initialize the cache manager."""
        self.redis = redis_client or redis.from_url(
            settings.REDIS_URL,
            decode_responses=True
        )
        self.default_ttl = 7200  # 2 hours default TTL
    
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
    
    def get_store(self, product_id: str) -> Optional[dict[str, Any]]:
        """Get a store blueprint from cache."""
        key = f"store:{product_id}"
        return self.get(key)
    
    def set_store(self, product_id: str, store: dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Cache a store blueprint."""
        key = f"store:{product_id}"
        return self.set(key, store, ttl)
    
    def invalidate_store(self, product_id: str) -> None:
        """Invalidate cache for a specific store."""
        self.delete(f"store:{product_id}")
    
    def invalidate_all(self) -> None:
        """Invalidate all store cache."""
        try:
            keys = self.redis.keys("store:*")
            if keys:
                self.redis.delete(*keys)
        except Exception:
            pass
