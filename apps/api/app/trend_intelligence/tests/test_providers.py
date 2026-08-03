"""
Unit Tests for Trend Intelligence Providers

Tests the provider abstract class and mock provider implementation.
"""

import pytest
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.trend_intelligence.providers.base import (
    BaseProvider,
    TrendItem,
    CollectionError,
    NormalizationError,
    ValidationError
)
from app.trend_intelligence.providers.mock_provider import MockProvider


class TestTrendItem:
    """Tests for TrendItem model."""
    
    def test_trend_item_creation(self):
        """Test creating a valid TrendItem."""
        item = TrendItem(
            id="test_1",
            source="test",
            product_name="Test Product",
            category="test_category",
            popularity_score=75.5,
            growth_score=80.0,
            competition_score=50.0,
            opportunity_score=70.0,
            confidence_score=85.0
        )
        
        assert item.id == "test_1"
        assert item.source == "test"
        assert item.product_name == "Test Product"
        assert item.popularity_score == 75.5
        assert item.tags == []
    
    def test_trend_item_with_tags(self):
        """Test TrendItem with tags."""
        item = TrendItem(
            id="test_2",
            source="test",
            product_name="Test Product",
            category="test_category",
            tags=["tag1", "tag2"],
            popularity_score=75.5,
            growth_score=80.0,
            competition_score=50.0,
            opportunity_score=70.0,
            confidence_score=85.0
        )
        
        assert len(item.tags) == 2
        assert "tag1" in item.tags
    
    def test_trend_item_score_validation(self):
        """Test that scores are validated to be between 0 and 100."""
        with pytest.raises(ValueError):
            TrendItem(
                id="test_3",
                source="test",
                product_name="Test Product",
                category="test_category",
                popularity_score=150.0,  # Invalid: > 100
                growth_score=80.0,
                competition_score=50.0,
                opportunity_score=70.0,
                confidence_score=85.0
            )
        
        with pytest.raises(ValueError):
            TrendItem(
                id="test_4",
                source="test",
                product_name="Test Product",
                category="test_category",
                popularity_score=75.5,
                growth_score=-10.0,  # Invalid: < 0
                competition_score=50.0,
                opportunity_score=70.0,
                confidence_score=85.0
            )


class TestMockProvider:
    """Tests for MockProvider implementation."""
    
    @pytest.fixture
    def provider(self):
        """Create a MockProvider instance for testing."""
        return MockProvider()
    
    @pytest.mark.asyncio
    async def test_collect_data(self, provider):
        """Test data collection."""
        raw_data = await provider.collect(limit=10)
        
        assert len(raw_data) == 10
        assert all("id" in item for item in raw_data)
        assert all("product_name" in item for item in raw_data)
    
    @pytest.mark.asyncio
    async def test_collect_with_category(self, provider):
        """Test data collection with category filter."""
        raw_data = await provider.collect(category="electronics", limit=5)
        
        assert len(raw_data) == 5
        assert all(item.get("category") == "electronics" for item in raw_data)
    
    @pytest.mark.asyncio
    async def test_collect_invalid_limit(self, provider):
        """Test that invalid limit raises error."""
        with pytest.raises(CollectionError):
            await provider.collect(limit=0)
        
        with pytest.raises(CollectionError):
            await provider.collect(limit=2000)
    
    def test_normalize_data(self, provider):
        """Test data normalization."""
        raw_data = [
            {
                "id": "test_1",
                "product_name": "Test Product",
                "brand": "TestBrand",
                "category": "electronics",
                "search_volume": 50000,
                "growth_rate": 50.0,
                "competition_index": 40.0,
                "timestamp": datetime.utcnow()
            }
        ]
        
        normalized = provider.normalize(raw_data)
        
        assert len(normalized) == 1
        assert isinstance(normalized[0], TrendItem)
        assert normalized[0].product_name == "Test Product"
        assert normalized[0].source == "mock"
        assert 0 <= normalized[0].popularity_score <= 100
        assert 0 <= normalized[0].growth_score <= 100
    
    def test_validate_valid_item(self, provider):
        """Test validation of valid TrendItem."""
        item = TrendItem(
            id="test_1",
            source="mock",
            product_name="Test Product",
            category="electronics",
            popularity_score=75.5,
            growth_score=80.0,
            competition_score=50.0,
            opportunity_score=70.0,
            confidence_score=85.0
        )
        
        assert provider.validate(item) is True
    
    def test_validate_invalid_item_missing_fields(self, provider):
        """Test validation fails with missing required fields."""
        item = TrendItem(
            id="test_1",
            source="mock",
            product_name="",  # Invalid: empty
            category="electronics",
            popularity_score=75.5,
            growth_score=80.0,
            competition_score=50.0,
            opportunity_score=70.0,
            confidence_score=85.0
        )
        
        assert provider.validate(item) is False
    
    def test_validate_invalid_item_scores(self, provider):
        """Test validation fails with invalid scores."""
        item = TrendItem.model_construct(
            id="test_1",
            source="mock",
            product_name="Test Product",
            category="electronics",
            popularity_score=150.0,  # Invalid: > 100
            growth_score=80.0,
            competition_score=50.0,
            opportunity_score=70.0,
            confidence_score=85.0,
            detected_at=datetime.utcnow(),
        )

        assert provider.validate(item) is False
    
    def test_validate_invalid_item_future_date(self, provider):
        """Test validation fails with future detection date."""
        future_date = datetime(2030, 1, 1)
        item = TrendItem(
            id="test_1",
            source="mock",
            product_name="Test Product",
            category="electronics",
            popularity_score=75.5,
            growth_score=80.0,
            competition_score=50.0,
            opportunity_score=70.0,
            confidence_score=85.0,
            detected_at=future_date
        )
        
        assert provider.validate(item) is False
    
    @pytest.mark.asyncio
    async def test_fetch_and_normalize(self, provider):
        """Test the complete fetch and normalize workflow."""
        items = await provider.fetch_and_normalize(limit=5)
        
        assert len(items) == 5
        assert all(isinstance(item, TrendItem) for item in items)
        assert all(provider.validate(item) for item in items)


class TestProviderRegistry:
    """Tests for provider registry."""
    
    def test_register_provider(self):
        """Test registering a provider."""
        from app.trend_intelligence.providers import get_registry
        
        registry = get_registry()
        
        # Check that mock provider is registered
        assert registry.is_registered("mock")
    
    def test_get_provider(self):
        """Test getting a provider instance."""
        from app.trend_intelligence.providers import get_registry
        
        registry = get_registry()
        provider = registry.get_provider("mock")
        
        assert isinstance(provider, MockProvider)
        assert provider.get_provider_name() == "mock"
    
    def test_get_nonexistent_provider(self):
        """Test getting a non-existent provider raises error."""
        from app.trend_intelligence.providers import get_registry
        
        registry = get_registry()
        
        with pytest.raises(ValueError):
            registry.get_provider("nonexistent_provider")
    
    def test_list_providers(self):
        """Test listing all registered providers."""
        from app.trend_intelligence.providers import get_registry
        
        registry = get_registry()
        providers = registry.list_providers()
        
        assert "mock" in providers
