from agents.conversion_engine.pricing_optimizer import PricingOptimizer
from .fixtures import minimal_blueprint


def test_never_mutates_price_fields():
    blueprint = minimal_blueprint()
    blueprint["price"] = 29.99
    blueprint["compare_at_price"] = 39.99

    PricingOptimizer().optimize(blueprint)

    assert blueprint["price"] == 29.99
    assert blueprint["compare_at_price"] == 39.99


def test_returns_recommendations_marked_as_not_applied():
    result = PricingOptimizer().optimize(minimal_blueprint())

    assert len(result.suggestions) >= 4
    assert all(s.applied is False for s in result.suggestions)
    assert result.details["mutates_blueprint"] is False


def test_does_not_add_any_new_keys_to_blueprint():
    blueprint = minimal_blueprint()
    keys_before = set(blueprint.keys())

    PricingOptimizer().optimize(blueprint)

    assert set(blueprint.keys()) == keys_before
