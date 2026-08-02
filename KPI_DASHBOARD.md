# KPI Dashboard — AI Commerce OS

## Objectif

Suivre la santé commerciale et technique du produit pour prendre des décisions basées sur les données.

## Funnel utilisateur

| Étape | Métrique | Définition | Objectif mensuel |
|---|---|---|---|
| Visites | **visiteurs uniques** | Visites landing page | +30 %/mois |
| Inscription | **signups** | Comptes créés | 10 % des visiteurs |
| Activation | **activation rate** % ayant généré une boutique | 40 % des signups |
| Retention | **D7 retention** % revenus 7 jours après signup | 20 % |
| Conversion | **free-to-paid** % passant Pro/Agency | 3–5 % |
| Revenu | **MRR** | Revenu mensuel récurrent | +20 %/mois |
| Santé | **churn** % ayant annulé | < 8 %/mois |

## KPI produit

| Métrique | Définition | Formule | Objectif |
|---|---|---|---|
| **Boutiques générées** | Nombre total | `COUNT(stores)` | +25 %/mois |
| **Exports Shopify** | Exports réalisés | `COUNT(shopify_exports)` | 20 % des boutiques générées |
| **Score readiness moyen** | Qualité | `AVG(readiness_score)` | > 85 |
| **Shopify readiness moyen** | Prêt Shopify | `AVG(shopify_readiness_score)` | > 80 |
| **Temps moyen de génération** | Durée | `AVG(launch_duration_ms)` | < 20s |
| **Taux d'erreur** | Erreurs API | `5xx / total` | < 1 % |

## KPI financiers

| Métrique | Définition | Formule | Objectif |
|---|---|---|---|
| **MRR** | Revenu mensuel récurrent | `SUM(plan_prices)` | +20 %/mois |
| **ARPU** | Revenu moyen par utilisateur | `MRR / paying_users` | 55 € |
| **LTV** | Valeur client | `ARPU * gross_margin / churn` | > 300 € |
| **CAC** | Coût acquisition | `marketing_spend / new_paying_customers` | < 30 € |
| **CAC payback** | Temps de récupération | `CAC / (ARPU * gross_margin)` | < 6 mois |
| **Marge brute** | % conservé | `(MRR - cogs) / MRR` | > 70 % |

## KPI coûts IA

| Métrique | Définition | Formule | Objectif |
|---|---|---|---|
| **Coût IA par génération** | Coût OpenAI | `openai_spend / generations` | < 0.50 € |
| **Coût IA par utilisateur** | Coût moyen | `openai_spend / active_users` | < 5 €/mois |
| **Coût IA par revenu** | Efficacité | `openai_spend / MRR` | < 15 % |
| **Crédits IA utilisés** | Consommation | `SUM(ai_credits_used)` | < 80 % des crédits alloués |

## KPI support et qualité

| Métrique | Définition | Objectif |
|---|---|---|
| **NPS** | Satisfaction | > 40 |
| **Tickets support** | Nombre | < 5 % des utilisateurs actifs |
| **Temps de réponse support** | Moyenne | < 24h (Pro), < 4h (Agency) |
| **Bugs critiques** | Ouverts | 0 |

## Dashboard technique

| Métrique | Source | Objectif |
|---|---|---|
| **Uptime API** | UptimeRobot | > 99.9 % |
| **Temps réponse moyen** | APM | < 300 ms |
| **Erreurs 5xx** | Logs | < 0.1 % |
| **Taux de conversion landing** | Analytics | > 10 % |

## Outils recommandés

- **Analytics produit :** PostHog ou Mixpanel
- **Analytics web :** Plausible ou Google Analytics 4
- **Monitoring :** Sentry + UptimeRobot
- **Revenus :** Stripe Dashboard
- **Email :** Mailchimp / Brevo
- **Support :** Crisp / Intercom (free)

## Tableau de bord hebdomadaire

| Indicateur | Cible | Semaine -1 | Semaine -2 | Semaine -3 |
|---|---|---|---|---|
| Visiteurs | +10 % | | | |
| Signups | +10 % | | | |
| Boutiques générées | +10 % | | | |
| Exports Shopify | +10 % | | | |
| MRR | +5 % | | | |
| Churn | < 8 % | | | |
| Coût IA | < 15 % du MRR | | | |

## Tableau de bord mensuel

| Indicateur | Cible | Mois -1 | Mois -2 | Mois -3 |
|---|---|---|---|---|
| Inscriptions | +30 % | | | |
| Utilisateurs actifs | +25 % | | | |
| Conversion Free → Payant | 3–5 % | | | |
| MRR | +20 % | | | |
| LTV/CAC | > 3 | | | |
| NPS | > 40 | | | |
