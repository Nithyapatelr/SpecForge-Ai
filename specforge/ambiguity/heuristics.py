"""
Heuristic ambiguity scorer for software requirements ("requirements smells").

Checks for:
1. Vague quantifiers / adjectives with no measurable value.
2. Passive voice without a named actor.
3. Missing measurable acceptance value (implying a threshold without numbers).
"""

import re

VAGUE_QUANTIFIERS = [
    "fast",
    "quickly",
    "scalable",
    "user-friendly",
    "user friendly",
    "several",
    "appropriate",
    "as needed",
    "efficient",
    "efficiently",
    "flexible",
    "robust",
    "seamless",
    "seamlessly",
    "intuitive",
    "easy",
    "easily",
    "timely",
    "optimal",
    "optimally",
    "adequate",
    "adequately",
]

# Patterns for passive voice without clear actor (e.g. "will be processed", "shall be sent")
PASSIVE_VOICE_PATTERN = re.compile(
    r"\b(shall|will|must|is|are|was|were|be|been|being)\s+([a-z]+ed)\b",
    re.IGNORECASE,
)


def heuristic_ambiguity_score(text: str) -> dict:
    """
    Compute heuristic ambiguity score (0.0 to 1.0) and identified smell reasons.

    Args:
        text: Requirement sentence text.

    Returns:
        dict with:
          - ambiguity_score (float)
          - smells (list[str])
    """
    smells = []
    text_lower = text.lower()

    # 1. Check vague quantifiers
    found_vague = [q for q in VAGUE_QUANTIFIERS if re.search(r"\b" + re.escape(q) + r"\b", text_lower)]
    if found_vague:
        smells.append(f"vague_quantifier: {', '.join(found_vague)}")

    # 2. Check passive voice without explicit actor ("by <actor>")
    matches = PASSIVE_VOICE_PATTERN.findall(text)
    if matches:
        # Check if 'by' follows shortly after
        if " by " not in text_lower:
            matched_phrases = [f"{m[0]} {m[1]}" for m in matches]
            smells.append(f"passive_voice_no_actor: {', '.join(matched_phrases)}")

    # 3. Check missing measurable value (has comparative/qualitative word but no numbers)
    has_numbers = bool(re.search(r"\b\d+(\.\d+)?\b", text))
    qualitative_words = ["fast", "quickly", "efficiently", "slow", "high", "low", "minimal"]
    found_qual = [w for w in qualitative_words if re.search(r"\b" + re.escape(w) + r"\b", text_lower)]
    if found_qual and not has_numbers:
        smells.append(f"missing_measurable_value: {', '.join(found_qual)}")

    # 4. Check un-anchored open conditionals / weak directives
    open_conditionals = ["as far as possible", "where feasible", "to the extent possible", "etc.", "and so on", "under all conditions", "within seconds"]
    found_open = [c for c in open_conditionals if c in text_lower]
    if found_open:
        smells.append(f"unanchored_conditional: {', '.join(found_open)}")

    # Compute score based on smells found (cap at 1.0)
    # Each smell type adds 0.50 to the score to ensure clear binary threshold flagging
    score = min(1.0, len(smells) * 0.50)

    return {
        "ambiguity_score": round(score, 2),
        "smells": smells,
    }

