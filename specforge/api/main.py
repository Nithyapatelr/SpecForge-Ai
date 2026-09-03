"""
FastAPI REST API for SpecForge AI diagnostic layer.
"""

import os
import tempfile
import uuid
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from specforge.ambiguity.service import detect_and_store
from specforge.classification.service import classify_and_store
from specforge.db.init_db import init_db
from specforge.db.models import Requirement
from specforge.db.session import get_session
from specforge.ingestion.service import ingest_document
from specforge.preprocessing.service import preprocess_requirement
from specforge.reporting.annotator import generate_annotated_spec

app = FastAPI(
    title="SpecForge AI API",
    description="Diagnostic layer API for requirement classification and ambiguity detection",
    version="0.1.0",
)


@app.on_event("startup")
def startup_event():
    """Ensure database tables exist on startup."""
    init_db()


class IngestTextRequest(BaseModel):
    raw_text: str
    source_doc_id: Optional[str] = None


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/ingest")
async def ingest_endpoint(
    raw_text: Optional[str] = Form(None),
    source_doc_id: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
):
    """
    Ingest a document (file upload or raw text) and preprocess into atomic units.
    """
    if file is None and not raw_text:
        raise HTTPException(status_code=400, detail="Provide either 'file' upload or 'raw_text'.")

    doc_id = source_doc_id or f"doc-{uuid.uuid4().hex[:8]}"

    if file:
        # Save temp file
        ext = os.path.splitext(file.filename or "")[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        try:
            initial_req = ingest_document(file_path=tmp_path, source_doc_id=doc_id)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    else:
        initial_req = ingest_document(raw_text=raw_text, source_doc_id=doc_id)

    # Preprocess into atomic units
    processed_reqs = preprocess_requirement(initial_req.requirement_id)
    req_ids = [r.requirement_id for r in processed_reqs]

    return {
        "source_doc_id": doc_id,
        "requirement_ids": req_ids,
        "total_atomic_units": len(req_ids),
    }


@app.post("/classify/{requirement_id}")
def classify_endpoint(requirement_id: str):
    """Classify a single requirement by ID."""
    try:
        clf = classify_and_store(requirement_id)
        return {
            "requirement_id": clf.requirement_id,
            "label_id": clf.label_id,
            "confidence_score": clf.confidence_score,
            "classifier_version": clf.classifier_version,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ambiguity/{requirement_id}")
def ambiguity_endpoint(requirement_id: str):
    """Detect ambiguity for a single requirement by ID."""
    try:
        flag = detect_and_store(requirement_id)
        return {
            "requirement_id": flag.requirement_id,
            "ambiguity_score": flag.ambiguity_score,
            "flag_reason": flag.flag_reason,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process/{source_doc_id}")
def process_full_doc_endpoint(source_doc_id: str):
    """Convenience endpoint to run classification & ambiguity detection for all reqs in doc."""
    with get_session() as session:
        reqs = session.query(Requirement).filter_by(source_doc_id=source_doc_id).all()
        req_ids = [r.requirement_id for r in reqs]

    if not req_ids:
        raise HTTPException(status_code=404, detail=f"No requirements found for source_doc_id '{source_doc_id}'")

    processed = []
    for rid in req_ids:
        clf = classify_and_store(rid)
        flag = detect_and_store(rid)
        processed.append({
            "requirement_id": rid,
            "label_id": clf.label_id,
            "ambiguity_score": flag.ambiguity_score,
        })

    return {
        "source_doc_id": source_doc_id,
        "processed_count": len(processed),
        "results": processed,
    }


@app.get("/report/{source_doc_id}")
def report_endpoint(source_doc_id: str):
    """Get diagnostic annotated spec report for a source_doc_id."""
    report = generate_annotated_spec(source_doc_id)
    if report["summary"]["total_requirements"] == 0:
        raise HTTPException(status_code=404, detail=f"No requirements found for source_doc_id '{source_doc_id}'")
    return report
