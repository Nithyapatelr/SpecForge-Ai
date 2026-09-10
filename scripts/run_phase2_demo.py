"""
Phase 2 End-to-End Demo Script — SpecForge AI.

Executes:
1. Database initialization and MAST taxonomy seeding.
2. Requirement ingestion & preprocessing for a sample project specification.
3. RIT intent classification & ambiguity detection.
4. Comparative MAS execution (Baseline vs. SpecForge-Annotated).
5. MAST failure tagging & LLM judge evaluation.
6. Console reporting of failure reduction metrics and category breakdown.

Usage:
    python scripts/run_phase2_demo.py
"""

import sys
import os
import json
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from specforge.ambiguity.service import detect_and_store
from specforge.classification.service import classify_and_store
from specforge.db.init_db import init_db
from specforge.experiments.runner import run_comparative_experiment
from specforge.ingestion.service import ingest_document
from specforge.preprocessing.service import preprocess_requirement
from scripts.seed_mast_taxonomy import seed_mast_taxonomy
from scripts.seed_taxonomy import seed_taxonomy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_phase2_demo():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print("==================================================================")
    print("SpecForge AI - Phase 2 End-to-End Comparative Demo")
    print("==================================================================\n")

    # 1. Initialize Database & Seed Taxonomies
    init_db()
    seed_taxonomy()
    seed_mast_taxonomy()

    # 2. Ingest Sample Document
    sample_file = os.path.join("data", "sample_requirements", "sample_01.txt")
    doc_id = "sample-phase2-demo"

    if os.path.exists(sample_file):
        print(f"[1/4] Ingesting sample specification file: {sample_file}...")
        initial_req = ingest_document(file_path=sample_file, source_doc_id=doc_id)
    else:
        sample_text = (
            "The system shall allow users to log in securely. "
            "The system should respond quickly to all requests. "
            "Only admin users may modify user permissions."
        )
        print("[1/4] Ingesting sample raw text specification...")
        initial_req = ingest_document(raw_text=sample_text, source_doc_id=doc_id)

    # 3. Preprocess, Classify, & Score Ambiguity
    print("[2/4] Preprocessing atomic units, classifying RIT intent & scoring ambiguity...")
    processed_reqs = preprocess_requirement(initial_req.requirement_id)
    for req in processed_reqs:
        classify_and_store(req.requirement_id)
        detect_and_store(req.requirement_id)

    task_desc = "Build a patient appointment booking CLI tool supporting login and appointment management."

    # 4. Run Comparative Experiment
    print("[3/4] Running Comparative MAS Experiment (MetaGPT)...")
    exp_res = run_comparative_experiment(
        source_doc_id=doc_id,
        task_description=task_desc,
        framework_name="metagpt",
    )

    # 5. Display Console Summary
    print("\n[4/4] ================= DEMO SUMMARY RESULTS =================")
    print(f"Source Doc ID      : {exp_res['source_doc_id']}")
    print(f"Framework Engine   : {exp_res['framework_name']}")
    print(f"Baseline Run Status : {exp_res['baseline_status']} (Run ID: {exp_res['baseline_run_id'][:8]}...)")
    print(f"Annotated Run Status: {exp_res['annotated_status']} (Run ID: {exp_res['annotated_run_id'][:8]}...)")
    print("------------------------------------------------------------------")
    print(f"Baseline Failure Count : {exp_res['baseline_failure_count']}")
    print(f"Annotated Failure Count: {exp_res['annotated_failure_count']}")
    print(f"Overall Failure Reduction : {exp_res['failure_reduction_percentage']:.1f}%")
    print("------------------------------------------------------------------")
    print("MAST Category Failure Breakdown:")
    print("  Category                    | Baseline | Annotated")
    print("  --------------------------------------------------")
    all_cats = set(exp_res['baseline_failures_by_category'].keys()) | set(exp_res['annotated_failures_by_category'].keys())
    for cat in sorted(all_cats):
        b_c = exp_res['baseline_failures_by_category'].get(cat, 0)
        a_c = exp_res['annotated_failures_by_category'].get(cat, 0)
        print(f"  {cat:<27} | {b_c:<8} | {a_c:<8}")
    print("==================================================================\n")


if __name__ == "__main__":
    run_phase2_demo()
