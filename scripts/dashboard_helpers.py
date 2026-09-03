"""
Dashboard helper functions for report transformation, sorting, and filtering.
"""

from __future__ import annotations


def process_report_data(report_json: dict) -> dict:
    """
    Extract and format report data for Streamlit display.

    Args:
        report_json: Dict returned from GET /report/{source_doc_id}.

    Returns:
        Dict with total_count, high_ambiguity_count, label_distribution, sorted_reqs.
    """
    summary = report_json.get("summary", {})
    requirements = report_json.get("requirements", [])

    # Sort requirements by ambiguity_score descending
    sorted_reqs = sorted(
        requirements, key=lambda r: r.get("ambiguity_score", 0.0), reverse=True
    )

    return {
        "total_count": summary.get("total_requirements", len(requirements)),
        "high_ambiguity_count": summary.get("high_ambiguity_count", 0),
        "label_distribution": summary.get("label_distribution", {}),
        "requirements": sorted_reqs,
    }
