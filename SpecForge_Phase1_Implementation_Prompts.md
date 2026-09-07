# SpecForge AI — Phase 1 (25%) Implementation Prompt Pack

**Team:** Abhavya, Nithya Patel
**Scope:** P1 (done) → P2 (RIT taxonomy) → P3 prototype (diagnostic layer + classifier)
**Explicitly NOT in this phase:** MAS adapter layer (MetaGPT/ChatDev/MARE), Failure Logging, Evaluation & Correlation Engine

## How to use this

Start from a completely empty project folder. Feed the prompts below **in order, one at a time**, to Claude Code (or another agentic coding tool). Each prompt assumes only what the previous ones actually built — don't skip ahead. After each prompt, run whatever it outputs (tests, `uvicorn`, `streamlit run`) before moving to the next one, so you catch problems early instead of at the end.

Each prompt is a complete, self-contained block — copy the whole thing including the context line.

---

## Prompt 0 — Project scaffolding

```
I'm starting a new Python project called SpecForge AI from a completely empty folder.
It's a diagnostic layer that classifies software requirements and flags ambiguity
before they're handed to multi-agent coding frameworks. Set up the project skeleton
only — no business logic yet.

Create:
1. A Python 3.10+ project using this structure:
   specforge/
     __init__.py
     ingestion/
     preprocessing/
     classification/
     ambiguity/
     reporting/
     api/
     db/
     config.py
   tests/
   data/sample_requirements/
   scripts/
   .env.example
   requirements.txt
   pyproject.toml (or setup.cfg — your choice, just be consistent)
   README.md
   .gitignore (Python + Docker + .env + venv + __pycache__)
   Dockerfile
   docker-compose.yml (a single service for now: the app; add a postgres
     service too, commented out, since we start on SQLite and migrate later)

2. requirements.txt should include: fastapi, uvicorn, sqlalchemy, pydantic,
   python-dotenv, anthropic, streamlit, pandas, scikit-learn, scipy, pytest,
   python-multipart, python-docx, pypdf, spacy (or nltk — pick one and
   justify it in a code comment).

3. config.py should load environment variables (ANTHROPIC_API_KEY, DATABASE_URL
   defaulting to a local SQLite file at ./data/specforge.db) using pydantic's
   BaseSettings.

4. README.md should explain: what the project is (one paragraph), how to set
   up a virtual environment, how to install dependencies, how to run tests,
   and how to run the API once it exists (leave a placeholder line for that).

5. Initialize a git repo and make an initial commit.

Do not write any classification, ingestion, or ambiguity logic yet — this
prompt is scaffolding only. Confirm the folder tree at the end.
```

---

## Prompt 1 — Database schema & models

```
Context: SpecForge AI project scaffolding exists (specforge/ package, db/ folder,
config.py with DATABASE_URL). Now implement the database layer for Phase 1 only.

Using SQLAlchemy (declarative ORM, not raw SQL), create models in specforge/db/models.py
for exactly these four tables — do NOT create MAS_Runs, Failure_Logs, or
Evaluation_Metrics tables yet, those belong to a later phase:

1. Requirements
   - requirement_id (PK, string UUID)
   - source_doc_id (string, nullable)
   - raw_text (text)
   - atomic_unit_text (text, nullable — filled in during preprocessing)
   - created_at (datetime, default now)

2. RITTaxonomy
   - label_id (PK, string)
   - label_name (string, unique)
   - label_definition (text)
   - parent_category (string, nullable)

3. Classifications
   - classification_id (PK, UUID)
   - requirement_id (FK -> Requirements.requirement_id)
   - label_id (FK -> RITTaxonomy.label_id)
   - confidence_score (float)
   - classifier_version (string)
   - timestamp (datetime, default now)

4. AmbiguityFlags
   - flag_id (PK, UUID)
   - requirement_id (FK -> Requirements.requirement_id)
   - ambiguity_score (float)
   - flag_reason (text)
   - timestamp (datetime, default now)

Also create:
- specforge/db/session.py — a SQLAlchemy engine + session factory reading
  DATABASE_URL from config.py, defaulting to sqlite:///./data/specforge.db
- specforge/db/init_db.py — a script that creates all tables (Base.metadata.create_all)
  and can be run standalone with `python -m specforge.db.init_db`
- A pytest test in tests/test_db.py that: creates an in-memory SQLite DB,
  inserts one row into each of the four tables with valid foreign keys, and
  asserts the round-trip read matches what was written.

Run the test and show me it passing before finishing.
```

