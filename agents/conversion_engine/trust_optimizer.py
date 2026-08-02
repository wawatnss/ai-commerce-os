"""
TrustOptimizer

Ensures the store blueprint carries the standard trust signals that reduce
purchase hesitation: guarantees, secure payment, shipping info, a returns
policy, and social proof badges.
"""

from typing import Any, Dict, List, Tuple

from .base import BaseOptimizer
from .models import OptimizerResult, Suggestion, clamp_score

# category -> (badge label to add, keywords that mean "already covered")
TRUST_CATEGORIES: Dict[str, Tuple[str, Tuple[str, ...]]] = {
    "payment": ("Secure Payment", ("secure", "payment", "ssl")),
    "shipping": ("Free Shipping", ("shipping",)),
    "returns": ("Easy 30-Day Returns", ("return",)),
    "guarantee": ("Money-Back Guarantee", ("guarantee", "money-back", "money back")),
    "social_proof": ("Verified Customer Reviews", ("review", "testimonial", "verified")),
}

DEFAULT_POLICIES = {
    "refund_policy": {
        "title": "Refund Policy",
        "days": 30,
        "conditions": ["Unused items", "Original packaging", "Within 30 days"],
        "process": "Contact our support team within 30 days of purchase",
    },
    "shipping_policy": {
        "title": "Shipping Policy",
        "free_shipping_threshold": 50,
        "shipping_times": {"standard": "5-7 business days", "express": "2-3 business days"},
        "international": "Available",
    },
}


class TrustOptimizer(BaseOptimizer):
    """Adds missing trust signals (badges + baseline policies)."""

    name = "trust"

    def optimize(self, blueprint: Dict[str, Any]) -> OptimizerResult:
        suggestions: List[Suggestion] = []
        score = 100.0

        badges = list(blueprint.get("trust_badges") or [])
        existing_lower = " | ".join(badges).lower()

        added: List[str] = []
        for label, keywords in TRUST_CATEGORIES.values():
            if not any(keyword in existing_lower for keyword in keywords):
                badges.append(label)
                added.append(label)
        blueprint["trust_badges"] = badges

        self._sync_homepage_trust_section(blueprint, badges, suggestions)

        policies_added = self._ensure_baseline_policies(blueprint, suggestions)

        if added:
            suggestions.append(Suggestion(
                id="trust-missing-badges",
                optimizer=self.name,
                severity="high" if len(added) >= 3 else "medium",
                title="Add missing trust signals",
                description=f"Added: {', '.join(added)}.",
            ))
            score -= min(50.0, len(added) * 10.0)

        if policies_added:
            score -= 10.0

        return OptimizerResult(
            optimizer=self.name,
            score=clamp_score(score),
            suggestions=suggestions,
            details={"trust_badges": badges},
        )

    def _sync_homepage_trust_section(
        self, blueprint: Dict[str, Any], badges: List[str], suggestions: List[Suggestion]
    ) -> None:
        homepage = blueprint.setdefault("homepage", [])
        trust_section = next((s for s in homepage if s.get("section_type") == "trust"), None)
        if trust_section is None:
            homepage.append({
                "section_type": "trust",
                "title": "Why Shop With Us",
                "content": {"badges": badges},
                "order": len(homepage),
                "enabled": True,
            })
            suggestions.append(Suggestion(
                id="trust-missing-section",
                optimizer=self.name,
                severity="high",
                title="Add a trust badges section",
                description="The homepage had no dedicated trust section; added one.",
            ))
        else:
            trust_section.setdefault("content", {})["badges"] = badges

    def _ensure_baseline_policies(self, blueprint: Dict[str, Any], suggestions: List[Suggestion]) -> bool:
        policies = blueprint.setdefault("policies", {})
        added_any = False
        for key, default_value in DEFAULT_POLICIES.items():
            if not policies.get(key):
                policies[key] = default_value
                added_any = True
        if added_any:
            suggestions.append(Suggestion(
                id="trust-missing-policies",
                optimizer=self.name,
                severity="medium",
                title="Add baseline store policies",
                description="Added default shipping/refund policy content where missing.",
            ))
        return added_any
