"""
Reliability Rule

Evaluates the reliability of a supplier based on historical data.
"""

from typing import Dict, Any, Optional
from .base import BaseRule, RuleResult


class ReliabilityRule(BaseRule):
    """
    Rule for evaluating supplier reliability.
    
    Analyzes historical performance metrics (mock implementation).
    In production, this would use actual performance data.
    """
    
    def evaluate(self, offer_data: Dict[str, Any], product_data: Optional[Dict[str, Any]] = None) -> RuleResult:
        """
        Evaluate the supplier reliability.
        
        Args:
            offer_data: Supplier offer data
            product_data: Optional product data
            
        Returns:
            RuleResult with reliability score
        """
        # In production, this would use historical performance data
        # For now, we'll use supplier metadata as a proxy
        supplier_metadata = offer_data.get("supplier_metadata", {})
        tier = supplier_metadata.get("tier", "standard")
        established = supplier_metadata.get("established", 2020)
        
        # Calculate reliability based on tier and years in business
        years_in_business = 2026 - established
        
        if tier == "premium" and years_in_business >= 10:
            reliability_score = 90
            reasoning = f"High reliability. Premium tier supplier with {years_in_business} years in business."
        elif tier == "premium":
            reliability_score = 75
            reasoning = f"Good reliability. Premium tier supplier."
        elif tier == "standard" and years_in_business >= 5:
            reliability_score = 60
            reasoning = f"Moderate reliability. Standard tier supplier with {years_in_business} years in business."
        else:
            reliability_score = 45
            reasoning = f"Average reliability. Standard tier supplier with limited track record."
        
        # Confidence based on data quality
        confidence = 60  # Lower confidence without actual performance data
        
        return RuleResult(
            rule_name=self.rule_name,
            score=reliability_score,
            confidence=confidence,
            reasoning=reasoning,
            factors={
                "tier": tier,
                "years_in_business": years_in_business
            },
            enabled=self.enabled
        )
