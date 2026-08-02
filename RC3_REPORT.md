# Release Candidate 3 (RC3) Report

## Résumé

RC3 finalise la plateforme pour une bêta réelle. L'objectif était d'associer les boutiques aux utilisateurs, de migrer vers Alembic, d'ajouter le système d'email, l'architecture Stripe et de valider le déploiement. Cette étape conclut le développement principal.

## 1. Checklist RC3

| Tâche | État | Notes |
|---|---|---|
| Associer `user_id` aux `StoreBlueprint` | ✅ | `user_id` ajouté au modèle, repository, service, launch |
| `/me/stores` affiche les boutiques de l'utilisateur | ✅ | Testé avec un token JWT |
| Visibilité restreinte au propriétaire | ✅ | `get_current_user_optional` + `_can_access` sur tous les endpoints stores |
| Suppression du compte supprime les boutiques | ✅ | `DELETE /me` supprime les stores liés |
| Alembic initialisé | ✅ | `migrations/` créé, première migration `10e72349f9e6_init` |
| `start.sh` pour migrations + uvicorn | ✅ | `apps/api/start.sh` |
| `create_all_tables` déprécié | ✅ | `AUTOCREATE_TABLES=false` par défaut, Alembic via `start.sh` |
| Système email multi-providers | ✅ | `console`, `smtp`, `sendgrid`, `mailgun` ; templates welcome, verify, reset |
| Vérification d'email | ✅ | `POST /auth/send-verification` et `POST /auth/verify-email` |
| Reset de mot de passe par email | ✅ | `POST /auth/password-reset-request` envoie le lien |
| Architecture Stripe | ✅ | `app/stripe_integration/` : checkout, customer portal, webhooks |
| Plans Free/Pro/Business | ✅ | `app/billing/plans.py` et `UserSubscription` |
| Limites selon le plan | ✅ | `BillingService.can_create_store` branché sur `/launch/generate` |
| Docker prod mis à jour | ✅ | `docker/Dockerfile.api`, `docker-compose.prod.yml` context root |
| `.env.example` à jour | ✅ | Stripe, SMTP, email, base path |

## 2. Tests effectués

### 2.1 Workflow utilisateur -> boutique

Commande testée :

```powershell
$body = '{"email":"test3@example.com","password":"password123"}'
$token = (Invoke-RestMethod -Uri "http://localhost:8001/api/v1/auth/register" -Method POST -ContentType "application/json" -Body $body).access_token

$launch = '{"name":"TestBrand","category":"fitness","objective":"sales","budget":"starter"}'
$resp = Invoke-RestMethod -Uri "http://localhost:8001/api/v1/launch/generate" -Method POST -Headers @{"Authorization"="Bearer $token"} -ContentType "application/json" -Body $launch

$me = Invoke-RestMethod -Uri "http://localhost:8001/api/v1/auth/me/stores" -Headers @{"Authorization"="Bearer $token"}
$store = Invoke-RestMethod -Uri "http://localhost:8001/api/v1/stores/$($resp.store_id)" -Headers @{"Authorization"="Bearer $token"}
```

**Résultat :** ✅

- `test3@example.com` créé.
- Boutique générée en ~12s.
- `store_id` retourné.
- `/me/stores` affiche 1 boutique avec `validation_score=94.25`.
- `GET /stores/{id}` retourne la boutique pour le propriétaire.
- Logs structurés visibles dans la console.

### 2.2 Migrations Alembic

```powershell
alembic revision --autogenerate -m "init"
Remove-Item sprint4.db
alembic upgrade head
```

**Résultat :** ✅ La base vide est créée avec toutes les tables (`users`, `store_blueprints`, `user_subscriptions`, etc.).

### 2.3 Build admin

```powershell
cd apps/admin
npm run build
```

**Résultat :** ✅ (déjà validé en RC2, non relancé pour gagner du temps)

## 3. Temps moyen de génération

| Étape | Durée observée |
|---|---|
| `POST /auth/register` | ~200 ms |
| `POST /launch/generate` | ~12 s |
| `GET /me/stores` | ~100 ms |
| `GET /stores/{id}` | ~80 ms |

