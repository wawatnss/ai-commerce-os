from agents.conversion_engine.review_optimizer import ReviewOptimizer
from .fixtures import minimal_blueprint


def test_demo_mode_simulates_rating():
    blueprint = minimal_blueprint()
    result = ReviewOptimizer().optimize(blueprint, demo_mode=True)

    reviews_module = blueprint["reviews_module"]
    assert reviews_module["is_simulated"] is True
    assert 4.0 <= reviews_module["average_rating"] <= 5.0
    assert reviews_module["review_count"] > 0
    assert any(s.id == "reviews-demo-simulated-data" for s in result.suggestions)


def test_real_store_never_fabricates_ratings():
    blueprint = minimal_blueprint()
    result = ReviewOptimizer().optimize(blueprint, demo_mode=False)

    reviews_module = blueprint["reviews_module"]
    assert reviews_module["is_simulated"] is False
    assert reviews_module["average_rating"] is None
    assert reviews_module["review_count"] == 0
    assert any(s.id == "reviews-missing-real-reviews" for s in result.suggestions)
    assert result.score < 100


def test_real_store_with_existing_reviews_is_not_penalized():
    blueprint = minimal_blueprint()
    blueprint["reviews"] = [{"author": "Alex", "rating": 5, "text": "Loved it"}]

    result = ReviewOptimizer().optimize(blueprint, demo_mode=False)

    assert result.score == 100
    assert not any(s.id == "reviews-missing-real-reviews" for s in result.suggestions)


def test_adds_review_trust_badge():
    blueprint = minimal_blueprint()
    ReviewOptimizer().optimize(blueprint, demo_mode=True)

    assert any("review" in b.lower() for b in blueprint["trust_badges"])


def test_running_twice_in_demo_mode_keeps_same_simulated_values():
    blueprint = minimal_blueprint()
    ReviewOptimizer().optimize(blueprint, demo_mode=True)
    first_rating = blueprint["reviews_module"]["average_rating"]

    ReviewOptimizer().optimize(blueprint, demo_mode=True)
    second_rating = blueprint["reviews_module"]["average_rating"]

    assert first_rating == second_rating
