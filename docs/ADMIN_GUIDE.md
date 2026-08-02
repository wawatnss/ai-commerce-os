# Guide administrateur — AI Commerce OS v1.0.0-beta

Ce guide est destiné à l'équipe technique qui installe, déploie et exploite AI Commerce OS.

## Architecture

```
Nginx (HTTPS)
  ├── /api/*     → FastAPI (Python)
  ├── /admin/*   → Next.js Admin
  └── /*         → Next.js Web (landing)

FastAPI
  ├── Auth (JWT, bcrypt, email)
  ├── Billing (Free/Pro/Business, Stripe)
  ├── Launch (génération complète)
  ├── Store Builder (blueprints, export, readiness)
  ├── Brand / Product / Supplier / Trend Intelligence
  └── PostgreSQL + Redis
```

## Variables d'environnement critiques

| Variable | Description | Exemple |
|---|---|---|
| `DATABASE_URL` | PostgreSQL | `postgresql+psycopg2://user:pass@postgres/db` |
| `REDIS_URL` | Cache / sessions | `redis://redis:6379/0` |
| `SECRET_KEY` | JWT | 64 caractères aléatoires |
| `OPENAI_API_KEY` | Génération IA | `sk-...` |
| `EMAIL_PROVIDER` | smtp, sendgrid, mailgun, console | `smtp` |
| `STRIPE_SECRET_KEY` | Paiements | `sk_test_...` |
| `STRIPE_WEBHOOK_SECRET` | Webhooks Stripe | `whsec_...` |
| `STRIPE_PRICE_ID_PRO` | Prix Stripe Pro | `price_...` |
| `CORS_ORIGINS` | Origines front | `["https://admin.votredomaine.com"]` |

## Démarrage

```bash
cd docker
docker compose -f docker-compose.prod.yml up -d
```

Vérifiez :

```bash
curl http://localhost:8000/health
```

## Migrations

Les migrations Alembic sont exécutées automatiquement par `apps/api/start.sh` au démarrage du conteneur `api`.

Pour forcer une migration manuelle :

```bash
cd apps/api
alembic upgrade head
```

## Sauvegardes

```bash
cd docker
chmod +x backup.sh
./backup.sh /chemin/des/backups
```

Le script sauvegarde :
- le dump PostgreSQL
- le fichier `dump.rdb` Redis
- le dossier `validation/`

## Mises à jour

```bash
cd docker
chmod +x update.sh
./update.sh
```

Le script :
1. `git pull`
2. rebuild des images
3. redémarrage des conteneurs
4. exécution des migrations

## Monitoring de base

- `/health` : état API, DB, Redis
- `/api/v1/admin/system-status` : métriques de requêtes
- Logs : `docker logs ai-commerce-api`

## Sécurité

- Changez `SECRET_KEY` dès l'installation.
- Limitez `CORS_ORIGINS` aux domaines de production.
- Activez HTTPS via `nginx.conf` + Let's Encrypt.
- Ne stockez jamais de clés API dans le code.

## Dépannage courant

| Symptôme | Cause probable | Solution |
|---|---|---|
| ` unhealthy` Redis | Redis non démarré | `docker compose up -d redis` |
| 500 sur `/launch/generate` | clé OpenAI manquante | renseigner `OPENAI_API_KEY` |
| Emails non envoyés | SMTP mal configuré | vérifier `EMAIL_PROVIDER` et `SMTP_*` |
| 403 sur `/api/v1/admin/*` | token manquant ou expiré | se reconnecter |
