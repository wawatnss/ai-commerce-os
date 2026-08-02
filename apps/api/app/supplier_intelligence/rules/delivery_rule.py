"""
Delivery Rule

Evaluates the delivery speed and reliability of a supplier offer.
"""

from typing import Dict, Any, Optional
from .base import BaseRule, RuleResult


class DeliveryRule(BaseRule):
    """
    Rule for evaluating delivery performance.
    
    Analyzes processing time and shipping time.
    """
    
    def evaluate(self, offer_data: Dict[str, Any], product_data: Optional[Dict[str, Any]] = None) -> RuleResult:
        """
        Evaluate the delivery performance.
        
        Args:
            offer_data: Supplier offer data
            product_data: Optional product data
            
        Returns:
            RuleResult with delivery score
        """
        processing_time = offer_data.get("estimated_processing_time", 0)
        shipping_time = offer_data.get("estimated_shipping_time", 0)
        total_time = processing_time + shipping_time
        
        # Normalize score based on total delivery time
        if total_time <= 10:
            delivery_score = 90
            reasoning = f"Excellent delivery speed. Total delivery time ({total_time} days) is very fast."
        elif total_time <= 20:
            delivery_score = 70
            reasoning = f"Good delivery speed. Total delivery time ({total_time} days) is reasonable."
        elif total_time <= 30:
            delivery_score = 50
            reasoning = f"Moderate delivery speed. Total delivery time ({total_time} days) is average."
        else:
            delivery_score = 30
            reasoning = f"Slower delivery. Total delivery time ({total_time} days) may impact customer satisfaction."
        
        # Confidence based on data quality
        confidence = 70  # Moderate confidence as estimates may vary
        
        return RuleResult(
            rule_name=self.rule_name,
            score=delivery_score,
            confidence=confidence,
            reasoning=reasoning,
            factors={
                "processing_time": processing_time,
                "shipping_time": shipping_time,
                "total_time": total_time
            },
            enabled=self.enabled
        )
