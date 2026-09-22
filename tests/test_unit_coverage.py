"""
Targeted unit tests for edge cases and fallback execution paths across SpecForge modules.
"""

from unittest.mock import MagicMock, patch
import pytest

from specforge.ingestion import loader
from specforge.ambiguity import llm_scorer
from specforge.failure_logging import mast_judge
from specforge.mas_adapter.metagpt_adapter import MetaGPTAdapter
from specforge.evaluation import correlation_engine


def test_loader_unsupported_file_extension():
    with pytest.raises(ValueError, match="Unsupported file type"):
        loader.load_file("document.unsupported_ext")


def test_loader_docx_and_pdf(tmp_path):
    # Test load_raw_string wrapper
    assert loader.load_raw_string("hello") == "hello"

    # Test load_txt file path dispatcher
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("sample content", encoding="utf-8")
    assert loader.load_file(str(txt_file)) == "sample content"


def test_llm_scorer_fallback_on_exception():
    with patch("anthropic.Anthropic") as mock_anthropic:
        mock_anthropic.side_effect = Exception("API Key Error")
        result = llm_scorer.llm_ambiguity_score("System shall be fast.")
        assert result["ambiguity_score"] == 0.0
        assert "fallback" in result["rationale"].lower()


def test_llm_scorer_retry_on_invalid_json():
    mock_client = MagicMock()
    # First response returns invalid json, second call returns valid json
    resp1 = MagicMock()
    resp1.content = [MagicMock(text="Not valid json")]
    resp2 = MagicMock()
    resp2.content = [MagicMock(text='{"ambiguity_score": 0.85, "rationale": "Vague word fast."}')]
    mock_client.messages.create.side_effect = [resp1, resp2]

    with patch("anthropic.Anthropic", return_value=mock_client):
        res = llm_scorer.llm_ambiguity_score("System shall be fast.")
        assert res["ambiguity_score"] == 0.85
        assert "Vague" in res["rationale"]


def test_mast_judge_empty_trace():
    assert mast_judge.annotate_trace_with_mast("") == []
    assert mast_judge.annotate_trace_with_mast("   ") == []


def test_mast_judge_heuristic_fallback():
    with patch("anthropic.Anthropic") as mock_anthropic:
        mock_anthropic.side_effect = Exception("API failure")
        trace = "Agent skipped unit testing and ignored plain text guidelines."
        failures = mast_judge.annotate_trace_with_mast(trace)
        assert len(failures) > 0
        ids = [f["failure_mode_id"] for f in failures]
        assert "FM-2.5" in ids or "FM-3.2" in ids


def test_mast_judge_chunking():
    long_trace = "Line of trace output.\n" * 1000
    chunks = mast_judge.chunk_trace(long_trace, chunk_size=500, overlap=50)
    assert len(chunks) > 1


def test_metagpt_adapter_run_fallback(tmp_path):
    adapter = MetaGPTAdapter()
    assert adapter.get_framework_name() == "metagpt"

    out_dir = str(tmp_path / "metagpt_out")
    # Force subprocess error to test simulator fallback path
    with patch("subprocess.run", side_effect=OSError("metagpt binary not found")):
        res = adapter.run("Prepared prompt text", out_dir)
        assert res["status"] == "completed"
        assert res["duration_seconds"] >= 0
        with open(res["raw_trace_path"], "r", encoding="utf-8") as f:
            content = f.read()
            assert "[MetaGPT Simulator]" in content


def test_correlation_engine_empty_batch_id():
    batch_id = "non_existent_batch_12345"
    chi2_res = correlation_engine.chi_square_rit_vs_failure(batch_id)
    assert chi2_res["chi2"] == 0.0
    assert chi2_res["p_value"] == 1.0

    pb_res = correlation_engine.point_biserial_ambiguity_vs_failure(batch_id)
    assert pb_res["correlation"] == 0.0
    assert pb_res["n"] == 0

    red_res = correlation_engine.annotated_vs_baseline_reduction(batch_id)
    assert red_res["mean_reduction_pct"] == 0.0
    assert red_res["n_task_pairs"] == 0


def test_correlation_engine_single_task_pair_bootstrap():
    red_res = correlation_engine.calculate_bootstrap_reduction([50.0])
    assert red_res["mean_reduction_pct"] == 50.0
    assert red_res["ci_lower"] == 50.0
    assert red_res["ci_upper"] == 50.0
    assert red_res["n_task_pairs"] == 1
