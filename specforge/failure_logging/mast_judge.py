"""
MAST LLM-as-a-Judge — Analyzes raw MAS framework execution traces and identifies
failure occurrences tagged against the 14 MAST failure modes (Cemri et al., 2025).
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List

import anthropic

from specforge.config import settings
from specforge.failure_logging.mast_taxonomy import MAST_FAILURE_MODES

logger = logging.getLogger(__name__)


def _build_system_prompt() -> str:
    """Build the system prompt containing all 14 MAST failure mode definitions."""
    modes_text = "\n".join(
        f"- [{m['failure_mode_id']}] ({m['category']}) **{m['mode_name']}**: {m['mode_definition']}"
        for m in MAST_FAILURE_MODES
    )

    return f"""You are an expert evaluator analyzing execution traces of Multi-Agent Systems (MAS).
Your task is to identify occurrences of system failures and tag them using the Multi-Agent System Failure Taxonomy (MAST).

## MAST Failure Taxonomy (14 Modes)

{modes_text}

## Evaluation Rules:
1. Carefully analyze the provided execution trace.
2. Identify every distinct failure occurrence in the trace.
3. For each failure, return an object in a JSON array with these keys:
   - "failure_mode_id": exact ID from the taxonomy above (e.g. "FM-1.1")
   - "agent_stage": agent role or phase where failure occurred (e.g. "Coder", "Reviewer", "Architect", "ProductManager")
   - "failure_description": specific explanation of what went wrong in this instance
   - "confidence": confidence score float between 0.0 and 1.0
4. If NO failure is present in the trace, return an EMPTY JSON ARRAY `[]`.
5. Output ONLY valid JSON — no markdown code block fences, no conversational preamble.
"""


def _parse_judge_response(text: str) -> List[Dict[str, Any]]:
    """Parse judge LLM JSON response array."""
    cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.IGNORECASE)
    parsed = json.loads(cleaned.strip())
    if not isinstance(parsed, list):
        raise ValueError(f"Expected JSON list from MAST judge, got {type(parsed)}")
    return parsed


def chunk_trace(trace_text: str, chunk_size: int = 10000, overlap: int = 1000) -> List[str]:
    """Split long execution trace into overlapping text chunks."""
    if len(trace_text) <= chunk_size:
        return [trace_text]

    chunks = []
    start = 0
    while start < len(trace_text):
        end = min(start + chunk_size, len(trace_text))
        chunks.append(trace_text[start:end])
        if end == len(trace_text):
            break
        start = end - overlap
    return chunks


def annotate_trace_with_mast(raw_trace_text: str) -> List[Dict[str, Any]]:
    """
    Analyze raw_trace_text with Claude API and identify MAST failures,
    falling back to heuristic pattern matching if API key is unconfigured.
    """
    if not raw_trace_text or not raw_trace_text.strip():
        return []

    try:
        chunks = chunk_trace(raw_trace_text)
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        system_prompt = _build_system_prompt()

        all_failures: List[Dict[str, Any]] = []

        for idx, chunk in enumerate(chunks):
            user_message = (
                f"Analyze execution trace chunk ({idx+1}/{len(chunks)}):\n"
                f"```\n{chunk}\n```"
            )

            def _call(strict: bool = False) -> str:
                extra = "\nOutput ONLY valid JSON array [ ... ]." if strict else ""
                response = client.messages.create(
                    model=settings.anthropic_model,
                    max_tokens=1024,
                    system=system_prompt + extra,
                    messages=[{"role": "user", "content": user_message}],
                )
                return response.content[0].text

            raw = _call(strict=False)
            try:
                items = _parse_judge_response(raw)
            except (json.JSONDecodeError, ValueError) as exc:
                logger.warning("MAST judge parse failed (%s), retrying with strict prompt...", exc)
                raw = _call(strict=True)
                try:
                    items = _parse_judge_response(raw)
                except (json.JSONDecodeError, ValueError) as exc2:
                    logger.error("Failed to parse MAST judge response: %s", raw)
                    continue

            for item in items:
                if "failure_mode_id" in item:
                    all_failures.append({
                        "failure_mode_id": str(item.get("failure_mode_id", "")),
                        "agent_stage": str(item.get("agent_stage", "Unknown")),
                        "failure_description": str(item.get("failure_description", "")),
                        "confidence": float(item.get("confidence", 1.0)),
                    })

        seen = set()
        deduped = []
        for f in all_failures:
            key = (f["failure_mode_id"], f["agent_stage"], f["failure_description"][:40])
            if key not in seen:
                seen.add(key)
                deduped.append(f)

        return deduped

    except Exception as exc:
        logger.warning("Claude API call for MAST judge failed (%s). Running heuristic trace fallback.", exc)
        failures = []
        lower_trace = raw_trace_text.lower()

        # Heuristic detection for demo trace evaluation when API key is unconfigured
        if any(w in lower_trace for w in ["skipped", "disobey", "failed to implement"]):
            failures.append({
                "failure_mode_id": "FM-1.1",
                "agent_stage": "Coder",
                "failure_description": "Disobeyed task specification constraints during module synthesis.",
                "confidence": 0.92,
            })
        if any(w in lower_trace for w in ["ignored", "plain text"]):
            failures.append({
                "failure_mode_id": "FM-2.5",
                "agent_stage": "Programmer",
                "failure_description": "Ignored input recommendations from peer agent.",
                "confidence": 0.88,
            })
        if any(w in lower_trace for w in ["no unit tests", "no or incomplete", "skipped testing"]):
            failures.append({
                "failure_mode_id": "FM-3.2",
                "agent_stage": "Reviewer",
                "failure_description": "No or incomplete verification of task outcomes.",
                "confidence": 0.85,
            })
        return failures

