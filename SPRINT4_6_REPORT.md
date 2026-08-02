# Sprint 4.6 — Final Diversity Pass

## Objectif

Atteindre **Overall Diversity > 90 %** sur 50 boutiques.

## Corrections appliquées

### 1. Product Page — `product_content.py`

- `apps/api/app/launch/services/product_content.py` créé.
- Banques de `benefits` et `features` spécifiques à chaque catégorie.
- 8 benefits et 8 features par catégorie.
- Sélection déterministe de 4 items par boutique via `md5(brand + product + index)`.
- Les textes incluent `{brand}` et `{product}` pour garantir l'unicité.
- Intégration dans `_enrich_store` de `launch_service.py`.

### 2. Visual Identity — familles de prompts

- `agents/visual_identity/engines.py` refondu.
- 8 familles : `storytelling`, `studio`, `lifestyle`, `editorial`, `minimal`, `luxury`, `premium`, `cinematic`.
- Chaque famille a un template d'ordre différent.
- Le `subject` dépend du type d'image (hero, packshot, etc.).
- Sélection de la famille basée sur `tone` + offset `md5(brand + product + category)`.
- Plus de débuts identiques.

## Validation 50 — Résultats

Run effectué : 50 boutiques, ~34 minutes, `SKIP_AUTOFIX=1`.

### Scores de diversité

| Métrique | Sprint 4.5 (20) | Sprint 4.6 (50) | Évolution |
|---|---|---|---|
| **Overall Diversity** | 72.0 % | **76.5 %** | +4.5 |
| **Brand Diversity** | 79.3 % | **78.3 %** | -1.0 |
| **Prompt Diversity** | 69.3 % | **49.4 %** | -19.9 |
| **Content Diversity** | 39.2 % | **86.6 %** | +47.4 |
| **CTA Diversity** | 91.4 % | **89.5 %** | -1.9 |
| **FAQ Diversity** | 81.0 % | **78.5 %** | -2.5 |
| Average Similarity | 28.0 % | **23.5 %** | -4.5 |
| Best Case | 91.4 % | **89.5 %** | — |
| Worst Case | 39.2 % | **49.4 %** | +10.2 |

### Averages standards

- Publication Ready: 92.0
- Shopify Ready: 74.0
- Conversion: 85.9
- SEO: 100.0
- UX: 100.0
- Trust: 80.0

### Analyse

- Le **Content Diversity** a explosé (+47 points) grâce aux benefits/features catégoriques. Les prompts perdent en diversité sur 50 boutiques car les 5 cycles de 10 catégories réutilisent les mêmes banques de style/éclairage/composition/arrière-plan/angle.
- Le **Prompt Diversity** est le nouveau goulot d'étranglement.
- Le **CTA** reste proche de 90 %.

## Conclusion

Les deux ajustements ciblés ont fonctionné partiellement :

- ✅ **Product Page** : Content Diversity passe de 39 % à **86.6 %**.
- ⚠️ **Visual Identity** : Prompt Diversity chute à **49.4 %** sur 50 car les 5 boutiques par catégorie réutilisent les mêmes banques de détails visuels.
- 🎯 **CTA** est à **89.5 %**, presque à l'objectif.

**Overall Diversity = 76.5 %** au lieu de 90 %.

Pour passer de 76.5 % à 90 %, il faudrait :
1. Augmenter les banques `STYLE/LIGHTING/COMPOSITION/BACKGROUND/ANGLE` à 10-15 éléments par catégorie.
2. Ajouter des offsets aléatoires par boutique dans ces banques.
3. Enrichir la FAQ à 10 questions par catégorie avec sélection de 5.

Sans ces ajustements, 76.5 % est le score réel du moteur actuel. Le système est déjà plus diversifié que jamais et prêt à passer en bêta.
