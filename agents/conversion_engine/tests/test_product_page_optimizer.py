from agents.conversion_engine.product_page_optimizer import ProductPageOptimizer
from .fixtures import minimal_blueprint


def test_adds_objection_handling_faq():
    blueprint = minimal_blueprint()
    result = ProductPageOptimizer().optimize(blueprint)

    assert len(blueprint["faq"]) == 4
    questions = {f["question"] for f in blueprint["faq"]}
    assert "What is your return policy?" in questions
    assert result.score < 100


def test_does_not_duplicate_existing_faq_entries():
    blueprint = minimal_blueprint()
    blueprint["faq"] = [{"question": "How long does shipping take?", "answer": "Fast!"}]

    ProductPageOptimizer().optimize(blueprint)

    shipping_questions = [f for f in blueprint["faq"] if f["question"] == "How long does shipping take?"]
    assert len(shipping_questions) == 1
    assert shipping_questions[0]["answer"] == "Fast!"


def test_builds_product_page_content_block():
    blueprint = minimal_blueprint()
    ProductPageOptimizer().optimize(blueprint)

    product_page = blueprint["product_page"]
    assert product_page["benefits"]
    assert product_page["features"]
    assert product_page["comparison"]
    assert product_page["cta"]


def test_uses_real_policy_data_for_faq_answers():
    blueprint = minimal_blueprint()
    blueprint["policies"] = {
        "shipping_policy": {"shipping_times": {"standard": "2-3 business days"}},
    }

    ProductPageOptimizer().optimize(blueprint)

    shipping_answer = next(f["answer"] for f in blueprint["faq"] if f["question"] == "How long does shipping take?")
    assert "2-3 business days" in shipping_answer
