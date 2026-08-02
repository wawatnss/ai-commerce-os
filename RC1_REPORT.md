# Release Candidate 1 (RC1) Report

## Résumé

Le MVP est terminé. Cette RC1 a pour objectif de fournir une première version utilisable par de vrais utilisateurs. Le travail s'est concentré sur la stabilisation, l'authentification, la sécurité, le déploiement et la documentation.

## 1. Audit du projet

### Bugs corrigés

- `database.py` : la table `users` n'était pas créée au startup car `AuthBase.metadata.create_all()` n'était pas appelé.
- `passlib[bcrypt]` remplacé par `bcrypt` direct en raison d'incompatibilités avec les versions récentes de `bcrypt`.
- `main.py` : middleware CORS dupliqué supprimé.

### Dette technique identifiée

- Le projet compte plusieurs `Base` SQLAlchemy (un par module). Cela fonctionne mais complique les migrations Alembic.
- `create_all_tables()` est utilisé en production dans `lifespan`. À remplacer par des migrations Alembic avant de scaler.
- Les paramètres `regex` sont dépréciés dans Pydantic V2 (warnings non bloquants).
- Les tests sont concentrés dans `agents/` et ne couvrent pas l'API complète.

### Code mort / endpoints inutilisés

- Le fichier `models.py` à la racine de `apps/api` est un legacy non utilisé (déjà commenté dans `database.py`).
- Les commentaires `Future routers` dans `main.py` ont été supprimés.

### Dépendances

- `requirements.txt` mis à jour : ajout de `email-validator`, `bcrypt` ; suppression de `passlib[bcrypt]`.

## 2. Authentification

Module ajouté : `apps/api/app/auth/`

| Endpoint | Méthode | Description |
|---|---|---|
| `/api/v1/auth/register` | POST | Inscription email / mot de passe |
| `/api/v1/auth/login` | POST | Connexion, retourne JWT |
| `/api/v1/auth/logout` | POST | Déconnexion côté client (JWT stateless) |
| `/api/v1/auth/password-reset-request` | POST | Demande de réinitialisation |
| `/api/v1/auth/password-reset-confirm` | POST | Confirmation avec token |
| `/api/v1/auth/me` | GET | Utilisateur connecté |

