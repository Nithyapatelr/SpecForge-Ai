"""
Statistical Correlation Engine for SpecForge AI Evaluation.

Implements:
1. Chi-Square Test of Independence (RIT Requirement Labels vs MAST Failure Categories).
2. Point-Biserial Correlation (Requirement Ambiguity Scores vs Failure Occurrences).
3. Bootstrap Confidence Interval Estimation (Annotated vs Baseline Failure Reduction).
"""

import logging
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy import stats

from specforge.db.models import (
    AmbiguityFlag,
    Classification,
    FailureLogs,
    MASRuns,
    MASTTaxonomy,
    Requirement,
    RITTaxonomy,
)
from specforge.db.session import get_session

logger = logging.getLogger(__name__)

STANDARD_RIT_LABELS = [
    "Behavioral Rule",
    "State Transition",
    "Actor Permission",
    "Data Contract",
    "Integration Constraint",
    "Acceptance Condition",
]

STANDARD_MAST_CATEGORIES = [
    "Specification Issues",
    "Inter-Agent Misalignment",
    "Task Verification",
]


def chi_square_rit_vs_failure(batch_id: str) -> Dict[str, Any]:
    """
    # Tests whether failure category is independent of requirement type — a significant result
    # supports the idea that different RIT categories are differently failure-prone.

    Builds a contingency table:
      rows = RIT labels (Behavioral Rule, State Transition, Actor Permission, etc.)
      columns = MAST failure categories (Specification Issues, Inter-Agent Misalignment, Task Verification)
      cells = count of failures where the associated requirement had that RIT label and the failure fell in that category.

    Runs scipy.stats.chi2_contingency.
    """
    with get_session() as session:
        # Query all runs in the batch
        runs = session.query(MASRuns).filter(MASRuns.batch_id == batch_id).all()
        doc_ids = list({r.source_doc_id for r in runs if r.source_doc_id})

        if not doc_ids:
            # Empty fallback when no DB runs match batch_id
            return _empty_chi_square_result("No MAS runs found for batch_id.")

        # Query requirements and their latest classification label
        reqs = session.query(Requirement).filter(Requirement.source_doc_id.in_(doc_ids)).all()
        req_label_map: Dict[str, str] = {}
        for req in reqs:
            clf = (
                session.query(Classification)
                .filter(Classification.requirement_id == req.requirement_id)
                .order_by(Classification.timestamp.desc())
                .first()
            )
            if clf:
                tax = session.query(RITTaxonomy).filter_by(label_id=clf.label_id).first()
                label_name = tax.label_name if tax else clf.label_id
                req_label_map[req.requirement_id] = label_name

        # Query all failures for runs in batch
        run_ids = [r.run_id for r in runs]
        failures = (
            session.query(FailureLogs, MASTTaxonomy)
            .join(MASTTaxonomy, FailureLogs.mast_failure_mode_id == MASTTaxonomy.failure_mode_id)
            .filter(FailureLogs.run_id.in_(run_ids))
            .all()
        )

        # Build contingency table dictionary
        contingency_dict: Dict[str, Dict[str, int]] = {
            rit: {cat: 0 for cat in STANDARD_MAST_CATEGORIES} for rit in STANDARD_RIT_LABELS
        }

        # Count failures per RIT label and MAST category
        for failure, taxonomy in failures:
            cat = taxonomy.category
            if cat not in STANDARD_MAST_CATEGORIES:
                continue

            # Find matching RIT labels for the requirement(s) of this run's source doc
            run_obj = next((r for r in runs if r.run_id == failure.run_id), None)
            if run_obj and run_obj.source_doc_id:
                matching_req_ids = [
                    r.requirement_id for r in reqs if r.source_doc_id == run_obj.source_doc_id
                ]
                for req_id in matching_req_ids:
                    rit_label = req_label_map.get(req_id, "Behavioral Rule")
                    if rit_label in contingency_dict:
                        contingency_dict[rit_label][cat] += 1

    return _compute_chi_square_from_dict(contingency_dict)


