# AI Commerce OS - Phase 7.5 Report: End-to-End Demo

**Date**: 2026-08-02
**Phase**: Phase 7.5 - End-to-End Demo
**Status**: Completed

## Executive Summary

Phase 7.5 delivers a one-click, fully self-contained demo of the whole
platform: **Trend Intelligence -> Product Intelligence -> Supplier
Intelligence -> Brand Builder -> Store Builder -> Store Preview**. Clicking
**Generate Demo Store** on `/demo` (or running `python seed_demo.py`) creates
a fictional trend, evaluates it into a product, selects a supplier, generates
a brand, builds a full store blueprint, and redirects to a live preview of
that store - all without calling OpenAI, Anthropic, or any other external
API.

Getting there required fixing several pre-existing, cross-cutting bugs in
`apps/api` that silently prevented the pipeline from ever running end-to-end
(see "Bugs Fixed" below). These were not introduced by this phase; they were
latent issues in code that had never actually been executed against a
database before.

---

## What Was Built

### 1. Demo Pipeline (`apps/api/app/demo`)

- `services/demo_service.py` - `DemoService.generate()` runs the 6 pipeline
  steps in order, recording status/duration/errors for each:
  1. **Trend detected** - `TrendService.create_trend(...)`
  2. **Product evaluated** - `ProductService.analyze_product(...)` (rule-based scoring, 11 criteria)
  3. **Supplier selected** - creates a supplier + offer, then `SupplierService.evaluate_supplier(...)` (rule-based scoring)
  4. **Brand generated** - `BrandService.generate_brand(..., use_ai=False)` (template/rule-based fallback)
  5. **Store generated** - `StoreService.generate_store(..., use_ai=False)` (fully rule-based engines)
  6. **Preview ready** - confirms the store blueprint is persisted and retrievable
- `schemas/demo.py` - `DemoStep`, `DemoStepStatus`, `DemoGenerateResponse`
- `api/router.py` - `POST /api/v1/demo/generate`

Each run picks one of a small pool of fictional products (earbuds, a plant
pot, a yoga mat) and a random 8-character suffix, so repeated clicks always
produce a fresh, independent demo store instead of colliding on unique
constraints (e.g. `trend_id`).

**No external API is ever called**: `use_ai` is explicitly set to `False`
for the brand and store generation steps, and the underlying engines already
had a rule-based/mock fallback (`if self.ai_provider: ... else: self._mock_generate(...)`)
that this phase relies on rather than reimplements. Supplier and trend data
use mock/local providers the same way.

### 2. `seed_demo.py`

A CLI entry point (`apps/api/seed_demo.py`) that runs the exact same
`DemoService` pipeline directly against the configured database, without
starting the API server. Useful for quick manual testing, CI smoke tests, or
bootstrapping a fresh database with a ready-to-show store:

```bash
cd apps/api
python seed_demo.py
```

### 3. `/demo` page (`apps/store-renderer/pages/demo.tsx`)

- A **Generate Demo Store** button
- Step-by-step progress UI (Trend detected -> Product evaluated -> Supplier
  selected -> Brand generated -> Store generated -> Preview ready), driven by
  the ordered `steps` array returned by the API
- Automatic redirect to `/store-preview/{store_id}` once the pipeline
  succeeds
- A link from the renderer's homepage (`/`) to `/demo`

---

## Bugs Fixed (required for the pipeline to run at all)

None of these were introduced for this phase - they were pre-existing
defects in code that had never been exercised end-to-end against a real
database. Fixing them was a prerequisite for "make the platform demoable".

### 1. `metadata` is a reserved SQLAlchemy attribute name

Every model with a `metadata = Column(JSON, ...)` field
(`trend_intelligence`, `product_intelligence`* , `supplier_intelligence`,
`brand_builder`, `store_builder`, and the legacy root `models.py`) raised:

```
sqlalchemy.exc.InvalidRequestError: Attribute name 'metadata' is reserved
when using the Declarative API.
```

This means **no row could ever be inserted** through any of these models -
the very first `db.add(...)` / class definition would blow up at import
time. Fixed by renaming the mapped attribute to `extra_metadata` (column
name stays `"metadata"` in the database) and re-exposing it as `.metadata`
via a plain `property` assigned right after the class body, which
SQLAlchemy's declarative scanning never sees:

```python
extra_metadata = Column("metadata", JSON, nullable=True)
...
Trend.metadata = property(lambda self: self.extra_metadata,
                           lambda self, value: setattr(self, "extra_metadata", value))
```

This keeps every repository, `to_dict()`, and Pydantic `from_attributes`
schema working unchanged.

\* `product_intelligence`'s report model doesn't have a `metadata` column,
so it wasn't affected by this specific bug.

### 2. Circular self-import in `product_intelligence/rules/__init__.py`

```python
from .__init__ import RuleRegistry, get_registry
```

This module was importing `RuleRegistry`/`get_registry` **from itself**
instead of defining them, causing an `ImportError` the moment anything
touched Product Intelligence. Fixed by implementing `RuleRegistry` (and the
module-level `registry`/`get_registry()`/`initialize_registry()`) directly
in this file, mirroring the working implementation in
`supplier_intelligence/rules/__init__.py`.

### 3. `store_builder`/`brand_builder` lost the real request data

