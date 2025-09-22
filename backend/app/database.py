"""Database configuration module.

This module sets up the SQLAlchemy connection and session management
for interacting with the database. It provides a dependency function
for FastAPI to inject database sessions into route handlers.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

# Create SQLAlchemy engine with connection pool
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Enables connection health checks
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()


def get_db():
    """Dependency for getting database session.
    
    This function creates a new SQLAlchemy session for each request and
    automatically closes it when the request is finished, even if there was an exception.
    
    Use this function with FastAPI's dependency injection system:
    ```
    @router.get("/")
    def endpoint(db: Session = Depends(get_db)):
        # use db session
    ```
    
    Yields:
        Session: SQLAlchemy Session object for database operations
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
