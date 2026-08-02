"""
PricingOptimizer

Prepares pricing STRATEGY RECOMMENDATIONS ONLY: psychological pricing,
discounts, bundles, and price anchoring. This optimizer must never modify
any actual price on the blueprint - it only ever returns suggestions for a
human (or a future, explicitly-approved automation) to apply.
"""

from typing import Any, Dict

from .base import BaseOptimizer
from .models import OptimizerResult, Suggestion


class PricingOptimizer(BaseOptimizer):
    """Advisory-only: never mutates prices, only suggests strategies."""

    name = "pricing"

    def optimize(self, blueprint: Dict[str, Any]) -> OptimizerResult:
        # Intentionally read-only: no blueprint field is ever modified here.
        suggestions = [
            Suggestion(
                id="pricing-charm",
                optimizer=self.name,
                severity="medium",
                title="Use charm pricing",
                description="Price items at $X.99 or $X.97 instead of round numbers to increase perceived value.",
                applied=False,
            ),
            Suggestion(
                id="pricing-anchor",
                optimizer=self.name,
                severity="medium",
                title="Add price anchoring",
                description="Show a higher 'compare at' price next to the sale price to make the offer feel like a deal.",
                applied=False,
            ),
            Suggestion(
                id="pricing-bundle",
                optimizer=self.name,
                severity="low",
                title="Offer bundles",
                description="Bundle complementary products at a slight discount to increase average order value.",
                applied=False,
            ),
            Suggestion(
                id="pricing-first-order-discount",
                optimizer=self.name,
                severity="low",
                title="Consider a first-order discount",
                description="A small first-purchase discount (5-10%) can reduce hesitation for new visitors.",
                applied=False,
            ),
        ]

        return OptimizerResult(
            optimizer=self.name,
            score=100.0,
            suggestions=suggestions,
            details={"note": "Recommendations only - no prices were modified.", "mutates_blueprint": False},
        )
