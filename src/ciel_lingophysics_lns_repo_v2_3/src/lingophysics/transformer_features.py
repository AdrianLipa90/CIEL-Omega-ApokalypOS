from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List
import json

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None


@dataclass(frozen=True)
class FeatureToken:
    token_id: int
    surface: str
    card_type: str
    features: Dict[str, Any]
    roles: tuple[str, ...] = ()
    concept_id: str | None = None
    operator_id: str | None = None


def load_feature_spec(path: str | Path) -> Dict[str, Any]:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if p.suffix.lower() in {".yaml", ".yml"}:
        if yaml is None:
            raise RuntimeError("PyYAML is required for YAML feature specs.")
        return yaml.safe_load(text)
    return json.loads(text)


def load_feature_tensor(path: str | Path) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def tokens_from_tensor(tensor: Dict[str, Any]) -> List[FeatureToken]:
    out: List[FeatureToken] = []
    for raw in tensor.get("tokens", []):
        out.append(FeatureToken(
            token_id=int(raw["id"]),
            surface=str(raw["surface"]),
            card_type=str(raw["card_type"]),
            features=dict(raw.get("features", {})),
            roles=tuple(raw.get("roles", ())),
            concept_id=raw.get("concept_id"),
            operator_id=raw.get("operator_id"),
        ))
    return out


def card_type_vector(card_type: str, spec: Dict[str, Any]) -> List[int]:
    labels = spec["feature_groups"]["card_type"]["labels"]
    if card_type not in labels:
        card_type = "UNKNOWN"
    return [1 if x == card_type else 0 for x in labels]


def role_vector(roles: Iterable[str], spec: Dict[str, Any]) -> List[int]:
    labels = spec["feature_groups"]["event_frame"]["labels"]
    role_set = set(roles)
    return [1 if x in role_set else 0 for x in labels]


def encode_feature_token(token: FeatureToken, spec: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "token_id": token.token_id,
        "surface": token.surface,
        "card_type": token.card_type,
        "card_type_vector": card_type_vector(token.card_type, spec),
        "role_vector": role_vector(token.roles, spec),
        "operator_incidence": float(token.features.get("operator_incidence", 0.0)),
        "concept_mass": float(token.features.get("concept_mass", 0.0)),
        "case_gauge": token.features.get("case_gauge"),
        "concept_id": token.concept_id,
        "operator_id": token.operator_id,
    }


def encode_tensor(tensor: Dict[str, Any], spec: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [encode_feature_token(t, spec) for t in tokens_from_tensor(tensor)]


def invariant_expectation_set(tensor: Dict[str, Any]) -> set[str]:
    return set(tensor.get("validator_expectations", []))
