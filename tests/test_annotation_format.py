"""
Unit tests for shared annotation format module.
"""

from specforge.mas_adapter.annotation_format import build_annotated_prompt


def test_build_annotated_prompt_none_or_empty():
    prompt = "Develop a web app"
    assert build_annotated_prompt(None, prompt) == prompt
    assert build_annotated_prompt({}, prompt) == prompt
    assert build_annotated_prompt({"source_doc_id": "1"}, prompt) == prompt


def test_build_annotated_prompt_with_requirements():
    annotated_spec = {
        "requirements": [
            {
                "atomic_unit_text": "Must respond quickly.",
                "rit_label": "Acceptance Condition",
                "ambiguity_score": 0.9,
                "ambiguity_reasons": ["vague_quantifier: quickly"],
            },
            {
                "atomic_unit_text": "API endpoint shall return JSON.",
                "rit_label": "Data Contract",
                "ambiguity_score": 0.0,
            },
        ]
    }
    result = build_annotated_prompt(annotated_spec, "Build API")
    assert "=== SPECFORGE AI PRE-ANALYSIS ANNOTATIONS ===" in result
    assert "Total Ingested Requirements: 2" in result
    assert "High Ambiguity Count: 1" in result
    assert "CRITICAL NOTICE" in result
    assert "Build API" in result
