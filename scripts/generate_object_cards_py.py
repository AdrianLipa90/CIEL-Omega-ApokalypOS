"""Auto-generate object cards for .py files in the CIEL project.

For each .py file (filtered by path): parse AST to extract classes/functions,
assign orbital_level/theta/horizon_class from folder rules, link to the
correct attractor sector, write/update docs/object_cards/repo/<slug>.md.

Usage:
    python scripts/generate_object_cards_py.py [--all] [--path SRC_PATH]
    --all        regenerate every card, not just new/changed files
    --path PATH  only process this specific file (relative to project root)
"""
from __future__ import annotations

import ast
import hashlib
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

# ── Project root ───────────────────────────────────────────────────────────────
_ROOT = Path(__file__).parent.parent
_CARDS_DIR = _ROOT / "docs" / "object_cards" / "repo"
_SECTORS_JSON = _ROOT / "integration" / "Orbital" / "main" / "manifests" / "sectors_global.json"

# ── Folder → orbital classification ──────────────────────────────────────────
# (folder_prefix, orbital_level, orbital_type, horizon_class, M_sem_base, attractor_system)
_FOLDER_RULES: list[tuple[str, int, str, str, float, str]] = [
    ("src/ciel_sot_agent",                        1, "F", "TRANSMISSIVE", 0.90, "noema_registry"),
    ("integration/Orbital/main",                  1, "F", "TRANSMISSIVE", 0.90, "orbital_bridge_core"),
    ("src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega", 2, "S", "POROUS",       0.80, "ciel_omega_core"),
    ("src/ciel_geometry",                         2, "S", "POROUS",       0.82, "orbital_bridge_core"),
    ("src/ciel_rh_control_mini_repo",             2, "S", "POROUS",       0.79, "orbital_bridge_core"),
    ("scripts",                                   3, "F", "OBSERVATIONAL",0.65, "noema_registry"),
    ("src/ciel-omega-demo-main",                  3, "S", "OBSERVATIONAL",0.60, "ciel_omega_core"),
    ("tests",                                     4, "S", "OBSERVATIONAL",0.40, "sync_core"),
    ("app",                                       4, "S", "OBSERVATIONAL",0.40, "noema_registry"),
]

# ── Subsystem → (theta, phi) from sectors_global ─────────────────────────────
_SUBSYSTEM_THETA: dict[str, tuple[float, float]] = {
    "noema_registry":      (0.10, 0.00),
    "ciel_omega_core":     (0.15, 0.00),
    "orbital_bridge_core": (0.20, 0.00),
    "sync_core":           (0.30, 0.00),
    "orch_orbital_core":   (0.35, 0.00),
    "db_orchestrator":     (0.40, 0.00),
}

# ── Attractor → primary attractor label ──────────────────────────────────────
_ATTRACTOR_LABEL = {
    "noema_registry":      "ent_Mr_Ciel_Apocalyptos (θ=0.0) via noema_registry",
    "orbital_bridge_core": "ent_Mr_Ciel_Apocalyptos (θ=0.0) via orbital_bridge_core",
    "ciel_omega_core":     "ent_Mr_Ciel_Apocalyptos (θ=0.0) via ciel_omega_core",
    "sync_core":           "orbital_bridge_core → ent_Mr_Ciel_Apocalyptos",
    "db_orchestrator":     "orbital_bridge_core → TSM memory",
}


def _folder_class(rel_path: str) -> tuple[int, str, str, float, str]:
    """Return (orbital_level, orbital_type, horizon_class, M_sem, attractor) for a path."""
    for prefix, lv, ot, hc, ms, att in _FOLDER_RULES:
        if rel_path.startswith(prefix):
            return lv, ot, hc, ms, att
    return 4, "S", "OBSERVATIONAL", 0.40, "noema_registry"


def _phi_from_path(rel_path: str) -> float:
    """Deterministic phi from path hash (spreads nodes within level)."""
    h = int(hashlib.md5(rel_path.encode()).hexdigest(), 16)
    return round((h % 6283) / 1000.0, 3)  # 0 … 2π


def _parse_py(path: Path) -> dict[str, Any]:
    """Extract module docstring, classes, functions via AST."""
    try:
        src = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(src)
    except Exception:
        return {"docstring": "", "classes": [], "functions": []}

    docstring = ast.get_docstring(tree) or ""
    classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    functions = [
        n.name for n in ast.walk(tree)
        if isinstance(n, ast.FunctionDef) and not n.name.startswith("__")
    ]
    return {
        "docstring": docstring[:400].strip(),
        "classes": classes[:20],
        "functions": functions[:30],
    }


