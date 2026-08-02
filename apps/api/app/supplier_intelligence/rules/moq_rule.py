"""
MOQ Rule

Evaluates the minimum order quantity requirements.
"""

from typing import Dict, Any, Optional
from .base import BaseRule, RuleResult


class MOQRule(BaseRule):
    """
    Rule for evaluating minimum order quantity.
    
    Analyzes whether MOQ is reasonable for the business.
    """
    
    def evaluate(self, offer_data: Dict[str, Any], product_data: Optional[Dict[str, Any]] = None) -> RuleResult:
        """
        Evaluate the MOQ requirements.
        
        Args:
            offer_data: Supplier offer data
            product_data: Optional product data
            
        Returns:
            RuleResult with MOQ score
        """
        moq = offer_data.get("minimum_order_quantity", 1)
        
        # Normalize score based on MOQ ranges
        if moq <= 10:
            moq_score = 90
            reasoning = f"Excellent MOQ. Minimum order quantity ({moq}) is very low, offering great flexibility."
        elif moq <= 50:
            moq_score = 70
            reasoning = f"Good MOQ. Minimum order quantity ({moq}) is reasonable for small businesses."
        elif moq <= 100:
            moq_score = 50
            reasoning = f"Moderate MOQ. Minimum order quantity ({moq}) is average but manageable."
        elif moq <= 500:
            moq_score = 30
            reasoning = f"High MOQ. Minimum order quantity ({moq}) requires significant upfront investment."
        else:
            moq_score = 10
            reasoning = f"Very high MOQ. Minimum order quantity ({moq}) may be prohibitive for small businesses."
        
        # Confidence based on data quality
        confidence = 85  # High confidence as MOQ is a clear metric
        
        return RuleResult(
            rule_name=self.rule_name,
            score=moq_score,
            confidence=confidence,
            reasoning=reasoning,
            factors={
                "minimum_order_quantity": moq
            },
            enabled=self.enabled
        )
