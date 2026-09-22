"""
Comparative Experiment Runner — executes baseline vs SpecForge-annotated MAS runs and compares failure metrics.
"""

import logging
from typing import Any, Dict

from specforge.db.models import FailureLogs, MASRuns, MASTTaxonomy
from specforge.db.session import get_session
from specforge.failure_logging.service import log_failures_for_run
from specforge.mas_adapter.service import execute_mas_run

logger = logging.getLogger(__name__)


def _get_run_failure_stats(run_id: str) -> Dict[str, Any]:
    """Retrieve failure count and category breakdown for a run from DB."""
    with get_session() as session:
        mas_run = session.query(MASRuns).filter_by(run_id=run_id).first()
        status = mas_run.status if mas_run else "unknown"

        failures = (
            session.query(FailureLogs, MASTTaxonomy)
            .join(MASTTaxonomy, FailureLogs.mast_failure_mode_id == MASTTaxonomy.failure_mode_id)
            .filter(FailureLogs.run_id == run_id)
            .all()
        )

        cat_breakdown = {
            "Specification Issues": 0,
            "Inter-Agent Misalignment": 0,
            "Task Verification": 0,
        }

        for failure, taxonomy in failures:
            cat = taxonomy.category
            cat_breakdown[cat] = cat_breakdown.get(cat, 0) + 1

        return {
            "status": status,
            "failure_count": len(failures),
            "failures_by_category": cat_breakdown,
        }


def run_comparative_experiment(
    source_doc_id: str,
    task_description: str,
    framework_name: str = "metagpt",
    batch_id: str | None = None,
) -> Dict[str, Any]:
    """
    Execute baseline (unmodified) and SpecForge-annotated MAS runs for a given task,
    tag execution failures with MAST, and produce a comparative summary.
    """
    logger.info("Starting comparative experiment for source_doc_id='%s' (%s, batch_id=%s)", source_doc_id, framework_name, batch_id)

    # 1. Baseline run (annotated=False)
    baseline_run_id = execute_mas_run(
        source_doc_id=source_doc_id,
        task_description=task_description,
        framework_name=framework_name,
        annotated=False,
        batch_id=batch_id,
    )
    log_failures_for_run(baseline_run_id)
    baseline_stats = _get_run_failure_stats(baseline_run_id)

    # 2. SpecForge-annotated run (annotated=True)
    annotated_run_id = execute_mas_run(
        source_doc_id=source_doc_id,
        task_description=task_description,
        framework_name=framework_name,
        annotated=True,
        batch_id=batch_id,
    )
    log_failures_for_run(annotated_run_id)
    annotated_stats = _get_run_failure_stats(annotated_run_id)

    b_count = baseline_stats["failure_count"]
    a_count = annotated_stats["failure_count"]
    reduction_pct = round(((b_count - a_count) / b_count * 100), 1) if b_count > 0 else 0.0

    comparison = {
        "source_doc_id": source_doc_id,
        "framework_name": framework_name,
        "task_description": task_description,
        "baseline_run_id": baseline_run_id,
        "annotated_run_id": annotated_run_id,
        "baseline_status": baseline_stats["status"],
        "annotated_status": annotated_stats["status"],
        "baseline_failure_count": b_count,
        "annotated_failure_count": a_count,
        "baseline_failures_by_category": baseline_stats["failures_by_category"],
        "annotated_failures_by_category": annotated_stats["failures_by_category"],
        "failure_reduction_percentage": reduction_pct,
    }

    logger.info(
        "Comparative experiment complete: Baseline Failures=%d, Annotated Failures=%d (%.1f%% reduction)",
        b_count, a_count, reduction_pct
    )
    return comparison
