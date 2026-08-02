import copy

from agents.conversion_engine.ux_optimizer import UXOptimizer
from .fixtures import minimal_blueprint, realistic_blueprint


def test_empty_homepage_scores_low():
    result = UXOptimizer().optimize(minimal_blueprint())
    assert result.score <= 60


def test_well_formed_homepage_scores_highly():
    result = UXOptimizer().optimize(realistic_blueprint())
    assert result.score >= 80


def test_never_mutates_the_blueprint():
    blueprint = realistic_blueprint()
    before = copy.deepcopy(blueprint)

    UXOptimizer().optimize(blueprint)

    assert blueprint == before


def test_flags_too_many_distinct_ctas():
    blueprint = realistic_blueprint()
    for i, section in enumerate(blueprint["homepage"]):
        section.setdefault("content", {})["cta"] = f"CTA {i}"

    result = UXOptimizer().optimize(blueprint)

    assert any(s.id == "ux-too-many-ctas" for s in result.suggestions)


def test_flags_missing_cta():
    blueprint = realistic_blueprint()
    for section in blueprint["homepage"]:
        section.get("content", {}).pop("cta", None)

    result = UXOptimizer().optimize(blueprint)

    assert any(s.id == "ux-no-cta" for s in result.suggestions)
