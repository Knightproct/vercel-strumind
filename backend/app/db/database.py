"""
Database configuration and session management
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# PostgreSQL engine (main database)
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.DEBUG
)

# SQLite engine (cache/local storage)
sqlite_engine = create_engine(
    settings.SQLITE_URL,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False},
    echo=settings.DEBUG
)

# Session factories
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SQLiteSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sqlite_engine)

# Base class for models
Base = declarative_base()

# Metadata for schema management
metadata = MetaData()

def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_sqlite_db() -> Session:
    """Get SQLite database session"""
    db = SQLiteSessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database"""
    try:
        Base.metadata.create_all(bind=engine)
        Base.metadata.create_all(bind=sqlite_engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
