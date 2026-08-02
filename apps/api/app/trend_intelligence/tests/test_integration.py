"""
Integration Tests for Trend Intelligence

Tests the integration between different components of the trend intelligence system.
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock, patch, AsyncMock

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.trend_intelligence.models.trend import Base, Trend, TrendCollection
from app.trend_intelligence.repositories.trend_repository import TrendRepository
from app.trend_intelligence.cache import TrendCache
from app.trend_intelligence.providers import MockProvider, TrendItem
from app.trend_intelligence.scoring import ScoreEngine
from app.trend_intelligence.schemas.trend import TrendItemCreate, TrendFilterParams


@pytest.fixture
def in_memory_db():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, TestingSessionLocal


@pytest.fixture
def db_session(in_memory_db):
    """Create a database session for testing."""
    engine, TestingSessionLocal = in_memory_db
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def mock_cache():
    """Create a mock cache for testing."""
    with patch('app.trend_intelligence.cache.redis.from_url'):
        cache = TrendCache()
        return cache


class TestTrendRepository:
    """Integration tests for TrendRepository."""
    
    @pytest.fixture
    def repository(self, db_session):
        """Create a repository instance."""
        return TrendRepository(db_session)
    
    def test_create_trend(self, repository):
        """Test creating a trend in the database."""
        trend_data = TrendItemCreate(
            trend_id="test_1",
            source="mock",
            product_name="Test Product",
            category="electronics",
            popularity_score=75.5,
            growth_score=80.0,
            competition_score=50.0,
            opportunity_score=70.0,
            confidence_score=85.0
        )
        
        trend = repository.create_trend(trend_data)
        
        assert trend.id is not None
        assert trend.trend_id == "test_1"
        assert trend.product_name == "Test Product"
    
    def test_get_trend_by_id(self, repository):
        """Test retrieving a trend by ID."""
        trend_data = TrendItemCreate(
            trend_id="test_2",
            source="mock",
            product_name="Test Product",
            category="electronics",
            popularity_score=75.5,
            growth_score=80.0,
            competition_score=50.0,
            opportunity_score=70.0,
            confidence_score=85.0
        )
        
        created = repository.create_trend(trend_data)
        retrieved = repository.get_trend_by_id(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.product_name == "Test Product"
    
    def test_get_trends_with_filters(self, repository):
        """Test retrieving trends with filters."""
        # Create multiple trends
        for i in range(5):
            trend_data = TrendItemCreate(
                trend_id=f"test_{i}",
                source="mock",
                product_name=f"Product {i}",
                category="electronics" if i < 3 else "fashion",
                popularity_score=50.0 + i * 10,
                growth_score=60.0 + i * 5,
                competition_score=40.0 + i * 5,
                opportunity_score=70.0,
                confidence_score=85.0
            )
            repository.create_trend(trend_data)
        
        # Filter by category
        filters = TrendFilterParams(category="electronics")
        trends, total = repository.get_trends(filters=filters)
        
        assert total == 3
        assert all(t.category == "electronics" for t in trends)
    
    def test_update_trend(self, repository):
        """Test updating a trend."""
        trend_data = TrendItemCreate(
            trend_id="test_3",
            source="mock",
            product_name="Test Product",
            category="electronics",
            popularity_score=75.5,
            growth_score=80.0,
            competition_score=50.0,
            opportunity_score=70.0,
            confidence_score=85.0
        )
        
        created = repository.create_trend(trend_data)
        
        from app.trend_intelligence.schemas.trend import TrendItemUpdate
        updated = repository.update_trend(
            created.id,
            TrendItemUpdate(product_name="Updated Product")
        )
        
        assert updated.product_name == "Updated Product"
    
    def test_delete_trend(self, repository):
        """Test deleting a trend."""
        trend_data = TrendItemCreate(
            trend_id="test_4",
            source="mock",
            product_name="Test Product",
            category="electronics",
            popularity_score=75.5,
            growth_score=80.0,
            competition_score=50.0,
            opportunity_score=70.0,
            confidence_score=85.0
        )
        
        created = repository.create_trend(trend_data)
        success = repository.delete_trend(created.id)
        
        assert success is True
        assert repository.get_trend_by_id(created.id) is None
    
    def test_bulk_create_trends(self, repository):
        """Test bulk creating trends."""
        trend_items = [
            TrendItemCreate(
                trend_id=f"bulk_{i}",
                source="mock",
                product_name=f"Product {i}",
                category="electronics",
                popularity_score=75.5,
                growth_score=80.0,
                competition_score=50.0,
                opportunity_score=70.0,
                confidence_score=85.0
            )
            for i in range(3)
        ]
        
        created = repository.bulk_create_trends(trend_items)
        
        assert len(created) == 3
        assert all(t.id is not None for t in created)


class TestProviderIntegration:
    """Integration tests for provider workflow."""
    
    @pytest.mark.asyncio
    async def test_full_provider_workflow(self):
        """Test the complete provider workflow: collect, normalize, validate."""
        provider = MockProvider()
        
        # Collect data
        raw_data = await provider.collect(limit=5)
        assert len(raw_data) == 5
        
        # Normalize data
        normalized = provider.normalize(raw_data)
        assert len(normalized) == 5
        assert all(isinstance(item, TrendItem) for item in normalized)
        
        # Validate data
        validated = [item for item in normalized if provider.validate(item)]
        assert len(validated) == 5
    
    @pytest.mark.asyncio
    async def test_provider_with_scoring(self):
        """Test provider integration with scoring engine."""
        provider = MockProvider()
        engine = ScoreEngine()
        
        # Get normalized data
        items = await provider.fetch_and_normalize(limit=3)
        
        # Score each item
        scored_items = []
        for item in items:
            score_result = engine.calculate_score(item.dict())
            scored_items.append({
                "item": item,
                "score": score_result.overall_score
            })
        
        assert len(scored_items) == 3
        assert all(0 <= s["score"] <= 100 for s in scored_items)


class TestCacheIntegration:
    """Integration tests for cache workflow."""
    
    def test_cache_write_read_cycle(self, mock_cache):
        """Test writing to and reading from cache."""
        test_data = {"id": 1, "product_name": "Test"}
        
        # Write
        mock_cache.redis.setex = Mock(return_value=True)
        mock_cache.set_trend("test_id", test_data)
        
        # Read
        mock_cache.redis.get = Mock(return_value='{"id": 1, "product_name": "Test"}')
        result = mock_cache.get_trend("test_id")
        
        assert result is not None
        assert result["product_name"] == "Test"
    
    def test_cache_invalidation(self, mock_cache):
        """Test cache invalidation."""
        mock_cache.redis.delete = Mock(return_value=1)
        mock_cache.redis.keys = Mock(return_value=["trends:list:1"])
        
        mock_cache.invalidate_trend("test_id")
        
        # Should delete trend and list caches
        assert mock_cache.redis.delete.call_count >= 1


class TestScoringIntegration:
    """Integration tests for scoring workflow."""
    
    def test_score_engine_with_real_data(self):
        """Test scoring engine with realistic trend data."""
        engine = ScoreEngine()
        
        data = {
            "popularity_score": 85.0,
            "growth_score": 75.0,
            "competition_score": 40.0,
            "opportunity_score": 80.0,
            "confidence_score": 90.0,
            "detected_at": datetime.utcnow()
        }
        
        result = engine.calculate_score(data)
        
        assert result.overall_score > 0
        assert result.overall_score <= 100
        assert len(result.component_scores) > 0
        assert len(result.weighted_scores) > 0
    
    def test_score_weight_adjustment(self):
        """Test adjusting score weights."""
        engine = ScoreEngine()
        
        from app.trend_intelligence.scoring import ScoreWeights
        new_weights = ScoreWeights(
            popularity=0.4,
            growth=0.3,
            competition=0.1,
            opportunity=0.1,
            confidence=0.1
        )
        
        engine.update_weights(new_weights)
        
        data = {
            "popularity_score": 100.0,
            "growth_score": 0.0,
            "competition_score": 50.0,
            "opportunity_score": 50.0,
            "confidence_score": 50.0,
            "detected_at": datetime.utcnow()
        }
        
        result = engine.calculate_score(data)
        
        # With higher popularity weight, overall score should be higher
        assert result.overall_score > 30


class TestEndToEndWorkflow:
    """End-to-end integration tests."""
    
    @pytest.mark.asyncio
    async def test_collection_to_database_workflow(self, db_session, mock_cache):
        """Test the complete workflow from collection to database storage."""
        repository = TrendRepository(db_session)
        provider = MockProvider()
        engine = ScoreEngine()
        
        # Collect data
        items = await provider.fetch_and_normalize(limit=3)
        
        # Score and store
        for item in items:
            score_result = engine.calculate_score(item.dict())
            
            trend_data = TrendItemCreate(
                trend_id=item.id,
                source=item.source,
                product_name=item.product_name,
                brand=item.brand,
                category=item.category,
                tags=item.tags,
                popularity_score=item.popularity_score,
                growth_score=item.growth_score,
                competition_score=item.competition_score,
                opportunity_score=item.opportunity_score,
                confidence_score=item.confidence_score,
                detected_at=item.detected_at,
                metadata=item.metadata
            )
            
            trend = repository.create_trend(trend_data)
            repository.update_trend_score(
                trend.id,
                score_result.overall_score,
                score_result.component_scores,
                score_result.weighted_scores
            )
        
        # Verify storage
        trends, total = repository.get_trends()
        assert total == 3
        assert all(t.overall_score > 0 for t in trends)
