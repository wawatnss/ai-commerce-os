from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Numeric, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="user")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    stores = relationship("Store", back_populates="user")


class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    domain = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text)
    logo = Column(Text)
    theme = Column(JSON, nullable=False)
    settings = Column(JSON, nullable=False)
    status = Column(String(50), nullable=False, default="active")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="stores")
    products = relationship("Product", back_populates="store")
    brand = relationship("Brand", back_populates="store", uselist=False)
    content = relationship("Content", back_populates="store")
    analytics = relationship("Analytics", back_populates="store")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    sku = Column(String(100), nullable=False, index=True)
    price = Column(Numeric(10, 2), nullable=False)
    compare_at_price = Column(Numeric(10, 2))
    cost_price = Column(Numeric(10, 2))
    images = Column(JSON, nullable=False)
    variants = Column(JSON, nullable=False)
    categories = Column(JSON, nullable=False)
    tags = Column(JSON, nullable=False)
    # Note: "metadata" is reserved by SQLAlchemy's Declarative API for
    # Base.metadata. The column stays named "metadata"; `.metadata` is
    # re-exposed via a property assigned after the class body (see below).
    extra_metadata = Column("metadata", JSON, nullable=False)
    status = Column(String(50), nullable=False, default="draft", index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    store = relationship("Store", back_populates="products")


Product.metadata = property(lambda self: self.extra_metadata, lambda self, value: setattr(self, "extra_metadata", value))


class Trend(Base):
    __tablename__ = "trends"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String(255), nullable=False, index=True)
    source = Column(String(100), nullable=False, index=True)
    volume = Column(Integer, nullable=False)
    growth = Column(Numeric(5, 2), nullable=False)
    category = Column(String(100), index=True)
    related_keywords = Column(JSON, nullable=False)
    detected_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime)


class Brand(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    tagline = Column(String(500))
    description = Column(Text)
    identity = Column(JSON, nullable=False)
    voice = Column(JSON, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    store = relationship("Store", back_populates="brand")


class Content(Base):
    __tablename__ = "content"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False, index=True)
    type = Column(String(50), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    # Note: "metadata" is reserved by SQLAlchemy's Declarative API for
    # Base.metadata. The column stays named "metadata"; `.metadata` is
    # re-exposed via a property assigned after the class body (see below).
    extra_metadata = Column("metadata", JSON, nullable=False)
    status = Column(String(50), nullable=False, default="draft", index=True)
    published_at = Column(DateTime, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    store = relationship("Store", back_populates="content")


Content.metadata = property(lambda self: self.extra_metadata, lambda self, value: setattr(self, "extra_metadata", value))


class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False, index=True)
    period = Column(JSON, nullable=False, index=True)
    metrics = Column(JSON, nullable=False)
    top_products = Column(JSON, nullable=False)
    top_content = Column(JSON, nullable=False)
    traffic_sources = Column(JSON, nullable=False)
    conversions = Column(JSON, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    store = relationship("Store", back_populates="analytics")


class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(100), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="idle", index=True)
    config = Column(JSON, nullable=False)
    last_run = Column(DateTime)
    next_run = Column(DateTime)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    executions = relationship("AgentExecution", back_populates="agent")


class AgentExecution(Base):
    __tablename__ = "agent_executions"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="pending", index=True)
    input = Column(JSON, nullable=False)
    output = Column(JSON)
    error = Column(Text)
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime)
    duration = Column(Integer)

    agent = relationship("Agent", back_populates="executions")


class ServiceConfig(Base):
    __tablename__ = "service_configs"

    id = Column(Integer, primary_key=True, index=True)
    service = Column(String(100), unique=True, nullable=False, index=True)
    enabled = Column(Boolean, nullable=False, default=True)
    config = Column(JSON, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
