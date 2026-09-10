"""
Unit tests for MAST judge and failure logging service.
"""

from unittest.mock import MagicMock, patch
import pytest

from specforge.db.models import FailureLogs, MASRuns
from specforge.db.session import get_session
from specforge.failure_logging.service import log_failures_for_run
from scripts.seed_mast_taxonomy import seed_mast_taxonomy


@patch("anthropic.Anthropic")
def test_mast_judge_and_logging_service(mock_anthropic_cls, tmp_path):
    seed_mast_taxonomy()

    # Create dummy trace file
    trace_file = tmp_path / "raw_trace.log"
    trace_file.write_text("Execution log with Disobey Task Specification error in Coder stage.")

    # Create MASRuns database record
    with get_session() as session:
        mas_run = MASRuns(
            source_doc_id="doc_test_mast",
            framework_name="metagpt",
            annotated=False,
            task_description="Build CLI app",
            raw_trace_path=str(trace_file),
            status="completed"
        )
        session.add(mas_run)
        session.commit()
        run_id = mas_run.run_id

    # Mock Anthropic API response
    canned_json = """
    [
      {
        "failure_mode_id": "FM-1.1",
        "agent_stage": "Coder",
        "failure_description": "Failed to implement mandatory add command.",
        "confidence": 0.92
      }
    ]
    """
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=canned_json)]
    mock_client.messages.create.return_value = mock_response
    mock_anthropic_cls.return_value = mock_client

    # Call service
    logged_ids = log_failures_for_run(run_id)
    assert len(logged_ids) == 1

    # Verify FailureLogs row in database
    with get_session() as session:
        failure = session.query(FailureLogs).filter_by(failure_id=logged_ids[0]).first()
        assert failure is not None
        assert failure.mast_failure_mode_id == "FM-1.1"
        assert failure.agent_stage == "Coder"
        assert failure.confidence == 0.92
