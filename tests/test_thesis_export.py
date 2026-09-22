"""
Unit tests for thesis & publication artifact export generator.
"""

import os
from specforge.thesis_export.generate_thesis_artifacts import export_all_thesis_artifacts


def test_export_all_thesis_artifacts(tmp_path):
    out_dir = str(tmp_path / "test_artifacts")
    res = export_all_thesis_artifacts(batch_id="eval_batch_v1", output_dir=out_dir)

    assert res["status"] == "success"
    assert os.path.exists(out_dir)

    expected_filenames = [
        "figure_1_chi_square_rit_vs_mast.png",
        "figure_1_chi_square_rit_vs_mast.svg",
        "figure_2_point_biserial_ambiguity.png",
        "figure_2_point_biserial_ambiguity.svg",
        "figure_3_bootstrap_ci_reduction.png",
        "figure_3_bootstrap_ci_reduction.svg",
        "figure_4_mare_head_to_head.png",
        "figure_4_mare_head_to_head.svg",
        "table_1_statistical_correlations.tex",
        "table_2_head_to_head_mare.tex",
        "table_3_mast_failure_breakdown.tex",
        "manifest.md",
    ]

    for fname in expected_filenames:
        filepath = os.path.join(out_dir, fname)
        assert os.path.isfile(filepath), f"Expected artifact {fname} missing!"
        assert os.path.getsize(filepath) > 0, f"Artifact {fname} is empty!"
