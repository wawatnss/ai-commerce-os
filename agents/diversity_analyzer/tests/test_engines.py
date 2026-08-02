"""Tests for Diversity Analyzer."""

from agents.diversity_analyzer.engines import DiversityAnalyzer


def test_diversity_score_high_for_different_blueprints():
    bp1 = {
        "store_name": "ProFit Bands",
        "store_description": "Get stronger with resistance bands.",
        "product_page": {"category": "fitness", "cta": "Claim My Gear"},
        "homepage": [{"section_type": "hero", "content": {"cta": "Start Your Transformation"}}],
        "faq": [{"question": "How long is shipping?", "answer": "5-7 days"}],
    }
    bp2 = {
        "store_name": "Glow Serum",
        "store_description": "Reveal your natural glow with skincare.",
        "product_page": {"category": "beauty", "cta": "Pamper Yourself"},
        "homepage": [{"section_type": "hero", "content": {"cta": "Reveal Your Glow"}}],
        "faq": [{"question": "Is it vegan?", "answer": "Yes, certified cruelty-free."}],
    }
    report = DiversityAnalyzer().run([bp1, bp2])
    assert report["overall_diversity_score"] > 45
    assert report["cta_diversity"] > 50
    assert report["faq_diversity"] > 50


def test_diversity_score_low_for_clones():
    bp = {
        "store_name": "Clone",
        "store_description": "Same stuff.",
        "product_page": {"category": "tech", "cta": "Buy Now"},
        "homepage": [{"section_type": "hero", "content": {"cta": "Buy Now"}}],
        "faq": [{"question": "Q", "answer": "A"}],
    }
    report = DiversityAnalyzer().run([bp, bp])
    assert report["overall_diversity_score"] < 10
