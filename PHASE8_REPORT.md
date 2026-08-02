# AI Commerce OS - Phase 8 Report: Conversion Optimization Engine

**Date**: 2026-08-02
**Phase**: Phase 8 - Conversion Optimization Engine
**Status**: Completed

## Executive Summary

Phase 8 introduces the platform's first feature built under the new project
priority rule: **every phase must move a measurable metric** (conversion,
SEO, speed, UX, or credibility). The Conversion Optimization Engine
(`agents/conversion_engine`) turns a "correct" store blueprint - the kind
produced by Store Builder - into one optimized to sell, by running 7
independent sub-optimizers and compiling their results into a single
Conversion Report with real, actionable scores.

The engine is a standalone, framework-agnostic Python package: no database,
no AI provider, no FastAPI dependency. It takes a store blueprint dict in and
returns an optimized blueprint dict + report out, which is what makes it
trivial to unit test (44 tests, all pure Python, running in under 0.2s) and
reusable from anywhere (the API, `seed_demo.py`, a CLI, a future background
job, ...).

---

## What Was Built

### 1. `agents/conversion_engine/` - 7 sub-optimizers + a facade

| Optimizer | Mutates blueprint? | What it does |
|---|---|---|
| `HeroOptimizer` | Yes | Fixes/generates headline, subheadline, CTA; reorders homepage sections into `hero -> features -> testimonials -> trust -> faq` |
| `TrustOptimizer` | Yes | Adds missing trust badges (secure payment, shipping, returns, guarantee, social proof) and baseline shipping/refund policies |
| `ProductPageOptimizer` | Yes | Adds objection-handling FAQ entries, benefits, features, a simple competitive comparison, and the primary CTA |
| `PricingOptimizer` | **Never** | Returns psychological-pricing, anchoring, bundle, and discount **recommendations only** - it is architecturally incapable of touching a price field |
| `ReviewOptimizer` | Yes (structure only) | Builds the review/UGC structure; only ever simulates a rating in explicit `demo_mode`, and clearly flags it as simulated. For a real store it never invents a rating, review count, or review content |
| `UXOptimizer` | No (analysis-only) | Scores visual hierarchy, section density, CTA clarity/count, readability, and spacing |
| `SEOOptimizer` | Yes | Fills meta title/description, H1/H2, Open Graph tags, an `Organization` JSON-LD block, an `FAQPage` JSON-LD block (when FAQ content exists), and keywords |

`ConversionEngine.run(blueprint, demo_mode=False)`:
1. Deep-copies the input blueprint (the original is never mutated)
2. Runs all 7 optimizers in a fixed order (Hero, Trust, ProductPage, Reviews,
   SEO first since several of them depend on each other's output - e.g. SEO's
   FAQ schema depends on ProductPage's FAQ entries - then UX and Pricing,
   which are pure analysis and don't need to run in any particular order)
3. Compiles a `ConversionReport`:
   - `conversion_score` = weighted average of SEO (20%), UX (20%), Trust (25%), Persuasion (35%)
   - `persuasion_score` = average of Hero, ProductPage, and Reviews scores
   - `strengths` / `weaknesses` derived from any sub-score >= 90 / < 70
   - `recommended_actions` = every suggestion from every optimizer, sorted by severity
4. Stores the report inside the returned blueprint under `conversion_report`

### 2. Store Builder integration (`apps/api/app/store_builder/api/router.py`)

- `POST /api/v1/stores/{store_id}/optimize` - runs the engine over the
  store's current blueprint and **persists** the optimized version (via
  `StoreRepository.update_store`)
- `GET /api/v1/stores/{store_id}/conversion-report` - returns the cached
  report from the last `/optimize` call, or recomputes one on demand
  (`?recompute=true`) without persisting - useful for previewing before
  committing to a change
- Demo stores (created via Phase 7.5's `DemoService`, whose `product_id`
  always starts with `demo-`) are auto-detected so `ReviewOptimizer` knows
  it's safe to simulate a rating; this can be overridden with the
  `demo_mode` query parameter

To make `agents/conversion_engine` importable from `apps/api` (a sibling,
not-pip-installed package), a small `sys.path` bootstrap was added to
`database.py` (imported by virtually every module in the app), so
`from agents.conversion_engine import ConversionEngine` works with zero
extra setup.

### 3. Frontend: `/store-analysis/{store_id}` (`apps/store-renderer`)

- Server-rendered (`getServerSideProps`) initial load of the cached/recomputed
  report, matching the existing `/store-preview/{store_id}` pattern
- Displays all 5 scores (conversion, SEO, UX, trust, persuasion), strengths,
  weaknesses, and every recommended action (with severity, which optimizer
  produced it, and whether it was already applied or is suggestion-only)
- A **Run Optimization** button that calls `POST /optimize` client-side and
  refreshes the displayed report
- A **View Conversion Analysis** link was added to every
  `/store-preview/{store_id}` page, linking back to its analysis

---

## Design Decisions

### Why a standalone package instead of another `apps/api/app/*` module?