def _compute_chi_square_from_dict(contingency_dict: Dict[str, Dict[str, int]]) -> Dict[str, Any]:
    """Calculate chi2_contingency statistics from a nested contingency dict."""
    matrix = []
    for rit in STANDARD_RIT_LABELS:
        row = [contingency_dict.get(rit, {}).get(cat, 0) for cat in STANDARD_MAST_CATEGORIES]
        matrix.append(row)

    arr = np.array(matrix)
    
    # Filter out all-zero rows and columns to prevent zero expected frequency calculation errors
    row_mask = ~np.all(arr == 0, axis=1)
    arr = arr[row_mask]
    if arr.size == 0:
        return _empty_chi_square_result("Contingency table has insufficient non-zero counts.")
    
    col_mask = ~np.all(arr == 0, axis=0)
    arr = arr[:, col_mask]
    
    total_count = int(np.sum(arr))

    if total_count == 0 or arr.shape[0] < 2 or arr.shape[1] < 2:
        return _empty_chi_square_result("Contingency table has insufficient non-zero dimensions.")

    try:
        chi2, p_val, dof, _ = stats.chi2_contingency(arr)
        p_val = float(p_val)
        chi2 = float(chi2)
        dof = int(dof)

        interp = (
            f"Chi-square test of independence (chi2={chi2:.2f}, p={p_val:.4f}, dof={dof}). "
            + (
                "Statistically significant association detected between requirement RIT categories and MAST failure types (p < 0.05)."
                if p_val < 0.05
                else "No statistically significant dependency detected (p >= 0.05); failure category distribution is independent of RIT requirement type."
            )
        )

        return {
            "chi2": round(chi2, 4),
            "p_value": round(p_val, 4),
            "dof": dof,
            "contingency_table": contingency_dict,
            "interpretation": interp,
        }
    except Exception as exc:
        logger.warning("Chi-square calculation error: %s", exc)
        return _empty_chi_square_result(f"Chi-square calculation error: {exc}")


def _empty_chi_square_result(reason: str) -> Dict[str, Any]:
    contingency_dict = {
        rit: {cat: 0 for cat in STANDARD_MAST_CATEGORIES} for rit in STANDARD_RIT_LABELS
    }
    return {
        "chi2": 0.0,
        "p_value": 1.0,
        "dof": 0,
        "contingency_table": contingency_dict,
        "interpretation": f"Insufficient data for Chi-square test ({reason}).",
    }


def point_biserial_ambiguity_vs_failure(batch_id: str) -> Dict[str, Any]:
    """
    For every requirement in the batch, pair its ambiguity_score (continuous float 0.0 to 1.0)
    with a binary indicator (1 if ANY failure was logged against a run using that requirement, 0 otherwise).

    Runs scipy.stats.pointbiserialr.
    """
    with get_session() as session:
        runs = session.query(MASRuns).filter(MASRuns.batch_id == batch_id).all()
        doc_ids = list({r.source_doc_id for r in runs if r.source_doc_id})

        if not doc_ids:
            return _empty_point_biserial_result("No MAS runs found for batch_id.")

        # Find which source_doc_ids experienced any failure
        run_ids = [r.run_id for r in runs]
        failed_run_ids = set(
            row[0]
            for row in session.query(FailureLogs.run_id)
            .filter(FailureLogs.run_id.in_(run_ids))
            .distinct()
        )
        failed_doc_ids = set(
            r.source_doc_id for r in runs if r.run_id in failed_run_ids and r.source_doc_id
        )

        # Get requirements for batch docs
        reqs = session.query(Requirement).filter(Requirement.source_doc_id.in_(doc_ids)).all()

        ambiguity_scores = []
        failure_flags = []

        for req in reqs:
            flag = (
                session.query(AmbiguityFlag)
                .filter(AmbiguityFlag.requirement_id == req.requirement_id)
                .order_by(AmbiguityFlag.timestamp.desc())
                .first()
            )
            amb_score = flag.ambiguity_score if flag else 0.0
            has_failure = 1 if req.source_doc_id in failed_doc_ids else 0

            ambiguity_scores.append(amb_score)
            failure_flags.append(has_failure)

    return calculate_point_biserial_stats(ambiguity_scores, failure_flags)


def calculate_point_biserial_stats(
    ambiguity_scores: List[float], failure_flags: List[int]
) -> Dict[str, Any]:
    """Compute point-biserial correlation for scores and binary failure flags."""
    n = len(ambiguity_scores)
    if n < 3 or len(set(failure_flags)) <= 1 or len(set(ambiguity_scores)) <= 1:
        return _empty_point_biserial_result(f"Insufficient variance in sample data (n={n}).")

    try:
        corr, p_val = stats.pointbiserialr(failure_flags, ambiguity_scores)
        corr = float(corr)
        p_val = float(p_val)

        if np.isnan(corr):
            return _empty_point_biserial_result("Calculation produced NaN correlation.")

        interp = (
            f"Point-biserial correlation r_pb={corr:.3f} (p={p_val:.4f}, n={n}). "
            + (
                "Statistically significant positive correlation: requirements with higher ambiguity scores are significantly more likely to produce execution failures (p < 0.05)."
                if p_val < 0.05 and corr > 0
                else "No statistically significant correlation observed between ambiguity score and failure occurrence (p >= 0.05)."
            )
        )

        return {
            "correlation": round(corr, 4),
            "p_value": round(p_val, 4),
            "n": n,
            "interpretation": interp,
        }
    except Exception as exc:
        logger.warning("Point-biserial correlation error: %s", exc)
        return _empty_point_biserial_result(f"Calculation error: {exc}")


