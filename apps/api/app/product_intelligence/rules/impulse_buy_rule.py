"""
Impulse Buy Rule

Evaluates the impulse buy potential of a product.
"""

from typing import Dict, Any
from .base import BaseRule, RuleResult


class ImpulseBuyRule(BaseRule):
    """
    Rule for evaluating impulse buy potential.
    
    Analyzes factors that influence impulse purchases:
    - Price point (lower = more impulse)
    - Product category
    - Market trends
    """
    
    def evaluate(self, trend_data: Dict[str, Any]) -> RuleResult:
        """
        Evaluate the impulse buy potential.
        
        Args:
            trend_data: Trend data
            
        Returns:
            RuleResult with impulse buy score (higher = more impulse potential)
        """
        category = trend_data.get("category", "").lower()
        popularity_score = trend_data.get("popularity_score", 50)
        
        # Category-based impulse buy potential (mock logic)
        high_impulse_categories = ["accessories", "beauty", "toys", "books", "fashion"]
        moderate_impulse_categories = ["electronics", "home", "sports"]
        low_impulse_categories = ["automotive", "appliances", "furniture"]
        
        if any(cat in category for cat in high_impulse_categories):
            base_score = 80
            reasoning = "Product category has high impulse buy potential. Low to moderate price point with emotional appeal."
        elif any(cat in category for cat in moderate_impulse_categories):
            base_score = 50
            reasoning = "Product category has moderate impulse buy potential. Consider price point and marketing strategy."
        elif any(cat in category for cat in low_impulse_categories):
            base_score = 20
            reasoning = "Product category has low impulse buy potential. High consideration purchases requiring research."
        else:
            base_score = 40
            reasoning = "Impulse buy potential cannot be determined from category alone."
        
        # Adjust based on popularity (trending items often have impulse appeal)
        if popularity_score > 70:
            base_score += 10
            reasoning += " High popularity indicates trend-driven impulse potential."
        
        impulse_score = min(100, max(0, base_score))
        
        # Confidence based on data quality
        confidence = 65  # Moderate confidence without price data
        
        return RuleResult(
            rule_name=self.rule_name,
            score=round(impulse_score, 2),
            confidence=round(confidence, 2),
            reasoning=reasoning,
            factors={
                "category": category,
                "popularity_score": popularity_score,
                "impulse_potential": "high" if impulse_score >= 70 else "moderate" if impulse_score >= 40 else "low"
            }
        )
