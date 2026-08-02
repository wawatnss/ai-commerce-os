"""
Fast validation runner for Sprint 4.5.

Generates 50 stores across varied verticals, autofixes them, and saves JSON
artifacts. No screenshots or PDFs to keep the run fast.

Run with the API already running on http://localhost:8000.

    python validation/run_validation_50.py
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path

import requests

API_BASE = "http://localhost:8000/api/v1"

BASE_NAMES = [
    "ProFit Resistance Bands",
    "Gourmet Chef Knife Set",
    "Glow Skincare Serum",
    "Nova Smart Hub",
    "TrailBlazer Camping Tent",
    "Lumina Smart Lamp",
    "PawComfort Pet Bed",
    "TinyCare Baby Monitor",
    "HyperGame Controller",
    "WanderPack Travel Backpack",
    "FitStep Yoga Mat",
    "ChefPro Blender",
    "LashLux Mascara",
    "EchoPod Earbuds",
    "Summit Hiking Boots",
    "CozyNest Throw",
    "WhiskerJoy Treats",
    "SnugWrap Carrier",
    "PixelStream Console",
    "GlobeTrek Suitcase",
    "FlexTone Weights",
    "SizzlePan Grill",
    "PureBloom Toner",
    "AeroView Drone",
    "RainGuard Jacket",
    "VelvetRoom Rug",
    "BarkBuddy Leash",
    "DreamEase Soother",
    "ThunderPad Keyboard",
    "JetSet Organizer",
    "SprintGear Shorts",
    "SpiceRack Set",
    "LumiSkin Cream",
    "SafeHome Camera",
    "PeakFuel Flask",
    "OasisBloom Planter",
    "PurrSoft Bed",
    "LittleHug Stroller",
    "RazorCore Mouse",
    "HorizonScope Binoculars",
    "CoreBalance Board",
    "FrostMate Cooler",
    "BloomLash Serum",
    "LinkHub Station",
    "TrailMix Pack",
    "CloudRest Pillow",
    "HappyPaws Bowl",
    "CuddleNest Monitor",
    "VortexHeadset",
    "AquaJug Filter",
]

CATEGORIES = [
    "fitness", "cuisine", "beauty", "tech", "outdoor",
    "home", "animaux", "bebe", "gaming", "voyage",
]


def launch_store(category: str, name: str) -> int:
    payload = {"name": name, "category": category, "objective": "sales", "budget": "growth"}
    resp = requests.post(f"{API_BASE}/launch/generate", json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    if not data.get("success") or not data.get("store_id"):
        raise RuntimeError(f"Launch failed for {category}: {data}")
    return int(data["store_id"])


def autofix_store(store_id: int) -> dict:
    resp = requests.post(f"{API_BASE}/stores/{store_id}/shopify-autofix", timeout=30)
    resp.raise_for_status()
    return resp.json()


def fetch_reports(store_id: int) -> tuple:
    publication = requests.get(f"{API_BASE}/stores/{store_id}/readiness", timeout=30).json()
    shopify = requests.get(f"{API_BASE}/stores/{store_id}/shopify-readiness", timeout=30).json()
    conversion = requests.get(f"{API_BASE}/stores/{store_id}/conversion-report", timeout=30).json()
    store = requests.get(f"{API_BASE}/stores/{store_id}", timeout=30).json()
    export = requests.get(f"{API_BASE}/stores/{store_id}/export/shopify", timeout=30).json()
    return publication, shopify, conversion, store, export


def main():
    limit = int(os.environ.get("VALIDATION_LIMIT", 50))
    if limit > len(BASE_NAMES):
        limit = len(BASE_NAMES)

    root = Path(__file__).parent
    for old in [d for d in root.iterdir() if d.is_dir()]:
        for f in old.iterdir():
            f.unlink()
        old.rmdir()

    start_time = time.perf_counter()
    for idx, name in enumerate(BASE_NAMES[:limit], start=1):
        category = CATEGORIES[(idx - 1) % len(CATEGORIES)]
        folder = root / f"{idx:02d}_{category}"
        folder.mkdir(parents=True, exist_ok=True)
        print(f"[{idx:02d}/{limit}] Launching {category}: {name}...")

        store_id = launch_store(category, name)
        print(f"  -> store_id {store_id}")

        if not os.environ.get("SKIP_AUTOFIX"):
            autofix_store(store_id)
        publication, shopify, conversion, store, export = fetch_reports(store_id)

        # store_id is not in the conversion report by default; inject it
        conversion["store_id"] = store_id

        (folder / "readiness.json").write_text(json.dumps(publication, indent=2, ensure_ascii=False), encoding="utf-8")
        (folder / "shopify.json").write_text(json.dumps(shopify, indent=2, ensure_ascii=False), encoding="utf-8")
        (folder / "conversion.json").write_text(json.dumps(conversion, indent=2, ensure_ascii=False), encoding="utf-8")
        (folder / "shopify-export.json").write_text(json.dumps(export, indent=2, ensure_ascii=False), encoding="utf-8")
        (folder / "blueprint.json").write_text(json.dumps(store.get("blueprint_json", {}), indent=2, ensure_ascii=False), encoding="utf-8")

        elapsed = time.perf_counter() - start_time
        est_remaining = (elapsed / idx) * (limit - idx)
        print(f"  -> done ({elapsed:.0f}s elapsed, ~{est_remaining:.0f}s remaining)")

    print(f"[validation] {limit} stores generated in {elapsed:.0f}s. Run generate_report.py.")


if __name__ == "__main__":
    main()
