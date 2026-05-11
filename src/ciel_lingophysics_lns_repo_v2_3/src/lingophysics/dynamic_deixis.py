from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional
import json

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None


@dataclass(frozen=True)
class DynamicAnchor:
    operator: str
    domain: str
    variable: str
    equation: str
    resolution_state: str
    false_precision_risk: float


def load_dynamic_deictics(path: str | Path) -> Dict[str, Any]:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if p.suffix.lower() in {".yaml", ".yml"}:
        if yaml is None:
            raise RuntimeError("PyYAML is required for YAML dynamic deictic files.")
        return yaml.safe_load(text)
    return json.loads(text)


def classify_dynamic_surface(surface: str) -> Optional[str]:
    s = surface.strip().lower()
    mapping = {
        "gdzieś": "Somewhere",
        "somewhere": "Somewhere",
        "irgendwo": "Somewhere",
        "quelque part": "Somewhere",
        "en algún lugar": "Somewhere",
        "gdziekolwiek": "Anywhere",
        "anywhere": "Anywhere",
        "n'importe où": "Anywhere",
        "donde sea": "Anywhere",
        "nigdzie": "Nowhere",
        "nowhere": "Nowhere",
        "nirgendwo": "Nowhere",
        "nulle part": "Nowhere",
        "en ninguna parte": "Nowhere",
        "kiedyś": "Sometime",
        "sometime": "Sometime",
        "once": "Sometime",
        "irgendwann": "Sometime",
        "un jour": "Sometime",
        "algún día": "Sometime",
        "kiedykolwiek": "Anytime",
        "anytime": "Anytime",
        "whenever": "Anytime",
        "jederzeit": "Anytime",
        "cuando sea": "Anytime",
        "nigdy": "Never",
        "never": "Never",
        "nie": "Never",
        "niemals": "Never",
        "jamais": "Never",
        "nunca": "Never",
        "jakoś": "Somehow",
        "somehow": "Somehow",
        "irgendwie": "Somehow",
        "de alguna manera": "Somehow",
        "dokądś": "TowardSomewhere",
        "skądś": "FromSomewhere",
        "from somewhere": "FromSomewhere",
    }
    return mapping.get(s)


def unresolved_anchor(operator: str) -> DynamicAnchor:
    op = operator.strip()
    if op in {"Somewhere", "Anywhere", "Nowhere"}:
        domain, variable = "Place", "x"
    elif op in {"Sometime", "Anytime", "Never"}:
        domain, variable = "Time", "t"
    elif op == "Somehow":
        domain, variable = "Manner", "m"
    elif op == "TowardSomewhere":
        domain, variable = "DestinationPlace", "d"
    elif op == "FromSomewhere":
        domain, variable = "SourcePlace", "s"
    else:
        raise KeyError(op)

    if op in {"Nowhere", "Never"}:
        equation = f"¬∃{variable}∈{domain}: ActiveDomain({variable})"
        risk = 0.55
    elif op in {"Anywhere", "Anytime"}:
        equation = f"free-choice {variable}∈{domain}"
        risk = 0.70
    else:
        equation = f"∃{variable}∈{domain}: resolution({variable})<1"
        risk = 0.90
    return DynamicAnchor(op, domain, variable, equation, "unresolved", risk)


def resolve_dynamic_anchor(operator: str, context: Dict[str, Any] | None = None) -> DynamicAnchor:
    """Resolve only when context explicitly provides an anchor.

    This deliberately avoids statistical guessing. If no anchor is provided, the unresolved state is preserved.
    """
    base = unresolved_anchor(operator)
    context = context or {}
    key_by_domain = {
        "Place": "place",
        "Time": "time",
        "Manner": "manner",
        "DestinationPlace": "destination",
        "SourcePlace": "source",
    }
    key = key_by_domain.get(base.domain)
    if key and context.get(key):
        value = str(context[key])
        return DynamicAnchor(
            base.operator,
            base.domain,
            base.variable,
            f"{base.variable} := {value}",
            "resolved",
            0.05,
        )
    return base


def is_false_precision(anchor: DynamicAnchor, rendered_as_precise: bool) -> bool:
    return anchor.resolution_state == "unresolved" and rendered_as_precise and anchor.false_precision_risk >= 0.75
