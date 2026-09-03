"""
Requirement ingestion loaders.

Each loader accepts a file path (or raw string) and returns plain text.
The choice of extraction strategy is determined by file extension.
"""

import pathlib


def load_txt(file_path: str) -> str:
    """Read a plain-text file and return its contents."""
    return pathlib.Path(file_path).read_text(encoding="utf-8")


def load_docx(file_path: str) -> str:
    """
    Extract text from a .docx file by concatenating all paragraph text.

    Uses python-docx.  Tables and headers within the document are not
    extracted in this version (plain paragraphs only).
    """
    from docx import Document  # type: ignore

    doc = Document(file_path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def load_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file by concatenating all page text.

    Uses pypdf.  Scanned/image-based PDFs without an embedded text layer
    will return empty or near-empty strings — OCR is out of scope for Phase 1.
    """
    from pypdf import PdfReader  # type: ignore

    reader = PdfReader(file_path)
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def load_raw_string(text: str) -> str:
    """
    Accept raw pasted text with no file I/O.

    This is a thin wrapper so the service layer has a uniform interface
    regardless of input source.
    """
    return text


def load_file(file_path: str) -> str:
    """
    Dispatch to the correct loader based on file extension.

    Supported extensions: .txt, .docx, .pdf
    Raises ValueError for unsupported types.
    """
    ext = pathlib.Path(file_path).suffix.lower()
    loaders = {
        ".txt": load_txt,
        ".docx": load_docx,
        ".pdf": load_pdf,
    }
    if ext not in loaders:
        raise ValueError(
            f"Unsupported file type '{ext}'. Supported: {', '.join(loaders)}"
        )
    return loaders[ext](file_path)
