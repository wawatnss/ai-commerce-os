# Changelog

## [v1.0.0-beta] - 2026-08-02

### Ajouts

- **Authentification complète**
  - Inscription, connexion, déconnexion, JWT
  - Modification du profil, changement de mot de passe, suppression de compte
  - Vérification d'email et réinitialisation de mot de passe par email
  - Historique des boutiques par utilisateur

- **Génération de boutiques end-to-end**
  - `/api/v1/launch/generate` : Trend → Product → Supplier → Brand → Store → Optimize
  - Génération rule-based et option OpenAI
  - Enrichissement visuel : CTA, FAQ, identité visuelle

- **Store Builder**
  - CRUD boutiques avec pagination et filtrage par utilisateur
  - Export JSON et Shopify
  - Publication readiness et Shopify readiness
  - Auto-fix Shopify
  - Conversion Optimization Engine

- **Brand Builder**
  - Génération de profils de marque
  - Palettes, typographies, slogans, missions

- **Billing & Abonnements**
  - Plans Free, Pro, Business
  - `UserSubscription` et `BillingService`
  - Architecture Stripe (checkout, customer portal, webhooks)

- **Email**
  - Provider abstrait supportant console, SMTP, SendGrid, Mailgun
  - Templates welcome, vérification, reset

- **Observabilité**
  - Logs structurés
  - Health check détaillé (API, DB, Redis)
  - Métriques par endpoint
  - Page Admin System Status

- **Dashboard Admin**
  - Stats (boutiques générées, score moyen, générations IA)
  - Liste des marques
  - Rapport Qualité IA

- **Onboarding**
  - Page onboarding étape par étape
  - FAQ intégrée

- **Déploiement**
  - Docker production (`docker-compose.prod.yml`, `Dockerfile.api/admin/web`, `nginx.conf`)
  - Alembic (migrations initiales)
  - Scripts `backup.sh` et `update.sh`

### Changements

- `create_all_tables()` retiré du démarrage automatique en production
- Rate limiting par IP
- CORS configurable
- `StoreBlueprint` lié au `user_id`

### Corrections

- Incompatibilité `passlib`/`bcrypt` corrigée en passant à `bcrypt` direct
- Table `users` correctement créée via Alembic
- Suppression du compte supprime les boutiques associées

### Limitations connues

- Docker non testé physiquement
- Stripe non testé sans clés
- SMTP en mode console par défaut
- Pas de file d'attente (génération synchrone)
- Pas d'éditeur WYSIWYG
