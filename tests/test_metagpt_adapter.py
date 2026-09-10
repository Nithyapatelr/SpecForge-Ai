"""
Unit and integration tests for MetaGPTAdapter.
"""

import os
import pytest

from specforge.mas_adapter.metagpt_adapter import MetaGPTAdapter


def test_metagpt_prepare_task_input_baseline():
    adapter = MetaGPTAdapter()
    raw_prompt = "Build a simple calculator"
    prepared = adapter.prepare_task_input(None, raw_prompt)
    assert prepared == raw_prompt


def test_metagpt_prepare_task_input_annotated():
    adapter = MetaGPTAdapter()
    annotated_spec = {
        "source_doc_id": "doc_test",
        "requirements": [
            {
                "requirement_id": "req_1",
                "atomic_unit_text": "The system shall calculate sum.",
                "rit_label": "Behavioral Rule",
                "ambiguity_score": 0.10,
                "ambiguity_reasons": [],
            },
            {
                "requirement_id": "req_2",
                "atomic_unit_text": "The system should perform fast.",
                "rit_label": "Acceptance Condition",
                "ambiguity_score": 0.85,
                "ambiguity_reasons": ["vague_quantifier: fast"],
            },
        ],
    }
    raw_prompt = "Build a simple calculator"
    prepared = adapter.prepare_task_input(annotated_spec, raw_prompt)

    assert "=== SPECFORGE AI PRE-ANALYSIS ANNOTATIONS ===" in prepared
    assert "Acceptance Condition" in prepared
    assert "WARNINGS: vague_quantifier: fast" in prepared
    assert raw_prompt in prepared


@pytest.mark.integration
def test_metagpt_adapter_integration(tmp_path):
    adapter = MetaGPTAdapter()

    # Baseline run
    baseline_out = str(tmp_path / "baseline")
    res_baseline = adapter.run("build a command-line calculator that adds two numbers", baseline_out)
    assert res_baseline["status"] == "completed"
    assert os.path.exists(res_baseline["raw_trace_path"])
    assert os.path.getsize(res_baseline["raw_trace_path"]) > 0

    # Annotated run
    annotated_out = str(tmp_path / "annotated")
    annotated_spec = {
        "requirements": [
            {
                "requirement_id": "r1",
                "atomic_unit_text": "The calculator shall take two floats as arguments.",
                "rit_label": "Data Contract",
                "ambiguity_score": 0.0,
            }
        ]
    }
    prep_input = adapter.prepare_task_input(annotated_spec, "build a command-line calculator that adds two numbers")
    res_annotated = adapter.run(prep_input, annotated_out)
    assert res_annotated["status"] == "completed"
    assert os.path.exists(res_annotated["raw_trace_path"])
    assert os.path.getsize(res_annotated["raw_trace_path"]) > 0