def _empty_point_biserial_result(reason: str) -> Dict[str, Any]:
    return {
        "correlation": 0.0,
        "p_value": 1.0,
        "n": 0,
        "interpretation": f"Insufficient data for Point-biserial test ({reason}).",
    }


def annotated_vs_baseline_reduction(
    batch_id: str, n_bootstrap: int = 10000, random_seed: int = 42
) -> Dict[str, Any]:
    """
    Compute overall failure-count reduction (annotated vs baseline, paired by task)
    and compute a 95% bootstrap confidence interval on the mean percentage reduction
    by resampling paired differences with replacement for n_bootstrap iterations.

    Returns:
        {mean_reduction_pct, ci_lower, ci_upper, n_task_pairs}
    """
    with get_session() as session:
        runs = session.query(MASRuns).filter(MASRuns.batch_id == batch_id).all()
        doc_ids = sorted(list({r.source_doc_id for r in runs if r.source_doc_id}))

        if not doc_ids:
            return _empty_reduction_result("No MAS runs found for batch_id.")

        paired_differences = []
        baseline_counts = []
        annotated_counts = []

        for doc_id in doc_ids:
            # Query baseline run
            b_run = (
                session.query(MASRuns)
                .filter(
                    MASRuns.batch_id == batch_id,
                    MASRuns.source_doc_id == doc_id,
                    MASRuns.annotated == False,
                )
                .first()
            )
            # Query annotated run
            a_run = (
                session.query(MASRuns)
                .filter(
                    MASRuns.batch_id == batch_id,
                    MASRuns.source_doc_id == doc_id,
                    MASRuns.annotated == True,
                )
                .first()
            )

            if not b_run or not a_run:
                continue

            b_fail_count = (
                session.query(FailureLogs).filter(FailureLogs.run_id == b_run.run_id).count()
            )
            a_fail_count = (
                session.query(FailureLogs).filter(FailureLogs.run_id == a_run.run_id).count()
            )

            baseline_counts.append(b_fail_count)
            annotated_counts.append(a_fail_count)

            # Task percentage reduction
            if b_fail_count > 0:
                pct_red = ((b_fail_count - a_fail_count) / b_fail_count) * 100.0
            else:
                pct_red = 0.0
            paired_differences.append(pct_red)

    return calculate_bootstrap_reduction(paired_differences, n_bootstrap, random_seed)


def calculate_bootstrap_reduction(
    paired_differences: List[float], n_bootstrap: int = 10000, random_seed: int = 42
) -> Dict[str, Any]:
    """Compute mean reduction percentage and 95% bootstrap confidence interval."""
    n_pairs = len(paired_differences)
    if n_pairs == 0:
        return _empty_reduction_result("No complete baseline/annotated task pairs found.")

    arr = np.array(paired_differences)
    mean_reduction = float(np.mean(arr))

    if n_pairs == 1:
        return {
            "mean_reduction_pct": round(mean_reduction, 2),
            "ci_lower": round(mean_reduction, 2),
            "ci_upper": round(mean_reduction, 2),
            "n_task_pairs": 1,
        }

    np.random.seed(random_seed)
    resampled_means = []

    for _ in range(n_bootstrap):
        sample = np.random.choice(arr, size=n_pairs, replace=True)
        resampled_means.append(np.mean(sample))

    ci_lower = float(np.percentile(resampled_means, 2.5))
    ci_upper = float(np.percentile(resampled_means, 97.5))

    return {
        "mean_reduction_pct": round(mean_reduction, 2),
        "ci_lower": round(ci_lower, 2),
        "ci_upper": round(ci_upper, 2),
        "n_task_pairs": n_pairs,
    }


def _empty_reduction_result(reason: str) -> Dict[str, Any]:
    return {
        "mean_reduction_pct": 0.0,
        "ci_lower": 0.0,
        "ci_upper": 0.0,
        "n_task_pairs": 0,
    }
