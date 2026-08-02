from agents.conversion_engine import ConversionEngine
from .fixtures import minimal_blueprint, realistic_blueprint


def test_run_returns_optimized_blueprint_and_report():
    optimized, report = ConversionEngine().run(minimal_blueprint())

    assert optimized["homepage"]
    assert optimized["conversion_report"] == report.to_dict()


def test_scores_are_within_bounds():
    _, report = ConversionEngine().run(minimal_blueprint())

    for score in (
        report.conversion_score,
        report.seo_score,
        report.ux_score,
        report.trust_score,
        report.persuasion_score,
    ):
        assert 0.0 <= score <= 100.0


def test_realistic_blueprint_scores_higher_than_minimal():
    _, minimal_report = ConversionEngine().run(minimal_blueprint())
    _, realistic_report = ConversionEngine().run(realistic_blueprint())

    assert realistic_report.conversion_score > minimal_report.conversion_score


def test_does_not_mutate_the_original_blueprint():
    original = minimal_blueprint()
    snapshot = minimal_blueprint()

    ConversionEngine().run(original)

    assert original == snapshot


def test_pricing_never_touches_price_fields_end_to_end():
    blueprint = minimal_blueprint()
    blueprint["price"] = 19.99

    optimized, _ = ConversionEngine().run(blueprint)

    assert optimized["price"] == 19.99


def test_demo_mode_flows_through_to_review_optimizer():
    optimized, report = ConversionEngine().run(minimal_blueprint(), demo_mode=True)

    assert optimized["reviews_module"]["is_simulated"] is True
    assert report.demo_mode is True


def test_non_demo_mode_never_fabricates_reviews():
    optimized, report = ConversionEngine().run(minimal_blueprint(), demo_mode=False)

    assert optimized["reviews_module"]["is_simulated"] is False
    assert optimized["reviews_module"]["average_rating"] is None
    assert report.demo_mode is False


def test_recommended_actions_sorted_by_severity():
    _, report = ConversionEngine().run(minimal_blueprint())

    severities = [s.severity for s in report.recommended_actions]
    order = {"high": 0, "medium": 1, "low": 2, "info": 3}
    assert severities == sorted(severities, key=lambda s: order.get(s, 9))


def test_report_to_dict_is_json_serializable():
    import json

    _, report = ConversionEngine().run(realistic_blueprint(), demo_mode=True)
    json.dumps(report.to_dict())  # should not raise
