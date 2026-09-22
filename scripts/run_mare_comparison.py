"""
Head-to-head comparison script running SpecForge AI and MARE on benchmark tasks,
scoring outputs on Completeness, Structure, and Ambiguity.
"""

import os
import json
import tempfile
from specforge.ingestion.service import ingest_document
from specforge.preprocessing.service import preprocess_requirement
from specforge.classification.service import classify_and_store
from specforge.ambiguity.service import detect_and_store
from specforge.reporting.annotator import generate_annotated_spec
from specforge.comparison.mare_runner import run_mare_on_task
from specforge.comparison.spec_quality_comparator import compare_specifications


BENCHMARK_TASKS = [
    {
        "doc_id": "task_calc_01",
        "title": "Command-Line Calculator App",
        "raw_text": (
            "The system shall provide a command-line calculator app. "
            "It must execute fast and calculate sum, difference, product, and quotient. "
            "Input arguments should be validated gracefully without crashing. "
            "The system shall log errors appropriately."
        ),
        "ground_truth_checklist": [
            "Command line interface for mathematical calculations",
            "Addition, subtraction, multiplication, and division operations",
            "Input argument validation and error handling for invalid input",
            "Division by zero handling",
            "Execution error logging and status output",
            "Fast performance response under standard workload",
            "Floating point and integer number support",
            "Non-crashing exception management",
            "User help menu and usage guidance",
            "Return status code compliance",
        ],
    },
    {
        "doc_id": "task_auth_02",
        "title": "User Authentication API Service",
        "raw_text": (
            "The system shall provide user authentication via JWT tokens. "
            "Users should be able to log in with email and password seamlessly. "
            "Passwords must be hashed using bcrypt with salt. "
            "The system shall enforce rate limiting on login attempts to prevent brute force attacks."
        ),
        "ground_truth_checklist": [
            "User login endpoint accepting email and password credentials",
            "JSON Web Token (JWT) generation and session verification",
            "Secure password hashing with bcrypt and salt",
            "Rate limiting mechanism against brute force attacks",
            "Invalid credential error handling and error messages",
            "Seamless user authentication workflow",
            "Token expiration and refreshment policy",
            "User role and access control permissions",
            "Audit log recording for login attempts",
            "HTTPS transmission security requirement",
        ],
    },
    {
        "doc_id": "task_taskmgr_03",
        "title": "Task Manager Backend API",
        "raw_text": (
            "The system shall allow users to create, read, update, and delete tasks. "
            "Task items must contain a title, description, priority level, and due date. "
            "The system should query tasks efficiently and support filtering by priority. "
            "Task records shall be stored in a SQLite or PostgreSQL database."
        ),
        "ground_truth_checklist": [
            "CRUD endpoints for task item creation, retrieval, updating, and deletion",
            "Task data model containing title, description, priority, and due date",
            "Task filtering capability by priority level",
            "Database storage using SQLite or PostgreSQL ORM",
            "Efficient database query performance",
            "Unique task ID generation and primary key tracking",
            "Task status tracking (pending, in-progress, completed)",
            "Pagination support for task list endpoints",
            "Validation for mandatory fields like task title",
            "Timestamp fields for created_at and updated_at",
        ],
    },
]


def run_specforge_on_task(doc_id: str, raw_text: str) -> dict:
    """Run full SpecForge ingestion, preprocessing, classification, and ambiguity pipeline."""
    req = ingest_document(raw_text=raw_text, source_doc_id=doc_id)
    
    # Preprocess atomic units
    processed_reqs = preprocess_requirement(req.requirement_id)
    
    for r in processed_reqs:
        # Classify RIT intent
        classify_and_store(r.requirement_id)
        # Detect ambiguity smells
        detect_and_store(r.requirement_id)

    # Generate annotated spec report
    annotated_spec = generate_annotated_spec(doc_id)
    return annotated_spec


def main():
    print("=" * 80)
    print("SPECFORGE AI vs MARE — HEAD-TO-HEAD SPECIFICATION QUALITY EVALUATION")
    print("=" * 80)

    summary_results = []

    for task in BENCHMARK_TASKS:
        doc_id = task["doc_id"]
        title = task["title"]
        raw_text = task["raw_text"]
        checklist = task["ground_truth_checklist"]

        print(f"\nProcessing Task: [{doc_id}] {title}...")

        # 1. Run SpecForge
        sf_spec = run_specforge_on_task(doc_id, raw_text)

        # 2. Run MARE
        with tempfile.TemporaryDirectory(prefix="mare_test_") as tmp_dir:
            mare_res = run_mare_on_task(raw_text, tmp_dir)
            mare_spec = mare_res["specification"]

        # 3. Compare specifications
        comp = compare_specifications(sf_spec, mare_spec, checklist)

        sf_m = comp["specforge_metrics"]
        mare_m = comp["mare_metrics"]

        summary_results.append({
            "task": title,
            "sf_completeness": sf_m["completeness_score"],
            "sf_structure": sf_m["structure_score"],
            "sf_ambiguity": sf_m["average_ambiguity_score"],
            "mare_completeness": mare_m["completeness_score"],
            "mare_structure": mare_m["structure_score"],
            "mare_ambiguity": mare_m["average_ambiguity_score"],
        })

    # Print Comparative Table
    print("\n" + "=" * 92)
    print("HEAD-TO-HEAD SPECIFICATION QUALITY COMPARISON MATRIX")
    print("=" * 92)
    header = f"{'Benchmark Task':<30} | {'SF Comp':<8} {'SF Struct':<9} {'SF Amb':<8} | {'MARE Comp':<9} {'MARE Struct':<10} {'MARE Amb':<8}"
    print(header)
    print("-" * 92)

    for r in summary_results:
        line = (
            f"{r['task'][:30]:<30} | "
            f"{r['sf_completeness']:<8.2f} {r['sf_structure']:<9.2f} {r['sf_ambiguity']:<8.2f} | "
            f"{r['mare_completeness']:<9.2f} {r['mare_structure']:<10.2f} {r['mare_ambiguity']:<8.2f}"
        )
        print(line)

    print("=" * 92)
    print("Notes:")
    print(" - Completeness: Fraction of hand-written ground-truth checklist requirements satisfied.")
    print(" - Structure: Schema parseability & standardized metadata score (0.0=unstructured text, 1.0=typed ADS).")
    print(" - Ambiguity: Blind heuristic ambiguity score across extracted requirement sentences (lower is better).")
    print("=" * 92)


if __name__ == "__main__":
    main()
