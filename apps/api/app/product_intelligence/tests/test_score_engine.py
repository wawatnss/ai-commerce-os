"""
Unit Tests for Product Score Engine

Tests the product scoring engine and score calculation.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.product_intelligence.engines import ProductScoreEngine, ScoreWeights


class TestProductScoreEngine:
    """Tests for ProductScoreEngine."""
    
    @pytest.fixture
    def engine(self):
        return ProductScoreEngine()
    
    def test_analyze_product(self, engine):
        """Test complete product analysis."""
        trend_data = {
            "product_name": "Test Product",
            "category": "electronics",
            "popularity_score": 75,
            "growth_score": 70,
            "competition_score": 45,
            "opportunity_score": 72,
            "confidence_score": 80,
            "detected_at": "2026-08-01T12:00:00Z"
        }
        
        result = engine.analyze(trend_data)
        
        assert 0 <= result.overall_score <= 100
        assert 0 <= result.confidence_score <= 100
        assert result.recommendation in ["strong_buy", "buy", "hold", "avoid"]
        assert len(result.reasoning) > 0
        assert len(result.rule_results) > 0
    
    def test_high_scoring_product(self, engine):
        """Test analysis of a high-scoring product."""
        trend_data = {
            "product_name": "High Score Product",
            "category": "electronics",
            "popularity_score": 90,
            "growth_score": 85,
            "competition_score": 30,
            "opportunity_score": 85,
            "confidence_score": 90,
            "detected_at": "2026-08-01T12:00:00Z"
        }
        
        result = engine.analyze(trend_data)
        
        assert result.overall_score >= 70
        assert result.recommendation in ["strong_buy", "buy"]
    
    def test_low_scoring_product(self, engine):
        """Test analysis of a low-scoring product."""
        trend_data = {
            "product_name": "Low Score Product",
            "category": "automotive",
            "popularity_score": 30,
            "growth_score": 20,
            "competition_score": 80,
            "opportunity_score": 25,
            "confidence_score": 60,
            "detected_at": "2026-08-01T12:00:00Z"
        }
        
        result = engine.analyze(trend_data)
        
        assert result.overall_score <= 50
        assert result.recommendation in ["hold", "avoid"]
    
    def test_strengths_weaknesses_identification(self, engine):
        """Test that strengths and weaknesses are identified."""
        trend_data = {
            "product_name": "Test Product",
            "category": "electronics",
            "popularity_score": 80,
            "growth_score": 30,
            "competition_score": 50,
            "opportunity_score": 60,
            "confidence_score": 70,
            "detected_at": "2026-08-01T12:00:00Z"
        }
        
        result = engine.analyze(trend_data)
        
        # Should have some strengths or weaknesses
        assert len(result.strengths) + len(result.weaknesses) > 0


class TestScoreWeights:
    """Tests for ScoreWeights configuration."""
    
    def test_default_weights(self):
        """Test default weight configuration."""
        weights = ScoreWeights()
        
        assert weights.validate_weights() is True
    
    def test_custom_weights(self):
        """Test custom weight configuration."""
        weights = ScoreWeights(
            estimated_margin=0.20,
            demand=0.20,
            competition=0.10,
            seasonality=0.05,
            shipping=0.05,
            impulse_buy=0.10,
            content_potential=0.10,
            seo=0.10,
            supplier_availability=0.05,
            return_risk=0.03,
            legal_risk=0.02
        )
        
        assert weights.validate_weights() is True
    
    def test_invalid_weights(self):
        """Test that invalid weights are rejected."""
        weights = ScoreWeights(
            estimated_margin=0.5,
            demand=0.5,
            competition=0.1,
            seasonality=0.1,
            shipping=0.1,
            impulse_buy=0.1,
            content_potential=0.1,
            seo=0.1,
            supplier_availability=0.1,
            return_risk=0.1,
            legal_risk=0.1
        )
        
        assert weights.validate_weights() is False
