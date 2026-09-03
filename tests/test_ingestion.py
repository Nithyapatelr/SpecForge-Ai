"""
Tests for the ingestion module.
"""

import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from specforge.db.models import Base, Requirement


@pytest.fixture(autouse=True)
def patch_db(tmp_path, monkeypatch):
    """Redirect all DB operations to a temporary SQLite database."""
    import specforge.db.session as db_session_module

    db_path = tmp_path / "test_ingestion.db"
    test_engine = create_engine(
        f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=test_engine)

    monkeypatch.setattr(db_session_module, "engine", test_engine)
    monkeypatch.setattr(
        db_session_module,
        "SessionLocal",
        sessionmaker(
            bind=test_engine, autocommit=False, autoflush=False, expire_on_commit=False
        ),
    )
    return test_engine


def test_ingest_txt_file(patch_db, tmp_path):
    """Ingesting a .txt file should create a Requirement row with non-empty raw_text."""
    sample = tmp_path / "req.txt"
    sample.write_text("The system shall allow patients to book appointments.", encoding="utf-8")

    from specforge.ingestion.service import ingest_document

    req = ingest_document(file_path=str(sample), source_doc_id="doc-test-001")

    assert req.requirement_id is not None
    assert req.raw_text == "The system shall allow patients to book appointments."
    assert req.source_doc_id == "doc-test-001"
    assert req.atomic_unit_text is None


def test_ingest_raw_text(patch_db):
    """Ingesting raw text should create a Requirement row with that text."""
    from specforge.ingestion.service import ingest_document

    raw = "Only a Senior Doctor may approve Schedule II prescriptions."
    req = ingest_document(raw_text=raw, source_doc_id="doc-raw-001")

    assert req.raw_text == raw
    assert req.atomic_unit_text is None


def test_ingest_sample_01(patch_db):
    """Ingesting the bundled sample_01.txt should create a row with non-empty raw_text."""
    sample_path = os.path.join(
        os.path.dirname(__file__), "..", "data", "sample_requirements", "sample_01.txt"
    )

    from specforge.ingestion.service import ingest_document

    req = ingest_document(file_path=sample_path, source_doc_id="sample-01")

    assert req.raw_text  # non-empty
    assert len(req.raw_text) > 100  # sanity — file has many lines


def test_ingest_raises_on_empty_text(patch_db, tmp_path):
    """Ingesting a file with only whitespace should raise ValueError."""
    empty_file = tmp_path / "empty.txt"
    empty_file.write_text("   \n\n  ", encoding="utf-8")

    from specforge.ingestion.service import ingest_document

    with pytest.raises(ValueError, match="empty"):
        ingest_document(file_path=str(empty_file))


def test_ingest_raises_on_both_inputs(patch_db, tmp_path):
    """Providing both file_path and raw_text should raise ValueError."""
    f = tmp_path / "f.txt"
    f.write_text("text", encoding="utf-8")

    from specforge.ingestion.service import ingest_document

    with pytest.raises(ValueError, match="only one"):
        ingest_document(file_path=str(f), raw_text="also text")
