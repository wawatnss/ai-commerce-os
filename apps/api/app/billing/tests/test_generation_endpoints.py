"""Endpoint-level tests for AI-generation enforcement (store generate, brand
generate, launch generate) across free/pro/business plans.

The underlying generation service methods (`StoreService.generate_store`,
`BrandService.generate_brand`) are monkeypatched to return a canned
successful response instantly. This suite verifies the *billing*
enforcement wiring the routers now perform, not the AI engines/providers
themselves - no AI provider, network call, or real LLM is ever invoked.
"""
from datetime import datetime

import pytest

from app.billing.plans import PLANS
from app.billing.models import UsageCounter
from app.billing.tests.conftest import set_plan
from app.store_builder.services.store_service import StoreService
from app.store_builder.schemas.store import StoreResponse
from app.brand_builder.services.brand_service import BrandService
from app.brand_builder.schemas.brand import BrandResponse


def _fake_store_response(**overrides) -> StoreResponse:
    base = dict(
        id=1, user_id=None, brand_profile_id="b1", product_id="p1", supplier_id=None,
        store_name="Fake Store", store_description="desc", tagline=None,
        blueprint_json={}, validation_score=80.0, validation_result=None, metadata=None,
        created_at=datetime.utcnow(), updated_at=datetime.utcnow(),
    )
    base.update(overrides)
    return StoreResponse(**base)


def _fake_brand_response(**overrides) -> BrandResponse:
    base = dict(
        id=1, product_id="p1", supplier_id=None, brand_name="Fake Brand", slogan=None,
        mission=None, vision=None, target_audience=None, customer_persona=None,
        tone_of_voice=None, writing_style=None, color_palette=None, typography=None,
        logo_prompt=None, packaging_prompt=None, product_photography_prompt=None,
        hero_banner_prompt=None, social_media_style=None, seo_style=None, email_style=None,
        trust_elements=None, unique_value_proposition=None, differentiators=None,
        domain_name_suggestions=None, confidence_score=80.0, validation_result=None,
        metadata=None, created_at=datetime.utcnow(), updated_at=datetime.utcnow(),
    )
    base.update(overrides)
    return BrandResponse(**base)


@pytest.fixture(autouse=True)
def stub_generation_services(monkeypatch):
    """Never touch a real AI provider/engine pipeline in this suite."""

    async def _fake_generate_store(self, request):
        return _fake_store_response()

    async def _fake_generate_brand(self, request):
        return _fake_brand_response()

    monkeypatch.setattr(StoreService, "generate_store", _fake_generate_store)
    monkeypatch.setattr(BrandService, "generate_brand", _fake_generate_brand)


STORE_GENERATE_BODY = {"brand_profile_id": "b1", "product_id": "p1"}
BRAND_GENERATE_BODY = {"product_id": "p1"}


# ---------------------------------------------------------------------------
# Store generation: max_generations + AI credits
# ---------------------------------------------------------------------------

def test_store_generate_without_ai_only_consumes_a_generation_slot(client, db_session, user):
    set_plan(db_session, user.id, "pro")

    resp = client.post("/api/v1/stores/generate", json={**STORE_GENERATE_BODY, "use_ai": False})

    assert resp.status_code == 200
    usage = db_session.query(UsageCounter).filter(UsageCounter.user_id == user.id).one()
    assert usage.generations_used == 1
    assert usage.ai_credits_used == 0


def test_store_generate_with_ai_consumes_both_a_generation_slot_and_ai_credit(client, db_session, user):
    set_plan(db_session, user.id, "pro")

    resp = client.post("/api/v1/stores/generate", json={**STORE_GENERATE_BODY, "use_ai": True})

    assert resp.status_code == 200
    usage = db_session.query(UsageCounter).filter(UsageCounter.user_id == user.id).one()
    assert usage.generations_used == 1
    assert usage.ai_credits_used == 1


def test_store_generate_free_plan_rejects_ai_use_even_with_generation_slots_left(client, db_session, user):
    set_plan(db_session, user.id, "free")

    resp = client.post("/api/v1/stores/generate", json={**STORE_GENERATE_BODY, "use_ai": True})

    assert resp.status_code == 402
    assert "AI credit" in resp.json()["detail"]
    # Nothing should have been recorded for a rejected request.
    usage = db_session.query(UsageCounter).filter(UsageCounter.user_id == user.id).first()
    assert usage is None or usage.generations_used == 0


def test_store_generate_free_plan_allows_non_ai_generation(client, db_session, user):
    set_plan(db_session, user.id, "free")

    resp = client.post("/api/v1/stores/generate", json={**STORE_GENERATE_BODY, "use_ai": False})

    assert resp.status_code == 200


