"""Master Semantic Calculator (MSC) — NOEMA na poziomie plików.

Dla każdego pliku w systemie liczy:
  E_raw(f) = α₁·ρ + α₂·p + α₃·w + α₄·ν + α₅·δ(χ)
  E_norm   = E_raw / Σ E_raw
  amplitude = √E_norm
  phase     = 2π · frac(hash(path) / 2³²)
  T_orbital = (a³ / M_sem_subsystem) ^ 0.5  [prawo Keplera]

Relacje między plikami (crossref graph):
  - import/from  → Python zależności
  - json/yaml ref → referencje do innych plików
  - Wynik: file_wij_graph.json (już częściowo istnieje)

Output:
  integration/registries/file_universal_catalog.json

Usage:
    python -m ciel_sot_agent.semantic_calculator
    python -m ciel_sot_agent.semantic_calculator --scan-relations
"""
from __future__ import annotations

import ast
import hashlib
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .paths import resolve_project_root

_ROOT = resolve_project_root(__file__)
_CATALOG_PATH = _ROOT / "integration" / "registries" / "file_universal_catalog.json"
_WIJ_PATH = _ROOT / "integration" / "registries" / "file_wij_graph.json"

_EXCLUDE_DIRS = {"__pycache__", "node_modules", ".git", "venv", ".venv", ".mypy_cache"}
_INCLUDE_EXTS = {".py", ".json", ".yaml", ".yml", ".md", ".txt", ".db", ".csv", ".toml", ".cfg", ".ini"}

# ── Tabele wag ──────────────────────────────────────────────────────────────

_PRESSURE_BY_TYPE = {
    # Typ pliku → ciśnienie relacyjne p ∈ [0,1]
    "registry":    0.95,
    "contract":    0.95,
    "noema_card":  0.92,
    "sectors":     0.92,
    "couplings":   0.90,
    "bridge":      0.88,
    "executor":    0.85,
    "orchestrator":0.85,
    "pipeline":    0.85,
    "index":       0.82,
    "manifest":    0.80,
    "algorithm":   0.78,
    "memory":      0.75,
    "config":      0.70,
    "hook":        0.68,
    "report":      0.55,
    "test":        0.40,
    "archive":     0.20,
    "other":       0.35,
}

_WEIGHT_BY_LEVEL = {
    # orbital_level → waga ontologiczna w
    0: 1.00,  # attractor
    1: 0.95,  # core
    2: 0.85,  # structure
    3: 0.70,  # relational
    4: 0.55,  # satellite
    99: 0.40, # unknown
}

_SUBSYSTEM_BY_PATH = {
    # prefix ścieżki → (subsystem_id, orbital_level, M_sem)
    "src/ciel_sot_agent/synchronize":        ("sync_core",           1, 0.91),
    "src/ciel_sot_agent/orbital_bridge":     ("orbital_bridge_core", 1, 0.95),
    "src/ciel_sot_agent/ciel_pipeline":      ("ciel_omega_core",     1, 0.97),
    "src/ciel_sot_agent/noema_sot":          ("noema_registry",      1, 0.99),
    "src/ciel_sot_agent/orch_orbital":       ("orch_orbital_core",   1, 0.88),
    "src/ciel_sot_agent/orbital_db":         ("db_orchestrator",     1, 0.86),
    "src/ciel_sot_agent/subsystem_registry": ("noema_registry",      1, 0.99),
    "src/ciel_sot_agent/semantic_calculator":("noema_registry",      1, 0.99),
    "src/ciel_sot_agent/diagnostics":        ("noema_registry",      1, 0.92),
    "src/ciel_sot_agent/md_library":         ("noema_registry",      1, 0.88),
    "src/ciel_sot_agent":                    ("noema_registry",      1, 0.80),
    "integration/Orbital/main":              ("orbital_bridge_core", 1, 0.93),
    "integration/subsystems":                ("noema_registry",      1, 0.90),
    "integration/registries":                ("noema_registry",      2, 0.85),
    "integration/couplings":                 ("orbital_bridge_core", 2, 0.85),
    "integration/db":                        ("db_orchestrator",     2, 0.82),
    "contracts":                             ("noema_registry",      0, 1.00),
    "governance":                            ("noema_registry",      0, 0.98),
    "scripts":                               ("sync_core",           1, 0.75),
    "src/CIEL_OMEGA_COMPLETE_SYSTEM/CIEL_MEMORY_SYSTEM": ("db_orchestrator", 2, 0.88),
    "src/CIEL_OMEGA_COMPLETE_SYSTEM":        ("ciel_omega_core",     2, 0.90),
    "src/ciel_geometry":                     ("orbital_bridge_core", 2, 0.82),
    "docs/architecture":                     ("noema_registry",      2, 0.78),
    "docs/science":                          ("noema_registry",      2, 0.75),
    "docs/operations":                       ("noema_registry",      2, 0.70),
    "docs/object_cards":                     ("noema_registry",      3, 0.50),
    "integration":                           ("db_orchestrator",     2, 0.70),
    "docs":                                  ("noema_registry",      3, 0.60),
    "src":                                   ("noema_registry",      2, 0.70),
}


