"""
Tests for Ambiguity Detection module.
"""

from unittest.mock import patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from specforge.ambiguity.heuristics import heuristic_ambiguity_score
from specforge.db.models import AmbiguityFlag, Base, Requirement


@pytest.fixture()
def session_and_engine(tmp_path, monkeypatch):
    """Redirect DB ops to temporary SQLite DB."""
    import specforge.db.session as db_session_module

    db_path = tmp_path / "test_ambiguity.db"
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


def test_heuristic_vague_vs_precise():
    """Vague sentence should score higher than precise sentence."""
    vague_text = "The system should respond quickly and be user-friendly."
    precise_text = "The system shall process patient search requests in under 500ms."

    vague_res = heuristic_ambiguity_score(vague_text)
    precise_res = heuristic_ambiguity_score(precise_text)

    assert vague_res["ambiguity_score"] > precise_res["ambiguity_score"]
    assert len(vague_res["smells"]) >= 1


@patch("specforge.ambiguity.service.llm_ambiguity_score")
def test_detect_and_store(mock_llm, session_and_engine):
    """Test detect_and_store storing AmbiguityFlags row."""
    from specforge.ambiguity.service import detect_and_store

    engine, SessionLocal = session_and_engine

    mock_llm.return_value = {
        "ambiguity_score": 0.75,
        "rationale": "Vague performance requirement.",
    }

    with SessionLocal() as s:
        req = Requirement(
            raw_text="The system should respond quickly.",
            atomic_unit_text="The system should respond quickly.",
            source_doc_id="doc-amb-01",
        )
        s.add(req)
        s.commit()
        req_id = req.requirement_id

    flag = detect_and_store(req_id)

    assert flag is not None
    assert flag.ambiguity_score >= 0.75
    assert "LLM:" in flag.flag_reason or "Heuristics:" in flag.flag_reason

    with SessionLocal() as s:
        db_flag = s.query(AmbiguityFlag).filter_by(requirement_id=req_id).first()
        assert db_flag is not None
        assert db_flag.ambiguity_score >= 0.75
