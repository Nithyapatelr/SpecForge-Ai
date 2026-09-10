"""
SQLAlchemy ORM models for SpecForge AI — Phase 1 tables only.

Deliberately excluded from this file (planned for later phases):
  - MAS_Runs
  - Failure_Logs
  - Evaluation_Metrics
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, relationship


def _uuid() -> str:
    """Generate a new UUID4 string."""
    return str(uuid.uuid4())


def _now() -> datetime:
    """Return the current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """Shared declarative base for all SpecForge models."""
    pass


class Requirement(Base):
    """
    A single raw or atomic requirement unit.

    A document ingested via the /ingest endpoint creates one initial row
    with raw_text populated and atomic_unit_text = None.  The preprocessing
    step then fills atomic_unit_text (and may create additional sibling rows
    if the raw text contains multiple atomic requirements).
    """

    __tablename__ = "requirements"

    requirement_id: str = Column(
        String, primary_key=True, default=_uuid
    )
    source_doc_id: str = Column(String, nullable=True)
    raw_text: str = Column(Text, nullable=False)
    atomic_unit_text: str = Column(Text, nullable=True)
    created_at: datetime = Column(DateTime, default=_now)

    # Relationships
    classifications = relationship(
        "Classification", back_populates="requirement", cascade="all, delete-orphan"
    )
    ambiguity_flags = relationship(
        "AmbiguityFlag", back_populates="requirement", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Requirement id={self.requirement_id[:8]}… source={self.source_doc_id}>"


class RITTaxonomy(Base):
    """
    Requirement Intent Taxonomy category definition.

    Seeded once via scripts/seed_taxonomy.py from
    specforge/classification/rit_taxonomy.py.  Should not change between
    runs unless a new taxonomy version is released.
    """

    __tablename__ = "rit_taxonomy"

    label_id: str = Column(String, primary_key=True)
    label_name: str = Column(String, unique=True, nullable=False)
    label_definition: str = Column(Text, nullable=False)
    parent_category: str = Column(String, nullable=True)

    # Relationships
    classifications = relationship("Classification", back_populates="rit_label")

    def __repr__(self) -> str:
        return f"<RITTaxonomy {self.label_id}: {self.label_name}>"


class Classification(Base):
    """
    The result of running the RIT classifier on one atomic requirement unit.

    One row per classifier invocation — a requirement can be re-classified
    (different classifier_version) without losing history.
    """

    __tablename__ = "classifications"

    classification_id: str = Column(
        String, primary_key=True, default=_uuid
    )
    requirement_id: str = Column(
        String, ForeignKey("requirements.requirement_id"), nullable=False
    )
    label_id: str = Column(
        String, ForeignKey("rit_taxonomy.label_id"), nullable=False
    )
    confidence_score: float = Column(Float, nullable=False)
    classifier_version: str = Column(String, nullable=False)
    timestamp: datetime = Column(DateTime, default=_now)

    # Relationships
    requirement = relationship("Requirement", back_populates="classifications")
    rit_label = relationship("RITTaxonomy", back_populates="classifications")

    def __repr__(self) -> str:
        return (
            f"<Classification req={self.requirement_id[:8]}… "
            f"label={self.label_id} conf={self.confidence_score:.2f}>"
        )


class AmbiguityFlag(Base):
    """
    The result of running the ambiguity detector on one atomic requirement unit.

    ambiguity_score is 0.0 (perfectly clear) to 1.0 (maximally vague).
    flag_reason is a pipe-separated concatenation of all detected smell strings.
    """

    __tablename__ = "ambiguity_flags"

    flag_id: str = Column(
        String, primary_key=True, default=_uuid
    )
    requirement_id: str = Column(
        String, ForeignKey("requirements.requirement_id"), nullable=False
    )
    ambiguity_score: float = Column(Float, nullable=False)
    flag_reason: str = Column(Text, nullable=False)
    timestamp: datetime = Column(DateTime, default=_now)

    # Relationships
    requirement = relationship("Requirement", back_populates="ambiguity_flags")

    def __repr__(self) -> str:
        return (
            f"<AmbiguityFlag req={self.requirement_id[:8]}… "
            f"score={self.ambiguity_score:.2f}>"
        )


class MASTTaxonomy(Base):
    """
    MAST (Multi-Agent System Failure Taxonomy) category and mode definitions.
    Seeded via scripts/seed_mast_taxonomy.py based on Cemri et al. (2025).
    """

    __tablename__ = "mast_taxonomy"

    failure_mode_id: str = Column(String, primary_key=True)
    category: str = Column(String, nullable=False)
    mode_name: str = Column(String, nullable=False)
    mode_definition: str = Column(Text, nullable=False)

    # Relationships
    failure_logs = relationship("FailureLogs", back_populates="mast_failure_mode")

    def __repr__(self) -> str:
        return f"<MASTTaxonomy {self.failure_mode_id}: {self.mode_name}>"


class MASRuns(Base):
    """
    Execution trace metadata for a Multi-Agent System (MAS) framework run.
    """

    __tablename__ = "mas_runs"

    run_id: str = Column(String, primary_key=True, default=_uuid)
    source_doc_id: str = Column(String, nullable=True)
    framework_name: str = Column(String, nullable=False)
    annotated: bool = Column(Boolean, nullable=False, default=False)
    task_description: str = Column(Text, nullable=False)
    run_timestamp: datetime = Column(DateTime, default=_now)
    raw_trace_path: str = Column(String, nullable=True)
    status: str = Column(String, nullable=False, default="running")

    # Relationships
    failure_logs = relationship(
        "FailureLogs", back_populates="run", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<MASRuns {self.run_id[:8]} framework={self.framework_name} "
            f"annotated={self.annotated} status={self.status}>"
        )


class FailureLogs(Base):
    """
    Log of a single detected MAST failure mode during a MAS framework run.
    """

    __tablename__ = "failure_logs"

    failure_id: str = Column(String, primary_key=True, default=_uuid)
    run_id: str = Column(
        String, ForeignKey("mas_runs.run_id"), nullable=False
    )
    mast_failure_mode_id: str = Column(
        String, ForeignKey("mast_taxonomy.failure_mode_id"), nullable=False
    )
    failure_description: str = Column(Text, nullable=False)
    agent_stage: str = Column(String, nullable=False)
    confidence: float = Column(Float, nullable=False)
    timestamp: datetime = Column(DateTime, default=_now)

    # Relationships
    run = relationship("MASRuns", back_populates="failure_logs")
    mast_failure_mode = relationship("MASTTaxonomy", back_populates="failure_logs")

    def __repr__(self) -> str:
        return (
            f"<FailureLogs {self.failure_id[:8]} mode={self.mast_failure_mode_id} "
            f"stage={self.agent_stage} conf={self.confidence:.2f}>"
        )

