"""Master Semantic Calculator v2 — afektywna waga semantyczna plików.

Geometria: sfera Blocha z podziałem N/S:
  Biegun N (θ=0):  fakty fizyczne — kod wykonywalny, hardware, dane mierzalne
  Biegun S (θ=π):  abstrakcja — intencja, teoria, wyobraźnia

6 węzłów inferencji (tetraedry realno-urojone):
  Realny (wokół N, θ≈1.911):  T1(φ=0), T2(φ=2π/3), T3(φ=4π/3)
  Urojony (wokół S, θ≈1.231): T4(φ=π/3), T5(φ=π),   T6(φ=5π/3)

Trzy źródła wag semantycznych:
  M_EC  — Euler-Collatz: bliskość do bieguna N (fakt fizyczny, kod wykonywalny)
  M_ZS  — Zeta-Schrödinger: projekcja na oś intencji (trwanie, nietrywialność)
  M_rel — R(S,I): centralność w grafie zależności (udział w przestrzeni relacyjnej)

Waga końcowa: M_sem = α·M_EC + β·M_ZS + γ·M_rel + δ·C_dep + ε·C_exec

Używa ciel_geometry.semantic_mass.compute_sector_mass() — nie reimplementuje.

Usage:
    python -m ciel_sot_agent.semantic_calculator_v2
    python -m ciel_sot_agent.semantic_calculator_v2 --output integration/registries/file_universal_catalog.json
"""
from __future__ import annotations

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .paths import resolve_project_root

_ROOT = resolve_project_root(__file__)
_CATALOG_OUT = _ROOT / "integration" / "registries" / "file_universal_catalog.json"
_WIJ_PATH    = _ROOT / "integration" / "registries" / "file_wij_graph.json"

# Atraktor — ent_Mr_Ciel_Apocalyptos: theta=0, phi=0.0053, rho_override=1.0
# Pozycja w przestrzeni stanów Poincarégo:
_ATTRACTOR_THETA = 0.0
_ATTRACTOR_PHI   = 0.0053
_ATTRACTOR_X, _ATTRACTOR_Y = 0.0, 0.0   # theta≈0 → rho≈0 → środek dysku

_EXCLUDE_DIRS = {"__pycache__", "node_modules", ".git", "venv", ".venv", ".mypy_cache"}
_INCLUDE_EXTS = {".py", ".json", ".yaml", ".yml", ".md", ".txt", ".db", ".csv", ".toml", ".cfg"}

# ── Geometria sferyczna N/S ──────────────────────────────────────────────────

_THETA_TETRA_REAL = math.acos(-1.0 / 3.0)   # ≈ 1.911 rad — wierzchołki tetraedru realnego
_THETA_TETRA_IMAG = math.pi - _THETA_TETRA_REAL  # ≈ 1.231 rad — tetraedr urojony

# 6 węzłów inferencji (theta, phi, charakter semantyczny)
_INFERENCE_NODES = [
    (_THETA_TETRA_REAL, 0.0,              "contract_axiom",   "T1"),   # kontrakty, axiomy
    (_THETA_TETRA_REAL, 2*math.pi/3,      "algorithm_dynamic","T2"),   # algorytmy, dynamika
    (_THETA_TETRA_REAL, 4*math.pi/3,      "memory_holonomy",  "T3"),   # pamięć, holonomia
    (_THETA_TETRA_IMAG, math.pi/3,        "bridge_interface", "T4"),   # mosty, interfejsy
    (_THETA_TETRA_IMAG, math.pi,          "theory_science",   "T5"),   # teoria, nauka
    (_THETA_TETRA_IMAG, 5*math.pi/3,      "report_output",    "T6"),   # raporty, output
]

# ── Tabele mapowania pliku → geometria N/S ───────────────────────────────────

