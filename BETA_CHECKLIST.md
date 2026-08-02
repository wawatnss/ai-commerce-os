# BETA_CHECKLIST.md — AI Commerce OS v1.0.0-beta

## Avant le lancement

### Infrastructure

- [ ] VPS Linux provisionné (Ubuntu 22.04/24.04)
- [ ] Docker et Docker Compose installés
- [ ] Nom de domaine enregistré et DNS pointé vers le VPS
- [ ] Ports 80/443 ouverts
- [ ] Certificat HTTPS configuré (Let's Encrypt ou Cloudflare)

### Base de données

- [ ] PostgreSQL 15+ accessible
- [ ] Migrations Alembic exécutées (`alembic upgrade head`)
- [ ] Redis accessible
- [ ] Backups automatisés testés

### API

- [ ] `SECRET_KEY` changée (>= 64 caractères aléatoires)
- [ ] `OPENAI_API_KEY` renseignée
- [ ] `DATABASE_URL` correcte
- [ ] `REDIS_URL` correcte
- [ ] CORS restreint aux domaines de production
- [ ] Rate limit adapté au plan

### Email

- [ ] SMTP / SendGrid / Mailgun configuré
- [ ] Email de bienvenue envoyé
- [ ] Vérification d'email testée
- [ ] Reset de mot de passe testé

### Paiements

- [ ] Compte Stripe créé
- [ ] `STRIPE_SECRET_KEY` renseignée
- [ ] `STRIPE_WEBHOOK_SECRET` renseignée
- [ ] `STRIPE_PRICE_ID_*` renseignées
- [ ] Checkout test session effectuée
- [ ] Webhook testé
- [ ] Customer Portal testé

### Front

- [ ] Admin buildé (`npm run build`)
- [ ] Web buildé (`npm run build`)
- [ ] Nginx redirige `/admin` vers admin
- [ ] Nginx redirige `/api` vers API

### Monitoring

- [ ] `/health` retourne `healthy`
- [ ] Logs centralisés (Logtail, Datadog ou CloudWatch)
- [ ] Sentry configuré pour les erreurs front
- [ ] Backups testés

### Conformité

- [ ] Page de politique de confidentialité
- [ ] Mention des conditions d'utilisation
- [ ] Processus de suppression de compte documenté
- [ ] RGPD : possibilité d'exporter/supprimer ses données

## Tests à effectuer avant ouverture

1. [ ] Inscription + vérification email
2. [ ] Connexion / déconnexion
3. [ ] Création d'une marque via `/launch/generate`
4. [ ] Vérification que la boutique apparaît dans `/me/stores`
5. [ ] Optimisation d'une boutique
6. [ ] Vérification du score de publication readiness
7. [ ] Vérification du score Shopify readiness
8. [ ] Auto-fix Shopify
9. [ ] Export Shopify
10. [ ] Upgrade vers plan Pro (test mode Stripe)
11. [ ] Customer Portal
12. [ ] Suppression de compte

## Go / No-Go

| Élément | Statut | Signataire |
|---|---|---|
| Infra OK | | |
| Workflow OK | | |
| Paiements OK | | |
| Emails OK | | |
| HTTPS OK | | |
| Sauvegardes OK | | |
