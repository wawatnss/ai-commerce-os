from agents.conversion_engine.hero_optimizer import HeroOptimizer
from .fixtures import minimal_blueprint, realistic_blueprint, clone


def test_adds_missing_hero_section():
    blueprint = minimal_blueprint()
    result = HeroOptimizer().optimize(blueprint)

    assert blueprint["homepage"][0]["section_type"] == "hero"
    assert result.score < 100
    assert any(s.id == "hero-missing-section" for s in result.suggestions)


def test_fills_missing_headline_and_subheadline():
    blueprint = minimal_blueprint()
    HeroOptimizer().optimize(blueprint)

    hero = blueprint["homepage"][0]
    assert hero["content"]["headline"]
    assert hero["content"]["subheadline"]


def test_replaces_weak_cta():
    blueprint = minimal_blueprint()
    HeroOptimizer().optimize(blueprint)

    hero = blueprint["homepage"][0]
    assert hero["content"]["cta"]
    assert hero["content"]["cta"].lower() != "click here"


def test_enriches_cta_with_free_shipping_benefit():
    blueprint = minimal_blueprint()
    blueprint["homepage"] = [{
        "section_type": "hero",
        # No urgency word (e.g. "now", "free") so the optimizer should enrich it.
        "content": {"headline": "Hi", "subheadline": "Hi", "cta": "Purchase"},
    }]
    blueprint["policies"] = {"shipping_policy": {"free_shipping_threshold": 50}}

    HeroOptimizer().optimize(blueprint)

    assert "50" in blueprint["homepage"][0]["content"]["cta"]


def test_reorders_sections_into_high_converting_flow():
    blueprint = realistic_blueprint()
    # Scramble the order
    blueprint["homepage"] = list(reversed(blueprint["homepage"]))

    result = HeroOptimizer().optimize(blueprint)

    order = [s["section_type"] for s in blueprint["homepage"]]
    assert order == ["hero", "features", "testimonials", "trust"]
    assert any(s.id == "hero-reorder-sections" for s in result.suggestions)


def test_well_formed_hero_scores_highly():
    blueprint = realistic_blueprint()
    result = HeroOptimizer().optimize(blueprint)
    assert result.score >= 90


def test_does_not_mutate_input_reference_of_other_keys():
    blueprint = realistic_blueprint()
    original_store_name = blueprint["store_name"]
    HeroOptimizer().optimize(blueprint)
    assert blueprint["store_name"] == original_store_name
