# SpecForge AI — Phase 1 & 2 Implementation

**Team:** Abhavya, Nithya Patel  
**Scope:** Phase 1 (Diagnostic Layer) + Phase 2 (MAS Adapter Layer, Failure Logging Layer with MAST Taxonomy, Comparative Experiment Runner, FastAPI & Streamlit Extensions).

SpecForge AI is a diagnostic and annotation layer designed to classify software requirements and detect ambiguity smells **before** handing specifications off to multi-agent coding frameworks (MetaGPT, ChatDev, MARE). By catching vague, ambiguous, or poorly structured requirements early and injecting structured pre-analysis annotations, SpecForge prevents downstream agent synthesis failures.

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
                               │ (7 Tables)             │
                               └───────────┬────────────┘
                                           │
                    ┌──────────────────────┴──────────────────────┐
                    │                                             │
                    ▼                                             ▼
      ┌───────────────────────────┐                 ┌───────────────────────────┐
      │ MAS Adapter Layer         │                 │ MAST Failure Logger       │
      │ (MetaGPT Adapter)         │                 │ (LLM-as-a-Judge 14 Modes) │
      └─────────────┬─────────────┘                 └─────────────┬─────────────┘
                    │                                             │
                    └──────────────────────┬──────────────────────┘
                                           │
                                           ▼
                               ┌────────────────────────┐
                               │ Comparative Experiment │
                               │ (Baseline vs Annotated)│
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

## MAST Failure Taxonomy (14 Modes)

SpecForge failure logging uses the published MAST (Multi-Agent System Failure Taxonomy) from Cemri et al. (UC Berkeley, 2025, arXiv:2503.13657):
- **Specification Issues** (5 modes): FM-1.1 Disobey Task Spec, FM-1.2 Disobey Role Spec, FM-1.3 Step Repetition, FM-1.4 Loss of History, FM-1.5 Unaware of Termination.
- **Inter-Agent Misalignment** (6 modes): FM-2.1 Conversation Reset, FM-2.2 Fail to Ask Clarification, FM-2.3 Task Derailment, FM-2.4 Information Withholding, FM-2.5 Ignored Input, FM-2.6 Reasoning-Action Mismatch.
- **Task Verification** (3 modes): FM-3.1 Premature Termination, FM-3.2 No/Incomplete Verification, FM-3.3 Incorrect Verification.

---

## Quickstart & Setup

### 1. Requirements & Environment Setup

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

Run fast default unit tests (excluding integration tests):
```bash
python -m pytest -v -m "not integration"
```

Run full test suite including integration tests:
```bash
python -m pytest -v
```

---

## Phase 2 Setup & Live Demo Commands

### Step 1: Build & Start MetaGPT Container

```bash
docker compose build metagpt
```

### Step 2: Seed Taxonomies (RIT & MAST)

```bash
python scripts/seed_taxonomy.py
python scripts/seed_mast_taxonomy.py
```

### Step 3: Run Phase 2 Live End-to-End Demo

Executes ingestion, pre-analysis annotation, baseline vs. annotated MetaGPT runs, MAST failure tagging, and prints comparative reduction metrics:

```bash
python scripts/run_phase2_demo.py
```

### Step 4: Run Batch Experiments

```bash
python scripts/run_experiment_batch.py
```

### Step 5: Run Manual MAST Tagging Verification

```bash
python scripts/manual_mast_check.py
```

---

## Running the API & Dashboard

### Terminal 1: Start FastAPI Service
```bash
uvicorn specforge.api.main:app --reload
```
Interactive OpenAPI docs available at `http://localhost:8000/docs`. Endpoints include `/experiment/run` and `/experiment/history`.

### Terminal 2: Start Streamlit Dashboard
```bash
streamlit run scripts/dashboard.py
```
Open `http://localhost:8501` to view the Diagnostic tab and the new **MAS Experiments** tab with side-by-side category failure charts and headline reduction metrics.

---

## Implementation Status

### ✅ Phase 1: DONE (Implemented & Verified)
- **Scaffolding & DB Layer**: SQLAlchemy ORM with `Requirements`, `RITTaxonomy`, `Classifications`, `AmbiguityFlags`.
- **Taxonomy Seeding**: 6 primary categories + sub-categories with idempotent seeding.
- **Ingestion Engine**: `.txt`, `.docx`, `.pdf`, and raw text loaders.
- **Atomic Preprocessor**: spaCy-based sentence segmentation + modal-verb compound sentence splitter.
- **RIT Classifier**: Few-shot Claude prompt with defensive JSON parsing.
- **Ambiguity Detector**: Multi-smell heuristic checks + LLM ambiguity scoring.
- **Diagnostic Reporter**: JSON annotated specification generator.
- **FastAPI & Streamlit**: Diagnostic endpoints and dashboard.

### ✅ Phase 2: DONE (Implemented & Verified)
- **Extended Database Schema**: 7 total tables (`Requirements`, `RITTaxonomy`, `Classifications`, `AmbiguityFlags`, `MASTTaxonomy`, `MASRuns`, `FailureLogs`).
- **MAST Taxonomy Seeding**: Idempotent seeding of 14 published failure modes across 3 categories.
- **MAS Adapter Layer**: `MASAdapter` abstract base class and `MetaGPTAdapter` concrete integration with non-invasive prompt augmentation.
- **Failure Logging Layer**: `annotate_trace_with_mast` LLM-as-a-judge trace evaluator using Claude system prompt and defensive parsing.
- **Comparative Experiment Runner**: `run_comparative_experiment` executing baseline vs. annotated runs and computing failure reduction metrics.
- **API & Dashboard Extensions**: `POST /experiment/run`, `GET /experiment/history`, and Streamlit "MAS Experiments" tab with category breakdown bar charts and average reduction metric.
- **Demo Script**: `scripts/run_phase2_demo.py` wiring end-to-end execution.

### ⏳ Future Phases (Planned for Phase 3+)
- **Additional MAS Adapters**: ChatDev and MARE adapters (reusing `MASAdapter` abstract interface).
- **Statistical Evaluation Engine**: Chi-square tests, bootstrap confidence intervals across 15-20 benchmark projects.
- **Fine-tuned BERT Ablation**: Fine-tuning local transformer models for offline classification.
