"""Tests for FAQ Engine."""

from agents.faq_engine.engines import FAQEngine


def test_faq_engine_different_categories():
    fitness = {
        "store_name": "ProFit",
        "product_page": {"category": "fitness"},
    }
    beauty = {
        "store_name": "Glow",
        "product_page": {"category": "beauty"},
    }
    f_faq = FAQEngine().run(fitness, {})
    b_faq = FAQEngine().run(beauty, {})
    questions_f = [i.question for i in f_faq.items]
    questions_b = [i.question for i in b_faq.items]
    assert questions_f != questions_b
    assert f_faq.diversity_score > 0
    assert b_faq.diversity_score > 0


def test_faq_uses_policies():
    bp = {
        "store_name": "ProFit",
        "product_page": {"category": "fitness"},
    }
    policies = {
        "refund_policy": {"days": 14},
        "shipping_policy": {"shipping_times": {"standard": "3-5 days"}},
    }
    faq = FAQEngine().run(bp, policies)
    text = " ".join(i.answer for i in faq.items)
    assert "3-5 days" in text
    assert "14 days" in text
