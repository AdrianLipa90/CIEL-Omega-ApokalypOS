"""Inference gate for deciding when GGUF teacher-validation is needed."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import json


def load_inference_gate_policy(path: str | Path) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def gguf_is_advisory(policy: Dict[str, Any]) -> bool:
    rule = str(policy.get("canonicality_rule", "")).lower()
    return "advisory" in rule and "cannot" in rule and "canonical" in rule


def decide_gate(route: Dict[str, Any], routing_policy: Dict[str, Any], gate_policy: Dict[str, Any], validator_pass: bool = True, high_impact: bool = False) -> Dict[str, Any]:
    thresholds = routing_policy.get("confidence_thresholds", {})
    confidence = float(route.get("confidence", 0.0))
    unresolved = list(route.get("unresolved", []))
    factual = bool(route.get("factual_validation_required", False))

    if high_impact and unresolved:
        level = "HUMAN_REVIEW"
        reason = "high_impact_unresolved"
    elif validator_pass and not unresolved and not factual and confidence >= float(thresholds.get("no_llm", 0.82)):
        level = "NO_LLM"
        reason = "resolved_by_noema_validator"
    elif factual:
        level = "GGUF_VALIDATOR"
        reason = "factual_validation_required"
    elif confidence >= float(thresholds.get("small_gguf", 0.62)) and not high_impact:
        level = "SMALL_GGUF"
        reason = "low_risk_generation_or_repair"
    elif confidence >= float(thresholds.get("medium_gguf", 0.42)):
        level = "MEDIUM_GGUF"
        reason = "ambiguity_or_unresolved_structure"
    elif confidence < float(thresholds.get("human_review", 0.25)):
        level = "HUMAN_REVIEW"
        reason = "confidence_too_low"
    else:
        level = "LARGE_GGUF"
        reason = "hard_synthesis_or_low_confidence"

    gate = gate_policy.get("gate_levels", {}).get(level, {})
    return {
        "level": level,
        "reason": reason,
        "requires_gguf": bool(gate.get("requires_gguf", False)),
        "model_multiplier": float(gate.get("model_multiplier", 0.0)),
        "confidence": round(confidence, 4),
        "unresolved": unresolved,
        "gguf_advisory": gguf_is_advisory(gate_policy),
    }
