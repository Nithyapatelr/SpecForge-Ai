"""
Dashboard helper functions for report transformation, sorting, filtering, and dark UI styling.
"""

from __future__ import annotations
from typing import Any, Dict, List


def process_report_data(report_json: dict) -> dict:
    """
    Extract and format report data for Streamlit display.

    Args:
        report_json: Dict returned from GET /report/{source_doc_id}.

    Returns:
        Dict with total_count, high_ambiguity_count, label_distribution, sorted_reqs, avg_confidence, ambiguity_rate.
    """
    summary = report_json.get("summary", {})
    requirements = report_json.get("requirements", [])

    # Sort requirements by ambiguity_score descending
    sorted_reqs = sorted(
        requirements, key=lambda r: r.get("ambiguity_score", 0.0), reverse=True
    )

    total_count = summary.get("total_requirements", len(requirements))
    high_ambiguity_count = summary.get("high_ambiguity_count", 0)

    confidences = [r.get("rit_confidence", 0.0) for r in requirements if "rit_confidence" in r]
    avg_confidence = round(sum(confidences) / len(confidences), 2) if confidences else 0.0
    ambiguity_rate = round((high_ambiguity_count / total_count * 100), 1) if total_count > 0 else 0.0

    return {
        "total_count": total_count,
        "high_ambiguity_count": high_ambiguity_count,
        "ambiguity_rate": ambiguity_rate,
        "avg_confidence": avg_confidence,
        "label_distribution": summary.get("label_distribution", {}),
        "requirements": sorted_reqs,
    }


def calculate_overall_reduction(runs: List[dict]) -> float:
    """
    Calculate average overall failure reduction percentage across completed experiment pairs.
    """
    by_doc: Dict[str, Dict[str, int]] = {}
    for r in runs:
        doc = r.get("source_doc_id")
        if not doc or r.get("status") != "completed":
            continue
        if doc not in by_doc:
            by_doc[doc] = {}
        if r.get("annotated"):
            by_doc[doc]["annotated"] = r.get("failure_count", 0)
        else:
            by_doc[doc]["baseline"] = r.get("failure_count", 0)

    reductions = []
    for doc, pair in by_doc.items():
        if "baseline" in pair and "annotated" in pair:
            b = pair["baseline"]
            a = pair["annotated"]
            if b > 0:
                reductions.append((b - a) / b * 100)
            else:
                reductions.append(0.0)

    if not reductions:
        return 0.0

    return round(sum(reductions) / len(reductions), 1)


def get_ambiguity_color(score: float) -> str:
    """Return dark mode status badge background color based on ambiguity score."""
    if score >= 0.6:
        return "#EF4444"  # Bright Red
    elif score >= 0.3:
        return "#F59E0B"  # Amber
    return "#10B981"  # Emerald Green
