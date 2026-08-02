"""
Publication Readiness Engine

Computes a human-facing publication readiness score from an existing
store blueprint. It NEVER invents data: every check only looks at what is
already present in the blueprint. Missing features (real logo, real
photos, payment, domain, etc.) are reported as explicit "remaining
actions" so the user knows exactly what to do before exporting.
"""

from typing import Any, Dict, List

from ..schemas.readiness import ReadinessCheck, ReadinessReport, ReadinessStatus

CHECKS = {
    "brand": {"label": "Brand", "max_score": 10},
    "homepage": {"label": "Homepage", "max_score": 10},
    "product_page": {"label": "Product Page", "max_score": 10},
    "seo": {"label": "SEO", "max_score": 15},
    "mobile": {"label": "Mobile", "max_score": 10},
    "policies": {"label": "Policies", "max_score": 10},
    "navigation": {"label": "Navigation", "max_score": 10},
    "conversion": {"label": "Conversion", "max_score": 15},
    "accessibility": {"label": "Accessibility", "max_score": 10},
}


def _has_section(homepage: List[Dict[str, Any]], section_type: str) -> bool:
    return any(s.get("section_type") == section_type for s in homepage)


class ReadinessEngine:
    """Analyse a blueprint and return a publication readiness report."""

    def run(self, blueprint: Dict[str, Any]) -> ReadinessReport:
        checks: List[ReadinessCheck] = []
        actions: List[str] = []

        # 1. Brand
        brand_score = 0
        brand_msg = []
        name = blueprint.get("store_name", "")
        desc = blueprint.get("store_description", "")
        tagline = blueprint.get("tagline")
        theme = blueprint.get("theme", {})
        if name and len(name) >= 2:
            brand_score += 4
        else:
            brand_msg.append("Nom de la marque manquant")
        if desc:
            brand_score += 3
        else:
            brand_msg.append("Description de la marque manquante")
        if tagline:
            brand_score += 2
        else:
            brand_msg.append("Tagline manquante")
        if theme.get("primary_color") and theme.get("font_family"):
            brand_score += 1
        else:
            brand_msg.append("Thème incomplet")
        if not blueprint.get("brand_profile_id"):
            brand_msg.append("Profil de marque absent")
        if brand_score < CHECKS["brand"]["max_score"]:
            actions.append("Affiner le profil de marque (nom, description, tagline)")
        checks.append(ReadinessCheck(
            key="brand",
            label=CHECKS["brand"]["label"],
            status=_status(brand_score, CHECKS["brand"]["max_score"]),
            score=brand_score,
            max_score=CHECKS["brand"]["max_score"],
            message="; ".join(brand_msg) if brand_msg else "Brand cohérent",
        ))

        # 2. Homepage
        homepage = blueprint.get("homepage", [])
        homepage_score = 0
        section_points = {"hero": 4, "features": 2, "testimonials": 2, "trust": 2}
        present = []
        for key, points in section_points.items():
            if _has_section(homepage, key):
                homepage_score += points
                present.append(key)
        for key in section_points:
            if key not in present:
                if key == "hero":
                    actions.append("Ajouter une section Hero à la homepage")
                elif key == "features":
                    actions.append("Ajouter une section Features")
                elif key == "testimonials":
                    actions.append("Ajouter une section Témoignages")
                elif key == "trust":
                    actions.append("Ajouter une section Trust")
        checks.append(ReadinessCheck(
            key="homepage",
            label=CHECKS["homepage"]["label"],
            status=_status(homepage_score, CHECKS["homepage"]["max_score"]),
            score=homepage_score,
            max_score=CHECKS["homepage"]["max_score"],
            message=f"{len(present)}/{len(section_points)} sections clés" if homepage_score else "Homepage vide",
        ))

        # 3. Product Page
        product_page = blueprint.get("product_page", {})
        product_score = 0
        if product_page.get("benefits"):
            product_score += 4
        else:
            actions.append("Ajouter les bénéfices produit")
        if product_page.get("features"):
            product_score += 3
        else:
            actions.append("Ajouter les caractéristiques produit")
        if blueprint.get("faq"):
            product_score += 3
        else:
            actions.append("Ajouter une FAQ produit")
        checks.append(ReadinessCheck(
            key="product_page",
            label=CHECKS["product_page"]["label"],
            status=_status(product_score, CHECKS["product_page"]["max_score"]),
            score=product_score,
            max_score=CHECKS["product_page"]["max_score"],
            message="Fiche produit structurée" if product_score >= 7 else "Fiche produit incomplète",
        ))

        # 4. SEO
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
        seo_score = min(seo_score, CHECKS["seo"]["max_score"])
        if seo_score < CHECKS["seo"]["max_score"]:
            actions.append("Compléter les balises SEO / Open Graph")
        checks.append(ReadinessCheck(
            key="seo",
            label=CHECKS["seo"]["label"],
            status=_status(seo_score, CHECKS["seo"]["max_score"]),
            score=seo_score,
            max_score=CHECKS["seo"]["max_score"],
            message="SEO complet" if seo_score >= 13 else "SEO partiel",
        ))

        # 5. Mobile
        nav = blueprint.get("navigation", {})
        mobile = nav.get("mobile_menu", {})
        mobile_score = 0
        if mobile.get("hamburger"):
            mobile_score += 5
        if theme.get("spacing") and theme.get("border_radius"):
            mobile_score += 3
        if theme.get("responsive_score", 0) >= 80:
            mobile_score += 2
        else:
            mobile_score += (2 if theme.get("font_family") == "Inter" else 0)
        mobile_score = min(mobile_score, CHECKS["mobile"]["max_score"])
        if mobile_score < CHECKS["mobile"]["max_score"]:
            actions.append("Vérifier le responsive / menu mobile")
        checks.append(ReadinessCheck(
            key="mobile",
            label=CHECKS["mobile"]["label"],
            status=_status(mobile_score, CHECKS["mobile"]["max_score"]),
            score=mobile_score,
            max_score=CHECKS["mobile"]["max_score"],
            message="Menu mobile OK" if mobile.get("hamburger") else "Menu mobile absent",
        ))

        # 6. Policies
        policies = blueprint.get("policies", {})
        required_policies = ["refund_policy", "shipping_policy", "privacy_policy", "terms_of_service"]
        present_policies = [k for k in required_policies if policies.get(k)]
        policy_score = len(present_policies) * 2 + (2 if len(present_policies) == len(required_policies) else 0)
        policy_score = min(policy_score, CHECKS["policies"]["max_score"])
        if policy_score < CHECKS["policies"]["max_score"]:
            actions.append("Vérifier les mentions légales (CGV, confidentialité, livraison, retours)")
        checks.append(ReadinessCheck(
            key="policies",
            label=CHECKS["policies"]["label"],
            status=_status(policy_score, CHECKS["policies"]["max_score"]),
            score=policy_score,
            max_score=CHECKS["policies"]["max_score"],
            message=f"{len(present_policies)}/{len(required_policies)} politiques",
        ))

        # 7. Navigation
        main_menu = nav.get("main_menu", [])
        nav_score = 0
        if len(main_menu) >= 3:
            nav_score += 5
        if nav.get("footer", {}).get("columns"):
            nav_score += 3
        if main_menu:
            nav_score += 2
        nav_score = min(nav_score, CHECKS["navigation"]["max_score"])
        if nav_score < CHECKS["navigation"]["max_score"]:
            actions.append("Compléter la navigation principale et le footer")
        checks.append(ReadinessCheck(
            key="navigation",
            label=CHECKS["navigation"]["label"],
            status=_status(nav_score, CHECKS["navigation"]["max_score"]),
            score=nav_score,
            max_score=CHECKS["navigation"]["max_score"],
            message=f"{len(main_menu)} liens dans le menu" if main_menu else "Aucune navigation",
        ))

        # 8. Conversion
        conversion_report = blueprint.get("conversion_report", {})
        trust_badges = blueprint.get("trust_badges", [])
        conv_score = 0
        if conversion_report.get("conversion_score", 0) >= 80:
            conv_score += 8
        elif conversion_report:
            conv_score += 4
        if trust_badges:
            conv_score += 4
        else:
            actions.append("Ajouter des trust badges")
        if not conversion_report:
            actions.append("Relancer l’analyse de conversion")
        conv_score = min(conv_score, CHECKS["conversion"]["max_score"])
        checks.append(ReadinessCheck(
            key="conversion",
            label=CHECKS["conversion"]["label"],
            status=_status(conv_score, CHECKS["conversion"]["max_score"]),
            score=conv_score,
            max_score=CHECKS["conversion"]["max_score"],
            message=f"Score conversion {conversion_report.get('conversion_score', 0):.0f}/100" if conversion_report else "Rapport conversion absent",
        ))

        # 9. Accessibility
        a11y_score = 0
        validation = blueprint.get("validation_result", {})
        a11y = validation.get("accessibility_score", 0)
        if a11y >= 90:
            a11y_score += 6
        elif a11y > 0:
            a11y_score += 3
        if theme.get("font_family"):
            a11y_score += 2
        if theme.get("primary_color") and theme.get("background_color"):
            a11y_score += 2
        a11y_score = min(a11y_score, CHECKS["accessibility"]["max_score"])
        if a11y_score < CHECKS["accessibility"]["max_score"]:
            actions.append("Vérifier le contraste et l’accessibilité")
        checks.append(ReadinessCheck(
            key="accessibility",
            label=CHECKS["accessibility"]["label"],
            status=_status(a11y_score, CHECKS["accessibility"]["max_score"]),
            score=a11y_score,
            max_score=CHECKS["accessibility"]["max_score"],
            message=f"Score accessibilité {a11y:.0f}/100" if a11y else "Accessibilité non validée",
        ))

        # Remaining business actions (always surfaced for real launch)
        if not blueprint.get("logo_url"):
            actions.append("Ajouter un vrai logo")
        if not blueprint.get("product_images") and not blueprint.get("collections"):
            actions.append("Ajouter des photos produit")
        actions.append("Connecter un domaine")
        actions.append("Ajouter un moyen de paiement")
        actions.append("Configurer les frais de livraison")

        # Deduplicate and keep order
        seen = set()
        unique_actions = []
        for a in actions:
            if a not in seen:
                seen.add(a)
                unique_actions.append(a)

        total_score = sum(c.score for c in checks)
        max_total = sum(CHECKS[k]["max_score"] for k in CHECKS)
        overall = round((total_score / max_total) * 100)
        is_ready = overall >= 80 and all(c.status != ReadinessStatus.FAIL for c in checks)

        return ReadinessReport(
            overall_score=overall,
            checks=checks,
            remaining_actions=unique_actions,
            is_ready=is_ready,
        )


def _status(score: int, max_score: int) -> ReadinessStatus:
    if score == max_score:
        return ReadinessStatus.PASS
    if score >= max_score * 0.5:
        return ReadinessStatus.PARTIAL
    return ReadinessStatus.FAIL
