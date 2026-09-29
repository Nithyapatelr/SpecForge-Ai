# SpecForge AI — Full Specification Engineering & Evaluation Suite

**Authors:** Abhavya, Nithya Patel  
**Repository:** [https://github.com/Nithyapatelr/SpecForge-Ai](https://github.com/Nithyapatelr/SpecForge-Ai)  
**License:** MIT License

SpecForge AI is an end-to-end diagnostic, pre-analysis annotation, and evaluation framework designed to classify software requirements, detect ambiguity smells, and prevent downstream multi-agent synthesis failures. By injecting structured pre-analysis annotations (RIT requirement taxonomy labels + ambiguity smell flags) into multi-agent framework inputs (MetaGPT, ChatDev), SpecForge systematically reduces execution failures categorized under the 14-mode MAST failure taxonomy (*Cemri et al., UC Berkeley, 2025*).

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
                               │ SQLite Database        │
                               │ (7 Schemas)            │
                               └───────────┬────────────┘
                                           │
                    ┌──────────────────────┴──────────────────────┐
                    │                                             │
                    ▼                                             ▼
      ┌───────────────────────────┐                 ┌───────────────────────────┐
      │ MAS Adapter Layer         │                 │ MAST Failure Logger       │
      │ (MetaGPT & ChatDev)       │                 │ (LLM-as-a-Judge 14 Modes) │
      └─────────────┬─────────────┘                 └─────────────┬─────────────┘
                    │                                             │
                    └──────────────────────┬──────────────────────┘
                                           │
                                           ▼
                               ┌────────────────────────┐
                               │ Evaluation & Thesis    │
                               │ Artifact Exporter      │
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

## Key Taxonomies

### 1. RIT Intent Taxonomy (6 Categories)
- **Behavioral Rule**: Condition-action rules ("if X then system shall Y").
- **State Transition**: Entity state movements ("Scheduled -> Confirmed").
- **Actor Permission**: Role authorization rules ("Only Senior Doctor may...").
- **Data Contract**: Schema, field format, and validation constraints.
- **Integration Constraint**: External API and boundary interactions.
- **Acceptance Condition**: Testable performance or quality thresholds.

### 2. MAST Failure Taxonomy (14 Modes across 3 Categories)
- **Specification Issues** (5 modes): FM-1.1 Disobey Task Spec, FM-1.2 Disobey Role Spec, FM-1.3 Step Repetition, FM-1.4 Loss of History, FM-1.5 Unaware of Termination.
- **Inter-Agent Misalignment** (6 modes): FM-2.1 Conversation Reset, FM-2.2 Fail to Ask Clarification, FM-2.3 Task Derailment, FM-2.4 Information Withholding, FM-2.5 Ignored Input, FM-2.6 Reasoning-Action Mismatch.
- **Task Verification** (3 modes): FM-3.1 Premature Termination, FM-3.2 No/Incomplete Verification, FM-3.3 Incorrect Verification.

---

## Reproduction & Quickstart Guide

### 1. Setup Virtual Environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

make install
python -m spacy download en_core_web_sm
```

### 2. Environment Variables
Copy `.env.example` to `.env` and set your Anthropic API Key:
```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
DATABASE_URL=sqlite:///./data/specforge.db
ANTHROPIC_MODEL=claude-sonnet-4-6
```

### 3. Initialize Database & Seed Benchmark Tasks
```bash
make init-db
make seed
```

### 4. Run Automated Test Suite
```bash
make test
```

### 5. Run Full Evaluation Batch & Generate Thesis Artifacts
```bash
make run-batch
make generate-artifacts
```

### 6. Generate Phase 1 Pilot Evaluation Report
Generates a scientifically rigorous Word document (`SpecForge_AI_Pilot_Evaluation_Report.docx`) showing performance on a held-out split (Items 11-20):
```bash
python -m scripts.generate_pilot_evaluation_report_docx
```

---

## Phase 4 Completion & Held-Out Pilot Evaluation

SpecForge AI implements a full empirical pipeline validated on a 20-item PROMISE NFR pilot set. To ensure scientific rigor and avoid train/test contamination, the evaluation uses a strict held-out split:
- **Tuning Subset (Items 1-10):** Used exclusively for observing failure modes and tuning heuristic weights/keywords.
- **Held-Out Evaluation (Items 11-20):** Locked subset; used only for final scoring.

**Phase 1 Pilot Highlights (Held-Out Set Only):**
- **Inter-Annotator Agreement:** Cohen's $\kappa = 0.9392$
- **RIT Classifier:** 100% Accuracy and Macro F1 on held-out subset.
- **Ambiguity Detector:** 100% Precision/Recall on held-out subset.
- **SCG Engine:** 100% conflict recovery rate (5/5 injected pairs) at $\tau_c = 0.60$.

---

## Reimplementation Disclaimers & Notes

### MARE Framework Implementation
The official MARE paper (*Jin et al., 2024*, arXiv:2405.03256) does not provide a public open-source software repository release. SpecForge includes a faithful, clearly-labeled **Reimplementation** of MARE's 5-agent pipeline (Stakeholder, Collector, Modeler, Checker, Documenter) across 4 stages (Elicitation, Modeling, Verification, Specification) for direct specification quality comparison. Every reimplementation function docstring is explicitly annotated: `"Reimplementation based on Jin et al. 2024 architecture description, not the original authors' code"`.

---

## API & Dashboard

- **FastAPI Backend**: `uvicorn specforge.api.main:app --reload` (Interactive docs at `http://localhost:8000/docs`).
- **Streamlit Dashboard**: `streamlit run scripts/dashboard.py` (Dashboard at `http://localhost:8501`).