---

## Prompt 2 — RIT Taxonomy v1 (seed data)

```
Context: SpecForge's DB models exist, including RITTaxonomy. Now define and
seed the actual Requirement Intent Taxonomy (RIT) — this is the project's
core research contribution, so the categories need real definitions, not
placeholders.

Create specforge/classification/rit_taxonomy.py containing a Python constant
RIT_CATEGORIES: a list of dicts, each with label_id, label_name,
label_definition, and parent_category. Define these six top-level categories
(you may add 2-3 sub-categories under each if it clearly improves precision,
but keep the total under 15 for now):

1. Behavioral Rule — a rule describing what the system must do under a
   specific condition ("if X then Y")
2. State Transition — a description of how an entity moves between states
   (e.g. order status: pending -> shipped -> delivered)
3. Actor Permission — a statement about who is allowed to do what
4. Data Contract — a description of a data field, its type, format, or
   validation rule
5. Integration Constraint — a requirement about how the system interacts
   with an external system, API, or protocol
6. Acceptance Condition — a testable statement of when a feature is
   considered correctly implemented

For each category, write a definition that is precise enough that two
different people classifying the same requirement sentence would agree at
least 80% of the time — this matters because it's what you'll defend in your
evaluation chapter. Include one clear example sentence per category as a
docstring or comment.

Then create scripts/seed_taxonomy.py that loads RIT_CATEGORIES into the
RITTaxonomy table via the session from specforge/db/session.py, skipping
rows that already exist (idempotent — running it twice should not duplicate
rows or error).

Add a pytest test in tests/test_taxonomy_seed.py that runs the seed script
against a temporary SQLite DB and asserts exactly the expected number of
rows exist afterward, and that running it a second time doesn't change the
count.
```

---

## Prompt 3 — Requirement ingestion

```
Context: DB models and RIT taxonomy seeding exist. Now build the ingestion
module that accepts raw requirement documents.

Create specforge/ingestion/loader.py with functions that accept a file path
and return plain text, supporting these input types:
- .txt (plain read)
- .docx (use python-docx; concatenate all paragraph text)
- .pdf (use pypdf; concatenate all page text)
- raw pasted string (a function that just wraps text with no file I/O)

Create specforge/ingestion/service.py with a function `ingest_document(file_path
or raw_text, source_doc_id) -> Requirement` that:
1. Extracts text using the right loader based on file extension
2. Creates a Requirements row with raw_text set, atomic_unit_text left null
   for now (that's the next module's job), and source_doc_id set
3. Saves it via the DB session and returns the created row

Create data/sample_requirements/sample_01.txt containing at least 15 varied,
realistic software requirement sentences (mix of clear and intentionally
vague ones — some with vague quantifiers like "fast" or "user-friendly",
some clearly testable) so later modules have something real to work against.
Write these yourself based on a plausible small software system (e.g. a
food delivery app or a hospital appointment system — pick one and be
consistent) - don't reuse SpecForge's own requirements as the sample data,
keep the test fixture project separate from the tool being built.

Add a pytest test in tests/test_ingestion.py that ingests sample_01.txt and
asserts a Requirements row was created with non-empty raw_text.
```

---

## Prompt 4 — Preprocessing & normalization

