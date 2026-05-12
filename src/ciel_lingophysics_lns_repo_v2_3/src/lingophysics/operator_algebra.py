from __future__ import annotations

from dataclasses import dataclass
from math import cos, sin, pi, sqrt
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
import json

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None


@dataclass(frozen=True)
class OperatorSignature:
    name: str
    arity: int | str
    domain: tuple[str, ...]
    codomain: str
    equation: str


@dataclass(frozen=True)
class OperatorRelation:
    relation_type: str
    left: str
    right: str
    invariant: str | None = None
    axis: str | None = None


def load_yaml(path: str | Path) -> Dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML is required to load operator algebra YAML files.")
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def load_json(path: str | Path) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def euler_phase_error(delta_phi: float, relation: str) -> float:
    """Return phase constraint error for synonym or antonym/inverse relation.

    synonym: |exp(iΔφ)-1|
    antonym/inverse: |exp(iΔφ)+1|
    """
    z_re = cos(delta_phi)
    z_im = sin(delta_phi)
    if relation in {"synonym", "aligned", "same_phase"}:
        return sqrt((z_re - 1.0) ** 2 + z_im**2)
    if relation in {"antonym", "inverse", "counterphase"}:
        return sqrt((z_re + 1.0) ** 2 + z_im**2)
    raise ValueError(f"Unsupported phase relation: {relation}")


def compose_dual(expression: str) -> str:
    """Minimal symbolic dual composer for canonical CIEL-LNS operator pairs."""
    clean = expression.replace(" ", "")
    if clean == "Inside(x,y)":
        return "Contains(y,x)"
    if clean == "Contains(x,y)":
        return "Inside(y,x)"
    if clean == "Before(x,y)":
        return "After(y,x)"
    if clean == "After(x,y)":
        return "Before(y,x)"
    if clean == "From(x,y)":
        return "To(y,x)"
    if clean == "To(x,y)":
        return "From(y,x)"
    return f"UNRESOLVED_DUAL({expression})"


def operator_power(
    structural_power: float,
    ambiguity_power: float,
    composition_depth: float,
    cross_language_variance: float,
    frequency_proxy: float = 0.0,
) -> float:
    """Simple normalized proxy for operator curvature/power.

    This is not corpus statistics. It is a deterministic seed score for the
    curated lingophysical library.
    """
    vals = [frequency_proxy, structural_power, ambiguity_power, composition_depth, cross_language_variance]
    vals = [max(0.0, min(1.0, float(v))) for v in vals]
    return sum(vals) / len(vals)


def validate_composition(domain: Iterable[str], codomain: str, next_domain: Iterable[str]) -> bool:
    """Check whether codomain of one operator can enter the domain of another."""
    nd = set(next_domain)
    return codomain in nd or "any" in nd or "relation" in nd


def classify_library_item(pos: str, semantic_role: str | None = None) -> str:
    """CIEL layer classifier for lexemes, used before card generation."""
    pos = pos.upper()
    role = (semantic_role or "").lower()
    if role in {"operator", "relation", "logic", "spatial", "temporal", "modal", "deictic"}:
        return "OPERATOR_CARD"
    if pos in {"ADP", "AUX", "PART", "SCONJ", "CCONJ", "DET"}:
        return "OPERATOR_CARD"
    if pos in {"NOUN", "PROPN"}:
        return "CONCEPT_CARD"
    if pos == "VERB":
        return "TRANSFORM_OPERATOR_OR_EVENT_CARD"
    if pos == "ADV":
        return "HIGHER_ORDER_OPERATOR_CARD"
    return "UNRESOLVED_CARD_TYPE"


PI = pi
