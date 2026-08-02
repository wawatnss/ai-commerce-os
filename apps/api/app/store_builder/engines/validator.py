"""
Store Validator

Validates generated store for coherence, SEO, UX, accessibility, responsive, performance.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field


class StoreValidationResult(BaseModel):
    """Result of store validation."""
    overall_score: float = Field(..., ge=0, le=100, description="Overall validation score")
    coherence_score: float = Field(..., ge=0, le=100, description="Coherence score")
    seo_score: float = Field(..., ge=0, le=100, description="SEO score")
    ux_score: float = Field(..., ge=0, le=100, description="UX score")
    accessibility_score: float = Field(..., ge=0, le=100, description="Accessibility score")
    responsive_score: float = Field(..., ge=0, le=100, description="Responsive score")
    performance_score: float = Field(..., ge=0, le=100, description="Performance score")
    strengths: List[str] = Field(default_factory=list, description="Identified strengths")
    weaknesses: List[str] = Field(default_factory=list, description="Identified weaknesses")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")


class StoreValidator:
    """Validator for store blueprints."""
    
    def validate(self, store_blueprint: Dict[str, Any]) -> StoreValidationResult:
        """Validate a complete store blueprint."""
        strengths = []
        weaknesses = []
        suggestions = []
        
        # Validate coherence
        coherence_score = self._validate_coherence(store_blueprint, strengths, weaknesses, suggestions)
        
        # Validate SEO
        seo_score = self._validate_seo(store_blueprint, strengths, weaknesses, suggestions)
        
        # Validate UX
        ux_score = self._validate_ux(store_blueprint, strengths, weaknesses, suggestions)
        
        # Validate accessibility
        accessibility_score = self._validate_accessibility(store_blueprint, strengths, weaknesses, suggestions)
        
        # Validate responsive
        responsive_score = self._validate_responsive(store_blueprint, strengths, weaknesses, suggestions)
        
        # Validate performance
        performance_score = self._validate_performance(store_blueprint, strengths, weaknesses, suggestions)
        
        # Calculate overall score
        overall_score = (
            coherence_score * 0.2 +
            seo_score * 0.2 +
            ux_score * 0.2 +
            accessibility_score * 0.15 +
            responsive_score * 0.15 +
            performance_score * 0.1
        )
        
        return StoreValidationResult(
            overall_score=round(overall_score, 2),
            coherence_score=coherence_score,
            seo_score=seo_score,
            ux_score=ux_score,
            accessibility_score=accessibility_score,
            responsive_score=responsive_score,
            performance_score=performance_score,
            strengths=strengths,
            weaknesses=weaknesses,
            suggestions=suggestions
        )
    
    def _validate_coherence(self, store: Dict[str, Any], strengths: List[str], weaknesses: List[str], suggestions: List[str]) -> float:
        """Validate store coherence."""
        score = 80
        
        if store.get("store_name") and store.get("store_description"):
            score += 10
            strengths.append("Store has name and description")
        else:
            score -= 20
            weaknesses.append("Missing store name or description")
        
        if store.get("homepage"):
            score += 10
            strengths.append("Homepage configured")
        
        return min(100, max(0, score))
    
    def _validate_seo(self, store: Dict[str, Any], strengths: List[str], weaknesses: List[str], suggestions: List[str]) -> float:
        """Validate SEO configuration."""
        score = 75
        
        seo = store.get("seo", {})
        if seo.get("title_template") and seo.get("meta_description_template"):
            score += 15
            strengths.append("SEO templates configured")
        else:
            score -= 15
            weaknesses.append("Missing SEO templates")
        
        if seo.get("keywords"):
            score += 10
            strengths.append("Keywords defined")
        
        return min(100, max(0, score))
    
    def _validate_ux(self, store: Dict[str, Any], strengths: List[str], weaknesses: List[str], suggestions: List[str]) -> float:
        """Validate UX design."""
        score = 75
        
        if store.get("navigation") and store.get("navigation", {}).get("main_menu"):
            score += 10
            strengths.append("Navigation configured")
        
        if store.get("homepage"):
            score += 10
            strengths.append("Homepage sections defined")
        
        return min(100, max(0, score))
    
    def _validate_accessibility(self, store: Dict[str, Any], strengths: List[str], weaknesses: List[str], suggestions: List[str]) -> float:
        """Validate accessibility."""
        score = 70
        
        theme = store.get("theme", {})
        if theme.get("dark_mode_enabled"):
            score += 15
            strengths.append("Dark mode supported")
        
        if theme.get("font_family"):
            score += 10
            strengths.append("Font configured")
        
        return min(100, max(0, score))
    
    def _validate_responsive(self, store: Dict[str, Any], strengths: List[str], weaknesses: List[str], suggestions: List[str]) -> float:
        """Validate responsive design."""
        score = 80
        
        theme = store.get("theme", {})
        if theme.get("spacing"):
            score += 10
            strengths.append("Responsive spacing configured")
        
        return min(100, max(0, score))
    
    def _validate_performance(self, store: Dict[str, Any], strengths: List[str], weaknesses: List[str], suggestions: List[str]) -> float:
        """Validate performance considerations."""
        score = 75
        
        theme = store.get("theme", {})
        if not theme.get("animations_enabled") or theme.get("animations_enabled") is False:
            score += 10
            strengths.append("Animations optimized")
        else:
            suggestions.append("Consider disabling animations for better performance")
        
        return min(100, max(0, score))