Phase 7.5 uncovered how much implicit coupling (shared declarative bases,
cross-service mock lookups, sys.path assumptions) had accumulated in
`apps/api/app/*`. For a module whose entire job is "take data in, return
better data + a score out", none of that database/FastAPI machinery is
needed. Keeping it in `agents/conversion_engine` as pure Python:
- Makes it trivially unit-testable (44 tests, no fixtures, no mocking, <0.2s)
- Makes the "never touch real prices" and "never fabricate reviews"
  guarantees easy to verify in isolation (see `test_pricing_optimizer.py`,
  `test_review_optimizer.py`)
- Keeps it reusable outside the API (CLI, background job, `seed_demo.py`)

### Why doesn't `ProductPageOptimizer` model a real per-product page?

The current Store Builder blueprint is store-level, not tied to a persisted
`Product` row with images/variants/price (that model exists in the legacy
`models.py` but isn't wired into any router - see PHASE7_5_REPORT.md). Rather
than inventing new database coupling, `ProductPageOptimizer` produces a
reusable `product_page` content block (benefits, features, comparison, FAQ,
CTA) at the blueprint level, ready for a future product-detail template to
render once per-product data exists.

### Why is `PricingOptimizer`'s score always 100?

It's advisory-only by design (per the phase requirements: "no real price
changes, only recommendations"). A numeric score implies something was
measured and found wanting; since this optimizer never inspects or changes
actual pricing data, giving it a score < 100 would misleadingly suggest the
*store's* pricing is bad, when really the optimizer simply always has ideas
to offer. `details.mutates_blueprint: false` documents this explicitly, and
tests assert no blueprint key is ever touched.

### Why is a real store's average rating `None` instead of `0`?

`0` is ambiguous (a genuinely bad average rating vs. "no data"). `None` (aka
`null` in the JSON output) unambiguously means "not yet collected", which
the frontend/store owner can distinguish from an actual low score.

---

## Verification

All of the following were actually executed, not just written:

```bash
pip install pytest
pytest agents/conversion_engine/tests -v
```
```
44 passed in 0.15s
```

Against a running FastAPI server (SQLite, same setup as Phase 7.5's
verification) with a demo store already generated via `seed_demo.py`:

```bash
curl -X POST http://localhost:8000/api/v1/stores/1/optimize
```
```json
{
  "store_id": 1,
  "demo_mode": true,
  "report": {
    "conversion_score": 89.4,
    "seo_score": 100.0,
    "ux_score": 100.0,
    "trust_score": 80.0,
    "persuasion_score": 84.0,
    "strengths": [
      "Hero is well optimized (score 100/100)",
      "Reviews is well optimized (score 100/100)",
      "Seo is well optimized (score 100/100)",
      "Ux is well optimized (score 100/100)",
      "Pricing is well optimized (score 100/100)"
    ],
    "weaknesses": ["Product Page needs improvement (score 52/100)"],
    "recommended_actions": [ /* 10 actions, sorted by severity */ ]
  }
}
```

```bash
curl http://localhost:8000/api/v1/stores/1/conversion-report
# -> {"cached": true, "report": {...same conversion_score: 89.4...}}
```

- `apps/store-renderer`'s `/store-analysis/[store_id]` page was fetched
  server-side against the running API and rendered all 5 scores, strengths,
  weaknesses, and all 10 recommended actions correctly
- `/store-preview/1` was re-fetched and confirmed to show the new "View
  Conversion Analysis" link, plus the trust badges/FAQ/theme the optimizer
  had just added
- `npm run build` / `npm run lint` still pass for every Node/TypeScript
  workspace (8/8 successful)

### How to verify yourself

```bash
# 1. Generate (or reuse) a demo store
cd apps/api
python seed_demo.py   # note the store_id it prints

# 2. Optimize it
curl -X POST http://localhost:8000/api/v1/stores/<store_id>/optimize

# 3. View the analysis
# (with apps/store-renderer running: npm run dev)
open http://localhost:3002/store-analysis/<store_id>
```

Or run just the engine's own test suite (no API/DB needed at all):

```bash
pip install pytest
pytest agents/conversion_engine/tests -v
```

---

## Current Limitations

- `ProductPageOptimizer` operates at the store-blueprint level rather than a
  true per-product page, since the codebase doesn't yet persist individual
  product records tied to a store (see "Design Decisions" above).
- The conversion score's weighting (SEO 20% / UX 20% / Trust 25% /
  Persuasion 35%) is a reasonable starting heuristic, not derived from real
  conversion data; it should be recalibrated once real store performance
  data exists.
- `UXOptimizer`'s "density" and "readability" checks are structural
  heuristics (section count, character counts), not real user-testing or
  Core Web Vitals data.
- Running `/optimize` repeatedly on the same store is idempotent for
  structure (won't duplicate badges/FAQ entries) but will re-roll a new
  simulated rating only if one doesn't already exist - it won't "improve" an
  already-simulated rating on subsequent runs.

## Next Steps

Per the new priority rule, upcoming work should keep moving the same five
metrics. Natural next steps building on this phase:
- Wire `PricingOptimizer`'s recommendations into an actual pricing UI where a
  human explicitly approves any price change (keeping the "never auto-change
  prices" guarantee)
- Feed real analytics (once collected) back into the conversion score weights
- Extend `ProductPageOptimizer` once real per-product data is modeled
- Add a Shopify/static-site export that carries the optimized blueprint
  (trust badges, FAQ, SEO/JSON-LD) through to the exported store
