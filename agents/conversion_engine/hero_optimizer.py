"""
HeroOptimizer

Optimizes the homepage hero section (headline, subheadline, CTA) and
reorders homepage sections into a higher-converting flow:
hero -> features -> testimonials -> trust -> faq -> everything else.
"""

from typing import Any, Dict, List, Optional, Tuple

from .base import BaseOptimizer
from .models import OptimizerResult, Suggestion, clamp_score

SECTION_PRIORITY = {
    "hero": 0,
    "features": 1,
    "testimonials": 2,
    "trust": 3,
    "faq": 4,
    "comparison": 5,
}

URGENCY_WORDS = ("free", "now", "today", "save", "limited", "exclusive")


class HeroOptimizer(BaseOptimizer):
    """Optimizes the hero section and homepage section order."""

    name = "hero"

    def optimize(self, blueprint: Dict[str, Any]) -> OptimizerResult:
        suggestions: List[Suggestion] = []
        score = 100.0

        homepage = blueprint.setdefault("homepage", [])
        hero = self._find_or_create_hero(homepage, blueprint, suggestions)
        if hero is None:
            score -= 40
        else:
            content = hero.setdefault("content", {})
            score -= self._optimize_headline(content, blueprint, suggestions)
            score -= self._optimize_subheadline(content, blueprint, suggestions)
            score -= self._optimize_cta(content, blueprint, suggestions)

        reorder_suggestion = self._reorder_sections(homepage)
        if reorder_suggestion:
            suggestions.append(reorder_suggestion)

        return OptimizerResult(
            optimizer=self.name,
            score=clamp_score(score),
            suggestions=suggestions,
            details={
                "headline": hero.get("content", {}).get("headline") if hero else None,
                "cta": hero.get("content", {}).get("cta") if hero else None,
                "section_order": [s.get("section_type") for s in homepage],
            },
        )

    def _find_or_create_hero(
        self, homepage: List[Dict[str, Any]], blueprint: Dict[str, Any], suggestions: List[Suggestion]
    ) -> Optional[Dict[str, Any]]:
        hero = next((s for s in homepage if s.get("section_type") == "hero"), None)
        if hero is not None:
            return hero

        hero = {
            "section_type": "hero",
            "title": blueprint.get("tagline", "Welcome"),
            "content": {},
            "order": 0,
            "enabled": True,
        }
        homepage.insert(0, hero)
        suggestions.append(Suggestion(
            id="hero-missing-section",
            optimizer=self.name,
            severity="high",
            title="Add a hero section",
            description="The homepage had no hero section; added one at the top of the page.",
        ))
        return hero

    def _optimize_headline(
        self, content: Dict[str, Any], blueprint: Dict[str, Any], suggestions: List[Suggestion]
    ) -> float:
        headline = (content.get("headline") or "").strip()
        if not headline:
            content["headline"] = f"Discover {blueprint.get('store_name', 'Our Store')}"
            suggestions.append(Suggestion(
                id="hero-missing-headline",
                optimizer=self.name,
                severity="high",
                title="Add a headline",
                description="The hero section had no headline; generated one from the store name.",
            ))
            return 20.0
        if len(headline) > 70:
            suggestions.append(Suggestion(
                id="hero-headline-too-long",
                optimizer=self.name,
                severity="low",
                title="Shorten the headline",
                description=f"The headline is {len(headline)} characters; aim for under 70 for readability and impact.",
            ))
            return 5.0
        return 0.0

    def _optimize_subheadline(
        self, content: Dict[str, Any], blueprint: Dict[str, Any], suggestions: List[Suggestion]
    ) -> float:
        subheadline = (content.get("subheadline") or "").strip()
        if not subheadline:
            content["subheadline"] = blueprint.get("store_description", "Quality products, delivered fast.")
            suggestions.append(Suggestion(
                id="hero-missing-subheadline",
                optimizer=self.name,
                severity="medium",
                title="Add a subheadline",
                description="The hero section had no supporting subheadline; generated one from the store description.",
            ))
            return 15.0
        return 0.0

    def _optimize_cta(
        self, content: Dict[str, Any], blueprint: Dict[str, Any], suggestions: List[Suggestion]
    ) -> float:
        penalty = 0.0
        cta = (content.get("cta") or "").strip()
        if not cta or cta.lower() in {"click here", "submit", "learn more"}:
            content["cta"] = "Shop Now"
            cta = "Shop Now"
            suggestions.append(Suggestion(
                id="hero-weak-cta",
                optimizer=self.name,
                severity="high",
                title="Use an action-oriented CTA",
                description="Replaced a missing/generic call-to-action with 'Shop Now'.",
            ))
            penalty += 15.0

        if not any(word in cta.lower() for word in URGENCY_WORDS):
            shipping = (blueprint.get("policies") or {}).get("shipping_policy", {})
            threshold = shipping.get("free_shipping_threshold")
            if threshold:
                content["cta"] = f"{cta} \u2014 Free Shipping Over ${threshold}"
                suggestions.append(Suggestion(
                    id="hero-cta-benefit",
                    optimizer=self.name,
                    severity="low",
                    title="Add a benefit to the CTA",
                    description="Appended the free-shipping threshold to the CTA to reduce checkout hesitation.",
                ))
                penalty += 5.0
        return penalty

    def _reorder_sections(self, homepage: List[Dict[str, Any]]) -> Optional[Suggestion]:
        original_order = [s.get("section_type") for s in homepage]

        def sort_key(section: Dict[str, Any]) -> Tuple[int, int]:
            return (SECTION_PRIORITY.get(section.get("section_type"), 99), section.get("order", 0))

        homepage.sort(key=sort_key)
        for index, section in enumerate(homepage):
            section["order"] = index

        new_order = [s.get("section_type") for s in homepage]
        if new_order != original_order:
            return Suggestion(
                id="hero-reorder-sections",
                optimizer=self.name,
                severity="medium",
                title="Reorder homepage sections",
                description=f"Reordered sections into a higher-converting flow: {' -> '.join(new_order)}.",
            )
        return None