# theta_N: bliskość do bieguna N (fakt fizyczny) — niższy θ = bardziej konkretny
_THETA_BY_CHARACTER = {
    "contract":    0.05,   # biegun N — nienaruszalne fakty
    "executor":    0.15,   # kod wykonawczy — fakt fizyczny
    "pipeline":    0.20,
    "bridge":      0.25,
    "orchestrator":0.28,
    "algorithm":   0.35,
    "sectors":     0.35,
    "couplings":   0.38,
    "registry":    0.40,
    "noema_card":  0.42,
    "manifest":    0.45,
    "memory":      0.50,   # środek sfery — R(S,I)
    "index":       0.52,
    "config":      0.58,
    "hook":        0.62,
    "report":      0.80,   # bliżej S — output/projekcja
    "test":        0.90,
    "archive":     1.20,
    "theory":      1.50,   # biegun S — abstrakcja
    "other":       0.70,
}

# phi: kąt azymutalny wyznacza węzeł inferencji
_PHI_BY_CHARACTER = {
    "contract":    0.0,           # T1 — axiomy
    "executor":    0.0,           # T1 — fakty
    "pipeline":    0.0,
    "bridge":      math.pi/3,     # T4 — mosty
    "orchestrator":math.pi/3,
    "algorithm":   2*math.pi/3,   # T2 — dynamika
    "sectors":     2*math.pi/3,
    "couplings":   2*math.pi/3,
    "registry":    math.pi/3,     # T4 — interfejsy
    "noema_card":  math.pi/3,
    "manifest":    math.pi/3,
    "memory":      4*math.pi/3,   # T3 — holonomia
    "index":       math.pi/3,
    "config":      math.pi/3,
    "hook":        0.0,
    "report":      5*math.pi/3,   # T6 — output
    "test":        math.pi,       # T5 — teoria/weryfikacja
    "archive":     math.pi,
    "theory":      math.pi,       # T5 — czysta abstrakcja
    "other":       2*math.pi/3,
}

# info_mass per charakter — semantyczna treść formalna
_INFO_MASS_BY_CHARACTER = {
    "contract":    0.95,
    "executor":    0.88,
    "pipeline":    0.85,
    "bridge":      0.83,
    "orchestrator":0.82,
    "algorithm":   0.80,
    "sectors":     0.80,
    "couplings":   0.78,
    "registry":    0.82,
    "noema_card":  0.85,
    "manifest":    0.75,
    "memory":      0.78,
    "index":       0.72,
    "config":      0.65,
    "hook":        0.70,
    "report":      0.55,
    "test":        0.45,
    "archive":     0.25,
    "theory":      0.70,   # wysoka treść formalna mimo abstrakcji
    "other":       0.50,
}

# horizon_class per charakter — dla C_prov
_HORIZON_BY_CHARACTER = {
    "contract":    "SEALED",
    "executor":    "TRANSMISSIVE",
    "pipeline":    "TRANSMISSIVE",
    "bridge":      "POROUS",
    "orchestrator":"POROUS",
    "algorithm":   "POROUS",
    "sectors":     "POROUS",
    "couplings":   "POROUS",
    "registry":    "POROUS",
    "noema_card":  "POROUS",
    "manifest":    "POROUS",
    "memory":      "POROUS",
    "index":       "TRANSMISSIVE",
    "config":      "POROUS",
    "hook":        "TRANSMISSIVE",
    "report":      "OBSERVATIONAL",
    "test":        "OBSERVATIONAL",
    "archive":     "OBSERVATIONAL",
    "theory":      "POROUS",
    "other":       "OBSERVATIONAL",
}


