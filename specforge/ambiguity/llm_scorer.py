"""
LLM-based ambiguity scorer using Claude API.
"""

from __future__ import annotations

import json
import logging
import re

import anthropic

from specforge.config import settings

logger = logging.getLogger(__name__)


def _parse_llm_response(text: str) -> dict:
    """Parse JSON output from Claude response."""
    cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.IGNORECASE)
    return json.loads(cleaned.strip())


def llm_ambiguity_score(text: str) -> dict:
    """
    Ask Claude to rate text ambiguity on 0.0-1.0 scale with rationale.

    Returns:
        dict with:
          - ambiguity_score (float)
          - rationale (str)
    """
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    system_prompt = (
        "You are an expert requirements engineer evaluating requirement clarity.\n"
        "Rate the ambiguity of the requirement sentence on a scale from 0.0 (perfectly clear, testable, precise) "
        "to 1.0 (extremely vague, subjective, ambiguous).\n"
        "Return ONLY valid JSON matching this schema:\n"
        '{"ambiguity_score": float, "rationale": "short explanation"}\n'
        "Do NOT include markdown fences, preamble, or commentary."
    )

    user_prompt = f'Rate ambiguity for:\n"{text}"'

    def _call(strict: bool = False) -> str:
        extra = "\n\nIMPORTANT: Return ONLY raw JSON object." if strict else ""
        response = client.messages.create(
            model=settings.anthropic_model,
            max_tokens=256,
            system=system_prompt + extra,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return response.content[0].text

    raw = _call(strict=False)
    try:
        res = _parse_llm_response(raw)
    except Exception as exc:
        logger.warning("LLM ambiguity parse failed (%s), retrying...", exc)
        raw = _call(strict=True)
        res = _parse_llm_response(raw)

    return {
        "ambiguity_score": float(res.get("ambiguity_score", 0.5)),
        "rationale": str(res.get("rationale", "LLM evaluation.")),
    }
