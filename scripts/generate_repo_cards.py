#!/usr/bin/env python3
"""
Automatyczny generator kart obiektów dla repo CIEL.
Skanuje src/**/*.py i kluczowe JSONy, generuje/aktualizuje karty w docs/object_cards/repo/.
Uruchamiany: ręcznie, z hooka post-commit, lub ze Stop hooka.
"""
from __future__ import annotations
import ast, json, os, sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).parent.parent
CARDS_DIR = REPO / "docs" / "object_cards" / "repo"
CARDS_DIR.mkdir(parents=True, exist_ok=True)

SCAN_DIRS = [
    REPO / "src" / "ciel_sot_agent",
    REPO / "scripts",
    REPO / "src" / "CIEL_OMEGA_COMPLETE_SYSTEM" / "ciel_omega",
]
SKIP = {"__pycache__", ".venv", "venv", "node_modules"}

KEY_JSONS = [
    REPO / "integration/Orbital/main/manifests/sectors_global.json",
    REPO / "integration/Orbital/main/manifests/couplings_global.json",
    REPO / "integration/reports/orbital_bridge/orbital_bridge_report.json",
    REPO / "integration/reports/ciel_pipeline_report.json",
]


def _extract_py_info(path: Path) -> dict:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return {}
    classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    functions = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    docstring = ast.get_docstring(tree) or ""
    return {"classes": classes, "functions": functions[:20], "docstring": docstring[:300]}


def _card_path(src: Path) -> Path:
    rel = src.relative_to(REPO)
    safe = str(rel).replace("/", "_").replace(".py", "").replace(".json", "")
    return CARDS_DIR / f"{safe}.md"


def _write_py_card(src: Path, info: dict) -> None:
    card = _card_path(src)
    rel = src.relative_to(REPO)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    existing_note = ""
    if card.exists():
        for line in card.read_text().splitlines():
            if line.startswith("## Note"):
                existing_note = "\n## Note\n"
            elif existing_note and line.strip():
                existing_note += line + "\n"
    classes_str = ", ".join(info["classes"]) or "—"
    funcs_str = ", ".join(info["functions"]) or "—"
    content = f"""# {src.name} — {rel}

## Identity
- **path:** `{rel}`
- **last_indexed:** `{now}`

## Contents
- **classes:** {classes_str}
- **functions:** {funcs_str}

## Docstring
{info.get('docstring') or '—'}
{existing_note or ''}"""
    card.write_text(content, encoding="utf-8")


def _write_json_card(src: Path) -> None:
    if not src.exists():
        return
    card = _card_path(src)
    rel = src.relative_to(REPO)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    try:
        data = json.loads(src.read_text(encoding="utf-8"))
        keys = list(data.keys())[:15] if isinstance(data, dict) else []
        keys_str = ", ".join(keys)
    except Exception:
        keys_str = "—"
    content = f"""# {src.name} — {rel}

## Identity
- **path:** `{rel}`
- **last_indexed:** `{now}`
- **type:** JSON artifact

## Top-level keys
{keys_str}
"""
    card.write_text(content, encoding="utf-8")


def _write_index(cards: list[Path]) -> None:
    idx = CARDS_DIR / "INDEX.md"
    lines = ["# Repo Object Cards — auto-generated\n"]
    for c in sorted(cards):
        lines.append(f"- [{c.stem}](./{c.name})")
    idx.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    cards: list[Path] = []
    count = 0
    for scan_dir in SCAN_DIRS:
        if not scan_dir.exists():
            continue
        for py in scan_dir.rglob("*.py"):
            if any(s in py.parts for s in SKIP):
                continue
            info = _extract_py_info(py)
            _write_py_card(py, info)
            cards.append(_card_path(py))
            count += 1
    for jpath in KEY_JSONS:
        _write_json_card(jpath)
        cards.append(_card_path(jpath))
        count += 1
    _write_index(cards)
    print(f"[generate_repo_cards] {count} kart wygenerowanych → {CARDS_DIR}", file=sys.stderr)


if __name__ == "__main__":
    main()
