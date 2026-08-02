"""
Unit Tests for Supplier Score Engine

Tests the supplier scoring engine and score calculation.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.supplier_intelligence.engines import SupplierScoreEngine, ScoreWeights


class TestSupplierScoreEngine:
    """Tests for SupplierScoreEngine."""
    
    @pytest.fixture
    def engine(self):
        return SupplierScoreEngine()
    
    def test_evaluate_supplier(self, engine):
        """Test complete supplier evaluation."""
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
        assert result.recommendation in ["strong_recommend", "recommend", "consider", "avoid"]
        assert len(result.reasoning) > 0
        assert len(result.rule_results) > 0
    
    def test_high_scoring_supplier(self, engine):
        """Test evaluation of a high-scoring supplier."""
        offer_data = {
            "unit_cost": 5.0,
            "minimum_order_quantity": 10,
            "estimated_processing_time": 3,
            "estimated_shipping_time": 7,
            "available_quantity": 1000,
            "currency": "USD",
            "metadata": {}
        }
        
        supplier_metadata = {
            "tier": "premium",
            "established": 2005
        }
        
        result = engine.evaluate(offer_data, supplier_metadata)
        
        assert result.overall_score >= 60
        assert result.recommendation in ["strong_recommend", "recommend"]
    
    def test_low_scoring_supplier(self, engine):
        """Test evaluation of a low-scoring supplier."""
        offer_data = {
            "unit_cost": 100.0,
            "minimum_order_quantity": 500,
            "estimated_processing_time": 15,
            "estimated_shipping_time": 30,
            "available_quantity": 50,
            "currency": "USD",
            "metadata": {}
        }
        
        supplier_metadata = {
            "tier": "standard",
            "established": 2020
        }
        
        result = engine.evaluate(offer_data, supplier_metadata)
        
        assert result.overall_score <= 50


class TestScoreWeights:
    """Tests for ScoreWeights configuration."""
    
    def test_default_weights(self):
        """Test default weight configuration."""
        weights = ScoreWeights()
        
        assert weights.validate_weights() is True
    
    def test_custom_weights(self):
        """Test custom weight configuration."""
        weights = ScoreWeights(
            cost=0.25,
            delivery=0.15,
            moq=0.15,
            availability=0.15,
            reliability=0.15,
            flexibility=0.10,
            data_quality=0.05
        )
        
        assert weights.validate_weights() is True
    
    def test_invalid_weights(self):
        """Test that invalid weights are rejected."""
        weights = ScoreWeights(
            cost=0.5,
            delivery=0.3,
            moq=0.2,
            availability=0.1,
            reliability=0.1,
            flexibility=0.1,
            data_quality=0.1
        )
        
        assert weights.validate_weights() is False
