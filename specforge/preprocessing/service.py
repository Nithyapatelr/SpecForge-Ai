"""
Preprocessing service — segments raw requirement text into atomic units
and persists the results back to the database.
"""

import uuid
from datetime import datetime, timezone

from specforge.db.models import Requirement
from specforge.db.session import get_session
from specforge.preprocessing.segmenter import segment_into_atomic_units


def preprocess_requirement(requirement_id: str) -> list[Requirement]:
    """
    Load a Requirements row, segment its raw_text into atomic units, and
    persist the results.

    Behaviour:
    - **Single atomic unit**: Sets ``atomic_unit_text`` on the existing row.
    - **Multiple atomic units**: Sets ``atomic_unit_text`` on the existing row
      for the first unit, then creates additional sibling rows (same
      ``source_doc_id``) for the remaining units.

    Args:
        requirement_id: PK of the Requirements row to preprocess.

    Returns:
        List of Requirements rows (original + any newly created siblings).

    Raises:
        ValueError: if no Requirement with that ID exists.
    """
    with get_session() as session:
        req: Requirement | None = session.get(Requirement, requirement_id)
        if req is None:
            raise ValueError(f"Requirement '{requirement_id}' not found.")

        units = segment_into_atomic_units(req.raw_text)

        if not units:
            # Fallback: treat the whole raw_text as one unit
            units = [req.raw_text.strip()]

        results: list[Requirement] = []

        for idx, unit_text in enumerate(units):
            if idx == 0:
                # Update the original row in place
                req.atomic_unit_text = unit_text
                session.add(req)
                results.append(req)
            else:
                # Create a sibling row for each additional atomic unit
                sibling = Requirement(
                    requirement_id=str(uuid.uuid4()),
                    source_doc_id=req.source_doc_id,
                    raw_text=req.raw_text,  # preserve original for traceability
                    atomic_unit_text=unit_text,
                    created_at=datetime.now(timezone.utc),
                )
                session.add(sibling)
                results.append(sibling)

        session.flush()
        for r in results:
            session.refresh(r)

    return results
