"""
Preprocessing — atomic requirement unit segmentation.

Strategy:
1. Strip line numbers (e.g. "1. ", "12. ") before segmentation.
2. Use spaCy's sentence boundary detection (en_core_web_sm) to split text
   into sentences.
3. For each sentence, apply a rule-based compound-sentence splitter:
   If a sentence contains a coordinating conjunction ("and", "as well as")
   joining two verb phrases that each begin with a modal verb ("shall",
   "must", "will", "should"), split into two separate atomic units.
"""

from __future__ import annotations

import logging
import re
from typing import Callable

logger = logging.getLogger(__name__)

_nlp = None


def _get_nlp():
    global _nlp
    if _nlp is None:
        import spacy  # type: ignore

        try:
            _nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model 'en_core_web_sm' not found.")
            raise
    return _nlp


_COMPOUND_PATTERN = re.compile(
    r"\s+(?:and|as well as)\s+(shall|must|will|should)\b",
    re.IGNORECASE,
)

# Pattern to strip leading numbering like "1.", "14.", "1. ", "Header Text"
_NUMBERING_PATTERN = re.compile(r"^\d+[\.\)]\s*")


def _split_compound_sentence(sentence: str) -> list[str]:
    """Split a sentence at a coordinating conjunction between two modal-verb phrases."""
    match = _COMPOUND_PATTERN.search(sentence)
    if match is None:
        return [sentence]

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

    second_clause = f"{subject} {second_verb_phrase}".strip()

    if not first_clause.endswith("."):
        first_clause += "."
    if not second_clause.endswith("."):
        second_clause += "."

    return [first_clause, second_clause]


def segment_into_atomic_units(
    raw_text: str,
    llm_fallback: Callable[[str], list[str]] | None = None,
) -> list[str]:
    """Segment *raw_text* into a list of atomic requirement strings."""
    from specforge.config import settings

    nlp = _get_nlp()

    # Pre-clean: split raw_text line by line and strip leading list numbers (e.g. "1. ")
    cleaned_lines = []
    for line in raw_text.splitlines():
        line_str = line.strip()
        if not line_str or line_str.lower().startswith("functional requirements") or line_str.lower().startswith("hospital appointment"):
            continue
        line_str = _NUMBERING_PATTERN.sub("", line_str).strip()
        if line_str:
            cleaned_lines.append(line_str)

    clean_text = " ".join(cleaned_lines)
    doc = nlp(clean_text)

    atomic_units: list[str] = []

    for sent in doc.sents:
        sentence = sent.text.strip()
        if not sentence:
            continue

        parts = _split_compound_sentence(sentence)

        if len(parts) == 1 and settings.use_llm_segmentation and llm_fallback:
            parts = llm_fallback(sentence) or [sentence]

        for part in parts:
            cleaned = part.strip()
            if cleaned and len(cleaned) > 5:  # filter out residual noise
                atomic_units.append(cleaned)

    return atomic_units
