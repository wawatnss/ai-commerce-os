"""
Base Rule for Supplier Intelligence

This module defines the abstract base class for supplier evaluation rules.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class RuleResult(BaseModel):
    """Result of a rule evaluation."""
    rule_name: str = Field(..., description="Name of the rule")
    score: float = Field(..., ge=0, le=100, description="Rule score (0-100)")
    confidence: float = Field(..., ge=0, le=100, description="Confidence in the score (0-100)")
    reasoning: str = Field(..., description="Explanation for the score")
    factors: Dict[str, Any] = Field(default_factory=dict, description="Factors influencing the score")
    enabled: bool = Field(default=True, description="Whether the rule is enabled")


class BaseRule(ABC):
    """
    Abstract base class for supplier evaluation rules.
    
    Each rule evaluates a specific aspect of a supplier offer.
    Rules are independent and can be enabled/disabled via configuration.
    """
    
    def __init__(self, weight: float = 1.0, enabled: bool = True, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the rule.
        
        Args:
            weight: Weight of this rule in overall score calculation
            enabled: Whether this rule is enabled
            config: Optional configuration for the rule
        """
        self.weight = weight
        self.enabled = enabled
        self.config = config or {}
        self.rule_name = self.__class__.__name__.replace("Rule", "")
    
    @abstractmethod
    def evaluate(self, offer_data: Dict[str, Any], product_data: Optional[Dict[str, Any]] = None) -> RuleResult:
        """
        Evaluate the supplier offer against this rule.
        
        Args:
            offer_data: Supplier offer data to evaluate
            product_data: Optional product data for context
            
        Returns:
            RuleResult with score, confidence, and reasoning
        """
        pass
    
    def get_weight(self) -> float:
        """Get the rule's weight."""
        return self.weight
    
    def get_name(self) -> str:
        """Get the rule's name."""
        return self.rule_name
    
    def is_enabled(self) -> bool:
        """Check if the rule is enabled."""
        return self.enabled
    
    def set_enabled(self, enabled: bool) -> None:
        """
        Enable or disable the rule.
        
        Args:
            enabled: Whether to enable the rule
        """
        self.enabled = enabled
    
    def set_weight(self, weight: float) -> None:
        """
        Set the rule's weight.
        
        Args:
            weight: New weight value
        """
        if not 0 <= weight <= 1:
            raise ValueError("Weight must be between 0 and 1")
        self.weight = weight


class RuleError(Exception):
    """Base exception for rule errors."""
    pass


class EvaluationError(RuleError):
    """Raised when rule evaluation fails."""
    pass
