from agents.conversion_engine.trust_optimizer import TrustOptimizer
from .fixtures import minimal_blueprint, realistic_blueprint


def test_adds_all_missing_badge_categories():
    blueprint = minimal_blueprint()
    result = TrustOptimizer().optimize(blueprint)

    badges_lower = " ".join(blueprint["trust_badges"]).lower()
    for keyword in ("payment", "shipping", "return", "guarantee", "review"):
        assert keyword in badges_lower
    assert result.score < 100


def test_does_not_duplicate_existing_badges():
    blueprint = minimal_blueprint()
    blueprint["trust_badges"] = ["Secure Payment", "Free Shipping", "Easy Returns", "Money-Back Guarantee", "Verified Customer Reviews"]
    # Also pre-populate the trust section + policies so the score reflects
    # badge de-duplication only, not these other (already-tested) checks.
    blueprint["homepage"] = [{"section_type": "trust", "content": {"badges": list(blueprint["trust_badges"])}}]
    blueprint["policies"] = {
        "refund_policy": {"days": 30},
        "shipping_policy": {"free_shipping_threshold": 50},
    }

    result = TrustOptimizer().optimize(blueprint)

    assert len(blueprint["trust_badges"]) == 5
    assert result.score == 100


def test_adds_trust_homepage_section_if_missing():
    blueprint = minimal_blueprint()
    TrustOptimizer().optimize(blueprint)

    assert any(s["section_type"] == "trust" for s in blueprint["homepage"])


def test_adds_baseline_policies_when_missing():
    blueprint = minimal_blueprint()
    TrustOptimizer().optimize(blueprint)

    assert blueprint["policies"].get("refund_policy")
    assert blueprint["policies"].get("shipping_policy")


def test_realistic_blueprint_keeps_existing_policies():
    blueprint = realistic_blueprint()
    original_refund_days = blueprint["policies"]["refund_policy"]["days"]

    TrustOptimizer().optimize(blueprint)

    assert blueprint["policies"]["refund_policy"]["days"] == original_refund_days
