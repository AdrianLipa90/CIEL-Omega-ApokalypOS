from pathlib import Path

from src.lingophysics.noema_index import load_noema_index
from src.lingophysics.noema_router import load_routing_policy, route_query
from src.lingophysics.inference_gate import load_inference_gate_policy, decide_gate, gguf_is_advisory
from src.lingophysics.energy_estimator import estimate_relative_cost, estimate_savings, estimate_from_gate

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "data" / "noema" / "noema_index_seed_v2_2.json"
ROUTING = ROOT / "data" / "noema" / "routing_policy_v2_2.json"
GATE = ROOT / "data" / "noema" / "inference_gate_policy_v2_2.json"


def _load():
    return load_noema_index(INDEX), load_routing_policy(ROUTING), load_inference_gate_policy(GATE)


def test_gguf_policy_is_advisory():
    _, _, gate = _load()
    assert gguf_is_advisory(gate)


def test_resolved_query_can_skip_gguf():
    index, routing, gate = _load()
    route = route_query("water inside glass", index, routing, language="en")
    decision = decide_gate(route, routing, gate, validator_pass=True)
    assert decision["gguf_advisory"] is True
    assert decision["level"] in {"NO_LLM", "SMALL_GGUF", "MEDIUM_GGUF"}


def test_factual_validation_routes_to_gguf_validator():
    index, routing, gate = _load()
    route = route_query("verify source factual claim about water", index, routing, language="en")
    decision = decide_gate(route, routing, gate, validator_pass=True)
    assert decision["level"] == "GGUF_VALIDATOR"
    assert decision["requires_gguf"] is True


def test_high_impact_unresolved_goes_to_human_review():
    index, routing, gate = _load()
    route = route_query("nie każdy gdzieś kiedyś", index, routing, language="pl")
    decision = decide_gate(route, routing, gate, validator_pass=True, high_impact=True)
    assert decision["level"] == "HUMAN_REVIEW"
    assert decision["requires_gguf"] is False


def test_energy_estimator_savings_positive():
    assert estimate_relative_cost(100, "LARGE_GGUF") > estimate_relative_cost(100, "SMALL_GGUF")
    savings = estimate_savings(1000, 120, routed_level="SMALL_GGUF")
    assert savings["relative_saving"] > 0.5


def test_energy_estimator_from_gate():
    estimate = estimate_from_gate(1000, 100, {"level": "NO_LLM"})
    assert estimate["routed_cost"] == 0.0
    assert estimate["relative_saving"] == 1.0
