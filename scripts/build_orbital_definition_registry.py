#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import csv
import json
from pathlib import Path
from typing import Any

DEFAULT_ROOTS = ["src", "scripts", "integration"]
SCAN_SUFFIXES = {".py", ".sh", ".md", ".json", ".yaml", ".yml", ".toml"}


def module_name_from_path(path: Path) -> str:
    parts = list(path.with_suffix("").parts)
    return ".".join(parts)


def short_doc(text: str | None) -> str:
    if not text:
        return ""
    line = text.strip().splitlines()[0].strip()
    return line[:180]


def record_id(kind: str, rel_path: str, qualname: str) -> str:
    return f"{kind}:{rel_path}:{qualname}" if qualname else f"{kind}:{rel_path}"


def iter_py_definitions(source: str, rel_path: str) -> list[dict[str, Any]]:
    tree = ast.parse(source)
    records: list[dict[str, Any]] = []
    module_imports: set[str] = set()

    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                module_imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ""
            module_imports.add(base)

    records.append({
        "id": record_id("file", rel_path, ""),
        "path": rel_path,
        "language": "python",
        "kind": "file",
        "name": Path(rel_path).name,
        "qualname": module_name_from_path(Path(rel_path)),
        "signature": "",
        "lineno": 1,
        "end_lineno": len(source.splitlines()),
        "doc": short_doc(ast.get_docstring(tree)),
        "imports": sorted(x for x in module_imports if x),
        "calls": [],
        "entrypoint": "if __name__ == '__main__'" in source,
    })

    def add_callable(node: ast.AST, prefix: str = "") -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            qualname = f"{prefix}.{node.name}" if prefix else node.name
            args = [a.arg for a in node.args.args]
            calls = sorted({
                n.func.id for n in ast.walk(node)
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
            })
            records.append({
                "id": record_id("definition", rel_path, qualname),
                "path": rel_path,
                "language": "python",
                "kind": "method" if prefix else "function",
                "name": node.name,
                "qualname": qualname,
                "signature": f"{node.name}({', '.join(args)})",
                "lineno": getattr(node, 'lineno', None),
                "end_lineno": getattr(node, 'end_lineno', None),
                "doc": short_doc(ast.get_docstring(node)),
                "imports": [],
                "calls": calls,
                "entrypoint": False,
            })
        elif isinstance(node, ast.ClassDef):
            qualname = f"{prefix}.{node.name}" if prefix else node.name
            bases = []
            for b in node.bases:
                if isinstance(b, ast.Name):
                    bases.append(b.id)
                elif isinstance(b, ast.Attribute):
                    bases.append(b.attr)
            records.append({
                "id": record_id("definition", rel_path, qualname),
                "path": rel_path,
                "language": "python",
                "kind": "class",
                "name": node.name,
                "qualname": qualname,
                "signature": f"class {node.name}({', '.join(bases)})" if bases else f"class {node.name}",
                "lineno": getattr(node, 'lineno', None),
                "end_lineno": getattr(node, 'end_lineno', None),
                "doc": short_doc(ast.get_docstring(node)),
                "imports": [],
                "calls": [],
                "entrypoint": False,
            })
            for child in node.body:
                add_callable(child, qualname)
        elif isinstance(node, ast.Assign):
            names = [t.id for t in node.targets if isinstance(t, ast.Name)]
            for name in names:
                records.append({
                    "id": record_id("definition", rel_path, name),
                    "path": rel_path,
                    "language": "python",
                    "kind": "constant",
                    "name": name,
                    "qualname": name,
                    "signature": name,
                    "lineno": getattr(node, 'lineno', None),
                    "end_lineno": getattr(node, 'end_lineno', None),
                    "doc": "",
                    "imports": [],
                    "calls": [],
                    "entrypoint": False,
                })

    for node in tree.body:
        add_callable(node)

    return records


def iter_generic_file(rel_path: str, suffix: str, source: str) -> list[dict[str, Any]]:
    return [{
        "id": record_id("file", rel_path, ""),
        "path": rel_path,
        "language": suffix.lstrip('.') or 'text',
        "kind": "file",
        "name": Path(rel_path).name,
        "qualname": module_name_from_path(Path(rel_path)),
        "signature": "",
        "lineno": 1,
        "end_lineno": len(source.splitlines()),
        "doc": source.splitlines()[0][:180] if source.splitlines() else "",
        "imports": [],
        "calls": [],
        "entrypoint": False,
    }]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--roots", nargs="*", default=DEFAULT_ROOTS)
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    out_dir = repo_root / "integration" / "registries" / "definitions"
    out_dir.mkdir(parents=True, exist_ok=True)

    records: list[dict[str, Any]] = []
    for root_name in args.roots:
        root = repo_root / root_name
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix not in SCAN_SUFFIXES:
                continue
            rel_path = str(path.relative_to(repo_root)).replace('\\', '/')
            try:
                source = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                source = path.read_text(encoding="utf-8", errors="replace")
            if path.suffix == ".py":
                try:
                    recs = iter_py_definitions(source, rel_path)
                except SyntaxError:
                    recs = iter_generic_file(rel_path, path.suffix, source)
            else:
                recs = iter_generic_file(rel_path, path.suffix, source)
            records.extend(recs)

    payload = {
        "schema": "ciel/orbital-definition-registry/v0.1",
        "count": len(records),
        "records": records,
    }
    json_path = out_dir / "definition_registry.json"
    csv_path = out_dir / "definition_registry.csv"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    fieldnames = ["id", "path", "language", "kind", "name", "qualname", "signature", "lineno", "end_lineno", "doc", "imports", "calls", "entrypoint"]
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for rec in records:
            row = rec.copy()
            row["imports"] = ";".join(rec.get("imports", []))
            row["calls"] = ";".join(rec.get("calls", []))
            writer.writerow(row)

    print(json.dumps({"ok": True, "count": len(records), "json": str(json_path), "csv": str(csv_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
