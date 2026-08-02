"""
UXOptimizer

Analysis-only: never mutates the blueprint. Scores visual hierarchy,
section density, CTA clarity, readability, and spacing signals, and returns
actionable suggestions.
"""

from typing import Any, Dict, List

from .base import BaseOptimizer
from .models import OptimizerResult, Suggestion, clamp_score

MIN_SECTIONS = 3
MAX_SECTIONS = 8
MAX_HEADLINE_LENGTH = 90


class UXOptimizer(BaseOptimizer):
    """Read-only UX analysis of the store blueprint."""

    name = "ux"

    def optimize(self, blueprint: Dict[str, Any]) -> OptimizerResult:
        suggestions: List[Suggestion] = []
        score = 100.0
        homepage = blueprint.get("homepage") or []
        enabled_sections = [s for s in homepage if s.get("enabled", True)]

        score -= self._check_hierarchy(homepage, suggestions)
        score -= self._check_density(enabled_sections, suggestions)
        ctas = self._collect_ctas(homepage)
        score -= self._check_ctas(ctas, suggestions)
        score -= self._check_readability(homepage, suggestions)
        score -= self._check_spacing(blueprint, suggestions)

        return OptimizerResult(
            optimizer=self.name,
            score=clamp_score(score),
            suggestions=suggestions,
            details={
                "section_count": len(enabled_sections),
                "cta_variants": len(set(ctas)),
            },
        )

    def _check_hierarchy(self, homepage: List[Dict[str, Any]], suggestions: List[Suggestion]) -> float:
        if not homepage:
            suggestions.append(Suggestion(
                id="ux-empty-homepage",
                optimizer=self.name,
                severity="high",
                title="Homepage has no sections",
                description="An empty homepage has no visual hierarchy at all.",
                applied=False,
            ))
            return 40.0
        if homepage[0].get("section_type") != "hero":
            suggestions.append(Suggestion(
                id="ux-hero-not-first",
                optimizer=self.name,
                severity="medium",
                title="Lead with the hero section",
                description="The hero section should be the first thing visitors see.",
                applied=False,
            ))
            return 15.0
        return 0.0

    def _check_density(self, enabled_sections: List[Dict[str, Any]], suggestions: List[Suggestion]) -> float:
        count = len(enabled_sections)
        if count < MIN_SECTIONS:
            suggestions.append(Suggestion(
                id="ux-homepage-too-thin",
                optimizer=self.name,
                severity="high",
                title="Homepage feels thin",
                description="Add more sections (features, testimonials, trust) to build visitor confidence.",
                applied=False,
            ))
            return 20.0
        if count > MAX_SECTIONS:
            suggestions.append(Suggestion(
                id="ux-homepage-too-dense",
                optimizer=self.name,
                severity="medium",
                title="Homepage may be too dense",
                description="Consider trimming sections to reduce cognitive load and improve scan-ability.",
                applied=False,
            ))
            return 10.0
        return 0.0

    def _collect_ctas(self, homepage: List[Dict[str, Any]]) -> List[str]:
        ctas = []
        for section in homepage:
            content = section.get("content")
            if isinstance(content, dict) and content.get("cta"):
                ctas.append(content["cta"])
        return ctas

    def _check_ctas(self, ctas: List[str], suggestions: List[Suggestion]) -> float:
        if not ctas:
            suggestions.append(Suggestion(
                id="ux-no-cta",
                optimizer=self.name,
                severity="high",
                title="No call-to-action found",
                description="At least one clear call-to-action is required to drive conversions.",
                applied=False,
            ))
            return 20.0
        if len(set(ctas)) > 3:
            suggestions.append(Suggestion(
                id="ux-too-many-ctas",
                optimizer=self.name,
                severity="low",
                title="Too many distinct CTAs",
                description="Keep a single, consistent primary call-to-action across the homepage.",
                applied=False,
            ))
            return 5.0
        return 0.0

    def _check_readability(self, homepage: List[Dict[str, Any]], suggestions: List[Suggestion]) -> float:
        hero = next((s for s in homepage if s.get("section_type") == "hero"), None)
        if not hero:
            return 0.0
        headline = (hero.get("content", {}) or {}).get("headline", "")
        if len(headline) > MAX_HEADLINE_LENGTH:
            suggestions.append(Suggestion(
                id="ux-headline-too-long",
                optimizer=self.name,
                severity="low",
                title="Headline hurts readability",
                description=f"The headline is {len(headline)} characters; long headlines reduce comprehension speed.",
                applied=False,
            ))
            return 10.0
        return 0.0

    def _check_spacing(self, blueprint: Dict[str, Any], suggestions: List[Suggestion]) -> float:
        theme = blueprint.get("theme") or {}
        if not theme.get("spacing"):
            suggestions.append(Suggestion(
                id="ux-missing-spacing",
                optimizer=self.name,
                severity="low",
                title="Define theme spacing",
                description="No spacing value found in the theme; consistent spacing improves visual rhythm.",
                applied=False,
            ))
            return 5.0
        return 0.0
