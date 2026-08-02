# Guide de déploiement sur VPS Linux — AI Commerce OS v1.0.0-beta

## Prérequis

- Un VPS Ubuntu 22.04/24.04, 2 vCPU, 4 GB RAM minimum
- Un nom de domaine pointant vers le VPS
- Docker + Docker Compose installés
- (Optionnel) un compte Cloudflare pour gérer le DNS

## 1. Préparer le serveur

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker.io docker-compose-plugin git
sudo usermod -aG docker $USER
# Se déconnecter puis reconnecter pour appliquer le groupe docker
```

## 2. Cloner et configurer

```bash
git clone <url-du-repo> ai-commerce
 cd ai-commerce
 cp .env.example .env
```

Éditez `.env` :

```env
DOMAIN=votredomaine.com
NEXT_PUBLIC_API_URL=https://api.votredomaine.com
SECRET_KEY=$(openssl rand -base64 48)
DATABASE_URL=postgresql+psycopg2://ai_commerce:ai_commerce_password@postgres:5432/ai_commerce
REDIS_URL=redis://redis:6379/0
OPENAI_API_KEY=sk-...
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=SG.xxx
EMAIL_FROM=noreply@votredomaine.com
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID_PRO=price_...
STRIPE_PRICE_ID_BUSINESS=price_...
CORS_ORIGINS=["https://admin.votredomaine.com"]
```

## 3. Lancer la stack

```bash
cd docker
sudo docker compose -f docker-compose.prod.yml up -d
```

Vérifiez :

```bash
sudo docker compose ps
sudo docker logs ai-commerce-api
```

## 4. Configurer Nginx HTTPS

### Option A : Certificat Let's Encrypt

```bash
sudo apt install -y certbot
sudo certbot certonly --standalone -d admin.votredomaine.com -d api.votredomaine.com -d votredomaine.com
```

Décommentez le bloc HTTPS dans `docker/nginx.conf` et montez les certificats dans `docker-compose.prod.yml`.

### Option B : Cloudflare origin certificate

1. Générez un certificat dans Cloudflare.
2. Placez `cloudflare_origin.pem` et `cloudflare_origin.key` dans `docker/certs/`.
3. Montez les certificats dans `docker-compose.prod.yml`.

## 5. DNS

Configurez les enregistrements A :

```
votredomaine.com     A  <IP-du-VPS>
admin.votredomaine.com  A  <IP-du-VPS>
api.votredomaine.com    A  <IP-du-VPS>
```

## 6. Backups

```bash
sudo mkdir -p /var/backups/ai-commerce
sudo docker exec ai-commerce-postgres pg_dump -U ai_commerce ai_commerce > /var/backups/ai-commerce/db-$(date +%F).sql
sudo docker cp ai-commerce-redis:/data/dump.rdb /var/backups/ai-commerce/redis-$(date +%F).rdb
```

Vous pouvez aussi utiliser `docker/backup.sh` en remplaçant le chemin cible.

## 7. Mise à jour

```bash
cd ai-commerce
git pull
cd docker
sudo docker compose -f docker-compose.prod.yml down
sudo docker compose -f docker-compose.prod.yml up -d --build
```

Les migrations Alembic sont exécutées automatiquement par le conteneur `api`.

## 8. Checklist post-déploiement

- [ ] `/health` retourne `healthy`
- [ ] `/api/v1/auth/register` crée un utilisateur
- [ ] `/admin` est accessible
- [ ] HTTPS fonctionne
- [ ] Les emails partent (vérifier les logs)
- [ ] Un paiement test Stripe fonctionne
- [ ] La sauvegarde automatique est programmée
