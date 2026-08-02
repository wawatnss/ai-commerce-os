"""
Phase 7.5 - End-to-End Demo seed script.

Creates a full demo store (trend -> product -> supplier -> brand -> store ->
preview) directly against the configured database, without starting the API
server and without calling any external AI provider.

Usage:
    cd apps/api
    python seed_demo.py

This is the same pipeline used by the `POST /api/v1/demo/generate` endpoint
(app/demo/services/demo_service.py); this script is a convenient CLI
entry point for local testing, CI smoke tests, or bootstrapping a fresh
database with a ready-to-show store.
"""

import asyncio
import sys

from database import SessionLocal, create_all_tables
from app.demo.services.demo_service import DemoService


async def run() -> int:
    print("AI Commerce OS - Demo Seed")
    print("=" * 40)

    print("Ensuring database tables exist...")
    create_all_tables()

    db = SessionLocal()
    try:
        service = DemoService(db)
        result = await service.generate()

        print()
        for step in result.steps:
            status_label = step.status.value.upper()
            line = f"[{status_label:<9}] {step.label}"
            if step.duration_ms is not None:
                line += f" ({step.duration_ms} ms)"
            print(line)
            if step.detail:
                print(f"            -> {step.detail}")

        print()
        if result.success:
            print(f"Demo store ready (store_id={result.store_id}).")
            print(f"Trend ID:     {result.trend_id}")
            print(f"Product ID:   {result.product_report_id}")
            print(f"Supplier ID:  {result.supplier_id}")
            print(f"Brand ID:     {result.brand_id}")
            print()
            print("Preview it with the store-renderer app (npm run dev in apps/store-renderer):")
            print(f"  http://localhost:3002/store-preview/{result.store_id}")
            return 0
        else:
            print(f"Demo generation failed: {result.error}")
            return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(asyncio.run(run()))
