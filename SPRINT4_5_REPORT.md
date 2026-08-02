# Sprint 4.5 — Diversity Refinement

## Objectif

Dépasser **90 %** d'Overall Diversity sur un échantillon de 50 boutiques.

## Analyse initiale

Le rapport Sprint 4 identifiait deux goulots d'étranglement :

1. **Brand Description** : le `IdentityEngine` produisait `To provide exceptional {category} that enhance customers' lives` sur toutes les boutiques.
2. **Visual Prompts** : les prompts image partageaient une structure commune et un vocabulaire répétitif.

## Corrections apportées

### 1. Brand Builder — `IdentityEngine`

Fichier : `apps/api/app/brand_builder/engines/identity_engine.py`

- Remplacement du template fixe par **5 familles de templates** par catégorie.
- Variété de :
  - longueur de phrase
  - structure grammaticale
  - storytelling (bénéfice client, origine, promesse)
  - ton (confident, raffiné, ludique, aventureux, doux, futuriste)
  - vocabulaire catégorique (muscles, yoga, gym, etc. pour fitness)
- Le choix est déterministe : `md5(brand_name + product_name + audience + personality) % len(templates)`.
- La `personality` est déduite du `vibe` (luxury → refined, playful → playful, etc.).

### 2. Visual Identity Engine

Fichier : `agents/visual_identity/engines.py`

- **PROMPT_BANKS** : 3 templates par type d'image, avec structure, ordre et vocabulaire différents.
- **STYLE_BANKS**, **LIGHTING_BANKS**, **COMPOSITION_BANKS**, **BACKGROUND_BANKS**, **ANGLE_BANKS** par catégorie.
- Sélection déterministe d'un style, d'un éclairage, d'une composition, d'un arrière-plan et d'un angle pour chaque prompt.
- Les prompts incluent `{brand}`, `{product}`, `{category}`, `{tone}`, `{style}`, `{lighting}`, `{composition}`, `{background}`, `{angle}`.
- Negative prompts enrichis.

### 3. Diversity Analyzer

Fichier : `agents/diversity_analyzer/engines.py`

Nouvelles métriques séparées :

- **Brand Diversity** : `store_name` + `tagline` + `store_description` + typographie
- **Prompt Diversity** : tous les prompts du `brand_asset_pack`
- **Content Diversity** : titres, sous-titres, bénéfices, features
- **CTA Diversity** : CTA hero, produit et variantes
- **FAQ Diversity** : questions + réponses

Puis **Overall Diversity** = moyenne.

Nouvelles statistiques :

- Average Similarity
- Best Case
- Worst Case
- Distribution par tranches

### 4. Validation Suite 50

Fichier : `validation/run_validation_50.py`

- Génère 50 boutiques (5 cycles sur 10 catégories, noms produits variés).
- Sauvegarde les artefacts JSON sans screenshots/PDF pour la vitesse.

### 5. Dashboard AI Quality Report

Fichier : `apps/admin/app/quality/page.tsx`

- Métriques 5 dimensions avec barres de progression.
- Distribution visuelle (histogramme en barres).
- Best/Worst/Average Similarity.
- Paires de boutiques similaires.

### 6. Tests

- Moteurs Visual Identity, CTA, FAQ, Diversity Analyzer testés.

## Résultats Validation Suite

*Pour cette session, le run a été effectué sur 20 boutiques (le script `run_validation_50.py` supporte 50 via `VALIDATION_LIMIT=50` ; 20 boutiques ≃ 14 min, 50 ≃ 35 min).*

### Scores 20 boutiques

| Métrique | Avant (Sprint 4) | Après (Sprint 4.5) | Δ |
|---|---|---|---|
| Overall Diversity | 48.6 % | **72.0 %** | +23.4 |
| Brand Diversity | 67.0 % | **79.3 %** | +12.3 |
| Prompt Diversity | 15.7 % | **69.3 %** | +53.6 |
| Content Diversity | 8.2 % | **39.2 %** | +31.0 |
| CTA Diversity | 68.5 % | **91.4 %** | +22.9 |
| FAQ Diversity | 83.5 % | **81.0 %** | -2.5 |
| Average Similarity | — | 28.0 % | — |
| Best Case | — | 91.4 % | — |
| Worst Case | — | 39.2 % | — |

### Averages standards

- Publication Ready: 92.0
- Shopify Ready: 74.0
- Conversion: 85.9
- SEO: 100.0
- UX: 100.0
- Trust: 80.0

### Problèmes récurrents identifiés

- 20/20 : CTA identiques sur les sections (analyseur détecte un seul CTA par section)
- 20/20 : Pas d'images produit
- 20/20 : Pas de vraies variantes produit

## Pourquoi on n'atteint pas encore 90 %

1. **Content Diversity = 39.2 %**
   - Les `benefits` et `features` du `product_page` proviennent du Conversion Engine et sont encore génériques (`Premium materials`, `Rigorous quality`, `Fast shipping`, etc.).
   - Fix : ajouter des `benefits`/`features` catégoriques dans l'étape `_enrich_store` ou dans le Conversion Engine.

2. **Prompt Diversity = 69.3 %**
   - Les prompts incluent beaucoup de labels communs (`Mood:`, `Style:`, `Lighting:`, `Composition:`, `Background:`, `Shot from`).
   - Fix : ajouter 3-4 templates supplémentaires par type d'image et réduire les étiquettes répétées.

3. **Brand Diversity = 79.3 %**
   - Les `tagline` et `store_name` partagent des structures (`Pro` suffixe). Déjà bon, mais peut gagner 10 points avec plus de variation dans le Brand Builder name.

## Prochaines actions pour dépasser 90 %

1. Surcharger `product_page.benefits` et `product_page.features` avec des listes catégoriques dans `_enrich_store`.
2. Ajouter 4-5 templates de prompts par type d'image avec des formulations paragraphes, listes, ou styles artistiques très différents.
3. Relancer `VALIDATION_LIMIT=50` : le run 50 vérifiera que l'objectif 90 % est atteint.

## Conclusion

Les descriptions de marque et les prompts visuels sont désormais générés avec plusieurs familles de templates. Le Diversity Analyzer est capable d'isoler les 5 dimensions de diversité. Le dashboard Qualité IA donne une vue synthétique. Le run 50 boutiques validera si l'objectif de 90 % est atteint.
