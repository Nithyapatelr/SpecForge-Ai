"""
Database initialisation script.

Creates all tables defined in specforge.db.models if they don't already exist.
Safe to run multiple times (CREATE TABLE IF NOT EXISTS semantics via SQLAlchemy).

Usage:
    python -m specforge.db.init_db
"""

import logging

from specforge.db.models import Base
from specforge.db.session import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db() -> None:
    """Create all tables.  Idempotent — existing tables are left unchanged."""
    logger.info("Creating database tables at: %s", engine.url)
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialisation complete.")


if __name__ == "__main__":
    init_db()
