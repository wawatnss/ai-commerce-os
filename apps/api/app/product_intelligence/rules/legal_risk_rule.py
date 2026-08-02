"""
Legal Risk Rule

Evaluates legal and regulatory risks for a product.
"""

from typing import Dict, Any
from .base import BaseRule, RuleResult


class LegalRiskRule(BaseRule):
    """
    Rule for evaluating legal and regulatory risks.
    
    Analyzes factors that affect legal compliance:
    - Product category regulations
    - Safety requirements
    - Intellectual property considerations
    """
    
    def evaluate(self, trend_data: Dict[str, Any]) -> RuleResult:
        """
        Evaluate the legal risk.
        
        Args:
            trend_data: Trend data
            
        Returns:
            RuleResult with legal risk score (higher = lower risk)
        """
        category = trend_data.get("category", "").lower()
        
        # Category-based legal risk (mock logic)
        # In production, this would check regulatory databases
        low_risk_categories = ["books", "fashion", "accessories", "toys"]
        moderate_risk_categories = ["electronics", "beauty", "home", "sports"]
        high_risk_categories = ["automotive", "medical", "food", "supplements"]
        
        if any(cat in category for cat in low_risk_categories):
            base_score = 90
            reasoning = "Product category has low legal risk. Standard consumer goods with minimal regulatory requirements."
        elif any(cat in category for cat in moderate_risk_categories):
            base_score = 65
            reasoning = "Product category has moderate legal risk. Some regulatory compliance required (safety standards, certifications)."
        elif any(cat in category for cat in high_risk_categories):
            base_score = 35
            reasoning = "Product category has high legal risk. Significant regulatory compliance required (safety certifications, testing, approvals)."
        else:
            base_score = 50
            reasoning = "Legal risk cannot be determined from category alone. Legal review recommended."
        
        legal_score = min(100, max(0, base_score))
        
        # Confidence based on data quality
        confidence = 60  # Lower confidence without legal expertise
        
        return RuleResult(
            rule_name=self.rule_name,
            score=round(legal_score, 2),
            confidence=round(confidence, 2),
            reasoning=reasoning,
            factors={
                "category": category,
                "legal_risk": "low" if legal_score >= 70 else "moderate" if legal_score >= 40 else "high"
            }
        )
