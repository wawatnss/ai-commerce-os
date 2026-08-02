"""Alembic environment configuration."""
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Add the apps/api path so that config.py and models can be imported.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import settings
from database import Base
from app.trend_intelligence.models.trend import Base as TrendBase
from app.product_intelligence.models.product import Base as ProductBase
from app.supplier_intelligence.models.supplier import Base as SupplierBase
from app.brand_builder.models.brand import Base as BrandBase
from app.store_builder.models.store import Base as StoreBase
from app.auth.base import Base as AuthBase
import app.billing.models  # noqa

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Set the SQLAlchemy URL from the application settings.
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Collect metadata from every declarative base so that autogenerate
# picks up all tables across vertical slices.
target_metadata = [
    Base.metadata,
    TrendBase.metadata,
    ProductBase.metadata,
    SupplierBase.metadata,
    BrandBase.metadata,
    StoreBase.metadata,
    AuthBase.metadata,
]


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
