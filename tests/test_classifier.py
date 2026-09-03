"""
Tests for the RIT Intent Classifier module using unittest.mock.
"""

from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from specforge.db.models import Base, Classification, RITTaxonomy, Requirement


@pytest.fixture()
def session_and_engine(tmp_path, monkeypatch):
    """Redirect DB ops to a temporary SQLite DB with seeded taxonomy."""
    import specforge.db.session as db_session_module

    db_path = tmp_path / "test_classifier.db"
    engine = create_engine(
        f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(
        bind=engine, autocommit=False, autoflush=False, expire_on_commit=False
    )
    monkeypatch.setattr(db_session_module, "engine", engine)
    monkeypatch.setattr(db_session_module, "SessionLocal", SessionLocal)

    # Seed RITTaxonomy
    with SessionLocal() as s:
        s.add_all([
            RITTaxonomy(label_id="BEHAVIORAL_RULE", label_name="Behavioral Rule", label_definition="Def"),
            RITTaxonomy(label_id="DATA_CONTRACT", label_name="Data Contract", label_definition="Def"),
        ])
        s.commit()

    return engine, SessionLocal


@patch("specforge.classification.classifier.anthropic.Anthropic")
def test_classify_requirement_mocked(mock_anthropic):
    """Test classify_requirement with mocked Anthropic client."""
    from specforge.classification.classifier import classify_requirement

    mock_client = MagicMock()
    mock_anthropic.return_value = mock_client

    mock_response = MagicMock()
    mock_response.content = [
        MagicMock(text='{"label_name": "Behavioral Rule", "confidence": 0.95, "rationale": "Clear rule."}')
    ]
    mock_client.messages.create.return_value = mock_response

    res = classify_requirement("When X happens system shall do Y.")

    assert res["label_name"] == "Behavioral Rule"
    assert res["confidence"] == 0.95
    assert res["rationale"] == "Clear rule."


@patch("specforge.classification.service.classify_requirement")
def test_classify_and_store(mock_classify, session_and_engine):
    """Test classify_and_store creating Classifications DB row."""
    from specforge.classification.service import classify_and_store

    engine, SessionLocal = session_and_engine

    mock_classify.return_value = {
        "label_name": "Data Contract",
        "confidence": 0.88,
        "rationale": "Defines field format.",
    }

    with SessionLocal() as s:
        req = Requirement(
            raw_text="Patient DOB must be ISO 8601.",
            atomic_unit_text="Patient DOB must be ISO 8601.",
            source_doc_id="doc-clf-01",
        )
        s.add(req)
        s.commit()
        req_id = req.requirement_id

    clf_row = classify_and_store(req_id)

    assert clf_row is not None
    assert clf_row.label_id == "DATA_CONTRACT"
    assert abs(clf_row.confidence_score - 0.88) < 1e-5

    with SessionLocal() as s:
        db_clf = s.query(Classification).filter_by(requirement_id=req_id).first()
        assert db_clf is not None
        assert db_clf.label_id == "DATA_CONTRACT"
