"""
Cost Rule

Evaluates the cost competitiveness of a supplier offer.
"""

from typing import Dict, Any, Optional
from .base import BaseRule, RuleResult


class CostRule(BaseRule):
    """
    Rule for evaluating cost competitiveness.
    
    Analyzes unit cost and overall cost efficiency.
    """
    
    def evaluate(self, offer_data: Dict[str, Any], product_data: Optional[Dict[str, Any]] = None) -> RuleResult:
        """
        Evaluate the cost competitiveness.
        
        Args:
            offer_data: Supplier offer data
            product_data: Optional product data
            
        Returns:
            RuleResult with cost score
        """
        unit_cost = offer_data.get("unit_cost", 0)
        minimum_order_quantity = offer_data.get("minimum_order_quantity", 1)
        
        # Calculate total minimum order cost
        total_min_cost = unit_cost * minimum_order_quantity
        
        # Normalize score based on cost ranges (mock logic)
        # In production, this would compare against market average or other offers
        if total_min_cost <= 100:
            cost_score = 90
            reasoning = f"Excellent cost efficiency. Total minimum order cost (${total_min_cost:.2f}) is very competitive."
        elif total_min_cost <= 500:
            cost_score = 70
            reasoning = f"Good cost efficiency. Total minimum order cost (${total_min_cost:.2f}) is reasonable."
        elif total_min_cost <= 1000:
            cost_score = 50
            reasoning = f"Moderate cost efficiency. Total minimum order cost (${total_min_cost:.2f}) is average."
        else:
            cost_score = 30
            reasoning = f"Higher cost. Total minimum order cost (${total_min_cost:.2f}) may impact margins."
        
        # Confidence based on data quality
        confidence = 80  # High confidence as cost data is usually accurate
        
        return RuleResult(
            rule_name=self.rule_name,
            score=cost_score,
            confidence=confidence,
            reasoning=reasoning,
            factors={
                "unit_cost": unit_cost,
                "minimum_order_quantity": minimum_order_quantity,
                "total_min_cost": total_min_cost
            },
            enabled=self.enabled
        )
