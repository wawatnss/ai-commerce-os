"""
Shipping Rule

Evaluates the shipping complexity and cost for a product.
"""

from typing import Dict, Any
from .base import BaseRule, RuleResult


class ShippingRule(BaseRule):
    """
    Rule for evaluating shipping complexity.
    
    Analyzes factors that affect shipping:
    - Product size and weight (from category)
    - Shipping cost considerations
    - Logistics complexity
    """
    
    def evaluate(self, trend_data: Dict[str, Any]) -> RuleResult:
        """
        Evaluate the shipping complexity.
        
        Args:
            trend_data: Trend data with product category
            
        Returns:
            RuleResult with shipping score (higher = easier to ship)
        """
        category = trend_data.get("category", "").lower()
        
        # Category-based shipping complexity (mock logic)
        # In production, this would use actual product dimensions/weight
        easy_to_ship_categories = ["books", "jewelry", "accessories", "digital"]
        moderate_shipping_categories = ["electronics", "fashion", "beauty", "toys"]
        difficult_shipping_categories = ["furniture", "automotive", "appliances", "home"]
        
        if any(cat in category for cat in easy_to_ship_categories):
            base_score = 90
            reasoning = "Product category indicates easy shipping (small, lightweight items). Low shipping costs and minimal logistics complexity."
        elif any(cat in category for cat in moderate_shipping_categories):
            base_score = 60
            reasoning = "Product category indicates moderate shipping complexity. Standard shipping requirements with manageable costs."
        elif any(cat in category for cat in difficult_shipping_categories):
            base_score = 30
            reasoning = "Product category indicates complex shipping (large, heavy items). Higher shipping costs and logistics complexity."
        else:
            base_score = 50
            reasoning = "Shipping complexity cannot be determined from category alone. Requires product-specific analysis."
        
        # Adjust based on opportunity (high opportunity may justify shipping complexity)
        opportunity_score = trend_data.get("opportunity_score", 50)
        if opportunity_score > 70 and base_score < 60:
            base_score += 10  # Bonus for high opportunity
            reasoning += " High market opportunity justifies shipping complexity."
        
        shipping_score = min(100, max(0, base_score))
        
        # Confidence based on data quality
        confidence = 60  # Lower confidence without product-specific data
        
        return RuleResult(
            rule_name=self.rule_name,
            score=round(shipping_score, 2),
            confidence=round(confidence, 2),
            reasoning=reasoning,
            factors={
                "category": category,
                "base_score": base_score,
                "shipping_complexity": "low" if shipping_score >= 70 else "moderate" if shipping_score >= 40 else "high"
            }
        )
