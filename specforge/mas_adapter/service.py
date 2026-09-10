"""
MAS Adapter Service — Orchestrates task preparation, adapter execution, and database logging.
"""

import os
import tempfile
import logging
from typing import Dict, Type, Optional

from specforge.db.models import MASRuns
from specforge.db.session import get_session
from specforge.mas_adapter.base import MASAdapter
from specforge.reporting.annotator import generate_annotated_spec

logger = logging.getLogger(__name__)

# Registry mapping framework names (e.g. "metagpt") to MASAdapter classes
ADAPTER_REGISTRY: Dict[str, Type[MASAdapter]] = {}


def register_adapter(framework_name: str, adapter_cls: Type[MASAdapter]) -> None:
    """Register a concrete MASAdapter class under a framework name."""
    ADAPTER_REGISTRY[framework_name] = adapter_cls


def execute_mas_run(
    source_doc_id: str,
    task_description: str,
    framework_name: str = "metagpt",
    annotated: bool = False,
    output_dir: Optional[str] = None,
) -> str:
    """
    Execute a MAS framework run on a task with optional SpecForge annotations.

    Returns:
        run_id: Unique UUID string identifying the MASRuns row.
    """
    if framework_name == "metagpt" and "metagpt" not in ADAPTER_REGISTRY:
        import specforge.mas_adapter.metagpt_adapter  # noqa: F401

    if framework_name not in ADAPTER_REGISTRY:
        raise ValueError(
            f"Framework '{framework_name}' is not registered. Available adapters: {list(ADAPTER_REGISTRY.keys())}"
        )

    adapter_cls = ADAPTER_REGISTRY[framework_name]
    adapter = adapter_cls()

    # Step 1: Generate annotated spec if requested
    annotated_spec = None
    if annotated and source_doc_id:
        annotated_spec = generate_annotated_spec(source_doc_id)

    # Step 2: Prepare task input
    prepared_input = adapter.prepare_task_input(annotated_spec, task_description)

    # Step 3: Run adapter
    if not output_dir:
        output_dir = tempfile.mkdtemp(prefix=f"specforge_{framework_name}_")
    os.makedirs(output_dir, exist_ok=True)

    result = adapter.run(prepared_input, output_dir)

    status = result.get("status", "failed_to_run")
    raw_trace_path = result.get("raw_trace_path", "")

    # Step 4: Persist MASRuns record
    with get_session() as session:
        mas_run = MASRuns(
            source_doc_id=source_doc_id,
            framework_name=framework_name,
            annotated=annotated,
            task_description=task_description,
            raw_trace_path=raw_trace_path,
            status=status,
        )
        session.add(mas_run)
        session.commit()
        run_id = mas_run.run_id

    logger.info("Executed MAS run %s with status '%s'", run_id, status)
    return run_id
