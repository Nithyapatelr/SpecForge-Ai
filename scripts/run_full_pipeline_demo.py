"""
End-to-End Demo Script for SpecForge AI Phase 1.

Runs init_db, seed_taxonomy, ingests sample_01.txt, preprocesses atomic units,
classifies units, detects ambiguity, generates annotated report, and prints summary.

Usage:
    python scripts/run_full_pipeline_demo.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from specforge.ambiguity.service import detect_and_store
from specforge.classification.service import classify_and_store
from specforge.db.init_db import init_db
from specforge.ingestion.service import ingest_document
from specforge.preprocessing.service import preprocess_requirement
from specforge.reporting.annotator import generate_annotated_spec, save_annotated_spec
from scripts.seed_taxonomy import seed_taxonomy


def main():
    print("=" * 70)
    print(" 🛡️  SPECFORGE AI — PHASE 1 END-TO-END PIPELINE DEMO")
    print("=" * 70)

    # 1. Initialize DB & Seed Taxonomy
    print("\n[Step 1/5] Initializing Database & Seeding RIT Taxonomy...")
    init_db()
    seed_count = seed_taxonomy()
    print(f" -> Database ready. (Seeded {seed_count} new taxonomy entries)")

    # 2. Ingest Sample File
    sample_file = os.path.join(
        os.path.dirname(__file__), "..", "data", "sample_requirements", "sample_01.txt"
    )
    doc_id = "sample-01"
    print(f"\n[Step 2/5] Ingesting sample document ({os.path.basename(sample_file)})...")
    initial_req = ingest_document(file_path=sample_file, source_doc_id=doc_id)
    print(f" -> Raw text ingested. Created initial requirement ID: {initial_req.requirement_id[:8]}...")

    # 3. Preprocess into Atomic Units
    print("\n[Step 3/5] Preprocessing text into atomic requirement units...")
    atomic_reqs = preprocess_requirement(initial_req.requirement_id)
    print(f" -> Preprocessed into {len(atomic_reqs)} atomic units.")

    # 4. Classify & Detect Ambiguity for each unit
    print("\n[Step 4/5] Running RIT Classification & Ambiguity Detection...")
    for idx, req in enumerate(atomic_reqs, start=1):
        rid = req.requirement_id
        text_snippet = (req.atomic_unit_text or req.raw_text)[:60]
        print(f"  [{idx}/{len(atomic_reqs)}] Processing: {text_snippet}...")

        # Classify
        try:
            clf = classify_and_store(rid)
            clf_label = clf.label_id
        except Exception as e:
            clf_label = f"Error ({e})"

        # Ambiguity
        try:
            flag = detect_and_store(rid)
            amb_score = flag.ambiguity_score
        except Exception as e:
            amb_score = 0.0

        print(f"      └─ RIT: {clf_label} | Ambiguity Score: {amb_score:.2f}")

    # 5. Generate Diagnostic Report
    print("\n[Step 5/5] Generating Annotated Diagnostic Specification Report...")
    report = generate_annotated_spec(doc_id)

    out_file = os.path.join(os.path.dirname(__file__), "..", "data", "annotated_spec_demo.json")
    save_annotated_spec(doc_id, out_file)
    print(f" -> Annotated spec report saved to: {out_file}")

    # Print Summary Report to Console
    summary = report["summary"]
    print("\n" + "=" * 70)
    print(" 📈  PIPELINE EXECUTION SUMMARY")
    print("=" * 70)
    print(f" Source Doc ID:            {report['source_doc_id']}")
    print(f" Total Atomic Requirements: {summary['total_requirements']}")
    print(f" High Ambiguity Flagged:    {summary['high_ambiguity_count']}")
    print("\n RIT Label Distribution:")
    for label, count in summary["label_distribution"].items():
        print(f"   - {label:<30}: {count}")

    # Top 3 most ambiguous requirements
    sorted_reqs = sorted(report["requirements"], key=lambda x: x["ambiguity_score"], reverse=True)
    print("\n Top 3 Most Ambiguous Requirements Flagged:")
    for i, r in enumerate(sorted_reqs[:3], start=1):
        print(f"\n {i}. Score {r['ambiguity_score']:.2f} — [{r['rit_label']}]")
        print(f"    Text: \"{r['atomic_unit_text']}\"")
        print(f"    Reasons: {' | '.join(r['ambiguity_reasons'])}")

    print("\n" + "=" * 70)
    print(" ✅  DEMO COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