- `BrandService.generate_brand()` compiled a brand profile dict that never
  included `product_id`, yet `BrandRepository.create_brand()` requires
  `brand_data["product_id"]` - every call raised `KeyError`.
- `StoreService.generate_store()` had the same problem for
  `brand_profile_id`/`product_id`, **and** `_compile_store_blueprint()`
  never produced a `blueprint_json` key even though
  `StoreRepository.create_store()` requires `store_data["blueprint_json"]`.
- Both services' `_get_brand_profile` / `_get_product_intelligence` /
  `_get_supplier_intelligence` helpers were hardcoded mocks ("Sample
  Product", "QualityStore") regardless of the IDs passed in, so even a
  successful call would ignore the real trend/product/supplier/brand data.

Fixed by:
- Preserving the real request identifiers before persisting
- Wrapping the flat, validated blueprint into a nested `blueprint_json` field
  (matching what `apps/store-renderer` expects) while keeping the flat
  version around only for `StoreValidator`, which reads flat keys
- Making the three `_get_*` helpers look up the real `ProductIntelligenceReport`
  / `Supplier` / `BrandProfile` rows when available, falling back to the
  original mock data otherwise (so existing manual/ad-hoc calls keep working)

### 4. `datetime` object inside a JSON column

`ProductService.analyze_product()` stored the trend's `detected_at`
(a `datetime`) directly inside a JSON column, which fails to serialize
(`TypeError: Object of type datetime is not JSON serializable`). Fixed by
calling `.isoformat()` before storing it.

### 5. Table name collision between legacy `models.py` and `trend_intelligence`

The repo has two completely different `Trend` SQLAlchemy models targeting
the same table name `"trends"`: the legacy, unused root `models.py`, and the
real one in `app/trend_intelligence/models/trend.py`. Calling `create_all`
for both against the same database means whichever runs first "wins" the
actual columns, silently breaking the other. Since `models.py` isn't wired
into any router, `create_all_tables()` (see below) intentionally excludes it.

### 6. No shared "create all tables" bootstrap

Each vertical slice declares its **own** `declarative_base()` instead of
sharing one, so `Base.metadata.create_all(...)` in `main.py` (using the root
`database.Base`) never created any of the tables actually used by the
routers. Added `database.create_all_tables()`, which creates the tables for
every vertical slice's `Base` against the shared engine, and wired it into
both `main.py`'s startup and `seed_demo.py`.

### 7. Hero section background color set to a whole color object

`HomepageEngine` set `content.background` to the entire
`{"hex": ..., "name": ..., "meaning": ...}` color object instead of just the
hex string, which would have rendered as `[object Object]` in the CSS
`backgroundColor`. Fixed to extract `.hex` when the primary color is an
object.

---

## Verification

All of the following were actually executed (not just written) as part of
this phase, using a temporary local Python virtual environment and a SQLite
database (the production/dev setup still uses Postgres via
`docker/docker-compose.yml`; SQLite was only used here to validate the logic
without requiring Docker in this environment):

```bash
cd apps/api
python seed_demo.py
```

```
[COMPLETED] Trend detected
[COMPLETED] Product evaluated
[COMPLETED] Supplier selected
[COMPLETED] Brand generated
[COMPLETED] Store generated
[COMPLETED] Preview ready

Demo store ready (store_id=1).
```

- `POST /api/v1/demo/generate` against a running `uvicorn` server returns
  `{"success": true, "store_id": 1, ...}`
- `GET /api/v1/stores/1` returns a fully-formed `blueprint_json` with a
  personalized `store_name` (derived from the generated brand), theme colors,
  4 homepage sections (hero/features/testimonials/trust), navigation, footer,
  SEO metadata, and a `validation_score` of 94.25/100
- `apps/store-renderer`'s `/demo` page builds and lints cleanly
  (`npm run build`, `npm run lint`) and renders the button + step list
- `npm run build`/`test`/`lint` still pass for every Node/TypeScript
  workspace (see the monorepo stabilization work in `INSTALL.md`)

### How to verify yourself

```bash
# 1. Start Postgres/Redis + the API
npm run docker:up
cd apps/api
pip install -r requirements.txt
uvicorn main:app --reload

# 2. Start the store renderer
cd apps/store-renderer
npm install
npm run dev

# 3. Open http://localhost:3002/demo and click "Generate Demo Store"
#    -> you should see all 6 steps complete and land on
#       http://localhost:3002/store-preview/{store_id}
```

Or, without starting the API server at all:

```bash
cd apps/api
python seed_demo.py
```

---

## Current Limitations

- The demo pipeline shares state through the same tables as "real" usage -
  it doesn't mark rows as demo data beyond `source="demo"` / `metadata.demo=true`
  fields, so a cleanup script would be needed before using this against a
  shared/production database.
- Cache classes (`TrendCache`, `ProductCache`, etc.) assume Redis is
  reachable; if Redis is down, each cache lookup can add noticeable latency
  before falling through (this pre-dates this phase and only affects
  performance, not correctness).
- The demo always drives the pipeline through `use_ai=False`; a follow-up
  "AI-enhanced demo" mode could reuse the same pipeline with `use_ai=True`
  once real API keys are configured, to show the qualitative difference.

## Next Steps

Per the roadmap, the next phase shifts focus away from infrastructure and
toward what directly impacts launchability and revenue: convincing product
pages, marketing content generation, SEO, and a real export path (Shopify or
a deployable storefront).
