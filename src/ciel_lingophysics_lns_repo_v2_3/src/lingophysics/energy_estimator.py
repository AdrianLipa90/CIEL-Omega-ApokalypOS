"""Relative energy/cost estimator for NOEMA-gated inference.

This is not a hardware power model. It is a deterministic planning estimator for
comparing routing decisions.
"""
from __future__ import annotations

from typing import Dict

DEFAULT_MULTIPLIERS = {
    "NO_LLM": 0.0,
    "SMALL_GGUF": 1.0,
    "MEDIUM_GGUF": 3.0,
    "LARGE_GGUF": 8.0,
    "GGUF_VALIDATOR": 2.0,
    "HUMAN_REVIEW": 0.0,
}


def estimate_relative_cost(token_count: int, gate_level: str, pass_count: int = 1, multipliers: Dict[str, float] | None = None) -> float:
    if token_count < 0:
        raise ValueError("token_count must be non-negative")
    if pass_count < 1:
        raise ValueError("pass_count must be >= 1")
    table = multipliers or DEFAULT_MULTIPLIERS
    return round(float(token_count) * float(table.get(gate_level, 1.0)) * pass_count, 4)


def estimate_savings(baseline_tokens: int, routed_tokens: int, baseline_level: str = "LARGE_GGUF", routed_level: str = "SMALL_GGUF") -> Dict[str, float]:
    baseline = estimate_relative_cost(baseline_tokens, baseline_level)
    routed = estimate_relative_cost(routed_tokens, routed_level)
    if baseline == 0:
        ratio = 0.0
    else:
        ratio = max(0.0, (baseline - routed) / baseline)
    return {"baseline_cost": baseline, "routed_cost": routed, "relative_saving": round(ratio, 4)}


def estimate_from_gate(baseline_tokens: int, routed_tokens: int, gate_decision: Dict[str, object]) -> Dict[str, float]:
    level = str(gate_decision.get("level", "SMALL_GGUF"))
    return estimate_savings(baseline_tokens, routed_tokens, baseline_level="LARGE_GGUF", routed_level=level)
