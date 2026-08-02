"""
Shopify Readiness Engine

Analyses whether a generated store blueprint is close to being directly
importable into Shopify. It NEVER invents data; it only inspects the
existing blueprint and flags what a real user still needs to configure
(payment, domain, real product photos, tax review).

After the AutoFix engine runs, placeholders are accepted for import but
still flagged as warnings so the user knows what to review later.
"""

from typing import Any, Dict, List

from ..schemas.shopify_readiness import ShopifyReadinessCheck, ShopifyReadinessReport, ShopifyReadinessStatus

SHOPIFY_CHECKS = {
    "product": {"label": "Produits complets", "max_score": 20},
    "variants": {"label": "Variantes", "max_score": 10},
    "navigation": {"label": "Navigation", "max_score": 10},
    "collections": {"label": "Collections", "max_score": 10},
    "legal_pages": {"label": "Pages légales", "max_score": 15},
    "seo": {"label": "SEO", "max_score": 15},
    "taxes": {"label": "Taxes", "max_score": 5},
    "shipping": {"label": "Politique de livraison", "max_score": 10},
    "refund": {"label": "Politique de remboursement", "max_score": 5},
}


class ShopifyReadinessEngine:
    """Compute Shopify import readiness from a store blueprint."""

    def run(self, blueprint: Dict[str, Any]) -> ShopifyReadinessReport:
        checks: List[ShopifyReadinessCheck] = []
        actions: List[str] = []

        autofixed = blueprint.get("metadata", {}).get("shopify_autofix_applied", False)

        # 1. Produits complets
        product_page = blueprint.get("product_page", {})
        product_score = 0
        if product_page.get("benefits"):
            product_score += 6
        if product_page.get("features"):
            product_score += 5
        if product_page.get("comparison") and product_page["comparison"].get("us"):
            product_score += 5
        if product_page.get("cta"):
            product_score += 4
        product_score = min(product_score, SHOPIFY_CHECKS["product"]["max_score"])
        if product_score < SHOPIFY_CHECKS["product"]["max_score"]:
            actions.append("Compléter la fiche produit (bénéfices, caractéristiques, comparatif)")
        checks.append(ShopifyReadinessCheck(
            key="product",
            label=SHOPIFY_CHECKS["product"]["label"],
            status=_status(product_score, SHOPIFY_CHECKS["product"]["max_score"]),
            score=product_score,
            max_score=SHOPIFY_CHECKS["product"]["max_score"],
            message=f"{product_score}/{SHOPIFY_CHECKS['product']['max_score']} données produit",
        ))

        # 2. Variantes
        variants = product_page.get("variants", [])
        variant_score = 0
        message = "Aucune variante trouvée"
        if variants:
            variant_score = SHOPIFY_CHECKS["variants"]["max_score"]
            if any(v.get("is_placeholder") for v in variants):
                message = "Variantes placeholders (à remplacer)"
                actions.append("Remplacer les variantes placeholders par les vraies options (taille, couleur, etc.)")
            else:
                message = "Variantes OK"
        else:
            actions.append("Ajouter les vraies variantes produit (taille, couleur, etc.)")
        checks.append(ShopifyReadinessCheck(
            key="variants",
            label=SHOPIFY_CHECKS["variants"]["label"],
            status=_status(variant_score, SHOPIFY_CHECKS["variants"]["max_score"]),
            score=variant_score,
            max_score=SHOPIFY_CHECKS["variants"]["max_score"],
            message=message,
        ))

        # 3. Navigation
        nav = blueprint.get("navigation", {})
        main_menu = nav.get("main_menu", [])
        nav_score = 0
        if len(main_menu) >= 4:
            nav_score += 6
        if len(main_menu) >= 3:
            nav_score += 3
        footer = nav.get("footer", {})
        if footer.get("columns"):
            nav_score += 1
        nav_score = min(nav_score, SHOPIFY_CHECKS["navigation"]["max_score"])
        if nav_score < SHOPIFY_CHECKS["navigation"]["max_score"]:
            actions.append("Compléter la navigation principale (au moins 4 liens) et le footer")
        checks.append(ShopifyReadinessCheck(
            key="navigation",
            label=SHOPIFY_CHECKS["navigation"]["label"],
            status=_status(nav_score, SHOPIFY_CHECKS["navigation"]["max_score"]),
            score=nav_score,
            max_score=SHOPIFY_CHECKS["navigation"]["max_score"],
            message=f"{len(main_menu)} liens dans le menu",
        ))

        # 4. Collections
        collections = blueprint.get("collections", [])
        collection_score = 0
        message = "Aucune collection"
        if collections:
            collection_score = SHOPIFY_CHECKS["collections"]["max_score"]
            if any(c.get("is_placeholder") for c in collections):
                message = "Collections placeholders (à remplacer)"
                actions.append("Remplacer la collection par défaut par vos vraies collections")
            else:
                message = f"{len(collections)} collection(s)"
        else:
            actions.append("Créer au moins une collection Shopify (manuelle ou importée)")
        checks.append(ShopifyReadinessCheck(
            key="collections",
            label=SHOPIFY_CHECKS["collections"]["label"],
            status=_status(collection_score, SHOPIFY_CHECKS["collections"]["max_score"]),
            score=collection_score,
            max_score=SHOPIFY_CHECKS["collections"]["max_score"],
            message=message,
        ))

        # 5. Pages légales
        policies = blueprint.get("policies", {})
        legal_required = ["refund_policy", "shipping_policy", "privacy_policy", "terms_of_service"]
        present = [k for k in legal_required if policies.get(k)]
        legal_score = min(len(present) * 4, SHOPIFY_CHECKS["legal_pages"]["max_score"])
        if legal_score < SHOPIFY_CHECKS["legal_pages"]["max_score"]:
            actions.append("Rédiger / vérifier les pages légales (CGV, confidentialité, livraison, retours)")
        checks.append(ShopifyReadinessCheck(
            key="legal_pages",
            label=SHOPIFY_CHECKS["legal_pages"]["label"],
            status=_status(legal_score, SHOPIFY_CHECKS["legal_pages"]["max_score"]),
            score=legal_score,
            max_score=SHOPIFY_CHECKS["legal_pages"]["max_score"],
            message=f"{len(present)}/{len(legal_required)} pages",
        ))

        # 6. SEO
        seo = blueprint.get("seo", {})
        seo_score = 0
        if seo.get("title_template"):
            seo_score += 4
        if seo.get("meta_description_template"):
            seo_score += 4
        if seo.get("keywords"):
            seo_score += 3
        if seo.get("json_ld"):
            seo_score += 2
        if seo.get("open_graph"):
            seo_score += 2
        seo_score = min(seo_score, SHOPIFY_CHECKS["seo"]["max_score"])
        if seo_score < SHOPIFY_CHECKS["seo"]["max_score"]:
            actions.append("Compléter le SEO Shopify (titre, description, mots-clés)")
        checks.append(ShopifyReadinessCheck(
            key="seo",
            label=SHOPIFY_CHECKS["seo"]["label"],
            status=_status(seo_score, SHOPIFY_CHECKS["seo"]["max_score"]),
            score=seo_score,
            max_score=SHOPIFY_CHECKS["seo"]["max_score"],
            message="SEO complet" if seo_score >= 13 else "SEO partiel",
        ))

        # 7. Taxes
        tax_config = blueprint.get("shopify_tax_config", {})
        if tax_config:
            if tax_config.get("is_placeholder"):
                tax_score = 3
                message = "Taxes placeholders (à vérifier)"
                actions.append("Vérifier et ajuster les taux de taxe avant la vente")
            else:
                tax_score = SHOPIFY_CHECKS["taxes"]["max_score"]
                message = "Taxes configurées"
        else:
            tax_score = 0
            message = "Taxes non configurées"
            actions.append("Configurer les taxes dans Shopify selon le pays de vente")
        checks.append(ShopifyReadinessCheck(
            key="taxes",
            label=SHOPIFY_CHECKS["taxes"]["label"],
            status=_status(tax_score, SHOPIFY_CHECKS["taxes"]["max_score"]),
            score=tax_score,
            max_score=SHOPIFY_CHECKS["taxes"]["max_score"],
            message=message,
        ))

        # 8. Shipping
        shipping = policies.get("shipping_policy", {})
        shipping_score = 0
        if shipping:
            shipping_score += 5
        if shipping.get("shipping_times", {}).get("standard"):
            shipping_score += 3
        if shipping.get("free_shipping_threshold"):
            shipping_score += 2
        shipping_score = min(shipping_score, SHOPIFY_CHECKS["shipping"]["max_score"])
        if shipping_score < SHOPIFY_CHECKS["shipping"]["max_score"]:
            actions.append("Configurer les vrais frais de livraison dans Shopify")
        checks.append(ShopifyReadinessCheck(
            key="shipping",
            label=SHOPIFY_CHECKS["shipping"]["label"],
            status=_status(shipping_score, SHOPIFY_CHECKS["shipping"]["max_score"]),
            score=shipping_score,
            max_score=SHOPIFY_CHECKS["shipping"]["max_score"],
            message=f"Frais: {shipping.get('free_shipping_threshold', 'N/A')}" if shipping else "Aucune politique",
        ))

        # 9. Refund
        refund = policies.get("refund_policy", {})
        refund_score = 0
        if refund:
            refund_score += 3
        if refund.get("days"):
            refund_score += 2
        refund_score = min(refund_score, SHOPIFY_CHECKS["refund"]["max_score"])
        if refund_score < SHOPIFY_CHECKS["refund"]["max_score"]:
            actions.append("Finaliser la politique de remboursement")
        checks.append(ShopifyReadinessCheck(
            key="refund",
            label=SHOPIFY_CHECKS["refund"]["label"],
            status=_status(refund_score, SHOPIFY_CHECKS["refund"]["max_score"]),
            score=refund_score,
            max_score=SHOPIFY_CHECKS["refund"]["max_score"],
            message=f"{refund.get('days', 'N/A')} jours" if refund else "Aucune politique",
        ))

        # Hard manual actions for any store before real Shopify launch
        if not blueprint.get("product_images") or any(m.get("is_placeholder") for m in blueprint.get("product_images", [])):
            actions.append("Générer / uploader les vraies photos produit (Sprint 4)")
        actions.append("Connecter un compte Shopify")
        actions.append("Ajouter un moyen de paiement")
        actions.append("Connecter un domaine")

        if autofixed:
            # If autofix has run, we also include its warnings in the report
            autofix_warnings = blueprint.get("metadata", {}).get("shopify_autofix_warnings", [])
            for w in autofix_warnings:
                if w not in actions:
                    actions.append(w)

        seen = set()
        unique_actions = []
        for a in actions:
            if a not in seen:
                seen.add(a)
                unique_actions.append(a)

        total_score = sum(c.score for c in checks)
        max_total = sum(SHOPIFY_CHECKS[k]["max_score"] for k in SHOPIFY_CHECKS)
        overall = round((total_score / max_total) * 100)
        is_ready = overall >= 85 and all(c.status != ShopifyReadinessStatus.FAIL for c in checks)

        return ShopifyReadinessReport(
            overall_score=overall,
            checks=checks,
            remaining_actions=unique_actions,
            is_ready=is_ready,
        )


def _status(score: int, max_score: int) -> ShopifyReadinessStatus:
    if score == max_score:
        return ShopifyReadinessStatus.PASS
    if score >= max_score * 0.5:
        return ShopifyReadinessStatus.PARTIAL
    return ShopifyReadinessStatus.FAIL
