"""Endpoint-level tests for export enforcement (store export, Shopify
export, brand export) across free/pro/business plans. These export paths
are pure DB lookups (no AI provider/engine pipeline involved), so real rows
are created and the real endpoints are exercised end-to-end.
"""
import pytest

from app.billing.plans import PLANS
from app.billing.tests.conftest import set_plan
from app.store_builder.models.store import StoreBlueprint
from app.brand_builder.models.brand import BrandProfile


def _create_store(db_session, user_id):
    store = StoreBlueprint(
        user_id=user_id,
        brand_profile_id="brand-1",
        product_id="product-1",
        store_name="Test Store",
        store_description="A test store",
        blueprint_json={"hello": "world"},
    )
    db_session.add(store)
    db_session.commit()
    db_session.refresh(store)
    return store


def _create_brand(db_session):
    brand = BrandProfile(product_id="product-1", brand_name="Test Brand")
    db_session.add(brand)
    db_session.commit()
    db_session.refresh(brand)
    return brand


@pytest.mark.parametrize("plan_slug", ["free", "pro"])
def test_store_export_enforces_limit(client, db_session, user, plan_slug):
    set_plan(db_session, user.id, plan_slug)
    store = _create_store(db_session, user.id)
    limit = PLANS[plan_slug].max_exports

    for _ in range(limit):
        resp = client.get(f"/api/v1/stores/{store.id}/export")
        assert resp.status_code == 200

    resp = client.get(f"/api/v1/stores/{store.id}/export")
    assert resp.status_code == 402
    assert "Export limit" in resp.json()["detail"]


def test_business_plan_store_export_is_unlimited(client, db_session, user):
    set_plan(db_session, user.id, "business")
    store = _create_store(db_session, user.id)

    for _ in range(20):
        resp = client.get(f"/api/v1/stores/{store.id}/export")
        assert resp.status_code == 200


def test_store_export_and_shopify_export_share_the_same_counter(client, db_session, user):
    """Both /export and /export/shopify draw from the same max_exports budget."""
    set_plan(db_session, user.id, "free")
    store = _create_store(db_session, user.id)

    resp = client.get(f"/api/v1/stores/{store.id}/export")
    assert resp.status_code == 200

    resp = client.get(f"/api/v1/stores/{store.id}/export/shopify")
    assert resp.status_code == 402


def test_store_export_shopify_boundary(client, db_session, user):
    set_plan(db_session, user.id, "free")
    store = _create_store(db_session, user.id)

    resp = client.get(f"/api/v1/stores/{store.id}/export/shopify")
    assert resp.status_code == 200

    resp = client.get(f"/api/v1/stores/{store.id}/export")
    assert resp.status_code == 402


def test_brand_export_enforces_limit(client, db_session, user):
    set_plan(db_session, user.id, "free")
    brand = _create_brand(db_session)

    resp = client.get(f"/api/v1/brands/{brand.id}/export")
    assert resp.status_code == 200

    resp = client.get(f"/api/v1/brands/{brand.id}/export")
    assert resp.status_code == 402
    assert "Export limit" in resp.json()["detail"]


def test_brand_export_shares_counter_with_store_export(client, db_session, user):
    """Exports are counted per-user across the whole app, not per resource type."""
    set_plan(db_session, user.id, "free")
    store = _create_store(db_session, user.id)
    brand = _create_brand(db_session)

    resp = client.get(f"/api/v1/stores/{store.id}/export")
    assert resp.status_code == 200

    resp = client.get(f"/api/v1/brands/{brand.id}/export")
    assert resp.status_code == 402


def test_business_plan_brand_export_is_unlimited(client, db_session, user):
    set_plan(db_session, user.id, "business")
    brand = _create_brand(db_session)

    for _ in range(20):
        resp = client.get(f"/api/v1/brands/{brand.id}/export")
        assert resp.status_code == 200
