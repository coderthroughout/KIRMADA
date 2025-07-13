"""
Database configuration and connection management
"""

import logging
from typing import AsyncGenerator
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings

logger = logging.getLogger(__name__)

# Create declarative base
Base = declarative_base()

# Database engines
engine = None
async_engine = None
SessionLocal = None
AsyncSessionLocal = None


def init_db():
    """Initialize database connection"""
    global engine, async_engine, SessionLocal, AsyncSessionLocal
    
    try:
        if settings.DATABASE_URL.startswith("sqlite"):
            # SQLite configuration
            engine = create_engine(
                settings.DATABASE_URL,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=settings.DATABASE_ECHO
            )
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        else:
            # PostgreSQL/MySQL configuration
            engine = create_engine(
                settings.DATABASE_URL,
                echo=settings.DATABASE_ECHO,
                pool_pre_ping=True
            )
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


async def init_async_db():
    """Initialize async database connection"""
    global async_engine, AsyncSessionLocal
    
    try:
        if settings.DATABASE_URL.startswith("sqlite"):
            # SQLite async configuration
            async_engine = create_async_engine(
                settings.DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///"),
                connect_args={"check_same_thread": False},
                echo=settings.DATABASE_ECHO
            )
        else:
            # PostgreSQL/MySQL async configuration
            async_engine = create_async_engine(
                settings.DATABASE_URL,
                echo=settings.DATABASE_ECHO,
                pool_pre_ping=True
            )
        
        AsyncSessionLocal = async_sessionmaker(
            async_engine, class_=AsyncSession, expire_on_commit=False
        )
        
        # Create tables
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Async database initialized successfully")
        
    except Exception as e:
        logger.error(f"Async database initialization failed: {e}")
        raise


def init_db():
    """Initialize database connection"""
    global engine, SessionLocal
    
    try:
        if settings.DATABASE_URL.startswith("sqlite"):
            # SQLite configuration
            engine = create_engine(
                settings.DATABASE_URL,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=settings.DATABASE_ECHO
            )
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        else:
            # PostgreSQL/MySQL configuration
            engine = create_engine(
                settings.DATABASE_URL,
                echo=settings.DATABASE_ECHO,
                pool_pre_ping=True
            )
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


def close_db():
    """Close database connections"""
    global engine, async_engine
    
    if engine:
        engine.dispose()
        logger.info("Sync database connection closed")
    
    if async_engine:
        async_engine.dispose()
        logger.info("Async database connection closed")


def close_db():
    """Close database connections"""
    global engine
    
    if engine:
        engine.dispose()
        logger.info("Database connection closed")


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_async_db():
    """Get database session (sync version for now)"""
    return get_db() 