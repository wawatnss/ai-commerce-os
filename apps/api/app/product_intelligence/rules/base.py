"""
Base Rule for Product Intelligence

This module defines the abstract base class for all product evaluation rules.
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
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class BaseRule(ABC):
    """
    Abstract base class for product evaluation rules.
    
    Each rule evaluates a specific aspect of a product's commercial potential.
    Rules should be independent and reusable across different contexts.
    """
    
    def __init__(self, weight: float = 1.0, config: Optional[Dict[str, Any]] = None, enabled: bool = True):
        """
        Initialize the rule.
        
        Args:
            weight: Weight of this rule in overall score calculation
            config: Optional configuration for the rule
            enabled: Whether this rule should be evaluated. Disabled rules are
                skipped entirely by ProductScoreEngine - they never run
                `evaluate()` and never contribute to the overall score.
        """
        self.weight = weight
        self.config = config or {}
        self.enabled = enabled
        self.rule_name = self.__class__.__name__.replace("Rule", "")
    
    @abstractmethod
    def evaluate(self, trend_data: Dict[str, Any]) -> RuleResult:
        """
        Evaluate the product against this rule.
        
        Args:
            trend_data: Trend data to evaluate
            
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
    
    def set_weight(self, weight: float) -> None:
        """
        Set the rule's weight.
        
        Args:
            weight: New weight value
        """
        if not 0 <= weight <= 1:
            raise ValueError("Weight must be between 0 and 1")
        self.weight = weight
    
    def is_enabled(self) -> bool:
        """Whether this rule should be evaluated."""
        return self.enabled
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable this rule."""
        self.enabled = enabled


class RuleError(Exception):
    """Base exception for rule errors."""
    pass


class EvaluationError(RuleError):
    """Raised when rule evaluation fails."""
    pass