def test_store_generate_enforces_max_generations_boundary(client, db_session, user):
    set_plan(db_session, user.id, "free")
    limit = PLANS["free"].max_generations  # 5

    for _ in range(limit):
        resp = client.post("/api/v1/stores/generate", json={**STORE_GENERATE_BODY, "use_ai": False})
        assert resp.status_code == 200

    resp = client.post("/api/v1/stores/generate", json={**STORE_GENERATE_BODY, "use_ai": False})
    assert resp.status_code == 402
    assert "Generation limit" in resp.json()["detail"]


def test_store_generate_business_plan_unlimited_generations(client, db_session, user):
    set_plan(db_session, user.id, "business")

    for _ in range(20):
        resp = client.post("/api/v1/stores/generate", json={**STORE_GENERATE_BODY, "use_ai": False})
        assert resp.status_code == 200


def test_store_generate_business_plan_ai_credits_still_capped(client, db_session, user):
    set_plan(db_session, user.id, "business")
    usage = db_session.query(UsageCounter).filter(UsageCounter.user_id == user.id).first()
    if not usage:
        usage = UsageCounter(user_id=user.id)
        db_session.add(usage)
    usage.ai_credits_used = PLANS["business"].ai_credits
    db_session.commit()

    resp = client.post("/api/v1/stores/generate", json={**STORE_GENERATE_BODY, "use_ai": True})

    assert resp.status_code == 402
    assert "AI credit" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# Brand generation: same rules, different endpoint
# ---------------------------------------------------------------------------

def test_brand_generate_free_plan_rejects_ai_use(client, db_session, user):
    set_plan(db_session, user.id, "free")

    resp = client.post("/api/v1/brands/generate", json={**BRAND_GENERATE_BODY, "use_ai": True})

    assert resp.status_code == 402
    assert "AI credit" in resp.json()["detail"]


def test_brand_generate_free_plan_allows_non_ai(client, db_session, user):
    set_plan(db_session, user.id, "free")

    resp = client.post("/api/v1/brands/generate", json={**BRAND_GENERATE_BODY, "use_ai": False})

    assert resp.status_code == 200
    usage = db_session.query(UsageCounter).filter(UsageCounter.user_id == user.id).one()
    assert usage.generations_used == 1


def test_brand_generate_pro_plan_ai_credit_boundary(client, db_session, user):
    set_plan(db_session, user.id, "pro")
    usage = UsageCounter(user_id=user.id, ai_credits_used=PLANS["pro"].ai_credits - 1)
    db_session.add(usage)
    db_session.commit()

    resp = client.post("/api/v1/brands/generate", json={**BRAND_GENERATE_BODY, "use_ai": True})
    assert resp.status_code == 200  # last credit consumed

    resp = client.post("/api/v1/brands/generate", json={**BRAND_GENERATE_BODY, "use_ai": True})
    assert resp.status_code == 402  # now exhausted


def test_brand_generate_and_store_generate_share_the_same_generation_counter(client, db_session, user):
    """Generations are counted per-user across the whole app, not per feature."""
    set_plan(db_session, user.id, "free")
    limit = PLANS["free"].max_generations  # 5

    for _ in range(limit - 1):
        resp = client.post("/api/v1/stores/generate", json={**STORE_GENERATE_BODY, "use_ai": False})
        assert resp.status_code == 200

    # One slot left - a brand generation (not a store generation) should
    # consume it, since both draw from the same per-user counter.
    resp = client.post("/api/v1/brands/generate", json={**BRAND_GENERATE_BODY, "use_ai": False})
    assert resp.status_code == 200

    resp = client.post("/api/v1/stores/generate", json={**STORE_GENERATE_BODY, "use_ai": False})
    assert resp.status_code == 402


# ---------------------------------------------------------------------------
# Anonymous requests: store_builder/brand_builder allow anonymous access
# (legacy admin behaviour) - billing must not apply to them, matching the
# existing can_create_store convention.
# ---------------------------------------------------------------------------

def test_store_generate_anonymous_request_bypasses_billing(client, db_session, user):
    """Overriding get_current_user_optional to return None simulates an
    unauthenticated request without needing a real missing-token flow."""
    import main
    from app.auth.dependencies import get_current_user_optional

    main.app.dependency_overrides[get_current_user_optional] = lambda: None
    try:
        resp = client.post("/api/v1/stores/generate", json={**STORE_GENERATE_BODY, "use_ai": True})
        assert resp.status_code == 200
    finally:
        main.app.dependency_overrides[get_current_user_optional] = lambda: user