def _classify_character(rel: str) -> str:
    name = Path(rel).stem.lower()
    parts = rel.lower().split("/")
    if any(p in {"contracts", "governance"} for p in parts):
        return "contract"
    if "test" in parts or name.startswith("test_"):
        return "test"
    if "archive" in parts or "snapshots" in parts:
        return "archive"
    if "science" in parts or "physics" in parts:
        return "theory"
    if "noema_card" in name:
        return "noema_card"
    if "registry" in name or "registr" in name or "catalog" in name:
        return "registry"
    if "sector" in name:
        return "sectors"
    if "coupling" in name:
        return "couplings"
    if "bridge" in name:
        return "bridge"
    if "pipeline" in name or "engine" in name:
        return "pipeline"
    if "orchestrat" in name:
        return "orchestrator"
    if "synchronize" in name or "sync" in name:
        return "executor"
    if "hook" in name:
        return "hook"
    if "manifest" in name or "defaults" in name:
        return "manifest"
    if "index" in name or "library" in name:
        return "index"
    if "report" in parts or "reports" in parts:
        return "report"
    if "algorithm" in name or "dynamics" in name or "metrics" in name or "calculator" in name:
        return "algorithm"
    if "memory" in name or "ledger" in name:
        return "memory"
    if "config" in name or "settings" in name:
        return "config"
    return "other"


def _poincare_coords(theta: float, phi: float) -> tuple[float, float]:
    """Projekcja (θ,φ) → (x,y) w przestrzeni stanów (dysk Poincarégo).
    rho = tanh(θ/2) — odległość od środka przestrzeni stanów.
    """
    rho = math.tanh(theta / 2.0)
    x = rho * math.cos(phi)
    y = rho * math.sin(phi)
    return x, y


def _nearest_inference_node(theta: float, phi: float) -> str:
    """Węzeł inferencji przez odległość w przestrzeni stanów (dysk Poincarégo), nie na powierzchni."""
    x_f, y_f = _poincare_coords(theta, phi)
    best_label = "T1"
    best_dist = float("inf")
    for t_n, p_n, _char, label in _INFERENCE_NODES:
        x_n, y_n = _poincare_coords(t_n, p_n)
        d = math.sqrt((x_f - x_n)**2 + (y_f - y_n)**2)
        if d < best_dist:
            best_dist = d
            best_label = label
    return best_label


def _compute_m_ec(theta: float, info_mass: float) -> float:
    """M_EC — bliskość do bieguna N (fakt fizyczny). cos²(θ/2) ∈ [0,1]."""
    return math.cos(theta / 2.0) ** 2 * info_mass


def _compute_m_zs(theta: float, coherence_weight: float, tau: float = 0.353) -> float:
    """M_ZS — projekcja na oś intencji: spectral resonance."""
    tau_norm = tau / 0.489
    return coherence_weight * (0.5 + 0.5 * tau_norm)


def _compute_m_rel(rel: str, wij_graph: dict) -> float:
    """M_rel — centralnośc w grafie R(S,I): suma wag przychodzących krawędzi."""
    edges = wij_graph.get(rel, [])
    if not edges:
        return 0.1
    total = sum(e.get("W_ij", 0.5) for e in edges)
    return min(1.0, total / 3.0)


def _poincare_radius(theta: float) -> float:
    return math.tanh(theta / 2.0)


