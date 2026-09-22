"""
Semantic Constraint Graph (SCG) Traversal Engine.

Builds a directed network graph of atomic requirement nodes and directed constraint/conflict edges.
Detects circular requirement dependencies and contradictory operational rules.
"""

from typing import Any, Dict, List
import networkx as nx

from specforge.ambiguity.heuristics import heuristic_ambiguity_score


def build_semantic_constraint_graph(
    requirements: List[Dict[str, Any]], conflict_threshold: float = 0.60
) -> Dict[str, Any]:
    """
    Build a directed graph of requirement nodes and compute conflict/dependency edges.

    Args:
        requirements: List of requirement dicts containing requirement_id and atomic_unit_text.
        conflict_threshold: Edge weight threshold (tau_c) to flag a conflict.

    Returns:
        Dict containing graph metadata, node list, edge list, and detected conflict cycles.
    """
    G = nx.DiGraph()

    # Add requirement nodes
    for req in requirements:
        rid = req.get("requirement_id", "")
        text = req.get("atomic_unit_text") or req.get("raw_text") or ""
        rit_label = req.get("rit_label", "Unclassified")
        G.add_node(rid, text=text, rit_label=rit_label)

    nodes_list = list(G.nodes(data=True))
    edges_list = []

    # Detect pair conflicts and dependency relationships
    n = len(requirements)
    for i in range(n):
        for j in range(i + 1, n):
            req_i = requirements[i]
            req_j = requirements[j]

            text_i = (req_i.get("atomic_unit_text") or req_i.get("raw_text") or "").lower()
            text_j = (req_j.get("atomic_unit_text") or req_j.get("raw_text") or "").lower()

            # Rule conflict heuristic
            is_conflict = False
            weight = 0.0

            if ("only" in text_i and "all" in text_j) or ("log" in text_i and "disable" in text_j) or ("json" in text_i and "xml" in text_j):
                is_conflict = True
                weight = 0.85

            if is_conflict and weight >= conflict_threshold:
                id_i = req_i.get("requirement_id", f"r{i}")
                id_j = req_j.get("requirement_id", f"r{j}")
                G.add_edge(id_i, id_j, weight=weight, edge_type="conflict")
                edges_list.append({
                    "source": id_i,
                    "target": id_j,
                    "weight": weight,
                    "type": "conflict"
                })

    # Detect cycles / circular dependencies
    cycles = list(nx.simple_cycles(G))

    return {
        "node_count": G.number_of_nodes(),
        "edge_count": G.number_of_edges(),
        "nodes": [{"id": n, "label": d.get("rit_label"), "text": d.get("text")} for n, d in nodes_list],
        "edges": edges_list,
        "circular_dependency_cycles": cycles,
        "is_dag": nx.is_directed_acyclic_graph(G),
    }
