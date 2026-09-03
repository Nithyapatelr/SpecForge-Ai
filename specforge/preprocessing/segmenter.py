"""
Preprocessing — atomic requirement unit segmentation.

Strategy:
1. Use spaCy's sentence boundary detection (en_core_web_sm) to split text
   into sentences.  spaCy handles abbreviations, decimal numbers, and
   parenthetical text far more reliably than a naive period-split.

2. For each sentence, apply a rule-based compound-sentence splitter:
   If a sentence contains a coordinating conjunction ("and", "as well as")
   joining two verb phrases that each begin with a modal verb ("shall",
   "must", "will", "should"), split into two separate atomic units.
   This catches requirements like:
     "The system shall log the user in and shall send a confirmation email."
   → ["The system shall log the user in.", "The system shall send a confirmation email."]

3. Optionally (USE_LLM_SEGMENTATION=true in .env), fall back to Claude for
   ambiguous compound sentences.  Disabled by default so tests need no API key.
"""

from __future__ import annotations

import re
import logging
from typing import Callable

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# spaCy lazy loader — avoids loading the model at import time (speeds up tests)
# ---------------------------------------------------------------------------
_nlp = None


def _get_nlp():
    global _nlp
    if _nlp is None:
        import spacy  # type: ignore

        try:
            _nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning(
                "spaCy model 'en_core_web_sm' not found. "
                "Run: python -m spacy download en_core_web_sm"
            )
            raise
    return _nlp


# ---------------------------------------------------------------------------
# Modal-verb compound splitter
# ---------------------------------------------------------------------------

# Matches " and shall|must|will|should " or " as well as shall|must|… "
_COMPOUND_PATTERN = re.compile(
    r"\s+(?:and|as well as)\s+(shall|must|will|should)\b",
    re.IGNORECASE,
)

_MODAL_VERBS = {"shall", "must", "will", "should"}


def _split_compound_sentence(sentence: str) -> list[str]:
    """
    Split a sentence at a coordinating conjunction between two modal-verb phrases.

    Only splits when the conjunction is followed by a modal verb, which strongly
    indicates a second independent requirement clause (not a list of nouns or
    adjectives).

    Returns a list with one element (unchanged) or two elements (split).
    """
    match = _COMPOUND_PATTERN.search(sentence)
    if match is None:
        return [sentence]

    # Find the subject of the first clause — we reuse it for the second clause.
    # Simple heuristic: everything up to the first modal verb is the shared subject.
    first_modal_match = re.search(
        r"\b(shall|must|will|should)\b", sentence, re.IGNORECASE
    )
    if first_modal_match is None:
        return [sentence]

    subject = sentence[: first_modal_match.start()].strip()

    split_start = match.start()
    conjunction_end = match.end()

    first_clause = sentence[:split_start].strip().rstrip(",")
    second_verb_phrase = sentence[conjunction_end - len(match.group(1)):].strip()

    # Reconstruct the second atomic unit with the shared subject
    second_clause = f"{subject} {second_verb_phrase}".strip()

    # Ensure both parts end with a period
    if not first_clause.endswith("."):
        first_clause += "."
    if not second_clause.endswith("."):
        second_clause += "."

    return [first_clause, second_clause]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def segment_into_atomic_units(
    raw_text: str,
    llm_fallback: Callable[[str], list[str]] | None = None,
) -> list[str]:
    """
    Segment *raw_text* into a list of atomic requirement strings.

    Args:
        raw_text:     One or more requirement sentences, possibly compound.
        llm_fallback: Optional callable that accepts a sentence and returns a
                      list of atomic units.  Called only when
                      USE_LLM_SEGMENTATION is True (injected by service layer).

    Returns:
        A list of cleaned, atomic requirement strings.  Each element is a
        single, indivisible requirement suitable for classification.
    """
    from specforge.config import settings

    nlp = _get_nlp()
    doc = nlp(raw_text)

    atomic_units: list[str] = []

    for sent in doc.sents:
        sentence = sent.text.strip()
        if not sentence:
            continue

        parts = _split_compound_sentence(sentence)

        # LLM fallback for multi-part sentences the rule didn't split
        if len(parts) == 1 and settings.use_llm_segmentation and llm_fallback:
            parts = llm_fallback(sentence) or [sentence]

        for part in parts:
            cleaned = part.strip()
            if cleaned:
                atomic_units.append(cleaned)

    return atomic_units
