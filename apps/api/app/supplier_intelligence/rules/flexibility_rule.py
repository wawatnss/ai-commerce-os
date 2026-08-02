"""
Flexibility Rule

Evaluates the flexibility of a supplier in terms of negotiations and terms.
"""

from typing import Dict, Any, Optional
from .base import BaseRule, RuleResult


class FlexibilityRule(BaseRule):
    """
    Rule for evaluating supplier flexibility.
    
    Analyzes terms and conditions (mock implementation).
    In production, this would assess actual negotiation flexibility.
    """
    
    def evaluate(self, offer_data: Dict[str, Any], product_data: Optional[Dict[str, Any]] = None) -> RuleResult:
        """
        Evaluate the supplier flexibility.
        
        Args:
            offer_data: Supplier offer data
            product_data: Optional product data
            
        Returns:
            RuleResult with flexibility score
        """
        # In production, this would assess actual terms and negotiation history
        # For now, we'll use a simple heuristic based on MOQ and currency
        moq = offer_data.get("minimum_order_quantity", 1)
        currency = offer_data.get("currency", "USD")
        
        # Lower MOQ generally indicates more flexibility
        moq_score = min(100, 100 - (moq / 10))
        
        # Major currencies (USD, EUR) often indicate more established, potentially less flexible suppliers
        currency_bonus = 10 if currency in ["USD", "EUR"] else 5
        
        flexibility_score = min(100, moq_score + currency_bonus)
        
        if flexibility_score >= 70:
            reasoning = f"Good flexibility. Reasonable MOQ ({moq}) and established terms."
        elif flexibility_score >= 50:
            reasoning = f"Moderate flexibility. Standard terms with some negotiation potential."
        else:
            reasoning = f"Limited flexibility. High MOQ ({moq}) or rigid terms."
        
        # Confidence based on data quality
        confidence = 50  # Lower confidence without actual negotiation data
        
        return RuleResult(
            rule_name=self.rule_name,
            score=flexibility_score,
            confidence=confidence,
            reasoning=reasoning,
            factors={
                "minimum_order_quantity": moq,
                "currency": currency
            },
            enabled=self.enabled
        )
