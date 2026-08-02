"""
Generate the Sprint 4.5 Validation Report from existing validation artifacts.

Requires the API to be running on http://localhost:8000.
"""

import json
from collections import Counter
from datetime import datetime
from pathlib import Path

import requests
from agents.diversity_analyzer.engines import DiversityAnalyzer

API_BASE = "http://localhost:8000/api/v1"


def analyze_blueprint(bp):
    """Inspect a blueprint and return a list of human-readable issues."""
    issues = []
    if not isinstance(bp, dict):
        return issues

    homepage = bp.get("homepage", []) if isinstance(bp.get("homepage"), list) else []
    hero = next((s for s in homepage if s.get("section_type") == "hero"), {})
    hero_content = hero.get("content", {}) if isinstance(hero, dict) else {}
    if len(hero_content.get("headline", "")) > 80:
        issues.append("Hero title is too long")
    if len(hero_content.get("subheadline", "")) > 120:
        issues.append("Hero subtitle is too long")

    cta_labels = set()
    for section in homepage:
        content = section.get("content", {}) if isinstance(section, dict) else {}
        cta = content.get("cta") or content.get("button_text") or section.get("cta")
        if cta:
            cta_labels.add(cta)
    if len(cta_labels) == 1 and cta_labels:
        issues.append("CTAs are identical across sections")

    faq = bp.get("faq", [])
    questions = [q.get("question", "").lower().strip() for q in faq if isinstance(q, dict)]
    if len(questions) != len(set(questions)):
        issues.append("FAQ questions are repetitive")
    answers = [q.get("answer", "").lower().strip() for q in faq if isinstance(q, dict)]
    if len(answers) != len(set(answers)):
        issues.append("FAQ answers are repetitive")
    if faq and len(faq) < 3:
        issues.append("FAQ is too short")

    product = bp.get("product_page", {})
    if not product.get("images"):
        issues.append("No product images")
    if not product.get("variants"):
        issues.append("No product variants")
    if not product.get("benefits"):
        issues.append("Product benefits are missing")

    return issues


def main():
    root = Path(__file__).parent
    results = []
    blueprints = []
    issues_counter = Counter()

    for folder in sorted(root.iterdir()):
        if not folder.is_dir():
            continue

        conversion_path = folder / "conversion.json"
        if not conversion_path.exists():
            continue

        with open(folder / "readiness.json", encoding="utf-8") as f:
            publication = json.load(f)
        with open(folder / "shopify.json", encoding="utf-8") as f:
            shopify = json.load(f)
        with open(folder / "conversion.json", encoding="utf-8") as f:
            conversion = json.load(f)
        with open(folder / "blueprint.json", encoding="utf-8") as f:
            bp = json.load(f)

        store_id = conversion.get("store_id")
        report = conversion.get("report", {})

        for issue in analyze_blueprint(bp):
            issues_counter[issue] += 1

        blueprints.append(bp)

        results.append({
            "category": folder.name,
            "store_id": store_id,
            "publication": float(publication.get("overall_score", 0)),
            "shopify": float(shopify.get("overall_score", 0)),
            "conversion": float(report.get("conversion_score", 0)),
            "seo": float(report.get("seo_score", 0)),
            "ux": float(report.get("ux_score", 0)),
            "trust": float(report.get("trust_score", 0)),
            "brand_pack": bool(bp.get("brand_asset_pack")),
            "cta_count": len(bp.get("product_page", {}).get("cta_variants", [])),
        })

    if not results:
        print("No validation artifacts found.")
        return

    diversity = DiversityAnalyzer().run(blueprints)

    avg = {
        "Publication Ready": round(sum(r["publication"] for r in results) / len(results), 1),
        "Shopify Ready": round(sum(r["shopify"] for r in results) / len(results), 1),
        "Conversion": round(sum(r["conversion"] for r in results) / len(results), 1),
        "SEO": round(sum(r["seo"] for r in results) / len(results), 1),
        "UX": round(sum(r["ux"] for r in results) / len(results), 1),
        "Trust": round(sum(r["trust"] for r in results) / len(results), 1),
    }

    lines = [
        "# Sprint 4.5 Validation Report",
        "",
        f"Generated: {datetime.now().isoformat()}",
        f"Stores: {len(results)}",
        "",
        "## Averages",
        "",
    ]
    for label, value in avg.items():
        lines.append(f"- **{label}:** {value}")

    lines.extend(["", "## Diversity scores", ""])
    lines.append(f"- **Overall Diversity:** {diversity.get('overall_diversity_score', 0)}%")
    lines.append(f"- **Brand Diversity:** {diversity.get('brand_diversity', 0)}%")
    lines.append(f"- **Prompt Diversity:** {diversity.get('prompt_diversity', 0)}%")
    lines.append(f"- **Content Diversity:** {diversity.get('content_diversity', 0)}%")
    lines.append(f"- **CTA Diversity:** {diversity.get('cta_diversity', 0)}%")
    lines.append(f"- **FAQ Diversity:** {diversity.get('faq_diversity', 0)}%")
    lines.append(f"- **Average Similarity:** {diversity.get('average_similarity', 0)}%")
    lines.append(f"- **Best Case:** {diversity.get('best_case', 0)}%")
    lines.append(f"- **Worst Case:** {diversity.get('worst_case', 0)}%")

    lines.extend(["", "## Distribution", ""])
    for bucket in diversity.get("distribution", []):
        lines.append(f"- {bucket['range']}%: {bucket['count']} dimensions")

    lines.extend(["", "## Per-store scores", ""])
    for r in results:
        lines.append(
            f"- Store {r['store_id']} ({r['category']}): "
            f"Publication {r['publication']}, Shopify {r['shopify']}, "
            f"Conversion {r['conversion']}, SEO {r['seo']}, UX {r['ux']}, Trust {r['trust']}"
            f" — Brand pack: {r['brand_pack']}, CTA variants: {r['cta_count']}"
        )

    lines.extend(["", "## Recurrent issues", ""])
    for issue, count in issues_counter.most_common():
        lines.append(f"- {issue}: {count}/{len(results)} stores")

    if diversity.get("similar_pairs"):
        lines.extend(["", "## Similar pairs", ""])
        for pair in diversity["similar_pairs"][:20]:
            lines.append(f"- {pair['store_a']} vs {pair['store_b']} (similarity {pair['similarity']}): {pair['reason']} -> {pair['recommendation']}")

    lines.append("")

    (root / "Validation Report.md").write_text("\n".join(lines), encoding="utf-8")
    (root / "report.json").write_text(json.dumps({
        "generated_at": datetime.now().isoformat(),
        "stores": len(results),
        "averages": avg,
        "diversity": diversity,
        "per_store": results,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print("Validation Report.md and report.json generated.")


if __name__ == "__main__":
    main()
