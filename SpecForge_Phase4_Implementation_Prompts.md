# SpecForge AI — Phase 4 Implementation Prompt Pack

**Builds on:** Phases 1-3, all assumed complete — ingestion through RIT
classification, ambiguity detection, MetaGPT/ChatDev adapters, MAST-based
failure logging, the MARE comparison module, the full evaluation batch, and
the statistical correlation engine (chi-square, point-biserial, bootstrap CI).

**Scope this phase:** P8 (related-work differentiation write-up + thesis
drafting support) + P9 (final polish, reproducibility packaging, viva/defense
prep). This phase produces almost no new features — it turns three phases of
working code into something you can hand in and defend.

**A different rhythm than before:** Prompts 0-3 are still for Claude Code —
real automation work (cleanup, testing, packaging, auto-generating figures).
Prompts 4-6 ask the agent to draft *text* (related-work comparison, threats
to validity, a question bank) — treat everything it produces there as a
first draft for you to personally read, verify against your actual results,
and rewrite in your own voice before it goes anywhere near your thesis. An
examiner asking a follow-up question about a paragraph you didn't actually
absorb is the single easiest way to lose credibility in a viva.

---

## Prompt 0 — Codebase polish pass

```
Context: SpecForge AI's codebase spans Phases 1-3: ingestion, preprocessing,
RIT classification, ambiguity detection, reporting, the FastAPI app, the
Streamlit dashboard, MAST taxonomy, MetaGPT/ChatDev adapters, failure
logging, the MARE comparison module, batch running, and the correlation
engine. Before writing anything up, do a full cleanup pass — no new features,
no behavior changes.

1. Run a linter/formatter across the whole codebase (black + ruff, or
   flake8 + isort if you prefer — pick one toolchain and apply it
   consistently) and fix everything it flags.

2. Add or complete docstrings on every public function and class across all
   specforge/ modules — one-line summary, Args, Returns, and a note of any
   side effects (DB writes, file writes, external API calls), since a
   reader unfamiliar with the codebase (e.g. an examiner skimming your
   appendix) should be able to understand each function without reading its
   body.

3. Search for and remove dead code, commented-out blocks, and leftover
   debug print statements across all modules.

4. Audit error handling: every external call (Claude API, subprocess calls
   to MetaGPT/ChatDev/MARE, file I/O) should fail with a clear, specific
   exception message, not a bare crash or a silently swallowed exception.
   Fix any bare `except:` or `except Exception: pass` blocks you find.

5. Pin exact versions in requirements.txt (currently likely has loose
   version specifiers) by running `pip freeze` in your working environment
   and reconciling it into a clean, minimal, exact-pinned requirements.txt —
   remove anything not actually imported anywhere in specforge/ or tests/.

6. Run the full fast test suite (`pytest -v -m "not integration"`) after
   every step above and confirm nothing broke. Report final pass/fail counts.

Do not modify test files' assertions to make failing tests pass — if a test
fails after cleanup, find and fix the actual regression.
```

---

## Prompt 1 — Test coverage push + CI

```
Context: Codebase is cleaned up and the fast test suite passes. Now measure
and improve coverage, and wire up continuous integration so this doesn't
silently regress before your final submission.

1. Add pytest-cov to requirements.txt. Run `pytest --cov=specforge
   --cov-report=term-missing -m "not integration"` and report the current
   coverage percentage and which modules are weakest.

2. For any module below 70% coverage (excluding the mas_adapter Docker/
   subprocess code, which is inherently hard to unit test and is already
   covered by the integration-marked tests), add targeted unit tests for the
   untested branches — especially error-handling paths (what happens when
   the Claude API returns malformed JSON, when a file path doesn't exist,
   when a foreign key doesn't resolve).

3. Create .github/workflows/tests.yml: a GitHub Actions workflow that, on
   every push and pull request, sets up Python 3.10+, installs
   requirements.txt, and runs `pytest -v -m "not integration"` (the
   Docker-dependent integration tests should NOT run in CI unless you also
   set up Docker-in-Docker, which is out of scope here — just make sure the
   fast suite runs automatically and the workflow fails the build if any
   test fails).

4. Add a coverage badge or summary step to the workflow output so coverage
   is visible on every PR/commit, not just something you check manually.

Confirm: final coverage percentage, and that the CI workflow YAML is valid
(you can validate it locally with `actionlint` if available, or just
carefully review the syntax).
```

---

