"""
Unit Tests for Trend Intelligence Scoring Engine

Tests the scoring engine and individual scorers.
"""

import pytest
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.trend_intelligence.scoring import (
    ScoreEngine,
    ScoreWeights,
    ScoringResult,
    PopularityScorer,
    GrowthScorer,
    CompetitionScorer,
    OpportunityScorer,
    ConfidenceScorer
)


class TestScoreWeights:
    """Tests for ScoreWeights model."""
    
    def test_default_weights(self):
        """Test default weight configuration."""
        weights = ScoreWeights()
        
        assert weights.validate_weights() is True
        assert weights.popularity == 0.25
        assert weights.growth == 0.25
    
    def test_custom_weights(self):
        """Test custom weight configuration."""
        weights = ScoreWeights(
            popularity=0.3,
            growth=0.3,
            competition=0.1,
            opportunity=0.2,
            confidence=0.1
        )
        
        assert weights.validate_weights() is True
        assert weights.popularity == 0.3
    
    def test_invalid_weights(self):
        """Test that invalid weights are rejected."""
        weights = ScoreWeights(
            popularity=0.5,
            growth=0.5,
            competition=0.1,
            opportunity=0.1,
            confidence=0.1
        )
        
        # Sum is 1.3, should fail validation
        assert weights.validate_weights() is False


class TestPopularityScorer:
    """Tests for PopularityScorer."""
    
    def test_score_calculation(self):
        """Test basic score calculation."""
        scorer = PopularityScorer(weight=1.0)
        data = {"popularity_score": 75.5}
        
        score = scorer.score(data)
        
        assert score == 75.5
    
    def test_score_clamping(self):
        """Test that scores are clamped to 0-100 range."""
        scorer = PopularityScorer(weight=1.0)
        
        # Test high value
        assert scorer.score({"popularity_score": 150.0}) == 100.0
        
        # Test low value
        assert scorer.score({"popularity_score": -10.0}) == 0.0
    
    def test_log_transform(self):
        """Test log transform configuration."""
        scorer = PopularityScorer(weight=1.0, config={"log_transform": True})
        data = {"popularity_score": 50.0}
        
        score = scorer.score(data)
        
        # With log transform, score should be different
        assert score != 50.0


class TestGrowthScorer:
    """Tests for GrowthScorer."""
    
    def test_score_calculation(self):
        """Test basic score calculation."""
        scorer = GrowthScorer(weight=1.0)
        data = {"growth_score": 80.0}
        
        score = scorer.score(data)
        
        assert score == 80.0
    
    def test_exponential_bonus(self):
        """Test exponential bonus for high growth."""
        scorer = GrowthScorer(weight=1.0, config={"exponential_bonus": True})
        data = {"growth_score": 85.0}
        
        score = scorer.score(data)
        
        # Should get bonus
        assert score > 85.0
        assert score <= 100.0


class TestCompetitionScorer:
    """Tests for CompetitionScorer."""
    
    def test_score_inversion(self):
        """Test that competition score is inverted."""
        scorer = CompetitionScorer(weight=1.0)
        data = {"competition_score": 70.0}
        
        score = scorer.score(data)
        
        # High competition should give low score
        assert score == 30.0  # 100 - 70
    
    def test_low_competition(self):
        """Test that low competition gives high score."""
        scorer = CompetitionScorer(weight=1.0)
        data = {"competition_score": 20.0}
        
        score = scorer.score(data)
        
        # Low competition should give high score
        assert score == 80.0  # 100 - 20


class TestOpportunityScorer:
    """Tests for OpportunityScorer."""
    
    def test_score_calculation(self):
        """Test basic score calculation."""
        scorer = OpportunityScorer(weight=1.0)
        data = {"opportunity_score": 75.0}
        
        score = scorer.score(data)
        
        assert score == 75.0
    
    def test_high_growth_low_competition_bonus(self):
        """Test bonus for high growth and low competition."""
        scorer = OpportunityScorer(weight=1.0)
        data = {
            "opportunity_score": 70.0,
            "growth_score": 80.0,
            "competition_score": 20.0
        }
        
        score = scorer.score(data)
        
        # Should get bonus
        assert score > 70.0


