import sys
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings

# Make the monorepo root importable so framework-agnostic sibling packages
# (e.g. `agents/conversion_engine`) can be imported from this FastAPI app.
# `database.py` is imported by virtually every module in `apps/api`, so this
# runs once, early, without needing a dedicated bootstrap import everywhere.
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_all_tables() -> None:
    """
    Create every table known to the application.

    Each vertical slice (trend_intelligence, product_intelligence,
    supplier_intelligence, brand_builder, store_builder, ...) declares its own
    SQLAlchemy declarative base instead of sharing a single one. To keep that
    modularity while still being able to bootstrap a fresh database (or an
    in-memory/demo database) with a single call, we explicitly create the
    tables for every one of those bases against the shared `engine`.
    """
    # NOTE: the legacy root-level `models.py` is intentionally NOT included
    # here. It predates the vertical-slice services below and some of its
    # tables (e.g. "trends") collide by name with theirs, which would leave
    # whichever one runs `create_all` first "winning" the actual DB schema.
    # It is kept in the repo for reference/history but is not wired into any
    # router, so it never needs its own tables at runtime.
    from app.trend_intelligence.models.trend import Base as TrendBase
    from app.product_intelligence.models.product import Base as ProductBase
    from app.supplier_intelligence.models.supplier import Base as SupplierBase
    from app.brand_builder.models.brand import Base as BrandBase
    from app.store_builder.models.store import Base as StoreBase
    from app.auth.models import Base as AuthBase
    # Import billing models so they register on the auth base for the FK.
    import app.billing.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    TrendBase.metadata.create_all(bind=engine)
    ProductBase.metadata.create_all(bind=engine)
    SupplierBase.metadata.create_all(bind=engine)
    BrandBase.metadata.create_all(bind=engine)
    StoreBase.metadata.create_all(bind=engine)
    AuthBase.metadata.create_all(bind=engine)
