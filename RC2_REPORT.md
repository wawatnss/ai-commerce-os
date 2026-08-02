# Release Candidate 2 (RC2) Report

## Résumé

RC2 a pour objectif de rendre la plateforme prête à accueillir des utilisateurs payants. Le travail a porté sur l'audit, l'observabilité, la gestion des utilisateurs, l'architecture d'abonnement, le dashboard et l'onboarding.

## 1. Audit complet

Fichier livré : `AUDIT_REPORT.md`

- 20 problèmes identifiés classés par criticité.
- 5 points bloquants déclarés avant bêta payante : migrations, permissions, email, rate limiting distribué, liens user-store.
- Score global : 2.3/5 avant corrections, 3.0/5 après RC2.

## 2. Observabilité

### Implémenté

- Logs structurés (format texte avec timestamp, level, name, message) via `app/core/logging.py`.
- `LoggerMiddleware` : log début/fin de chaque requête avec méthode, path, status, duration.
- `MetricsCollector` : compteurs, erreurs 500 et temps moyen par endpoint.
- Health check étendu : API, PostgreSQL, Redis.
- Endpoint `/api/v1/admin/system-status` (public en RC2, à sécuriser avant ouverture).
- Page Admin `System Status` (`apps/admin/app/system/page.tsx`).

### Limitations
- Pas d'export vers Prometheus/CloudWatch.
- Pas d'alerting.
- Métriques en mémoire uniquement (perdues au redémarrage).

## 3. Gestion des utilisateurs

### Endpoints ajoutés

| Endpoint | Description |
|---|---|
| `GET /api/v1/auth/me` | Profil |
| `PATCH /api/v1/auth/me` | Modifier email |
| `POST /api/v1/auth/me/password` | Changer le mot de passe |
| `DELETE /api/v1/auth/me` | Supprimer le compte |
| `GET /api/v1/auth/me/stores` | Historique des boutiques générées |
| `POST /api/v1/auth/me/verify-email` | Vérifier l'email (stub, envoi réel à intégrer) |

### Modèle
- `User` : ajout de `email_verified`.
- `StoreBlueprint` : ajout de `user_id` (optionnel, prêt pour le lien user-store).

### Limitations
- L'envoi d'email de vérification n'est pas branché.
- Les endpoints de génération (`/launch/generate`) ne passent pas encore l'`user_id` (peut être branché en branchant `get_current_user` dans `launch` router).
- Pas d'upload d'avatar ou de profil enrichi.

## 4. Gestion des abonnements (architecture)

Fichiers créés :

- `app/billing/models.py` : `UserSubscription` avec `user_id`, `plan`, `status`, `expires_at`.
- `app/billing/plans.py` : plans `free`, `pro`, `business` avec limites.
- `app/billing/service.py` : `BillingService` pour vérifier les limites de boutiques.

| Plan | Boutiques | Exports | Générations | Crédits IA | Support |
|---|---|---|---|---|---|
| Free | 3 | 1 | 5 | 0 | community |
| Pro | 25 | 10 | 50 | 500 | email |
| Business | illimité | illimité | illimité | 5000 | priority |

### Limitations
- Aucune intégration de prestataire de paiement.
- Aucun webhook de facturation.
- Les limites ne sont pas encore appliquées dans les endpoints.

## 5. Dashboard

- Endpoint `/api/v1/dashboard` : total de boutiques, score moyen, dernières générations, consommation IA.
- Page Admin `Dashboard` (`/`) mise à jour avec statistiques.
- Navigation admin revue avec liens Dashboard, Qualité IA, Système, FAQ.

## 6. Onboarding

- Page `Onboarding` (`/onboarding`) avec les 5 étapes clés.
- Page `FAQ` (`/faq`) avec 6 questions/réponses.
- La visite guidée interactive et l'aide contextuelle ne sont pas implémentées (peut être ajoutée avec un outil comme `react-joyride`).

## 7. Déploiement

### Test sur serveur vierge

- Docker n'est pas disponible dans cet environnement, donc `docker compose up -d` n'a pas été testé physiquement.
- Les fichiers `docker/docker-compose.prod.yml`, `docker/nginx.conf`, `docker/backup.sh` et `docker/update.sh` sont à jour.
- L'admin supporte `ADMIN_BASE_PATH=/admin` via la variable d'environnement.
- `.env.example` est à jour.

### Procédure d'installation restante

```bash
git clone <repo>
cd ecom-wawa
cp .env.example .env
# éditer .env
cd docker
docker compose -f docker-compose.prod.yml up -d
```

## 8. Tests

### Tests automatisés

```bash
pytest agents/visual_identity/tests agents/cta_engine/tests agents/faq_engine/tests agents/diversity_analyzer/tests -q
```

**Résultat : 10 passed.**

### Tests manuels effectués

| Scénario | État |
|---|---|
| `POST /api/v1/auth/register` | ✅ |
| `GET /api/v1/health` | ✅ (Redis indisponible en local, d'où `unhealthy`) |
| `GET /api/v1/dashboard` | ✅ |
| `GET /api/v1/admin/system-status` | ✅ |
| Admin build | ✅ |

### Tests NON effectués

- Installation Docker sur serveur vierge (Docker indisponible ici).
- Création de marque complète avec nouvelle authentification.
- Export Shopify end-to-end.
- Sauvegarde et restauration.
- Tests E2E.

## 9. Bugs restants

1. Redis health check est `error` quand Redis n'est pas lancé (comportement attendu, mais provoque `unhealthy` en dev).
2. Pydantic warnings `regex` et `schema_extra` non corrigés (non bloquants).
3. `launch/generate` n'utilise pas encore `get_current_user`, donc les boutiques ne sont pas liées au compte.
4. La vérification d'email est un stub.

## 10. Limitations connues

- Pas de migrations Alembic (toujours `create_all_tables`).
- Pas de RBAC.
- Pas d'audit log.
- Pas d'intégration de paiement.
- Métriques en mémoire.
- Pas de tests E2E.
- Docker prod non testé physiquement.
- Pas d'envoi d'email SMTP.

## 11. Recommandations avant ouverture de la bêta

1. **Brancher `get_current_user` sur `/api/v1/launch/generate`** pour lier boutique et utilisateur.
2. **Ajouter Alembic** et retirer `create_all_tables` du startup.
3. **Configurer un serveur SMTP** pour la vérification d'email et le reset de mot de passe.
4. **Tester `docker compose up -d`** sur un serveur vierge (DigitalOcean, Hetzner, etc.).
5. **Ajouter un provider de paiement** (Stripe, Lemon Squeezy) et appliquer les limites de plan.
6. **Mettre en place un vrai monitoring** (Sentry, Logtail, Prometheus).
7. **Lancer une bêta fermée de 20 utilisateurs** pour mesurer conversion, bugs et revenu.

## 12. Conclusion

RC2 fournit une fondation production-ready pour une bêta privée : auth, health, billing, dashboard, onboarding. Les 7 points bloquants restants sont documentés et peuvent être traités en 1 à 2 sprints. La plateforme n'est pas encore prête pour des utilisateurs payants sans ces ajustements, mais elle est proche.
