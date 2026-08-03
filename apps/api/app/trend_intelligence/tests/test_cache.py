"""
Unit Tests for Trend Intelligence Cache

Tests the Redis cache functionality.
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.trend_intelligence.cache import TrendCache


class TestTrendCache:
    """Tests for TrendCache."""
    
    @pytest.fixture
    def mock_redis(self):
        """Create a mock Redis client."""
        return Mock()
    
    @pytest.fixture
    def cache(self, mock_redis):
        """Create a TrendCache instance with mock Redis."""
        with patch('app.trend_intelligence.cache.redis_cache.redis.from_url', return_value=mock_redis):
            return TrendCache()
    
    def test_get_trend(self, cache, mock_redis):
        """Test getting a trend from cache."""
        mock_redis.get.return_value = '{"id": 1, "product_name": "Test"}'
        
        result = cache.get_trend("test_id")
        
        assert result is not None
        assert result["product_name"] == "Test"
        mock_redis.get.assert_called_once()
    
    def test_set_trend(self, cache, mock_redis):
        """Test setting a trend in cache."""
        trend_data = {"id": 1, "product_name": "Test"}
        mock_redis.setex.return_value = True
        
        result = cache.set_trend("test_id", trend_data)
        
        assert result is True
        mock_redis.setex.assert_called_once()
    
    def test_delete_trend(self, cache, mock_redis):
        """Test deleting a trend from cache."""
        mock_redis.delete.return_value = 1
        
        result = cache.delete("test_key")
        
        assert result is True
        mock_redis.delete.assert_called_once()
    
    def test_get_analytics(self, cache, mock_redis):
        """Test getting analytics from cache."""
        mock_redis.get.return_value = '{"total_trends": 100}'
        
        result = cache.get_analytics()
        
        assert result is not None
        assert result["total_trends"] == 100
    
    def test_set_analytics(self, cache, mock_redis):
        """Test setting analytics in cache."""
        analytics = {"total_trends": 100}
        mock_redis.setex.return_value = True
        
        result = cache.set_analytics(analytics)
        
        assert result is True
        # Should use 5 minute TTL
        call_args = mock_redis.setex.call_args
        assert call_args[0][1] == 300
    
    def test_invalidate_trend(self, cache, mock_redis):
        """Test invalidating a specific trend."""
        mock_redis.delete.return_value = 1
        mock_redis.keys.return_value = ["trends:list:1", "trends:list:2"]
        
        cache.invalidate_trend("test_id")
        
        # Should delete the trend and list caches
        assert mock_redis.delete.call_count >= 2
    
    def test_invalidate_all_trends(self, cache, mock_redis):
        """Test invalidating all trend caches."""
        mock_redis.delete.return_value = 1
        mock_redis.keys.return_value = ["trend:1", "trend:2", "trends:list:1"]
        
        cache.invalidate_all_trends()
        
        # Should delete multiple keys
        assert mock_redis.delete.call_count >= 2
    
    def test_check_collection_running(self, cache, mock_redis):
        """Test checking if collection is running."""
        mock_redis.exists.return_value = 1
        
        result = cache.check_collection_running("mock")
        
        assert result is True
        mock_redis.exists.assert_called_once()
    
    def test_set_collection_running(self, cache, mock_redis):
        """Test setting collection as running."""
        mock_redis.setex.return_value = True
        
        result = cache.set_collection_running("mock", "collection_123")
        
        assert result is True
        mock_redis.setex.assert_called_once()
    
    def test_clear_collection_running(self, cache, mock_redis):
        """Test clearing collection running flag."""
        mock_redis.delete.return_value = 1
        
        result = cache.clear_collection_running("mock")
        
        assert result is True
        mock_redis.delete.assert_called_once()
    
    def test_get_stats(self, cache, mock_redis):
        """Test getting cache statistics."""
        mock_redis.info.return_value = {
            "used_memory_human": "100M",
            "used_memory_peak_human": "150M",
            "db0": {"keys": 1000},
            "keyspace_hits": 800,
            "keyspace_misses": 200
        }
        
        stats = cache.get_stats()
        
        assert stats["connected"] is True
        assert stats["used_memory_human"] == "100M"
        assert stats["total_keys"] == 1000
        assert stats["hit_rate"] == 80.0  # 800 / (800 + 200)
    
    def test_get_stats_disconnected(self, cache, mock_redis):
        """Test getting stats when Redis is disconnected."""
        mock_redis.info.side_effect = Exception("Connection error")
        
        stats = cache.get_stats()
        
        assert stats["connected"] is False
        assert "error" in stats


class TestCacheKeyGeneration:
    """Tests for cache key generation."""
    
    @pytest.fixture
    def cache(self):
        """Create a TrendCache instance."""
        with patch('app.trend_intelligence.cache.redis_cache.redis.from_url'):
            return TrendCache()
    
    def test_make_key(self, cache):
        """Test cache key generation."""
        key = cache._make_key("prefix", "part1", "part2")
        
        assert key == "prefix:part1:part2"
    
    def test_make_key_with_numbers(self, cache):
        """Test cache key generation with numbers."""
        key = cache._make_key("prefix", 1, 2, 3)
        
        assert key == "prefix:1:2:3"
