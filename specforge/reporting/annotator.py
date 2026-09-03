"""
Diagnostic Report Generator — annotates a specification document's requirements
with classification labels and ambiguity flags into a structured JSON report.
"""

import json
from datetime import datetime, timezone

from specforge.db.models import AmbiguityFlag, Classification, RITTaxonomy, Requirement
from specforge.db.session import get_session


def generate_annotated_spec(source_doc_id: str) -> dict:
    """
    Generate an annotated specification report dict for a given source_doc_id.

    Args:
        source_doc_id: Identifier of the document to report on.

    Returns:
        Structured dictionary containing requirements list and summary statistics.
    """
    with get_session() as session:
        requirements = (
            session.query(Requirement)
            .filter(Requirement.source_doc_id == source_doc_id)
            .all()
        )

        req_items = []
        label_distribution = {}
        high_ambiguity_count = 0

        for req in requirements:
            # Latest classification
            latest_clf = (
                session.query(Classification)
                .filter(Classification.requirement_id == req.requirement_id)
                .order_by(Classification.timestamp.desc())
                .first()
            )

            # RIT label name lookup
            rit_label_name = "Unclassified"
            rit_confidence = 0.0
            if latest_clf:
                rit_confidence = latest_clf.confidence_score
                tax_row = session.query(RITTaxonomy).filter_by(label_id=latest_clf.label_id).first()
                if tax_row:
                    rit_label_name = tax_row.label_name
                else:
                    rit_label_name = latest_clf.label_id

            label_distribution[rit_label_name] = label_distribution.get(rit_label_name, 0) + 1

            # Latest ambiguity flag
            latest_flag = (
                session.query(AmbiguityFlag)
                .filter(AmbiguityFlag.requirement_id == req.requirement_id)
                .order_by(AmbiguityFlag.timestamp.desc())
                .first()
            )

            ambiguity_score = 0.0
            ambiguity_reasons = []
            if latest_flag:
                ambiguity_score = latest_flag.ambiguity_score
                ambiguity_reasons = [r.strip() for r in latest_flag.flag_reason.split("||") if r.strip()]

            if ambiguity_score > 0.6:
                high_ambiguity_count += 1

            req_items.append({
                "requirement_id": req.requirement_id,
                "atomic_unit_text": req.atomic_unit_text or req.raw_text,
                "rit_label": rit_label_name,
                "rit_confidence": round(rit_confidence, 2),
                "ambiguity_score": round(ambiguity_score, 2),
                "ambiguity_reasons": ambiguity_reasons,
            })

        report = {
            "source_doc_id": source_doc_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "requirements": req_items,
            "summary": {
                "total_requirements": len(req_items),
                "label_distribution": label_distribution,
                "high_ambiguity_count": high_ambiguity_count,
            },
        }

    return report


def save_annotated_spec(source_doc_id: str, output_path: str) -> None:
    """Save the generated annotated spec report as pretty-printed JSON to disk."""
    report = generate_annotated_spec(source_doc_id)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