## Prompt 2 — Reproducibility packaging

```
Context: Codebase is clean, tested, and covered by CI. An examiner or your
guides should be able to take this repository and reproduce every result in
your thesis without asking you clarifying questions. Package for that.

1. Create a single Makefile (or scripts/reproduce_all.sh if you prefer
   shell scripts over Make) with clearly named targets/sections for every
   major reproducible step across all phases:
   - setup: create venv, install requirements, run init_db + seed_taxonomy
     + seed_mast_taxonomy
   - test: run the fast test suite
   - demo-phase1 / demo-phase2 / demo-phase3: run each phase's existing
     demo script
   - run-full-batch: run the complete 15-20 task evaluation batch
     (warn in a comment that this takes hours and needs Docker + API budget)
   - evaluation-report: generate the final Markdown/figures from a
     completed batch
   - dashboard: start the API and Streamlit dashboard together

2. Finalize docker-compose.yml so `docker compose up` brings up the main
   app, MetaGPT, and ChatDev services correctly with the right
   volumes/networks — test this actually works from a clean checkout, not
   just on a machine that already has partial state from development.

3. Write a single canonical README.md restructured with these sections, in
   this order: Project Summary, Architecture Diagram, Quickstart (the
   shortest possible path from clean clone to seeing a result), Full Setup,
   Reproducing Every Result By Phase, Repository Structure, Known
   Limitations (a pointer to Prompt 5's output), Citation/Attribution
   (MAST taxonomy — Cemri et al. 2025; MARE — Jin et al. 2024; any other
   external code/frameworks used).

4. Add a LICENSE file if one doesn't exist (check with your guides what your
   university/department expects for capstone code — MIT is a common
   permissive default if there's no institutional requirement).

5. Do a final clean-checkout test: clone the repo into a completely new
   directory (or at minimum simulate it by removing all __pycache__, venv,
   and local DB files) and follow your own README's Quickstart section
   exactly as written, fixing anything that doesn't work as documented.

Confirm: the exact sequence of commands a stranger would need to go from
`git clone` to seeing the Phase 3 demo output, and that you've personally
verified this sequence works.
```

---

## Prompt 3 — Auto-generate thesis artifacts from stored data

```
Context: A completed (or near-complete) evaluation batch exists in the
database with all correlation engine results computable via
build_evaluation_report(batch_id). Instead of manually copying numbers into
your thesis, generate publication-ready artifacts directly from real data.

Create specforge/thesis_export/ with a script generate_thesis_artifacts.py
that, given a batch_id, produces into a thesis_artifacts/ folder:

1. Figures (matplotlib, saved as both .png at 300 DPI and .svg for LaTeX):
   - The RIT label distribution bar chart
   - The MAST failure category distribution, baseline vs annotated,
     side-by-side bars
   - The ambiguity score vs. failure occurrence box/violin plot
   - The chi-square contingency table rendered as a heatmap
   - A bootstrap distribution histogram for the failure-reduction estimate,
     with the CI bounds marked as vertical lines

2. Tables, exported as both CSV and a ready-to-paste LaTeX tabular snippet
   (use pandas' to_latex or write it manually if you need more control):
   - Per-task summary: task name, framework, baseline failures, annotated
     failures, % reduction
   - The RIT taxonomy definitions table (for an appendix)
   - The MAST taxonomy summary table (14 modes, 3 categories, with a
     citation note — for an appendix)
   - The MARE comparison results (completeness/structure/ambiguity scores,
     SpecForge vs MARE, per task)

3. A single manifest.md listing every generated file with a one-line
   caption suggestion for each, so when you're writing the thesis you can
   go figure-by-figure rather than hunting through the folder.

Add a pytest test in tests/test_thesis_export.py that runs this against a
small synthetic batch (reuse the synthetic data pattern from
tests/test_correlation_engine.py) and asserts every expected file actually
gets created and is non-empty.

Run this for real against your actual completed batch and confirm the
figures look sensible before trusting them in your thesis draft — a script
producing a beautiful chart from buggy data is worse than no chart.
```

---

## Prompt 4 — Related-work differentiation draft (P8)

