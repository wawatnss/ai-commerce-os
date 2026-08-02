from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+psycopg2://ai_commerce:ai_commerce_password@localhost:5432/ai_commerce"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # AI Providers
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Application
    APP_NAME: str = "AI Commerce OS"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    API_PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    AUTOCREATE_TABLES: bool = False  # Use Alembic in production
    
    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Stripe
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    STRIPE_PRICE_ID_FREE: Optional[str] = None
    STRIPE_PRICE_ID_PRO: Optional[str] = None
    STRIPE_PRICE_ID_BUSINESS: Optional[str] = None
    
    # Email
    EMAIL_PROVIDER: str = "console"  # console, smtp, sendgrid, mailgun
    EMAIL_FROM: str = "noreply@ai-commerce.com"
    PUBLIC_ADMIN_URL: str = "http://localhost:3001"
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USE_TLS: bool = True
    EMAIL_API_KEY: str = ""
    EMAIL_DOMAIN: str = ""

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
