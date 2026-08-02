"""Diversity Analyzer."""

import re
from difflib import SequenceMatcher
from typing import Any, Dict, List


class DiversityAnalyzer:
    """Compare multiple store blueprints and return a diversity report."""

    def run(self, blueprints: List[Dict[str, Any]]) -> Dict[str, Any]:
        if len(blueprints) < 2:
            return {
                "overall_diversity_score": 0.0,
                "brand_diversity": 0.0,
                "prompt_diversity": 0.0,
                "content_diversity": 0.0,
                "cta_diversity": 0.0,
                "faq_diversity": 0.0,
                "average_similarity": 100.0,
                "best_case": 0.0,
                "worst_case": 0.0,
                "distribution": [],
                "similar_pairs": [],
            }

        brand_items = [self._extract_brand(bp) for bp in blueprints]
        prompt_items = [self._extract_visual_prompts(bp) for bp in blueprints]
        content_items = [self._extract_content(bp) for bp in blueprints]
        cta_items = [self._extract_cta(bp) for bp in blueprints]
        faq_items = [self._extract_faq(bp) for bp in blueprints]

        brand_sim, brand_pairs = self._similarity_details(brand_items)
        prompt_sim, prompt_pairs = self._similarity_details(prompt_items)
        content_sim, content_pairs = self._similarity_details(content_items)
        cta_sim, cta_pairs = self._similarity_details(cta_items)
        faq_sim, faq_pairs = self._similarity_details(faq_items)

        brand_div = 100 - brand_sim * 100
        prompt_div = 100 - prompt_sim * 100
        content_div = 100 - content_sim * 100
        cta_div = 100 - cta_sim * 100
        faq_div = 100 - faq_sim * 100

        overall = (brand_div + prompt_div + content_div + cta_div + faq_div) / 5
        avg_sim = (brand_sim + prompt_sim + content_sim + cta_sim + faq_sim) / 5

        all_scores = [overall, brand_div, prompt_div, content_div, cta_div, faq_div]

        return {
            "overall_diversity_score": round(overall, 1),
            "brand_diversity": round(brand_div, 1),
            "prompt_diversity": round(prompt_div, 1),
            "content_diversity": round(content_div, 1),
            "cta_diversity": round(cta_div, 1),
            "faq_diversity": round(faq_div, 1),
            "average_similarity": round(avg_sim * 100, 1),
            "best_case": round(max(all_scores), 1),
            "worst_case": round(min(all_scores), 1),
            "distribution": self._distribution(brand_div, prompt_div, content_div, cta_div, faq_div),
            "similar_pairs": self._find_similar_pairs(
                blueprints, brand_pairs, prompt_pairs, content_pairs, cta_pairs, faq_pairs
            ),
        }

    def _distribution(self, brand: float, prompt: float, content: float, cta: float, faq: float) -> List[Dict[str, Any]]:
        return [
            {"range": "90-100", "count": sum(1 for v in [brand, prompt, content, cta, faq] if 90 <= v <= 100)},
            {"range": "80-89", "count": sum(1 for v in [brand, prompt, content, cta, faq] if 80 <= v < 90)},
            {"range": "70-79", "count": sum(1 for v in [brand, prompt, content, cta, faq] if 70 <= v < 80)},
            {"range": "60-69", "count": sum(1 for v in [brand, prompt, content, cta, faq] if 60 <= v < 70)},
            {"range": "0-59", "count": sum(1 for v in [brand, prompt, content, cta, faq] if v < 60)},
        ]

    def _extract_brand(self, bp: Dict[str, Any]) -> str:
        parts = [
            bp.get("store_name", ""),
            bp.get("tagline", ""),
            bp.get("store_description", ""),
            bp.get("brand_asset_pack", {}).get("branding", {}).get("typography", {}).get("heading", ""),
        ]
        return " ".join(str(p) for p in parts if p).lower().strip()

    def _extract_content(self, bp: Dict[str, Any]) -> str:
        parts = []
        homepage = bp.get("homepage", [])
        if isinstance(homepage, list):
            for s in homepage:
                if isinstance(s, dict):
                    content = s.get("content", {})
                    parts.extend([
                        s.get("title", ""),
                        content.get("headline", ""),
                        content.get("subheadline", ""),
                        content.get("description", ""),
                    ])
        product = bp.get("product_page", {})
        parts.extend([
            product.get("product_name", ""),
            " ".join(str(b) for b in product.get("benefits", []) if b),
            " ".join(str(f) for f in product.get("features", []) if f),
        ])
        return " ".join(str(p) for p in parts if p).lower().strip()

    def _extract_cta(self, bp: Dict[str, Any]) -> str:
        parts = []
        homepage = bp.get("homepage", [])
        if isinstance(homepage, list):
            for s in homepage:
                if isinstance(s, dict) and s.get("section_type") == "hero":
                    content = s.get("content", {})
                    cta = content.get("cta")
                    if cta:
                        parts.append(cta)
        product = bp.get("product_page", {})
        if product.get("cta"):
            parts.append(product["cta"])
        for v in product.get("cta_variants", []):
            if isinstance(v, dict) and v.get("label"):
                parts.append(v["label"])
        return " ".join(str(p) for p in parts if p).lower().strip()

    def _extract_faq(self, bp: Dict[str, Any]) -> str:
        faq = bp.get("faq", [])
        if isinstance(faq, list):
            return " ".join(
                f"{q.get('question', '')} {q.get('answer', '')}" for q in faq if isinstance(q, dict)
            ).lower().strip()
        return str(faq).lower()

    def _extract_visual_prompts(self, bp: Dict[str, Any]) -> str:
        pack = bp.get("brand_asset_pack", {})
        prompts = []
        for group in ["store", "product", "marketing"]:
            group_data = pack.get(group, {})
            if isinstance(group_data, dict):
                prompts.extend(str(v.get("prompt", "")) for v in group_data.values() if isinstance(v, dict))
        return " ".join(prompts).lower().strip()

    def _tokens(self, text: str) -> set:
        return set(re.findall(r"[a-zA-Z]+", text.lower()))

    def _jaccard(self, a: str, b: str) -> float:
        ta, tb = self._tokens(a), self._tokens(b)
        if not ta or not tb:
            return 0.0
        return len(ta & tb) / len(ta | tb)

    def _similarity(self, a: str, b: str) -> float:
        if not a and not b:
            return 1.0
        if not a or not b:
            return 0.0
        return (self._jaccard(a, b) + SequenceMatcher(None, a, b).ratio()) / 2

    def _similarity_details(self, items: List[str]) -> tuple:
        scores = []
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                scores.append(self._similarity(items[i], items[j]))
        avg = sum(scores) / len(scores) if scores else 0.0
        return avg, scores

    def _find_similar_pairs(self, blueprints: List[Dict[str, Any]], brand: List[float],
                            prompt: List[float], content: List[float], cta: List[float],
                            faq: List[float]) -> List[Dict[str, Any]]:
        pairs = []
        idx = 0
        for i in range(len(blueprints)):
            for j in range(i + 1, len(blueprints)):
                avg_sim = (brand[idx] + prompt[idx] + content[idx] + cta[idx] + faq[idx]) / 5
                if avg_sim > 0.85:
                    pairs.append({
                        "store_a": blueprints[i].get("store_name"),
                        "store_b": blueprints[j].get("store_name"),
                        "similarity": round(avg_sim, 2),
                        "reason": "High average similarity across brand, prompts, content, CTA and FAQ",
                        "recommendation": "Change product name, brand story, and at least one visual prompt template.",
                    })
                idx += 1
        return pairs
