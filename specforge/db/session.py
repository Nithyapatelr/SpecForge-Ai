"""
SQLAlchemy engine and session factory.

Usage:
    from specforge.db.session import get_session

    with get_session() as session:
        session.add(some_model_instance)
        session.commit()
"""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from specforge.config import settings

# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

# connect_args is only relevant for SQLite — enables multi-threaded access
# from FastAPI's thread pool without "check_same_thread" errors.
_connect_args = (
    {"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {}
)

engine = create_engine(
    settings.database_url,
    connect_args=_connect_args,
    echo=False,  # Set to True for SQL query logging during debugging
)

# ---------------------------------------------------------------------------
# Session factory
# ---------------------------------------------------------------------------

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Yield a database session and close it automatically.

    Example::

        with get_session() as session:
            results = session.query(Requirement).all()
    """
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