```
Context: You have real comparison data from specforge/comparison/
(SpecForge vs MARE) and real citations already gathered across Phases 1-3:
Vogelsang 2024 (prompts as requirements), Femmer et al. 2017 (requirements
smells), Frattini et al. 2022 (quality factor ontology), Cemri et al. 2025
(MAST), Jin et al. 2024 (MARE), plus GitHub Spec Kit / AWS Kiro / OpenSpec
as industry-side related work discussed earlier in this project's planning.

Draft a related-work section (aim for 1000-1500 words, structured, not a
list of one-line paper summaries) covering:

1. Classical Requirements Engineering quality research (Femmer, Frattini) —
   what "requirements smells" and quality ontologies establish, and how RIT
   + the ambiguity detector build on rather than duplicate this work.

2. LLM-based Requirements Engineering assistance (Vogelsang, MARE) — draw
   the distinction clearly and honestly: MARE automates the RE process
   itself with agent collaboration; SpecForge diagnoses and annotates
   requirements BEFORE they reach a downstream multi-agent coding system,
   then measures the downstream effect. Use the actual comparison data from
   Prompt 3/specforge/comparison/ to make specific, evidenced claims here —
   not generic statements like "SpecForge is more machine-readable" without
   a number backing it up.

3. Multi-agent system failure analysis (Cemri et al./MAST) — explain that
   SpecForge is, as far as your literature search found, among the first to
   apply MAST's failure taxonomy as a DOWNSTREAM EVALUATION METRIC for a
   requirements-quality intervention, rather than purely as a diagnostic
   tool for the MAS itself. State this claim carefully and only as strongly
   as your actual literature search supports — do not claim novelty you
   haven't verified; flag it as "to the best of our knowledge" language,
   standard academic hedging, rather than an absolute claim.

4. Industry spec-driven development tools (GitHub Spec Kit, AWS Kiro,
   OpenSpec) — position SpecForge as academically validating and extending
   a direction the industry is independently converging on, with SQS-style
   scoring and MAST-based failure correlation as the parts that go beyond
   what these tools currently offer publicly.

Write this as a genuine first draft in academic prose, but flag clearly at
the top: "DRAFT — verify every specific claim against the actual underlying
paper/data before using in the thesis; do not cite anything here without
having read the source yourself."
```

---

## Prompt 5 — Limitations and threats to validity (P8/P9)

```
Context: All experimental infrastructure and results exist. Every capstone
needs an honest limitations section — examiners specifically probe here, so
this needs to be based on real decisions made in this codebase, not generic
boilerplate.

Draft a "Limitations and Threats to Validity" section covering, at minimum,
these categories the implementation actually involves — pull the specific
detail from the real code/config, don't write generically:

1. Sample size — n=15-20 tasks is small for chi-square/point-biserial
   significance; state the actual n used and what that means for the
   confidence interval widths actually observed in your results.

2. Single LLM family dependency — classification, ambiguity scoring, and
   MAST failure tagging all rely on the Claude API (state which model
   version was actually used, from config.py); results may not generalize
   to other LLM families without re-validation.

3. MARE reimplementation risk (if Prompt 1 of this pack's Phase 3 work used
   a reimplementation rather than the original authors' code) — explicitly
   state this and its implication: differences from the original MARE
   paper's reported numbers could reflect reimplementation gaps, not a true
   limitation of MARE itself.

4. LLM-as-judge reliability for MAST tagging — you're relying on MAST's own
   authors' validated methodology (94% accuracy, Cohen's Kappa 0.77 in
   their paper) but have not run your own inter-annotator agreement study
   against human labels; state this as an open validity question.

5. Task selection bias — the 15-20 evaluation tasks were authored by the
   project team, not sourced from real industry requirements documents;
   discuss what this means for external validity/generalization.

6. Non-invasive architecture assumption — the "annotation-only" adapter
   design assumes MetaGPT/ChatDev's own internal behavior doesn't change in
   ways unrelated to the annotation (e.g. model API rate limits, version
   drift in the underlying LLM used BY MetaGPT/ChatDev themselves between
   baseline and annotated runs if they weren't run back-to-back) — flag
   this as a controlled-conditions caveat.

7. Timeout/failure classification — note that the mas_adapter run() timeout
   (20 minutes) means some legitimate slow-but-correct runs get logged as
   failed_to_run, which could bias failure counts; state this explicitly.

Write each point as 2-4 honest sentences, not a bullet with no elaboration —
examiners respect a well-reasoned limitation far more than a hidden one.
```

---

## Prompt 6 — Viva/defense question bank consolidation

