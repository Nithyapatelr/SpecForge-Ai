"""
Ingestion service — creates a Requirements row from a file or raw string.
"""

import uuid
from datetime import datetime, timezone

from specforge.db.models import Requirement
from specforge.db.session import get_session
from specforge.ingestion.loader import load_file, load_raw_string


def ingest_document(
    file_path: str | None = None,
    raw_text: str | None = None,
    source_doc_id: str | None = None,
) -> Requirement:
    """
    Ingest a document from a file path or raw text string.

    Exactly one of *file_path* or *raw_text* must be provided.

    Args:
        file_path:    Absolute or relative path to a .txt / .docx / .pdf file.
        raw_text:     Raw requirement text pasted directly (no file I/O).
        source_doc_id: Optional identifier for the source document. If omitted
                       a new UUID is generated.

    Returns:
        The persisted :class:`~specforge.db.models.Requirement` ORM row
        (with *atomic_unit_text* still null — preprocessing fills that).

    Raises:
        ValueError: if neither or both of *file_path* / *raw_text* are provided.
    """
    if file_path is None and raw_text is None:
        raise ValueError("Provide either 'file_path' or 'raw_text'.")
    if file_path is not None and raw_text is not None:
        raise ValueError("Provide only one of 'file_path' or 'raw_text', not both.")

    text = load_file(file_path) if file_path is not None else load_raw_string(raw_text)  # type: ignore[arg-type]

    if not text.strip():
        raise ValueError("Extracted text is empty — check the input document.")

    req = Requirement(
        requirement_id=str(uuid.uuid4()),
        source_doc_id=source_doc_id or str(uuid.uuid4()),
        raw_text=text.strip(),
        atomic_unit_text=None,
        created_at=datetime.now(timezone.utc),
    )

    with get_session() as session:
        session.add(req)
        session.flush()   # assign DB defaults before expiry
        session.refresh(req)

    return req
