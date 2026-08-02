"""
Demand Rule

Evaluates the market demand for a product based on trend data.
"""

from typing import Dict, Any
from .base import BaseRule, RuleResult


class DemandRule(BaseRule):
    """
    Rule for evaluating market demand.
    
    Analyzes factors that indicate market demand such as:
    - Popularity score
    - Growth rate
    - Search volume trends
    """
    
    def evaluate(self, trend_data: Dict[str, Any]) -> RuleResult:
        """
        Evaluate the market demand.
        
        Args:
            trend_data: Trend data with popularity and growth metrics
            
        Returns:
            RuleResult with demand score
        """
        popularity_score = trend_data.get("popularity_score", 50)
        growth_score = trend_data.get("growth_score", 50)
        opportunity_score = trend_data.get("opportunity_score", 50)
        
        # Higher popularity indicates strong current demand
        demand_from_popularity = popularity_score * 0.4
        
        # Higher growth indicates increasing demand
        demand_from_growth = growth_score * 0.4
        
        # Opportunity score reflects demand-supply balance
        demand_from_opportunity = opportunity_score * 0.2
        
        # Calculate overall demand score
        demand_score = demand_from_popularity + demand_from_growth + demand_from_opportunity
        demand_score = min(100, max(0, demand_score))
        
        # Confidence based on data quality
        confidence = trend_data.get("confidence_score", 70)
        
        # Generate reasoning
        if demand_score >= 70:
            reasoning = f"Strong market demand indicated by high popularity ({popularity_score}/100) and rapid growth ({growth_score}/100). Product is trending upward."
        elif demand_score >= 50:
            reasoning = f"Moderate market demand. Steady popularity ({popularity_score}/100) with consistent growth ({growth_score}/100)."
        else:
            reasoning = f"Limited market demand indicated by low popularity ({popularity_score}/100) or stagnant growth ({growth_score}/100). Market may be saturated."
        
        return RuleResult(
            rule_name=self.rule_name,
            score=round(demand_score, 2),
            confidence=round(confidence, 2),
            reasoning=reasoning,
            factors={
                "popularity_score": popularity_score,
                "growth_score": growth_score,
                "opportunity_score": opportunity_score,
                "demand_from_popularity": round(demand_from_popularity, 2),
                "demand_from_growth": round(demand_from_growth, 2),
                "demand_from_opportunity": round(demand_from_opportunity, 2)
            }
        )