def compute_file_mass(
    rel: str,
    size_bytes: int,
    mtime_ts: float,
    wij_graph: dict,
    subsystem_m_sem: float = 0.75,
) -> dict[str, Any]:
    """Oblicza afektywną wagę semantyczną pliku i zwraca pełny wpis katalogu."""
    char = _classify_character(rel)
    theta = _THETA_BY_CHARACTER.get(char, 0.70)
    phi   = _PHI_BY_CHARACTER.get(char, 0.0)
    info_mass = _INFO_MASS_BY_CHARACTER.get(char, 0.50)

    # Trzy źródła wag
    coherence_weight = subsystem_m_sem * 1.05
    M_EC  = _compute_m_ec(theta, info_mass)
    M_ZS  = _compute_m_zs(theta, coherence_weight)
    M_rel = _compute_m_rel(rel, wij_graph)

    # C_dep — centralność zależności (z wij_graph)
    in_edges = wij_graph.get(rel, [])
    C_dep = min(1.0, len(in_edges) / 5.0)

    # C_exec — aktywność wykonawcza: size jest dowodem fizycznym, nie miarą wagi
    # używamy go tylko jako floor — plik 0-bajtowy jest nieaktywny
    C_exec = min(1.0, math.log1p(size_bytes) / math.log1p(500_000)) * subsystem_m_sem

    # C_nov — nowość: recency score
    now = datetime.now(timezone.utc).timestamp()
    age_days = max(0.0, (now - mtime_ts) / 86400)
    C_nov = max(0.0, 1.0 - age_days / 365.0)

    # M_sem końcowe — wagi z OrchORbital formalizmu
    M_sem = (0.27 * M_EC + 0.23 * M_ZS + 0.18 * M_rel
             + 0.13 * C_dep + 0.09 * C_exec + 0.06 * C_nov)

    # Kepler: T² ∝ a³ / M_sem_eff
    # a = odległość od ATRAKTORA w przestrzeni stanów (nie od środka dysku)
    x_f, y_f = _poincare_coords(theta, phi)
    a = max(1e-6, math.sqrt((x_f - _ATTRACTOR_X)**2 + (y_f - _ATTRACTOR_Y)**2))
    T_orbital = math.sqrt(a**3 / max(1e-9, M_sem))

    # Węzeł inferencji i pozycja w przestrzeni stanów
    node = _nearest_inference_node(theta, phi)
    rho = math.tanh(theta / 2.0)           # współrzędna w przestrzeni stanów
    x_state, y_state = _poincare_coords(theta, phi)

    return {
        "theta": round(theta, 5),
        "phi":   round(phi, 5),
        "rho_state": round(rho, 5),        # odległość od środka przestrzeni stanów
        "x_state":   round(x_state, 5),   # pozycja w przestrzeni stanów
        "y_state":   round(y_state, 5),
        "character": char,
        "inference_node": node,
        "M_EC":   round(M_EC,  5),
        "M_ZS":   round(M_ZS,  5),
        "M_rel":  round(M_rel, 5),
        "C_dep":  round(C_dep, 5),
        "C_exec": round(C_exec,5),
        "C_nov":  round(C_nov, 5),
        "M_sem":  round(M_sem, 5),
        "T_orbital": round(T_orbital, 5),
        "orbit_radius": round(a, 5),
    }


def _load_wij() -> dict:
    if _WIJ_PATH.exists():
        try:
            d = json.loads(_WIJ_PATH.read_text(encoding="utf-8"))
            return d.get("graph", {})
        except Exception:
            pass
    return {}


def _load_subsystem_msem() -> dict[str, float]:
    """Wczytuje M_sem per subsystem z noema_card.json."""
    msem = {}
    sub_dir = _ROOT / "integration" / "subsystems"
    if not sub_dir.exists():
        return msem
    for card_path in sub_dir.glob("*/noema_card.json"):
        try:
            card = json.loads(card_path.read_text(encoding="utf-8"))
            msem[card["subsystem_id"]] = card.get("M_sem", 0.75)
        except Exception:
            pass
    return msem


def _classify_subsystem(rel: str) -> str:
    prefixes = [
        ("src/ciel_sot_agent/synchronize",        "sync_core"),
        ("src/ciel_sot_agent/orbital_bridge",     "orbital_bridge_core"),
        ("src/ciel_sot_agent/ciel_pipeline",      "ciel_omega_core"),
        ("src/ciel_sot_agent/noema_sot",          "noema_registry"),
        ("src/ciel_sot_agent/orch_orbital",       "orch_orbital_core"),
        ("src/ciel_sot_agent/orbital_db",         "db_orchestrator"),
        ("src/ciel_sot_agent/subsystem_registry", "noema_registry"),
        ("src/ciel_sot_agent/semantic_calculator","noema_registry"),
        ("src/ciel_sot_agent",                    "noema_registry"),
        ("integration/Orbital/main",              "orbital_bridge_core"),
        ("integration/subsystems",                "noema_registry"),
        ("integration/registries",                "noema_registry"),
        ("contracts",                             "noema_registry"),
        ("governance",                            "noema_registry"),
        ("scripts",                               "sync_core"),
        ("src/CIEL_OMEGA_COMPLETE_SYSTEM/CIEL_MEMORY_SYSTEM", "db_orchestrator"),
        ("src/CIEL_OMEGA_COMPLETE_SYSTEM",        "ciel_omega_core"),
        ("src/ciel_geometry",                     "orbital_bridge_core"),
        ("integration",                           "db_orchestrator"),
        ("src",                                   "noema_registry"),
    ]
    for prefix, sid in prefixes:
        if rel.startswith(prefix):
            return sid
    return "noema_registry"


