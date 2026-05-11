from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import json

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None

from .transformer_features import FeatureToken


def load_bias_rules(path: str | Path) -> Dict[str, Any]:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if p.suffix.lower() in {".yaml", ".yml"}:
        if yaml is None:
            raise RuntimeError("PyYAML is required for YAML bias rules.")
        return yaml.safe_load(text)
    return json.loads(text)


def operator_argument_link(a: FeatureToken, b: FeatureToken) -> bool:
    return (a.card_type == "OPERATOR_CARD" and b.card_type == "CONCEPT_CARD") or (b.card_type == "OPERATOR_CARD" and a.card_type == "CONCEPT_CARD")


def case_role_link(a: FeatureToken, b: FeatureToken) -> bool:
    return bool(a.features.get("case_gauge") or b.features.get("case_gauge")) and bool(set(a.roles) | set(b.roles))


def phase_compatible(a: FeatureToken, b: FeatureToken) -> bool:
    return not (a.features.get("phase_conflict") or b.features.get("phase_conflict"))


def pair_bias(a: FeatureToken, b: FeatureToken, rules: Dict[str, Any]) -> float:
    if a.token_id == b.token_id:
        return 0.0
    w = rules["weights"]
    score = 0.0
    if operator_argument_link(a, b):
        score += float(w.get("operator_argument_link", 0.0))
    if set(a.roles) & set(b.roles):
        score += float(w.get("same_event_frame", 0.0))
    if case_role_link(a, b):
        score += float(w.get("case_role_link", 0.0))
    if phase_compatible(a, b):
        score += float(w.get("phase_compatibility", 0.0))
    else:
        score -= float(w.get("conflict_penalty", 0.0))
    return round(score, 6)


def build_attention_bias_matrix(tokens: List[FeatureToken], rules: Dict[str, Any]) -> List[List[float]]:
    return [[pair_bias(a, b, rules) for b in tokens] for a in tokens]


def has_positive_structural_bias(matrix: List[List[float]]) -> bool:
    return any(cell > 0 for row in matrix for cell in row)
