"""
Supplier Availability Rule

Evaluates the availability of suppliers for a product.
"""

from typing import Dict, Any
from .base import BaseRule, RuleResult


class SupplierAvailabilityRule(BaseRule):
    """
    Rule for evaluating supplier availability.
    
    Analyzes factors that affect supplier availability:
    - Market maturity
    - Category ubiquity
    - Supply chain complexity
    """
    
    def evaluate(self, trend_data: Dict[str, Any]) -> RuleResult:
        """
        Evaluate the supplier availability.
        
        Args:
            trend_data: Trend data
            
        Returns:
            RuleResult with supplier availability score
        """
        category = trend_data.get("category", "").lower()
        popularity_score = trend_data.get("popularity_score", 50)
        
        # Category-based supplier availability (mock logic)
        # In production, this would check actual supplier databases
        high_availability_categories = ["electronics", "fashion", "beauty", "home", "toys"]
        moderate_availability_categories = ["books", "sports", "accessories"]
        low_availability_categories = ["automotive", "industrial", "specialty"]
        
        if any(cat in category for cat in high_availability_categories):
            base_score = 85
            reasoning = "Product category has high supplier availability. Multiple sourcing options with competitive pricing."
        elif any(cat in category for cat in moderate_availability_categories):
            base_score = 60
            reasoning = "Product category has moderate supplier availability. Good sourcing options with some specialization required."
        elif any(cat in category for cat in low_availability_categories):
            base_score = 35
            reasoning = "Product category has limited supplier availability. May require specialized suppliers or direct relationships."
        else:
            base_score = 50
            reasoning = "Supplier availability cannot be determined from category alone."
        
        # Adjust based on popularity (popular products have more suppliers)
        if popularity_score > 70:
            base_score += 10
            reasoning += " High popularity indicates established supply chain."
        
        supplier_score = min(100, max(0, base_score))
        
        # Confidence based on data quality
        confidence = 60  # Lower confidence without actual supplier data
        
        return RuleResult(
            rule_name=self.rule_name,
            score=round(supplier_score, 2),
            confidence=round(confidence, 2),
            reasoning=reasoning,
            factors={
                "category": category,
                "popularity_score": popularity_score,
                "supplier_availability": "high" if supplier_score >= 70 else "moderate" if supplier_score >= 40 else "low"
            }
        )
