"""Endpoint-level tests for billing enforcement on POST /api/v1/launch/generate.

`LaunchService.generate` (the full Trend->Product->Supplier->Brand->Store
pipeline) is monkeypatched to return a canned response instantly - this
suite tests the router's billing gate, not the pipeline itself.
"""
import pytest

from app.billing.plans import PLANS
from app.billing.models import UsageCounter
from app.billing.tests.conftest import set_plan
from app.launch.services.launch_service import LaunchService
from app.launch.schemas.launch import LaunchResponse

LAUNCH_BODY = {"name": "Test Brand", "category": "electronics"}


@pytest.fixture()
def stub_launch_success(monkeypatch):
    async def _fake_generate(self, request, user_id=None):
        return LaunchResponse(success=True, steps=[], store_id=1, store_name="Test Store")

    monkeypatch.setattr(LaunchService, "generate", _fake_generate)


@pytest.fixture()
def stub_launch_failure(monkeypatch):
    async def _fake_generate(self, request, user_id=None):
        return LaunchResponse(success=False, steps=[], error="pipeline exploded")

    monkeypatch.setattr(LaunchService, "generate", _fake_generate)


def test_launch_generate_consumes_a_generation_slot_on_success(client, db_session, user, stub_launch_success):
    set_plan(db_session, user.id, "pro")

    resp = client.post("/api/v1/launch/generate", json=LAUNCH_BODY)

    assert resp.status_code == 200
    usage = db_session.query(UsageCounter).filter(UsageCounter.user_id == user.id).one()
    assert usage.generations_used == 1
    assert usage.ai_credits_used == 0  # launch's internal pipeline uses use_ai=False today


def test_launch_generate_does_not_consume_on_pipeline_failure(client, db_session, user, stub_launch_failure):
    set_plan(db_session, user.id, "pro")

    resp = client.post("/api/v1/launch/generate", json=LAUNCH_BODY)

    assert resp.status_code == 200  # the endpoint itself succeeds; the pipeline reports failure in the body
    assert resp.json()["success"] is False
    usage = db_session.query(UsageCounter).filter(UsageCounter.user_id == user.id).first()
    assert usage is None or usage.generations_used == 0


def test_launch_generate_enforces_max_generations_boundary(client, db_session, user, stub_launch_success):
    set_plan(db_session, user.id, "free")
    limit = PLANS["free"].max_generations  # 5

    for _ in range(limit):
        resp = client.post("/api/v1/launch/generate", json=LAUNCH_BODY)
        assert resp.status_code == 200

    resp = client.post("/api/v1/launch/generate", json=LAUNCH_BODY)
    assert resp.status_code == 402
    assert "Generation limit" in resp.json()["detail"]


def test_launch_generate_business_plan_unlimited(client, db_session, user, stub_launch_success):
    set_plan(db_session, user.id, "business")

    for _ in range(10):
        resp = client.post("/api/v1/launch/generate", json=LAUNCH_BODY)
        assert resp.status_code == 200
