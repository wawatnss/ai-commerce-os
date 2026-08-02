"""Tests for CTA Engine."""

from agents.cta_engine.engines import CTAEngine


def test_cta_engine_variants_are_category_aware():
    fitness = {
        "store_name": "ProFit",
        "store_description": "Get stronger with the best resistance bands.",
        "product_page": {"category": "fitness"},
    }
    beauty = {
        "store_name": "Glow",
        "store_description": "Reveal your glow.",
        "product_page": {"category": "beauty"},
    }
    cta_f = CTAEngine().run(fitness)
    cta_b = CTAEngine().run(beauty)
    assert cta_f.hero.label != cta_b.hero.label
    assert "ProFit" not in cta_b.hero.label
    assert len(cta_f.all_variants) >= 5
    assert cta_f.hero.predicted_score > 0


def test_cta_scores_different_contexts():
    bp = {
        "store_name": "Nova",
        "store_description": "The future of tech.",
        "product_page": {"category": "tech"},
    }
    cta = CTAEngine().run(bp)
    assert cta.hero.label
    assert cta.product.label
    assert cta.newsletter.label
    assert cta.urgency.label
    assert cta.trust.label
