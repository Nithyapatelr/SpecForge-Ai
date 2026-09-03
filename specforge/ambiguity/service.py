"""
Ambiguity detection service — combines heuristic and LLM scores and stores in DB.
"""

import uuid
from datetime import datetime, timezone

from specforge.ambiguity.heuristics import heuristic_ambiguity_score
from specforge.ambiguity.llm_scorer import llm_ambiguity_score
from specforge.db.models import AmbiguityFlag, Requirement
from specforge.db.session import get_session


def detect_and_store(requirement_id: str) -> AmbiguityFlag:
    """
    Run heuristic and LLM ambiguity scoring on a requirement and store the result.

    Score combination rationale:
    We take the maximum (max) of heuristic_score and llm_score rather than simple average.
    Rationale: Software safety and requirements engineering prioritize high recall for defects.
    If either a deterministic heuristic rule (e.g. vague word detected) OR an LLM semantic model
    identifies an ambiguity smell, flagging it ensures critical ambiguities are not diluted by an
    overly forgiving second model.

    Args:
        requirement_id: PK of the Requirement row to evaluate.

    Returns:
        Persisted AmbiguityFlag ORM row.
    """
    with get_session() as session:
        req: Requirement | None = session.get(Requirement, requirement_id)
        if req is None:
            raise ValueError(f"Requirement '{requirement_id}' not found.")

        target_text = req.atomic_unit_text or req.raw_text
        if not target_text or not target_text.strip():
            raise ValueError(f"Requirement '{requirement_id}' has empty text to score.")

        # 1. Run heuristic scorer
        h_res = heuristic_ambiguity_score(target_text)
        h_score = h_res["ambiguity_score"]
        h_smells = h_res["smells"]

        # 2. Run LLM scorer (with fallback if API key is not configured or in tests)
        try:
            l_res = llm_ambiguity_score(target_text)
            l_score = l_res["ambiguity_score"]
            l_rationale = l_res["rationale"]
        except Exception:
            # In test environments or when API key is missing
            l_score = h_score
            l_rationale = "LLM scoring skipped or unavailable."

        # Take max score for conservative diagnostic safety
        final_score = round(max(h_score, l_score), 2)

        reasons = []
        if h_smells:
            reasons.append("Heuristics: " + " | ".join(h_smells))
        if l_rationale:
            reasons.append(f"LLM: {l_rationale}")
        if not reasons:
            reasons.append("No ambiguity smells detected.")

        flag_reason_str = " || ".join(reasons)

        flag = AmbiguityFlag(
            flag_id=str(uuid.uuid4()),
            requirement_id=requirement_id,
            ambiguity_score=final_score,
            flag_reason=flag_reason_str,
            timestamp=datetime.now(timezone.utc),
        )

        session.add(flag)
        session.flush()
        session.refresh(flag)

    return flag
