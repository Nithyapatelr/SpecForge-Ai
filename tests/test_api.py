"""
Integration tests for FastAPI endpoints using TestClient.
"""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from specforge.api.main import app
from specforge.db.models import Base, RITTaxonomy


@pytest.fixture()
def client_with_db(tmp_path, monkeypatch):
    """Setup TestClient with temporary SQLite DB."""
    import specforge.db.session as db_session_module

    db_path = tmp_path / "test_api.db"
    engine = create_engine(
        f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(
        bind=engine, autocommit=False, autoflush=False, expire_on_commit=False
    )
    monkeypatch.setattr(db_session_module, "engine", engine)
    monkeypatch.setattr(db_session_module, "SessionLocal", SessionLocal)

    # Seed taxonomy
    with SessionLocal() as s:
        s.add_all([
            RITTaxonomy(label_id="BEHAVIORAL_RULE", label_name="Behavioral Rule", label_definition="Def"),
            RITTaxonomy(label_id="DATA_CONTRACT", label_name="Data Contract", label_definition="Def"),
        ])
        s.commit()

    return TestClient(app)


def test_health_endpoint(client_with_db):
    """GET /health should return 200 OK."""
    response = client_with_db.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@patch("specforge.ambiguity.service.llm_ambiguity_score")
@patch("specforge.classification.service.classify_requirement")
def test_full_api_workflow(mock_classify, mock_llm_amb, client_with_db):
    """Full workflow: ingest -> process -> report."""
    mock_classify.return_value = {
        "label_name": "Behavioral Rule",
        "confidence": 0.9,
        "rationale": "Clear behavioral rule.",
    }
    mock_llm_amb.return_value = {
        "ambiguity_score": 0.1,
        "rationale": "Clear sentence.",
    }

    # 1. Ingest raw text
    text_data = "When patient cancels appointment, system shall notify doctor."
    response = client_with_db.post("/ingest", data={"raw_text": text_data, "source_doc_id": "test-api-doc-1"})
    assert response.status_code == 200
    ingest_res = response.json()
    assert ingest_res["source_doc_id"] == "test-api-doc-1"
    assert len(ingest_res["requirement_ids"]) >= 1

    # 2. Process full document
    proc_resp = client_with_db.post(f"/process/{ingest_res['source_doc_id']}")
    assert proc_resp.status_code == 200
    proc_res = proc_resp.json()
    assert proc_res["processed_count"] >= 1

    # 3. Get report
    rep_resp = client_with_db.get(f"/report/{ingest_res['source_doc_id']}")
    assert rep_resp.status_code == 200
    report = rep_resp.json()
    assert report["source_doc_id"] == "test-api-doc-1"
    assert report["summary"]["total_requirements"] >= 1
