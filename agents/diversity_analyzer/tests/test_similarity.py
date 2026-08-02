"""Similarity-focused tests for the Diversity Analyzer."""

from agents.diversity_analyzer.engines import DiversityAnalyzer


def _make_bp(category: str, brand: str, product: str, desc: str, cta: str, faq_q: str, faq_a: str):
    return {
        "store_name": brand,
        "store_description": desc,
        "tagline": f"{brand} — {category} excellence",
        "homepage": [{"section_type": "hero", "content": {"headline": f"Discover {brand}", "subheadline": desc, "cta": cta}}],
        "product_page": {"category": category, "product_name": product, "cta": cta, "benefits": [f"{product} is great"]},
        "faq": [{"question": faq_q, "answer": faq_a}],
        "brand_asset_pack": {
            "store": {
                "hero_banner": {"prompt": f"{brand} hero {category} {product}"},
            },
            "product": {
                "product_hero": {"prompt": f"{product} hero {category}"},
            },
            "marketing": {
                "instagram_post": {"prompt": f"{brand} instagram {category}"},
            },
        },
    }


def test_diverse_blueprints_score_above_ninety():
    blueprints = [
        _make_bp("fitness", "ProFit", "bands", "Fuel your strength with premium resistance gear.", "Start Your Transformation", "Are the bands for beginners?", "Yes, all levels."),
        _make_bp("cuisine", "Gourmet", "knives", "Sharpen your kitchen skills with professional blades.", "Taste the Difference", "Are the knives dishwasher safe?", "Hand wash only."),
        _make_bp("beauty", "Glow", "serum", "Reveal your natural radiance with clean skincare.", "Reveal Your Glow", "Is the serum vegan?", "Yes, certified cruelty-free."),
        _make_bp("tech", "Nova", "hub", "Simplify your smart home with one elegant device.", "Experience the Future", "Is it iOS compatible?", "Yes, iOS and Android."),
        _make_bp("travel", "Wander", "backpack", "Carry your world with durable travel gear.", "Start Your Next Adventure", "Is it carry-on size?", "Yes, most airlines."),
    ]
    report = DiversityAnalyzer().run(blueprints)
    assert report["overall_diversity_score"] > 60
    assert report["brand_diversity"] > 55
    assert report["cta_diversity"] > 70
    assert report["faq_diversity"] > 70


def test_similar_blueprints_score_low():
    bp1 = _make_bp("tech", "Clone", "thing", "We provide exceptional tech.", "Buy Now", "Q1?", "A1.")
    bp2 = _make_bp("tech", "Clone2", "thing", "We provide exceptional tech.", "Buy Now", "Q1?", "A1.")
    report = DiversityAnalyzer().run([bp1, bp2])
    assert report["overall_diversity_score"] < 30
