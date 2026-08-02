"""
Integration Tests for Product Intelligence

Tests the integration between different components of the product intelligence system.
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock, patch

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.product_intelligence.models.product import Base, ProductIntelligenceReport
from app.product_intelligence.repositories.product_repository import ProductRepository
from app.product_intelligence.cache.product_cache import ProductCache
from app.product_intelligence.engines import ProductScoreEngine
from app.product_intelligence.rules import get_registry


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
    with patch('app.product_intelligence.cache.product_cache.redis.from_url'):
        cache = ProductCache()
        return cache


class TestProductRepository:
    """Integration tests for ProductRepository."""
    
    @pytest.fixture
    def repository(self, db_session):
        return ProductRepository(db_session)
    
    def test_create_report(self, repository):
        """Test creating a product intelligence report."""
        report_data = {
            "trend_id": "test_1",
            "product_name": "Test Product",
            "category": "electronics",
            "estimated_margin_score": 75.5,
            "demand_score": 80.0,
            "competition_score": 50.0,
            "shipping_complexity_score": 60.0,
            "supplier_availability_score": 70.0,
            "seasonality_score": 65.0,
            "impulse_buy_score": 55.0,
            "content_potential_score": 70.0,
            "seo_potential_score": 75.0,
            "return_risk_score": 60.0,
            "legal_risk_score": 65.0,
            "overall_score": 68.0,
            "confidence_score": 75.0,
            "recommendation": "buy",
            "reasoning": "Test reasoning",
            "strengths": ["Good margin", "High demand"],
            "weaknesses": ["Moderate competition"],
            "rule_results": {},
            "trend_data": {}
        }
        
        report = repository.create_report(report_data)
        
        assert report.id is not None
        assert report.trend_id == "test_1"
        assert report.overall_score == 68.0
    
    def test_get_report_by_trend_id(self, repository):
        """Test retrieving a report by trend ID."""
        report_data = {
            "trend_id": "test_2",
            "product_name": "Test Product",
            "category": "electronics",
            "estimated_margin_score": 75.5,
            "demand_score": 80.0,
            "competition_score": 50.0,
            "shipping_complexity_score": 60.0,
            "supplier_availability_score": 70.0,
            "seasonality_score": 65.0,
            "impulse_buy_score": 55.0,
            "content_potential_score": 70.0,
            "seo_potential_score": 75.0,
            "return_risk_score": 60.0,
            "legal_risk_score": 65.0,
            "overall_score": 68.0,
            "confidence_score": 75.0,
            "recommendation": "buy",
            "reasoning": "Test reasoning",
            "strengths": [],
            "weaknesses": [],
            "rule_results": {},
            "trend_data": {}
        }
        
        created = repository.create_report(report_data)
        retrieved = repository.get_report_by_trend_id("test_2")
        
        assert retrieved is not None
        assert retrieved.id == created.id
    
    def test_get_reports_with_filters(self, repository):
        """Test retrieving reports with filters."""
        # Create multiple reports
        for i in range(5):
            report_data = {
                "trend_id": f"test_{i}",
                "product_name": f"Product {i}",
                "category": "electronics" if i < 3 else "fashion",
                "estimated_margin_score": 50.0 + i * 10,
                "demand_score": 50.0 + i * 10,
                "competition_score": 50.0 + i * 5,
                "shipping_complexity_score": 50.0,
                "supplier_availability_score": 50.0,
                "seasonality_score": 50.0,
                "impulse_buy_score": 50.0,
                "content_potential_score": 50.0,
                "seo_potential_score": 50.0,
                "return_risk_score": 50.0,
                "legal_risk_score": 50.0,
                "overall_score": 50.0 + i * 10,
                "confidence_score": 70.0,
                "recommendation": "buy",
                "reasoning": "Test",
                "strengths": [],
                "weaknesses": [],
                "rule_results": {},
                "trend_data": {}
            }
            repository.create_report(report_data)
        
        # Filter by category
        from app.product_intelligence.schemas.product import ProductFilterParams
        filters = ProductFilterParams(category="electronics")
        reports, total = repository.get_reports(filters=filters)
        
        assert total == 3
        assert all(r.category == "electronics" for r in reports)


class TestProductScoreEngineIntegration:
    """Integration tests for score engine with rules."""
    
    @pytest.fixture
    def engine(self):
        return ProductScoreEngine()
    
    def test_full_analysis_workflow(self, engine):
        """Test complete analysis workflow."""
        trend_data = {
            "product_name": "Test Product",
            "category": "electronics",
            "popularity_score": 80,
            "growth_score": 75,
            "competition_score": 40,
            "opportunity_score": 70,
            "confidence_score": 85,
            "detected_at": datetime.utcnow()
        }
        
        result = engine.analyze(trend_data)
        
        assert 0 <= result.overall_score <= 100
        assert 0 <= result.confidence_score <= 100
        assert len(result.rule_results) > 0
        assert len(result.strengths) + len(result.weaknesses) > 0


class TestCacheIntegration:
    """Integration tests for cache workflow."""
    
    @pytest.fixture
    def cache(self):
        with patch('app.product_intelligence.cache.product_cache.redis.from_url'):
            return ProductCache()
    
    def test_cache_write_read_cycle(self, cache):
        """Test writing to and reading from cache."""
        test_data = {"id": 1, "product_name": "Test"}
        
        cache.redis.setex = Mock(return_value=True)
        cache.set_report("test_id", test_data)
        
        cache.redis.get = Mock(return_value='{"id": 1, "product_name": "Test"}')
        result = cache.get_report("test_id")
        
        assert result is not None
        assert result["product_name"] == "Test"
