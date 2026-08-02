"""
Validation runner for Sprint 4.

Generates 10 stores across verticals, applies the new Visual Identity, CTA
and FAQ engines, then builds a Validation Report with diversity metrics.

Run with the API and store-renderer already running on their default ports.

    python validation/run_validation.py
"""

import json
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path

import requests
from fpdf import FPDF

API_BASE = "http://localhost:8000/api/v1"
RENDERER_BASE = "http://localhost:3002"
EDGE_EXE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

STORES = [
    ("fitness", "ProFit Resistance Bands"),
    ("cuisine", "Gourmet Chef Knife Set"),
    ("beauty", "Glow Skincare Serum"),
    ("tech", "Nova Smart Hub"),
    ("outdoor", "TrailBlazer Camping Tent"),
    ("maison", "Lumina Smart Lamp"),
    ("animaux", "PawComfort Pet Bed"),
    ("bebe", "TinyCare Baby Monitor"),
    ("gaming", "HyperGame Controller"),
    ("voyage", "WanderPack Travel Backpack"),
]


def launch_store(category: str, name: str) -> int:
    payload = {
        "name": name,
        "category": category,
        "objective": "sales",
        "budget": "growth",
    }
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


def screenshot(url: str, output: Path):
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            EDGE_EXE,
            "--headless=new",
            f"--screenshot={output}",
            "--window-size=1440,900",
            "--no-sandbox",
            "--disable-gpu",
            url,
        ],
        check=True,
        capture_output=True,
    )


def _multi_line(pdf, h, text):
    pdf.set_x(10)
    pdf.multi_cell(pdf.w - 20, h, text)


def make_pdf(path: Path, category: str, name: str, store_id: int,
             publication: dict, shopify: dict, conversion: dict, export: dict):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, name, ln=True)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, f"Category: {category}    Store ID: {store_id}", ln=True)
    pdf.ln(5)

    report = conversion.get("report", {})
    scores = [
        ("Publication Ready", publication.get("overall_score", 0)),
        ("Shopify Ready", shopify.get("overall_score", 0)),
        ("Conversion", report.get("conversion_score", 0)),
        ("SEO", report.get("seo_score", 0)),
        ("UX", report.get("ux_score", 0)),
        ("Trust", report.get("trust_score", 0)),
    ]
    for label, score in scores:
        pdf.cell(0, 8, f"{label}: {score}", ln=True)
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Remaining actions", ln=True)
    pdf.set_font("Helvetica", "", 10)
    for action in shopify.get("remaining_actions", [])[:12]:
        _multi_line(pdf, 6, f"- {action}")

    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Export compatibility", ln=True)
    pdf.set_font("Helvetica", "", 10)
    _multi_line(pdf, 6, f"Products: {len(export.get('products', []))}")
    _multi_line(pdf, 6, f"Collections: {len(export.get('collections', []))}")
    _multi_line(pdf, 6, f"Pages: {len(export.get('pages', []))}")
    _multi_line(pdf, 6, f"Warnings: {len(export.get('warnings', []))}")

    pdf.output(str(path))


def main():
    root = Path(__file__).parent
    results = []

    for category, name in STORES:
        folder = root / category
        folder.mkdir(parents=True, exist_ok=True)
        print(f"[validation] Launching {category}...")

        store_id = launch_store(category, name)
        print(f"  -> store_id {store_id}")

        print(f"  -> autofix...")
        autofix_store(store_id)

        print(f"  -> fetching reports...")
        publication, shopify, conversion, store, export = fetch_reports(store_id)

        (folder / "readiness.json").write_text(json.dumps(publication, indent=2, ensure_ascii=False), encoding="utf-8")
        (folder / "shopify.json").write_text(json.dumps(shopify, indent=2, ensure_ascii=False), encoding="utf-8")
        (folder / "conversion.json").write_text(json.dumps(conversion, indent=2, ensure_ascii=False), encoding="utf-8")
        (folder / "shopify-export.json").write_text(json.dumps(export, indent=2, ensure_ascii=False), encoding="utf-8")
        (folder / "blueprint.json").write_text(json.dumps(store.get("blueprint_json", {}), indent=2, ensure_ascii=False), encoding="utf-8")

        time.sleep(2)
        print(f"  -> screenshots...")
        screenshot(f"{RENDERER_BASE}/store-preview/{store_id}", folder / "homepage.png")
        screenshot(f"{RENDERER_BASE}/store-preview/{store_id}/product", folder / "product.png")

        print(f"  -> PDF...")
        make_pdf(folder / "store.pdf", category, name, store_id,
                 publication, shopify, conversion, export)

        results.append({
            "category": category,
            "name": name,
            "store_id": store_id,
        })

    print("[validation] Done. Run generate_report.py to build the report.")


if __name__ == "__main__":
    main()
