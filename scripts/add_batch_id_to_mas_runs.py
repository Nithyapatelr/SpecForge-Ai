"""
Database Migration Script — Adds batch_id column to mas_runs table.
"""

from sqlalchemy import text
from specforge.db.session import engine


def migrate_add_batch_id() -> None:
    """
    Idempotent migration adding batch_id column to mas_runs table.
    """
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE mas_runs ADD COLUMN batch_id VARCHAR"))
            conn.commit()
            print("Successfully added batch_id column to mas_runs table.")
        except Exception as exc:
            print(f"Migration note (column may already exist or table created with column): {exc}")


if __name__ == "__main__":
    migrate_add_batch_id()
