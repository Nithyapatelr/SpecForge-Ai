"""
Batch Experiment Runner — Executes large-scale evaluation benchmark suite across MAS frameworks.

Provides timestamped progress logging and stateful resumability: interrupting and re-running a batch
with the same batch_id skips previously completed (batch_id, source_doc_id, framework_name) runs.
"""

import datetime
import json
import logging
import os
import uuid
from typing import Any, Dict, List, Optional

from specforge.ambiguity.service import detect_and_store
from specforge.classification.service import classify_and_store
from specforge.db.models import MASRuns
from specforge.db.session import get_session
from specforge.experiments.runner import run_comparative_experiment
from specforge.ingestion.service import ingest_document
from specforge.preprocessing.service import preprocess_requirement

logger = logging.getLogger(__name__)


def _log_progress(msg: str) -> None:
    """Print timestamped progress message."""
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_msg = f"[{ts}] {msg}"
    print(formatted_msg)
    logger.info(formatted_msg)


def is_combination_completed(
    batch_id: str, source_doc_id: str, framework_name: str
) -> bool:
    """
    Check if both baseline (annotated=False) and annotated (annotated=True) runs
    for a (batch_id, source_doc_id, framework_name) combination completed successfully in DB.
    """
    with get_session() as session:
        completed_runs = (
            session.query(MASRuns)
            .filter(
                MASRuns.batch_id == batch_id,
                MASRuns.source_doc_id == source_doc_id,
                MASRuns.framework_name == framework_name,
                MASRuns.status == "completed",
            )
            .all()
        )
        has_baseline = any(not r.annotated for r in completed_runs)
        has_annotated = any(r.annotated for r in completed_runs)
        return has_baseline and has_annotated


def run_full_evaluation_batch(
    task_dir: str = "./data/evaluation_tasks",
    frameworks: Optional[List[str]] = None,
    batch_id: Optional[str] = None,
) -> str:
    """
    Run full evaluation batch across all task documents in task_dir for each framework in frameworks.

    Args:
        task_dir: Directory containing task .json or .txt specification files.
        frameworks: List of MAS framework identifiers to evaluate (default: ["metagpt", "chatdev"]).
        batch_id: Unique batch identifier string. If None, a new timestamped batch_id is generated.

    Returns:
        batch_id: The batch identifier string tagging all persisted MASRuns rows.
    """
    if frameworks is None:
        frameworks = ["metagpt", "chatdev"]

    if not batch_id:
        ts_suffix = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        batch_id = f"batch_{ts_suffix}_{uuid.uuid4().hex[:6]}"

    _log_progress(f"=== INITIATING BATCH RUN: batch_id='{batch_id}' ===")
    _log_progress(f"Target Directory: '{task_dir}' | Target Frameworks: {frameworks}")

    if not os.path.exists(task_dir):
        _log_progress(f"Task directory '{task_dir}' does not exist.")
        return batch_id

    # Gather task files
    task_files = [
        os.path.join(task_dir, f)
        for f in sorted(os.listdir(task_dir))
        if f.endswith(".json") or f.endswith(".txt")
    ]

    if not task_files:
        _log_progress(f"No .json or .txt task files found in '{task_dir}'.")
        return batch_id

    _log_progress(f"Discovered {len(task_files)} evaluation task documents.")

    total_combinations = len(task_files) * len(frameworks)
    current_count = 0

    for task_file in task_files:
        # Load task description and doc_id
        doc_id = os.path.splitext(os.path.basename(task_file))[0]
        raw_text = ""

        if task_file.endswith(".json"):
            with open(task_file, "r", encoding="utf-8") as f:
                task_json = json.load(f)
                doc_id = task_json.get("task_id", doc_id)
                raw_text = task_json.get("raw_text", "")
        else:
            with open(task_file, "r", encoding="utf-8") as f:
                raw_text = f.read()

        if not raw_text.strip():
            _log_progress(f"[SKIP] Empty raw text in '{task_file}'.")
            continue

        # Step 1: SpecForge Ingestion, Preprocessing, Classification, and Ambiguity Detection
        req = ingest_document(raw_text=raw_text, source_doc_id=doc_id)
        processed_reqs = preprocess_requirement(req.requirement_id)
        for r in processed_reqs:
            classify_and_store(r.requirement_id)
            detect_and_store(r.requirement_id)

        # Step 2: Framework Invocations with Resumability Skip
        for framework in frameworks:
            current_count += 1
            if is_combination_completed(batch_id, doc_id, framework):
                _log_progress(
                    f"({current_count}/{total_combinations}) [RESUME-SKIP] Task '{doc_id}' "
                    f"with framework '{framework}' already completed in batch '{batch_id}'."
                )
                continue

            _log_progress(
                f"({current_count}/{total_combinations}) [RUNNING] Task '{doc_id}' "
                f"on framework '{framework}'..."
            )

            res = run_comparative_experiment(
                source_doc_id=doc_id,
                task_description=raw_text,
                framework_name=framework,
                batch_id=batch_id,
            )

            _log_progress(
                f"({current_count}/{total_combinations}) [FINISHED] Task '{doc_id}' "
                f"on framework '{framework}' -> Failure Reduction: {res.get('failure_reduction_percentage', 0.0)}%"
            )

    _log_progress(f"=== BATCH RUN COMPLETE: batch_id='{batch_id}' ===")
    return batch_id


if __name__ == "__main__":
    import sys
    b_id = sys.argv[1] if len(sys.argv) > 1 else None
    run_full_evaluation_batch(batch_id=b_id)
