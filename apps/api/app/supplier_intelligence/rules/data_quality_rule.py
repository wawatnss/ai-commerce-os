"""
Data Quality Rule

Evaluates the quality and completeness of supplier data.
"""

from typing import Dict, Any, Optional
from .base import BaseRule, RuleResult


class DataQualityRule(BaseRule):
    """
    Rule for evaluating data quality.
    
    Analyzes completeness and freshness of supplier data.
    """
    
    def evaluate(self, offer_data: Dict[str, Any], product_data: Optional[Dict[str, Any]] = None) -> RuleResult:
        """
        Evaluate the data quality.
        
        Args:
            offer_data: Supplier offer data
            product_data: Optional product data
            
        Returns:
            RuleResult with data quality score
        """
        # Check required fields
        required_fields = ["unit_cost", "minimum_order_quantity", "estimated_processing_time", "estimated_shipping_time"]
        missing_fields = [f for f in required_fields if offer_data.get(f) is None]
        
        # Calculate completeness score
        completeness = (len(required_fields) - len(missing_fields)) / len(required_fields) * 100
        
        # Check for recent updates (from metadata)
        metadata = offer_data.get("metadata", {})
        last_sync = metadata.get("last_sync", "")
        
        # Simple check for recent data (mock logic)
        data_freshness = 80 if last_sync else 50
        
        # Overall data quality score
        data_quality_score = (completeness * 0.7) + (data_freshness * 0.3)
        
        if data_quality_score >= 80:
            reasoning = f"Excellent data quality. All required fields present and data is current."
        elif data_quality_score >= 60:
            reasoning = f"Good data quality. Most required fields present with current data."
        elif data_quality_score >= 40:
            reasoning = f"Moderate data quality. Some fields missing or data may be outdated."
        else:
            reasoning = f"Poor data quality. Missing required fields or outdated data."
        
        # Confidence based on the quality itself
        confidence = data_quality_score
        
        return RuleResult(
            rule_name=self.rule_name,
            score=round(data_quality_score, 2),
            confidence=round(confidence, 2),
            reasoning=reasoning,
            factors={
                "completeness": round(completeness, 2),
                "data_freshness": data_freshness,
                "missing_fields": missing_fields
            },
            enabled=self.enabled
        )
