"""
Shopify Export Engine

Generates a platform-compatible JSON structure from an existing store
blueprint. It never invents data: missing values are represented as
placeholders or warnings. The output is designed to be translated into
Shopify's import format (CSV or Admin API) with minimal manual work.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List


class ShopifyExportEngine:
    """Builds a Shopify export payload from a store blueprint."""

    def run(self, blueprint: Dict[str, Any], store_id: int) -> Dict[str, Any]:
        warnings: List[str] = []
        if not blueprint:
            warnings.append("Blueprint is empty. Cannot generate a meaningful export.")
            return {
                "compatibility": "shopify-v1",
                "store_id": store_id,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "warnings": warnings,
            }

        product_page = blueprint.get("product_page", {})
        variants = product_page.get("variants", [])
        collections = blueprint.get("collections", [])
        policies = blueprint.get("policies", {})
        nav = blueprint.get("navigation", {})
        seo = blueprint.get("seo", {})
        theme = blueprint.get("theme", {})
        tax_config = blueprint.get("shopify_tax_config", {})

        # Product
        product_name = blueprint.get("store_name", "Product")
        product_type = blueprint.get("product_page", {}).get("category") or "General"
        product = {
            "handle": self._handle(product_name),
            "title": product_name,
            "body_html": blueprint.get("store_description", ""),
            "vendor": blueprint.get("store_name", "Brand"),
            "product_type": product_type,
            "tags": seo.get("keywords", [])[:10],
            "variants": [
                {
                    "title": v.get("title", "Default Title"),
                    "price": str(v.get("price", 29.99)),
                    "sku": v.get("sku", "SKU-001"),
                    "barcode": v.get("barcode", ""),
                    "grams": self._grams(v.get("weight", 0.5), v.get("weight_unit", "kg")),
                    "inventory_quantity": v.get("inventory_quantity", 100),
                    "requires_shipping": True,
                    "taxable": True,
                    "is_placeholder": v.get("is_placeholder", False),
                }
                for v in variants
            ] or [self._default_variant(product_name)],
            "images": [
                {
                    "src": m.get("src", ""),
                    "alt": m.get("alt", product_name),
                    "position": m.get("position", 1),
                    "is_placeholder": m.get("is_placeholder", True),
                }
                for m in blueprint.get("product_images", [])
            ] or [{"src": "", "alt": product_name, "position": 1, "is_placeholder": True}],
            "seo": {
                "title": product_name,
                "description": blueprint.get("store_description", "")[:320],
            },
        }
        if any(v.get("is_placeholder") for v in product["variants"]):
            warnings.append("Product variants are placeholders. Replace before launch.")
        if any(i.get("is_placeholder") for i in product["images"]):
            warnings.append("Product images are placeholders. Generate/upload real images in Sprint 4.")

        # Collections
        export_collections = [
            {
                "handle": c.get("handle", self._handle(c.get("title", "Collection"))),
                "title": c.get("title", "Collection"),
                "body_html": c.get("description", ""),
                "products": [product["handle"]],
                "is_placeholder": c.get("is_placeholder", False),
            }
            for c in collections
        ] or [{"handle": "all-products", "title": "All Products", "body_html": "", "products": [product["handle"]], "is_placeholder": True}]
        if any(c.get("is_placeholder") for c in export_collections):
            warnings.append("Collections are placeholders. Replace with real collections before launch.")

        # Pages (legal)
        pages = []
        page_mapping = {
            "refund_policy": ("Refund Policy", "refund-policy"),
            "shipping_policy": ("Shipping Policy", "shipping-policy"),
            "privacy_policy": ("Privacy Policy", "privacy-policy"),
            "terms_of_service": ("Terms of Service", "terms-of-service"),
        }
        for key, (title, handle) in page_mapping.items():
            data = policies.get(key)
            if data:
                body = self._policy_body(key, data)
                pages.append({
                    "handle": handle,
                    "title": data.get("title", title),
                    "body_html": body,
                    "seo": {
                        "title": data.get("title", title),
                        "description": body[:320],
                    },
                })
            else:
                warnings.append(f"Missing {title.lower()}. Add it before launch.")

        # Menus
        main_menu = nav.get("main_menu", [])
        footer_columns = nav.get("footer", {}).get("columns", [])
        menus = {
            "main_menu": [
                {"title": m.get("label", ""), "url": m.get("link", "#")}
                for m in main_menu
            ],
            "footer": [
                {
                    "title": col.get("title", ""),
                    "links": [{"title": l.get("label", ""), "url": l.get("link", "#")} for l in col.get("links", [])],
                }
                for col in footer_columns
            ],
        }

        # Tax settings
        taxes = []
        if tax_config:
            taxes = tax_config.get("taxes", [])
            if tax_config.get("is_placeholder"):
                warnings.append("Tax rates are set to 0% placeholder. Configure real rates before selling.")
        else:
            warnings.append("No tax configuration. Shopify will use default 0% until you configure taxes.")

        # Store settings
        store_settings = {
            "name": blueprint.get("store_name", ""),
            "description": blueprint.get("store_description", ""),
            "email": "",
            "currency": "USD",
            "money_format": "${{amount}}",
            "weight_unit": "kg",
            "timezone": "UTC",
            "taxes_included": False,
            "taxes": taxes,
        }

        return {
            "compatibility": "shopify-v1",
            "store_id": store_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "store": store_settings,
            "products": [product],
            "collections": export_collections,
            "pages": pages,
            "menus": menus,
            "global_seo": {
                "title_template": seo.get("title_template", ""),
                "meta_description_template": seo.get("meta_description_template", ""),
                "keywords": seo.get("keywords", []),
                "open_graph": seo.get("open_graph", {}),
                "json_ld": seo.get("json_ld", {}),
            },
            "policies": {k: v for k, v in policies.items() if v},
            "media": blueprint.get("product_images", []),
            "warnings": warnings,
        }

    def _handle(self, name: str) -> str:
        return "".join(c if c.isalnum() or c == " " else " " for c in name).lower().strip().replace(" ", "-")

    def _default_variant(self, product_name: str) -> Dict[str, Any]:
        return {
            "title": "Default Title",
            "price": "29.99",
            "sku": "DEFAULT-001",
            "barcode": "",
            "grams": 500,
            "inventory_quantity": 100,
            "requires_shipping": True,
            "taxable": True,
            "is_placeholder": True,
        }

    def _grams(self, weight: float, unit: str) -> int:
        unit = (unit or "kg").lower()
        if unit == "kg":
            return int(weight * 1000)
        if unit == "g":
            return int(weight)
        if unit == "lb":
            return int(weight * 453.592)
        return int(weight * 1000)

    def _policy_body(self, key: str, data: Dict[str, Any]) -> str:
        parts = [f"<h1>{data.get('title', key.replace('_', ' ').title())}</h1>"]
        for k, v in data.items():
            if k == "title" or not v:
                continue
            if isinstance(v, (list, dict)):
                v = ", ".join(str(i) for i in (v if isinstance(v, list) else v.values()))
            parts.append(f"<p><strong>{k.replace('_', ' ').title()}:</strong> {v}</p>")
        return "".join(parts)
