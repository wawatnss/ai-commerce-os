# AI Commerce OS - Architecture Documentation

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Principles](#architecture-principles)
3. [Component Architecture](#component-architecture)
4. [Data Architecture](#data-architecture)
5. [Service Architecture](#service-architecture)
6. [Agent Architecture](#agent-architecture)
7. [AI Integration](#ai-integration)
8. [Security Architecture](#security-architecture)
9. [Scalability Strategy](#scalability-strategy)
10. [Technology Choices](#technology-choices)
11. [Trend Intelligence Engine](#trend-intelligence-engine)

## System Overview

AI Commerce OS is designed as a modular, scalable SaaS platform that orchestrates multiple AI-powered services to automate e-commerce operations. The system follows a microservices-inspired architecture within a monorepo structure, balancing development efficiency with production scalability.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                          │
├──────────────────────────┬──────────────────────────────────┤
│     Web Storefront       │       Admin Dashboard            │
│     (Next.js)            │       (Next.js)                  │
└──────────┬───────────────┴──────────────┬───────────────────┘
           │                              │
           └──────────────┬───────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                      API Gateway Layer                       │
│                    (FastAPI Backend)                        │
└──────────┬──────────────────────────────────────────────────┘
           │
┌──────────▼──────────────────────────────────────────────────┐
│                   Service Layer                             │
├──────────┬──────────┬──────────┬──────────┬────────────────┤
│   Trend  │ Product  │  Brand   │  Store   │     SEO        │
│Intelligence│Intel  │ Builder  │ Builder  │    Engine      │
├──────────┼──────────┼──────────┼──────────┼────────────────┤
│  Content │Analytics │Customer  │          │                │
│  Engine  │          │ Support  │          │                │
└──────────┴──────────┴──────────┴──────────┴────────────────┘
           │
┌──────────▼──────────────────────────────────────────────────┐
│                   Agent Layer                                │
├──────────┬──────────┬──────────┬──────────┬────────────────┤
│   Trend  │ Product  │  Brand   │  Store   │     SEO        │
│  Analyst │Evaluator │ Creator  │Generator │   Optimizer    │
├──────────┼──────────┼──────────┼──────────┼────────────────┤
│  Content │ Support  │          │          │                │
│  Writer  │Assistant │          │          │                │
└──────────┴──────────┴──────────┴──────────┴────────────────┘
           │
┌──────────▼──────────────────────────────────────────────────┐
│                   Data Layer                                 │
├──────────┬──────────┬──────────┬──────────┬────────────────┤
│PostgreSQL│  Redis   │   File   │  External│                │
│ Primary  │  Cache   │  Storage │   APIs   │                │
└──────────┴──────────┴──────────┴──────────┴────────────────┘
           │
┌──────────▼──────────────────────────────────────────────────┐
│                AI Provider Layer                             │
├──────────┬──────────┬───────────────────────────────────────┤
│  OpenAI  │Anthropic │         Custom Providers              │
└──────────┴──────────┴───────────────────────────────────────┘
```

## Architecture Principles

### 1. Modularity
Each service and agent is designed as an independent module with clear interfaces. This allows for:
- Independent development and testing
- Easy replacement or upgrades
- Scalable deployment options

### 2. Provider Abstraction
The AI provider layer abstracts the specific AI service implementation, enabling:
- Easy switching between AI providers
- Cost optimization through provider selection
- Redundancy and failover capabilities

### 3. Data-Driven Design
All decisions and automation are based on structured data:
- Quantitative metrics for product evaluation
- Structured trend analysis
- Measurable SEO and content performance

### 4. Configurability
Every aspect of the system is configurable:
- Service parameters
- Agent schedules and triggers
- AI model selection and parameters
- Integration settings

### 5. Scalability
The architecture supports horizontal scaling:
- Stateless API design
- Distributed caching with Redis
- Asynchronous job processing
- Database indexing and optimization

## Component Architecture

### Applications Layer

#### Web Storefront (`apps/web`)
- **Purpose**: Customer-facing e-commerce store
- **Technology**: Next.js 14, React, TypeScript, Tailwind CSS
- **Features**: Product catalog, shopping cart, checkout, blog, FAQ, contact
- **Key Components**:
  - Page components (home, product, blog, etc.)
  - Shopping cart and checkout flow
  - SEO-optimized routing
  - Responsive design

#### Admin Dashboard (`apps/admin`)
- **Purpose**: Administrative interface for store management
- **Technology**: Next.js 14, React, TypeScript, Tailwind CSS
- **Features**: Product management, analytics, agent monitoring, configuration
- **Key Components**:
  - Dashboard with key metrics
  - Product and content management
  - Agent execution monitoring
  - Service configuration

#### API Backend (`apps/api`)
- **Purpose**: RESTful API and business logic
- **Technology**: FastAPI, Python, SQLAlchemy
- **Features**: Authentication, data processing, AI orchestration
- **Key Components**:
  - RESTful endpoints
  - Authentication middleware
  - Request validation
  - Response formatting

### Packages Layer

#### Types (`packages/types`)
- **Purpose**: Shared TypeScript type definitions
- **Content**: Domain models, API types, configuration types
- **Usage**: Ensures type consistency across applications

#### Database (`packages/database`)
- **Purpose**: Database schema and utilities
- **Technology**: Drizzle ORM (TypeScript), SQLAlchemy (Python)
- **Content**: Table definitions, migrations, connection management

#### Shared (`packages/shared`)
- **Purpose**: Shared utilities and helpers
- **Content**: Validation functions, formatters, constants
- **Usage**: Common functionality across applications

#### UI (`packages/ui`)
- **Purpose**: Shared React components
- **Content**: Reusable UI components, design system
- **Usage**: Consistent UI across web and admin applications

## Data Architecture

### Database Schema

The PostgreSQL database is designed with the following key tables:

#### Core Entities
- **users**: User accounts and authentication
- **stores**: E-commerce store configurations
- **products**: Product catalog with metadata
- **brands**: Brand identity and voice

#### Content & SEO
- **content**: Blog posts, pages, product descriptions
- **trends**: Market trend data and analysis

#### Analytics
- **analytics**: Performance metrics and reports

#### Automation
- **agents**: Agent configurations and schedules
- **agent_executions**: Agent execution history

#### Configuration
- **service_configs**: Service-specific configurations

### Data Flow

1. **Ingestion**: External APIs and user input populate the database
2. **Processing**: Agents read data, apply AI models, write results
3. **Storage**: Processed data is stored with proper indexing
4. **Retrieval**: API endpoints query data for frontend consumption
5. **Caching**: Frequently accessed data is cached in Redis

### Caching Strategy

- **Session Data**: User sessions and authentication tokens
- **Query Results**: Frequently accessed database queries
- **API Responses**: External API responses with TTL
- **Computed Metrics**: Pre-calculated analytics data

## Service Architecture

Each service is designed as an independent module with:

### Service Interface
```typescript
interface Service {
  name: string;
  version: string;
  config: ServiceConfig;
  initialize(): Promise<void>;
  execute(input: any): Promise<any>;
  healthCheck(): Promise<boolean>;
}
```

### Service Categories

#### Analysis Services
- **Trend Intelligence**: Market trend detection and analysis
- **Product Intelligence**: Product evaluation and scoring

#### Generation Services
- **Brand Builder**: Brand identity creation
- **Store Builder**: Store page generation
- **Content Engine**: Content creation and optimization
- **SEO Engine**: SEO metadata and optimization

#### Operational Services
- **Analytics**: Data aggregation and reporting
- **Customer Support**: AI-powered customer assistance

### Service Communication

Services communicate through:
- **Direct Function Calls**: For synchronous operations
- **Message Queues**: For asynchronous operations (via Redis)
- **Database**: For shared state and persistence

## Agent Architecture

Agents are autonomous workers that execute specific tasks on schedules or triggers.

### Agent Lifecycle

1. **Initialization**: Load configuration and connect to services
2. **Execution**: Process input using AI models and business logic
3. **Output Generation**: Write results to database or external systems
4. **Error Handling**: Log errors and implement retry logic
5. **Cleanup**: Release resources and update status

### Agent Types

#### Trend Analyst
- **Schedule**: Hourly/Daily
- **Input**: External trend sources
- **Output**: Trend database records
- **AI Model**: Trend analysis and categorization

#### Product Evaluator
- **Schedule**: On product creation/update
- **Input**: Product data
- **Output**: Product metadata with scores
- **AI Model**: Product evaluation criteria

#### Brand Creator
- **Schedule**: Manual trigger
- **Input**: Store preferences and market data
- **Output**: Brand identity configuration
- **AI Model**: Creative generation

#### Store Generator
- **Schedule**: Manual trigger
- **Input**: Brand identity and product catalog
- **Output**: Store pages and content
- **AI Model**: Content generation

#### SEO Optimizer
- **Schedule**: Daily/Weekly
- **Input**: Content and performance data
- **Output**: SEO recommendations and optimizations
- **AI Model**: SEO analysis

#### Content Writer
- **Schedule**: Configurable intervals
- **Input**: Topics and brand voice
- **Output**: Blog posts and descriptions
- **AI Model**: Content generation

#### Support Assistant
- **Schedule**: Real-time
- **Input**: Customer queries
- **Output**: Response suggestions
- **AI Model**: Question answering

#### Conversion Optimization Engine (Phase 8)
- **Location**: `agents/conversion_engine/` - a standalone, framework-agnostic
  Python package (no database or AI provider dependency)
- **Schedule**: On-demand, triggered via `POST /api/v1/stores/{store_id}/optimize`
- **Input**: A Store Builder blueprint (`blueprint_json`)
- **Output**: An optimized blueprint + a `ConversionReport` (conversion, SEO,
  UX, trust and persuasion scores, strengths/weaknesses, recommended actions)
- **Sub-optimizers**: `HeroOptimizer`, `TrustOptimizer`,
  `ProductPageOptimizer`, `PricingOptimizer` (recommendations only, never
  mutates real prices), `ReviewOptimizer` (never fabricates reviews outside
  of demo mode), `UXOptimizer` and `SEOOptimizer` (both analysis-only)
- **AI Model**: None - fully rule-based and deterministic, consistent with
  the rest of the platform's "works with zero external API" design

### Agent Execution Model

```python
class AgentExecution:
    id: str
    agent_id: str
    status: 'pending' | 'running' | 'completed' | 'failed'
    input: Dict[str, Any]
    output: Optional[Dict[str, Any]]
    error: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]
    duration: Optional[int]
```

## AI Integration

### Provider Abstraction

The AI provider layer abstracts different AI services behind a common interface:

```python
class AIProvider(ABC):
    async def generate(
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        pass
    
    def get_usage() -> Dict[str, int]:
        pass
```

### Supported Providers

#### OpenAI
- **Models**: GPT-4, GPT-3.5-turbo
- **Use Cases**: Content generation, analysis, coding
- **Strengths**: Versatile, well-documented

#### Anthropic
- **Models**: Claude 3 Opus, Sonnet, Haiku
- **Use Cases**: Long-form content, complex reasoning
- **Strengths**: Large context window, safety features

#### Custom Providers
- **Extensibility**: Custom models can be integrated
- **Use Cases**: Specialized models, cost optimization
- **Implementation**: Implement AIProvider interface

### AI Usage Tracking

All AI usage is tracked for:
- Cost monitoring and optimization
- Performance analysis
- Rate limiting and quota management
- Provider selection decisions

## Security Architecture

### Authentication & Authorization

- **JWT Tokens**: Stateless authentication
- **Role-Based Access Control**: Admin, user, moderator roles
- **API Key Authentication**: For service-to-service communication

### Data Protection

- **Encryption at Rest**: Database encryption
- **Encryption in Transit**: TLS/SSL for all communications
- **Secrets Management**: Environment variables for sensitive data
- **Input Validation**: Strict validation on all inputs

### API Security

- **Rate Limiting**: Per-IP and per-user limits
- **CORS Configuration**: Controlled cross-origin access
- **Request Validation**: Pydantic models for validation
- **SQL Injection Prevention**: Parameterized queries

## Scalability Strategy

### Horizontal Scaling

- **API Servers**: Multiple instances behind load balancer
- **Worker Processes**: Separate worker processes for agents
- **Database**: Read replicas for query scaling
- **Cache**: Redis cluster for distributed caching

### Vertical Scaling

- **Database Optimization**: Indexing, query optimization
- **Connection Pooling**: Efficient database connections
- **Memory Management**: Redis memory optimization
- **Resource Limits**: Container resource constraints

### Performance Optimization

- **Database Indexing**: Strategic indexes on frequently queried columns
- **Query Optimization**: Efficient queries with proper joins
- **Caching Layers**: Multiple caching levels (memory, Redis, CDN)
- **Lazy Loading**: Load data only when needed
- **Pagination**: Large result sets are paginated

## Technology Choices

### Frontend: Next.js
- **Reason**: Modern React framework with excellent SEO
- **Benefits**: Server-side rendering, API routes, file-based routing
- **Alternatives Considered**: Nuxt.js, SvelteKit

### Backend: FastAPI
- **Reason**: Modern, fast Python framework
- **Benefits**: Automatic documentation, type hints, async support
- **Alternatives Considered**: Django, Flask, Express.js

### Database: PostgreSQL
- **Reason**: Robust relational database with advanced features
- **Benefits**: JSON support, full-text search, ACID compliance
- **Alternatives Considered**: MySQL, MongoDB

### Cache: Redis
- **Reason**: Fast in-memory data store
- **Benefits**: Versatile data structures, pub/sub, persistence
- **Alternatives Considered**: Memcached

### ORM: Drizzle & SQLAlchemy
- **Reason**: Type-safe database access
- **Benefits**: Schema validation, migration support, query building
- **Alternatives Considered**: Prisma, TypeORM

### Build System: Turbo
- **Reason**: Monorepo-optimized build system
- **Benefits**: Incremental builds, caching, parallel execution
- **Alternatives Considered**: Nx, Lerna

### Containerization: Docker
- **Reason**: Consistent deployment environments
- **Benefits**: Reproducibility, isolation, easy scaling
- **Alternatives Considered**: Podman, Kubernetes

## Trend Intelligence Engine

### Overview

The Trend Intelligence Engine is the first fully implemented service in AI Commerce OS. It provides a production-ready system for discovering, analyzing, and scoring market trends from multiple data sources.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Trend Intelligence Engine                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐      ┌──────────────┐                    │
│  │    API       │─────▶│   Service    │                    │
│  │   Layer      │      │    Layer     │                    │
│  └──────────────┘      └──────┬───────┘                    │
│                               │                             │
│          ┌────────────────────┼────────────────────┐       │
│          ▼                    ▼                    ▼       │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐│
│  │  Providers   │    │   Scoring    │    │   Cache      ││
│  │              │    │   Engine     │    │   (Redis)    ││
│  │ • Mock       │    │              │    │              ││
│  │ • Google     │    │ • Popularity │    │ • Trends     ││
│  │ • Social     │    │ • Growth     │    │ • Analytics  ││
│  │ • Ecommerce  │    │ • Competition│    │ • Collections││
│  └──────────────┘    │ • Opportunity│    └──────────────┘│
│                      │ • Confidence │                    │
│                      └──────┬───────┘                    │
│                             │                             │
│                      ┌──────▼───────┐                    │
│                      │  Repository  │                    │
│                      │   (SQLAlchemy)│                   │
│                      └──────┬───────┘                    │
│                             │                             │
│                      ┌──────▼───────┐                    │
│                      │   Database   │                    │
│                      │ (PostgreSQL) │                    │
│                      └──────────────┘                    │
│                                                              │
│  ┌──────────────┐      ┌──────────────┐                    │
│  │ Background   │      │  Task Queue  │                    │
│  │   Tasks      │─────▶│   (Redis)    │                    │
│  └──────────────┘      └──────────────┘                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

#### Provider System

The provider system implements an abstract base class (`BaseProvider`) that all data sources must implement:

- **collect()**: Fetch raw data from the source
- **normalize()**: Convert raw data to unified `TrendItem` format
- **validate()**: Validate normalized data quality

This architecture allows easy addition of new data sources without modifying core logic.

#### Scoring Engine

The scoring engine provides a flexible, extensible system for calculating trend scores:

- **Modular Scorers**: Individual scorer classes for each metric (popularity, growth, competition, etc.)
- **Configurable Weights**: Adjustable weight system for score calculation
- **Extensible**: Easy to add new scoring criteria
- **Batch Processing**: Efficient scoring of multiple trends

#### Data Models

Unified data models ensure consistency across the system:

- **TrendItem**: Standardized trend data format
- **Trend**: Database model with all scores and metadata
- **TrendCollection**: Collection job tracking
- **TrendScoreHistory**: Historical score tracking

#### Caching Layer

Redis-based caching provides:

- **Trend Caching**: Individual trend data
- **List Caching**: Paginated trend lists
- **Analytics Caching**: Computed analytics
- **Collection Caching**: Collection results
- **Invalidation**: Smart cache invalidation strategies

#### Background Tasks

Async task system for:

- **Data Collection**: Non-blocking trend collection
- **Score Recalculation**: Batch score updates
- **Task Queue**: Redis-based task queue
- **Status Tracking**: Real-time job status

### API Endpoints

The engine provides comprehensive REST API endpoints:

- **Trend CRUD**: Create, read, update, delete trends
- **Collection**: Start and monitor collection jobs
- **Scoring**: Trigger score recalculation
- **Analytics**: Get trend analytics
- **Providers**: List available providers
- **Cache Management**: Cache statistics and control

### Database Schema

Optimized database schema with:

- **Trends Table**: Main trend data with all scores
- **Trend Collections Table**: Collection job tracking
- **Trend Score History Table**: Historical score data
- **Indexes**: Strategic indexes for common queries
- **JSON Columns**: Flexible metadata storage

### Testing

Comprehensive test coverage:

- **Unit Tests**: Provider, scoring, cache components
- **Integration Tests**: End-to-end workflows
- **Mock Data**: Mock provider for testing
- **Test Isolation**: In-memory database for tests

### Configuration

Environment-based configuration:

- **Provider Settings**: Default provider, timeouts, limits
- **Scoring Weights**: Configurable score weights
- **Cache Settings**: TTL values for different data types
- **Cleanup Settings**: Automatic cleanup configuration

---

## Product Intelligence Engine

### Overview

The Product Intelligence Engine is the second fully implemented service in AI Commerce OS. It provides a comprehensive system for evaluating the commercial potential of products identified by the Trend Intelligence Engine. The system uses a modular rule-based approach to analyze products across multiple dimensions.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Product Intelligence Engine                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐      ┌──────────────┐                    │
│  │    API       │─────▶│   Service    │                    │
│  │   Layer      │      │    Layer     │                    │
│  └──────────────┘      └──────┬───────┘                    │
│                               │                             │
│          ┌────────────────────┼────────────────────┐       │
│          ▼                    ▼                    ▼       │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐│
│  │  Rule Engine │    │ Score Engine │    │   Cache      ││
│  │              │    │              │    │   (Redis)    ││
│  │ • Margin     │    │ • Weights    │    │              ││
│  │ • Demand     │    │ • Overall    │    │ • Reports   ││
│  │ • Competition│    │ • Analysis   │    │ • Analytics  ││
│  │ • 11 Rules   │    │ • Recommend. │    │              ││
│  └──────────────┘    └──────┬───────┘    └──────────────┘│
│                              │                             │
│                      ┌──────▼───────┐                    │
│                      │  Repository  │                    │
│                      │   (SQLAlchemy)│                   │
│                      └──────┬───────┘                    │
│                             │                             │
│                      ┌──────▼───────┐                    │
│                      │   Database   │                    │
│                      │ (PostgreSQL) │                    │
│                      └──────────────┘                    │
│                                                              │
│  ┌──────────────┐      ┌──────────────┐                    │
│  │ Background   │─────▶  Trend       │                    │
│  │   Tasks      │      │ Intelligence │                    │
│  └──────────────┘      └──────────────┘                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

#### Rule Engine

The rule engine implements a modular evaluation system with 11 independent rules:

- **EstimatedMarginRule**: Evaluates profit margin potential
- **DemandRule**: Analyzes market demand
- **CompetitionRule**: Assesses competitive landscape
- **SeasonalityRule**: Evaluates seasonal demand patterns
- **ShippingRule**: Assesses shipping complexity and cost
- **ImpulseBuyRule**: Evaluates impulse purchase potential
- **ContentPotentialRule**: Assesses content marketing potential
- **SEORule**: Evaluates SEO opportunities
- **SupplierAvailabilityRule**: Assesses supplier availability
- **ReturnRiskRule**: Evaluates return risk
- **LegalRiskRule**: Evaluates legal and regulatory risks

Each rule is independent and can be added/removed without affecting the core system.

#### Score Engine

The score engine orchestrates rule evaluation and generates comprehensive reports:

- **Configurable Weights**: Adjustable weight system for each rule
- **Overall Score Calculation**: Weighted combination of rule scores
- **Recommendation System**: Generates buy/hold/avoid recommendations
- **Strengths/Weaknesses**: Identifies key factors
- **Detailed Reasoning**: Provides comprehensive analysis

#### Product Intelligence Report

Unified data model containing:

- **Individual Scores**: 11 rule-specific scores
- **Overall Assessment**: Overall score and confidence
- **Recommendation**: Actionable recommendation (strong_buy, buy, hold, avoid)
- **Reasoning**: Detailed explanation of the recommendation
- **Strengths/Weaknesses**: Key factors identified
- **Rule Results**: Detailed breakdown of each rule evaluation

#### Caching Layer

Redis-based caching for:

- **Report Caching**: Individual product reports
- **Top Products Caching**: Cached top products lists
- **Analytics Caching**: Computed analytics data
- **Smart Invalidation**: Cache invalidation on updates

#### Background Tasks

Async task system for:

- **Product Analysis**: Async analysis of individual products
- **Batch Analysis**: Batch processing of multiple products
- **Cache Management**: Automatic cache invalidation

### API Endpoints

The engine provides comprehensive REST API endpoints:

- **Analysis**: POST /api/v1/products/analyze, POST /api/v1/products/analyze/batch
- **Reports**: GET /api/v1/products/, GET /api/v1/products/{id}
- **Dashboard**: GET /api/v1/products/top, GET /api/v1/products/analytics
- **Configuration**: POST /api/v1/products/weights

### Database Schema

Optimized database schema with:

- **Product Intelligence Reports Table**: Main report data with all scores
- **Indexes**: Strategic indexes for filtering and sorting
- **JSON Columns**: Flexible storage for rule results and metadata

### Testing

Comprehensive test coverage:

- **Rule Tests**: Unit tests for all 11 rules
- **Score Engine Tests**: Score calculation and weight configuration
- **Integration Tests**: End-to-end workflow tests
- **Mock Data**: Mock trend data for testing

### Integration with Trend Intelligence

The Product Intelligence Engine integrates seamlessly with the Trend Intelligence Engine:

- **Data Source**: Uses trend data from Trend Intelligence Engine
- **Analysis Trigger**: Can be triggered automatically on new trends
- **Score Correlation**: Uses trend scores as input for product evaluation
- **Combined Analytics**: Provides combined trend and product insights

---

## Supplier Intelligence Engine

### Overview

The Supplier Intelligence Engine is the third fully implemented service in AI Commerce OS. It provides a comprehensive system for comparing and evaluating suppliers across multiple dimensions. The system features a modular provider interface designed for future integration with official APIs or data imports.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Supplier Intelligence Engine                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐      ┌──────────────┐                    │
│  │    API       │─────▶│   Service    │                    │
│  │   Layer      │      │    Layer     │                    │
│  └──────────────┘      └──────┬───────┘                    │
│                               │                             │
│          ┌────────────────────┼────────────────────┐       │
│          ▼                    ▼                    ▼       │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐│
│  │  Provider    │    │ Rule Engine  │    │   Cache      ││
│  │   Interface  │    │              │    │   (Redis)    ││
│  │              │    │ • Cost       │    │              ││
│  │ • Base       │    │ • Delivery   │    │ • Evaluations││
│  │ • Mock       │    │ • MOQ        │    │ • Best Offers││
│  │ • Future     │    │ • 7 Rules    │    │              ││
│  └──────────────┘    └──────┬───────┘    └──────────────┘│
│                              │                             │
│                      ┌──────▼───────┐                    │
│                      │ Score Engine │                    │
│                      │              │                    │
│                      │ • Weights    │                    │
│                      │ • Overall    │                    │
│                      │ • Recommend. │                    │
│                      └──────┬───────┘                    │
│                              │                             │
│                      ┌──────▼───────┐                    │
│                      │  Repository  │                    │
│                      │   (SQLAlchemy)│                   │
│                      └──────┬───────┘                    │
│                             │                             │
│                      ┌──────▼───────┐                    │
│                      │   Database   │                    │
│                      │ (PostgreSQL) │                    │
│                      └──────────────┘                    │
│                                                              │
│  ┌──────────────┐      ┌──────────────┐                    │
│  │ Background   │─────▶  Product     │                    │
│  │   Tasks      │      │ Intelligence │                    │
│  └──────────────┘      └──────────────┘                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

#### Provider Interface

The provider interface implements an abstract base class for supplier data sources:

- **BaseSupplierProvider**: Abstract class for all data providers
- **Standardized Data Models**: SupplierData and SupplierOfferData
- **Future Integration**: Designed for official API integrations (Alibaba, AliExpress, etc.)
- **No Scraping**: Architecture supports legitimate data imports only

**Current Implementation**:
- MockProvider for testing and development
- No scraping or circumvention of protections
- Ready for official API integration

#### Rule Engine

The rule engine implements 7 independent evaluation rules:

- **CostRule**: Evaluates cost competitiveness
- **DeliveryRule**: Assesses delivery speed and reliability
- **MOQRule**: Evaluates minimum order quantity requirements
- **AvailabilityRule**: Assesses inventory availability
- **ReliabilityRule**: Evaluates supplier reliability (based on metadata)
- **FlexibilityRule**: Assesses negotiation flexibility
- **DataQualityRule**: Evaluates data completeness and freshness

Each rule can be enabled/disabled via configuration.

#### Score Engine

The score engine orchestrates rule evaluation and generates comprehensive reports:

- **Configurable Weights**: Adjustable weight system for each rule
- **Overall Score Calculation**: Weighted combination of rule scores
- **Recommendation System**: Generates strong_recommend, recommend, consider, avoid
- **Strengths/Weaknesses**: Identifies key factors
- **Detailed Reasoning**: Provides comprehensive analysis

#### Database Models

Three main database models:

- **Supplier**: Supplier information (name, source, country, contact)
- **SupplierOffer**: Offer details (cost, MOQ, delivery times, availability)
- **SupplierEvaluation**: Evaluation results with all scores and recommendations

#### Caching Layer

Redis-based caching for:

- **Evaluation Caching**: Individual supplier evaluations
- **Best Offers Caching**: Cached best offers lists
- **Smart Invalidation**: Cache invalidation on updates

#### Background Tasks

Async task system for:

- **Catalog Import**: Import supplier offers from providers
- **Batch Evaluation**: Evaluate multiple suppliers asynchronously
- **Cache Management**: Automatic cache invalidation

### API Endpoints

The engine provides comprehensive REST API endpoints:

- **Supplier Management**: POST /api/v1/suppliers/
- **Offer Import**: POST /api/v1/suppliers/offers/import
- **Evaluation**: POST /api/v1/suppliers/evaluate
- **Comparison**: POST /api/v1/suppliers/compare
- **Best Offers**: GET /api/v1/suppliers/best
- **Configuration**: POST /api/v1/suppliers/weights

### Integration with Product Intelligence

The Supplier Intelligence Engine integrates with the Product Intelligence Engine:

- **Product Data**: Uses product data from Product Intelligence Engine
- **Offer Collection**: Collects offers for evaluated products
- **Comprehensive Analysis**: Combines product and supplier intelligence

### Future Provider Integration

The provider interface is designed for future integration with:

- **Official Platform APIs**: Alibaba, AliExpress, CJ Dropshipping, etc.
- **Data Imports**: CSV, XML, JSON imports
- **Custom Integrations**: Bespoke supplier systems
- **No Scraping**: Architecture supports legitimate data sources only

---

## Brand Builder

### Overview

The Brand Builder is the fourth fully implemented service in AI Commerce OS and marks a significant architectural milestone: it's the first module that integrates data from the previous three intelligence engines (Trend, Product, Supplier) to generate usable brand identity. This represents the transition from isolated modules to integrated functionality.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Brand Builder                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐      ┌──────────────┐                    │
│  │    API       │─────▶│   Service    │                    │
│  │   Layer      │      │    Layer     │                    │
│  └──────────────┘      └──────┬───────┘                    │
│                               │                             │
│          ┌────────────────────┼────────────────────┐       │
│          ▼                    ▼                    ▼       │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐│
│  │   Engines    │    │  Templates   │    │   Cache      ││
│  │              │    │              │    │   (Redis)    ││
│  │ • Name       │    │ • Name       │    │              ││
│  │ • Audience   │    │ • Audience   │    │ • Brands     ││
│  │ • Identity   │    │ • Identity   │    │              ││
│  │ • Visual     │    │ • Colors     │    │              ││
│  │ • Messaging  │    │ • Typography │    │              ││
│  │ • Positioning │    │ • Tone       │    │              ││
│  │ • Validator  │    │ • Positioning │    │              ││
│  └──────┬───────┘    └──────────────┘    └──────────────┘│
│         │                                                │
│         └────────────────────┬───────────────────────┘│
│                              │                         │
│                      ┌──────▼───────┐                │
│                      │ AI Provider  │                │
│                      │   (OpenAI/   │                │
│                      │  Anthropic)  │                │
│                      └──────┬───────┘                │
│                             │                         │
│         ┌───────────────────┼───────────────────┐    │
│         ▼                   ▼                   ▼    │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐│
│  │  Trend       │   │  Product     │   │  Supplier    ││
│  │ Intelligence │   │ Intelligence │   │ Intelligence ││
│  └──────────────┘   └──────────────┘   └──────────────┘│
│                                                              │
│                      ┌──────▼───────┐                    │
│                      │  Repository  │                    │
│                      │   (SQLAlchemy)│                   │
│                      └──────┬───────┘                    │
│                             │                             │
│                      ┌──────▼───────┐                    │
│                      │   Database   │                    │
│                      │ (PostgreSQL) │                    │
│                      └──────────────┘                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

#### Prompt Template System

Versioned, configurable prompt templates externalized in the `prompts/` directory:

- **Name Template**: Brand name generation
- **Audience Template**: Customer persona creation
- **Identity Template**: Mission and vision generation
- **Colors Template**: Color palette generation
- **Typography Template**: Font recommendations
- **Tone Template**: Tone of voice definition
- **Value Proposition Template**: UVP generation

Each template is:
- Versioned for tracking changes
- Configurable with temperature and max_tokens
- Independent and easily replaceable
- Designed for AI provider abstraction

#### Modular Brand Engines

Six independent engines generating brand components:

- **NameEngine**: Generates brand names
- **AudienceEngine**: Creates customer personas
- **IdentityEngine**: Generates mission, vision, values
- **VisualEngine**: Creates color palette, typography, design prompts
- **MessagingEngine**: Defines tone of voice and communication style
- **PositioningEngine**: Generates value proposition and differentiators

Each engine:
- Works independently or combined
- Uses AIProvider abstraction (OpenAI/Anthropic)
- Has fallback mock generation for testing
- Returns structured EngineResult

#### Brand Validator

Validates generated brand identity for:

- **Coherence**: Internal consistency of brand elements
- **Readability**: Clarity and memorability
- **Uniqueness**: Differentiation from competitors
- **Marketing Coherence**: Alignment with target audience
- **SEO Coherence**: Search engine friendliness

Returns:
- Overall validation score
- Identified strengths and weaknesses
- Improvement suggestions

#### Integration with Intelligence Engines

Brand Builder integrates with previous engines:

- **Product Intelligence**: Uses product data (name, category, audience, UVP)
- **Supplier Intelligence**: Uses supplier data (reliability, location)
- **Trend Intelligence**: Uses trend data (vibe, market positioning)

This creates the first end-to-end integration in the platform.

### API Endpoints

- `POST /api/v1/brands/generate` - Generate complete brand profile
- `GET /api/v1/brands/{id}` - Get specific brand
- `GET /api/v1/brands/` - List all brands
- `POST /api/v1/brands/{id}/validate` - Validate brand
- `GET /api/v1/brands/{id}/export` - Export brand as JSON

### JSON Export

Complete brand export including:
- Full brand profile
- Source intelligence data
- Export timestamp
- Ready for use by future modules (Store Builder, Content Engine)

---

## Store Builder

### Overview

The Store Builder is the fifth fully implemented service in AI Commerce OS and represents the most significant milestone to date: it's the first module that transforms the data produced by all previous intelligence engines into a concrete, usable result—a complete e-commerce store. This phase realizes the platform's core value proposition by creating an end-to-end flow from trend discovery to store generation.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Store Builder                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐      ┌──────────────┐                    │
│  │    API       │─────▶│   Service    │                    │
│  │   Layer      │      │    Layer     │                    │
│  └──────────────┘      └──────┬───────┘                    │
│                               │                             │
│          ┌────────────────────┼────────────────────┐       │
│          ▼                    ▼                    ▼       │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐│
│  │   Engines    │    │  Templates   │    │   Cache      ││
│  │              │    │              │    │   (Redis)    ││
│  │ • Homepage   │    │ • Homepage   │    │              ││
│  │ • Navigation │    │ • Product    │    │ • Stores     ││
│  │ • Theme      │    │ • About      │    │              ││
│  │ • SEO        │    │ • Contact    │    │              ││
│  │ • Policy     │    │              │    │              ││
│  │ • Validator  │    │              │    │              ││
│  └──────┬───────┘    └──────────────┘    └──────────────┘│
│         │                                                │
│         └────────────────────┬───────────────────────┘│
│                              │                         │
│         ┌────────────────────┼───────────────────────┤│
│         ▼                    ▼                        ▼│
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐│
│  │  Brand       │   │  Product     │   │  Supplier    ││
│  │  Builder     │   │ Intelligence │   │ Intelligence ││
│  └──────────────┘   └──────────────┘   └──────────────┘│
│                                                              │
│                      ┌──────▼───────┐                    │
│                      │  Repository  │                    │
│                      │   (SQLAlchemy)│                   │
│                      └──────┬───────┘                    │
│                             │                             │
│                      ┌──────▼───────┐                    │
│                      │   Database   │                    │
│                      │ (PostgreSQL) │                    │
│                      └──────────────┘                    │
│                                                              │
│  ┌──────────────┐      ┌──────────────┐                    │
│  │   Export     │─────▶  Platform    │                    │
│  │   System     │      │  Agnostic   │                    │
│  │              │      │  JSON        │                    │
│  └──────────────┘      └──────────────┘                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

#### Store Blueprint Model

Complete store configuration model containing:

- **Source Data**: Brand profile ID, product ID, supplier ID
- **Store Identity**: Store name, description, tagline
- **Pages**: Homepage, navigation, footer, product pages, landing pages
- **Content**: Collections, FAQ, policies, about, contact
- **Trust Elements**: Testimonials, reviews, trust badges
- **Visual Elements**: Hero sections, banners
- **Configuration**: Theme, SEO, social, emails
- **Export Configuration**: Platform-agnostic export settings

#### Template System

Versioned templates for store pages externalized in templates/ directory:

- **Homepage Template**: Hero, features, testimonials, trust badges
- **Product Page Template**: Product hero, features, specs, reviews, FAQ
- **About Page Template**: Brand story, mission, vision, values, team
- **Contact Page Template**: Contact info, form, hours, social links

Each template is:
- Versioned for tracking changes
- Configurable with placeholder substitution
- Independent and easily replaceable
- Designed for flexibility

#### Modular Store Engines

Five independent engines generating store components:

- **HomepageEngine**: Generates homepage sections (hero, features, testimonials, trust)
- **NavigationEngine**: Generates navigation structure and footer
- **ThemeEngine**: Generates complete theme configuration (colors, typography, spacing)
- **SEOEngine**: Generates SEO configuration (titles, meta descriptions, keywords)
- **PolicyEngine**: Generates store policies (refund, shipping, privacy, terms)

Each engine:
- Works independently or combined
- Uses brand profile and intelligence data
- Returns structured EngineResult
- Has AI provider integration support

#### Store Validator

Validates generated store for:

- **Coherence**: Internal consistency of store elements
- **SEO**: Search engine optimization configuration
- **UX**: User experience design
- **Accessibility**: Accessibility considerations (dark mode, fonts)
- **Responsive**: Responsive design considerations
- **Performance**: Performance optimization (animations)

Returns:
- Overall validation score
- Individual criterion scores
- Strengths, weaknesses, and suggestions

#### Platform-Agnostic Export

Export system designed for future platform integrations:

- **JSON Format**: Complete store blueprint as documented JSON
- **Platform Independent**: Not tied to Shopify, WooCommerce, or Next.js
- **Extensible**: Ready for future platform-specific exporters
- **Well-Documented**: Clear structure for frontend implementation

### Integration with Previous Engines

Store Builder integrates with all previous intelligence engines:

- **Brand Builder**: Uses brand profile (colors, typography, tone, differentiators)
- **Product Intelligence**: Uses product data (name, category, audience, vibe)
- **Supplier Intelligence**: Uses supplier data (reliability, location)
- **Trend Intelligence**: Uses trend data (market positioning)

This creates the complete end-to-end flow:
**Trend → Product → Supplier → Brand → Store**

### API Endpoints

- `POST /api/v1/stores/generate` - Generate complete store blueprint
- `GET /api/v1/stores/` - List all stores with pagination
- `GET /api/v1/stores/{id}` - Get specific store blueprint
- `POST /api/v1/stores/{id}/validate` - Validate store blueprint
- `GET /api/v1/stores/{id}/export` - Export store as platform-agnostic JSON
- `DELETE /api/v1/stores/{id}` - Delete store blueprint

### Export System

Platform-agnostic JSON export including:
- Complete store configuration
- Theme and styling
- Navigation and footer
- Homepage sections
- SEO configuration
- Policies
- Source intelligence data
- Export timestamp

---

## Sprint 4: Visual Identity, CTA, FAQ & Diversity

### New Engines

| Engine | Location | Responsibility |
| --- | --- | --- |
| Visual Identity Engine | `agents/visual_identity/engines.py` | Produces Brand Asset Pack (logo SVG, favicon, palette, typography, image prompts) |
| CTA Engine | `agents/cta_engine/engines.py` | Generates category/product/tone contextual CTA variants |
| FAQ Engine | `agents/faq_engine/engines.py` | Generates category-specific FAQs with policy integration |
| Diversity Analyzer | `agents/diversity_analyzer/engines.py` | Computes CTA, FAQ, title, description, visual-prompt diversity |

### Integration

- `app/launch/services/launch_service.py` step 6: **Content & Identity**
  1. Detects category from launch request.
  2. Runs `VisualIdentityEngine`, `CTAEngine`, `FAQEngine`.
  3. Persists `brand_asset_pack`, `cta_variants`, and `faq` into `blueprint_json`.

### Dashboard

- `apps/admin/app/quality/page.tsx` fetches `GET /api/v1/validation/report`.
- Displays Overall, CTA, FAQ, Brand, Description and Visual Prompt diversity.

---

## Sprint 4.5: Diversity Refinement

### Objectif
Atteindre > 90 % d'Overall Diversity en corrigant les templates fixes du Brand Builder et en diversifiant les prompts image.

### Améliorations

- **Brand Builder** (`app/brand_builder/engines/identity_engine.py`)
  - 5 familles de templates `mission` par catégorie.
  - Sélection par `md5(brand + product + audience + personality)`.
  - `personality` déduite du `vibe`.

- **Visual Identity Engine** (`agents/visual_identity/engines.py`)
  - `PROMPT_BANKS` avec 3 structures différentes par type d'image.
  - `STYLE_BANKS`, `LIGHTING_BANKS`, `COMPOSITION_BANKS`, `BACKGROUND_BANKS`, `ANGLE_BANKS` par catégorie.

- **Diversity Analyzer** (`agents/diversity_analyzer/engines.py`)
  - Métriques séparées : Brand, Prompt, Content, CTA, FAQ, Overall.
  - Statistiques : Average Similarity, Best Case, Worst Case, Distribution.

- **Validation Suite** (`validation/run_validation_50.py`)
  - Génération jusqu'à 50 boutiques (paramétrable avec `VALIDATION_LIMIT`).

- **Dashboard AI Quality Report** (`apps/admin/app/quality/page.tsx`)
  - 5 dimensions de diversité, histogramme de distribution, best/worst/similarity.

---

**Document Version**: 1.7  
**Last Updated**: 2026-08-02  
**Maintained By**: Architecture Team
