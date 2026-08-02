"""
Unit Tests for Product Intelligence Rules

Tests the rule engine and individual rule implementations.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.product_intelligence.rules import (
    BaseRule,
    RuleResult,
    EstimatedMarginRule,
    DemandRule,
    CompetitionRule,
    get_registry
)


class TestEstimatedMarginRule:
    """Tests for EstimatedMarginRule."""
    
    @pytest.fixture
    def rule(self):
        return EstimatedMarginRule(weight=0.15)
    
    def test_evaluate_high_margin(self, rule):
        """Test evaluation with high margin potential."""
        trend_data = {
            "competition_score": 30,
            "growth_score": 80,
            "opportunity_score": 75,
            "confidence_score": 80
        }
        
        result = rule.evaluate(trend_data)
        
        assert result.score >= 70
        assert result.rule_name == "EstimatedMargin"
        assert "margin" in result.reasoning.lower()
    
    def test_evaluate_low_margin(self, rule):
        """Test evaluation with low margin potential."""
        trend_data = {
            "competition_score": 80,
            "growth_score": 30,
            "opportunity_score": 40,
            "confidence_score": 70
        }
        
        result = rule.evaluate(trend_data)
        
        assert result.score <= 50
        assert "competition" in result.reasoning.lower()


class TestDemandRule:
    """Tests for DemandRule."""
    
    @pytest.fixture
    def rule(self):
        return DemandRule(weight=0.15)
    
    def test_evaluate_high_demand(self, rule):
        """Test evaluation with high demand."""
        trend_data = {
            "popularity_score": 85,
            "growth_score": 80,
            "opportunity_score": 75,
            "confidence_score": 80
        }
        
        result = rule.evaluate(trend_data)
        
        assert result.score >= 70
        assert "demand" in result.reasoning.lower()
    
    def test_evaluate_low_demand(self, rule):
        """Test evaluation with low demand."""
        trend_data = {
            "popularity_score": 30,
            "growth_score": 20,
            "opportunity_score": 30,
            "confidence_score": 70
        }
        
        result = rule.evaluate(trend_data)
        
        assert result.score <= 50


class TestCompetitionRule:
    """Tests for CompetitionRule."""
    
    @pytest.fixture
    def rule(self):
        return CompetitionRule(weight=0.12)
    
    def test_evaluate_low_competition(self, rule):
        """Test evaluation with low competition (high opportunity)."""
        trend_data = {
            "competition_score": 25,
            "confidence_score": 80
        }
        
        result = rule.evaluate(trend_data)
        
        assert result.score >= 70
        assert "opportunity" in result.reasoning.lower()
    
    def test_evaluate_high_competition(self, rule):
        """Test evaluation with high competition."""
        trend_data = {
            "competition_score": 80,
            "confidence_score": 70
        }
        
        result = rule.evaluate(trend_data)
        
        assert result.score <= 50


class TestRuleRegistry:
    """Tests for rule registry."""
    
    def test_registry_initialization(self):
        """Test that registry is initialized with default rules."""
        registry = get_registry()
        
        assert "estimated_margin" in registry.list_rules()
        assert "demand" in registry.list_rules()
        assert "competition" in registry.list_rules()
    
    def test_get_rule(self):
        """Test getting a rule from registry."""
        registry = get_registry()
        
        rule = registry.get_rule("estimated_margin", weight=0.15)
        
        assert isinstance(rule, EstimatedMarginRule)
        assert rule.get_weight() == 0.15
    
    def test_rule_weight_update(self):
        """Test updating rule weight."""
        registry = get_registry()
        
        rule = registry.get_rule("demand", weight=0.15)
        rule.set_weight(0.20)
        
        assert rule.get_weight() == 0.20
