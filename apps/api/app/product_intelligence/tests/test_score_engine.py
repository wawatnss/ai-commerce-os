"""
Unit Tests for Product Score Engine

Tests the product scoring engine and score calculation.
"""

import logging

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.product_intelligence.engines import ProductScoreEngine, ScoreWeights
from app.product_intelligence.rules import get_registry, CompetitionRule


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


class TestProductScoreEngineRegressions:
    """Regression tests for RC1: RuleRegistry.get_rule() used to raise
    `TypeError: BaseRule.__init__() got an unexpected keyword argument
    'enabled'` on every single call, which ProductScoreEngine.analyze()
    silently swallowed (`except Exception: continue`, no logging). The net
    effect was that every product analysis returned overall_score=0,
    recommendation=AVOID, and rule_results={}, with no error raised or
    logged anywhere - a silent, total outage of this feature.
    """

    TREND_DATA = {
        "product_name": "Test Product",
        "category": "electronics",
        "popularity_score": 80,
        "growth_score": 75,
        "competition_score": 40,
        "opportunity_score": 70,
        "confidence_score": 85,
    }

    def test_rules_actually_execute(self):
        """Every registered rule must run and contribute a result - this is
        the core RC1 regression: previously every rule call raised and was
        silently skipped, leaving rule_results empty."""
        engine = ProductScoreEngine()
        registered_rule_count = len(get_registry().list_rules())

        result = engine.analyze(self.TREND_DATA)

        assert registered_rule_count > 0
        assert len(result.rule_results) == registered_rule_count
        assert result.metadata["rules_evaluated"] == registered_rule_count
        assert result.metadata["failed_rules"] == []
        assert result.metadata["skipped_rules"] == []

    def test_scoring_returns_meaningful_values_again(self):
        """The overall score/confidence must reflect the actual rules, not
        the all-zero fallback produced when every rule silently failed."""
        engine = ProductScoreEngine()

        result = engine.analyze(self.TREND_DATA)

        assert result.overall_score > 0
        assert result.metadata["total_weight"] > 0
        assert result.rule_results != {}

    def test_disabled_rules_are_skipped_intentionally(self):
        """A disabled rule must never be evaluated and must not appear in
        rule_results, but every other rule must still run normally."""
        engine = ProductScoreEngine(disabled_rules={"competition"})

        result = engine.analyze(self.TREND_DATA)

        assert "competition" not in result.rule_results
        assert "competition" in result.metadata["skipped_rules"]
        assert "competition" not in result.metadata["failed_rules"]
        # Every other registered rule still ran.
        other_rules = [r for r in get_registry().list_rules() if r != "competition"]
        for rule_name in other_rules:
            assert rule_name in result.rule_results

    def test_disabled_rule_evaluate_is_never_called(self, monkeypatch):
        """Belt-and-suspenders check that a disabled rule's evaluate() is
        never invoked at all, not just filtered out of the results."""
        calls = []
        original_evaluate = CompetitionRule.evaluate

        def _tracking_evaluate(self, trend_data):
            calls.append(self.rule_name)
            return original_evaluate(self, trend_data)

        monkeypatch.setattr(CompetitionRule, "evaluate", _tracking_evaluate)

        engine = ProductScoreEngine(disabled_rules={"competition"})
        engine.analyze(self.TREND_DATA)

        assert calls == []

    def test_rule_exceptions_are_logged_not_silently_swallowed(self, monkeypatch, caplog):
        """A rule that raises during evaluate() must be logged (with
        exc_info) and excluded from the result - but must never crash the
        whole analysis or vanish without a trace, per the RC1 fix
        requirement to stop silently ignoring rule failures."""

        def _boom(self, trend_data):
            raise RuntimeError("synthetic rule failure for regression test")

        monkeypatch.setattr(CompetitionRule, "evaluate", _boom)

        engine = ProductScoreEngine()
        with caplog.at_level(logging.ERROR, logger="ai_commerce"):
            result = engine.analyze(self.TREND_DATA)

        assert "competition" not in result.rule_results
        assert "competition" in result.metadata["failed_rules"]
        # The other 10 rules must still have executed normally.
        assert len(result.rule_results) == len(get_registry().list_rules()) - 1

        logged_messages = [record.getMessage() for record in caplog.records]
        assert any("competition" in msg and "failed" in msg for msg in logged_messages)
        # logger.exception() must have captured the actual traceback, not
        # just a bare message.
        exception_records = [r for r in caplog.records if r.exc_info is not None]
        assert any("synthetic rule failure" in str(r.exc_info[1]) for r in exception_records)


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