```
Context: Ingestion module exists and can create Requirements rows with
raw_text populated. Now build the preprocessing step that segments a raw
document's text into atomic requirement units — one row per single,
indivisible requirement.

Create specforge/preprocessing/segmenter.py with a function
`segment_into_atomic_units(raw_text: str) -> list[str]` that:
1. First splits on sentence boundaries (use spaCy or nltk — whichever you
   installed in Prompt 0 — do NOT just split on periods with string methods,
   that breaks on abbreviations and decimals)
2. Then, for compound sentences joined by "and"/"as well as" that clearly
   describe two separate requirements (e.g. "the system shall log the user
   in and shall send a confirmation email"), further splits them into
   separate atomic units. Use a simple rule-based approach first (look for
   coordinating conjunctions between two verb phrases starting with modal
   verbs like "shall", "must", "will"); if you want to add an LLM-assisted
   fallback for ambiguous cases, put it behind a config flag
   (USE_LLM_SEGMENTATION=false by default) so tests don't require an API key.

Create specforge/preprocessing/service.py with a function
`preprocess_requirement(requirement_id: str)` that:
1. Loads the Requirements row by ID
2. Runs segment_into_atomic_units on its raw_text
3. For a single-sentence requirement, just sets atomic_unit_text to the
   cleaned sentence
4. For a multi-sentence document, creates ADDITIONAL Requirements rows (one
   per atomic unit) all pointing to the same source_doc_id, and sets
   atomic_unit_text on each

Add a pytest test in tests/test_preprocessing.py using at least 3 example
inputs: one already-atomic sentence, one compound sentence that should
split into two, and one multi-sentence paragraph. Assert the expected
number of atomic units comes out of each case.
```

---

## Prompt 5 — RIT Intent Classifier (core contribution)

```
Context: Requirements can now be ingested and segmented into atomic units.
RIT taxonomy is seeded in the DB. Now build the classifier — this is
SpecForge's primary research contribution, so make it clean and well-tested.

Create specforge/classification/classifier.py with a function
`classify_requirement(atomic_unit_text: str) -> dict` that:
1. Loads the current RIT_CATEGORIES definitions (from rit_taxonomy.py)
2. Builds a few-shot prompt for the Claude API (use the `anthropic` package,
   model "claude-sonnet-4-6", read the API key from config.py) that:
   - Lists all RIT categories with their definitions in the system prompt
   - Includes 1-2 worked examples per category as few-shot demonstrations
   - Asks the model to classify the given atomic requirement into exactly
     one category, and return a confidence score 0.0-1.0
   - Forces structured JSON output: {"label_name": str, "confidence": float,
     "rationale": str} — instruct the model to output ONLY valid JSON, no
     preamble or markdown fences, and parse it defensively (strip fences if
     present, catch JSON errors and retry once with a stricter instruction
     before raising)
3. Returns the parsed dict

Create specforge/classification/service.py with a function
`classify_and_store(requirement_id: str, classifier_version="rit-v1-fewshot")`
that:
1. Loads the Requirements row
2. Calls classify_requirement on its atomic_unit_text
3. Looks up the matching RITTaxonomy row by label_name
4. Creates a Classifications row with the result and saves it

Add a pytest test in tests/test_classifier.py that mocks the Anthropic API
call (do not make real API calls in tests — use unittest.mock to return a
canned JSON response) and asserts classify_and_store creates a correctly
populated Classifications row. Separately, add a small standalone script
scripts/manual_classify_check.py that DOES call the real API against the
15 sample requirements from sample_01.txt and prints each one next to its
predicted label and confidence — this is what you'll actually run live
during your review to show it working.
```

---

## Prompt 6 — Ambiguity Detection Module

