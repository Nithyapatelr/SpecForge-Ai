"""
Unit tests for Phase 2 database models (MASTTaxonomy, MASRuns, FailureLogs).
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from specforge.db.models import Base, FailureLogs, MASRuns, MASTTaxonomy


@pytest.fixture()
def temp_session(tmp_path):
    """
    Provide a temporary file-based SQLite session for DB model tests.
    """
    db_path = tmp_path / "test_db_phase2.db"
    test_engine = create_engine(
        f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=test_engine)
    Session = sessionmaker(bind=test_engine, autocommit=False, autoflush=False)
    db = Session()
    try:
        yield db
    finally:
        db.close()


def test_db_phase2_models(temp_session):
    db = temp_session
    # Insert MASTTaxonomy row
    taxonomy_item = MASTTaxonomy(
        failure_mode_id="FM-TEST-1.1",
        category="Specification Issues",
        mode_name="Disobey Task Specification",
        mode_definition="Failure to adhere to specified constraints."
    )
    db.add(taxonomy_item)
    db.commit()

    # Insert MASRuns row
    run_item = MASRuns(
        source_doc_id="doc_123",
        framework_name="metagpt",
        annotated=True,
        task_description="Build a CLI calculator",
        raw_trace_path="/tmp/trace.log",
        status="completed"
    )
    db.add(run_item)
    db.commit()
    db.refresh(run_item)

    # Insert FailureLogs row
    failure_item = FailureLogs(
        run_id=run_item.run_id,
        mast_failure_mode_id="FM-TEST-1.1",
        failure_description="Agent failed to implement subtract option.",
        agent_stage="Coder",
        confidence=0.95
    )
    db.add(failure_item)
    db.commit()

    # Query back and assert
    fetched_tax = db.query(MASTTaxonomy).filter_by(failure_mode_id="FM-TEST-1.1").first()
    assert fetched_tax is not None
    assert fetched_tax.mode_name == "Disobey Task Specification"

    fetched_run = db.query(MASRuns).filter_by(run_id=run_item.run_id).first()
    assert fetched_run is not None
    assert fetched_run.framework_name == "metagpt"
    assert fetched_run.annotated is True

    fetched_failure = db.query(FailureLogs).filter_by(run_id=run_item.run_id).first()
    assert fetched_failure is not None
    assert fetched_failure.mast_failure_mode_id == "FM-TEST-1.1"
    assert fetched_failure.confidence == 0.95
