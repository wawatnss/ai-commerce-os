"""
Supplier Score Engine

This module implements the scoring engine that orchestrates rules and generates
comprehensive supplier evaluations.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from ..rules import get_registry, RuleResult
from ..schemas.supplier import Recommendation


class ScoreWeights(BaseModel):
    """Configuration for rule weights."""
    cost: float = Field(default=0.20, ge=0, le=1)
    delivery: float = Field(default=0.15, ge=0, le=1)
    moq: float = Field(default=0.15, ge=0, le=1)
    availability: float = Field(default=0.15, ge=0, le=1)
    reliability: float = Field(default=0.15, ge=0, le=1)
    flexibility: float = Field(default=0.10, ge=0, le=1)
    data_quality: float = Field(default=0.10, ge=0, le=1)
    
    def validate_weights(self) -> bool:
        """Validate that weights sum to approximately 1.0."""
        total = sum([
            self.cost, self.delivery, self.moq, self.availability,
            self.reliability, self.flexibility, self.data_quality
        ])
        return 0.95 <= total <= 1.05


class SupplierScoreResult(BaseModel):
    """Result of supplier scoring."""
    overall_score: float = Field(..., ge=0, le=100)
    confidence_score: float = Field(..., ge=0, le=100)
    recommendation: Recommendation
    reasoning: str
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    rule_results: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SupplierScoreEngine:
    """
    Main scoring engine for supplier intelligence.
    
    Orchestrates multiple rules to generate comprehensive supplier evaluations.
    """
    
    def __init__(self, weights: Optional[ScoreWeights] = None):
        """
        Initialize the scoring engine.
        
        Args:
            weights: Optional custom weights
        """
        self.weights = weights or ScoreWeights()
        self.registry = get_registry()
    
    def evaluate(
        self,
        offer_data: Dict[str, Any],
        supplier_metadata: Optional[Dict[str, Any]] = None,
        product_data: Optional[Dict[str, Any]] = None
    ) -> SupplierScoreResult:
        """
        Evaluate a supplier offer using all registered rules.
        
        Args:
            offer_data: Offer data to evaluate
            supplier_metadata: Optional supplier metadata
            product_data: Optional product data
            
        Returns:
            SupplierScoreResult with comprehensive evaluation
        """
        # Add supplier metadata to offer data for rule evaluation
        if supplier_metadata:
            offer_data["supplier_metadata"] = supplier_metadata
        
        rule_results = {}
        weighted_scores = {}
        total_weighted_score = 0.0
        total_weight = 0.0
        
        # Get weight mapping
        weight_map = {
            "cost": self.weights.cost,
            "delivery": self.weights.delivery,
            "moq": self.weights.moq,
            "availability": self.weights.availability,
            "reliability": self.weights.reliability,
            "flexibility": self.weights.flexibility,
            "data_quality": self.weights.data_quality
        }
        
        # Evaluate each rule
        for rule_name in self.registry.list_rules():
            try:
                rule = self.registry.get_rule(rule_name, weight=weight_map.get(rule_name, 0.1))
                
                # Skip disabled rules
                if not rule.is_enabled():
                    continue
                
                result = rule.evaluate(offer_data, product_data)
                
                rule_results[rule_name] = result.dict()
                weighted_score = result.score * rule.get_weight()
                weighted_scores[rule_name] = weighted_score
                
                total_weighted_score += weighted_score
                total_weight += rule.get_weight()
                
            except Exception as e:
                # Log error in production
                continue
        
        # Calculate overall score
        overall_score = total_weighted_score / total_weight if total_weight > 0 else 0
        overall_score = min(100, max(0, overall_score))
        
        # Calculate confidence score (average of rule confidences)
        confidences = [r.get("confidence", 50) for r in rule_results.values()]
        confidence_score = sum(confidences) / len(confidences) if confidences else 50
        
        # Generate recommendation
        recommendation = self._generate_recommendation(overall_score, confidence_score)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(rule_results, overall_score)
        
        # Identify strengths and weaknesses
        strengths, weaknesses = self._identify_strengths_weaknesses(rule_results)
        
        return SupplierScoreResult(
            overall_score=round(overall_score, 2),
            confidence_score=round(confidence_score, 2),
            recommendation=recommendation,
            reasoning=reasoning,
            strengths=strengths,
            weaknesses=weaknesses,
            rule_results=rule_results,
            metadata={
                "total_weight": total_weight,
                "rules_evaluated": len(rule_results),
                "weights_used": weight_map
            }
        )
    
    def _generate_recommendation(self, overall_score: float, confidence_score: float) -> Recommendation:
        """
        Generate recommendation based on scores.
        
        Args:
            overall_score: Overall supplier score
            confidence_score: Confidence in the evaluation
            
        Returns:
            Recommendation level
        """
        # Adjust for low confidence
        if confidence_score < 50:
            return Recommendation.CONSIDER
        
        if overall_score >= 75:
            return Recommendation.STRONG_RECOMMEND
        elif overall_score >= 60:
            return Recommendation.RECOMMEND
        elif overall_score >= 40:
            return Recommendation.CONSIDER
        else:
            return Recommendation.AVOID
    
    def _generate_reasoning(self, rule_results: Dict[str, Any], overall_score: float) -> str:
        """
        Generate comprehensive reasoning for the recommendation.
        
        Args:
            rule_results: Results from individual rules
            overall_score: Overall supplier score
            
        Returns:
            Reasoning string
        """
        # Get top performing and bottom performing rules
        sorted_rules = sorted(
            rule_results.items(),
            key=lambda x: x[1].get("score", 0),
            reverse=True
        )
        
        top_3 = sorted_rules[:3]
        bottom_3 = sorted_rules[-3:]
        
        reasoning_parts = []
        
        # Overall assessment
        if overall_score >= 70:
            reasoning_parts.append("This supplier shows strong overall performance with multiple favorable factors.")
        elif overall_score >= 50:
            reasoning_parts.append("This supplier shows moderate overall performance with mixed factors.")
        else:
            reasoning_parts.append("This supplier shows limited overall performance with significant challenges.")
        
        # Top factors
        if top_3:
            top_names = [r[0].replace("_", " ").title() for r in top_3]
            reasoning_parts.append(f"Key strengths: {', '.join(top_names)}.")
        
        # Bottom factors
        if bottom_3:
            bottom_names = [r[0].replace("_", " ").title() for r in bottom_3]
            reasoning_parts.append(f"Areas of concern: {', '.join(bottom_names)}.")
        
        return " ".join(reasoning_parts)
    
    def _identify_strengths_weaknesses(self, rule_results: Dict[str, Any]) -> tuple[List[str], List[str]]:
        """
        Identify strengths and weaknesses from rule results.
        
        Args:
            rule_results: Results from individual rules
            
        Returns:
            Tuple of (strengths, weaknesses)
        """
        strengths = []
        weaknesses = []
        
        for rule_name, result in rule_results.items():
            score = result.get("score", 0)
            reasoning = result.get("reasoning", "")
            
            if score >= 70:
                strengths.append(f"{rule_name.replace('_', ' ').title()}: {reasoning}")
            elif score <= 40:
                weaknesses.append(f"{rule_name.replace('_', ' ').title()}: {reasoning}")
        
        return strengths, weaknesses
    
    def update_weights(self, new_weights: ScoreWeights) -> None:
        """
        Update scoring weights.
        
        Args:
            new_weights: New weight configuration
            
        Raises:
            ValueError: If weights don't sum to approximately 1.0
        """
        if not new_weights.validate_weights():
            raise ValueError("Weights must sum to approximately 1.0")
        
        self.weights = new_weights
    
    def get_weights(self) -> ScoreWeights:
        """Get current weights."""
        return self.weights
