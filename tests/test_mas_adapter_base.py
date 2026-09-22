"""
Unit tests for MASAdapter base class and service layer.
"""

import os
import pytest

from specforge.db.models import MASRuns
from specforge.db.session import get_session
from specforge.mas_adapter.base import MASAdapter
from specforge.mas_adapter.service import ADAPTER_REGISTRY, execute_mas_run, register_adapter


class DummyAdapter(MASAdapter):
    def prepare_task_input(self, annotated_spec, task_description):
        if annotated_spec:
            return f"ANNOTATED: {task_description}"
        return task_description

    def run(self, prepared_input, output_dir):
        trace_file = os.path.join(output_dir, "trace.log")
        with open(trace_file, "w", encoding="utf-8") as f:
            f.write(f"Execution trace for: {prepared_input}\nStep 1: Done\n")
        return {
            "status": "completed",
            "raw_trace_path": trace_file,
            "duration_seconds": 0.5,
        }

    def get_framework_name(self):
        return "dummy"


def test_mas_adapter_plumbing(tmp_path):
    register_adapter("dummy", DummyAdapter)
    assert "dummy" in ADAPTER_REGISTRY

    out_dir = str(tmp_path / "run_out")
    run_id = execute_mas_run(
        source_doc_id="doc_dummy",
        task_description="Build dummy feature",
        framework_name="dummy",
        annotated=False,
        output_dir=out_dir,
    )

    assert run_id is not None

    with get_session() as session:
        run_row = session.query(MASRuns).filter_by(run_id=run_id).first()
        assert run_row is not None
        assert run_row.framework_name == "dummy"
        assert run_row.annotated is False
        assert run_row.status == "completed"
        assert os.path.exists(run_row.raw_trace_path)


def test_execute_mas_run_chatdev(tmp_path):
    out_dir = str(tmp_path / "chatdev_run")
    run_id = execute_mas_run(
        source_doc_id="doc_chatdev",
        task_description="Build calculator app",
        framework_name="chatdev",
        annotated=False,
        output_dir=out_dir,
    )

    assert run_id is not None
    with get_session() as session:
        run_row = session.query(MASRuns).filter_by(run_id=run_id).first()
        assert run_row is not None
        assert run_row.framework_name == "chatdev"
        assert run_row.status == "completed"
        assert os.path.exists(run_row.raw_trace_path)

