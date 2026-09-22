"""
Shared helper for formatting SpecForge AI pre-analysis annotations into task prompts.
"""

from typing import Any, Dict, Optional


def build_annotated_prompt(
    annotated_spec: Optional[Dict[str, Any]], task_description: str
) -> str:
    """
    Build a unified annotated prompt string with SpecForge AI pre-analysis annotations
    prepended to the task description. If annotated_spec is None or empty, returns task_description as-is.
    """
    if not annotated_spec or "requirements" not in annotated_spec:
        return task_description

    reqs = annotated_spec.get("requirements", [])
    high_ambiguity_reqs = [r for r in reqs if r.get("ambiguity_score", 0.0) > 0.6]

    lines = [
        "=== SPECFORGE AI PRE-ANALYSIS ANNOTATIONS ===",
        f"Total Ingested Requirements: {len(reqs)}",
        f"High Ambiguity Count: {len(high_ambiguity_reqs)}",
        "",
        "Requirements Summary & Intent Classifications:",
    ]

    for idx, r in enumerate(reqs, start=1):
        lbl = r.get("rit_label", "Unclassified")
        score = r.get("ambiguity_score", 0.0)
        text = r.get("atomic_unit_text", "")
        lines.append(f"  {idx}. [{lbl}] (Ambiguity: {score:.2f}) {text}")
        reasons = r.get("ambiguity_reasons", [])
        if reasons:
            lines.append(f"     -> WARNINGS: {'; '.join(reasons)}")

    if high_ambiguity_reqs:
        lines.append("")
        lines.append(
            "CRITICAL NOTICE: Pay special attention to requirements flagged with high ambiguity (>0.60). "
            "Clarify or constrain these requirements during specification breakdown."
        )

    lines.append("=== END SPECFORGE ANNOTATIONS ===")
    lines.append("")
    lines.append(task_description)

    return "\n".join(lines)
