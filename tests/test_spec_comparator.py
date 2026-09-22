"""
Unit tests for specification quality comparator module.
"""

import os
import pytest
from specforge.comparison.spec_quality_comparator import compare_specifications


def test_spec_quality_comparator_completeness_and_structure():
    """
    Test that compare_specifications correctly identifies that a complete and structured
    specification scores higher on completeness and structure metrics than a partial/unstructured one.
    """
    # Hand-built ground-truth checklist (5 items)
    checklist = [
        "User login endpoint using email and password credentials",
        "JWT token generation for session authorization",
        "Bcrypt password hashing for password security",
        "Rate limiting on login endpoint against brute force attacks",
        "Error handling and invalid credentials messaging",
    ]

    # Specification A: Highly complete and structured (SpecForge style)
    spec_a = {
        "source_doc_id": "doc_complete",
        "summary": {"total_requirements": 5},
        "requirements": [
            {
                "requirement_id": "r1",
                "atomic_unit_text": "The system shall provide a user login endpoint using email and password credentials.",
                "rit_label": "Data Contract",
                "rit_confidence": 0.95,
                "ambiguity_score": 0.0,
            },
            {
                "requirement_id": "r2",
                "atomic_unit_text": "The system shall generate JWT tokens for session authorization upon login.",
                "rit_label": "Behavioral Rule",
                "rit_confidence": 0.90,
                "ambiguity_score": 0.0,
            },
            {
                "requirement_id": "r3",
                "atomic_unit_text": "The system shall use bcrypt password hashing for password security.",
                "rit_label": "Security Constraint",
                "rit_confidence": 0.92,
                "ambiguity_score": 0.0,
            },
            {
                "requirement_id": "r4",
                "atomic_unit_text": "The system shall enforce rate limiting on login endpoint against brute force attacks.",
                "rit_label": "Operational Policy",
                "rit_confidence": 0.88,
                "ambiguity_score": 0.0,
            },
            {
                "requirement_id": "r5",
                "atomic_unit_text": "The system shall return error handling and invalid credentials messaging on login failure.",
                "rit_label": "Acceptance Condition",
                "rit_confidence": 0.91,
                "ambiguity_score": 0.0,
            },
        ],
    }

    # Specification B: Incomplete, unstructured, and ambiguous (Plain text style)
    spec_b = {
        "raw_text": (
            "System Idea:\n"
            "Build a login app quickly. Users log in with email. "
            "It should perform fast and be user friendly."
        ),
        "functional_requirements": [
            "Build a login app quickly.",
            "Users log in with email.",
        ],
    }

    result = compare_specifications(spec_a, spec_b, checklist)

    sf_metrics = result["specforge_metrics"]
    mare_metrics = result["mare_metrics"]

    # Assert Spec A (complete & structured) scores higher on completeness than Spec B
    assert sf_metrics["completeness_score"] > mare_metrics["completeness_score"]
    assert sf_metrics["completeness_score"] == 1.0

    # Assert Spec A scores higher on structure than Spec B
    assert sf_metrics["structure_score"] > mare_metrics["structure_score"]
    assert sf_metrics["structure_score"] == 1.0

    # Assert Spec A (precise requirements) has lower ambiguity score than Spec B (vague quantifiers)
    assert sf_metrics["average_ambiguity_score"] < mare_metrics["average_ambiguity_score"]
    assert mare_metrics["total_ambiguity_smells"] > 0


def test_run_mare_on_task(tmp_path):
    """
    Test that run_mare_on_task executes the MARE 5-agent pipeline and writes JSON and TXT artifacts.
    """
    from specforge.comparison.mare_runner import run_mare_on_task

    out_dir = str(tmp_path / "mare_out")
    result = run_mare_on_task("Build a simple calculator app", out_dir)

    assert result["status"] == "completed"
    assert "specification" in result
    assert result["specification"]["title"].startswith("SRS for")
    assert len(result["specification"]["functional_requirements"]) > 0
    assert os.path.exists(result["artifact_path"])

