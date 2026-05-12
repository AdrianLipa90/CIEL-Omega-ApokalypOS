from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional
import json
import math

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None


@dataclass(frozen=True)
class QuantifierSignature:
    name: str
    symbol: str
    operator: str
    quantifier_class: str
    phase: float
    force: float


@dataclass(frozen=True)
class ScopeExpression:
    quantifier: str
    predicate: str
    negation_position: str
    normalized: str
    phase: float
    scope_status: str


def load_scope_system(path: str | Path) -> Dict[str, Any]:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if p.suffix.lower() in {".yaml", ".yml"}:
        if yaml is None:
            raise RuntimeError("PyYAML is required for YAML scope files.")
        return yaml.safe_load(text)
    return json.loads(text)


def encode_quantifier(name: str, system: Dict[str, Any]) -> QuantifierSignature:
    key = name.upper()
    meta = system["dimensions"]["quantifier"][key]
    return QuantifierSignature(
        name=key,
        symbol=meta["symbol"],
        operator=meta["operator"],
        quantifier_class=meta["class"],
        phase=round(float(meta["phase"]), 6),
        force=round(float(meta["force"]), 6),
    )


def _negation_phase(system: Dict[str, Any], negation_position: str) -> float:
    return float(system["dimensions"]["negation_position"][negation_position]["phase"])


def normalize_scope(
    quantifier_name: str,
    predicate: str,
    negation_position: str,
    system: Dict[str, Any],
    domain: str = "DOMAIN",
) -> ScopeExpression:
    q = encode_quantifier(quantifier_name, system)
    if negation_position not in system["dimensions"]["negation_position"]:
        negation_position = "unresolved"
    if negation_position == "unresolved":
        return ScopeExpression(q.name, predicate, negation_position, "UNRESOLVED_SCOPE", round(q.phase + _negation_phase(system, negation_position), 6), "unresolved")

    if q.name == "ALL" and negation_position == "outside_quantifier":
        normalized = f"EXISTS(x, {domain}(x) AND NOT({predicate}(x)))"
    elif q.name == "ALL" and negation_position == "inside_predicate":
        normalized = f"FORALL(x, {domain}(x) -> NOT({predicate}(x)))"
    elif q.name == "SOME" and negation_position == "outside_quantifier":
        normalized = f"NOT(EXISTS(x, {domain}(x) AND {predicate}(x)))"
    elif q.name == "SOME" and negation_position == "inside_predicate":
        normalized = f"EXISTS(x, {domain}(x) AND NOT({predicate}(x)))"
    elif q.name == "NO" or negation_position == "quantifier_negative":
        normalized = f"FORALL(x, {domain}(x) -> NOT({predicate}(x)))"
        negation_position = "quantifier_negative"
    elif negation_position == "none":
        if q.name == "ALL":
            normalized = f"FORALL(x, {domain}(x) -> {predicate}(x))"
        elif q.name == "SOME":
            normalized = f"EXISTS(x, {domain}(x) AND {predicate}(x))"
        else:
            normalized = f"{q.operator}(x, {domain}(x), {predicate}(x))"
    else:
        normalized = "UNRESOLVED_SCOPE"
        negation_position = "unresolved"

    phase = round(q.phase + _negation_phase(system, negation_position), 6)
    status = "resolved" if normalized != "UNRESOLVED_SCOPE" else "unresolved"
    return ScopeExpression(q.name, predicate, negation_position, normalized, phase, status)


def phase_distance(a: ScopeExpression, b: ScopeExpression) -> float:
    return round(abs(math.sin((a.phase - b.phase) / 2.0)) * 2.0, 6)


def scope_equivalent(a: ScopeExpression, b: ScopeExpression) -> bool:
    return a.scope_status == "resolved" and b.scope_status == "resolved" and a.normalized == b.normalized


def event_equivalence_guard(
    predicate_frame_equal: bool,
    roles_equal: bool,
    tame_compatible: bool,
    a: ScopeExpression,
    b: ScopeExpression,
) -> bool:
    return bool(predicate_frame_equal and roles_equal and tame_compatible and scope_equivalent(a, b))


def is_false_equivalence_not_all_vs_none(a: ScopeExpression, b: ScopeExpression) -> bool:
    pair = {a.normalized, b.normalized}
    has_not_all = any("EXISTS" in x and "NOT" in x for x in pair)
    has_none = any(x.startswith("FORALL") and "NOT" in x for x in pair)
    return has_not_all and has_none and not scope_equivalent(a, b)
