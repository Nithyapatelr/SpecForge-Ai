"""
Tests for Diagnostic Report Generator.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from specforge.db.models import AmbiguityFlag, Base, Classification, RITTaxonomy, Requirement
from specforge.reporting.annotator import generate_annotated_spec


@pytest.fixture()
def seeded_db(tmp_path, monkeypatch):
    """Seed temporary SQLite DB with 3 Requirements + Classifications + AmbiguityFlags."""
    import specforge.db.session as db_session_module

    db_path = tmp_path / "test_annotator.db"
    engine = create_engine(
        f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(
        bind=engine, autocommit=False, autoflush=False, expire_on_commit=False
    )
    monkeypatch.setattr(db_session_module, "engine", engine)
    monkeypatch.setattr(db_session_module, "SessionLocal", SessionLocal)

    with SessionLocal() as s:
        # Taxonomy
        s.add_all([
            RITTaxonomy(label_id="BEHAVIORAL_RULE", label_name="Behavioral Rule", label_definition="Def"),
            RITTaxonomy(label_id="ACCEPTANCE_CONDITION", label_name="Acceptance Condition", label_definition="Def"),
        ])
        s.commit()

        # 3 Requirements
        r1 = Requirement(requirement_id="req-1", source_doc_id="doc-report-1", raw_text="Req 1 text", atomic_unit_text="Req 1 text")
        r2 = Requirement(requirement_id="req-2", source_doc_id="doc-report-1", raw_text="Req 2 text", atomic_unit_text="Req 2 text")
        r3 = Requirement(requirement_id="req-3", source_doc_id="doc-report-1", raw_text="Req 3 text", atomic_unit_text="Req 3 text")
        s.add_all([r1, r2, r3])
        s.commit()

        # Classifications
        s.add_all([
            Classification(requirement_id="req-1", label_id="BEHAVIORAL_RULE", confidence_score=0.9, classifier_version="v1"),
            Classification(requirement_id="req-2", label_id="BEHAVIORAL_RULE", confidence_score=0.85, classifier_version="v1"),
            Classification(requirement_id="req-3", label_id="ACCEPTANCE_CONDITION", confidence_score=0.95, classifier_version="v1"),
        ])

        # AmbiguityFlags (req-1 high ambiguity > 0.6)
        s.add_all([
            AmbiguityFlag(requirement_id="req-1", ambiguity_score=0.8, flag_reason="vague"),
            AmbiguityFlag(requirement_id="req-2", ambiguity_score=0.2, flag_reason="none"),
            AmbiguityFlag(requirement_id="req-3", ambiguity_score=0.1, flag_reason="none"),
        ])
        s.commit()

    return engine


def test_generate_annotated_spec(seeded_db):
    """Test report generation shape and summary metrics."""
    report = generate_annotated_spec("doc-report-1")

    assert report["source_doc_id"] == "doc-report-1"
    assert len(report["requirements"]) == 3

    summary = report["summary"]
    assert summary["total_requirements"] == 3
    assert summary["label_distribution"]["Behavioral Rule"] == 2
    assert summary["label_distribution"]["Acceptance Condition"] == 1
    assert summary["high_ambiguity_count"] == 1
