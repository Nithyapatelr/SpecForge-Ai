"""
Seed the RIT taxonomy into the database.

Idempotent: running this script multiple times will not duplicate rows or raise errors.

Usage:
    python scripts/seed_taxonomy.py
"""

import sys
import os

# Allow running as a standalone script from the project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import logging

from specforge.classification.rit_taxonomy import RIT_CATEGORIES
from specforge.db.init_db import init_db
from specforge.db.models import RITTaxonomy
from specforge.db.session import get_session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_taxonomy() -> int:
    """
    Insert RIT categories that don't already exist.

    Returns the number of rows actually inserted (0 if already seeded).
    """
    # Ensure tables exist before trying to insert
    init_db()

    inserted = 0
    with get_session() as session:
        existing_ids = {
            row.label_id
            for row in session.query(RITTaxonomy.label_id).all()
        }

        for cat in RIT_CATEGORIES:
            if cat["label_id"] in existing_ids:
                logger.debug("Skipping existing label: %s", cat["label_id"])
                continue

            row = RITTaxonomy(
                label_id=cat["label_id"],
                label_name=cat["label_name"],
                label_definition=cat["label_definition"],
                parent_category=cat.get("parent_category"),
            )
            session.add(row)
            inserted += 1
            logger.info("Inserted: %s", cat["label_id"])

    logger.info(
        "Taxonomy seeding complete. %d new rows inserted (%d total categories).",
        inserted,
        len(RIT_CATEGORIES),
    )
    return inserted


if __name__ == "__main__":
    seed_taxonomy()
