from pathlib import Path

from src.lingophysics.noema_index import load_noema_index, search_noema, compact_context_bundle
from src.lingophysics.noema_router import load_routing_policy, route_query

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "data" / "noema" / "noema_index_seed_v2_2.json"
POLICY = ROOT / "data" / "noema" / "routing_policy_v2_2.json"


def test_noema_index_loads_cards():
    index = load_noema_index(INDEX)
    assert index["noema_index_version"] == "2.2"
    assert len(index["cards"]) >= 8
    assert "does not make dense GGUF" in index["non_claim"]


def test_search_retrieves_inside_water_glass():
    index = load_noema_index(INDEX)
    policy = load_routing_policy(POLICY)
    results = search_noema("Woda jest w szklance", index, policy=policy, language="pl")
    ids = {item["id"] for item in results}
    assert "noema:concept:water" in ids
    assert "noema:concept:glass" in ids
    bundle = compact_context_bundle(results)
    assert "Inside" in bundle["operator_hooks"] or "Contains" in bundle["operator_hooks"]


def test_route_detects_dynamic_anchor():
    index = load_noema_index(INDEX)
    policy = load_routing_policy(POLICY)
    route = route_query("Spotkajmy się gdzieś kiedyś", index, policy, language="pl")
    assert "unresolved_anchor_or_scope" in route["unresolved"]
    assert route["confidence"] < 1.0


def test_route_requires_factual_validation():
    index = load_noema_index(INDEX)
    policy = load_routing_policy(POLICY)
    route = route_query("verify factual source for water claim", index, policy, language="en")
    assert route["factual_validation_required"] is True
