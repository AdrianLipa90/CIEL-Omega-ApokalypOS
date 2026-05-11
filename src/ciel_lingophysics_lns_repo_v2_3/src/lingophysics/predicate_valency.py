from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List
import json

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None


@dataclass(frozen=True)
class ValencyCheck:
    operator: str
    valid: bool
    missing_roles: tuple[str, ...]
    unexpected_roles: tuple[str, ...]
    compatibility: float


def load_event_frames(path: str | Path) -> Dict[str, Any]:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if p.suffix.lower() in {".yaml", ".yml"}:
        if yaml is None:
            raise RuntimeError("PyYAML is required for YAML event frame files.")
        return yaml.safe_load(text)
    return json.loads(text)


def get_frame(operator: str, frames: Dict[str, Any]) -> Dict[str, Any]:
    op = operator.strip().lower()
    for frame in frames["frames"]:
        if frame["canonical_operator"].lower() == op or frame["frame_id"].lower() == op:
            return frame
    raise KeyError(operator)


def required_roles(operator: str, frames: Dict[str, Any]) -> List[str]:
    return list(get_frame(operator, frames).get("required_roles", []))


def optional_roles(operator: str, frames: Dict[str, Any]) -> List[str]:
    return list(get_frame(operator, frames).get("optional_roles", []))


def validate_roles(operator: str, provided_roles: list[str] | set[str], frames: Dict[str, Any]) -> ValencyCheck:
    frame = get_frame(operator, frames)
    required = set(frame.get("required_roles", []))
    optional = set(frame.get("optional_roles", []))
    provided = set(provided_roles)
    missing = tuple(sorted(required - provided))
    unexpected = tuple(sorted(provided - required - optional))
    denom = max(1, len(required))
    compatibility = (len(required & provided) / denom) * (1.0 if not unexpected else 0.75)
    return ValencyCheck(
        operator=frame["canonical_operator"],
        valid=not missing and not unexpected,
        missing_roles=missing,
        unexpected_roles=unexpected,
        compatibility=round(compatibility, 4),
    )


def role_for_polish_case(operator: str, case: str, frames: Dict[str, Any]) -> list[str]:
    """Return candidate roles licensed by a predicate frame for a Polish case.

    This does not claim that case alone determines role. It intersects case hints with predicate valency.
    """
    frame = get_frame(operator, frames)
    target = case.strip().capitalize()
    hits: list[str] = []
    for role, encoded in frame.get("pl_case_realization", {}).items():
        variants = {v.strip().capitalize() for v in str(encoded).replace("/", ",").split(",")}
        if target in variants:
            hits.append(role)
    return hits


def transduction_strategy(operator: str, target_language: str, frames: Dict[str, Any]) -> str:
    frame = get_frame(operator, frames)
    lang = target_language.strip().lower()
    strategies = frame.get("language_realization", {})
    if lang not in strategies:
        raise KeyError((operator, target_language))
    return strategies[lang]


def frame_equation(operator: str, frames: Dict[str, Any]) -> str:
    return get_frame(operator, frames)["equation"]
