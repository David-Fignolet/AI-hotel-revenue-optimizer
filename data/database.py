# src/data/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import logging
from ..utils.config import settings

logger = logging.getLogger(__name__)

# Create database engine
DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=10,
    max_overflow=20,
    echo=settings.SQL_ECHO
)

# Create a scoped session factory
SessionLocal = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
)

# Base class for models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    """Get a database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize the database"""
    from . import models  # noqa: F401
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

def drop_db():
    """Drop all database tables (use with caution!)"""
    from . import models  # noqa: F401
    
    try:
        Base.metadata.drop_all(bind=engine)
        logger.warning("Dropped all database tables")
    except Exception as e:
        logger.error(f"Error dropping database: {str(e)}")
        raise