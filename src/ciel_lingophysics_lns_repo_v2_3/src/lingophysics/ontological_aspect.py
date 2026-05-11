from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict
import json

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None


@dataclass(frozen=True)
class BeingResolution:
    surface: str
    language: str
    canonical_operator: str
    equation: str
    confidence: float


def load_ontological_aspect(path: str | Path) -> Dict[str, Any]:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if p.suffix.lower() in {".yaml", ".yml"}:
        if yaml is None:
            raise RuntimeError("PyYAML is required for YAML ontological aspect files.")
        return yaml.safe_load(text)
    return json.loads(text)


def surface_index(data: Dict[str, Any]) -> dict[tuple[str, str], Dict[str, Any]]:
    idx: dict[tuple[str, str], Dict[str, Any]] = {}
    for op in data["operators"]:
        lang = op["language"].lower()
        for s in op.get("surfaces", []):
            idx[(lang, s.lower())] = op
    return idx


def classify_ontological_surface(surface: str, language: str, data: Dict[str, Any]) -> str:
    key = (language.strip().lower(), surface.strip().lower())
    idx = surface_index(data)
    if key not in idx:
        raise KeyError(key)
    return idx[key]["canonical_operator"]


def resolve_be(surface: str, language: str, complement_type: str, data: Dict[str, Any]) -> BeingResolution:
    """Resolve a be-like operator into IdentityBe or StateBe.

    Spanish ser/estar are high-confidence lexical splits. English and Polish need complement typing.
    """
    lang = language.strip().lower()
    s = surface.strip().lower()
    c = complement_type.strip().lower()

    try:
        canonical = classify_ontological_surface(s, lang, data)
    except KeyError:
        canonical = "UnknownBeingOperator"

    if canonical in {"SerIdentityBe", "MonoConcreteThing", "KotoAbstractEventFact"}:
        return BeingResolution(surface, lang, canonical, "IdentityOrOntologyResolved(surface)", 0.95 if canonical == "SerIdentityBe" else 0.85)
    if canonical == "EstarStateBe":
        return BeingResolution(surface, lang, "StateBe", "StateBe(Entity, StateOrLocation, Time?)", 0.95)

    identity_types = {"class", "role", "origin", "identity", "kind", "profession", "essence"}
    state_types = {"state", "location", "result_state", "condition", "temporary", "position"}
    if c in identity_types:
        return BeingResolution(surface, lang, "IdentityBe", "IdentityBe(Entity, Identity)", 0.75)
    if c in state_types:
        return BeingResolution(surface, lang, "StateBe", "StateBe(Entity, StateOrLocation, Time?)", 0.75)
    return BeingResolution(surface, lang, canonical, "ResolveByContext(Entity, Complement)", 0.35)


def is_koto_mono_contrast(a: str, b: str) -> bool:
    pair = {a.strip().lower(), b.strip().lower()}
    return bool(pair & {"koto", "こと", "事"}) and bool(pair & {"mono", "もの", "物"})
