"""
Rules Module Initialization

Exports all rule classes and the rule registry.
"""

from .base import BaseRule, RuleResult, RuleError, EvaluationError
from .margin_rule import EstimatedMarginRule
from .demand_rule import DemandRule
from .competition_rule import CompetitionRule
from .seasonality_rule import SeasonalityRule
from .shipping_rule import ShippingRule
from .impulse_buy_rule import ImpulseBuyRule
from .content_potential_rule import ContentPotentialRule
from .seo_rule import SEORule
from .supplier_availability_rule import SupplierAvailabilityRule
from .return_risk_rule import ReturnRiskRule
from .legal_risk_rule import LegalRiskRule


class RuleRegistry:
    """
    Registry for managing product evaluation rules.
    
    Allows dynamic registration, enabling/disabling, and retrieval of rules.
    """
    
    def __init__(self):
        self._rules = {}
        self._instances = {}
    
    def register(self, rule_class, name: str = None) -> None:
        """Register a rule class."""
        rule_name = name or rule_class.__name__.replace("Rule", "").lower()
        self._rules[rule_name] = rule_class
    
    def unregister(self, name: str) -> None:
        """Unregister a rule."""
        if name in self._rules:
            del self._rules[name]
        if name in self._instances:
            del self._instances[name]
    
    def get_rule(self, name: str, weight: float = 1.0, enabled: bool = True, config: dict = None):
        """Get a rule instance."""
        if name not in self._rules:
            raise ValueError(f"Rule '{name}' is not registered")
        
        cache_key = f"{name}_{weight}_{enabled}_{id(config) if config else 'default'}"
        
        if cache_key not in self._instances:
            rule_class = self._rules[name]
            self._instances[cache_key] = rule_class(weight=weight, enabled=enabled, config=config)
        
        return self._instances[cache_key]
    
    def list_rules(self) -> list:
        """List all registered rule names."""
        return list(self._rules.keys())
    
    def is_registered(self, name: str) -> bool:
        """Check if a rule is registered."""
        return name in self._rules


# Global registry instance
registry = RuleRegistry()


def initialize_registry() -> None:
    """Initialize the registry with default rules."""
    registry.register(EstimatedMarginRule, "estimated_margin")
    registry.register(DemandRule, "demand")
    registry.register(CompetitionRule, "competition")
    registry.register(SeasonalityRule, "seasonality")
    registry.register(ShippingRule, "shipping")
    registry.register(ImpulseBuyRule, "impulse_buy")
    registry.register(ContentPotentialRule, "content_potential")
    registry.register(SEORule, "seo")
    registry.register(SupplierAvailabilityRule, "supplier_availability")
    registry.register(ReturnRiskRule, "return_risk")
    registry.register(LegalRiskRule, "legal_risk")


# Initialize on import
initialize_registry()


def get_registry() -> RuleRegistry:
    """Get the global rule registry."""
    return registry


__all__ = [
    "BaseRule",
    "RuleResult",
    "RuleError",
    "EvaluationError",
    "EstimatedMarginRule",
    "DemandRule",
    "CompetitionRule",
    "SeasonalityRule",
    "ShippingRule",
    "ImpulseBuyRule",
    "ContentPotentialRule",
    "SEORule",
    "SupplierAvailabilityRule",
    "ReturnRiskRule",
    "LegalRiskRule",
    "RuleRegistry",
    "get_registry",
]
