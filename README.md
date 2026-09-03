# SpecForge AI — Phase 1 Implementation

**Team:** Abhavya, Nithya Patel  
**Scope:** Phase 1 (25% prototype) — Ingestion → Preprocessing → RIT Classification → Ambiguity Detection → Reporting & Visualization.

SpecForge AI is a diagnostic layer designed to classify software requirements and detect ambiguity smells **before** handing specifications off to multi-agent coding frameworks (MetaGPT, ChatDev, MARE). By catching vague, ambiguous, or poorly structured requirements early, SpecForge prevents downstream agent synthesis failures.

---

## Architecture Diagram

```
                              ┌────────────────────────┐
                              │ Input Document         │
                              │ (.txt, .docx, .pdf)    │
                              └───────────┬────────────┘
                                          │
                                          ▼
                              ┌────────────────────────┐
                              │ Ingestion Module       │
                              │ (specforge.ingestion)  │
                              └───────────┬────────────┘
                                          │
                                          ▼
                              ┌────────────────────────┐
                              │ Preprocessing          │
                              │ (Atomic Segmentation)  │
                              └───────────┬────────────┘
                                          │
                   ┌──────────────────────┴──────────────────────┐
                   │                                             │
                   ▼                                             ▼
     ┌───────────────────────────┐                 ┌───────────────────────────┐
     │ RIT Intent Classifier     │                 │ Ambiguity Detector        │
     │ (Few-Shot Claude Prompt)  │                 │ (Heuristics + LLM Scorer) │
     └─────────────┬─────────────┘                 └─────────────┬─────────────┘
                   │                                             │
                   └──────────────────────┬──────────────────────┘
                                          │
                                          ▼
                              ┌────────────────────────┐
                              │ SQLite / Postgres DB   │
                              │ (specforge.db)         │
                              └───────────┬────────────┘
                                          │
                                          ▼
                              ┌────────────────────────┐
                              │ Diagnostic Reporter    │
                              │ (Annotated Spec JSON)  │
                              └───────────┬────────────┘
                                          │
                    ┌─────────────────────┴─────────────────────┐
                    │                                           │
                    ▼                                           ▼
      ┌───────────────────────────┐               ┌───────────────────────────┐
      │ FastAPI REST Service      │               │ Streamlit Dashboard       │
      │ (http://localhost:8000)   │ ────────────> │ (http://localhost:8501)   │
      └───────────────────────────┘               └───────────────────────────┘
```

---

## RIT Taxonomy v1

SpecForge uses a 6-category Requirement Intent Taxonomy (RIT):
1. **Behavioral Rule**: Condition-action rules ("if X then system shall Y").
2. **State Transition**: State movement of entities ("Scheduled -> Confirmed").
3. **Actor Permission**: Role authorization rules ("Only Senior Doctor may...").
4. **Data Contract**: Schema, field format, and validation constraints.
5. **Integration Constraint**: External API and boundary interactions.
6. **Acceptance Condition**: Testable performance or quality thresholds.

---

## Quickstart & Setup

### 1. Requirements & Virtual Environment

```bash
# Using Python 3.10+
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Configure Environment

Copy `.env.example` to `.env` and insert your Anthropic API Key:
```env
ANTHROPIC_API_KEY=your_actual_api_key_here
DATABASE_URL=sqlite:///./data/specforge.db
ANTHROPIC_MODEL=claude-sonnet-4-6
```

---

## Running the Automated Test Suite

All unit and integration tests use an in-memory SQLite database and mock Anthropic API calls (no live API key required for testing):

```bash
python -m pytest -v
```

---

## Three Commands to Run the Live Review Demo

### Command 1: Run Full End-to-End Pipeline Demo (Console)

Executes database init, taxonomy seeding, sample ingestion (15 requirements), atomic segmentation, classification, ambiguity scoring, and prints a diagnostic summary report:

```bash
python scripts/run_full_pipeline_demo.py
```

### Command 2: Start FastAPI REST Backend

In terminal 1:
```bash
uvicorn specforge.api.main:app --reload
```
Interactive OpenAPI docs will be available at `http://localhost:8000/docs`.

### Command 3: Start Streamlit Dashboard

In terminal 2:
```bash
streamlit run scripts/dashboard.py
```
Open `http://localhost:8501` to view distribution charts and high-ambiguity requirement tables.

---

## Implementation Status (Phase 1 vs. Future Phases)

### ✅ Phase 1: DONE (Implemented & Verified)
- **Scaffolding & DB Layer**: SQLAlchemy ORM with `Requirements`, `RITTaxonomy`, `Classifications`, `AmbiguityFlags`.
- **Taxonomy Seeding**: 6 primary categories + sub-categories with idempotent seeding.
- **Ingestion Engine**: `.txt`, `.docx`, `.pdf`, and raw text loaders.
- **Atomic Preprocessor**: spaCy-based sentence segmentation + modal-verb compound sentence splitter.
- **RIT Classifier**: Few-shot Claude prompt with defensive JSON parsing.
- **Ambiguity Detector**: Multi-smell heuristic checks + LLM ambiguity scoring (max score safety strategy).
- **Diagnostic Reporter**: JSON annotated specification generator.
- **FastAPI REST API**: Endpoints for ingest, classify, ambiguity, full doc process, report, and health.
- **Streamlit Dashboard**: Metrics, bar chart of RIT distribution, and highlighted table sorted by ambiguity score descending.
- **Automated Tests**: 29 unit and integration tests passing.

### ⏳ Future Phases (Planned for Phase 2+)
- **MAS Adapter Layer**: Integration with MetaGPT, ChatDev, and MARE frameworks (Phase 4).
- **Failure Logging**: Run tracking and agent execution error logging (Phase 4).
- **Evaluation & Correlation Engine**: Metric analysis between ambiguity scores and agent execution success (Phase 7).
- **Fine-tuned BERT Ablation**: Fine-tuning local transformer models for offline classification (Phase 7).
