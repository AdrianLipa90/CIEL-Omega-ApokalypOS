#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def repo_relative(repo_root: Path, path: Path) -> str:
    """
    Compute a repository-relative POSIX-style path for a given filesystem path.
    
    If `path` can be made relative to `repo_root`, returns that relative path with forward slashes (`/`). If the relative computation fails for any reason (e.g., paths are unrelated), returns the absolute string form of `path`.
    
    Parameters:
        repo_root (Path): Repository root used as the base for relativity.
        path (Path): Path to convert to a repository-relative form.
    
    Returns:
        str: Repository-relative path with forward slashes, or the absolute path string if relativity cannot be determined.
    """
    try:
        return str(path.resolve().relative_to(repo_root.resolve())).replace("\\", "/")
    except Exception:
        return str(path)


def edge(source: str, target: str, relation: str, weight: float) -> dict[str, Any]:
    """
    Constructs an edge dictionary representing a relationship between two nodes.
    
    Parameters:
        source (str): ID of the source node.
        target (str): ID of the target node.
        relation (str): Relationship type between source and target (e.g., "contains", "imports").
        weight (float): Numeric weight for the edge; will be rounded to three decimal places.
    
    Returns:
        dict[str, Any]: Edge object with keys `"source"`, `"target"`, `"relation"`, and `"weight"` (rounded to 3 decimals).
    """
    return {
        "source": source,
        "target": target,
        "relation": relation,
        "weight": round(weight, 3),
    }


def main() -> int:
    """
    CLI entrypoint that builds nonlocal definition edges from an Orbital definition registry and writes them to a JSON output file.
    
    Reads the registry JSON from integration/registries/definitions/orbital_definition_registry.json under the repository root, derives edges between records (contains, imports, calls, orbital_resonance), deduplicates them, writes the result to integration/registries/definitions/nonlocal_definition_edges.json, and prints a JSON summary with the written path and count.
    
    Returns:
        int: Exit code; `0` on success.
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    reg_path = repo_root / "integration" / "registries" / "definitions" / "orbital_definition_registry.json"
    raw = json.loads(reg_path.read_text(encoding="utf-8"))
    records = raw["records"]

    by_path: dict[str, list[dict[str, Any]]] = {}
    by_name: dict[str, list[dict[str, Any]]] = {}
    for rec in records:
        by_path.setdefault(rec["path"], []).append(rec)
        by_name.setdefault(rec["name"], []).append(rec)

    edges: list[dict[str, Any]] = []

    for path, recs in by_path.items():
        file_nodes = [r for r in recs if r["kind"] == "file"]
        defs = [r for r in recs if r["kind"] != "file"]
        for f in file_nodes:
            for d in defs:
                edges.append(edge(f["id"], d["id"], "contains", 1.0))

    for rec in records:
        for imp in rec.get("imports", []):
            for candidate in records:
                if candidate.get("kind") == "file" and candidate.get("qualname", "").endswith(imp):
                    edges.append(edge(rec["id"], candidate["id"], "imports", 0.82))
        for call in rec.get("calls", []):
            for candidate in by_name.get(call, []):
                if candidate["id"] != rec["id"]:
                    edges.append(edge(rec["id"], candidate["id"], "calls", 0.74))

    orbit_groups: dict[str, list[dict[str, Any]]] = {}
    for rec in records:
        orbit_groups.setdefault(rec.get("orbital_role", "UNRESOLVED"), []).append(rec)
    for orbit, recs in orbit_groups.items():
        if orbit == "UNRESOLVED":
            continue
        for i, a in enumerate(recs):
            for b in recs[i + 1 : i + 4]:
                edges.append(edge(a["id"], b["id"], "orbital_resonance", 0.41))

    seen = set()
    deduped = []
    for e in edges:
        key = (e["source"], e["target"], e["relation"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(e)

    out = repo_root / "integration" / "registries" / "definitions" / "nonlocal_definition_edges.json"
    payload = {
        "schema": "ciel/nonlocal-definition-edges/v0.1",
        "count": len(deduped),
        "edges": deduped,
    }
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "count": len(deduped), "path": repo_relative(repo_root, out)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
