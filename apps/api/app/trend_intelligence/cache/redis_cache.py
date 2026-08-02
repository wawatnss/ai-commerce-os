"""
Redis Cache for Trend Intelligence

This module implements Redis caching for trend data to avoid redundant processing
and improve performance.
"""

import json
import redis
from typing import Optional, Any, List, Dict
from datetime import timedelta
from config import settings


class TrendCache:
    """
    Redis cache manager for trend intelligence data.
    
    Provides caching for trend data, collection results, and computed scores
    to reduce database load and improve response times.
    """
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        """
        Initialize the cache manager.
        
        Args:
            redis_client: Optional Redis client (creates default if not provided)
        """
        self.redis = redis_client or redis.from_url(
            settings.REDIS_URL,
            decode_responses=True
        )
        self.default_ttl = 3600  # 1 hour default TTL
    
    def _make_key(self, prefix: str, *parts: str) -> str:
        """
        Create a cache key.
        
        Args:
            prefix: Key prefix
            *parts: Key parts
            
        Returns:
            Formatted cache key
        """
        return ":".join([prefix] + [str(p) for p in parts])
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        try:
            value = self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            # Log error in production
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set a value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (uses default if not provided)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            ttl = ttl or self.default_ttl
            serialized = json.dumps(value)
            return self.redis.setex(key, ttl, serialized)
        except Exception as e:
            # Log error in production
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete a value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            return bool(self.redis.delete(key))
        except Exception as e:
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """
        Delete keys matching a pattern.
        
        Args:
            pattern: Key pattern (e.g., "trend:*")
            
        Returns:
            Number of keys deleted
        """
        try:
            keys = self.redis.keys(pattern)
            if keys:
                return self.redis.delete(*keys)
            return 0
        except Exception as e:
            return 0
    
    # Trend-specific cache methods
    
    def get_trend(self, trend_id: str) -> Optional[Dict]:
        """
        Get a trend from cache.
        
        Args:
            trend_id: Trend identifier
            
        Returns:
            Trend data or None
        """
        key = self._make_key("trend", trend_id)
        return self.get(key)
    
    def set_trend(self, trend_id: str, trend_data: Dict, ttl: Optional[int] = None) -> bool:
        """
        Cache a trend.
        
        Args:
            trend_id: Trend identifier
            trend_data: Trend data
            ttl: Time to live
            
        Returns:
            True if successful
        """
        key = self._make_key("trend", trend_id)
        return self.set(key, trend_data, ttl)
    
    def get_trends_list(self, cache_key: str) -> Optional[List[Dict]]:
        """
        Get a cached trends list.
        
        Args:
            cache_key: Cache key for the list
            
        Returns:
            List of trends or None
        """
        return self.get(cache_key)
    
    def set_trends_list(self, cache_key: str, trends: List[Dict], ttl: Optional[int] = None) -> bool:
        """
        Cache a trends list.
        
        Args:
            cache_key: Cache key for the list
            trends: List of trend data
            ttl: Time to live
            
        Returns:
            True if successful
        """
        return self.set(cache_key, trends, ttl)
    
    def get_collection_result(self, collection_id: str) -> Optional[Dict]:
        """
        Get a collection result from cache.
        
        Args:
            collection_id: Collection identifier
            
        Returns:
            Collection result or None
        """
        key = self._make_key("collection", collection_id)
        return self.get(key)
    
    def set_collection_result(self, collection_id: str, result: Dict, ttl: Optional[int] = None) -> bool:
        """
        Cache a collection result.
        
        Args:
            collection_id: Collection identifier
            result: Collection result
            ttl: Time to live
            
        Returns:
            True if successful
        """
        key = self._make_key("collection", collection_id)
        return self.set(key, result, ttl)
    
    def get_analytics(self) -> Optional[Dict]:
        """
        Get cached analytics data.
        
        Returns:
            Analytics data or None
        """
        key = self._make_key("analytics")
        return self.get(key)
    
    def set_analytics(self, analytics: Dict, ttl: Optional[int] = None) -> bool:
        """
        Cache analytics data.
        
        Args:
            analytics: Analytics data
            ttl: Time to live (default 5 minutes)
            
        Returns:
            True if successful
        """
        key = self._make_key("analytics")
        return self.set(key, analytics, ttl or 300)
    
    def invalidate_trend(self, trend_id: str) -> None:
        """
        Invalidate cache for a specific trend.
        
        Args:
            trend_id: Trend identifier
        """
        # Delete the trend itself
        self.delete(self._make_key("trend", trend_id))
        
        # Invalidate list caches
        self.delete_pattern("trends:list:*")
        
        # Invalidate analytics
        self.delete(self._make_key("analytics"))
    
    def invalidate_category(self, category: str) -> None:
        """
        Invalidate cache for a category.
        
        Args:
            category: Category name
        """
        # Invalidate list caches for this category
        self.delete_pattern(f"trends:list:*:{category}:*")
        
        # Invalidate analytics
        self.delete(self._make_key("analytics"))
    
    def invalidate_all_trends(self) -> None:
        """
        Invalidate all trend-related cache.
        """
        self.delete_pattern("trend:*")
        self.delete_pattern("trends:list:*")
        self.delete(self._make_key("analytics"))
    
    def get_provider_last_collection(self, provider: str) -> Optional[str]:
        """
        Get the last collection ID for a provider.
        
        Args:
            provider: Provider name
            
        Returns:
            Last collection ID or None
        """
        key = self._make_key("provider", provider, "last_collection")
        return self.get(key)
    
    def set_provider_last_collection(self, provider: str, collection_id: str) -> bool:
        """
        Set the last collection ID for a provider.
        
        Args:
            provider: Provider name
            collection_id: Collection identifier
            
        Returns:
            True if successful
        """
        key = self._make_key("provider", provider, "last_collection")
        return self.set(key, collection_id, ttl=86400)  # 24 hours
    
    def check_collection_running(self, provider: str) -> bool:
        """
        Check if a collection is currently running for a provider.
        
        Args:
            provider: Provider name
            
        Returns:
            True if collection is running
        """
        key = self._make_key("provider", provider, "running")
        return self.redis.exists(key) > 0
    
    def set_collection_running(self, provider: str, collection_id: str, ttl: int = 300) -> bool:
        """
        Mark a collection as running for a provider.
        
        Args:
            provider: Provider name
            collection_id: Collection identifier
            ttl: Time to live (default 5 minutes)
            
        Returns:
            True if successful
        """
        key = self._make_key("provider", provider, "running")
        return self.set(key, {"collection_id": collection_id}, ttl)
    
    def clear_collection_running(self, provider: str) -> bool:
        """
        Clear the running flag for a provider.
        
        Args:
            provider: Provider name
            
        Returns:
            True if successful
        """
        key = self._make_key("provider", provider, "running")
        return self.delete(key)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        try:
            info = self.redis.info()
            return {
                "connected": True,
                "used_memory_human": info.get("used_memory_human"),
                "used_memory_peak_human": info.get("used_memory_peak_human"),
                "total_keys": info.get("db0", {}).get("keys", 0),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(info)
            }
        except Exception as e:
            return {
                "connected": False,
                "error": str(e)
            }
    
    def _calculate_hit_rate(self, info: Dict) -> float:
        """Calculate cache hit rate."""
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total = hits + misses
        if total == 0:
            return 0.0
        return round((hits / total) * 100, 2)
    
    def flush_all(self) -> bool:
        """
        Flush all cache data.
        
        Warning: This clears all data in the Redis database.
        
        Returns:
            True if successful
        """
        try:
            return self.redis.flushdb()
        except Exception as e:
            return False
