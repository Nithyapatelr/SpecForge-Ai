# SpecForge AI

SpecForge AI is a diagnostic layer that classifies software requirements using a
custom **Requirement Intent Taxonomy (RIT)** and flags ambiguity before requirements
are handed off to multi-agent coding frameworks (MetaGPT, ChatDev, MARE). It ingests
plain-text, `.docx`, and `.pdf` specification documents, segments them into atomic
requirement units, classifies each unit into one of six RIT categories using a
few-shot Claude prompt, scores each unit's ambiguity via both heuristic rules and LLM
scoring, and packages the results into an annotated JSON report with a Streamlit
visualization dashboard.

---

## Setup

### 1. Clone and create a virtual environment

```bash
git clone <repo-url>
cd specforge-ai
python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 3. Configure environment variables

```bash
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY
```

### 4. Initialize the database and seed the RIT taxonomy

```bash
python -m specforge.db.init_db
python scripts/seed_taxonomy.py
```

---

## Running Tests

```bash
pytest -v
```

Tests use an in-memory SQLite database and mock all Anthropic API calls — no API key required.

---

## Running the API

```bash
uvicorn specforge.api.main:app --reload
```

API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

---

## Running the Streamlit Dashboard

In a second terminal (while the API is running):

```bash
streamlit run scripts/dashboard.py
```

---

## Running the End-to-End Demo Script

```bash
python scripts/run_full_pipeline_demo.py
```

Requires `ANTHROPIC_API_KEY` set in `.env`.

---

## What's Implemented (Phase 1)

- ✅ Requirement ingestion (`.txt`, `.docx`, `.pdf`, raw text)
- ✅ Preprocessing & atomic unit segmentation (spaCy + rule-based compound splitting)
- ✅ RIT classification via few-shot Claude prompt
- ✅ Ambiguity detection (heuristic + LLM scorer)
- ✅ Annotated JSON report generation
- ✅ FastAPI REST backend
- ✅ Streamlit visualization dashboard

## Not Yet Implemented (Planned for Later Phases)

- ⏳ MAS adapter layer (MetaGPT / ChatDev / MARE integration) — Phase 4
- ⏳ Failure logging — Phase 4
- ⏳ Evaluation & correlation engine — Phase 7
- ⏳ Fine-tuned BERT ablation study — Phase 7
