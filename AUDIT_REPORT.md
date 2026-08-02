# Audit Report — RC2

Date : 2026-08-02
Scope : `apps/api`, `apps/admin`, `apps/web`, `docker`, `agents/`
Objectif : identifier les problèmes de production avant bêta commerciale.

## 1. Métrique globale

| Domaine | Score /5 | Commentaire |
|---|---|---|
| Stabilité | 3 | Génération OK, mais pas de migrations, `create_all_tables()` en prod |
| Sécurité | 3 | Auth JWT, rate limit, CORS, mais pas de RBAC ni audit log |
| Performance | 2 | Pas de cache intelligent, appels API AI synchrones, pas de traces |
| Maintenabilité | 2 | Plusieurs `Base` SQLAlchemy, dette dans les routers |
| Observabilité | 1 | Logs bruts, pas de métriques, health check basique |
| Déploiement | 3 | Docker prod proposé, non testé sur serveur vierge |

**Moyenne : 2.3/5 — insuffisant pour ouverture payante sans les corrections ci-dessous.**

## 2. Problèmes par criticité

### Critique (bloquant avant bêta payante)

1. **Pas de migrations Alembic** — `create_all_tables()` détruit/recrée le schéma à chaque démarrage si mal utilisé. En production cela peut causer des pertes.
2. **Pas de logging structuré** — impossible de déboguer un incident client en production.
3. **Pas de permissions / RBAC** — n'importe quel JWT peut appeler n'importe quel endpoint.
4. **Pas de validation d'email** — le reset de mot de passe n'envoie rien, les comptes ne sont pas vérifiés.
5. **Rate limiting in-memory uniquement** — ne fonctionne pas si on scale à plusieurs workers/containers.

### Haute (à corriger rapidement)

6. **Store n'est pas lié à un utilisateur** — impossible de savoir qui a généré quoi, facturation impossible.
7. **Pas d'historique de génération** — pas de traçabilité métier.
8. **Health check basique** — ne vérifie pas PostgreSQL, Redis, AI providers.
9. **Variables d'environnement en clair** — `SECRET_KEY`, clés API peuvent être commitées par erreur.
10. **Pas de gestion des abonnements** — indispensable avant de facturer.

### Moyenne (amélioration qualité)

11. **Warnings Pydantic V2** (`regex` → `pattern`, `schema_extra` → `json_schema_extra`) — bruit de logs.
12. **CORS `allow_origins=["*"]` en dev** — devrait être restreint en prod.
13. **Pas de pagination sur `/stores`** — peut devenir lent avec 1000+ boutiques.
14. **Images produit générées mais absentes du product page** — les rapports disent "No product images".
15. **Docker compose prod n'a pas été testé end-to-end** — risque de build failure.

### Faible (polish)

16. **Nommage inconsistants** : `bebe` vs `baby`, `cuisine` vs `food`, `animaux` vs `pets`.
17. **Composants Next.js non utilisés** : certains imports peuvent être morts.
18. **Absent `__init__.py` dans certains packages** — gère correctement via namespace ? Vérifier.
19. **Dead code** : `apps/api/models.py` legacy non utilisé.
20. **Documentation manquante** pour l'onboarding et la FAQ.

## 3. Endpoints et composants inutilisés

- `apps/api/models.py` — legacy, jamais importé.
- `apps/api/app/demo` — utilisé ? Vérifier s'il reste en prod ou si c'est un POC.
- `apps/admin/app/brands/[id]/readiness` et `shopify` — utilisés mais partagent du code.
- `apps/web` — landing page/statique ? Pas sûr qu'elle soit connectée au funnel de conversion.

## 4. Dépendances

### Utiles en prod
- `fastapi`, `uvicorn`, `sqlalchemy`, `pydantic`, `redis`
- `python-jose`, `bcrypt`, `email-validator`

### À vérifier / potentiellement inutiles
- `anthropic` si seul `openai` est utilisé
- `fpdf2` si les PDFs ne sont plus générés (Sprint 4.6 n'utilise plus screenshots/PDF)
- `httpx` utile pour les appels externes, garder

### Manquantes
- `alembic` pour les migrations (à ajouter)
- `structlog` ou `python-json-logger` pour logs structurés (optionnel)
- `prometheus-client` pour métriques (optionnel)

## 5. Recommandations prioritaires

1. **Ajouter Alembic et retirer `create_all_tables()` du startup.**
2. **Lier `Store` à `User` et protéger les endpoints `launch`.**
3. **Ajouter un `LoggerMiddleware` et logger en JSON.**
4. **Créer un endpoint `/health` détaillé (DB, Redis, AI).**
5. **Préparer l'architecture des plans d'abonnement.**
6. **Tester `docker-compose -f docker-compose.prod.yml up` sur un serveur vierge.**
7. **Ajouter pagination et indexes sur `store_name`, `created_at`.**

## 6. Conclusion

Le MVP est solide. Avant d'ouvrir la bêta commerciale, il faut impérativement résoudre les 5 points critiques. Le reste est du polish qui peut être géré dans un hotfix rapide.
