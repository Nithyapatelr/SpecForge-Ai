"""
Tests for dashboard helper functions.
"""

from scripts.dashboard_helpers import process_report_data


def test_process_report_data_sorting():
    """Verify requirements are sorted by ambiguity_score descending."""
    mock_report = {
        "source_doc_id": "doc-1",
        "summary": {
            "total_requirements": 3,
            "label_distribution": {"Behavioral Rule": 2, "Data Contract": 1},
            "high_ambiguity_count": 1,
        },
        "requirements": [
            {"atomic_unit_text": "A", "ambiguity_score": 0.2},
            {"atomic_unit_text": "B", "ambiguity_score": 0.8},
            {"atomic_unit_text": "C", "ambiguity_score": 0.5},
        ],
    }

    res = process_report_data(mock_report)

    assert res["total_count"] == 3
    assert res["high_ambiguity_count"] == 1
    assert res["requirements"][0]["atomic_unit_text"] == "B"
    assert res["requirements"][1]["atomic_unit_text"] == "C"
    assert res["requirements"][2]["atomic_unit_text"] == "A"
