from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "data" / "diagnostics" / "global_diagnostic_summary_v2_0.json"
COSTS = ROOT / "data" / "diagnostics" / "cross_language_reconstruction_costs.csv"
REGISTRY = ROOT / "data" / "diagnostics" / "conflict_ambiguity_unresolved_registry.json"
GRAPH = ROOT / "data" / "graphs" / "global_diagnostic_graph.json"


def test_diagnostic_summary_counts():
    from src.lingophysics.diagnostic_geometry import load_json
    summary = load_json(SUMMARY)
    assert summary["version"] == "2.0"
    assert summary["cards_total"] >= 72
    assert summary["operator_links_total"] > 0
    assert summary["relation_edges_total"] > 0


def test_cross_language_cost_matrix_has_polish_english_cost():
    from src.lingophysics.diagnostic_geometry import load_reconstruction_costs, cost_lookup, max_cost
    rows = load_reconstruction_costs(COSTS)
    assert cost_lookup(rows, "pl", "pl") == 0.0
    assert cost_lookup(rows, "pl", "en") > 0.0
    assert max_cost(rows) > 0.0


def test_conflict_registry_has_no_blockers():
    from src.lingophysics.diagnostic_geometry import load_conflict_registry, issue_counts_by_severity
    registry = load_conflict_registry(REGISTRY)
    counts = issue_counts_by_severity(registry)
    assert counts.get("BLOCKER", 0) == 0
    assert counts.get("WARN", 0) >= 1


def test_global_diagnostic_graph_is_nonempty():
    from src.lingophysics.diagnostic_geometry import load_graph, graph_counts
    graph = load_graph(GRAPH)
    nodes, edges = graph_counts(graph)
    assert nodes >= 72
    assert edges > nodes


def test_seed_diagnostic_pass():
    from src.lingophysics.diagnostic_geometry import load_json, load_conflict_registry, diagnostic_pass
    assert diagnostic_pass(load_json(SUMMARY), load_conflict_registry(REGISTRY)) is True
