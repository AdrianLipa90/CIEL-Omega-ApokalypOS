#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

DEFAULT_EXCLUDE_PREFIXES = [
    "integration/registries/definitions",
    "integration/imports/audio_orbital_stack/state",
    "dist",
    "build",
    ".buildozer",
    ".git",
]


def repo_relative(repo_root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve())).replace("\\", "/")
    except Exception:
        return str(path)


def normalize_id(rec: dict[str, Any]) -> str:
    kind = rec.get("kind")
    path = rec.get("path", "")
    qualname = rec.get("qualname", "")
    lineno = rec.get("lineno")
    if kind == "file" or not qualname:
        return f"file:{path}" if kind == "file" else f"definition:{path}"
    return f"definition:{path}:{qualname}@L{lineno}" if lineno is not None else f"definition:{path}:{qualname}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--exclude-prefixes", nargs="*", default=DEFAULT_EXCLUDE_PREFIXES)
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    reg_dir = repo_root / "integration" / "registries" / "definitions"
    json_path = reg_dir / "definition_registry.json"
    csv_path = reg_dir / "definition_registry.csv"
    raw = json.loads(json_path.read_text(encoding="utf-8"))
    exclude_prefixes = tuple(p.strip("/") for p in args.exclude_prefixes if p.strip())

    normalized: list[dict[str, Any]] = []
    removed = 0
    for rec in raw.get("records", []):
        path = rec.get("path", "")
        if exclude_prefixes and path.startswith(exclude_prefixes):
            removed += 1
            continue
        rec2 = dict(rec)
        rec2["id"] = normalize_id(rec2)
        normalized.append(rec2)

    payload = {
        "schema": raw.get("schema", "ciel/orbital-definition-registry/v0.1"),
        "count": len(normalized),
        "records": normalized,
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    fieldnames = ["id", "path", "language", "kind", "name", "qualname", "signature", "lineno", "end_lineno", "doc", "imports", "calls", "entrypoint"]
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for rec in normalized:
            row = {k: rec.get(k) for k in fieldnames}
            row["imports"] = ";".join(rec.get("imports", []))
            row["calls"] = ";".join(rec.get("calls", []))
            writer.writerow(row)

    print(json.dumps({
        "ok": True,
        "count": len(normalized),
        "removed": removed,
        "json": repo_relative(repo_root, json_path),
        "csv": repo_relative(repo_root, csv_path),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