class TestConfidenceScorer:
    """Tests for ConfidenceScorer."""
    
    def test_score_calculation(self):
        """Test basic score calculation."""
        scorer = ConfidenceScorer(weight=1.0)
        data = {"confidence_score": 85.0}
        
        score = scorer.score(data)
        
        assert score == 85.0
    
    def test_time_decay(self):
        """Test time decay for old data."""
        scorer = ConfidenceScorer(weight=1.0, config={"time_decay": True})
        
        # Recent data
        recent_data = {
            "confidence_score": 85.0,
            "detected_at": datetime.utcnow()
        }
        recent_score = scorer.score(recent_data)
        
        # Old data (1 week ago)
        old_data = {
            "confidence_score": 85.0,
            "detected_at": datetime.utcnow() - timedelta(days=7)
        }
        old_score = scorer.score(old_data)
        
        # Old data should have lower score
        assert old_score < recent_score


class TestScoreEngine:
    """Tests for ScoreEngine."""
    
    @pytest.fixture
    def engine(self):
        """Create a ScoreEngine instance for testing."""
        return ScoreEngine()
    
    def test_calculate_score(self, engine):
        """Test overall score calculation."""
        data = {
            "popularity_score": 75.0,
            "growth_score": 80.0,
            "competition_score": 50.0,
            "opportunity_score": 70.0,
            "confidence_score": 85.0,
            "detected_at": datetime.utcnow()
        }
        
        result = engine.calculate_score(data)
        
        assert isinstance(result, ScoringResult)
        assert 0 <= result.overall_score <= 100
        assert "popularity" in result.component_scores
        assert "popularity" in result.weighted_scores
    
    def test_calculate_batch_scores(self, engine):
        """Test batch score calculation."""
        data_list = [
            {
                "popularity_score": 75.0,
                "growth_score": 80.0,
                "competition_score": 50.0,
                "opportunity_score": 70.0,
                "confidence_score": 85.0,
                "detected_at": datetime.utcnow()
            },
            {
                "popularity_score": 60.0,
                "growth_score": 70.0,
                "competition_score": 60.0,
                "opportunity_score": 65.0,
                "confidence_score": 75.0,
                "detected_at": datetime.utcnow()
            }
        ]
        
        results = engine.calculate_batch_scores(data_list)
        
        assert len(results) == 2
        assert all(isinstance(r, ScoringResult) for r in results)
    
    def test_update_weights(self, engine):
        """Test updating scoring weights."""
        new_weights = ScoreWeights(
            popularity=0.4,
            growth=0.3,
            competition=0.1,
            opportunity=0.1,
            confidence=0.1
        )
        
        engine.update_weights(new_weights)
        
        # Check that weights were updated
        assert engine.weights.popularity == 0.4
    
    def test_update_invalid_weights(self, engine):
        """Test that invalid weights are rejected."""
        invalid_weights = ScoreWeights(
            popularity=0.5,
            growth=0.5,
            competition=0.1,
            opportunity=0.1,
            confidence=0.1
        )
        
        with pytest.raises(ValueError):
            engine.update_weights(invalid_weights)
    
    def test_register_custom_scorer(self, engine):
        """Test registering a custom scorer."""
        from app.trend_intelligence.scoring import BaseScorer
        
        class CustomScorer(BaseScorer):
            def score(self, data):
                return 50.0
        
        custom_scorer = CustomScorer(weight=0.1)
        engine.register_scorer("custom", custom_scorer)
        
        assert "custom" in engine.get_scorers()
    
    def test_unregister_scorer(self, engine):
        """Test unregistering a scorer."""
        engine.unregister_scorer("popularity")
        
        assert "popularity" not in engine.get_scorers()
