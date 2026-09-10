"""
Unit tests for comparative experiment runner.
"""

from unittest.mock import patch
import pytest

from specforge.experiments.runner import run_comparative_experiment
from specforge.mas_adapter.base import MASAdapter
from specforge.mas_adapter.service import register_adapter
from scripts.seed_mast_taxonomy import seed_mast_taxonomy


class MockExperimentAdapter(MASAdapter):
    def prepare_task_input(self, annotated_spec, task_description):
        return task_description

    def run(self, prepared_input, output_dir):
        import os
        log_path = os.path.join(output_dir, "trace.log")
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("Mock trace content")
        return {
            "status": "completed",
            "raw_trace_path": log_path,
            "duration_seconds": 0.1,
        }

    def get_framework_name(self):
        return "mock_exp"


@patch("specforge.failure_logging.service.annotate_trace_with_mast")
def test_run_comparative_experiment_mocked(mock_judge):
    seed_mast_taxonomy()
    register_adapter("mock_exp", MockExperimentAdapter)

    # First call (baseline run) returns 2 failures, second call (annotated run) returns 1 failure
    mock_judge.side_effect = [
        [
            {
                "failure_mode_id": "FM-1.1",
                "agent_stage": "Coder",
                "failure_description": "Baseline specification error.",
                "confidence": 0.9,
            },
            {
                "failure_mode_id": "FM-2.2",
                "agent_stage": "Reviewer",
                "failure_description": "Fail to ask clarification.",
                "confidence": 0.85,
            },
        ],
        [
            {
                "failure_mode_id": "FM-1.1",
                "agent_stage": "Coder",
                "failure_description": "Annotated specification error.",
                "confidence": 0.9,
            }
        ],
    ]

    result = run_comparative_experiment(
        source_doc_id="doc_mock_exp",
        task_description="Build mock app",
        framework_name="mock_exp",
    )

    assert result["source_doc_id"] == "doc_mock_exp"
    assert result["framework_name"] == "mock_exp"
    assert result["baseline_failure_count"] == 2
    assert result["annotated_failure_count"] == 1
    assert result["failure_reduction_percentage"] == 50.0
    assert result["baseline_failures_by_category"]["Specification Issues"] == 1
    assert result["baseline_failures_by_category"]["Inter-Agent Misalignment"] == 1
    assert result["annotated_failures_by_category"]["Specification Issues"] == 1
