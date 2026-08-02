"""
Score Engine for Trend Intelligence

This module implements a flexible, extensible scoring engine that calculates
overall trend scores from multiple indicators. New scoring criteria can be
easily added without modifying the core engine.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
from pydantic import BaseModel, Field
from enum import Enum
import numpy as np


class ScoringCriterion(str, Enum):
    """Enumeration of available scoring criteria."""
    POPULARITY = "popularity"
    GROWTH = "growth"
    COMPETITION = "competition"
    OPPORTUNITY = "opportunity"
    CONFIDENCE = "confidence"
    SEASONALITY = "seasonality"
    MARKET_SIZE = "market_size"
    PROFITABILITY = "profitability"


class ScoreWeights(BaseModel):
    """
    Configuration for score weights.
    
    Defines how much each criterion contributes to the overall score.
    All weights should sum to 1.0.
    """
    popularity: float = Field(default=0.25, ge=0, le=1, description="Weight for popularity score")
    growth: float = Field(default=0.25, ge=0, le=1, description="Weight for growth score")
    competition: float = Field(default=0.15, ge=0, le=1, description="Weight for competition score")
    opportunity: float = Field(default=0.20, ge=0, le=1, description="Weight for opportunity score")
    confidence: float = Field(default=0.15, ge=0, le=1, description="Weight for confidence score")
    
    def validate_weights(self) -> bool:
        """Validate that weights sum to approximately 1.0."""
        total = sum([
            self.popularity, self.growth, self.competition,
            self.opportunity, self.confidence
        ])
        return 0.95 <= total <= 1.05


class ScoringResult(BaseModel):
    """Result of a scoring calculation."""
    overall_score: float = Field(..., ge=0, le=100, description="Overall score (0-100)")
    component_scores: Dict[str, float] = Field(default_factory=dict, description="Individual component scores")
    weighted_scores: Dict[str, float] = Field(default_factory=dict, description="Weighted component scores")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional scoring metadata")


class BaseScorer(ABC):
    """
    Abstract base class for scoring components.
    
    Each scoring component (e.g., popularity scorer, growth scorer) should
    inherit from this class and implement the scoring logic.
    """
    
    def __init__(self, weight: float = 1.0, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the scorer.
        
        Args:
            weight: Weight for this scorer in the overall calculation
            config: Optional configuration for the scorer
        """
        self.weight = weight
        self.config = config or {}
        self.scorer_name = self.__class__.__name__.replace("Scorer", "").lower()
    
    @abstractmethod
    def score(self, data: Dict[str, Any]) -> float:
        """
        Calculate a score for the given data.
        
        Args:
            data: Dictionary containing relevant data for scoring
            
        Returns:
            Score between 0 and 100
        """
        pass
    
    def get_weight(self) -> float:
        """Get the scorer's weight."""
        return self.weight
    
    def get_name(self) -> str:
        """Get the scorer's name."""
        return self.scorer_name


class PopularityScorer(BaseScorer):
    """Scores based on popularity metrics."""
    
    def score(self, data: Dict[str, Any]) -> float:
        """
        Calculate popularity score.
        
        Args:
            data: Dictionary containing popularity metrics
            
        Returns:
            Popularity score (0-100)
        """
        popularity_score = data.get("popularity_score", 0)
        
        # Apply any configured transformations
        if self.config.get("log_transform", False):
            popularity_score = np.log1p(popularity_score) * 20
        
        return min(100, max(0, popularity_score))


class GrowthScorer(BaseScorer):
    """Scores based on growth metrics."""
    
    def score(self, data: Dict[str, Any]) -> float:
        """
        Calculate growth score.
        
        Args:
            data: Dictionary containing growth metrics
            
        Returns:
            Growth score (0-100)
        """
        growth_score = data.get("growth_score", 0)
        
        # Apply bonus for exponential growth
        if self.config.get("exponential_bonus", False) and growth_score > 80:
            growth_score = min(100, growth_score * 1.1)
        
        return min(100, max(0, growth_score))


class CompetitionScorer(BaseScorer):
    """Scores based on competition level (inverted - lower competition is better)."""
    
    def score(self, data: Dict[str, Any]) -> float:
        """
        Calculate competition score (inverted).
        
        Args:
            data: Dictionary containing competition metrics
            
        Returns:
            Competition score (0-100, where 100 = low competition)
        """
        competition_score = data.get("competition_score", 50)
        
        # Invert: high competition = low score
        inverted_score = 100 - competition_score
        
        return min(100, max(0, inverted_score))


class OpportunityScorer(BaseScorer):
    """Scores based on opportunity metrics."""
    
    def score(self, data: Dict[str, Any]) -> float:
        """
        Calculate opportunity score.
        
        Args:
            data: Dictionary containing opportunity metrics
            
        Returns:
            Opportunity score (0-100)
        """
        opportunity_score = data.get("opportunity_score", 0)
        
        # Apply multiplier for high-growth, low-competition items
        growth = data.get("growth_score", 0)
        competition = data.get("competition_score", 50)
        
        if growth > 70 and competition < 30:
            opportunity_score = min(100, opportunity_score * 1.15)
        
        return min(100, max(0, opportunity_score))