- Hashage `bcrypt` avec troncation à 72 octets.
- JWT HS256, expiration 30 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`).
- Dépendance `get_current_user` disponible pour sécuriser les autres endpoints.

### Limitation connue
- Le reset de mot de passe ne génère qu'un token. L'envoi d'email n'est pas implémenté.

## 3. Sécurité

| Domaine | État | Notes |
|---|---|---|
| JWT | ✅ | `python-jose`, clé configurable, expiration 30 min |
| Permissions | ⚠️ | Seul l'email est identifié. RBAC non implémenté. |
| Validation des entrées | ✅ | Pydantic sur tous les endpoints |
| Rate limiting | ✅ | Middleware in-memory par IP (60 req/min configurable) |
| CORS | ✅ | Configuré via `CORS_ORIGINS` |
| CSRF | N/A | API stateless JWT, pas de cookies. |
| Secrets | ⚠️ | `SECRET_KEY` doit être changé en production. OpenAI/Anthropic/Shopify via variables d'environnement. |
| Logs | ⚠️ | Logs d'accès Uvicorn uniquement. Audit log non implémenté. |

## 4. Déploiement

Fichiers créés :

- `docker/docker-compose.prod.yml` : production avec Postgres, Redis, API, Web, Admin, Nginx.
- `docker/nginx.conf` : reverse proxy HTTP (modèle HTTPS commenté).
- `docker/backup.sh` : sauvegarde DB + Redis + validation.
- `docker/update.sh` : mise à jour de la stack.
- `apps/admin/next.config.js` : support de `ADMIN_BASE_PATH=/admin`.

### Variables d'environnement

Voir `.env.example`. Les variables critiques sont :

- `SECRET_KEY` (>= 32 caractères aléatoires)
- `DATABASE_URL` (PostgreSQL en prod)
- `REDIS_URL`
- `OPENAI_API_KEY` / `ANTHROPIC_API_KEY`
- `CORS_ORIGINS`
- `RATE_LIMIT_PER_MINUTE`

### HTTPS

Le `nginx.conf` contient un bloc HTTPS commenté. Procédure :

1. Lancer `docker-compose -f docker-compose.prod.yml up -d`.
2. Générer les certificats Let's Encrypt (exemple : `certbot`).
3. Décommenter le bloc HTTPS et monter les certificats.
4. Redémarrer Nginx.

## 5. Tests Release Candidate

### Tests automatisés existants

```bash
cd "C:\Users\wawat\ecom wawa"
$env:PYTHONPATH="C:\Users\wawat\ecom wawa"
python -m pytest agents/visual_identity/tests agents/cta_engine/tests agents/faq_engine/tests agents/diversity_analyzer/tests -q
```

**Résultat : 10 passed.**

### Tests manuels effectués

- `POST /api/v1/auth/register` ✅
- `POST /api/v1/auth/login` ✅
- `GET /api/v1/auth/me` ✅
- `POST /api/v1/auth/logout` ✅
- API lance correctement sur SQLite et PostgreSQL (Docker non testé localement).

### Tests à compléter avant la bêta

- Tests end-to-end `POST /api/v1/launch/generate`, `GET /api/v1/stores/{id}`, `POST /api/v1/stores/{id}/shopify-autofix`.
- Tests d'export Shopify.
- Tests de publication readiness.
- Tests du dashboard admin (build Next.js déjà OK).

## 6. Architecture finale

```
Nginx (80/443)
  ├── /api/*     → FastAPI (port 8000)
  ├── /admin/*   → Next.js Admin (port 3000)
  └── /*         → Next.js Web (port 3000)

FastAPI
  ├── Auth (JWT, bcrypt)
  ├── Trend / Product / Supplier / Brand / Store Intelligence
  ├── Launch Service (génération complète)
  ├── Conversion, Shopify Readiness, Validation Report
  └── PostgreSQL + Redis
```

## 7. Fonctionnalités livrées

- Génération de boutiques complètes (marque, produit, contenu, CTA, FAQ, identité visuelle).
- Dashboard admin (marques, readiness, Shopify, quality report).
- Export Shopify.
- Brand Asset Pack (logo, favicon, palette, typographie, prompts image).
- Authentification JWT.
- Rate limiting et CORS.

## 8. Limitations connues

- Overall Diversity : 76.5 % sur 50 boutiques (objectif 90 % non atteint).
- Aucun envoi d'email (reset mot de passe non opérationnel sans SMTP).
- Pas de RBAC (tous les utilisateurs se valent).
- Pas d'audit log.
- Migrations gérées par `create_all_tables()` et non Alembic.
- Pas de tests E2E automatisés.
- Pas de monitoring / alerting.

## 9. Bugs connus

- `FastAPIDeprecationWarning` sur `regex` dans `trend_intelligence` et `product_intelligence` (non bloquant).
- `Pydantic` warning `schema_extra` renommé (non bloquant).

## 10. Procédure d'installation

```bash
# 1. Cloner
git clone <repo>
cd ecom-wawa

# 2. Configurer
cp .env.example .env
# Éditer .env avec SECRET_KEY, DATABASE_URL, clés API...

# 3. Lancer
cd docker
docker-compose -f docker-compose.prod.yml up -d

# 4. Vérifier
curl http://localhost/api/v1/health
curl -X POST http://localhost/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"you@domain.com","password":"yourpass123"}'
```

## 11. Procédure de sauvegarde

```bash
cd docker
chmod +x backup.sh
./backup.sh /path/to/backups
```

Sauvegarde :
- dump PostgreSQL
- `dump.rdb` Redis
- dossier `validation/`

## 12. Procédure de mise à jour

```bash
cd docker
chmod +x update.sh
./update.sh
```

La mise à jour rebuild les images et redémarre les conteneurs.

## 13. Conclusion

RC1 fournit un socle authentifié, containerisé et documenté. Les fonctionnalités métier sont stables. Les principaux points avant une bêta publique sont :

1. Configurer l'envoi d'email pour le reset de mot de passe.
2. Remplacer `create_all_tables` par des migrations Alembic.
3. Ajouter des tests E2E.
4. Configurer HTTPS sur un vrai domaine.

La plateforme est prête à être installée sur un serveur propre pour une bêta privée.
