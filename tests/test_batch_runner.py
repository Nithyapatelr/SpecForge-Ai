"""
Unit tests for batch experiment runner and resumable execution logic.
"""

import os
import json
from unittest.mock import MagicMock, patch

import pytest
from specforge.db.models import MASRuns
from specforge.db.session import get_session
from specforge.experiments.batch_runner import is_combination_completed, run_full_evaluation_batch


@pytest.fixture
def temp_task_dir(tmp_path):
    """Create a temporary task directory with 2 dummy task JSON files."""
    task_dir = tmp_path / "eval_tasks"
    task_dir.mkdir()

    t1 = {
        "task_id": "test_task_01",
        "title": "Task 1",
        "raw_text": "The system shall calculate sum fast.",
        "ground_truth_checklist": ["Check sum"],
    }
    t2 = {
        "task_id": "test_task_02",
        "title": "Task 2",
        "raw_text": "The system shall store logs seamlessly.",
        "ground_truth_checklist": ["Check logs"],
    }

    with open(task_dir / "t1.json", "w", encoding="utf-8") as f:
        json.dump(t1, f)
    with open(task_dir / "t2.json", "w", encoding="utf-8") as f:
        json.dump(t2, f)

    return str(task_dir)


@patch("specforge.experiments.batch_runner.run_comparative_experiment")
def test_batch_runner_fresh_run_attempts_all_combinations(mock_run_exp, temp_task_dir):
    """
    Assert that on a fresh batch run, all task/framework combinations are attempted.
    """
    mock_run_exp.return_value = {
        "failure_reduction_percentage": 50.0,
        "baseline_status": "completed",
        "annotated_status": "completed",
    }

    frameworks = ["metagpt", "chatdev"]
    batch_id = "batch_fresh_test_01"

    returned_batch_id = run_full_evaluation_batch(
        task_dir=temp_task_dir,
        frameworks=frameworks,
        batch_id=batch_id,
    )

    assert returned_batch_id == batch_id
    # 2 task files * 2 frameworks = 4 combinations attempted
    assert mock_run_exp.call_count == 4

    called_combinations = [
        (call.kwargs["source_doc_id"], call.kwargs["framework_name"])
        for call in mock_run_exp.call_args_list
    ]

    expected = [
        ("test_task_01", "metagpt"),
        ("test_task_01", "chatdev"),
        ("test_task_02", "metagpt"),
        ("test_task_02", "chatdev"),
    ]

    for combo in expected:
        assert combo in called_combinations


@patch("specforge.experiments.batch_runner.run_comparative_experiment")
def test_batch_runner_resumability_skips_completed_combinations(mock_run_exp, temp_task_dir):
    """
    Assert that re-running with the same batch_id after a simulated partial failure
    correctly skips completed combinations and only retries the missing ones.
    """
    batch_id = "batch_resume_test_02"
    frameworks = ["metagpt", "chatdev"]

    # Manually insert completed MASRuns rows for test_task_01 + metagpt into the DB
    with get_session() as session:
        r1 = MASRuns(
            batch_id=batch_id,
            source_doc_id="test_task_01",
            framework_name="metagpt",
            annotated=False,
            task_description="test task 1",
            status="completed",
        )
        r2 = MASRuns(
            batch_id=batch_id,
            source_doc_id="test_task_01",
            framework_name="metagpt",
            annotated=True,
            task_description="test task 1 annotated",
            status="completed",
        )
        session.add_all([r1, r2])
        session.commit()

    # Verify that test_task_01 + metagpt is detected as completed
    assert is_combination_completed(batch_id, "test_task_01", "metagpt") is True
    # Verify that test_task_01 + chatdev is NOT completed yet
    assert is_combination_completed(batch_id, "test_task_01", "chatdev") is False

    mock_run_exp.return_value = {
        "failure_reduction_percentage": 25.0,
        "baseline_status": "completed",
        "annotated_status": "completed",
    }

    # Execute batch run with the same batch_id
    returned_batch_id = run_full_evaluation_batch(
        task_dir=temp_task_dir,
        frameworks=frameworks,
        batch_id=batch_id,
    )

    assert returned_batch_id == batch_id
    # 4 total combinations - 1 completed combination = 3 expected mock calls
    assert mock_run_exp.call_count == 3

    called_combinations = [
        (call.kwargs["source_doc_id"], call.kwargs["framework_name"])
        for call in mock_run_exp.call_args_list
    ]

    # test_task_01 + metagpt should NOT be in called combinations
    assert ("test_task_01", "metagpt") not in called_combinations
    # Remaining combinations SHOULD be called
    assert ("test_task_01", "chatdev") in called_combinations
    assert ("test_task_02", "metagpt") in called_combinations
    assert ("test_task_02", "chatdev") in called_combinations
