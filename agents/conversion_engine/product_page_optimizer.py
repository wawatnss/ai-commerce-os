"""
ProductPageOptimizer

Optimizes the product-page content block: benefits, objection-handling FAQ,
a lightweight competitive comparison, features, and the primary CTA.

Note: the current Store Builder blueprint doesn't model an individual
product's full detail page (price/images/variants), so this optimizer works
at the store-blueprint level, producing a reusable `product_page` content
block that a future product-detail template can render.
"""

from typing import Any, Dict, List, Optional, Tuple

from .base import BaseOptimizer
from .models import OptimizerResult, Suggestion, clamp_score

# (question, policy key to pull an answer from, if any)
OBJECTION_FAQS: Tuple[Tuple[str, Optional[str]], ...] = (
    ("How long does shipping take?", "shipping_policy"),
    ("What is your return policy?", "refund_policy"),
    ("Is my payment information secure?", None),
    ("Do you ship internationally?", "shipping_policy"),
)


class ProductPageOptimizer(BaseOptimizer):
    """Populates FAQ/objection handling and a product-page content block."""

    name = "product_page"

    def optimize(self, blueprint: Dict[str, Any]) -> OptimizerResult:
        suggestions: List[Suggestion] = []
        score = 100.0

        faq_added = self._optimize_faq(blueprint, suggestions)
        score -= min(30.0, faq_added * 7.0)

        score -= self._optimize_product_page_block(blueprint, suggestions)

        return OptimizerResult(
            optimizer=self.name,
            score=clamp_score(score),
            suggestions=suggestions,
            details={
                "faq_count": len(blueprint.get("faq") or []),
                "product_page": blueprint.get("product_page", {}),
            },
        )

    def _optimize_faq(self, blueprint: Dict[str, Any], suggestions: List[Suggestion]) -> int:
        policies = blueprint.get("policies") or {}
        store_name = blueprint.get("store_name", "our store")

        faq = list(blueprint.get("faq") or [])
        existing_questions = {(f.get("question") or "").strip().lower() for f in faq}

        added = 0
        for question, policy_key in OBJECTION_FAQS:
            if question.lower() in existing_questions:
                continue
            faq.append({"question": question, "answer": self._answer_for(question, policy_key, policies, store_name)})
            added += 1

        blueprint["faq"] = faq
        if added:
            suggestions.append(Suggestion(
                id="product-page-missing-faq",
                optimizer=self.name,
                severity="high" if added >= 3 else "medium",
                title="Add objection-handling FAQ entries",
                description=f"Added {added} FAQ entries covering common purchase objections.",
            ))
        return added

    def _answer_for(self, question: str, policy_key: Optional[str], policies: Dict[str, Any], store_name: str) -> str:
        policy = policies.get(policy_key) if policy_key else None
        if policy_key == "shipping_policy" and policy:
            times = policy.get("shipping_times", {})
            return f"Standard shipping takes {times.get('standard', '5-7 business days')}; express options are available."
        if policy_key == "refund_policy" and policy:
            return (
                f"We offer a {policy.get('days', 30)}-day return policy \u2014 "
                f"{policy.get('process', 'contact our support team to get started')}."
            )
        if "secure" in question.lower():
            return "Yes. All payments are processed through encrypted, PCI-compliant checkout."
        if "international" in question.lower():
            return f"{store_name} currently ships domestically, with international shipping rolling out soon."
        return "Reach out to our support team and we'll be happy to help."

    def _optimize_product_page_block(self, blueprint: Dict[str, Any], suggestions: List[Suggestion]) -> float:
        penalty = 0.0
        product_page = blueprint.setdefault("product_page", {})

        if not product_page.get("benefits"):
            product_page["benefits"] = self._default_benefits(blueprint)
            suggestions.append(Suggestion(
                id="product-page-missing-benefits",
                optimizer=self.name,
                severity="medium",
                title="Add product benefits",
                description="Generated a benefits list from the store's trust signals.",
            ))
            penalty += 10.0

        if not product_page.get("features"):
            product_page["features"] = ["Premium materials", "Rigorous quality control", "Ready to ship"]
            suggestions.append(Suggestion(
                id="product-page-missing-features",
                optimizer=self.name,
                severity="low",
                title="Add product features",
                description="Added a default feature list; replace with real specs once available.",
            ))
            penalty += 5.0

        if not product_page.get("comparison"):
            product_page["comparison"] = {
                "us": {"quality": "Premium", "shipping": "Fast & tracked", "support": "24/7", "guarantee": "30-day money-back"},
                "typical_competitor": {"quality": "Variable", "shipping": "Slow", "support": "Limited", "guarantee": "None"},
            }
            suggestions.append(Suggestion(
                id="product-page-missing-comparison",
                optimizer=self.name,
                severity="low",
                title="Add a competitive comparison",
                description="Added a simple us-vs-typical-competitor comparison table.",
            ))
            penalty += 5.0

        product_page.setdefault("cta", "Add to Cart")
        return penalty

    def _default_benefits(self, blueprint: Dict[str, Any]) -> List[str]:
        badges = [b.lower() for b in (blueprint.get("trust_badges") or [])]
        benefits: List[str] = []
        if any("shipping" in b for b in badges):
            benefits.append("Fast, reliable shipping to your door")
        if any("guarantee" in b or "money" in b for b in badges):
            benefits.append("Risk-free with our money-back guarantee")
        if any("secure" in b for b in badges):
            benefits.append("100% secure checkout")
        benefits.append("Crafted with quality you can trust")
        return benefits