```
Context: Classifier exists and is tested. Now build the ambiguity detector —
SpecForge's secondary research contribution.

Create specforge/ambiguity/heuristics.py with a function
`heuristic_ambiguity_score(text: str) -> dict` that checks for known
"requirements smells" and returns a score plus reasons. Implement checks for
at least:
1. Vague quantifiers/adjectives with no measurable value ("fast", "scalable",
   "user-friendly", "several", "appropriate", "as needed" — keep this list
   in a constant so it's easy to extend)
2. Passive voice without a named actor ("the data will be processed" — who
   processes it?)
3. Missing measurable acceptance value (a sentence implying a threshold —
   "quickly", "efficiently" — without a number attached)
Each check should contribute a partial score; combine them into a single
0.0-1.0 ambiguity_score, and return which specific smells were found as a
list of strings (this becomes flag_reason).

Create specforge/ambiguity/llm_scorer.py with a function
`llm_ambiguity_score(text: str) -> dict` that asks Claude to rate the same
text's ambiguity 0.0-1.0 with a short rationale, independent of the
heuristic approach — same structured-JSON-output pattern as Prompt 5, and
mock it the same way in tests.

Create specforge/ambiguity/service.py with `detect_and_store(requirement_id: str)`
that runs BOTH the heuristic and LLM scorer, averages them into a final
ambiguity_score (or takes the max — pick one and justify it in a comment,
since this choice matters for your evaluation later), and stores one
AmbiguityFlags row with flag_reason combining both sets of findings.

Add tests in tests/test_ambiguity.py: one that feeds heuristic_ambiguity_score
an obviously vague sentence and an obviously precise sentence and asserts
the vague one scores higher; one that mocks the LLM call the same way as
Prompt 5's test.
```

---

## Prompt 7 — Diagnostic Report Generator

```
Context: Classification and ambiguity detection both exist and write to the
DB. Now build the module that packages both into a single annotated
specification — this is the artifact that would eventually be handed to a
MAS framework (that handoff itself is Phase 4, not now).

Create specforge/reporting/annotator.py with a function
`generate_annotated_spec(source_doc_id: str) -> dict` that:
1. Loads every Requirements row for the given source_doc_id
2. For each, joins its latest Classifications row and latest AmbiguityFlags
   row
3. Returns a single JSON-serializable dict shaped like:
   {
     "source_doc_id": "...",
     "generated_at": "<ISO timestamp>",
     "requirements": [
       {
         "requirement_id": "...",
         "atomic_unit_text": "...",
         "rit_label": "...",
         "rit_confidence": 0.0,
         "ambiguity_score": 0.0,
         "ambiguity_reasons": ["..."]
       },
       ...
     ],
     "summary": {
       "total_requirements": N,
       "label_distribution": {"Behavioral Rule": N, ...},
       "high_ambiguity_count": N   # count where ambiguity_score > 0.6
     }
   }

Add a function `save_annotated_spec(source_doc_id, output_path)` that writes
this dict as pretty-printed JSON to disk.

Add a pytest test in tests/test_annotator.py that seeds a tiny in-memory DB
with 3 fake Requirements + Classifications + AmbiguityFlags rows and asserts
the generated dict has the right shape and correct summary counts.
```

---

## Prompt 8 — FastAPI backend

```
Context: All core modules (ingestion, preprocessing, classification,
ambiguity, reporting) exist and are individually tested. Now wire them
together behind a minimal FastAPI service — this is what you'll demo live.

Create specforge/api/main.py with a FastAPI app exposing:
1. POST /ingest — accepts a file upload (multipart) or raw text, calls
   ingest_document, then preprocess_requirement on the result, returns the
   list of created requirement_ids
2. POST /classify/{requirement_id} — calls classify_and_store, returns the
   classification result
3. POST /ambiguity/{requirement_id} — calls detect_and_store, returns the
   ambiguity result
4. POST /process/{source_doc_id} — a convenience endpoint that runs
   classify_and_store AND detect_and_store for every requirement under that
   source_doc_id (i.e. the full pipeline in one call)
5. GET /report/{source_doc_id} — calls generate_annotated_spec and returns
   it as JSON
6. GET /health — returns {"status": "ok"} for a basic liveness check

Wire this into a runnable app: `uvicorn specforge.api.main:app --reload`
should work from the project root once dependencies are installed and
init_db + seed_taxonomy have been run.

Add a pytest test in tests/test_api.py using FastAPI's TestClient that
walks through the full flow against an in-memory/temp SQLite DB: ingest the
sample text, hit /process, then hit /report, and assert the report contains
the expected number of requirements. Mock any real Anthropic API calls the
same way as previous prompts.

Update README.md with the actual run instructions for the API (replace the
placeholder from Prompt 0).
```

---

## Prompt 9 — Streamlit dashboard

