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
class TAMESignature:
    tense: str
    aspect: str
    mood: str
    modality: Optional[str]
    evidentiality: str
    phase: float
    assertion_force: float


def load_tame(path: str | Path) -> Dict[str, Any]:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if p.suffix.lower() in {".yaml", ".yml"}:
        if yaml is None:
            raise RuntimeError("PyYAML is required for YAML TAM-E files.")
        return yaml.safe_load(text)
    return json.loads(text)


def _phase_for(tame: Dict[str, Any], dimension: str, value: Optional[str]) -> float:
    if value is None:
        return 0.0
    return float(tame["dimensions"][dimension][value]["phase"])


def encode_tame_signature(
    tense: str,
    aspect: str,
    mood: str,
    evidentiality: str,
    tame: Dict[str, Any],
    modality: Optional[str] = None,
) -> TAMESignature:
    phase = (
        _phase_for(tame, "tense", tense)
        + _phase_for(tame, "aspect", aspect)
        + _phase_for(tame, "mood", mood)
        + _phase_for(tame, "modality", modality)
        + _phase_for(tame, "evidentiality", evidentiality)
    )
    # assertion force is intentionally simple seed logic.
    force = 1.0
    if mood in {"Conditional", "Subjunctive"}:
        force *= 0.55
    if mood == "Imperative":
        force *= 0.35
    if evidentiality == "Reportative":
        force *= 0.60
    if evidentiality == "Inferential":
        force *= 0.75
    if evidentiality == "Unknown":
        force *= 0.50
    return TAMESignature(tense, aspect, mood, modality, evidentiality, round(phase, 6), round(force, 6))


def phase_distance(a: TAMESignature, b: TAMESignature) -> float:
    return round(abs(math.sin((a.phase - b.phase) / 2.0)) * 2.0, 6)


def compatible_tame(a: TAMESignature, b: TAMESignature, epsilon: float = 0.15) -> bool:
    same_core = (a.tense == b.tense and a.aspect == b.aspect and a.mood == b.mood and a.modality == b.modality)
    if not same_core:
        return False
    return phase_distance(a, b) <= epsilon


def event_equivalence_guard(frame_equal: bool, roles_equal: bool, polarity_equal: bool, a: TAMESignature, b: TAMESignature) -> bool:
    return bool(frame_equal and roles_equal and polarity_equal and compatible_tame(a, b))


def evidentiality_allows_verification(sig: TAMESignature) -> bool:
    return sig.evidentiality == "Direct" and sig.assertion_force >= 0.9