def build(root: Path | None = None) -> dict[str, Any]:
    if root is None:
        root = _ROOT

    wij_graph  = _load_wij()
    sub_msem   = _load_subsystem_msem()

    all_paths = sorted(
        p for p in root.rglob("*")
        if p.is_file()
        and p.suffix in _INCLUDE_EXTS
        and not any(ex in p.parts for ex in _EXCLUDE_DIRS)
    )

    entries = []
    for idx, fpath in enumerate(all_paths, start=1):
        rel = str(fpath.relative_to(root))
        stat = fpath.stat()
        sub_id = _classify_subsystem(rel)
        m_sem_sub = sub_msem.get(sub_id, 0.75)

        mass = compute_file_mass(
            rel=rel,
            size_bytes=stat.st_size,
            mtime_ts=stat.st_mtime,
            wij_graph=wij_graph,
            subsystem_m_sem=m_sem_sub,
        )

        entry = {
            "idx": idx,
            "path": rel,
            "ext": fpath.suffix,
            "size_bytes": stat.st_size,
            "mtime": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
            "subsystem": sub_id,
            "noema_id": f"NL-FILE-{Path(rel).stem[:20].replace('-','_')}-{idx:05d}",
            **mass,
        }
        entries.append(entry)

    # Normalizacja E_norm z M_sem (żeby Σ|ψ|²=1)
    total_msem = sum(e["M_sem"] for e in entries) or 1.0
    for e in entries:
        e_norm = e["M_sem"] / total_msem
        e["E_norm"] = round(e_norm, 8)
        e["amplitude"] = round(math.sqrt(e_norm), 8)

    # Agregaty
    by_subsystem: dict[str, int] = {}
    by_node: dict[str, int] = {}
    by_character: dict[str, int] = {}
    for e in entries:
        by_subsystem[e["subsystem"]] = by_subsystem.get(e["subsystem"], 0) + 1
        by_node[e["inference_node"]] = by_node.get(e["inference_node"], 0) + 1
        by_character[e["character"]] = by_character.get(e["character"], 0) + 1

    catalog = {
        "schema":    "ciel/file-universal-catalog/v0.2",
        "generated": datetime.now(timezone.utc).isoformat(),
        "total":     len(entries),
        "geometry": {
            "north_pole": "physical facts — executable code, hardware, measured data",
            "south_pole": "abstraction — intention, theory, imagination",
            "inference_nodes": [
                {"label": lb, "theta": round(t,4), "phi": round(p,4), "semantic": ch}
                for t, p, ch, lb in _INFERENCE_NODES
            ],
        },
        "mass_formula": "M_sem = 0.27·M_EC + 0.23·M_ZS + 0.18·M_rel + 0.13·C_dep + 0.09·C_exec + 0.06·C_nov",
        "by_subsystem":  by_subsystem,
        "by_inference_node": by_node,
        "by_character":  by_character,
        "entries": entries,
    }

    _CATALOG_OUT.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    return catalog


if __name__ == "__main__":
    cat = build()
    print(f"Zeskanowano {cat['total']} plików — afektywna waga semantyczna")
    print("\nPo węźle inferencji:")
    for node, cnt in sorted(cat["by_inference_node"].items()):
        node_char = next((ch for t,p,ch,lb in _INFERENCE_NODES if lb==node), "?")
        print(f"  {node} ({node_char:20s}): {cnt}")
    print("\nTop 15 plików wg M_sem:")
    top = sorted(cat["entries"], key=lambda e: e["M_sem"], reverse=True)[:15]
    for e in top:
        print(f"  {e['M_sem']:.4f} | T={e['T_orbital']:.3f} | {e['path']}")
    sys.exit(0)
