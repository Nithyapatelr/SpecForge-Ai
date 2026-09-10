"""
Failure Logging Service — reads MAS run traces, invokes MAST judge, and persists FailureLogs.
"""

import os
import logging
from typing import List

from specforge.db.models import FailureLogs, MASRuns, MASTTaxonomy
from specforge.db.session import get_session
from specforge.failure_logging.mast_judge import annotate_trace_with_mast

logger = logging.getLogger(__name__)


def log_failures_for_run(run_id: str) -> List[str]:
    """
    Load raw trace for a MAS run, evaluate it against MAST failure modes,
    and persist FailureLogs entries.

    Returns:
        List of created failure_id UUID strings.
    """
    with get_session() as session:
        mas_run = session.query(MASRuns).filter_by(run_id=run_id).first()
        if not mas_run:
            raise ValueError(f"MASRuns record with run_id='{run_id}' not found.")

        raw_trace_path = mas_run.raw_trace_path
        if not raw_trace_path or not os.path.exists(raw_trace_path):
            logger.warning("Trace file '%s' not found for run %s", raw_trace_path, run_id)
            return []

        with open(raw_trace_path, "r", encoding="utf-8") as f:
            trace_content = f.read()

        failures = annotate_trace_with_mast(trace_content)

        # Check existing valid MAST IDs in database
        valid_mast_ids = {
            r.failure_mode_id for r in session.query(MASTTaxonomy.failure_mode_id).all()
        }

        created_ids = []
        for fail_item in failures:
            mode_id = fail_item["failure_mode_id"]
            if valid_mast_ids and mode_id not in valid_mast_ids:
                logger.warning("Unrecognized MAST failure mode '%s', skipping DB insert.", mode_id)
                continue

            failure_row = FailureLogs(
                run_id=run_id,
                mast_failure_mode_id=mode_id,
                failure_description=fail_item["failure_description"],
                agent_stage=fail_item["agent_stage"],
                confidence=fail_item["confidence"],
            )
            session.add(failure_row)
            session.commit()
            created_ids.append(failure_row.failure_id)

    logger.info("Logged %d MAST failures for MAS run %s", len(created_ids), run_id)
    return created_ids
