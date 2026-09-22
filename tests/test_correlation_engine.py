"""
Unit tests for correlation engine and report builder using synthetic data with engineered signals.
"""

import pytest
from specforge.evaluation.correlation_engine import (
    _compute_chi_square_from_dict,
    calculate_bootstrap_reduction,
    calculate_point_biserial_stats,
)
from specforge.evaluation.report_builder import build_evaluation_report, render_report_markdown


def test_point_biserial_detects_engineered_ambiguity_signal():
    """
    Construct synthetic requirements where high ambiguity scores strongly co-occur
    with failures (1) and low ambiguity scores co-occur with non-failures (0).
    Assert that calculate_point_biserial_stats detects a strong, positive, statistically significant correlation.
    """
    # High ambiguity scores -> failure = 1
    high_ambiguity = [0.75, 0.80, 0.85, 0.90, 0.95, 1.00, 0.88, 0.92]
    high_failures = [1, 1, 1, 1, 1, 1, 1, 1]

    # Low ambiguity scores -> failure = 0
    low_ambiguity = [0.00, 0.05, 0.10, 0.12, 0.15, 0.20, 0.08, 0.05]
    low_failures = [0, 0, 0, 0, 0, 0, 0, 0]

    ambiguity_scores = high_ambiguity + low_ambiguity
    failure_flags = high_failures + low_failures

    res = calculate_point_biserial_stats(ambiguity_scores, failure_flags)

    assert res["n"] == 16
    assert res["correlation"] > 0.85, f"Expected strong positive correlation, got {res['correlation']}"
    assert res["p_value"] < 0.01, f"Expected p < 0.01, got {res['p_value']}"
    assert "Statistically significant positive correlation" in res["interpretation"]


def test_chi_square_detects_engineered_rit_failure_association():
    """
    Construct synthetic contingency data where specific RIT categories associate exclusively
    with specific MAST failure types.
    Assert that _compute_chi_square_from_dict detects significant non-independence (p < 0.001).
    """
    contingency_dict = {
        "Behavioral Rule": {"Specification Issues": 30, "Inter-Agent Misalignment": 0, "Task Verification": 0},
        "State Transition": {"Specification Issues": 0, "Inter-Agent Misalignment": 35, "Task Verification": 0},
        "Acceptance Condition": {"Specification Issues": 0, "Inter-Agent Misalignment": 0, "Task Verification": 40},
        "Actor Permission": {"Specification Issues": 0, "Inter-Agent Misalignment": 0, "Task Verification": 0},
        "Data Contract": {"Specification Issues": 0, "Inter-Agent Misalignment": 0, "Task Verification": 0},
        "Integration Constraint": {"Specification Issues": 0, "Inter-Agent Misalignment": 0, "Task Verification": 0},
    }

    res = _compute_chi_square_from_dict(contingency_dict)

    assert res["chi2"] > 50.0
    assert res["p_value"] < 0.001
    assert res["dof"] > 0
    assert "Statistically significant association detected" in res["interpretation"]


def test_bootstrap_ci_bounds_contain_true_mean_reduction():
    """
    Construct synthetic paired differences centered around a known mean of 50.0%.
    Assert bootstrap CI bounds correctly surround the sample mean.
    """
    paired_differences = [45.0, 50.0, 55.0, 48.0, 52.0, 50.0, 46.0, 54.0]
    # Sample mean = 400 / 8 = 50.0

    res = calculate_bootstrap_reduction(paired_differences, n_bootstrap=5000, random_seed=42)

    assert res["n_task_pairs"] == 8
    assert res["mean_reduction_pct"] == 50.0
    assert res["ci_lower"] < 50.0 < res["ci_upper"]
    assert res["ci_lower"] >= 40.0
    assert res["ci_upper"] <= 60.0


def test_build_evaluation_report_and_markdown_rendering():
    """
    Test report builder and markdown renderer with sample size caveat.
    """
    report = build_evaluation_report(batch_id="test_demo_batch")
    assert "summary" in report
    assert "chi_square_analysis" in report
    assert "point_biserial_analysis" in report
    assert "failure_reduction_analysis" in report

    md_text = render_report_markdown(report)
    assert "# Chapter 7: Empirical Evaluation & Statistical Analysis" in md_text
    assert "test_demo_batch" in md_text
    # Verify presence of sample size caveat box
    assert "Sample Size & Generalizability Caveat" in md_text
