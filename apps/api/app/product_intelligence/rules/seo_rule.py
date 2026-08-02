"""
SEO Rule

Evaluates the SEO potential for a product.
"""

from typing import Dict, Any
from .base import BaseRule, RuleResult


class SEORule(BaseRule):
    """
    Rule for evaluating SEO potential.
    
    Analyzes factors that influence SEO:
    - Keyword competition
    - Search volume
    - Content opportunities
    """
    
    def evaluate(self, trend_data: Dict[str, Any]) -> RuleResult:
        """
        Evaluate the SEO potential.
        
        Args:
            trend_data: Trend data
            
        Returns:
            RuleResult with SEO score
        """
        competition_score = trend_data.get("competition_score", 50)
        popularity_score = trend_data.get("popularity_score", 50)
        growth_score = trend_data.get("growth_score", 50)
        
        # Lower competition = better SEO opportunities
        seo_from_competition = (100 - competition_score) * 0.4
        
        # Higher popularity = more search volume
        seo_from_popularity = popularity_score * 0.3
        
        # Higher growth = trending searches
        seo_from_growth = growth_score * 0.3
        
        # Calculate overall SEO score
        seo_score = seo_from_competition + seo_from_popularity + seo_from_growth
        seo_score = min(100, max(0, seo_score))
        
        # Confidence based on data quality
        confidence = trend_data.get("confidence_score", 70)
        
        # Generate reasoning
        if seo_score >= 70:
            reasoning = f"Strong SEO potential. Low competition ({competition_score}/100) with high search volume ({popularity_score}/100) and trending growth ({growth_score}/100). Good keyword opportunities."
        elif seo_score >= 50:
            reasoning = f"Moderate SEO potential. Manageable competition ({competition_score}/100) with steady search volume ({popularity_score}/100). Content strategy important."
        else:
            reasoning = f"Limited SEO potential. High competition ({competition_score}/100) or low search volume ({popularity_score}/100). Requires long-tail keyword strategy."
        
        return RuleResult(
            rule_name=self.rule_name,
            score=round(seo_score, 2),
            confidence=round(confidence, 2),
            reasoning=reasoning,
            factors={
                "competition_score": competition_score,
                "popularity_score": popularity_score,
                "growth_score": growth_score,
                "seo_from_competition": round(seo_from_competition, 2),
                "seo_from_popularity": round(seo_from_popularity, 2),
                "seo_from_growth": round(seo_from_growth, 2)
            }
        )
