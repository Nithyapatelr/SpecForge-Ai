"""
Manual classification check against 15 sample requirements.

Usage:
    python scripts/manual_classify_check.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from specforge.classification.classifier import classify_requirement
from specforge.ingestion.loader import load_txt
from specforge.preprocessing.segmenter import segment_into_atomic_units


def main():
    sample_file = os.path.join(
        os.path.dirname(__file__), "..", "data", "sample_requirements", "sample_01.txt"
    )
    raw_text = load_txt(sample_file)
    units = segment_into_atomic_units(raw_text)

    print(f"\n--- Classifying {len(units)} Atomic Requirement Units ---\n")
    for i, unit in enumerate(units, start=1):
        print(f"[{i}] {unit}")
        try:
            res = classify_requirement(unit)
            print(f"    └─ Label: {res['label_name']} | Confidence: {res['confidence']:.2f}")
            print(f"       Rationale: {res['rationale']}\n")
        except Exception as e:
            print(f"    └─ Error: {e}\n")


if __name__ == "__main__":
    main()
