"""
Unit Tests for Supplier Intelligence Rules

Tests the rule engine and individual rule implementations.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.supplier_intelligence.rules import (
    BaseRule,
    RuleResult,
    CostRule,
    DeliveryRule,
    MOQRule,
    get_registry
)


class TestCostRule:
    """Tests for CostRule."""
    
    @pytest.fixture
    def rule(self):
        return CostRule(weight=0.20)
    
    def test_evaluate_low_cost(self, rule):
        """Test evaluation with low cost."""
        offer_data = {
            "unit_cost": 5.0,
            "minimum_order_quantity": 10
        }
        
        result = rule.evaluate(offer_data)
        
        assert result.score >= 70
        assert result.rule_name == "Cost"
        assert "cost" in result.reasoning.lower()
    
    def test_evaluate_high_cost(self, rule):
        """Test evaluation with high cost."""
        offer_data = {
            "unit_cost": 50.0,
            "minimum_order_quantity": 100
        }
        
        result = rule.evaluate(offer_data)
        
        assert result.score <= 50


class TestDeliveryRule:
    """Tests for DeliveryRule."""
    
    @pytest.fixture
    def rule(self):
        return DeliveryRule(weight=0.15)
    
    def test_evaluate_fast_delivery(self, rule):
        """Test evaluation with fast delivery."""
        offer_data = {
            "estimated_processing_time": 3,
            "estimated_shipping_time": 5
        }
        
        result = rule.evaluate(offer_data)
        
        assert result.score >= 70
    
    def test_evaluate_slow_delivery(self, rule):
        """Test evaluation with slow delivery."""
        offer_data = {
            "estimated_processing_time": 10,
            "estimated_shipping_time": 25
        }
        
        result = rule.evaluate(offer_data)
        
        assert result.score <= 50


class TestMOQRule:
    """Tests for MOQRule."""
    
    @pytest.fixture
    def rule(self):
        return MOQRule(weight=0.15)
    
    def test_evaluate_low_moq(self, rule):
        """Test evaluation with low MOQ."""
        offer_data = {
            "minimum_order_quantity": 5
        }
        
        result = rule.evaluate(offer_data)
        
        assert result.score >= 70
    
    def test_evaluate_high_moq(self, rule):
        """Test evaluation with high MOQ."""
        offer_data = {
            "minimum_order_quantity": 500
        }
        
        result = rule.evaluate(offer_data)
        
        assert result.score <= 30


class TestRuleRegistry:
    """Tests for rule registry."""
    
    def test_registry_initialization(self):
        """Test that registry is initialized with default rules."""
        registry = get_registry()
        
        assert "cost" in registry.list_rules()
        assert "delivery" in registry.list_rules()
        assert "moq" in registry.list_rules()
    
    def test_get_rule(self):
        """Test getting a rule from registry."""
        registry = get_registry()
        
        rule = registry.get_rule("cost", weight=0.20)
        
        assert isinstance(rule, CostRule)
        assert rule.get_weight() == 0.20
    
    def test_rule_enable_disable(self):
        """Test enabling and disabling rules."""
        registry = get_registry()
        
        rule = registry.get_rule("delivery", weight=0.15, enabled=True)
        assert rule.is_enabled() is True
        
        rule.set_enabled(False)
        assert rule.is_enabled() is False
