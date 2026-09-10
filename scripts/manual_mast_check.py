"""
Manual check script for MAST Failure Logging (LLM-as-a-Judge).
Runs live Anthropic API against synthetic execution traces.

Usage:
    python scripts/manual_mast_check.py
"""

import sys
import os
import json
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from specforge.failure_logging.mast_judge import annotate_trace_with_mast

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SAMPLE_TRACES = [
    {
        "name": "Trace 1: Disobey Specification & Premature Termination",
        "text": """
[MetaGPT Log]
[ProductManager] Preparing PRD for CLI Budget Tracker. Required features: Add Income, Add Expense, Export CSV.
[Architect] Generating architecture diagram and module dependencies.
[Coder] Implementing main.py. Created add_income and add_expense functions. Skipped export_csv function because time was limited.
[Tester] Testing CLI commands. Running add_income: PASS. Running add_expense: PASS.
[Manager] Task marked as completed successfully and finished execution.
"""
    },
    {
        "name": "Trace 2: Ignored Input & Lack of Verification",
        "text": """
[ChatDev Log]
[CEO] Let's build a REST API for user authentication with JWT tokens.
[CTO] Remember to include password hashing using bcrypt before storing passwords in DB.
[Programmer] Writing auth module. Stored password as plain text string in SQLite database without hashing.
[Code Reviewer] Looked over files. Everything looks good, LGTM! No unit tests executed.
[CEO] Project completed.
"""
    }
]


def run_manual_mast_check():
    print("==================================================================")
    print("SpecForge AI — Manual MAST Failure Tagging Check (Live LLM Judge)")
    print("==================================================================\n")

    for trace in SAMPLE_TRACES:
        print(f"--- Evaluating {trace['name']} ---")
        print("Trace Text:\n", trace["text"].strip())
        print("\nCalling MAST LLM Judge...")

        try:
            failures = annotate_trace_with_mast(trace["text"])
            print(f"Identified Failure Count: {len(failures)}")
            print(json.dumps(failures, indent=2))
        except Exception as exc:
            print(f"API Call Error: {exc}")
        print("\n" + "="*66 + "\n")


if __name__ == "__main__":
    run_manual_mast_check()