```
Context: Across Phases 1-3, this project's planning generated several
"if asked X" answers for anticipated review questions. Consolidate every
one of those into a single master document, and extend it with the harder
questions specific to a final viva rather than an interim progress review.

Create VIVA_PREP.md at the repo root, structured by theme, pulling forward
every "if asked" answer already established in this project's phase
documents (Phase 1: why isn't MAS integration done; Phase 2: why only
MetaGPT, is this statistically significant, how do you know MAST tagging is
accurate; Phase 3: why isn't MARE run the same way, are these results
significant, what's left) and add NEW questions specific to final defense:

1. "What is your single strongest, most defensible research contribution?"
   — answer using the actual RIT taxonomy + ambiguity detector + its
   measured downstream effect on MAST failure rates, with the real numbers
   from your completed batch, not the ambitions from the original design doc.

2. "What would you do differently if you started over?" — answer honestly
   based on what actually took longer/was harder than planned across
   Phases 1-3 (be specific: was it the MetaGPT container setup? classifier
   prompt tuning? the MARE reimplementation decision?).

3. "How is this different from just using GitHub Spec Kit or AWS Kiro?" —
   answer using the actual differentiator: SpecForge measures the causal
   effect of specification quality on downstream multi-agent failure rates
   using a published failure taxonomy, which these industry tools do not
   publicly report doing.

4. "Why did you choose Claude specifically, and would results differ with
   GPT-4 or an open model?" — answer honestly: pragmatic choice for
   consistency and API quality; acknowledge as a limitation (already
   covered in Prompt 5) rather than defending it as objectively optimal.

5. "Walk me through what happens, end to end, for one single requirement
   sentence, from upload to final report" — this should be a question you
   can answer without looking at the code, tracing: ingestion → segmentation
   → RIT classification → ambiguity scoring → annotation → MAS run
   (baseline + annotated) → failure tagging → correlation analysis →
   dashboard. Write this walkthrough out in full in the document.

6. Any question about a specific number in your results tables — the
   document should note: "Before the viva, re-run generate_thesis_artifacts
   and re-read every number in thesis_artifacts/ so you can defend each one
   from memory, not just recognize it."

This file is explicitly a study aid for the team, not thesis content — keep
it direct and in plain language, not academic prose.
```

---

## Prompt 7 — Final end-to-end verification

```
Context: This is the last prompt in the project's implementation plan. All
code, tests, documentation, thesis artifacts, and viva prep exist.

1. From a completely clean checkout (new directory, fresh clone), run
   through the Makefile/reproduce_all.sh targets in order: setup, test,
   demo-phase1, demo-phase2, demo-phase3, and (if time/budget allows)
   run-full-batch followed by evaluation-report. Fix anything that fails —
   this is the last chance to catch an environment-dependent bug before
   submission.

2. Run `pytest --cov=specforge -m "not integration"` one final time and
   record the final coverage percentage for your thesis's implementation
   chapter.

3. Verify every file referenced in README.md's "Reproducing Every Result By
   Phase" section actually exists and actually works as described.

4. Do a final git log review: squash or clean up any obviously broken
   intermediate commits if your institution's submission process looks at
   commit history, and tag a release (e.g. `git tag v1.0-submission`).

Report back: final test count and coverage %, confirmation that a clean
checkout reproduces every phase's demo successfully, and the final list of
thesis_artifacts/ files ready to drop into the write-up.
```

---

## What this phase does NOT include

On purpose — these belong to you and your guides, not to an agent:
- Actually writing the thesis narrative in full (Prompts 4-5 give you
  drafts; the thesis itself needs your own synthesis and voice)
- Deciding your final headline claim/framing for the defense — that's a
  judgment call based on what your real numbers actually showed
- Rehearsing the live demo out loud — do this yourself, more than once,
  including a version where something goes wrong and you talk through it
  calmly instead of panicking

## If asked "why is X not done yet" (final-review version)

- *"Why does the limitations section mention so many caveats — does that
  weaken your contribution?"* → "No — an examiner trusts honestly-scoped
  results more than a project that hides its limitations. Every caveat here
  is a specific, named decision we made and can defend, not something we
  missed."
- *"What's genuinely novel here versus what's assembled from existing
  work?"* → Be precise: the RIT taxonomy, the ambiguity detector, and the
  specific measured correlation between annotation and MAST-tagged failure
  reduction are the contribution; the MAST taxonomy, MARE, MetaGPT, and
  ChatDev are all correctly-cited external work you built on top of, not
  claimed as your own.
