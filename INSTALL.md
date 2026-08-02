# AI Commerce OS - Installation Guide

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Docker Installation](#docker-installation)
4. [Manual Installation](#manual-installation)
5. [Configuration](#configuration)
6. [Database Setup](#database-setup)
7. [Running the Application](#running-the-application)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software

- **Node.js**: Version 18.0.0 or higher
- **Python**: Version 3.11 or higher
- **npm**: Version 9.0.0 or higher
- **Docker**: Version 20.10.0 or higher
- **Docker Compose**: Version 2.0.0 or higher
- **Git**: For cloning the repository

### Optional Software

- **PostgreSQL Client**: For direct database access
- **Redis CLI**: For direct Redis access
- **VS Code**: Recommended IDE with extensions

### System Requirements

- **RAM**: Minimum 8GB, recommended 16GB
- **Disk Space**: Minimum 20GB free space
- **CPU**: Multi-core processor recommended

## Monorepo & Workspaces

This project uses **npm workspaces** to manage the JavaScript/TypeScript side of the monorepo
(`apps/*` and `packages/*`), orchestrated by **Turbo** for caching and task scheduling.

```
ai-commerce-os/
├── apps/
│   ├── web/             # Next.js storefront (App Router)
│   ├── admin/           # Next.js admin dashboard (App Router)
│   ├── store-renderer/  # Next.js store preview renderer (Pages Router)
│   └── api/             # FastAPI backend (Python, not an npm workspace dependency)
└── packages/
    ├── types/           # Shared TypeScript types, consumed directly from src
    ├── shared/           # Shared utilities: formatDate, formatCurrency, slugify, classNames/cn, ...
    ├── ui/               # Shared React component library (Button, Card, Container, Section,
    │                     # Heading, Text, Input, Badge, Grid)
    └── database/        # Drizzle ORM schema and database utilities
```

- `packages/ui` and `packages/shared` are built with `tsc` into `dist/`, and consumed by the
  Next.js apps both through Node module resolution (`main`/`types` fields) and through Next's
  `transpilePackages` option, which lets the apps import the TypeScript source directly.
- `apps/api` has a `package.json` purely so Turbo/npm can orchestrate its scripts (`dev`, `test`,
  `lint`, ...) alongside the rest of the monorepo. Its real dependencies live in
  `requirements.txt` and are installed with `pip`, never with `npm`, to avoid dependency-confusion
  risks (Python package names are not npm package names).

### Verifying the workspace setup

```bash
# Install every workspace's dependencies in one shot
npm install

# Build every package/app in dependency order (packages/types -> packages/shared ->
# packages/ui -> apps/*)
npm run build

# Run the JS/TS test suites (packages/ui, packages/shared)
npm run test

# Type-check and lint every workspace
npm run typecheck
npm run lint
```

All of the commands above should complete without errors for the Node.js/TypeScript workspaces.
`apps/api`'s `test`, `lint` and `typecheck` scripts call Python tools (`pytest`, `ruff`, `mypy`)
which require the virtualenv from [Manual Installation](#manual-installation) step
"Install Python Dependencies" plus `pip install ruff mypy pytest` — install these to include the
API in those checks. Because the monorepo mixes Node and Python tooling, `npm run test`, `lint` and
`typecheck` all pass `--continue` to Turbo so a missing Python toolchain doesn't prevent the
JavaScript/TypeScript workspaces from reporting their own results.

## Environment Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ai-commerce-os
```

### 2. Verify Software Versions

```bash
# Check Node.js
node --version  # Should be 18.0.0 or higher

# Check npm
npm --version  # Should be 9.0.0 or higher

# Check Python
python --version  # Should be 3.11 or higher

# Check Docker
docker --version  # Should be 20.10.0 or higher

# Check Docker Compose
docker-compose --version  # Should be 2.0.0 or higher
```

### 3. Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit the `.env` file with your specific configuration:

```bash
# Database
POSTGRES_USER=ai_commerce
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=ai_commerce
DATABASE_URL=postgresql+psycopg2://ai_commerce:your_secure_password@localhost:5432/ai_commerce

# Redis
REDIS_URL=redis://localhost:6379/0

# AI Providers
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Security
SECRET_KEY=your_very_secure_secret_key_change_this

# Application
NODE_ENV=development
NEXT_PUBLIC_API_URL=http://localhost:8000
API_PORT=8000
WEB_PORT=3000
ADMIN_PORT=3001
```

## Docker Installation

### Quick Start with Docker Compose

This is the recommended method for local development.

#### 1. Start Services

```bash
# Start PostgreSQL and Redis
npm run docker:up

# Or directly with docker-compose
cd docker
docker-compose up -d
```

#### 2. Verify Services

```bash
# Check PostgreSQL
docker ps | grep postgres

# Check Redis
docker ps | grep redis

# Check logs
docker-compose logs -f
```

#### 3. Stop Services

```bash
npm run docker:down

# Or directly
cd docker
docker-compose down
```

#### 4. Rebuild Services

```bash
npm run docker:build

# Or directly
cd docker
docker-compose build
```

> **Note:** `docker/Dockerfile.web` and `docker/Dockerfile.admin` build with the **monorepo root**
> as their Docker build context (`docker-compose.yml` sets `context: ..`), because `npm install`
> needs to see every workspace (`apps/*`, `packages/*`) to resolve internal dependencies such as
> `@ai-commerce/ui`. Each image runs `npx turbo run build --filter=<app>...` inside the build stage
> and then copies only the Next.js `standalone` output into the final runtime image, so the
> published images stay small despite the larger build context. `docker/Dockerfile.api` is
> unaffected and keeps `apps/api` as its build context since it has no npm workspace dependencies.

### Docker Services

The following services are included in Docker Compose:

- **PostgreSQL**: Database server on port 5432
- **Redis**: Cache and message queue on port 6379
- **API**: FastAPI backend on port 8000
- **Web**: Next.js storefront on port 3000
- **Admin**: Next.js admin on port 3001

## Manual Installation

If you prefer not to use Docker for all services, you can install components manually.

### 1. Install PostgreSQL

#### Windows
Download and install from: https://www.postgresql.org/download/windows/

#### macOS
```bash
brew install postgresql@15
brew services start postgresql@15
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### 2. Install Redis

#### Windows
Download and install from: https://github.com/microsoftarchive/redis/releases

#### macOS
```bash
brew install redis
brew services start redis
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis
```

### 3. Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create user and database
CREATE USER ai_commerce WITH PASSWORD 'your_secure_password';
CREATE DATABASE ai_commerce OWNER ai_commerce;
GRANT ALL PRIVILEGES ON DATABASE ai_commerce TO ai_commerce;
\q
```

## Configuration

### 1. Install Node.js Dependencies

```bash
# Install root dependencies
npm install

# Install all workspace dependencies
npm install --workspaces
```

### 2. Install Python Dependencies

```bash
cd apps/api

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure TypeScript

The TypeScript configuration is already set up in `tsconfig.json` at the root level. Each application has its own `tsconfig.json` that extends the root configuration.

### 4. Configure ESLint and Prettier

```bash
# Install linting tools
npm install -D eslint prettier

# Run linting
npm run lint

# Run formatting
npm run format
```

## Database Setup

### 1. Run Migrations

#### Using Alembic (Python)

```bash
cd apps/api

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Initialize Alembic (first time only)
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Run migration
alembic upgrade head
```

#### Using Drizzle (TypeScript)

```bash
cd packages/database

# Generate migration
npm run migrate

# Run migration
npm run migrate:up
```

### 2. Seed Database

```bash
cd apps/api

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Run seed script
python scripts/seed.py
```

### 3. Verify Database

```bash
# Connect to database
psql -U ai_commerce -d ai_commerce

# List tables
\dt

# Exit
\q
```

## Running the Application

### Development Mode

#### 1. Start PostgreSQL and Redis

If not using Docker Compose for these services:

```bash
# Start PostgreSQL
# On Windows
net start postgresql-x64-15
# On macOS/Linux
brew services start postgresql@15
# or
sudo systemctl start postgresql

# Start Redis
# On Windows
redis-server
# On macOS/Linux
brew services start redis
# or
sudo systemctl start redis
```

#### 2. Start API Backend

```bash
cd apps/api

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. Start Web Storefront

```bash
cd apps/web

# Install dependencies (if not already installed)
npm install

# Run development server
npm run dev
```

#### 4. Start Admin Dashboard

```bash
cd apps/admin

# Install dependencies (if not already installed)
npm install

# Run development server
npm run dev
```

#### 5. Using Turbo for All Services

```bash
# Start all services in development mode
npm run dev
```

### Production Mode

#### 1. Build Applications

```bash
# Build all applications
npm run build

# Build specific application
cd apps/web
npm run build
```

#### 2. Start Production Servers

```bash
# Start API
cd apps/api
uvicorn main:app --host 0.0.0.0 --port 8000

# Start Web
cd apps/web
npm start

# Start Admin
cd apps/admin
npm start
```

#### 3. Using Docker Compose

```bash
cd docker
docker-compose up -d
```

## Verification

### 1. Health Check

```bash
# Check API health
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "app": "AI Commerce OS",
#   "version": "0.1.0"
# }
```

### 2. Access Applications

- **Web Storefront**: http://localhost:3000
- **Admin Dashboard**: http://localhost:3001
- **API Documentation**: http://localhost:8000/docs

### 3. Database Connection

```bash
# Test database connection
psql -U ai_commerce -d ai_commerce -c "SELECT version();"
```

### 4. Redis Connection

```bash
# Test Redis connection
redis-cli ping
# Expected response: PONG
```

## Troubleshooting

### Common Issues

#### Port Already in Use

```bash
# Find process using port
# On Windows
netstat -ano | findstr :3000
# On macOS/Linux
lsof -i :3000

# Kill process
# On Windows
taskkill /PID <PID> /F
# On macOS/Linux
kill -9 <PID>
```

#### Database Connection Failed

```bash
# Check PostgreSQL status
# On Windows
net start postgresql-x64-15
# On macOS/Linux
brew services list
# or
sudo systemctl status postgresql

# Check connection string in .env
# Ensure DATABASE_URL is correct
```

#### Redis Connection Failed

```bash
# Check Redis status
# On Windows
redis-cli ping
# On macOS/Linux
redis-cli ping

# Start Redis if not running
# On macOS/Linux
brew services start redis
# or
sudo systemctl start redis
```

#### Python Dependencies Issues

```bash
# Recreate virtual environment
cd apps/api
rm -rf venv
python -m venv venv

# Activate and reinstall
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

#### Node.js Dependencies Issues

```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# For workspace
rm -rf node_modules package-lock.json apps/*/node_modules packages/*/node_modules
npm install
```

#### Docker Issues

```bash
# Restart Docker daemon
# On Windows
# Restart Docker Desktop from system tray

# On macOS/Linux
sudo systemctl restart docker

# Rebuild containers
cd docker
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Logs and Debugging

#### API Logs

```bash
# Development logs are shown in terminal
# For production, check configured log location
```

#### Docker Logs

```bash
cd docker
docker-compose logs -f

# Specific service logs
docker-compose logs -f api
docker-compose logs -f web
docker-compose logs -f postgres
```

#### Database Logs

```bash
# PostgreSQL logs location varies by OS
# On macOS/Linux
tail -f /usr/local/var/log/postgres.log
# or
tail -f /var/log/postgresql/postgresql-15-main.log
```

### Getting Help

If you encounter issues not covered here:

1. Check the [ARCHITECTURE.md](./ARCHITECTURE.md) for system details
2. Review the [ROADMAP.md](./ROADMAP.md) for current phase status
3. Check the [TODO.md](./TODO.md) for known issues
4. Contact the development team

---

## Next Steps

After successful installation:

1. Review the [ARCHITECTURE.md](./ARCHITECTURE.md) to understand the system
2. Check the [ROADMAP.md](./ROADMAP.md) for development progress
3. Set up your development environment with IDE extensions
4. Review coding conventions and guidelines
5. Start with the current phase tasks

---

**Document Version**: 1.0  
**Last Updated**: 2026-08-01  
**Maintained By**: Development Team
