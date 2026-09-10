# SpecForge AI — Phase 2 Implementation Prompt Pack

**Builds on:** Phase 1 (Requirement Ingestion → Preprocessing → RIT Classifier →
Ambiguity Detection → Diagnostic Report Generator → FastAPI → Streamlit), assumed complete.

**Scope this phase:** P4 (MAS Adapter Layer, one framework first — MetaGPT) + the
Failure Logging Layer + MAST taxonomy seeding + the first baseline-vs-annotated
experimental run. This is the phase that actually produces your core research result.

**Explicitly NOT in this phase:** ChatDev/MARE adapters (add those by repeating
Prompt 3 with a new framework), the full statistical Evaluation & Correlation
Engine (chi-square, bootstrap CIs — that's P7), spec versioning/diffing, and any
frontend polish beyond what's needed to see results.

## How to use this

Same rule as Phase 1: feed these to Claude Code **in order**, run tests/scripts
after each one before moving to the next. Each prompt assumes the previous
Phase 1 prompt pack was fully completed — ingestion, preprocessing, RIT
classification, ambiguity detection, reporting, the FastAPI app, and the four
DB tables (Requirements, RITTaxonomy, Classifications, AmbiguityFlags) all
exist and work.

---

## Prompt 0 — Extend the DB schema for MAS runs and failures

```
Context: SpecForge AI Phase 1 is complete. The DB has four tables: Requirements,
RITTaxonomy, Classifications, AmbiguityFlags (see specforge/db/models.py). Now
add the tables needed for MAS integration and failure tracking, per the
project's design doc.

Add these SQLAlchemy models to specforge/db/models.py — do NOT modify the
existing four tables' schemas, only add new ones:

1. MASTTaxonomy
   - failure_mode_id (PK, string, e.g. "FM-1.1")
   - category (string — one of: "Specification Issues", "Inter-Agent
     Misalignment", "Task Verification")
   - mode_name (string, e.g. "Disobey Task Specification")
   - mode_definition (text)

2. MASRuns
   - run_id (PK, UUID)
   - source_doc_id (string — links back to the Requirements batch used)
   - framework_name (string, e.g. "metagpt")
   - annotated (boolean — True if this run used SpecForge's RIT+ambiguity
     annotations, False if it's the unmodified baseline)
   - task_description (text — the actual task given to the MAS)
   - run_timestamp (datetime, default now)
   - raw_trace_path (string — file path to the saved raw execution log/trace)
   - status (string — "running" | "completed" | "failed_to_run")

3. FailureLogs
   - failure_id (PK, UUID)
   - run_id (FK -> MASRuns.run_id)
   - mast_failure_mode_id (FK -> MASTTaxonomy.failure_mode_id)
   - failure_description (text — specific to this occurrence)
   - agent_stage (string — which agent/phase it occurred in, e.g. "Coder",
     "Reviewer", "Tester" for MetaGPT)
   - confidence (float — how confident the tagger was, 0.0-1.0)
   - timestamp (datetime, default now)

Update specforge/db/init_db.py so it still creates all seven tables correctly
(the four from Phase 1 plus these three).

Add a pytest test in tests/test_db_phase2.py that inserts one valid row into
each of the three new tables (with correct foreign keys) and reads it back.
Run it and confirm it passes before finishing.
```

---

## Prompt 1 — Seed the MAST taxonomy

```
Context: MASTTaxonomy table exists (Prompt 0). Now seed it with the real,
published MAST (Multi-Agent System Failure Taxonomy) from Cemri et al.,
"Why Do Multi-Agent LLM Systems Fail?" (UC Berkeley, 2025, arXiv:2503.13657) —
this is a real academic taxonomy, not something to invent. Use the exact
14 failure modes below, grouped into their 3 categories, with their published
definitions:

Category: Specification Issues
- FM-1.1 Disobey Task Specification — Failure to adhere to the specified
  constraints or requirements of a given task, leading to suboptimal or
  incorrect outcomes.
- FM-1.2 Disobey Role Specification — Failure to adhere to the defined
  responsibilities and constraints of an assigned role, potentially leading
  to an agent behaving like another.
- FM-1.3 Step Repetition — Unnecessary reiteration of previously completed
  steps in a process, potentially causing delays or errors in task completion.
- FM-1.4 Loss of Conversation History — Unexpected context truncation,
  disregarding recent interaction history and reverting to an antecedent
  conversational state.
- FM-1.5 Unaware of Termination Conditions — Lack of recognition or
  understanding of the criteria that should trigger the termination of the
  agents' interaction, potentially leading to unnecessary continuation.

Category: Inter-Agent Misalignment
- FM-2.1 Conversation Reset — Unexpected or unwarranted restarting of a
  dialogue, potentially losing context and progress made in the interaction.
- FM-2.2 Fail to Ask for Clarification — Inability to request additional
  information when faced with unclear or incomplete data, potentially
  resulting in incorrect actions.
- FM-2.3 Task Derailment — Deviation from the intended objective or focus of
  a given task, potentially resulting in irrelevant or unproductive actions.
- FM-2.4 Information Withholding — Failure to share or communicate important
  data or insights that an agent possesses and that could impact
  decision-making of other agents if shared.
- FM-2.5 Ignored Other Agent's Input — Disregarding or failing to adequately
  consider input or recommendations provided by other agents in the system.
- FM-2.6 Reasoning-Action Mismatch — Discrepancy between the logical
  reasoning process and the actual actions taken by the agent.

Category: Task Verification
- FM-3.1 Premature Termination — Ending a dialogue, interaction, or task
  before all necessary information has been exchanged or objectives have
  been met.
- FM-3.2 No or Incomplete Verification — (Partial) omission of proper
  checking or confirmation of task outcomes or system outputs, potentially
  allowing errors or inconsistencies to propagate undetected.
- FM-3.3 Incorrect Verification — Failure to adequately validate or
  cross-check crucial information or decisions during the iterations.

Create specforge/failure_logging/mast_taxonomy.py with a MAST_FAILURE_MODES
constant (list of dicts: failure_mode_id, category, mode_name, mode_definition)
containing exactly these 14 entries, and scripts/seed_mast_taxonomy.py that
loads them into the MASTTaxonomy table, idempotently (same pattern as
scripts/seed_taxonomy.py from Phase 1 — skip existing rows, safe to re-run).

Add a pytest test in tests/test_mast_seed.py asserting exactly 14 rows exist
after seeding and running it twice doesn't duplicate rows. Also assert the
category counts are 5 / 6 / 3 for the three categories respectively.

In your report/thesis writing later, cite this taxonomy properly: Cemri et al.,
2025, MAST, NeurIPS 2025 — do not present these as your own categories.
```

---

## Prompt 2 — MAS Adapter Layer: abstract interface

```
Context: DB now has all 7 tables, MAST taxonomy is seeded. Before touching any
real MAS framework, build the adapter abstraction so MetaGPT/ChatDev/MARE can
be swapped without changing the rest of SpecForge.

Create specforge/mas_adapter/base.py defining an abstract base class
MASAdapter (using Python's abc module) with these methods that every concrete
adapter must implement:

- prepare_task_input(annotated_spec: dict, task_description: str) -> Any
    Takes SpecForge's annotated spec (the dict shape from
    generate_annotated_spec in Phase 1's reporting module) and the raw task
    description, and returns whatever input format the target MAS framework
    expects. For the baseline (non-annotated) case, this should be callable
    with annotated_spec=None, in which case it returns just the plain task
    description with no annotation injected.

- run(prepared_input: Any, output_dir: str) -> dict
    Actually invokes the MAS framework (e.g. as a subprocess, or via its
    Python API if it has one) and returns a dict with at minimum:
    {"status": "completed"|"failed_to_run", "raw_trace_path": str,
     "duration_seconds": float}. This should write the full raw execution
    log/trace to raw_trace_path so the Failure Logging step can read it later.

- get_framework_name() -> str
    Returns a short identifier like "metagpt".

Create specforge/mas_adapter/service.py with a function
`execute_mas_run(source_doc_id: str, task_description: str, framework_name: str,
annotated: bool) -> str` (returns run_id) that:
1. If annotated=True, calls generate_annotated_spec(source_doc_id) to build
   the annotation; if annotated=False, passes None
2. Looks up the correct concrete adapter by framework_name (use a simple
   registry dict for now — {"metagpt": MetaGPTAdapter}, extendable later)
3. Calls prepare_task_input, then run
4. Creates and saves a MASRuns row with the result

Add a pytest test in tests/test_mas_adapter_base.py using a fake
DummyAdapter(MASAdapter) that just writes a canned log file and returns
status "completed" immediately — this tests the plumbing (service.py) without
needing a real MAS framework installed yet. Confirm this passes.
```

---

## Prompt 3 — MetaGPT adapter (first concrete integration)

```
Context: The MASAdapter abstract base and registry exist and are tested with
a dummy adapter. Now build the real MetaGPT adapter — this is the first
actual multi-agent framework integration, per the design doc's "one at a
time" plan (MetaGPT first, then ChatDev, then MARE later).

1. Add a Dockerfile.metagpt (separate from the main app's Dockerfile, since
   MetaGPT has its own dependency tree that conflicts with SpecForge's) that
   clones MetaGPT (https://github.com/geekan/MetaGPT) at a pinned commit/tag
   (pick the latest stable release tag, not main branch, so results are
   reproducible) and installs its dependencies in an isolated environment.

2. Create specforge/mas_adapter/metagpt_adapter.py implementing MetaGPTAdapter
   (MASAdapter):
   - prepare_task_input: MetaGPT normally takes a single natural-language
     project idea string. For the baseline case, just pass task_description
     through unchanged. For the annotated case, construct an augmented
     prompt string that prepends a structured block listing each atomic
     requirement's RIT label and any ambiguity warnings BEFORE the original
     task description — e.g. "The following requirements have been
     pre-analyzed. Pay special attention to items flagged HIGH AMBIGUITY: ..."
     followed by the original task_description unchanged. Do NOT modify
     MetaGPT's own source code — the annotation must be purely an input
     transformation, consistent with the design doc's non-invasive principle.
   - run: invoke MetaGPT as a subprocess (its CLI entrypoint) inside the
     Docker container, with a timeout (say 20 minutes — these can hang),
     capture stdout/stderr and any generated code/log files into
     raw_trace_path, and return status "completed" or "failed_to_run"
     (network/timeout/crash all count as failed_to_run — log the reason).

3. Register "metagpt" -> MetaGPTAdapter in the adapter registry from Prompt 2.

4. Update docker-compose.yml to add the metagpt service (built from
   Dockerfile.metagpt), on its own network/volume so it doesn't conflict
   with the main app's Python environment.

Add an integration test in tests/test_metagpt_adapter.py — since this needs
Docker and takes real time, mark it with @pytest.mark.integration (so it's
skipped by default in fast test runs) and have it run one small, simple task
end-to-end (e.g. "build a command-line calculator that adds two numbers") in
both annotated and baseline mode, asserting both produce status "completed"
and a non-empty raw_trace_path.

Do not proceed to ChatDev or MARE yet — get MetaGPT fully working first,
since that's the design doc's stated order.
```

---

## Prompt 4 — Failure Logging Layer (LLM-as-judge, MAST-based)

```
Context: MetaGPT adapter can run tasks and produce raw execution traces
(text logs). MAST taxonomy is seeded (14 failure modes). Now build the
component that reads a raw trace and tags it against MAST — this directly
follows the LLM-as-a-judge approach used by MAST's own authors (Cemri et al.
report 94% accuracy, Cohen's Kappa 0.77, using few-shot examples), so build
it the same way rather than inventing a different method.

Create specforge/failure_logging/mast_judge.py with a function
`annotate_trace_with_mast(raw_trace_text: str) -> list[dict]` that:
1. Loads the 14 MAST_FAILURE_MODES definitions (from Prompt 1's module)
2. Builds a prompt for the Claude API that:
   - Lists all 14 failure modes with their category and definition in the
     system prompt
   - Includes the trace text (truncate/chunk if it exceeds a reasonable
     context size — add a simple sliding-window chunking function if needed,
     don't just silently cut it off)
   - Asks the model to identify every distinct failure occurrence in the
     trace, returning a JSON list where each item has:
     {"failure_mode_id": str, "agent_stage": str, "failure_description": str,
      "confidence": float}
   - If NO failures are found, it should return an empty list — do not force
     it to find something
   - Same defensive JSON parsing pattern as Phase 1's classifier (strip
     fences, retry once on parse failure)

Create specforge/failure_logging/service.py with a function
`log_failures_for_run(run_id: str)` that:
1. Loads the MASRuns row, reads its raw_trace_path
2. Calls annotate_trace_with_mast on the trace content
3. For each identified failure, looks up the MASTTaxonomy row and creates a
   FailureLogs row

Add a pytest test in tests/test_mast_judge.py that mocks the Claude API call
(same pattern as Phase 1's classifier test) with a canned trace and canned
JSON response, and asserts log_failures_for_run creates the expected
FailureLogs rows. Separately, add scripts/manual_mast_check.py that runs the
REAL API against 2-3 short example traces you write by hand (base these on
the example failure traces in Cemri et al.'s paper appendix D, rewritten in
your own words — do not copy their trace text verbatim) so you can sanity
check real classifications during your review demo.
```

---

## Prompt 5 — Baseline-vs-annotated experiment runner

```
Context: You can now run MetaGPT on a task with or without SpecForge
annotation (Prompt 3), and tag the resulting trace with MAST failure modes
(Prompt 4). Now build the experiment runner that ties these together into
the core comparison your evaluation depends on.

Create specforge/experiments/runner.py with a function
`run_comparative_experiment(source_doc_id: str, task_description: str,
framework_name: str = "metagpt") -> dict` that:
1. Runs execute_mas_run with annotated=False (baseline), waits for
   completion, then runs log_failures_for_run on that run
2. Runs execute_mas_run with annotated=True (SpecForge-annotated), waits for
   completion, then runs log_failures_for_run on that run
3. Returns a comparison dict:
   {
     "source_doc_id": ...,
     "baseline_run_id": ..., "annotated_run_id": ...,
     "baseline_failure_count": N, "annotated_failure_count": N,
     "baseline_failures_by_category": {...}, "annotated_failures_by_category": {...},
     "baseline_status": ..., "annotated_status": ...
   }

Create scripts/run_experiment_batch.py: a script that takes a small set of
task descriptions (start with 3-5 simple, varied software tasks — e.g. a
calculator, a to-do list API, a simple chat bot — write these yourself,
don't reuse SpecForge's own requirements) tied to real ingested/processed
Requirements documents, runs run_comparative_experiment on each, and prints
a summary table: task | baseline failures | annotated failures | reduction %.

This script is intentionally small-scale for now (full 20-project evaluation
is Phase 3/P7) — the goal here is to prove the comparison mechanism works
end-to-end, not to produce a publishable result yet.

Add a pytest test in tests/test_experiment_runner.py that mocks BOTH the MAS
adapter's run() (return canned "completed" results) and the MAST judge (return
canned failure lists) so this test runs fast with no Docker/API calls, and
asserts the comparison dict has the right shape and correct counts.
```

---

## Prompt 6 — Extend the API and dashboard with MAS results

```
Context: The comparative experiment runner works and is tested. Now expose it
through the API and dashboard so results are visible without reading raw
JSON.

Add to specforge/api/main.py:
1. POST /experiment/run — accepts source_doc_id, task_description,
   framework_name (default "metagpt"); calls run_comparative_experiment;
   returns the comparison dict. Note in the endpoint's docstring that this
   can take several minutes since it invokes a real MAS framework twice.
2. GET /experiment/history — returns all MASRuns with their failure counts,
   most recent first, so past experiments can be reviewed without re-running

Add to scripts/dashboard.py a new "MAS Experiments" section/tab (keep the
Phase 1 "Requirements" tab working as-is) that:
1. Shows a table of past experiment runs: framework, annotated (yes/no),
   status, failure count, timestamp
2. For a selected pair of baseline/annotated runs on the same source_doc_id,
   shows a side-by-side bar chart of failure counts by MAST category
   (Specification Issues / Inter-Agent Misalignment / Task Verification)
3. Shows a single headline metric: overall % reduction in failure count,
   annotated vs baseline, averaged across all completed experiment pairs so far

Add a pytest test in tests/test_api_experiments.py using FastAPI's TestClient
that mocks the underlying experiment runner and asserts /experiment/history
returns correctly shaped data.

Update README.md's "What's implemented" section: move "MAS Adapter Layer
(MetaGPT only)" and "Failure Logging Layer" from NOT YET to DONE, and add a
note that ChatDev/MARE adapters and the full statistical evaluation are still
pending.
```

---

## Prompt 7 — End-to-end Phase 2 demo wiring

```
Context: Every Phase 2 module exists and is tested: MAST taxonomy seeding,
the MetaGPT adapter, the MAST-based failure logger, the comparative
experiment runner, and the API/dashboard views for it.

1. Create scripts/run_phase2_demo.py: against a fresh (or existing) local DB,
   in order: seed MAST taxonomy (if not already seeded), ingest one of the
   sample task requirement documents, run one full comparative experiment via
   run_comparative_experiment, and print a clear before/after summary to the
   console: baseline failure count and category breakdown vs. annotated
   failure count and category breakdown, plus the % reduction.

2. Run the full pytest suite (pytest -v — note that Docker/API-dependent
   integration tests marked @pytest.mark.integration should be excludable
   via `pytest -v -m "not integration"` for a fast default run) and fix
   anything failing.

3. Update README.md: add a "Phase 2" section explaining the MAS adapter +
   failure logging architecture, how to run the MetaGPT container
   (docker compose up metagpt), and how to run the Phase 2 demo script.
   Keep the Phase 1 instructions intact above it.

4. Commit everything with a clear commit message referencing Phase 2.

Confirm at the end: how many total DB tables now exist, how many tests pass
(fast run vs. full run including integration tests), and give the exact
sequence of commands to run the live Phase 2 demo (build/start MetaGPT
container, run seed script, run the demo script).
```

---

## What to actually show for this review

1. `python scripts/run_phase2_demo.py` — live console output showing one task
   run through MetaGPT twice (baseline vs. SpecForge-annotated), with real
   MAST failure counts on each side
2. The dashboard's "MAS Experiments" tab — the side-by-side failure-category
   chart and the headline reduction percentage
3. `python scripts/manual_mast_check.py` — a couple of hand-written example
   traces getting tagged live against the real 14 MAST failure modes, so the
   classifier itself is visibly working, independent of the full pipeline

## If asked "why is X not done yet"

- *"Why only MetaGPT, not ChatDev/MARE?"* → "The design doc calls for
  integrating one framework at a time to validate the adapter pattern before
  replicating it — ChatDev and MARE are the same MASAdapter interface,
  just a new concrete class, planned for the rest of this phase."
- *"Is this result statistically significant?"* → Be honest: "Not yet — this
  is a small-scale proof that the comparison mechanism works end-to-end.
  The formal evaluation with bootstrap confidence intervals across 15-20
  tasks is Phase 3 / P7, which needs this working pipeline as a prerequisite."
- *"How do you know the MAST tagging is accurate?"* → "We're using the same
  LLM-as-a-judge approach MAST's own authors validated (94% accuracy against
  human annotators in their paper) — we haven't run our own inter-annotator
  agreement study yet, that's part of the evaluation methodology in Phase 3."
