"""
Product Score Engine

This module implements the scoring engine that orchestrates rules and generates
comprehensive product intelligence reports.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from ..rules import get_registry, RuleResult
from ..schemas.product import Recommendation


class ScoreWeights(BaseModel):
    """Configuration for rule weights."""
    estimated_margin: float = Field(default=0.15, ge=0, le=1)
    demand: float = Field(default=0.15, ge=0, le=1)
    competition: float = Field(default=0.12, ge=0, le=1)
    seasonality: float = Field(default=0.08, ge=0, le=1)
    shipping: float = Field(default=0.08, ge=0, le=1)
    impulse_buy: float = Field(default=0.08, ge=0, le=1)
    content_potential: float = Field(default=0.10, ge=0, le=1)
    seo: float = Field(default=0.10, ge=0, le=1)
    supplier_availability: float = Field(default=0.07, ge=0, le=1)
    return_risk: float = Field(default=0.04, ge=0, le=1)
    legal_risk: float = Field(default=0.03, ge=0, le=1)
    
    def validate_weights(self) -> bool:
        """Validate that weights sum to approximately 1.0."""
        total = sum([
            self.estimated_margin, self.demand, self.competition,
            self.seasonality, self.shipping, self.impulse_buy,
            self.content_potential, self.seo, self.supplier_availability,
            self.return_risk, self.legal_risk
        ])
        return 0.95 <= total <= 1.05


class ProductScoreResult(BaseModel):
    """Result of product scoring."""
    overall_score: float = Field(..., ge=0, le=100)
    confidence_score: float = Field(..., ge=0, le=100)
    recommendation: Recommendation
    reasoning: str
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    rule_results: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ProductScoreEngine:
    """
    Main scoring engine for product intelligence.
    
    Orchestrates multiple rules to generate comprehensive product evaluations.
    """
    
    def __init__(self, weights: Optional[ScoreWeights] = None):
        """
        Initialize the scoring engine.
        
        Args:
            weights: Optional custom weights
        """
        self.weights = weights or ScoreWeights()
        self.registry = get_registry()
    
    def analyze(self, trend_data: Dict[str, Any]) -> ProductScoreResult:
        """
        Analyze a product using all registered rules.
        
        Args:
            trend_data: Trend data to analyze
            
        Returns:
            ProductScoreResult with comprehensive analysis
        """
        rule_results = {}
        weighted_scores = {}
        total_weighted_score = 0.0
        total_weight = 0.0
        
        # Get weight mapping
        weight_map = {
            "estimated_margin": self.weights.estimated_margin,
            "demand": self.weights.demand,
            "competition": self.weights.competition,
            "seasonality": self.weights.seasonality,
            "shipping": self.weights.shipping,
            "impulse_buy": self.weights.impulse_buy,
            "content_potential": self.weights.content_potential,
            "seo": self.weights.seo,
            "supplier_availability": self.weights.supplier_availability,
            "return_risk": self.weights.return_risk,
            "legal_risk": self.weights.legal_risk
        }
        
        # Evaluate each rule
        for rule_name in self.registry.list_rules():
            try:
                rule = self.registry.get_rule(rule_name, weight=weight_map.get(rule_name, 0.1))
                result = rule.evaluate(trend_data)
                
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
        
        return ProductScoreResult(
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
            overall_score: Overall product score
            confidence_score: Confidence in the analysis
            
        Returns:
            Recommendation level
        """
        # Adjust for low confidence
        if confidence_score < 50:
            return Recommendation.HOLD
        
        if overall_score >= 75:
            return Recommendation.STRONG_BUY
        elif overall_score >= 60:
            return Recommendation.BUY
        elif overall_score >= 40:
            return Recommendation.HOLD
        else:
            return Recommendation.AVOID
    
    def _generate_reasoning(self, rule_results: Dict[str, Any], overall_score: float) -> str:
        """
        Generate comprehensive reasoning for the recommendation.
        
        Args:
            rule_results: Results from individual rules
            overall_score: Overall product score
            
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
            reasoning_parts.append("This product shows strong commercial potential with multiple favorable factors.")
        elif overall_score >= 50:
            reasoning_parts.append("This product shows moderate commercial potential with mixed factors.")
        else:
            reasoning_parts.append("This product shows limited commercial potential with significant challenges.")
        
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
