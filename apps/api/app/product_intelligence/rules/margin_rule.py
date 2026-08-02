"""
Estimated Margin Rule

Evaluates the potential profit margin for a product based on trend data.
"""

from typing import Dict, Any
from .base import BaseRule, RuleResult


class EstimatedMarginRule(BaseRule):
    """
    Rule for evaluating estimated profit margin.
    
    Analyzes factors that influence profit potential such as:
    - Competition level (lower competition = higher margin potential)
    - Market demand vs supply balance
    - Price point considerations
    """
    
    def evaluate(self, trend_data: Dict[str, Any]) -> RuleResult:
        """
        Evaluate the estimated margin potential.
        
        Args:
            trend_data: Trend data with competition and growth metrics
            
        Returns:
            RuleResult with margin score
        """
        competition_score = trend_data.get("competition_score", 50)
        growth_score = trend_data.get("growth_score", 50)
        opportunity_score = trend_data.get("opportunity_score", 50)
        
        # Lower competition = higher margin potential
        margin_from_competition = (100 - competition_score) * 0.4
        
        # Higher growth = better margin potential (early adopters pay premium)
        margin_from_growth = growth_score * 0.3
        
        # Higher opportunity = better margin potential
        margin_from_opportunity = opportunity_score * 0.3
        
        # Calculate overall margin score
        margin_score = margin_from_competition + margin_from_growth + margin_from_opportunity
        margin_score = min(100, max(0, margin_score))
        
        # Confidence based on data quality
        confidence = trend_data.get("confidence_score", 70)
        
        # Generate reasoning
        if margin_score >= 70:
            reasoning = f"High margin potential due to low competition ({competition_score}/100) and strong growth ({growth_score}/100). Early market entry opportunity."
        elif margin_score >= 50:
            reasoning = f"Moderate margin potential. Competition is manageable ({competition_score}/100) with steady growth ({growth_score}/100)."
        else:
            reasoning = f"Lower margin potential due to high competition ({competition_score}/100) or limited growth ({growth_score}/100). Consider differentiation strategy."
        
        return RuleResult(
            rule_name=self.rule_name,
            score=round(margin_score, 2),
            confidence=round(confidence, 2),
            reasoning=reasoning,
            factors={
                "competition_score": competition_score,
                "growth_score": growth_score,
                "opportunity_score": opportunity_score,
                "margin_from_competition": round(margin_from_competition, 2),
                "margin_from_growth": round(margin_from_growth, 2),
                "margin_from_opportunity": round(margin_from_opportunity, 2)
            }
        )
