"""Database connection and initialisation helpers."""

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.models import Base


ROOT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DATABASE_URL = f"sqlite:///{ROOT_DIR / 'production_planning.db'}"


def get_database_url() -> str:
    """Return the configured database URL or the local SQLite default."""
    return os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


def get_engine():
    """Create a SQLAlchemy engine for the configured database."""
    connect_args = {"check_same_thread": False} if get_database_url().startswith("sqlite") else {}
    return create_engine(get_database_url(), connect_args=connect_args)


def get_session_factory():
    """Create a session factory connected to the application database."""
    return sessionmaker(bind=get_engine(), expire_on_commit=False)


def init_database() -> None:
    """Create all tables if they do not already exist."""
    Base.metadata.create_all(get_engine())


def get_session() -> Session:
    """Return a new database session for one application operation."""
    return get_session_factory()()
