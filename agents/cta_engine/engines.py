"""CTA Engine."""

from typing import Any, Dict, List

from .schemas import CTASet, CTAVariant


CTA_TEMPLATES: Dict[str, List[Dict[str, Any]]] = {
    "fitness": [
        {"label": "{brand}: Start Your Transformation", "context": "hero", "tone": "motivational"},
        {"label": "Claim My {product} Gear", "context": "product", "tone": "action"},
        {"label": "Get {brand} Tips Every Week", "context": "newsletter", "tone": "community"},
        {"label": "Only 12 {product} Left at This Price", "context": "urgency", "tone": "scarcity"},
        {"label": "Trusted by 50,000 {brand} Athletes", "context": "trust", "tone": "social-proof"},
    ],
    "cuisine": [
        {"label": "{brand}: Taste the Difference", "context": "hero", "tone": "sensory"},
        {"label": "Add {product} to Your Kitchen", "context": "product", "tone": "action"},
        {"label": "Weekly Recipes from {brand}", "context": "newsletter", "tone": "community"},
        {"label": "Fresh {product} Stock Today", "context": "urgency", "tone": "scarcity"},
        {"label": "Loved by {brand} Home Chefs", "context": "trust", "tone": "social-proof"},
    ],
    "beauty": [
        {"label": "{brand}: Reveal Your Glow", "context": "hero", "tone": "emotional"},
        {"label": "Pamper Yourself with {product}", "context": "product", "tone": "indulgence"},
        {"label": "{brand} Glow Tips Weekly", "context": "newsletter", "tone": "community"},
        {"label": "Limited {product} Restock", "context": "urgency", "tone": "scarcity"},
        {"label": "{product} Rated 4.9 by Beauty Experts", "context": "trust", "tone": "social-proof"},
    ],
    "tech": [
        {"label": "{brand}: Experience the Future", "context": "hero", "tone": "innovation"},
        {"label": "Upgrade {product} Today", "context": "product", "tone": "action"},
        {"label": "{brand} Tech Insights Weekly", "context": "newsletter", "tone": "community"},
        {"label": "{product} Launch Price Ends Soon", "context": "urgency", "tone": "scarcity"},
        {"label": "{product} Engineered for 10M+ Users", "context": "trust", "tone": "social-proof"},
    ],
    "outdoor": [
        {"label": "{brand}: Explore More", "context": "hero", "tone": "adventure"},
        {"label": "Gear Up with {product}", "context": "product", "tone": "action"},
        {"label": "{brand} Trail Reports Weekly", "context": "newsletter", "tone": "community"},
        {"label": "{product} Season Stock Running Low", "context": "urgency", "tone": "scarcity"},
        {"label": "{product} Tested on Real Expeditions", "context": "trust", "tone": "social-proof"},
    ],
    "home": [
        {"label": "{brand}: Make Home Yours", "context": "hero", "tone": "comfort"},
        {"label": "Add {product} Comfort", "context": "product", "tone": "action"},
        {"label": "{brand} Design Ideas Weekly", "context": "newsletter", "tone": "community"},
        {"label": "{product} Selling Fast This Month", "context": "urgency", "tone": "scarcity"},
        {"label": "{product} Styled in 100,000 Homes", "context": "trust", "tone": "social-proof"},
    ],
    "animals": [
        {"label": "{brand}: Spoil Your Pet", "context": "hero", "tone": "emotional"},
        {"label": "Treat Your Pet with {product}", "context": "product", "tone": "indulgence"},
        {"label": "{brand} Pet Tips Every Week", "context": "newsletter", "tone": "community"},
        {"label": "Last {product} Batch of the Month", "context": "urgency", "tone": "scarcity"},
        {"label": "{product} Vet-Approved & Loved", "context": "trust", "tone": "social-proof"},
    ],
    "baby": [
        {"label": "{brand}: Gentle Care for Little Ones", "context": "hero", "tone": "caring"},
        {"label": "Add {product} to Nursery", "context": "product", "tone": "action"},
        {"label": "{brand} Parenting Tips Weekly", "context": "newsletter", "tone": "community"},
        {"label": "{product} Soft Stock Limited", "context": "urgency", "tone": "scarcity"},
        {"label": "{product} Chosen by 100,000 Parents", "context": "trust", "tone": "social-proof"},
    ],
    "gaming": [
        {"label": "{brand}: Level Up", "context": "hero", "tone": "competitive"},
        {"label": "{product} Dominate the Game", "context": "product", "tone": "action"},
        {"label": "{brand} Pro Tips Weekly", "context": "newsletter", "tone": "community"},
        {"label": "{product} Drop Ends at Midnight", "context": "urgency", "tone": "scarcity"},
        {"label": "{product} Trusted by Pro Players", "context": "trust", "tone": "social-proof"},
    ],
    "travel": [
        {"label": "{brand}: Start Your Next Adventure", "context": "hero", "tone": "aspirational"},
        {"label": "Pack the {product} Essentials", "context": "product", "tone": "action"},
        {"label": "{brand} Hidden Destinations Weekly", "context": "newsletter", "tone": "community"},
        {"label": "This {product} Fare Won't Last", "context": "urgency", "tone": "scarcity"},
        {"label": "{product} Recommended by 50,000 Travelers", "context": "trust", "tone": "social-proof"},
    ],
}


