"""Roadmap helpers for CIELingo.

The roadmap is intentionally data-driven so future patches can inspect the
stage plan without parsing Markdown. This module performs lightweight checks;
full JSON Schema validation is optional and kept out of the dependency chain.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

REQUIRED_PHASE_FIELDS = {"id", "name", "target_version", "status", "objective", "deliverables", "exit_criteria"}


def load_roadmap(path: str | Path) -> Dict[str, Any]:
    """Load a roadmap JSON file."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_roadmap(data: Dict[str, Any]) -> List[str]:
    """Return a list of validation errors. Empty list means pass."""
    errors: List[str] = []
    if not data.get("cielingo_roadmap_version"):
        errors.append("missing:cielingo_roadmap_version")
    phases = data.get("phases")
    if not isinstance(phases, list) or not phases:
        errors.append("missing:phases")
        return errors
    seen = set()
    for idx, phase in enumerate(phases):
        missing = REQUIRED_PHASE_FIELDS - set(phase)
        if missing:
            errors.append(f"phase[{idx}]:missing:{','.join(sorted(missing))}")
        pid = phase.get("id")
        if pid in seen:
            errors.append(f"phase[{idx}]:duplicate_id:{pid}")
        seen.add(pid)
        for key in ("deliverables", "exit_criteria"):
            if not isinstance(phase.get(key), list) or not phase.get(key):
                errors.append(f"phase[{idx}]:empty_or_invalid:{key}")
    return errors


def planned_phases(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return phases that are not completed."""
    return [p for p in data.get("phases", []) if not str(p.get("status", "")).startswith("completed")]


def next_phase(data: Dict[str, Any]) -> Dict[str, Any] | None:
    """Return the first planned/current phase that is not completed."""
    phases = planned_phases(data)
    return phases[0] if phases else None


def gguf_is_advisory(policy: Dict[str, Any]) -> bool:
    """Check the key safety/canonicality rule for GGUF/LLM validators."""
    text = (policy.get("canonicality_rule") or "").lower()
    return "cannot" in text and "canonical" in text