```
Context: FastAPI backend is running and exposes /report/{source_doc_id}.
Now build the minimal visualization dashboard described in the design doc.

Create scripts/dashboard.py, a Streamlit app that:
1. Has a text input for a source_doc_id and a "Load Report" button that
   calls the running FastAPI /report/{source_doc_id} endpoint (use
   `requests`, with the base URL read from an environment variable
   defaulting to http://localhost:8000)
2. Displays a bar chart of the RIT label distribution (st.bar_chart from
   the summary.label_distribution field)
3. Displays a table of all requirements with columns: atomic_unit_text,
   rit_label, rit_confidence, ambiguity_score — sorted by ambiguity_score
   descending, so the most concerning requirements surface first
4. Highlights (e.g. colored background via pandas Styler, or just a
   separate "High Ambiguity" table) any requirement with ambiguity_score > 0.6
5. Shows the summary counts (total requirements, high ambiguity count) as
   Streamlit metrics (st.metric) at the top

This should be runnable with `streamlit run scripts/dashboard.py` while the
FastAPI server is running separately. Update README.md with these run
instructions too.

No test needed for the Streamlit file itself (UI code) — but add a short
tests/test_dashboard_helpers.py if you factor any pure data-transformation
logic (e.g. sorting/filtering the requirements list) out of the Streamlit
script into a testable helper function, which is good practice anyway.
```

---

## Prompt 10 — End-to-end demo wiring + docs

```
Context: Every module (ingestion → preprocessing → classification →
ambiguity → reporting), the FastAPI backend, and the Streamlit dashboard
all exist and are individually tested. This is the final Phase-1 prompt —
tie it all together for a live review demo.

1. Create scripts/run_full_pipeline_demo.py: a single script that, against
   a fresh local SQLite DB, in order: runs init_db, runs seed_taxonomy,
   ingests data/sample_requirements/sample_01.txt, preprocesses it into
   atomic units, classifies every unit, runs ambiguity detection on every
   unit, generates the annotated report, and pretty-prints a short summary
   to the console (total requirements, label distribution, how many flagged
   high-ambiguity, and the 3 most ambiguous requirements by text). This
   should be runnable with zero setup beyond `pip install -r requirements.txt`
   and a valid ANTHROPIC_API_KEY in .env.

2. Run the full pytest suite (`pytest -v`) and fix anything failing so the
   whole test suite passes cleanly end to end.

3. Rewrite README.md top-to-bottom with: project description, architecture
   diagram (ASCII is fine), setup instructions, how to run the demo script,
   how to run the API + dashboard together, how to run tests, and a short
   "What's implemented in Phase 1 vs. what's planned for later phases"
   section that explicitly lists: DONE (ingestion, preprocessing,
   classification, ambiguity detection, reporting, API, dashboard) vs.
   NOT YET (MAS adapter layer for MetaGPT/ChatDev/MARE, failure logging,
   evaluation & correlation engine, fine-tuned BERT ablation).

4. Commit everything with a clear commit message.

Confirm at the end: how many requirements/modules exist, how many tests
pass, and give me the exact three commands needed to run the live demo
(init/seed, start API, start dashboard).
```

---

## What to actually show on review day

Run, in order, live:
1. `python scripts/run_full_pipeline_demo.py` — console output showing the pipeline working end-to-end on 15 real sample requirements
2. `uvicorn specforge.api.main:app --reload` in one terminal, then `streamlit run scripts/dashboard.py` in another
3. Load the report in the dashboard — show the RIT label distribution chart and the ambiguity-sorted table live

## If asked "why is X not done yet"

- *"Where's the MAS integration?"* → "That's Phase 4, months 4–6 — it depends on validating the classifier and ambiguity module first, which is what this demo shows working."
- *"Where's the evaluation/correlation analysis?"* → "That needs baseline-vs-annotated MAS runs to compare against, which come after Phase 4. Right now we're proving the annotation layer itself works correctly."
- *"Is the classifier accurate?"* → Be honest: "We haven't run formal accuracy validation yet — that's part of Phase 7's evaluation methodology — but here's it running live on real examples, and confidence scores are visible per classification."
