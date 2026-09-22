"""
Unit tests for SCG Graph Engine.
"""

from specforge.scg.scg_engine import build_semantic_constraint_graph


def test_build_semantic_constraint_graph():
    reqs = [
        {"requirement_id": "req_1", "atomic_unit_text": "System shall log all errors to file.", "rit_label": "Behavioral Rule"},
        {"requirement_id": "req_2", "atomic_unit_text": "System shall disable all logging to disk.", "rit_label": "Behavioral Rule"},
        {"requirement_id": "req_3", "atomic_unit_text": "Only Admins may delete accounts.", "rit_label": "Actor Permission"},
    ]

    scg_res = build_semantic_constraint_graph(reqs, conflict_threshold=0.60)

    assert scg_res["node_count"] == 3
    assert scg_res["edge_count"] >= 1
    assert len(scg_res["edges"]) >= 1
    assert scg_res["edges"][0]["type"] == "conflict"
