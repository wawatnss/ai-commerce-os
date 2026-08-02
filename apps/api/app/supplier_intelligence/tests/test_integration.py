"""
Integration Tests for Supplier Intelligence

Tests the integration between different components of the supplier intelligence system.
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock, patch

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.supplier_intelligence.models.supplier import Base, Supplier, SupplierOffer, SupplierEvaluation
from app.supplier_intelligence.repositories.supplier_repository import SupplierRepository
from app.supplier_intelligence.cache.supplier_cache import SupplierCache
from app.supplier_intelligence.engines import SupplierScoreEngine


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
    with patch('app.supplier_intelligence.cache.supplier_cache.redis.from_url'):
        cache = SupplierCache()
        return cache


class TestSupplierRepository:
    """Integration tests for SupplierRepository."""
    
    @pytest.fixture
    def repository(self, db_session):
        return SupplierRepository(db_session)
    
    def test_create_supplier(self, repository):
        """Test creating a supplier."""
        supplier_data = {
            "supplier_id": "SUPP001",
            "name": "Test Supplier",
            "source": "mock",
            "country": "China",
            "currency": "USD",
            "contact": {"email": "test@example.com"},
            "metadata": {"tier": "premium"}
        }
        
        supplier = repository.create_supplier(supplier_data)
        
        assert supplier.id is not None
        assert supplier.supplier_id == "SUPP001"
        assert supplier.name == "Test Supplier"
    
    def test_create_offer(self, repository):
        """Test creating a supplier offer."""
        offer_data = {
            "supplier_id": "SUPP001",
            "product_id": "PROD001",
            "unit_cost": 15.0,
            "minimum_order_quantity": 50,
            "estimated_processing_time": 5,
            "estimated_shipping_time": 10,
            "available_quantity": 500,
            "currency": "USD",
            "metadata": {}
        }
        
        offer = repository.create_offer(offer_data)
        
        assert offer.id is not None
        assert offer.supplier_id == "SUPP001"
        assert offer.product_id == "PROD001"
    
    def test_create_evaluation(self, repository):
        """Test creating a supplier evaluation."""
        evaluation_data = {
            "supplier_id": "SUPP001",
            "product_id": "PROD001",
            "cost_score": 75.0,
            "delivery_score": 70.0,
            "moq_score": 65.0,
            "availability_score": 60.0,
            "reliability_score": 70.0,
            "flexibility_score": 55.0,
            "data_quality_score": 80.0,
            "overall_score": 68.0,
            "confidence_score": 75.0,
            "recommendation": "recommend",
            "reasoning": "Test reasoning",
            "strengths": ["Good cost", "Fast delivery"],
            "weaknesses": ["Limited flexibility"],
            "rule_results": {},
            "rule_config": {}
        }
        
        evaluation = repository.create_evaluation(evaluation_data)
        
        assert evaluation.id is not None
        assert evaluation.overall_score == 68.0


class TestSupplierScoreEngineIntegration:
    """Integration tests for score engine with rules."""
    
    @pytest.fixture
    def engine(self):
        return SupplierScoreEngine()
    
    def test_full_evaluation_workflow(self, engine):
        """Test complete evaluation workflow."""
        offer_data = {
            "unit_cost": 15.0,
            "minimum_order_quantity": 50,
            "estimated_processing_time": 5,
            "estimated_shipping_time": 10,
            "available_quantity": 500,
            "currency": "USD",
            "metadata": {}
        }
        
        supplier_metadata = {
            "tier": "premium",
            "established": 2010
        }
        
        result = engine.evaluate(offer_data, supplier_metadata)
        
        assert 0 <= result.overall_score <= 100
        assert 0 <= result.confidence_score <= 100
        assert len(result.rule_results) > 0
        assert len(result.strengths) + len(result.weaknesses) > 0
