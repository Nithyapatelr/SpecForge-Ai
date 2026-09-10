"""
Batch Experiment Runner — executes comparative experiments across a batch of sample software tasks.

Usage:
    python scripts/run_experiment_batch.py
"""

import sys
import os
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from specforge.ambiguity.service import detect_and_store
from specforge.classification.service import classify_and_store
from specforge.db.init_db import init_db
from specforge.experiments.runner import run_comparative_experiment
from specforge.ingestion.service import ingest_text
from specforge.preprocessing.service import preprocess_requirement
from scripts.seed_mast_taxonomy import seed_mast_taxonomy
from scripts.seed_taxonomy import seed_taxonomy

logging.basicConfig(level=logging.INFO)

SAMPLE_TASKS = [
    {
        "title": "Command-Line Calculator API",
        "spec_text": "The calculator shall add two numbers. The calculator should execute very fast. If invalid input is provided, the system shall display an error.",
    },
    {
        "title": "To-Do List REST Service",
        "spec_text": "The service shall allow users to create tasks. Only admin users can delete completed tasks. Tasks must load in under 1 second.",
    },
    {
        "title": "Simple Chatbot Engine",
        "spec_text": "The chatbot shall respond to user greetings. The chatbot must handle high user load smoothly. Users can reset the conversation.",
    },
]


def run_batch_experiments():
    init_db()
    seed_taxonomy()
    seed_mast_taxonomy()

    print("==================================================================")
    print("SpecForge AI — Batch Comparative Experiments (MetaGPT)")
    print("==================================================================\n")

    results = []

    for task in SAMPLE_TASKS:
        print(f"Processing Task: {task['title']}...")
        doc_id = ingest_text(task["spec_text"])
        req_ids = preprocess_requirement(doc_id)
        for req_id in req_ids:
            classify_and_store(req_id)
            detect_and_store(req_id)

        exp_result = run_comparative_experiment(
            source_doc_id=doc_id,
            task_description=task["spec_text"],
            framework_name="metagpt",
        )
        results.append((task["title"], exp_result))

    print("\n" + "="*70)
    print(f"{'Task Title':<30} | {'Baseline Failures':<18} | {'Annotated Failures':<18} | {'Reduction %':<10}")
    print("="*70)

    for title, res in results:
        b_f = res["baseline_failure_count"]
        a_f = res["annotated_failure_count"]
        red = res["failure_reduction_percentage"]
        print(f"{title:<30} | {b_f:<18} | {a_f:<18} | {red:<9.1f}%")

    print("="*70 + "\n")


if __name__ == "__main__":
    run_batch_experiments()
