"""MD Library — System Informacji o Systemie (SIS).

Skanuje wszystkie pliki .md w CIEL1 i buduje indeks z kategoryzacją,
tytułami i tagami. Wynik zapisuje do integration/registries/md_library_index.json.

Usage:
    python -m ciel_sot_agent.md_library
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .paths import resolve_project_root

_EXCLUDE = {"__pycache__", "node_modules", ".git", "venv", ".venv"}
_EXCLUDE_NAMES = {"README.md", "readme.md", "Readme.md"}

_CATEGORY_RULES: list[tuple[str, str]] = [
    ("docs/object_cards",   "object_card"),
    ("docs/architecture",   "architecture"),
    ("docs/science",        "science"),
    ("docs/operations",     "operations"),
    ("docs/audits",         "audit"),
    ("docs/analogies",      "analogy"),
    ("docs/integration",    "integration_doc"),
    ("docs/desktop",        "desktop"),
    ("contracts",           "contract"),
    ("governance",          "contract"),
    ("integration/reports", "integration_report"),
    ("integration",         "integration_doc"),
    ("src",                 "src_readme"),
    ("scripts",             "src_readme"),
    ("archive",             "archive"),
    ("app",                 "app"),
    ("packaging",           "packaging"),
    ("snapshots",           "snapshot"),
    ("tests",               "test"),
    ("vendor",              "vendor"),
    (".github",             "ci"),
]

_TAG_STOP = {"the", "a", "an", "of", "in", "and", "or", "for", "to", "is",
             "with", "on", "at", "by", "from", "as", "this", "that", "it"}


def _categorize(rel: str) -> str:
    for prefix, cat in _CATEGORY_RULES:
        if rel.startswith(prefix):
            return cat
    return "root"


def _extract_title(path: Path) -> str:
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if line.startswith("#"):
                return re.sub(r"^#+\s*", "", line).strip() or path.stem
    except OSError:
        pass
    return path.stem


def _extract_tags(title: str, rel: str) -> list[str]:
    words = re.findall(r"[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ]{3,}", title.lower())
    stem_words = re.findall(r"[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ]{3,}", Path(rel).stem.lower().replace("_", " "))
    tags = list(dict.fromkeys(w for w in words + stem_words if w not in _TAG_STOP))
    return tags[:8]


def scan(root: str | Path) -> dict[str, Any]:
    root = Path(root)
    entries: list[dict[str, Any]] = []

    for md in sorted(root.rglob("*.md")):
        if any(ex in md.parts for ex in _EXCLUDE):
            continue
        if md.name in _EXCLUDE_NAMES:
            continue
        rel = str(md.relative_to(root))
        cat = _categorize(rel)
        stat = md.stat()
        title = _extract_title(md) if cat != "object_card" else md.stem
        tags = _extract_tags(title, rel)
        entries.append({
            "path": rel,
            "category": cat,
            "title": title,
            "size_bytes": stat.st_size,
            "mtime": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
            "tags": tags,
        })

    by_category: dict[str, list[str]] = {}
    for e in entries:
        by_category.setdefault(e["category"], []).append(e["path"])

    return {
        "schema": "ciel/md-library/v0.1",
        "generated": datetime.now(timezone.utc).isoformat(),
        "total": len(entries),
        "by_category_count": {k: len(v) for k, v in sorted(by_category.items())},
        "by_category": by_category,
        "entries": entries,
    }


def build(root: str | Path | None = None) -> dict[str, Any]:
    if root is None:
        root = resolve_project_root(__file__)
    root = Path(root)
    index = scan(root)
    out = root / "integration" / "registries" / "md_library_index.json"
    out.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    return index


if __name__ == "__main__":
    import sys
    idx = build()
    print(f"Zeskanowano {idx['total']} plików MD")
    for cat, count in idx["by_category_count"].items():
        print(f"  {cat:25s}: {count}")
    sys.exit(0)
