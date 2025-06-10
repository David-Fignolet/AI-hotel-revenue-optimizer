# src/data/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from ..utils.config import settings

# Create database engine
engine = create_engine(
    settings.database.url,
    echo=settings.database.echo,
    pool_pre_ping=True,
    pool_recycle=3600
)

# Create session factory
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database
def init_db():
    from . import models
    models.Base.metadata.create_all(bind=engine)