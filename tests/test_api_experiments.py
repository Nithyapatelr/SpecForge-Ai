"""
Unit tests for FastAPI experiment endpoints (/experiment/run and /experiment/history).
"""

from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient

from specforge.api.main import app
from specforge.db.models import MASRuns
from specforge.db.session import get_session

client = TestClient(app)


def test_experiment_history_endpoint():
    # Insert a dummy MASRuns row into DB
    with get_session() as session:
        run_item = MASRuns(
            source_doc_id="doc_api_history_test",
            framework_name="metagpt",
            annotated=False,
            task_description="Build CLI calculator",
            status="completed"
        )
        session.add(run_item)
        session.commit()

    response = client.get("/experiment/history")
    assert response.status_code == 200
    data = response.json()
    assert "total_runs" in data
    assert "runs" in data
    assert data["total_runs"] >= 1
    run_ids = [r["source_doc_id"] for r in data["runs"]]
    assert "doc_api_history_test" in run_ids


@patch("specforge.api.main.run_comparative_experiment")
def test_experiment_run_endpoint_mocked(mock_run_exp):
    mock_run_exp.return_value = {
        "source_doc_id": "doc_api_run_test",
        "baseline_failure_count": 3,
        "annotated_failure_count": 1,
        "failure_reduction_percentage": 66.7,
    }

    payload = {
        "source_doc_id": "doc_api_run_test",
        "task_description": "Build CLI app",
        "framework_name": "metagpt",
    }
    response = client.post("/experiment/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["source_doc_id"] == "doc_api_run_test"
    assert data["baseline_failure_count"] == 3
    assert data["annotated_failure_count"] == 1
    assert data["failure_reduction_percentage"] == 66.7
