# Stratégie de pricing — AI Commerce OS

## Objectifs

1. Maximiser les inscriptions (free plan attractif).
2. Convertir 3–5 % des utilisateurs actifs en payant.
3. Maximiser le MRR par unité via les plans Pro/Agency.
4. Rester 10× moins cher qu'une agence.

## Modèles analysés

### Modèle 1 — Free / Starter / Pro / Agency / Enterprise

| Plan | Prix | Cible | Avantages | Inconvénients |
|---|---|---|---|---|
| Free | 0 € | Testeurs | Acquisition massive | Coût support, pas de revenu |
| Starter | 19 €/mois | Solopreneurs | Entrée de gamme abordable | Faible LTV, peut cannibaliser Pro |
| Pro | 49 €/mois | Créateurs, PME | Bon rapport valeur/prix | Need marketing ciblé |
| Agency | 149 €/mois | Agences | Gros LTV, volume | Nécessite multi-seats |
| Enterprise | Sur devis | Grand compte | Contrats annuels | Cycle de vente long |

**Verdict : modèle recommandé.**

### Modèle 2 — Usage-based (crédits)

- Paiement à la boutique générée.
- Exemple : 5 € par boutique + 0.10 € par crédit IA.

**Avantages :** transparent, peur du gaspillage faible.  
**Inconvénients :** difficile à prédire, mauvais pour le MRR, friction au moment de payer.

**Verdict : complément, pas modèle principal.**

### Modèle 3 — Commission sur ventes

- Gratuit à l'usage, prélèvement de 1–3 % des ventes.

**Avantages :** aligné avec le succès client.  
**Inconvénients :** difficile à tracer, complexe juridiquement, mauvaise trésorerie.

**Verdict : trop tôt, rejeter.**

### Modèle 4 — Abonnement annuel seul

- 490 €/an pour Pro.

**Avantages :** cash up front, churn réduit.  
**Inconvénients :** friction à l'inscription, baisse des conversions.

**Verdict : proposer en option, pas par défaut.**

## Pricing recommandé

| Plan | Prix mensuel | Prix annuel (2 mois offerts) | Boutiques | Exports | Crédits IA |
|---|---|---|---|---|---|
| **Free** | 0 € | — | 3 | 1 | 0 |
| **Starter** | 19 € | 190 € | 10 | 5 | 100 |
| **Pro** | 49 € | 490 € | 25 | 25 | 500 |
| **Agency** | 149 € | 1 490 € | 100 | illimité | 2 000 |
| **Enterprise** | Sur devis | Sur devis | illimité | illimité | Sur mesure |

### Pourquoi ce modèle ?

- **Free** permet de virer le produit et d'obtenir des retours.
- **Starter** est le seuil psychologique de confort pour un solopreneur.
- **Pro** est le plan "aspirational" pour les créateurs sérieux.
- **Agency** génère la majorité du MRR avec peu de churn.
- **Enterprise** sécurise des contrats annuels à 5 chiffres.

## Tactiques de conversion

1. **Free trial de Pro 14 jours** après l'inscription.
2. **Limitation intelligente :** Free cache l'export Shopify après 1 usage, mais permet la génération rule-based.
3. **Upsell contextuel :** message "Vous avez atteint 3/3 boutiques. Passez Pro pour 49 €/mois".
4. **Annual discount 17 %** (2 mois offerts).
5. **Guarantee :** remboursé sous 7 jours si aucune boutique exportée.

## KPI pricing

- **Conversion Free → Pro :** 3 % minimum, 5 % objectif.
- **ARPU :** 55 €/mois.
- **Annual ratio :** 30 % des abonnements payants en annuel.
- **Churn :** < 8 %/mois.