class ConfidenceScorer(BaseScorer):
    """Scores based on data confidence/reliability."""
    
    def score(self, data: Dict[str, Any]) -> float:
        """
        Calculate confidence score.
        
        Args:
            data: Dictionary containing confidence metrics
            
        Returns:
            Confidence score (0-100)
        """
        confidence_score = data.get("confidence_score", 50)
        
        # Apply time decay for older data
        detected_at = data.get("detected_at")
        if detected_at and self.config.get("time_decay", True):
            from datetime import datetime, timedelta
            age_hours = (datetime.utcnow() - detected_at).total_seconds() / 3600
            decay_factor = max(0.5, 1 - (age_hours / 168))  # Decay over 1 week
            confidence_score *= decay_factor
        
        return min(100, max(0, confidence_score))


class ScoreEngine:
    """
    Main scoring engine that orchestrates multiple scorers.
    
    This engine manages a collection of scorers and calculates overall
    scores by combining individual scorer results with configurable weights.
    """
    
    def __init__(self, weights: Optional[ScoreWeights] = None):
        """
        Initialize the scoring engine.
        
        Args:
            weights: Optional custom weights (defaults to equal weights)
        """
        self.weights = weights or ScoreWeights()
        self.scorers: Dict[str, BaseScorer] = {}
        self._register_default_scorers()
    
    def _register_default_scorers(self) -> None:
        """Register the default scoring components."""
        self.register_scorer("popularity", PopularityScorer(weight=self.weights.popularity))
        self.register_scorer("growth", GrowthScorer(weight=self.weights.growth))
        self.register_scorer("competition", CompetitionScorer(weight=self.weights.competition))
        self.register_scorer("opportunity", OpportunityScorer(weight=self.weights.opportunity))
        self.register_scorer("confidence", ConfidenceScorer(weight=self.weights.confidence))
    
    def register_scorer(self, name: str, scorer: BaseScorer) -> None:
        """
        Register a custom scorer.
        
        Args:
            name: Name for the scorer
            scorer: Scorer instance
        """
        self.scorers[name] = scorer
    
    def unregister_scorer(self, name: str) -> None:
        """
        Unregister a scorer.
        
        Args:
            name: Name of the scorer to remove
        """
        if name in self.scorers:
            del self.scorers[name]
    
    def calculate_score(self, data: Dict[str, Any]) -> ScoringResult:
        """
        Calculate overall score for the given data.
        
        Args:
            data: Dictionary containing trend data
            
        Returns:
            ScoringResult with overall score and component breakdown
        """
        component_scores = {}
        weighted_scores = {}
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for name, scorer in self.scorers.items():
            # Calculate component score
            component_score = scorer.score(data)
            component_scores[name] = round(component_score, 2)
            
            # Apply weight
            weight = scorer.get_weight()
            weighted_score = component_score * weight
            weighted_scores[name] = round(weighted_score, 2)
            
            total_weighted_score += weighted_score
            total_weight += weight
        
        # Calculate overall score
        overall_score = total_weighted_score / total_weight if total_weight > 0 else 0
        overall_score = min(100, max(0, overall_score))
        
        return ScoringResult(
            overall_score=round(overall_score, 2),
            component_scores=component_scores,
            weighted_scores=weighted_scores,
            metadata={
                "total_weight": total_weight,
                "scorers_used": list(self.scorers.keys())
            }
        )
    
    def calculate_batch_scores(self, data_list: List[Dict[str, Any]]) -> List[ScoringResult]:
        """
        Calculate scores for multiple data items.
        
        Args:
            data_list: List of trend data dictionaries
            
        Returns:
            List of ScoringResult objects
        """
        return [self.calculate_score(data) for data in data_list]
    
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
        self.scorers.clear()
        self._register_default_scorers()
    
    def get_scorers(self) -> Dict[str, BaseScorer]:
        """
        Get all registered scorers.
        
        Returns:
            Dictionary of scorer name to scorer instance
        """
        return self.scorers.copy()


class ScoreOptimizer:
    """
    Utility for optimizing score weights based on historical performance.
    
    This class can be used to adjust scoring weights based on which
    criteria best predict successful trends.
    """
    
    def __init__(self, engine: ScoreEngine):
        """
        Initialize the optimizer.
        
        Args:
            engine: ScoreEngine instance to optimize
        """
        self.engine = engine
        self.historical_data: List[Dict[str, Any]] = []
    
    def add_historical_data(self, data: Dict[str, Any], actual_performance: float) -> None:
        """
        Add historical performance data.
        
        Args:
            data: Trend data that was scored
            actual_performance: Actual performance metric (e.g., sales, revenue)
        """
        self.historical_data.append({
            "data": data,
            "performance": actual_performance
        })
    
    def optimize_weights(self) -> ScoreWeights:
        """
        Calculate optimal weights based on historical data.
        
        This is a simple implementation that can be enhanced with
        more sophisticated optimization algorithms.
        
        Returns:
            Optimized ScoreWeights
        """
        if len(self.historical_data) < 10:
            # Not enough data, return current weights
            return self.weights
        
        # Simple correlation-based optimization
        # In production, use more sophisticated methods
        correlations = {}
        
        for scorer_name in self.engine.get_scorers().keys():
            scorer = self.engine.scorers[scorer_name]
            scores = [scorer.score(item["data"]) for item in self.historical_data]
            performances = [item["performance"] for item in self.historical_data]
            
            # Calculate correlation (simplified)
            correlation = np.corrcoef(scores, performances)[0, 1] if len(scores) > 1 else 0
            correlations[scorer_name] = max(0, correlation)  # Only positive correlations
        
        # Normalize correlations to create weights
        total_correlation = sum(correlations.values()) or 1
        optimized_weights = {}
        
        for scorer_name, correlation in correlations.items():
            optimized_weights[scorer_name] = correlation / total_correlation
        
        return ScoreWeights(**optimized_weights)
