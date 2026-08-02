"""
Content Potential Rule

Evaluates the potential for content creation around a product.
"""

from typing import Dict, Any
from .base import BaseRule, RuleResult


class ContentPotentialRule(BaseRule):
    """
    Rule for evaluating content creation potential.
    
    Analyzes factors that influence content marketing:
    - Visual appeal (from category)
    - Storytelling potential
    - Social media suitability
    """
    
    def evaluate(self, trend_data: Dict[str, Any]) -> RuleResult:
        """
        Evaluate the content creation potential.
        
        Args:
            trend_data: Trend data
            
        Returns:
            RuleResult with content potential score
        """
        category = trend_data.get("category", "").lower()
        popularity_score = trend_data.get("popularity_score", 50)
        
        # Category-based content potential (mock logic)
        high_content_categories = ["fashion", "beauty", "home", "food", "travel"]
        moderate_content_categories = ["electronics", "sports", "books", "toys"]
        low_content_categories = ["automotive", "appliances", "industrial"]
        
        if any(cat in category for cat in high_content_categories):
            base_score = 85
            reasoning = "Product category has high content potential. Visual appeal and storytelling opportunities for social media and blogs."
        elif any(cat in category for cat in moderate_content_categories):
            base_score = 60
            reasoning = "Product category has moderate content potential. Requires creative approach for engaging content."
        elif any(cat in category for cat in low_content_categories):
            base_score = 35
            reasoning = "Product category has limited content potential. Technical content may be more appropriate than visual content."
        else:
            base_score = 50
            reasoning = "Content potential cannot be determined from category alone."
        
        # Adjust based on popularity (trending items are easier to create content for)
        if popularity_score > 70:
            base_score += 10
            reasoning += " High popularity makes content more shareable and discoverable."
        
        content_score = min(100, max(0, base_score))
        
        # Confidence based on data quality
        confidence = 70
        
        return RuleResult(
            rule_name=self.rule_name,
            score=round(content_score, 2),
            confidence=round(confidence, 2),
            reasoning=reasoning,
            factors={
                "category": category,
                "popularity_score": popularity_score,
                "content_potential": "high" if content_score >= 70 else "moderate" if content_score >= 40 else "low"
            }
        )
