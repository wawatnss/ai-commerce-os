# Guide d'installation — AI Commerce OS v1.0.0-beta

Ce guide explique comment installer AI Commerce OS sur votre machine locale ou un serveur de développement.

## Prérequis

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+ (ou SQLite pour les tests)
- Redis 7+
- Compte OpenAI (obligatoire pour la génération avec IA)
- Comptes SMTP et Stripe (optionnels mais recommandés pour la production)

## 1. Cloner le dépôt

```bash
git clone <url-du-repo>
cd ecom-wawa
```

## 2. Configurer l'environnement

```bash
cp .env.example .env
```

Éditez `.env` et renseignez au minimum :

```env
DATABASE_URL=sqlite:///./sprint4.db           # pour les tests
# DATABASE_URL=postgresql+psycopg2://...      # pour la production
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=sk-...
SECRET_KEY=une-clé-très-longue-et-aléatoire
```

## 3. Installer l'API

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate  # Windows : .\.venv\Scripts\activate
pip install -r requirements.txt
```

## 4. Créer la base de données

```bash
alembic upgrade head
```

> Sur SQLite, `alembic` créera automatiquement le fichier `sprint4.db`.  
> Sur PostgreSQL, assurez-vous que la base existe et est accessible.

## 5. Lancer l'API

```bash
uvicorn main:app --port 8000
# ou, pour les migrations + démarrage en un seul script :
./start.sh
```

## 6. Installer l'Admin

```bash
cd apps/admin
npm install
npm run build
```

Pour le mode développement :

```bash
npm run dev
```

Pour le mode production :

```bash
npm start
```

## 7. Vérifier l'installation

- API : `http://localhost:8000/health`
- Admin : `http://localhost:3000` ou `http://localhost:3001`
- Documentation OpenAPI : `http://localhost:8000/docs`

## 8. Premier utilisateur

Utilisez l'API directement pour créer un compte :

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"vous@exemple.com","password":"votre-mot-de-passe"}'
```

Récupérez le `access_token` dans la réponse et utilisez-le pour les appels suivants.