def _classify_path(rel: str) -> tuple[str, str, int, float]:
    """Returns (subsystem_id, file_type_char, orbital_level, M_sem_subsystem)."""
    # subsystem lookup — najdłuższy prefix wins
    sub_id = "noema_registry"
    orbital_level = 99
    m_sem_sub = 0.5
    best_len = -1
    for prefix, (sid, lv, ms) in _SUBSYSTEM_BY_PATH.items():
        if rel.startswith(prefix) and len(prefix) > best_len:
            sub_id, orbital_level, m_sem_sub = sid, lv, ms
            best_len = len(prefix)

    # character / pressure class
    name = Path(rel).stem.lower()
    parts = rel.lower().split("/")
    if any(p in {"contracts", "governance"} for p in parts):
        char = "contract"
    elif "test" in parts or name.startswith("test_"):
        char = "test"
    elif "archive" in parts or "snapshots" in parts:
        char = "archive"
    elif "registry" in name or "registr" in name:
        char = "registry"
    elif "sector" in name or "coupling" in name:
        char = "sectors" if "sector" in name else "couplings"
    elif "bridge" in name:
        char = "bridge"
    elif "pipeline" in name or "engine" in name:
        char = "pipeline"
    elif "orchestrat" in name:
        char = "orchestrator"
    elif "synchronize" in name or "sync" in name:
        char = "executor"
    elif "hook" in name:
        char = "hook"
    elif "manifest" in name or "noema_card" in name:
        char = "noema_card" if "noema_card" in name else "manifest"
    elif "index" in name or "catalog" in name or "library" in name:
        char = "index"
    elif "report" in parts or "reports" in parts:
        char = "report"
    elif "algorithm" in name or "dynamics" in name or "metrics" in name:
        char = "algorithm"
    elif "memory" in name or "ledger" in name:
        char = "memory"
    elif "config" in name or "settings" in name or "defaults" in name:
        char = "config"
    else:
        char = "other"

    return sub_id, char, orbital_level, m_sem_sub


def _file_hash_int(rel: str) -> int:
    return int(hashlib.sha256(rel.encode()).hexdigest()[:8], 16)


def _phase_from_path(rel: str) -> float:
    h = _file_hash_int(rel)
    return (h / 0xFFFFFFFF) * 2 * math.pi


def _recency_score(mtime: float, now: float) -> float:
    """ν ∈ [0,1] — 1.0 = zmieniony dziś, 0 = ponad rok temu."""
    age_days = (now - mtime) / 86400
    return max(0.0, 1.0 - age_days / 365.0)


def _scan_python_imports(path: Path) -> list[str]:
    """Parsuje importy Pythona, zwraca listę modułów."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return []
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return imports


def _scan_json_refs(path: Path, all_rels: set[str]) -> list[str]:
    """Szuka ścieżek do innych plików w JSONie."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    found = []
    # szuka stringów które wyglądają jak ścieżki
    for m in re.finditer(r'"([^"]+\.(py|json|yaml|yml|md|db|csv))"', text):
        candidate = m.group(1)
        # sprawdź czy jest w katalogu projektu
        for rel in all_rels:
            if rel.endswith(candidate) or candidate in rel:
                found.append(rel)
                break
    return found


