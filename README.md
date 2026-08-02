# AI Commerce OS

An AI-powered e-commerce platform designed to maximize organic sales through intelligent automation.

## Overview

AI Commerce OS is a comprehensive SaaS platform that leverages artificial intelligence to automate and optimize every aspect of e-commerce operations. From trend analysis and product evaluation to brand building, store creation, SEO optimization, and content generation, our platform provides a complete toolkit for running successful online stores.

## Key Features

### Intelligent Modules

- **Trend Intelligence (v1)**: ✅ Production-ready trend discovery engine with multi-provider support, automated scoring, and real-time analytics
- **Product Intelligence (v1)**: ✅ Rule-based product evaluation engine with 11 scoring criteria, comprehensive reports, and recommendation system
- **Supplier Intelligence (v1)**: ✅ Modular supplier comparison engine with provider interface, rule-based evaluation, and multi-supplier comparison
- **Brand Builder (v1)**: ✅ AI-powered brand generation engine with modular engines, prompt templates, and integration with previous intelligence engines
- **Store Builder (v1)**: ✅ Complete e-commerce store generation from intelligence data with theme system, validation, and platform-agnostic export
- **Visual Store Renderer (v1)**: ✅ Next.js renderer that transforms store blueprints into navigable e-commerce stores with dynamic components and theme application
- **End-to-End Demo (Phase 7.5)**: ✅ One-click demo mode that runs the whole pipeline (trend, product, supplier, brand, store, preview) with no external API
- **Conversion Optimization Engine (Phase 8)**: ✅ Automatically turns a generated store into one optimized to sell - hero copy, trust signals, objection-handling FAQ, SEO structured data, UX and conversion scoring, all viewable at `/store-analysis/{store_id}`
- **Visual Identity Engine (Sprint 4)**: ✅ Generates a full Brand Asset Pack - logo SVG, favicon, color palette, typography, icons, and ready-to-use image generation prompts for hero, product, and marketing assets
- **CTA Engine (Sprint 4)**: ✅ Produces contextual, category-driven CTA variants with predicted scores
- **FAQ Engine (Sprint 4)**: ✅ Generates category-specific FAQs driven by policies and objections, with diversity scoring
- **Diversity Analyzer (Sprint 4)**: ✅ Compares generated stores to compute CTA, FAQ, title, description and visual-prompt diversity
- **Brand Builder Diversity (Sprint 4.5)**: ✅ Multiple mission/vision template families per category, vibe-driven personality, no more `To provide exceptional...`
- **Visual Prompt Diversity (Sprint 4.5)**: ✅ Multiple prompt structures, styles, lighting, composition, backgrounds and angles per category
- **AI Quality Report (Sprint 4.5)**: ✅ Dashboard with Brand, Prompt, Content, CTA, FAQ and Overall diversity metrics
- **SEO Engine**: Automated metadata generation, content creation, and technical optimization
- **Content Engine**: Produce content variants adapted for different marketing channels
- **Analytics**: Comprehensive dashboards for sales, traffic, conversions, and performance metrics
- **Customer Support**: AI-powered customer assistance using store documentation

### Architecture Highlights

- **Monorepo Structure**: Organized codebase with shared packages and applications
- **Multi-Provider AI**: Abstracted AI layer supporting OpenAI, Anthropic, and custom providers
- **Scalable Backend**: FastAPI with PostgreSQL and Redis for high performance
- **Modern Frontend**: Next.js with TypeScript and Tailwind CSS
- **Containerized**: Full Docker support for easy deployment
- **Agent-Based**: Autonomous agents for continuous optimization tasks

## Technology Stack

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **React**: Component library

### Backend
- **FastAPI**: Modern Python web framework
- **PostgreSQL**: Relational database
- **Redis**: Caching and job queues
- **SQLAlchemy**: ORM for database operations
- **Alembic**: Database migrations

### AI Integration
- **OpenAI**: GPT models
- **Anthropic**: Claude models
- **Custom Provider Support**: Extensible architecture

