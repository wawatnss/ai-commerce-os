"""
Return Risk Rule

Evaluates the risk of product returns.
"""

from typing import Dict, Any
from .base import BaseRule, RuleResult


class ReturnRiskRule(BaseRule):
    """
    Rule for evaluating return risk.
    
    Analyzes factors that influence return rates:
    - Product category
    - Quality considerations
    - Customer expectations
    """
    
    def evaluate(self, trend_data: Dict[str, Any]) -> RuleResult:
        """
        Evaluate the return risk.
        
        Args:
            trend_data: Trend data
            
        Returns:
            RuleResult with return risk score (higher = lower risk)
        """
        category = trend_data.get("category", "").lower()
        
        # Category-based return risk (mock logic)
        # In production, this would use historical return data
        low_return_categories = ["books", "digital", "accessories", "beauty"]
        moderate_return_categories = ["electronics", "fashion", "toys", "home"]
        high_return_categories = ["furniture", "appliances", "clothing"]
        
        if any(cat in category for cat in low_return_categories):
            base_score = 85
            reasoning = "Product category has low return risk. Items typically meet customer expectations with minimal issues."
        elif any(cat in category for cat in moderate_return_categories):
            base_score = 60
            reasoning = "Product category has moderate return risk. Quality control and accurate descriptions important."
        elif any(cat in category for cat in high_return_categories):
            base_score = 35
            reasoning = "Product category has high return risk. Size, fit, or quality issues common. Requires excellent quality control."
        else:
            base_score = 50
            reasoning = "Return risk cannot be determined from category alone."
        
        return_score = min(100, max(0, base_score))
        
        # Confidence based on data quality
        confidence = 65  # Moderate confidence without historical return data
        
        return RuleResult(
            rule_name=self.rule_name,
            score=round(return_score, 2),
            confidence=round(confidence, 2),
            reasoning=reasoning,
            factors={
                "category": category,
                "return_risk": "low" if return_score >= 70 else "moderate" if return_score >= 40 else "high"
            }
        )
