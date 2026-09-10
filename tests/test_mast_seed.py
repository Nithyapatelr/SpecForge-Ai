"""
Unit tests for MAST taxonomy seeding.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from scripts.seed_mast_taxonomy import seed_mast_taxonomy
from specforge.db.models import Base, MASTTaxonomy


@pytest.fixture()
def temp_session(tmp_path):
    """
    Provide a temporary file-based SQLite session so seed_mast_taxonomy can call
    init_db (which reads from global engine) without interfering with other tests.
    """
    import specforge.db.session as db_session_module

    db_path = tmp_path / "test_mast_taxonomy.db"
    test_engine = create_engine(
        f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
    )

    original_engine = db_session_module.engine
    original_session_local = db_session_module.SessionLocal

    db_session_module.engine = test_engine
    db_session_module.SessionLocal = sessionmaker(
        bind=test_engine, autocommit=False, autoflush=False, expire_on_commit=False
    )

    Base.metadata.create_all(bind=test_engine)

    yield test_engine

    db_session_module.engine = original_engine
    db_session_module.SessionLocal = original_session_local


def test_mast_taxonomy_seeding(temp_session):
    first_inserted = seed_mast_taxonomy()
    assert first_inserted == 14

    # Run second time for idempotency check
    second_inserted = seed_mast_taxonomy()
    assert second_inserted == 0

    Session = sessionmaker(bind=temp_session)
    with Session() as session:
        all_rows = session.query(MASTTaxonomy).all()
        assert len(all_rows) == 14

        spec_issues = [r for r in all_rows if r.category == "Specification Issues"]
        misalignment = [r for r in all_rows if r.category == "Inter-Agent Misalignment"]
        verification = [r for r in all_rows if r.category == "Task Verification"]

        assert len(spec_issues) == 5
        assert len(misalignment) == 6
        assert len(verification) == 3