### DevOps
- **Docker**: Containerization
- **Docker Compose**: Local development
- **npm workspaces**: Dependency management across `apps/*` and `packages/*`
- **Turbo**: Monorepo build system and task orchestration
- **Vitest**: Unit tests for `packages/ui` and `packages/shared`

## Project Structure

```
ai-commerce-os/
├── apps/
│   ├── web/           # Main storefront application
│   ├── admin/         # Admin dashboard
│   └── api/           # FastAPI backend
├── packages/
│   ├── types/         # Shared TypeScript types
│   ├── database/      # Database schema and utilities
│   ├── shared/        # Shared utilities and helpers
│   └── ui/            # Shared UI components
├── services/
│   ├── trend-intelligence/
│   ├── product-intelligence/
│   ├── brand-builder/
│   ├── store-builder/
│   ├── seo-engine/
│   ├── content-engine/
│   ├── analytics/
│   └── customer-support/
├── agents/
│   ├── conversion_engine/  # Standalone, framework-agnostic optimizers (Phase 8)
│   ├── trend-analyst/
│   ├── product-evaluator/
│   ├── brand-creator/
│   ├── store-generator/
│   ├── seo-optimizer/
│   ├── content-writer/
│   └── support-assistant/
├── database/
│   ├── migrations/
│   └── seeds/
├── docker/
│   ├── docker-compose.yml
│   ├── Dockerfile.api
│   ├── Dockerfile.web
│   └── Dockerfile.admin
├── docs/
├── scripts/
└── README.md
```

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+
- Docker and Docker Compose
- PostgreSQL 15+
- Redis 7+

### Installation

See [INSTALL.md](./INSTALL.md) for detailed installation instructions.

### Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd ai-commerce-os

# Copy environment variables
cp .env.example .env

# Install every workspace's dependencies (npm workspaces: apps/*, packages/*)
npm install

# Build all packages/apps in dependency order
npm run build

# Start services with Docker (Postgres, Redis, API, Web, Admin)
npm run docker:up

# Run development servers (Turbo runs `dev` in every workspace)
npm run dev
```

See [Monorepo & Workspaces](./INSTALL.md#monorepo--workspaces) in INSTALL.md for details on how
the workspace is wired together and how to verify `npm install` / `npm run build` succeed.

### Try the End-to-End Demo

No external API key required - the demo pipeline runs entirely on local, rule-based logic.

```bash
# 1. Start Postgres/Redis and the API
npm run docker:up
cd apps/api && pip install -r requirements.txt && uvicorn main:app --reload

# 2. Start the store renderer
cd apps/store-renderer && npm install && npm run dev

# 3. Open http://localhost:3002/demo and click "Generate Demo Store"
```

Or generate a demo store straight from the command line:

```bash
cd apps/api
python seed_demo.py
```

See [PHASE7_5_REPORT.md](./PHASE7_5_REPORT.md) for details on how the demo pipeline works.

### Analyze & Optimize a Store's Conversion Rate

Once you have a `store_id` (from the demo above, or a real generation), run:

```bash
curl -X POST http://localhost:8000/api/v1/stores/1/optimize
```

Then open `http://localhost:3002/store-analysis/1` to see the conversion,
SEO, UX, trust and persuasion scores, plus every recommended action. See
[PHASE8_REPORT.md](./PHASE8_REPORT.md) for details on the Conversion
Optimization Engine (`agents/conversion_engine`).

## Documentation

- [ARCHITECTURE.md](./ARCHITECTURE.md) - Detailed architecture documentation
- [ROADMAP.md](./ROADMAP.md) - Development roadmap and milestones
- [INSTALL.md](./INSTALL.md) - Installation and setup guide
- [TODO.md](./TODO.md) - Current tasks and improvements

## Contributing

Contributions are welcome! Please read our development conventions before submitting pull requests.

## License

Proprietary - All rights reserved

## Support

For support and questions, please contact the development team.

---

**Version**: 0.8.0  
**Status**: Phase 8 - Conversion Optimization Engine Complete  
**Last Updated**: 2026-08-02
