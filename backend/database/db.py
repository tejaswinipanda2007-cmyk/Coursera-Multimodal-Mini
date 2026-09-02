"""
Database connection setup.

DATABASE_URL comes from .env. If not set, we default to a local SQLite file
(coursera_multimodal.db) so the project runs with zero database setup.

To upgrade to PostgreSQL/Supabase later (Week 6 deployment), just set
DATABASE_URL in .env to something like:
  postgresql://user:password@host:5432/dbname
No other code changes needed - that's the benefit of using SQLAlchemy.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from backend.database.models import Base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL") or "sqlite:///./coursera_multimodal.db"

# SQLite needs this extra flag to work with FastAPI's multi-threaded requests
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    """Create all tables if they don't exist yet. Safe to call every startup."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency: gives each request its own DB session, closes it after."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
