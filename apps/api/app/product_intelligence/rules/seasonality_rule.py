"""
Seasonality Rule

Evaluates the seasonality of a product demand.
"""

from typing import Dict, Any
from datetime import datetime
from .base import BaseRule, RuleResult


class SeasonalityRule(BaseRule):
    """
    Rule for evaluating product seasonality.
    
    Analyzes seasonal demand patterns:
    - Whether demand is year-round or seasonal
    - Peak demand periods
    - Seasonal risk factors
    """
    
    def evaluate(self, trend_data: Dict[str, Any]) -> RuleResult:
        """
        Evaluate the seasonality of the product.
        
        Args:
            trend_data: Trend data
            
        Returns:
            RuleResult with seasonality score (higher = more year-round stable)
        """
        # For this implementation, we'll use growth stability as a proxy for seasonality
        # In production, this would use historical data to detect seasonal patterns
        growth_score = trend_data.get("growth_score", 50)
        popularity_score = trend_data.get("popularity_score", 50)
        
        # Stable growth and popularity indicate year-round demand
        stability_score = (growth_score + popularity_score) / 2
        
        # Adjust for category-based seasonality (mock logic)
        category = trend_data.get("category", "").lower()
        seasonal_categories = ["swimwear", "holiday", "christmas", "winter", "summer"]
        
        seasonality_penalty = 0
        if any(seasonal_cat in category for seasonal_cat in category.split()):
            seasonality_penalty = 30  # Penalty for seasonal products
        
        # Calculate seasonality score (higher = more year-round stable)
        seasonality_score = stability_score - seasonality_penalty
        seasonality_score = min(100, max(0, seasonality_score))
        
        # Confidence based on data quality
        confidence = trend_data.get("confidence_score", 60)  # Lower confidence for seasonality without historical data
        
        # Generate reasoning
        if seasonality_score >= 60:
            reasoning = f"Product shows year-round demand potential. Stable growth ({growth_score}/100) and popularity ({popularity_score}/100) indicate consistent demand."
        elif seasonality_score >= 40:
            reasoning = f"Product may have seasonal demand patterns. Consider inventory planning for peak periods. Growth ({growth_score}/100) suggests upward trend."
        else:
            reasoning = f"Product appears highly seasonal. Demand may fluctuate significantly throughout the year. Requires careful inventory management."
        
        return RuleResult(
            rule_name=self.rule_name,
            score=round(seasonality_score, 2),
            confidence=round(confidence, 2),
            reasoning=reasoning,
            factors={
                "stability_score": round(stability_score, 2),
                "seasonality_penalty": seasonality_penalty,
                "category": category,
                "is_seasonal": seasonality_penalty > 0
            }
        )
