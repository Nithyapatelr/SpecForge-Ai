"""
Evaluation Report Builder — Assembles statistical analyses into a JSON report
and renders a Markdown report for thesis inclusion.
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict

from specforge.evaluation.correlation_engine import (
    annotated_vs_baseline_reduction,
    chi_square_rit_vs_failure,
    point_biserial_ambiguity_vs_failure,
)


def build_evaluation_report(batch_id: str) -> Dict[str, Any]:
    """
    Execute all three evaluation analyses for a batch and assemble into a JSON-serializable dictionary.

    Args:
        batch_id: Unique batch identifier string.

    Returns:
        JSON-serializable report dictionary.
    """
    chi2_res = chi_square_rit_vs_failure(batch_id)
    pb_res = point_biserial_ambiguity_vs_failure(batch_id)
    red_res = annotated_vs_baseline_reduction(batch_id)

    report = {
        "batch_id": batch_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "n_task_pairs": red_res["n_task_pairs"],
            "mean_reduction_pct": red_res["mean_reduction_pct"],
            "bootstrap_ci_95": [red_res["ci_lower"], red_res["ci_upper"]],
            "ambiguity_correlation_r": pb_res["correlation"],
            "ambiguity_correlation_p": pb_res["p_value"],
            "chi2_stat": chi2_res["chi2"],
            "chi2_p_value": chi2_res["p_value"],
        },
        "chi_square_analysis": chi2_res,
        "point_biserial_analysis": pb_res,
        "failure_reduction_analysis": red_res,
    }

    return report


def render_report_markdown(report: Dict[str, Any]) -> str:
    """
    Render an evaluation report dictionary as a publication-grade Markdown document
    suitable for direct inclusion in a thesis evaluation chapter.

    Args:
        report: Dictionary returned by build_evaluation_report.

    Returns:
        Formatted Markdown string.
    """
    batch_id = report.get("batch_id", "Unknown")
    gen_time = report.get("generated_at", "")
    summary = report.get("summary", {})

    chi2 = report.get("chi_square_analysis", {})
    pb = report.get("point_biserial_analysis", {})
    red = report.get("failure_reduction_analysis", {})

    n_pairs = summary.get("n_task_pairs", 0)

    lines = [
        f"# Chapter 7: Empirical Evaluation & Statistical Analysis",
        f"**Evaluation Batch ID:** `{batch_id}`  ",
        f"**Report Generated:** `{gen_time}`  ",
        f"**Sample Size:** N = {n_pairs} Paired Benchmark Tasks  ",
        "",
        "## Executive Summary",
        f"- **Mean MAST Failure Reduction:** **{summary.get('mean_reduction_pct', 0.0):.1f}%**",
        f"- **95% Bootstrap Confidence Interval:** **[{red.get('ci_lower', 0.0):.1f}%, {red.get('ci_upper', 0.0):.1f}%]** (10,000 iterations)",
        f"- **Ambiguity vs Failure Correlation:** r_pb = **{pb.get('correlation', 0.0):.3f}** (p = **{pb.get('p_value', 1.0):.4f}**)",
        f"- **RIT Category vs Failure Independence:** χ² = **{chi2.get('chi2', 0.0):.2f}** (p = **{chi2.get('p_value', 1.0):.4f}**, dof = {chi2.get('dof', 0)})",
        "",
    ]

    # Sample size caveat box for intellectual honesty
    if n_pairs <= 30:
        lines.extend([
            "> [!WARNING]",
            "> **Sample Size & Generalizability Caveat**",
            f"> This evaluation batch comprises N = {n_pairs} paired benchmark task executions. Given this sample size, statistical findings are presented as directional and exploratory evidence rather than conclusive population inference. Future work scaling to larger enterprise task suites will further narrow bootstrap confidence bounds.",
            "",
        ])

    # Section 1: Failure Reduction Analysis
    lines.extend([
        "## 7.1 Paired Failure Reduction & Bootstrap Confidence Bounds",
        "To quantify the impact of SpecForge's pre-analysis annotations on multi-agent execution reliability, we compare baseline (unmodified specification) against SpecForge-annotated runs across paired benchmark tasks.",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| **Paired Task Count (N)** | `{n_pairs}` |",
        f"| **Mean Failure Reduction** | `{red.get('mean_reduction_pct', 0.0):.2f}%` |",
        f"| **95% Bootstrap CI (2.5% - 97.5%)** | `[{red.get('ci_lower', 0.0):.2f}%, {red.get('ci_upper', 0.0):.2f}%]` |",
        "",
    ])

    # Section 2: Ambiguity Correlation Analysis
    lines.extend([
        "## 7.2 Requirement Ambiguity Smell Correlation (Point-Biserial Test)",
        "We evaluate whether requirement-level ambiguity scores (measured continuous heuristic smell score, 0.0–1.0) correlate with downstream multi-agent system execution failures (binary failure indicator).",
        "",
        f"- **Point-Biserial Correlation (r_pb):** `{pb.get('correlation', 0.0):.4f}`",
        f"- **Statistical Significance (p-value):** `{pb.get('p_value', 1.0):.4f}`",
        f"- **Requirement Sample Size (n):** `{pb.get('n', 0)}`",
        f"- **Interpretation:** {pb.get('interpretation', 'N/A')}",
        "",
    ])

    # Section 3: RIT Category vs Failure Type Contingency
    lines.extend([
        "## 7.3 Requirement Intent Taxonomy (RIT) vs MAST Failure Independence (Chi-Square Test)",
        "We test whether specific Requirement Intent Taxonomy (RIT) categories exhibit differential vulnerability to distinct MAST failure modes.",
        "",
        f"- **Chi-Square Statistic (χ²):** `{chi2.get('chi2', 0.0):.4f}`",
        f"- **Degrees of Freedom (dof):** `{chi2.get('dof', 0)}`",
        f"- **Asymptotic Significance (p-value):** `{chi2.get('p_value', 1.0):.4f}`",
        f"- **Interpretation:** {chi2.get('interpretation', 'N/A')}",
        "",
    ])

    # Contingency Table Breakdown
    ct = chi2.get("contingency_table", {})
    if ct:
        lines.extend([
            "### Contingency Matrix (RIT Label vs MAST Failure Category)",
            "",
            "| RIT Category | Specification Issues | Inter-Agent Misalignment | Task Verification |",
            "|---|---|---|---|",
        ])
        for rit, cats in ct.items():
            s_val = cats.get("Specification Issues", 0)
            m_val = cats.get("Inter-Agent Misalignment", 0)
            v_val = cats.get("Task Verification", 0)
            lines.append(f"| **{rit}** | {s_val} | {m_val} | {v_val} |")
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    b_id = sys.argv[1] if len(sys.argv) > 1 else "demo_batch"
    rep = build_evaluation_report(b_id)
    md = render_report_markdown(rep)
    print(md)
