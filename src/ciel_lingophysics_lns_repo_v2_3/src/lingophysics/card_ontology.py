"""Card ontology utilities for CIELingo v1.7.

The ontology protects the core distinction:
concept cards are semantic masses; operator cards are forces/functions;
grammar, case, TAM-E, scope, deixis, and event frames are typed control layers.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional
import json

ONTOLOGY_PATH = Path("data/card_ontology/card_ontology_v1_7.json")


@dataclass(frozen=True)
class CardTypeSpec:
    name: str
    storage_root: str
    semantic_role: str
    status_default: str
    primary_payload: tuple[str, ...]
    forbidden_payload: tuple[str, ...]


def load_card_ontology(root: Path) -> Dict[str, object]:
    return json.loads((root / ONTOLOGY_PATH).read_text(encoding="utf-8"))


def card_type_specs(root: Path) -> Dict[str, CardTypeSpec]:
    ontology = load_card_ontology(root)
    specs: Dict[str, CardTypeSpec] = {}
    for name, raw in ontology["card_types"].items():
        specs[name] = CardTypeSpec(
            name=name,
            storage_root=raw["storage_root"],
            semantic_role=raw["semantic_role"],
            status_default=raw["status_default"],
            primary_payload=tuple(raw.get("primary_payload", [])),
            forbidden_payload=tuple(raw.get("forbidden_payload", [])),
        )
    return specs


def infer_card_type_from_path(path: str, specs: Mapping[str, CardTypeSpec]) -> str:
    normalized = path.replace("\\", "/")
    # Prefer longer roots first so more specific layers win.
    ordered = sorted(specs.values(), key=lambda spec: len(spec.storage_root), reverse=True)
    for spec in ordered:
        if normalized.startswith(spec.storage_root):
            return spec.name
    if normalized.startswith("schemas/"):
        return "SCHEMA"
    if normalized.startswith("docs/"):
        return "DOC"
    if normalized.startswith("src/"):
        return "SOURCE"
    if normalized.startswith("tests/"):
        return "TEST"
    if normalized.startswith("reports/"):
        return "REPORT"
    return "ROOT_OR_MISC"


def validate_payload_shape(card_type: str, payload: Mapping[str, object], specs: Mapping[str, CardTypeSpec]) -> Dict[str, List[str]]:
    """Return explicit ontology validation messages for an in-memory card payload."""
    errors: List[str] = []
    warnings: List[str] = []
    spec = specs.get(card_type)
    if spec is None:
        errors.append(f"UNKNOWN_CARD_TYPE:{card_type}")
        return {"errors": errors, "warnings": warnings}
    for key in spec.forbidden_payload:
        if key in payload:
            errors.append(f"FORBIDDEN_PAYLOAD:{card_type}:{key}")
    if card_type == "CONCEPT_CARD" and "formal_modes" in payload and "operator_hooks" not in payload:
        errors.append("CONCEPT_CARD_WITH_PRIMARY_OPERATOR_MODES")
    if card_type == "OPERATOR_CARD" and not ("arity" in payload or "formal_modes" in payload or payload.get("unresolved") is True):
        warnings.append("OPERATOR_CARD_WITHOUT_ARITY_OR_FORMAL_MODES")
    if card_type == "DEICTIC_CARD" and "anchor_domain" not in payload:
        warnings.append("DEICTIC_CARD_WITHOUT_ANCHOR_DOMAIN")
    if card_type == "SCOPE_CARD" and "scope_stack" not in payload:
        warnings.append("SCOPE_CARD_WITHOUT_SCOPE_STACK")
    return {"errors": errors, "warnings": warnings}


def ontology_required_paths() -> List[str]:
    return [
        "docs/32_CARD_ONTOLOGY_REFACTOR.md",
        "docs/33_CARD_MIGRATION_AND_TYPE_RESOLUTION.md",
        "data/card_ontology/card_ontology_v1_7.json",
        "data/card_ontology/card_type_constraints_v1_7.json",
        "data/card_ontology/card_type_migration_map_v1_7.json",
        "schemas/ciel_lns_card_ontology.schema.json",
        "src/lingophysics/card_ontology.py",
        "reports/v1_7_card_ontology_refactor_report.md",
    ]


def required_path_status(root: Path, required: Optional[Iterable[str]] = None) -> Dict[str, str]:
    paths = list(required or ontology_required_paths())
    return {path: ("PASS" if (root / path).exists() else "BLOCKER") for path in paths}


def classify_repository_files(root: Path) -> Dict[str, int]:
    specs = card_type_specs(root)
    counts: Dict[str, int] = {}
    for path in root.rglob("*"):
        if not path.is_file() or ".git" in path.parts or ".pytest_cache" in path.parts:
            continue
        rel = path.relative_to(root).as_posix()
        typ = infer_card_type_from_path(rel, specs)
        counts[typ] = counts.get(typ, 0) + 1
    return counts
