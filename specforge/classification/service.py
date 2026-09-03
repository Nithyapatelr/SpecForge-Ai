"""
Classification service — runs classify_requirement on a Requirement's
atomic_unit_text, matches the RITTaxonomy label in DB, and stores a Classifications row.
"""

import uuid
from datetime import datetime, timezone

from specforge.classification.classifier import classify_requirement
from specforge.db.models import Classification, RITTaxonomy, Requirement
from specforge.db.session import get_session


def classify_and_store(
    requirement_id: str,
    classifier_version: str = "rit-v1-fewshot",
) -> Classification:
    """
    Classify a requirement and store the result in the database.

    Args:
        requirement_id: PK of the Requirements row to classify.
        classifier_version: Model/version tag for the classification record.

    Returns:
        The created :class:`~specforge.db.models.Classification` ORM row.
    """
    with get_session() as session:
        req: Requirement | None = session.get(Requirement, requirement_id)
        if req is None:
            raise ValueError(f"Requirement '{requirement_id}' not found.")

        target_text = req.atomic_unit_text or req.raw_text
        if not target_text or not target_text.strip():
            raise ValueError(f"Requirement '{requirement_id}' has empty text to classify.")

        clf_result = classify_requirement(target_text)

        # Look up taxonomy label by name
        label_name = clf_result["label_name"]
        taxonomy_row = (
            session.query(RITTaxonomy)
            .filter(RITTaxonomy.label_name.ilike(label_name))
            .first()
        )

        if taxonomy_row is None:
            # Fallback matching by label_id or partial match
            taxonomy_row = (
                session.query(RITTaxonomy)
                .filter(RITTaxonomy.label_id.ilike(label_name.replace(" ", "_")))
                .first()
            )

        if taxonomy_row is None:
            # Fallback to BEHAVIORAL_RULE if taxonomy match fails
            taxonomy_row = session.query(RITTaxonomy).first()
            if taxonomy_row is None:
                raise ValueError("Taxonomy table is empty. Run seed_taxonomy first.")

        classification = Classification(
            classification_id=str(uuid.uuid4()),
            requirement_id=requirement_id,
            label_id=taxonomy_row.label_id,
            confidence_score=float(clf_result.get("confidence", 0.8)),
            classifier_version=classifier_version,
            timestamp=datetime.now(timezone.utc),
        )

        session.add(classification)
        session.flush()
        session.refresh(classification)

    return classification