def _slug(rel_path: str) -> str:
    """Convert relative path to card filename slug."""
    return rel_path.replace("/", "_").replace(".py", "") + ".md"


def _card_path(rel_path: str) -> Path:
    return _CARDS_DIR / _slug(rel_path)


def _card_id(rel_path: str) -> str:
    stem = Path(rel_path).stem.upper().replace("-", "_")[:20]
    h = hashlib.md5(rel_path.encode()).hexdigest()[:4].upper()
    return f"REPO-{stem}-{h}"


def build_card(rel_path: str, parsed: dict[str, Any], force: bool = False) -> str:
    """Build markdown card content for a .py file."""
    lv, ot, hc, ms, att = _folder_class(rel_path)
    theta_info = _SUBSYSTEM_THETA.get(att, (0.785 * lv / 2, 0.0))
    theta = theta_info[0]
    phi = _phi_from_path(rel_path)
    attractor_label = _ATTRACTOR_LABEL.get(att, att)
    filename = Path(rel_path).name
    cid = _card_id(rel_path)
    today = date.today().isoformat()

    doc_first_line = (parsed["docstring"].split("\n")[0] if parsed["docstring"] else "—")
    classes_str = ", ".join(parsed["classes"]) or "—"
    funcs_str = ", ".join(f"`{f}`" for f in parsed["functions"]) or "—"

    level_names = {1: "CORE", 2: "STRUCTURE", 3: "RELATIONAL", 4: "SATELLITE"}
    level_label = level_names.get(lv, str(lv))

    card = f"""# {filename} — {rel_path}

## Identity
- **card_id:** `{cid}`
- **path:** `{rel_path}`
- **last_indexed:** `{today}`
- **orbital_level:** {lv} ({level_label})
- **orbital_type:** `{ot}`
- **θ (theta):** `{theta:.3f}`
- **φ (phi):** `{phi:.3f}`
- **M_sem:** `{ms:.2f}`

## Anchors
- `{rel_path}`

## Attractor
- **system:** `{att}`
- **primary attractor:** {attractor_label}

## Orbital mechanics
| param | value |
|---|---|
| orbit_level | {lv} ({level_label}) |
| orbit_type | {ot} |
| θ | {theta:.3f} |
| φ | {phi:.3f} |
| horizon_class | **{hc}** |
| M_sem | {ms:.2f} |

## Horizon relation
`{hc}` — orbital level {lv}, system `{att}`.

## Role
{doc_first_line}

## Flow
- **input_from:** *inferred from folder — {att} subsystem*
- **output_to:** *inferred from folder — {att} subsystem*

## Contents
- **classes:** {classes_str}
- **functions:** {funcs_str}

## Docstring
{parsed['docstring'] or '—'}
"""
    return card


def _should_update(card_path: Path, py_path: Path, force: bool) -> bool:
    if force or not card_path.exists():
        return True
    # Update if .py is newer than card
    return py_path.stat().st_mtime > card_path.stat().st_mtime


def _iter_py_files() -> list[Path]:
    excludes = {".venv", "venv", "site-packages", "__pycache__", ".git", "node_modules"}
    result = []
    for p in _ROOT.rglob("*.py"):
        parts = set(p.parts)
        if parts & excludes:
            continue
        result.append(p)
    return result


def run(force: bool = False, single_path: str | None = None) -> None:
    _CARDS_DIR.mkdir(parents=True, exist_ok=True)

    if single_path:
        targets = [_ROOT / single_path]
    else:
        targets = _iter_py_files()

    created, updated, skipped = 0, 0, 0

    for py_path in targets:
        try:
            rel = py_path.relative_to(_ROOT).as_posix()
        except ValueError:
            continue

        card_p = _card_path(rel)
        if not _should_update(card_p, py_path, force):
            skipped += 1
            continue

        parsed = _parse_py(py_path)
        content = build_card(rel, parsed, force)

        # If card exists, preserve ## Adnotacje section
        if card_p.exists():
            existing = card_p.read_text(encoding="utf-8")
            ann_match = re.search(r"(## Adnotacje.*)", existing, re.DOTALL)
            if ann_match:
                content = content.rstrip() + "\n\n" + ann_match.group(1).strip() + "\n"
            updated += 1
        else:
            created += 1

        card_p.write_text(content, encoding="utf-8")

    print(f"Object cards: {created} created, {updated} updated, {skipped} skipped (up to date)")
    print(f"Cards directory: {_CARDS_DIR}")


if __name__ == "__main__":
    force_flag = "--all" in sys.argv
    single = None
    for i, arg in enumerate(sys.argv):
        if arg == "--path" and i + 1 < len(sys.argv):
            single = sys.argv[i + 1]
    run(force=force_flag, single_path=single)
