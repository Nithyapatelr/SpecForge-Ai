"""
RIT Intent Classifier — SpecForge's primary research contribution.

Uses a few-shot Claude prompt to classify an atomic requirement into one of
the six top-level RIT categories.  Returns structured JSON with the label,
confidence, and a short rationale.
"""

from __future__ import annotations

import json
import logging
import re

import anthropic

from specforge.classification.rit_taxonomy import RIT_CATEGORIES
from specforge.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Few-shot examples (one per top-level category)
# ---------------------------------------------------------------------------

FEW_SHOT_EXAMPLES: list[dict] = [
    {
        "requirement": "When a patient cancels an appointment less than 24 hours in advance, the system shall charge the cancellation fee.",
        "label_name": "Behavioral Rule",
        "confidence": 0.97,
        "rationale": "Contains an explicit condition ('less than 24 hours') and a triggered system action ('charge fee').",
    },
    {
        "requirement": "An appointment moves from 'Scheduled' to 'Confirmed' once the doctor accepts it.",
        "label_name": "State Transition",
        "confidence": 0.96,
        "rationale": "Names two discrete states (Scheduled, Confirmed) and the event that causes the transition.",
    },
    {
        "requirement": "Only users with the 'Senior Doctor' role shall be permitted to approve prescriptions for controlled substances.",
        "label_name": "Actor Permission",
        "confidence": 0.95,
        "rationale": "Explicitly states which role (Senior Doctor) is authorised to perform a specific action (approve prescriptions).",
    },
    {
        "requirement": "The patient's date-of-birth field must be stored in ISO 8601 format and must not be a future date.",
        "label_name": "Data Contract",
        "confidence": 0.94,
        "rationale": "Defines the format and validation rule for a specific data field.",
    },
    {
        "requirement": "The system shall send appointment reminders via the Twilio SMS API within 60 seconds of confirmation.",
        "label_name": "Integration Constraint",
        "confidence": 0.93,
        "rationale": "Specifies interaction with an external system (Twilio) across a system boundary.",
    },
    {
        "requirement": "The appointment booking page must load in under 2 seconds for 95% of requests under 100 concurrent users.",
        "label_name": "Acceptance Condition",
        "confidence": 0.96,
        "rationale": "Contains a measurable, testable threshold (2 seconds, 95%, 100 users).",
    },
]


def _build_system_prompt() -> str:
    """Build the system prompt listing all RIT categories with definitions."""
    # Only include top-level categories in the system prompt for clarity
    top_level = [c for c in RIT_CATEGORIES if c.get("parent_category") is None]
    cats = "\n".join(
        f"- **{c['label_name']}**: {c['label_definition']}"
        for c in top_level
    )

    examples_text = "\n".join(
        f'Requirement: "{ex["requirement"]}"\n'
        f'Output: {{"label_name": "{ex["label_name"]}", "confidence": {ex["confidence"]}, "rationale": "{ex["rationale"]}"}}'
        for ex in FEW_SHOT_EXAMPLES
    )

    return f"""You are an expert requirements engineer classifying software requirement sentences into the Requirement Intent Taxonomy (RIT).

## RIT Categories

{cats}

## Classification Rules
- Choose EXACTLY ONE label from the categories above.
- Output ONLY valid JSON — no markdown fences, no preamble, no trailing text.
- Format: {{"label_name": "<category name>", "confidence": <0.0–1.0>, "rationale": "<one sentence>"}}
- confidence must be a float between 0.0 and 1.0.

## Examples

{examples_text}"""


def _parse_response(text: str) -> dict:
    """
    Parse the model's text response into a dict, stripping markdown fences
    if present.  Raises ValueError if JSON is malformed.
    """
    # Strip ```json ... ``` or ``` ... ``` fences if present
    cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.IGNORECASE)
    return json.loads(cleaned.strip())


def classify_requirement(atomic_unit_text: str) -> dict:
    """
    Classify a single atomic requirement sentence using the Claude API.

    Args:
        atomic_unit_text: A single, atomic requirement sentence.

    Returns:
        dict with keys: label_name (str), confidence (float), rationale (str).

    Raises:
        ValueError: if the API response cannot be parsed after one retry.
        anthropic.APIError: on network/auth failures.
    """
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    system_prompt = _build_system_prompt()
    user_message = f'Classify this requirement:\n"{atomic_unit_text}"'

    def _call(strict: bool = False) -> str:
        extra = (
            "\n\nIMPORTANT: Output ONLY the raw JSON object. No markdown, no explanation."
            if strict
            else ""
        )
        response = client.messages.create(
            model=settings.anthropic_model,
            max_tokens=256,
            system=system_prompt + extra,
            messages=[{"role": "user", "content": user_message}],
        )
        return response.content[0].text

    # First attempt
    raw = _call(strict=False)
    try:
        result = _parse_response(raw)
    except (json.JSONDecodeError, ValueError) as exc:
        logger.warning("First parse failed (%s), retrying with strict prompt…", exc)
        raw = _call(strict=True)
        try:
            result = _parse_response(raw)
        except (json.JSONDecodeError, ValueError) as exc2:
            raise ValueError(
                f"Could not parse classifier response after retry: {raw!r}"
            ) from exc2

    # Validate required keys
    for key in ("label_name", "confidence", "rationale"):
        if key not in result:
            raise ValueError(f"Missing key '{key}' in classifier response: {result}")

    result["confidence"] = float(result["confidence"])
    return result