def _normalize_category(category: str) -> str:
    category = category.lower().strip()
    mapping = {
        "home-goods": "home",
        "maison": "home",
        "cuisine": "cuisine",
        "food": "cuisine",
        "nourriture": "cuisine",
        "animals": "animals",
        "animaux": "animals",
        "pets": "animals",
        "bebe": "baby",
        "baby": "baby",
        "voyage": "travel",
        "gaming": "gaming",
        "games": "gaming",
        "tech": "tech",
        "electronics": "tech",
    }
    return mapping.get(category, category)


class CTAEngine:
    """Generate contextual CTA variants for a brand."""

    def run(self, blueprint: Dict[str, Any]) -> CTASet:
        category = _normalize_category(blueprint.get("product_page", {}).get("category", "tech"))
        brand = blueprint.get("store_name", "Brand")
        product = blueprint.get("product_page", {}).get("product_name") or brand
        tone = self._detect_tone(blueprint)

        templates = CTA_TEMPLATES.get(category, CTA_TEMPLATES["tech"])
        variants: List[CTAVariant] = []
        for t in templates:
            label = self._personalize(t["label"], brand, product)
            variants.append(CTAVariant(
                label=label,
                context=t["context"],
                tone=t["tone"],
                predicted_score=self._score(label, t["context"], tone),
            ))

        # Add one extra fallback variant derived from brand/product
        variants.append(CTAVariant(
            label=f"Discover {brand}",
            context="brand",
            tone="brand",
            predicted_score=70.0,
        ))

        by_context = {v.context: v for v in variants}
        return CTASet(
            hero=by_context.get("hero", variants[0]),
            product=by_context.get("product", variants[1]),
            newsletter=by_context.get("newsletter", variants[2]),
            urgency=by_context.get("urgency", variants[3]),
            trust=by_context.get("trust", variants[4]),
            all_variants=variants,
        )

    def _personalize(self, label: str, brand: str, product: str) -> str:
        return label.replace("{brand}", brand).replace("{product}", product)

    def _detect_tone(self, blueprint: Dict[str, Any]) -> str:
        desc = blueprint.get("store_description", "")
        if any(w in desc.lower() for w in ["premium", "elegant", "luxury"]):
            return "premium"
        if any(w in desc.lower() for w in ["fun", "playful", "joy"]):
            return "playful"
        if any(w in desc.lower() for w in ["adventure", "explore"]):
            return "adventurous"
        return "confident"

    def _score(self, label: str, context: str, tone: str) -> float:
        score = 70.0
        if len(label) <= 25:
            score += 10
        if " " in label:
            score += 5
        if context == "hero" and any(w in label.lower() for w in ["start", "experience", "reveal", "explore", "make", "level"]):
            score += 10
        if context == "product" and any(w in label.lower() for w in ["claim", "add", "upgrade", "treat", "dominate", "pack", "discover"]):
            score += 10
        if tone in ["motivational", "adventure", "competitive", "aspirational"]:
            score += 5
        return min(score, 98.0)
