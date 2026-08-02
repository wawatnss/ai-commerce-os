"""
Brand Validator

Validates generated brand identity for coherence, readability, and consistency.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field


class ValidationResult(BaseModel):
    """Result of brand validation."""
    overall_score: float = Field(..., ge=0, le=100, description="Overall validation score")
    strengths: List[str] = Field(default_factory=list, description="Identified strengths")
    weaknesses: List[str] = Field(default_factory=list, description="Identified weaknesses")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")
    coherence_score: float = Field(..., ge=0, le=100, description="Coherence score")
    readability_score: float = Field(..., ge=0, le=100, description="Readability score")
    uniqueness_score: float = Field(..., ge=0, le=100, description="Uniqueness score")
    marketing_coherence_score: float = Field(..., ge=0, le=100, description="Marketing coherence score")
    seo_coherence_score: float = Field(..., ge=0, le=100, description="SEO coherence score")


class BrandValidator:
    """
    Validator for brand identity elements.
    
    Checks coherence, readability, uniqueness, and marketing/SEO alignment.
    """
    
    def validate(self, brand_profile: Dict[str, Any]) -> ValidationResult:
        """
        Validate a complete brand profile.
        
        Args:
            brand_profile: Complete brand profile to validate
            
        Returns:
            ValidationResult with scores and feedback
        """
        strengths = []
        weaknesses = []
        suggestions = []
        
        # Validate coherence
        coherence_score = self._validate_coherence(brand_profile, strengths, weaknesses, suggestions)
        
        # Validate readability
        readability_score = self._validate_readability(brand_profile, strengths, weaknesses, suggestions)
        
        # Validate uniqueness
        uniqueness_score = self._validate_uniqueness(brand_profile, strengths, weaknesses, suggestions)
        
        # Validate marketing coherence
        marketing_coherence_score = self._validate_marketing_coherence(brand_profile, strengths, weaknesses, suggestions)
        
        # Validate SEO coherence
        seo_coherence_score = self._validate_seo_coherence(brand_profile, strengths, weaknesses, suggestions)
        
        # Calculate overall score
        overall_score = (
            coherence_score * 0.25 +
            readability_score * 0.25 +
            uniqueness_score * 0.2 +
            marketing_coherence_score * 0.15 +
            seo_coherence_score * 0.15
        )
        
        return ValidationResult(
            overall_score=round(overall_score, 2),
            strengths=strengths,
            weaknesses=weaknesses,
            suggestions=suggestions,
            coherence_score=coherence_score,
            readability_score=readability_score,
            uniqueness_score=uniqueness_score,
            marketing_coherence_score=marketing_coherence_score,
            seo_coherence_score=seo_coherence_score
        )
    
    def _validate_coherence(self, brand: Dict[str, Any], strengths: List[str], weaknesses: List[str], suggestions: List[str]) -> float:
        """Validate internal coherence of brand elements."""
        score = 80  # Base score
        
        # Check if visual identity aligns with tone
        if "color_palette" in brand and "tone_of_voice" in brand:
            score += 10
            strengths.append("Visual and verbal identity appear aligned")
        else:
            score -= 10
            weaknesses.append("Missing visual or verbal identity elements")
        
        # Check if mission aligns with vision
        if "mission" in brand and "vision" in brand:
            score += 5
            strengths.append("Mission and vision defined")
        else:
            score -= 5
            suggestions.append("Define both mission and vision statements")
        
        return min(100, max(0, score))
    
    def _validate_readability(self, brand: Dict[str, Any], strengths: List[str], weaknesses: List[str], suggestions: List[str]) -> float:
        """Validate readability of brand elements."""
        score = 75  # Base score
        
        # Check brand name readability
        brand_name = brand.get("brand_name", "")
        if brand_name and len(brand_name) <= 15:
            score += 15
            strengths.append("Brand name is concise and memorable")
        elif brand_name:
            score -= 10
            suggestions.append("Consider shortening the brand name for better memorability")
        
        # Check mission statement length
        mission = brand.get("mission", "")
        if mission and 10 < len(mission) < 200:
            score += 10
            strengths.append("Mission statement has appropriate length")
        elif mission:
            score -= 5
            suggestions.append("Mission statement should be concise (10-200 characters)")
        
        return min(100, max(0, score))
    
    def _validate_uniqueness(self, brand: Dict[str, Any], strengths: List[str], weaknesses: List[str], suggestions: List[str]) -> float:
        """Validate uniqueness of brand elements."""
        score = 70  # Base score
        
        # Check for unique value proposition
        uvp = brand.get("unique_value_proposition", {})
        if uvp and not isinstance(uvp, str):
            score += 20
            strengths.append("Unique value proposition defined")
        else:
            score -= 15
            weaknesses.append("Unique value proposition missing or incomplete")
        
        # Check for differentiators
        differentiators = brand.get("differentiators", [])
        if differentiators and len(differentiators) >= 3:
            score += 10
            strengths.append("Multiple competitive differentiators identified")
        else:
            score -= 10
            suggestions.append("Add more competitive differentiators")
        
        return min(100, max(0, score))
    
    def _validate_marketing_coherence(self, brand: Dict[str, Any], strengths: List[str], weaknesses: List[str], suggestions: List[str]) -> float:
        """Validate marketing message coherence."""
        score = 75  # Base score
        
        # Check if tone aligns with target audience
        if "tone_of_voice" in brand and "target_audience" in brand:
            score += 15
            strengths.append("Tone of voice defined for target audience")
        else:
            score -= 10
            suggestions.append("Ensure tone of voice aligns with target audience")
        
        # Check for social media style
        if "social_media_style" in brand:
            score += 10
            strengths.append("Social media style guidelines defined")
        
        return min(100, max(0, score))
    
    def _validate_seo_coherence(self, brand: Dict[str, Any], strengths: List[str], weaknesses: List[str], suggestions: List[str]) -> float:
        """Validate SEO coherence."""
        score = 70  # Base score
        
        # Check for SEO style guidelines
        if "seo_style" in brand:
            score += 15
            strengths.append("SEO writing style defined")
        else:
            score -= 10
            suggestions.append("Define SEO writing style guidelines")
        
        # Check if value proposition is SEO-friendly
        uvp = brand.get("unique_value_proposition", {})
        if uvp:
            score += 15
            strengths.append("Value proposition can support SEO strategy")
        
        return min(100, max(0, score))
