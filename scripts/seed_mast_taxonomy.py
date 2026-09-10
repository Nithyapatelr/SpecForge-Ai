"""
Seed the MAST failure taxonomy into the database.

Idempotent: running this script multiple times will not duplicate rows or raise errors.

Usage:
    python scripts/seed_mast_taxonomy.py
"""

import sys
import os
import logging

# Allow running as a standalone script from the project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from specforge.failure_logging.mast_taxonomy import MAST_FAILURE_MODES
from specforge.db.init_db import init_db
from specforge.db.models import MASTTaxonomy
from specforge.db.session import get_session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_mast_taxonomy() -> int:
    """
    Insert MAST failure modes that don't already exist.

    Returns the number of rows actually inserted (0 if already seeded).
    """
    init_db()

    inserted = 0
    with get_session() as session:
        existing_ids = {
            row.failure_mode_id
            for row in session.query(MASTTaxonomy.failure_mode_id).all()
        }

        for mode in MAST_FAILURE_MODES:
            if mode["failure_mode_id"] in existing_ids:
                logger.debug("Skipping existing failure mode: %s", mode["failure_mode_id"])
                continue

            row = MASTTaxonomy(
                failure_mode_id=mode["failure_mode_id"],
                category=mode["category"],
                mode_name=mode["mode_name"],
                mode_definition=mode["mode_definition"],
            )
            session.add(row)
            inserted += 1
            logger.info("Inserted MAST failure mode: %s", mode["failure_mode_id"])

    logger.info(
        "MAST Taxonomy seeding complete. %d new rows inserted (%d total failure modes).",
        inserted,
        len(MAST_FAILURE_MODES),
    )
    return inserted


if __name__ == "__main__":
    seed_mast_taxonomy()
