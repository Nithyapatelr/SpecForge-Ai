"""
Tests for RIT taxonomy seeding.

Verifies that:
1. The seed script inserts exactly the expected number of rows.
2. Running the seed script a second time does not change the row count or raise errors.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from specforge.classification.rit_taxonomy import RIT_CATEGORIES
from specforge.db.models import Base, RITTaxonomy


@pytest.fixture()
def temp_session(tmp_path):
    """
    Provide a temporary file-based SQLite session so seed_taxonomy can call
    init_db (which reads from the global engine) without interfering with other
    tests.  We monkey-patch specforge.db.session.engine for the duration.
    """
    import specforge.db.session as db_session_module
    import specforge.db.init_db as init_db_module

    db_path = tmp_path / "test_taxonomy.db"
    test_engine = create_engine(
        f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
    )

    # Patch the module-level engine used by init_db and get_session
    original_engine = db_session_module.engine
    original_session_local = db_session_module.SessionLocal

    db_session_module.engine = test_engine
    db_session_module.SessionLocal = sessionmaker(
        bind=test_engine, autocommit=False, autoflush=False, expire_on_commit=False
    )

    Base.metadata.create_all(bind=test_engine)

    yield test_engine

    # Restore
    db_session_module.engine = original_engine
    db_session_module.SessionLocal = original_session_local


def test_seed_inserts_expected_row_count(temp_session):
    """Seeding should create exactly len(RIT_CATEGORIES) rows."""
    from scripts.seed_taxonomy import seed_taxonomy

    seed_taxonomy()

    Session = sessionmaker(bind=temp_session)
    with Session() as session:
        count = session.query(RITTaxonomy).count()

    assert count == len(RIT_CATEGORIES), (
        f"Expected {len(RIT_CATEGORIES)} rows, got {count}"
    )


def test_seed_is_idempotent(temp_session):
    """Running seed twice must not change the row count or raise an exception."""
    from scripts.seed_taxonomy import seed_taxonomy

    seed_taxonomy()
    seed_taxonomy()  # second run — should be a no-op

    Session = sessionmaker(bind=temp_session)
    with Session() as session:
        count = session.query(RITTaxonomy).count()

    assert count == len(RIT_CATEGORIES), (
        f"Expected {len(RIT_CATEGORIES)} rows after second seed, got {count}"
    )


def test_seed_label_names_match_definition(temp_session):
    """Spot-check that inserted rows have the correct label_name values."""
    from scripts.seed_taxonomy import seed_taxonomy

    seed_taxonomy()

    expected_names = {cat["label_name"] for cat in RIT_CATEGORIES}

    Session = sessionmaker(bind=temp_session)
    with Session() as session:
        db_names = {row.label_name for row in session.query(RITTaxonomy).all()}

    assert expected_names == db_names
