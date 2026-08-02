from agents.conversion_engine.seo_optimizer import SEOOptimizer
from .fixtures import minimal_blueprint, realistic_blueprint


def test_fills_missing_meta_title_and_description():
    blueprint = minimal_blueprint()
    SEOOptimizer().optimize(blueprint)

    assert blueprint["seo"]["title_template"]
    assert blueprint["seo"]["meta_description_template"]


def test_builds_organization_json_ld():
    blueprint = minimal_blueprint()
    SEOOptimizer().optimize(blueprint)

    json_ld = blueprint["seo"]["json_ld"]
    assert json_ld["@type"] == "Organization"
    assert json_ld["name"] == blueprint["store_name"]


def test_no_faq_schema_without_faq_content():
    blueprint = minimal_blueprint()
    result = SEOOptimizer().optimize(blueprint)

    assert "faq_schema" not in blueprint["seo"]
    assert any(s.id == "seo-missing-faq-schema" for s in result.suggestions)


def test_faq_schema_generated_when_faq_present():
    blueprint = minimal_blueprint()
    blueprint["faq"] = [{"question": "Do you ship internationally?", "answer": "Yes."}]

    SEOOptimizer().optimize(blueprint)

    faq_schema = blueprint["seo"]["faq_schema"]
    assert faq_schema["@type"] == "FAQPage"
    assert faq_schema["mainEntity"][0]["name"] == "Do you ship internationally?"


def test_open_graph_fields_populated():
    blueprint = minimal_blueprint()
    SEOOptimizer().optimize(blueprint)

    og = blueprint["seo"]["open_graph"]
    assert og["og_title"]
    assert og["og_type"] == "website"


def test_keeps_existing_keywords():
    blueprint = realistic_blueprint()
    original_keywords = list(blueprint["seo"]["keywords"])

    SEOOptimizer().optimize(blueprint)

    assert blueprint["seo"]["keywords"] == original_keywords