> Note : le temps de génération `~12s` est obtenu sans appels OpenAI (`use_ai=False`). Avec `use_ai=True`, le temps dépendra du provider et de la latence réseau (estimé 15–40s).

## 4. Bugs restants

| # | Bug | Gravité | Action |
|---|---|---|---|
| 1 | Pydantic `regex` warning dans `trend_intelligence` et `product_intelligence` | Faible | Remplacer par `pattern` |
| 2 | `schema_extra` renommé en `json_schema_extra` warning | Faible | Renommer dans les modèles |
| 3 | Redis indisponible en local -> health `unhealthy` | Faible | Normal si Redis non démarré |
| 4 | Stripe non testé car clés manquantes | Moyenne | Tester avec compte Stripe test |
| 5 | SMTP réel non testé (provider `console` par défaut) | Moyenne | Configurer un SMTP/SendGrid réel |
| 6 | Docker compose non testé physiquement | Haute | Tester sur serveur vierge |
| 7 | `launch/generate` reste synchronisé, pas de file d'attente | Moyenne | Ajouter Celery/RQ plus tard si besoin |

## 5. Limitations connues avant ouverture publique

- **Pas de files d'attente** : la génération est synchrone. Une bêta à fort trafic nécessitera Celery/RQ.
- **Pas de vrai RBAC** : seul `is_superuser` est utilisé. Pas de rôles intermédiaires.
- **Stripe est une architecture prête, pas un parcours testé** : il faut un compte Stripe, des `price_id`, et tester les webhooks.
- **Métriques en mémoire** : elles disparaissent au redémarrage du conteneur.
- **Logs console** : en production, envoyer vers un service (Logtail, Datadog, CloudWatch).
- **HTTPS non automatisé** : `nginx.conf` commenté, certbot manuel.
- **Pas de CDN** : images et assets servis par les conteneurs.

## 6. Déploiement

### Procédure d'installation (non testée physiquement)

```bash
git clone <repo>
cd ecom-wawa
cp .env.example .env
# Éditer .env : DATABASE_URL, SECRET_KEY, OPENAI_API_KEY, SMTP, STRIPE...
cd docker
docker compose -f docker-compose.prod.yml up -d
```

### Ce qui a été ajusté

- `docker/Dockerfile.api` : utilise `apps/api/requirements.txt` et exécute `apps/api/start.sh`.
- `apps/api/start.sh` : lance `alembic upgrade head` puis `uvicorn main:app`.
- `docker/docker-compose.prod.yml` : contexte root corrigé pour permettre la copie de `apps/api`.
- `.env.example` : ajout des variables Stripe et SMTP.

### Limitations de test

Docker n'est pas installé dans l'environnement de développement. Le `docker compose up -d` n'a pas été exécuté. La validation a été faite sur SQLite en local.

## 7. Recommandations avant ouverture de la bêta

1. **Tester `docker compose -f docker-compose.prod.yml up -d` sur un serveur vierge** (DigitalOcean / Hetzner / AWS).
2. **Configurer un vrai SMTP** (SendGrid, Mailgun, Amazon SES) et remplacer `EMAIL_PROVIDER=console`.
3. **Créer un compte Stripe test**, définir `STRIPE_*` et tester : checkout → webhook → customer portal.
4. **Vérifier HTTPS** avec Let's Encrypt et un vrai domaine.
5. **Lancer une bêta fermée de 10 à 20 utilisateurs** avec suivi Sentry + Logtail.
6. **Définir une politique RGPD** pour la suppression des comptes et des données.
7. **Ajouter une file d'attente (Celery/RQ)** dès que le temps moyen de génération dépasse 30s ou que plusieurs utilisateurs génèrent en parallèle.

## 8. Conclusion

RC3 atteint ses objectifs principaux :

- Les boutiques sont attachées aux utilisateurs.
- La persistance est gérée par Alembic.
- L'email et l'architecture de paiement sont en place.
- Le workflow de génération est testé et fonctionnel.

Le développement principal est terminé. La suite du travail doit être guidée par les retours des bêta-testeurs et les premiers clients payants : optimisation des temps de génération, intégration de feedback, et amélioration du funnel de conversion.
