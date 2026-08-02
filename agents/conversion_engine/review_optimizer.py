"""
ReviewOptimizer

Builds the review/UGC structure (layout, badges, social-proof section) for
a store. Simulated ratings are ONLY ever generated in explicit `demo_mode`,
clearly flagged as simulated. For a real store, this optimizer NEVER
fabricates reviews, ratings, or review counts - it only prepares the
structure and flags that real reviews still need to be collected.
"""

import random
from typing import Any, Dict, List

from .base import BaseOptimizer
from .models import OptimizerResult, Suggestion, clamp_score


class ReviewOptimizer(BaseOptimizer):
    """Prepares the review/UGC structure; simulates data in demo mode only."""

    name = "reviews"

    def optimize(self, blueprint: Dict[str, Any], demo_mode: bool = False) -> OptimizerResult:
        suggestions: List[Suggestion] = []
        score = 100.0

        reviews_module = blueprint.setdefault("reviews_module", {})
        reviews_module.setdefault("structure", {
            "layout": "grid",
            "show_rating_summary": True,
            "show_verified_badge": True,
            "allow_photos": True,
        })
        reviews_module["ugc_section_enabled"] = True

        if demo_mode:
            score -= self._apply_demo_data(reviews_module, suggestions)
        else:
            score -= self._apply_real_store_safeguards(blueprint, reviews_module, suggestions)

        self._ensure_review_trust_badge(blueprint)

        return OptimizerResult(
            optimizer=self.name,
            score=clamp_score(score),
            suggestions=suggestions,
            details=reviews_module,
        )

    def _apply_demo_data(self, reviews_module: Dict[str, Any], suggestions: List[Suggestion]) -> float:
        if reviews_module.get("is_simulated"):
            return 0.0

        reviews_module["average_rating"] = round(random.uniform(4.4, 4.9), 1)
        reviews_module["review_count"] = random.randint(38, 240)
        reviews_module["is_simulated"] = True
        suggestions.append(Suggestion(
            id="reviews-demo-simulated-data",
            optimizer=self.name,
            severity="low",
            title="Simulated review data added (demo mode only)",
            description="A demo average rating and review count were generated for demonstration purposes only.",
        ))
        return 0.0

    def _apply_real_store_safeguards(
        self, blueprint: Dict[str, Any], reviews_module: Dict[str, Any], suggestions: List[Suggestion]
    ) -> float:
        # Never invent ratings/review counts for a real store.
        reviews_module.setdefault("average_rating", None)
        reviews_module.setdefault("review_count", 0)
        reviews_module["is_simulated"] = False

        if not blueprint.get("reviews"):
            suggestions.append(Suggestion(
                id="reviews-missing-real-reviews",
                optimizer=self.name,
                severity="high",
                title="Collect real customer reviews",
                description=(
                    "No reviews yet. Connect a review-collection tool (e.g. a post-purchase "
                    "email) before launch. Never fabricate reviews for a real store."
                ),
                applied=False,
            ))
            return 30.0
        return 0.0

    def _ensure_review_trust_badge(self, blueprint: Dict[str, Any]) -> None:
        badges = blueprint.setdefault("trust_badges", [])
        if not any("review" in b.lower() for b in badges):
            badges.append("Verified Customer Reviews")