def scan_files(root: Path) -> list[dict[str, Any]]:
    """Skanuje wszystkie pliki i buduje listę wpisów."""
    now = datetime.now(timezone.utc).timestamp()
    entries = []

    all_paths = sorted(p for p in root.rglob("*")
                       if p.is_file()
                       and p.suffix in _INCLUDE_EXTS
                       and not any(ex in p.parts for ex in _EXCLUDE_DIRS))

    # Pierwsza pętla: zbieramy E_raw dla każdego pliku
    raw_entries = []
    for i, fpath in enumerate(all_paths):
        rel = str(fpath.relative_to(root))
        stat = fpath.stat()
        sub_id, char, orbital_level, m_sem_sub = _classify_path(rel)

        # ρ — gęstość (size-based, log-normalizowane)
        size = stat.st_size
        rho = math.log1p(size) / math.log1p(1_000_000)  # [0,1] przy max ~1MB

        # p — ciśnienie
        p = _PRESSURE_BY_TYPE.get(char, 0.35)

        # w — waga ontologiczna
        w = _WEIGHT_BY_LEVEL.get(orbital_level, 0.40)

        # ν — recency
        nu = _recency_score(stat.st_mtime, now)

        # E_raw = α₁ρ + α₂p + α₃w + α₄ν  (α równe, kalibrowalny)
        e_raw = 0.25 * rho + 0.35 * p + 0.30 * w + 0.10 * nu

        raw_entries.append({
            "idx": i + 1,
            "path": rel,
            "ext": fpath.suffix,
            "size_bytes": size,
            "mtime": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
            "subsystem": sub_id,
            "character": char,
            "orbital_level": orbital_level,
            "M_sem_subsystem": round(m_sem_sub, 4),
            "rho": round(rho, 4),
            "pressure": round(p, 4),
            "weight": round(w, 4),
            "recency": round(nu, 4),
            "E_raw": round(e_raw, 6),
            "phase": round(_phase_from_path(rel), 6),
        })

    # Normalizacja energii
    total_e = sum(e["E_raw"] for e in raw_entries) or 1.0
    for e in raw_entries:
        e_norm = e["E_raw"] / total_e
        amp = math.sqrt(e_norm)
        # Okres orbitalny — Kepler: T² ∝ a³/M_sem, a ∝ 1/w (bliżej atraktora = mniejsza a)
        a = 1.0 - e["weight"] * e["M_sem_subsystem"]  # półoś — odległość od atraktora
        a = max(a, 0.01)
        m_eff = e["M_sem_subsystem"]
        t_orbital = math.sqrt(a ** 3 / m_eff) if m_eff > 0 else 99.0
        e["E_norm"] = round(e_norm, 8)
        e["amplitude"] = round(amp, 6)
        e["T_orbital"] = round(t_orbital, 4)
        noema_stem = Path(e["path"]).stem.replace("-", "_").replace(".", "_")[:20]
        e["noema_id"] = f"NL-FILE-{noema_stem}-{e['idx']:04d}"
        entries.append(e)

    return entries


def build_wij_relations(entries: list[dict[str, Any]], root: Path) -> dict[str, list[dict]]:
    """Buduje graf relacji między plikami — crossref/import/reference."""
    rel_to_entry = {e["path"]: e for e in entries}
    all_rels = set(rel_to_entry.keys())

    graph: dict[str, list[dict]] = {}

    for e in entries:
        path = root / e["path"]
        rels = []

        if e["ext"] == ".py":
            imports = _scan_python_imports(path)
            for imp in imports:
                # Mapuj moduł Python → plik
                imp_parts = imp.replace(".", "/")
                for rel in all_rels:
                    if imp_parts in rel and rel.endswith(".py"):
                        rels.append({"target": rel, "relation": "imports", "W_ij": 0.7})
                        break

        elif e["ext"] in {".json", ".yaml", ".yml"}:
            refs = _scan_json_refs(path, all_rels)
            for ref in refs:
                if ref != e["path"]:
                    rels.append({"target": ref, "relation": "references", "W_ij": 0.5})

        # Sprzężenie do subsystem noema_card
        noema_card_rel = f"integration/subsystems/{e['subsystem']}/noema_card.json"
        if noema_card_rel in all_rels and noema_card_rel != e["path"]:
            rels.append({"target": noema_card_rel, "relation": "belongs_to_subsystem", "W_ij": 0.9})

        if rels:
            graph[e["path"]] = rels

    return graph


def build(root: Path | None = None, scan_relations: bool = True) -> dict[str, Any]:
    if root is None:
        root = _ROOT
    root = Path(root)

    entries = scan_files(root)
    graph = build_wij_relations(entries, root) if scan_relations else {}

    catalog = {
        "schema": "ciel/file-universal-catalog/v0.1",
        "generated": datetime.now(timezone.utc).isoformat(),
        "total": len(entries),
        "alpha_weights": {"rho": 0.25, "pressure": 0.35, "weight": 0.30, "recency": 0.10},
        "by_subsystem": {},
        "by_level": {},
        "entries": entries,
    }

    for e in entries:
        catalog["by_subsystem"].setdefault(e["subsystem"], 0)
        catalog["by_subsystem"][e["subsystem"]] += 1
        catalog["by_level"].setdefault(str(e["orbital_level"]), 0)
        catalog["by_level"][str(e["orbital_level"])] += 1

    _CATALOG_PATH.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")

    if scan_relations:
        wij = {
            "schema": "ciel/file-wij-graph/v0.2",
            "generated": datetime.now(timezone.utc).isoformat(),
            "total_nodes": len(entries),
            "total_edges": sum(len(v) for v in graph.values()),
            "graph": graph,
        }
        _WIJ_PATH.write_text(json.dumps(wij, ensure_ascii=False, indent=2), encoding="utf-8")

    return catalog


if __name__ == "__main__":
    import sys
    scan_rel = "--scan-relations" in sys.argv or "--full" in sys.argv
    cat = build(scan_relations=scan_rel)
    print(f"Zeskanowano {cat['total']} plików")
    print("\nPo subsystemie:")
    for sub, cnt in sorted(cat["by_subsystem"].items(), key=lambda x: -x[1]):
        print(f"  {sub:30s}: {cnt}")
    print("\nPo poziomie orbitalnym:")
    for lv, cnt in sorted(cat["by_level"].items()):
        print(f"  lv={lv}: {cnt}")
    sys.exit(0)
