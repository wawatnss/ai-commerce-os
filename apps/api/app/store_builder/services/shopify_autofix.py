"""
Shopify AutoFix Engine

Fills the missing Shopify-import data that can be safely auto-generated
without pretending the data is real. Everything produced is labelled as a
placeholder/default and the user is warned to replace it with real
information before going live.
"""

import copy
from typing import Any, Dict, List


class ShopifyAutoFixEngine:
    """Mutate a blueprint to reach a high Shopify readiness score."""

    def run(self, blueprint: Dict[str, Any]) -> Dict[str, Any]:
        working = copy.deepcopy(blueprint)

        # 1. Default product variant
        product_page = working.setdefault("product_page", {})
        if not product_page.get("variants"):
            product_page["variants"] = [
                {
                    "title": "Default Title",
                    "price": 29.99,
                    "sku": self._sku(working.get("store_name", "product")),
                    "barcode": "",
                    "weight": 0.5,
                    "weight_unit": "kg",
                    "inventory_quantity": 100,
                    "is_placeholder": True,
                    "note": "Placeholder variant. Replace with real variants before launch.",
                }
            ]

        # 2. At least one default collection
        collections = working.setdefault("collections", [])
        if not collections:
            category = self._guess_category(working)
            collections.append({
                "handle": f"all-{category}",
                "title": f"All {category.title()} Products",
                "description": f"Explore the best {category} products from {working.get('store_name', 'our store')}.",
                "is_placeholder": True,
                "note": "Default collection. Replace or enrich before launch.",
            })

        # 3. Placeholder media for product and hero
        media = working.setdefault("product_images", [])
        if not media:
            media.append({
                "src": "",
                "alt": f"{working.get('store_name', 'Product')} - main image",
                "position": 1,
                "is_placeholder": True,
                "note": "Placeholder. Generate or upload a real product image in Sprint 4.",
            })

        # 4. Tax placeholder with 0% and a warning
        tax_config = working.setdefault("shopify_tax_config", {
            "is_placeholder": True,
            "note": "Taxes set to 0% as a placeholder. Configure real tax rates before launching.",
            "taxes": [
                {
                    "country": "US",
                    "rate": 0.0,
                    "name": "Placeholder Tax",
                    "regions": [],
                }
            ],
        })

        # 5. Ensure navigation has at least 4 links
        nav = working.setdefault("navigation", {})
        main_menu = nav.setdefault("main_menu", [])
        required = [
            {"label": "Home", "link": "/"},
            {"label": "Shop", "link": "/shop"},
            {"label": "About", "link": "/about"},
            {"label": "Contact", "link": "/contact"},
        ]
        existing_labels = {m.get("label") for m in main_menu}
        for item in required:
            if item["label"] not in existing_labels:
                main_menu.append(item)

        # 6. Ensure footer has columns
        footer = nav.setdefault("footer", {})
        if not footer.get("columns"):
            footer["columns"] = [
                {
                    "title": "About",
                    "links": [{"label": "Our Story", "link": "/about"}],
                },
                {
                    "title": "Customer Service",
                    "links": [{"label": "FAQ", "link": "/faq"}],
                },
            ]

        # 7. Mark that autofix was applied and list new warnings
        working.setdefault("metadata", {}).update({
            "shopify_autofix_applied": True,
            "shopify_autofix_warnings": [
                "Product variants are placeholder values.",
                "Collection is a default placeholder.",
                "Product images are not generated yet (Sprint 4).",
                "Taxes are set to 0% and must be reviewed.",
                "Footer menu was completed with defaults.",
            ],
        })

        return working

    def _sku(self, name: str) -> str:
        safe = "".join(c for c in name if c.isalnum()).upper()[:6] or "PROD"
        return f"{safe}-001"

    def _guess_category(self, blueprint: Dict[str, Any]) -> str:
        product_name = blueprint.get("store_name", "products")
        if blueprint.get("product_page", {}).get("category"):
            return blueprint["product_page"]["category"]
        words = [w for w in product_name.lower().split() if len(w) > 3]
        return words[-1] if words else "products"
