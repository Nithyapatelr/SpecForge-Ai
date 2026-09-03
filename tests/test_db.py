"""
Tests for database models — round-trip insert/read on all four Phase-1 tables.

Uses an in-memory SQLite database so no file I/O or external services are needed.
"""

import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from specforge.db.models import (
    AmbiguityFlag,
    Base,
    Classification,
    RITTaxonomy,
    Requirement,
)


@pytest.fixture()
def session():
    """Provide a fresh in-memory SQLite session for each test."""
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_requirement_round_trip(session):
    """Insert a Requirement row and read it back."""
    req = Requirement(
        requirement_id=str(uuid.uuid4()),
        source_doc_id="doc-001",
        raw_text="The system shall allow patients to book appointments online.",
        atomic_unit_text=None,
        created_at=datetime.now(timezone.utc),
    )
    session.add(req)
    session.commit()

    fetched = session.query(Requirement).filter_by(source_doc_id="doc-001").one()
    assert fetched.raw_text == "The system shall allow patients to book appointments online."
    assert fetched.atomic_unit_text is None
    assert fetched.source_doc_id == "doc-001"


def test_rit_taxonomy_round_trip(session):
    """Insert a RITTaxonomy row and read it back."""
    label = RITTaxonomy(
        label_id="BEHAVIORAL_RULE",
        label_name="Behavioral Rule",
        label_definition="A rule describing what the system must do under a specific condition.",
        parent_category=None,
    )
    session.add(label)
    session.commit()

    fetched = session.query(RITTaxonomy).filter_by(label_id="BEHAVIORAL_RULE").one()
    assert fetched.label_name == "Behavioral Rule"
    assert fetched.parent_category is None


def test_classification_round_trip(session):
    """Insert linked Requirement + RITTaxonomy + Classification rows and read back."""
    req_id = str(uuid.uuid4())
    req = Requirement(
        requirement_id=req_id,
        raw_text="The system shall validate the patient's email address.",
    )
    label = RITTaxonomy(
        label_id="DATA_CONTRACT",
        label_name="Data Contract",
        label_definition="A description of a data field, its type, format, or validation rule.",
    )
    session.add_all([req, label])
    session.commit()

    clf = Classification(
        classification_id=str(uuid.uuid4()),
        requirement_id=req_id,
        label_id="DATA_CONTRACT",
        confidence_score=0.92,
        classifier_version="rit-v1-fewshot",
        timestamp=datetime.now(timezone.utc),
    )
    session.add(clf)
    session.commit()

    fetched = session.query(Classification).filter_by(requirement_id=req_id).one()
    assert fetched.label_id == "DATA_CONTRACT"
    assert abs(fetched.confidence_score - 0.92) < 1e-6
    assert fetched.classifier_version == "rit-v1-fewshot"


def test_ambiguity_flag_round_trip(session):
    """Insert linked Requirement + AmbiguityFlag rows and read back."""
    req_id = str(uuid.uuid4())
    req = Requirement(
        requirement_id=req_id,
        raw_text="The system should respond quickly.",
    )
    session.add(req)
    session.commit()

    flag = AmbiguityFlag(
        flag_id=str(uuid.uuid4()),
        requirement_id=req_id,
        ambiguity_score=0.85,
        flag_reason="vague_quantifier: quickly | missing_measurable_value",
        timestamp=datetime.now(timezone.utc),
    )
    session.add(flag)
    session.commit()

    fetched = session.query(AmbiguityFlag).filter_by(requirement_id=req_id).one()
    assert abs(fetched.ambiguity_score - 0.85) < 1e-6
    assert "quickly" in fetched.flag_reason


def test_all_four_tables_with_valid_foreign_keys(session):
    """Smoke test: one row in all four tables with valid FK chain."""
    req_id = str(uuid.uuid4())

    req = Requirement(requirement_id=req_id, raw_text="The admin shall approve leave requests.")
    label = RITTaxonomy(label_id="ACTOR_PERM", label_name="Actor Permission",
                        label_definition="Who is allowed to do what.")
    session.add_all([req, label])
    session.commit()

    clf = Classification(
        requirement_id=req_id,
        label_id="ACTOR_PERM",
        confidence_score=0.78,
        classifier_version="rit-v1-fewshot",
    )
    flag = AmbiguityFlag(
        requirement_id=req_id,
        ambiguity_score=0.1,
        flag_reason="none",
    )
    session.add_all([clf, flag])
    session.commit()

    assert session.query(Requirement).count() == 1
    assert session.query(RITTaxonomy).count() == 1
    assert session.query(Classification).count() == 1
    assert session.query(AmbiguityFlag).count() == 1
