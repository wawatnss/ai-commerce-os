"""
SEOOptimizer

Ensures the blueprint's `seo` block carries everything needed for good
technical SEO: H1/H2, meta title/description, Open Graph tags, JSON-LD
structured data (Organization + FAQPage when FAQ content exists), and
keywords.
"""

import re
from typing import Any, Dict, List

from .base import BaseOptimizer
from .models import OptimizerResult, Suggestion, clamp_score

STOPWORDS = {
    "the", "and", "for", "with", "your", "that", "this", "from", "our",
    "are", "you", "will", "shop", "store",
}


class SEOOptimizer(BaseOptimizer):
    """Optimizes on-page and structured-data SEO fields."""

    name = "seo"

    def optimize(self, blueprint: Dict[str, Any]) -> OptimizerResult:
        suggestions: List[Suggestion] = []
        score = 100.0
        seo = blueprint.setdefault("seo", {})

        score -= self._optimize_meta(blueprint, seo, suggestions)
        self._optimize_headings(blueprint, seo)
        self._optimize_open_graph(blueprint, seo)
        seo["json_ld"] = self._build_organization_json_ld(blueprint)
        score -= self._optimize_faq_schema(blueprint, seo, suggestions)
        score -= self._optimize_keywords(blueprint, seo, suggestions)

        return OptimizerResult(
            optimizer=self.name,
            score=clamp_score(score),
            suggestions=suggestions,
            details={"h1": seo.get("h1"), "keywords": seo.get("keywords")},
        )

    def _optimize_meta(self, blueprint: Dict[str, Any], seo: Dict[str, Any], suggestions: List[Suggestion]) -> float:
        penalty = 0.0
        store_name = blueprint.get("store_name", "Store")
        description = blueprint.get("store_description", "")

        if not seo.get("title_template"):
            seo["title_template"] = f"{store_name} | Shop Now"
            suggestions.append(Suggestion(
                id="seo-missing-title",
                optimizer=self.name,
                severity="high",
                title="Add a meta title",
                description="Generated a meta title template from the store name.",
            ))
            penalty += 15.0

        if not seo.get("meta_description_template"):
            seo["meta_description_template"] = (
                description[:155] or f"Shop {store_name} for quality products, fast shipping, and a satisfaction guarantee."
            )
            suggestions.append(Suggestion(
                id="seo-missing-description",
                optimizer=self.name,
                severity="high",
                title="Add a meta description",
                description="Generated a meta description from the store description.",
            ))
            penalty += 15.0
        return penalty

    def _optimize_headings(self, blueprint: Dict[str, Any], seo: Dict[str, Any]) -> None:
        homepage = blueprint.get("homepage") or []
        hero = next((s for s in homepage if s.get("section_type") == "hero"), None)
        seo["h1"] = (hero.get("content", {}) or {}).get("headline") if hero else blueprint.get("store_name")
        seo["h2_suggestions"] = [
            s.get("title") for s in homepage
            if s.get("title") and s.get("section_type") != "hero"
        ]

    def _optimize_open_graph(self, blueprint: Dict[str, Any], seo: Dict[str, Any]) -> None:
        og = seo.setdefault("open_graph", {})
        og.setdefault("og_title", seo.get("title_template", blueprint.get("store_name", "Store")))
        og.setdefault("og_description", seo.get("meta_description_template", ""))
        og.setdefault("og_type", "website")
        og.setdefault("og_image", blueprint.get("logo") or "")
        seo["open_graph_enabled"] = True

    def _build_organization_json_ld(self, blueprint: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": blueprint.get("store_name"),
            "description": blueprint.get("store_description"),
            "slogan": blueprint.get("tagline"),
        }

    def _optimize_faq_schema(self, blueprint: Dict[str, Any], seo: Dict[str, Any], suggestions: List[Suggestion]) -> float:
        faq = blueprint.get("faq") or []
        if not faq:
            suggestions.append(Suggestion(
                id="seo-missing-faq-schema",
                optimizer=self.name,
                severity="medium",
                title="Add FAQ content for SEO",
                description="FAQ content enables FAQPage structured data. Run the product page optimizer first.",
                applied=False,
            ))
            return 10.0

        seo["faq_schema"] = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": item.get("question", ""),
                    "acceptedAnswer": {"@type": "Answer", "text": item.get("answer", "")},
                }
                for item in faq
            ],
        }
        return 0.0

    def _optimize_keywords(self, blueprint: Dict[str, Any], seo: Dict[str, Any], suggestions: List[Suggestion]) -> float:
        if seo.get("keywords"):
            return 0.0

        text = f"{blueprint.get('store_name', '')} {blueprint.get('store_description', '')}".lower()
        words = {w for w in re.findall(r"[a-z]{4,}", text) if w not in STOPWORDS}
        seo["keywords"] = sorted(words)[:10]
        suggestions.append(Suggestion(
            id="seo-missing-keywords",
            optimizer=self.name,
            severity="low",
            title="Add SEO keywords",
            description="Extracted keyword candidates from the store name/description.",
        ))
        return 5.0
