"""NOEMA file-sense layer.

Builds a semantic registry over repository files so cleanup and inspection can
reason about function, ownership, hierarchy, and lifecycle rather than raw
paths alone.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .paths import resolve_project_root

_ROOT = resolve_project_root(__file__)
_DEFINITION_REGISTRY = _ROOT / "integration" / "registries" / "definitions" / "orbital_definition_registry.json"
_INTERNAL_CARDS = _ROOT / "integration" / "registries" / "definitions" / "internal_subsystem_cards.json"
_SYNC_REGISTRY = _ROOT / "integration" / "registries" / "definitions" / "subsystem_sync_registry.json"
_OUTPUT_REGISTRY = _ROOT / "integration" / "registries" / "file_sense_registry.json"
_OUTPUT_REPORT = _ROOT / "integration" / "reports" / "file_sense_report.json"
_AUDIT_ANNOTATIONS = _ROOT / "integration" / "registries" / "file_sense_audit_annotations.json"

_CANONICAL_PREFIXES = (
    "src/",
    "scripts/",
    "tests/",
    "docs/",
    "contracts/",
    "manifests/",
    "integration/",
    "app/",
)
_GENERATED_TOKENS = ("/generated/", "_generated", ".generated", "generated/")
_LEGACY_TOKENS = ("legacy", "archive", "deprecated", "snapshot", "old")
_ARTIFACT_EXTS = {".json", ".jsonl", ".db", ".sqlite", ".csv", ".yaml", ".yml", ".npz", ".npy", ".md", ".html"}
_EXECUTABLE_EXTS = {".py", ".sh", ".ts", ".tsx", ".js"}


def _load_json(path: Path, fallback: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback


def _normalize_annotation(raw: dict[str, Any]) -> dict[str, Any]:
    comment = str(raw.get("audit_comment") or raw.get("comment") or "").strip()
    flags = raw.get("audit_flags") or raw.get("flags") or []
    if isinstance(flags, str):
        flags = [flags]
    flags = [str(flag).strip() for flag in flags if str(flag).strip()]
    stage = str(raw.get("audit_stage") or raw.get("stage") or "").strip()
    source = str(raw.get("audit_source") or raw.get("source") or "manual_audit").strip()
    return {
        "audit_comment": comment,
        "audit_flags": flags,
        "audit_stage": stage,
        "audit_source": source,
    }


def _path_location(path: str) -> str:
    parts = path.split("/")
    return parts[0] if parts else "root"


def _infer_file_type(path: str, rec: dict[str, Any]) -> str:
    ext = Path(path).suffix.lower()
    if path.endswith(".md"):
        if "/object_cards/" in path:
            return "object_card"
        return "document"
    if path.endswith(".json") or path.endswith(".jsonl") or path.endswith(".yaml") or path.endswith(".yml"):
        return "manifest" if "manifest" in path or "registry" in path or "index" in path else "data"
    if ext in {".db", ".sqlite"}:
        return "database"
    if path.startswith("tests/"):
        return "test"
    if path.startswith("scripts/"):
        return "script"
    if path.startswith("app/"):
        return "app_ui"
    if path.startswith("integration/"):
        return "integration_asset"
    if ext in {".py", ".js", ".ts", ".tsx"}:
        if rec.get("entrypoint"):
            return "entrypoint"
        return "code"
    return ext.lstrip(".") or "unknown"


def _infer_subsystem(path: str, rec: dict[str, Any], internal: dict[str, Any] | None) -> str:
    board = rec.get("board_card_id") or (internal or {}).get("board_card_id")
    if path.startswith("src/ciel_sot_agent/"):
        return "ciel_sot_agent"
    if path.startswith("src/CIEL_OMEGA_COMPLETE_SYSTEM/"):
        return "ciel_omega_complete_system"
    if path.startswith("integration/Orbital/"):
        return "orbital"
    if path.startswith("app/"):
        return "portal_app"
    if isinstance(board, str) and board and not board.startswith("file:"):
        return board
    semantic = str(rec.get("semantic_role", "")).lower()
    if "noema" in semantic or "noema" in path.lower():
        return "noema_registry"
    if "orbital" in path.lower():
        return "orbital_bridge_core"
    if "pipeline" in path.lower():
        return "ciel_omega_core"
    return str(rec.get("subsystem_kind") or (internal or {}).get("subsystem_kind") or "unassigned")


def _infer_purpose(path: str, rec: dict[str, Any]) -> str:
    lowered = f"{path} {rec.get('semantic_role','')} {rec.get('manybody_role','')}".lower()
    if "test" in lowered:
        return "validation"
    if any(token in lowered for token in ["registry", "catalog", "index", "manifest", "schema"]):
        return "registry"
    if any(token in lowered for token in ["report", "export", "projection"]):
        return "reporting"
    if any(token in lowered for token in ["bridge", "pipeline", "runtime", "orchestrator"]):
        return "runtime"
    if any(token in lowered for token in ["card", "docs", "contract"]):
        return "documentation"
    return "support"


def _infer_status(path: str, rec: dict[str, Any], internal: dict[str, Any] | None) -> str:
    lowered = path.lower()
    if any(token in lowered for token in _LEGACY_TOKENS):
        return "legacy"
    if any(token in lowered for token in _GENERATED_TOKENS):
        return "generated"
    if path.startswith("tests/"):
        return "active_test"
    if path.startswith(("src/", "scripts/", "app/")):
        return "active"
    if path.startswith(("docs/", "contracts/")):
        return "reference"
    if path.startswith("integration/"):
        if rec.get("kind") == "file" and Path(path).suffix.lower() in _ARTIFACT_EXTS:
            return "generated"
        return "integration"
    if internal and internal.get("internal_candidate_states"):
        return "classified"
    return "unknown"


def _infer_authority(path: str, status: str, purpose: str) -> str:
    if path.startswith("src/"):
        return "code_canonical"
    if path.startswith("scripts/"):
        return "execution_support"
    if path.startswith("tests/"):
        return "validation_support"
    if path.startswith("docs/object_cards/"):
        return "object_card_sot"
    if path.startswith("docs/"):
        return "documentation"
    if path.startswith("contracts/"):
        return "contract"
    if path.startswith("integration/") and status == "generated":
        return "generated_projection"
    if purpose == "registry":
        return "registry_surface"
    return "auxiliary"


def _safe_flags(path: str, status: str, authority: str) -> tuple[bool, bool]:
    safe_to_delete = status in {"generated", "legacy"} and authority not in {"code_canonical", "contract", "object_card_sot"}
    safe_to_move = authority not in {"code_canonical", "contract", "object_card_sot"} and not path.startswith(("src/", "scripts/"))
    return safe_to_move, safe_to_delete


def _build_sync_lookup(sync_doc: dict[str, Any]) -> dict[str, dict[str, Any]]:
    lookup: dict[str, dict[str, Any]] = {}
    for rec in sync_doc.get("records", []):
        board_id = rec.get("board_card_id")
        if isinstance(board_id, str) and board_id:
            lookup[board_id] = rec
    return lookup


def _build_internal_lookup(internal_doc: dict[str, Any]) -> dict[str, dict[str, Any]]:
    lookup: dict[str, dict[str, Any]] = {}
    for rec in internal_doc.get("internal_cards", []):
        export_id = rec.get("export_card_id")
        internal_id = rec.get("internal_card_id")
        for key in (export_id, internal_id):
            if isinstance(key, str) and key and key not in lookup:
                lookup[key] = rec
    return lookup


def _build_annotation_lookup(annotation_doc: dict[str, Any]) -> dict[str, dict[str, Any]]:
    lookup: dict[str, dict[str, Any]] = {}
    for raw in annotation_doc.get("annotations", []):
        path = str(raw.get("path", "")).strip()
        if not path:
            continue
        lookup[path] = _normalize_annotation(raw)
    return lookup


def build_registry(repo_root: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root) if repo_root else _ROOT
    definition_doc = _load_json(root / _DEFINITION_REGISTRY.relative_to(_ROOT), {"records": []})
    internal_doc = _load_json(root / _INTERNAL_CARDS.relative_to(_ROOT), {"internal_cards": []})
    sync_doc = _load_json(root / _SYNC_REGISTRY.relative_to(_ROOT), {"records": []})
    annotation_doc = _load_json(root / _AUDIT_ANNOTATIONS.relative_to(_ROOT), {"annotations": []})
    internal_lookup = _build_internal_lookup(internal_doc)
    sync_lookup = _build_sync_lookup(sync_doc)
    annotation_lookup = _build_annotation_lookup(annotation_doc)

    entries: list[dict[str, Any]] = []
    seen_paths: set[str] = set()

    for rec in definition_doc.get("records", []):
        path = str(rec.get("path", "")).strip()
        if not path or path in seen_paths:
            continue
        seen_paths.add(path)
        if not path.startswith(_CANONICAL_PREFIXES):
            continue

        board_card_id = rec.get("board_card_id")
        internal = internal_lookup.get(str(board_card_id), None) if board_card_id else None
        sync = sync_lookup.get(str(board_card_id), {}) if board_card_id else {}
        file_type = _infer_file_type(path, rec)
        purpose = _infer_purpose(path, rec)
        status = _infer_status(path, rec, internal)
        authority = _infer_authority(path, status, purpose)
        safe_to_move, safe_to_delete = _safe_flags(path, status, authority)
        ext = Path(path).suffix.lower()
        annotation = annotation_lookup.get(path, {})

        entries.append({
            "path": path,
            "location": _path_location(path),
            "extension": ext,
            "file_type": file_type,
            "language": rec.get("language", ""),
            "kind": rec.get("kind", "file"),
            "orbital_role": rec.get("orbital_role", "UNRESOLVED"),
            "semantic_role": rec.get("semantic_role", "unresolved"),
            "subsystem": _infer_subsystem(path, rec, internal),
            "purpose": purpose,
            "manybody_role": rec.get("manybody_role", "UNSET"),
            "board_card_id": board_card_id,
            "container_card_id": rec.get("container_card_id"),
            "horizon_id": rec.get("horizon_id"),
            "sync_scope": (internal or {}).get("sync_scope"),
            "tau_orbit": sync.get("tau_orbit"),
            "tau_system": sync.get("tau_system"),
            "lifecycle_status": status,
            "authority_class": authority,
            "generated": status == "generated",
            "safe_to_move": safe_to_move,
            "safe_to_delete": safe_to_delete,
            "entrypoint": bool(rec.get("entrypoint")),
            "imports_count": len(rec.get("imports", []) or []),
            "calls_count": len(rec.get("calls", []) or []),
            "audit_comment": annotation.get("audit_comment", ""),
            "audit_flags": annotation.get("audit_flags", []),
            "audit_stage": annotation.get("audit_stage", ""),
            "audit_source": annotation.get("audit_source", ""),
        })

    for path, annotation in annotation_lookup.items():
        if path in seen_paths:
            continue
        if not path.startswith(_CANONICAL_PREFIXES):
            continue
        status = "annotated_only"
        purpose = _infer_purpose(path, {})
        authority = _infer_authority(path, status, purpose)
        safe_to_move, safe_to_delete = _safe_flags(path, status, authority)
        ext = Path(path).suffix.lower()
        entries.append({
            "path": path,
            "location": _path_location(path),
            "extension": ext,
            "file_type": _infer_file_type(path, {}),
            "language": "",
            "kind": "file",
            "orbital_role": "AUDIT_ONLY",
            "semantic_role": "audit_annotation_only",
            "subsystem": _infer_subsystem(path, {}, None),
            "purpose": purpose,
            "manybody_role": "UNSET",
            "board_card_id": None,
            "container_card_id": None,
            "horizon_id": None,
            "sync_scope": None,
            "tau_orbit": None,
            "tau_system": None,
            "lifecycle_status": status,
            "authority_class": authority,
            "generated": False,
            "safe_to_move": safe_to_move,
            "safe_to_delete": safe_to_delete,
            "entrypoint": False,
            "imports_count": 0,
            "calls_count": 0,
            "audit_comment": annotation.get("audit_comment", ""),
            "audit_flags": annotation.get("audit_flags", []),
            "audit_stage": annotation.get("audit_stage", ""),
            "audit_source": annotation.get("audit_source", ""),
        })

    counts = {
        "by_file_type": dict(sorted(Counter(e["file_type"] for e in entries).items())),
        "by_location": dict(sorted(Counter(e["location"] for e in entries).items())),
        "by_subsystem": dict(sorted(Counter(e["subsystem"] for e in entries).items())),
        "by_status": dict(sorted(Counter(e["lifecycle_status"] for e in entries).items())),
        "by_authority": dict(sorted(Counter(e["authority_class"] for e in entries).items())),
        "audit_flag_counts": dict(sorted(Counter(flag for e in entries for flag in e.get("audit_flags", [])).items())),
        "annotated_entries": sum(1 for e in entries if e.get("audit_comment") or e.get("audit_flags")),
    }

    return {
        "schema": "ciel/noema-file-sense-registry/v0.2",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "count": len(entries),
        "entries": entries,
        "counts": counts,
    }


def filter_entries(
    registry: dict[str, Any],
    *,
    file_type: str | None = None,
    location: str | None = None,
    subsystem: str | None = None,
    status: str | None = None,
    authority: str | None = None,
    purpose: str | None = None,
    path_prefix: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    entries = registry.get("entries", [])

    def _match(entry: dict[str, Any]) -> bool:
        if file_type and entry.get("file_type") != file_type:
            return False
        if location and entry.get("location") != location:
            return False
        if subsystem and entry.get("subsystem") != subsystem:
            return False
        if status and entry.get("lifecycle_status") != status:
            return False
        if authority and entry.get("authority_class") != authority:
            return False
        if purpose and entry.get("purpose") != purpose:
            return False
        if path_prefix and not str(entry.get("path", "")).startswith(path_prefix):
            return False
        return True

    matched = [entry for entry in entries if _match(entry)]
    matched.sort(key=lambda item: (item.get("location", ""), item.get("path", "")))
    if limit is not None:
        return matched[:limit]
    return matched


def inspect_registry(
    *,
    repo_root: str | Path | None = None,
    file_type: str | None = None,
    location: str | None = None,
    subsystem: str | None = None,
    status: str | None = None,
    authority: str | None = None,
    purpose: str | None = None,
    path_prefix: str | None = None,
    limit: int = 25,
    write: bool = False,
) -> dict[str, Any]:
    registry = build_registry(repo_root=repo_root)
    matches = filter_entries(
        registry,
        file_type=file_type,
        location=location,
        subsystem=subsystem,
        status=status,
        authority=authority,
        purpose=purpose,
        path_prefix=path_prefix,
        limit=limit,
    )
    counts = registry.get("counts", {})
    top_subsystems = dict(sorted((counts.get("by_subsystem") or {}).items(), key=lambda kv: (-kv[1], kv[0]))[:15])
    report = {
        "schema": "ciel/noema-file-sense-report/v0.2",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "filters": {
            "file_type": file_type,
            "location": location,
            "subsystem": subsystem,
            "status": status,
            "authority": authority,
            "purpose": purpose,
            "path_prefix": path_prefix,
            "limit": limit,
        },
        "registry_count": registry.get("count", 0),
        "match_count": len(matches),
        "counts": {
            "by_file_type": counts.get("by_file_type", {}),
            "by_location": counts.get("by_location", {}),
            "by_status": counts.get("by_status", {}),
            "by_authority": counts.get("by_authority", {}),
            "audit_flag_counts": counts.get("audit_flag_counts", {}),
            "annotated_entries": counts.get("annotated_entries", 0),
            "top_subsystems": top_subsystems,
        },
        "matches": matches,
    }
    if write:
        write_registry(registry, report, repo_root=repo_root)
    return report


def write_registry(registry: dict[str, Any], report: dict[str, Any], repo_root: str | Path | None = None) -> None:
    root = Path(repo_root) if repo_root else _ROOT
    registry_path = root / _OUTPUT_REGISTRY.relative_to(_ROOT)
    report_path = root / _OUTPUT_REPORT.relative_to(_ROOT)
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2), encoding="utf-8")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build and inspect the NOEMA semantic file registry.")
    parser.add_argument("--repo-root", default=None, help="Optional repository root.")
    parser.add_argument("--file-type", default=None)
    parser.add_argument("--location", default=None)
    parser.add_argument("--subsystem", default=None)
    parser.add_argument("--status", default=None)
    parser.add_argument("--authority", default=None)
    parser.add_argument("--purpose", default=None)
    parser.add_argument("--path-prefix", default=None)
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--write", action="store_true", help="Write registry and report to integration/.")
    args = parser.parse_args(argv)

    report = inspect_registry(
        repo_root=args.repo_root,
        file_type=args.file_type,
        location=args.location,
        subsystem=args.subsystem,
        status=args.status,
        authority=args.authority,
        purpose=args.purpose,
        path_prefix=args.path_prefix,
        limit=args.limit,
        write=args.write,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
