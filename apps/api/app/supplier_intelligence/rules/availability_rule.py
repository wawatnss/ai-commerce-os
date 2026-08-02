"""
Availability Rule

Evaluates the inventory availability of a supplier offer.
"""

from typing import Dict, Any, Optional
from .base import BaseRule, RuleResult


class AvailabilityRule(BaseRule):
    """
    Rule for evaluating inventory availability.
    
    Analyzes available quantity and stock levels.
    """
    
    def evaluate(self, offer_data: Dict[str, Any], product_data: Optional[Dict[str, Any]] = None) -> RuleResult:
        """
        Evaluate the inventory availability.
        
        Args:
            offer_data: Supplier offer data
            product_data: Optional product data
            
        Returns:
            RuleResult with availability score
        """
        available_quantity = offer_data.get("available_quantity", 0)
        
        # Normalize score based on available quantity
        if available_quantity >= 1000:
            availability_score = 90
            reasoning = f"Excellent availability. Large stock ({available_quantity} units) ensures supply stability."
        elif available_quantity >= 500:
            availability_score = 70
            reasoning = f"Good availability. Sufficient stock ({available_quantity} units) for steady orders."
        elif available_quantity >= 100:
            availability_score = 50
            reasoning = f"Moderate availability. Limited stock ({available_quantity} units) may require planning."
        elif available_quantity > 0:
            availability_score = 30
            reasoning = f"Limited availability. Low stock ({available_quantity} units) may lead to stockouts."
        else:
            availability_score = 10
            reasoning = f"No availability. Currently out of stock."
        
        # Confidence based on data quality
        confidence = 75  # Moderate confidence as stock levels change
        
        return RuleResult(
            rule_name=self.rule_name,
            score=availability_score,
            confidence=confidence,
            reasoning=reasoning,
            factors={
                "available_quantity": available_quantity
            },
            enabled=self.enabled
        )
