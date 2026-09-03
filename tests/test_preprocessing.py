"""
Tests for preprocessing — atomic unit segmentation.

Three scenarios as required by the prompt:
1. Already-atomic single sentence → one unit out.
2. Compound sentence with two modal-verb clauses → two units out.
3. Multi-sentence paragraph → one unit per sentence (+ compound splitting).
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from specforge.db.models import Base, Requirement
from specforge.preprocessing.segmenter import segment_into_atomic_units


# ---------------------------------------------------------------------------
# Pure segmenter unit tests (no DB needed)
# ---------------------------------------------------------------------------


def test_already_atomic_sentence():
    """A single, simple sentence should come out as exactly one unit."""
    text = "The system shall allow patients to search for available appointments."
    units = segment_into_atomic_units(text)
    assert len(units) == 1
    assert "patients" in units[0]


def test_compound_sentence_splits_into_two():
    """
    'shall … and shall …' should produce two atomic units.
    """
    text = (
        "The system shall log the user in and shall send a confirmation email."
    )
    units = segment_into_atomic_units(text)
    assert len(units) == 2, f"Expected 2 units, got {len(units)}: {units}"
    assert any("log" in u.lower() for u in units)
    assert any("confirmation" in u.lower() or "email" in u.lower() for u in units)


def test_multi_sentence_paragraph():
    """
    A multi-sentence paragraph should produce one unit per sentence
    (possibly more if any are compound).
    """
    text = (
        "The system shall allow registered patients to book appointments. "
        "Only a Senior Doctor may approve prescriptions for controlled substances. "
        "An appointment moves from Requested to Confirmed once a doctor accepts it."
    )
    units = segment_into_atomic_units(text)
    # At minimum one unit per sentence
    assert len(units) >= 3, f"Expected at least 3 units, got {len(units)}: {units}"


def test_empty_string_returns_empty_list():
    """Empty input should return an empty list without errors."""
    units = segment_into_atomic_units("   ")
    assert units == []


def test_compound_with_must():
    """'must … and must …' should also split."""
    text = "The system must validate the email and must store the result."
    units = segment_into_atomic_units(text)
    assert len(units) == 2


# ---------------------------------------------------------------------------
# Service-level tests (with DB)
# ---------------------------------------------------------------------------


@pytest.fixture()
def session_and_engine(tmp_path, monkeypatch):
    """Redirect DB ops to a temporary SQLite DB."""
    import specforge.db.session as db_session_module

    db_path = tmp_path / "test_preprocessing.db"
    engine = create_engine(
        f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(
        bind=engine, autocommit=False, autoflush=False, expire_on_commit=False
    )
    monkeypatch.setattr(db_session_module, "engine", engine)
    monkeypatch.setattr(db_session_module, "SessionLocal", SessionLocal)
    return engine, SessionLocal


def test_preprocess_single_sentence_sets_atomic_text(session_and_engine):
    """Preprocessing an already-atomic requirement sets atomic_unit_text."""
    from specforge.preprocessing.service import preprocess_requirement

    engine, SessionLocal = session_and_engine
    with SessionLocal() as s:
        req = Requirement(
            raw_text="The admin shall approve leave requests.",
            source_doc_id="doc-pp-001",
        )
        s.add(req)
        s.commit()
        req_id = req.requirement_id

    results = preprocess_requirement(req_id)
    assert len(results) == 1
    assert results[0].atomic_unit_text is not None
    assert "admin" in results[0].atomic_unit_text.lower()


def test_preprocess_compound_creates_siblings(session_and_engine):
    """Preprocessing a compound sentence should create an extra sibling row."""
    from specforge.preprocessing.service import preprocess_requirement

    engine, SessionLocal = session_and_engine
    with SessionLocal() as s:
        req = Requirement(
            raw_text="The system shall log the user in and shall send a confirmation email.",
            source_doc_id="doc-pp-002",
        )
        s.add(req)
        s.commit()
        req_id = req.requirement_id

    results = preprocess_requirement(req_id)
    assert len(results) == 2, f"Expected 2, got {len(results)}"

    with SessionLocal() as s:
        rows = s.query(Requirement).filter_by(source_doc_id="doc-pp-002").all()
    assert len(rows) == 2


def test_preprocess_missing_requirement_raises(session_and_engine):
    """Preprocessing a non-existent requirement_id should raise ValueError."""
    from specforge.preprocessing.service import preprocess_requirement

    with pytest.raises(ValueError, match="not found"):
        preprocess_requirement("non-existent-uuid")
