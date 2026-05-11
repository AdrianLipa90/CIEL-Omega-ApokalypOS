"""Repository coherence utilities for CIELingo v1.6.

The module intentionally avoids heavyweight dependencies. It scans files,
classifies repository layers, audits YAML/JSON pairs, and checks required
paths. It is a repo-level safety rail: missing or unresolved objects should be
visible rather than silently absorbed.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List
import json

CARD_TYPE_PREFIXES = {
    "CONCEPT_CARD": "data/concept_cards/",
    "OPERATOR_CARD": "data/operator_cards/",
    "OPERATOR_FAMILY": "data/operator_families/",
    "OPERATOR_COMPOSITION": "data/operator_compositions/",
    "GRAMMAR_CARD": "data/grammar/",
    "CASE_GAUGE_CARD": "data/case_systems/",
    "CASE_MAPPING": "data/case_mappings/",
    "EVENT_FRAME": "data/event_frames/",
    "ONTOLOGICAL_ASPECT": "data/ontological_aspect/",
    "TAME_CARD": "data/tame/",
    "SCOPE_CARD": "data/scope/",
    "JSON_FALLBACK": "data/json/",
    "SCHEMA": "schemas/",
    "DOC": "docs/",
    "SOURCE": "src/",
    "TEST": "tests/",
    "REPORT": "reports/",
}

REQUIRED_V16_PATHS = [
    "data/registry/card_type_registry_v1_6.json",
    "data/registry/canonical_status_registry_v1_6.json",
    "data/coherence/repository_coherence_summary_v1_6.json",
    "data/coherence/yaml_json_pair_audit_v1_6.json",
    "data/schema_coverage/schema_coverage_map_v1_6.json",
    "data/integrity/relation_integrity_report_v1_6.json",
    "data/json/fallback_manifest_v1_6.json",
    "schemas/ciel_lns_repo_coherence.schema.json",
]


def iter_files(root: Path) -> List[Path]:
    """Return repository files excluding VCS internals."""
    return sorted(p for p in root.rglob("*") if p.is_file() and ".git" not in p.parts)


def classify_path(path: str) -> str:
    """Classify a repository path into a CIELingo layer."""
    normalized = path.replace("\\", "/")
    for card_type, prefix in CARD_TYPE_PREFIXES.items():
        if normalized.startswith(prefix):
            return card_type
    return "ROOT_OR_MISC"


def count_by_type(root: Path) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for path in iter_files(root):
        rel = path.relative_to(root).as_posix()
        typ = classify_path(rel)
        counts[typ] = counts.get(typ, 0) + 1
    return counts


def yaml_json_pair_audit(root: Path) -> Dict[str, object]:
    yaml_files = sorted(root.glob("data/**/*.yaml"))
    json_files = sorted(root.glob("data/**/*.json"))
    json_stems = {p.with_suffix("").as_posix() for p in json_files}
    missing_json = []
    for yaml_path in yaml_files:
        if yaml_path.with_suffix("").as_posix() not in json_stems:
            missing_json.append(yaml_path.relative_to(root).as_posix())
    return {
        "yaml_count": len(yaml_files),
        "json_count": len(json_files),
        "missing_json_count": len(missing_json),
        "missing_json": missing_json,
    }


def required_path_status(root: Path, required: Iterable[str] = REQUIRED_V16_PATHS) -> Dict[str, str]:
    return {path: ("PASS" if (root / path).exists() else "BLOCKER") for path in required}


def load_coherence_summary(root: Path) -> Dict[str, object]:
    summary_path = root / "data/coherence/repository_coherence_summary_v1_6.json"
    return json.loads(summary_path.read_text(encoding="utf-8"))
