"""
Competition Rule

Evaluates the competitive landscape for a product.
"""

from typing import Dict, Any
from .base import BaseRule, RuleResult


class CompetitionRule(BaseRule):
    """
    Rule for evaluating competition level.
    
    Analyzes factors that indicate market competition:
    - Competition score (inverted for opportunity)
    - Market saturation indicators
    - Barrier to entry considerations
    """
    
    def evaluate(self, trend_data: Dict[str, Any]) -> RuleResult:
        """
        Evaluate the competition level.
        
        Args:
            trend_data: Trend data with competition metrics
            
        Returns:
            RuleResult with competition score (higher = less competition)
        """
        competition_score = trend_data.get("competition_score", 50)
        
        # Invert competition score: high competition = low opportunity score
        opportunity_from_competition = (100 - competition_score) * 0.7
        
        # Add bonus for low competition segments
        if competition_score < 30:
            opportunity_from_competition += 15  # Bonus for low competition
        elif competition_score > 70:
            opportunity_from_competition -= 10  # Penalty for high competition
        
        # Calculate overall competition opportunity score
        competition_opportunity_score = min(100, max(0, opportunity_from_competition))
        
        # Confidence based on data quality
        confidence = trend_data.get("confidence_score", 70)
        
        # Generate reasoning
        if competition_opportunity_score >= 70:
            reasoning = f"Low competitive environment ({competition_score}/100 competition). Good opportunity for market entry with differentiation potential."
        elif competition_opportunity_score >= 50:
            reasoning = f"Moderate competition ({competition_score}/100). Market has established players but room for differentiation."
        else:
            reasoning = f"High competitive environment ({competition_score}/100). Market may be saturated. Strong differentiation required."
        
        return RuleResult(
            rule_name=self.rule_name,
            score=round(competition_opportunity_score, 2),
            confidence=round(confidence, 2),
            reasoning=reasoning,
            factors={
                "competition_score": competition_score,
                "opportunity_from_competition": round(opportunity_from_competition, 2),
                "market_saturated": competition_score > 70
            }
        )
