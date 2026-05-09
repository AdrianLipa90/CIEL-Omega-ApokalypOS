"""Build W_{ij} dependency graph for CIEL1 Python files.

Output:
  integration/registries/file_catalog.json   — per-file metadata + W_ij
  integration/registries/file_wij_graph.json — edge list
  nonlocal_graph.db                          — edges registered in nonlocal graph

Run from CIEL1 repo root:
  python3 scripts/build_file_wij.py
"""
from __future__ import annotations

import ast
import csv
import json
import math
import sqlite3
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"

PACKAGES = [
    SRC / "ciel_sot_agent",
    SRC / "ciel_geometry",
    SRC / "CIEL_OMEGA_COMPLETE_SYSTEM" / "ciel_omega",
    REPO_ROOT / "integration" / "Orbital" / "main",
]

CALL_GRAPH_CSV = (
    REPO_ROOT / "integration" / "imports" / "relational_mechanism"
    / "registries" / "critical_call_graph_v1.csv"
)

OUT_CATALOG = REPO_ROOT / "integration" / "registries" / "file_catalog.json"
OUT_GRAPH   = REPO_ROOT / "integration" / "registries" / "file_wij_graph.json"
DB_PATH = (
    SRC / "CIEL_OMEGA_COMPLETE_SYSTEM" / "CIEL_MEMORY_SYSTEM"
    / "TSM" / "ledger" / "nonlocal_graph.db"
)


def _file_id(path: Path) -> str:
    try:
        rel = path.relative_to(SRC)
    except ValueError:
        try:
            rel = path.relative_to(REPO_ROOT)
        except ValueError:
            rel = path
    return "file:" + str(rel.with_suffix("")).replace("/", ".")


def _collect_files() -> list[Path]:
    files = []
    for pkg in PACKAGES:
        if pkg.exists():
            files.extend(
                p for p in pkg.rglob("*.py")
                if "__pycache__" not in str(p) and p.name != "__init__.py"
            )
    return sorted(set(files))


def _extract_imports(path: Path) -> list[tuple[str, float]]:
    """Return list of (module_name, weight) from AST import analysis."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return []
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append((alias.name, 1.0))
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            imports.append((mod, 0.7))
    return imports


def _module_to_file(module: str, file_index: dict[str, Path]) -> str | None:
    """Resolve module name to file_id if it's an internal module."""
    parts = module.split(".")
    for n in range(len(parts), 0, -1):
        candidate = ".".join(parts[:n])
        if candidate in file_index:
            return file_index[candidate]
    return None


def _build_module_index(files: list[Path]) -> dict[str, str]:
    """Map importable module name → file_id."""
    index: dict[str, str] = {}
    for f in files:
        fid = _file_id(f)
        # try relative to SRC
        for base in [SRC] + PACKAGES:
            try:
                rel = f.relative_to(base)
                mod = str(rel.with_suffix("")).replace("/", ".").replace("\\", ".")
                index[mod] = fid
                # also register short name (last component)
                index[mod.split(".")[-1]] = fid
                break
            except ValueError:
                continue
    return index


def _load_call_graph_centrality() -> dict[str, float]:
    """Load critical_call_graph CSV and compute per-file call count as centrality."""
    centrality: dict[str, float] = defaultdict(float)
    if not CALL_GRAPH_CSV.exists():
        return centrality
    with CALL_GRAPH_CSV.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            src = row.get("source_path", "").strip()
            tgt = row.get("target_path", "").strip()
            if src:
                centrality[src] += 1.0
            if tgt:
                centrality[tgt] += 1.0
    # normalise to [0, 0.3]
    mx = max(centrality.values(), default=1.0)
    return {k: round(v / mx * 0.3, 4) for k, v in centrality.items()}


def _horizon_class(in_degree: int) -> str:
    if in_degree == 0:
        return "SEALED"
    if in_degree <= 3:
        return "TRANSMISSIVE"
    return "POROUS"


def _euler_phase_metrics(
    fid: str,
    edges_out: dict[str, float],
    phi_map: dict[str, float],
) -> tuple[float, int, float]:
    """Compute phi_i, spin_i, closure_defect_i for node i."""
    in_deg = sum(
        1 for (s, d) in edges_out.items() for _ in [None]  # placeholder
    )
    # phi_i = weighted sum of neighbour phases mod 2π
    w_sum = sum(edges_out.values()) or 1.0
    phi_i = sum(w * phi_map.get(d, 0.0) for d, w in edges_out.items()) / w_sum
    phi_i = phi_i % (2 * math.pi)

    out_deg = len(edges_out)
    spin_i = 1 if out_deg % 2 == 0 else -1

    # closure defect: |Σ W_ij * e^{i*phi_j}| - 1
    re_sum = sum(w * math.cos(phi_map.get(d, 0.0)) for d, w in edges_out.items())
    im_sum = sum(w * math.sin(phi_map.get(d, 0.0)) for d, w in edges_out.items())
    magnitude = math.sqrt(re_sum**2 + im_sum**2)
    closure = round(abs(magnitude - w_sum) / (w_sum + 1e-9), 5)

    return round(phi_i, 5), spin_i, closure


def _register_in_db(edges: list[tuple[str, str, float]]) -> None:
    if not DB_PATH.exists():
        return
    try:
        con = sqlite3.connect(DB_PATH, timeout=10, isolation_level=None)
        con.execute("PRAGMA journal_mode=WAL")
        con.execute(
            "CREATE TABLE IF NOT EXISTS nonlocal_edges "
            "(src TEXT NOT NULL, dst TEXT NOT NULL, weight REAL NOT NULL, "
            "updated_at TEXT NOT NULL, PRIMARY KEY (src, dst))"
        )
        now = datetime.now(timezone.utc).isoformat()
        con.executemany(
            "INSERT OR REPLACE INTO nonlocal_edges(src,dst,weight,updated_at) VALUES(?,?,?,?)",
            [(s, d, w, now) for s, d, w in edges],
        )
        con.close()
        print(f"  DB: {len(edges)} krawędzi zarejestrowanych w nonlocal_graph.db")
    except Exception as e:
        print(f"  DB: pominięto ({e})")


def main() -> None:
    print("=== build_file_wij.py ===")
    files = _collect_files()
    print(f"Pliki: {len(files)}")

    module_index = _build_module_index(files)
    centrality = _load_call_graph_centrality()

    # Build adjacency: fid → {neighbor_fid: weight}
    adj: dict[str, dict[str, float]] = defaultdict(dict)
    for f in files:
        fid = _file_id(f)
        imports = _extract_imports(f)
        for mod, base_w in imports:
            target_fid = _module_to_file(mod, module_index)
            if target_fid and target_fid != fid:
                # wzmocnienie z call graph
                path_key = str(f.relative_to(REPO_ROOT))
                boost = centrality.get(path_key, 0.0)
                w = round(min(1.0, base_w + boost), 4)
                # keep max weight if duplicate
                adj[fid][target_fid] = max(adj[fid].get(target_fid, 0.0), w)

    # in-degree
    in_deg: dict[str, int] = defaultdict(int)
    for fid, neighbors in adj.items():
        for nid in neighbors:
            in_deg[nid] += 1

    # seed phi from in_degree (heuristic: more central = larger phase angle)
    all_fids = {_file_id(f) for f in files}
    max_in = max(in_deg.values(), default=1)
    phi_map: dict[str, float] = {
        fid: (in_deg.get(fid, 0) / max_in) * math.pi
        for fid in all_fids
    }

    # build catalog
    catalog_files = []
    db_edges: list[tuple[str, str, float]] = []

    for f in files:
        fid = _file_id(f)
        neighbors = adj.get(fid, {})
        phi_i, spin_i, closure_i = _euler_phase_metrics(fid, neighbors, phi_map)
        ind = in_deg.get(fid, 0)
        try:
            rel_path = str(f.relative_to(REPO_ROOT))
        except ValueError:
            rel_path = str(f)

        # package label
        for pkg in PACKAGES:
            try:
                f.relative_to(pkg)
                pkg_label = pkg.name
                break
            except ValueError:
                continue
        else:
            pkg_label = "unknown"

        entry = {
            "id": fid,
            "path": rel_path,
            "package": pkg_label,
            "phi": phi_i,
            "spin": spin_i,
            "closure_defect": closure_i,
            "in_degree": ind,
            "out_degree": len(neighbors),
            "horizon_class": _horizon_class(ind),
            "W_ij": neighbors,
        }
        catalog_files.append(entry)

        for nid, w in neighbors.items():
            db_edges.append((fid, nid, w))

    catalog_files.sort(key=lambda x: x["in_degree"], reverse=True)

    OUT_CATALOG.parent.mkdir(parents=True, exist_ok=True)
    OUT_CATALOG.write_text(
        json.dumps({"generated_at": datetime.now(timezone.utc).isoformat(),
                    "nodes": len(catalog_files), "files": catalog_files}, indent=2),
        encoding="utf-8",
    )
    print(f"Katalog: {OUT_CATALOG} ({len(catalog_files)} węzłów)")

    edge_list = [
        {"src": s, "dst": d, "weight": w}
        for s, neighbors in adj.items()
        for d, w in neighbors.items()
    ]
    OUT_GRAPH.write_text(
        json.dumps({"generated_at": datetime.now(timezone.utc).isoformat(),
                    "edges": edge_list}, indent=2),
        encoding="utf-8",
    )
    print(f"Graf:    {OUT_GRAPH} ({len(edge_list)} krawędzi)")

    _register_in_db(db_edges)

    print("\n=== TOP 10 (in_degree) ===")
    for entry in catalog_files[:10]:
        print(
            f"  {entry['in_degree']:>3} in | {entry['out_degree']:>3} out | "
            f"closure={entry['closure_defect']:.4f} | {entry['horizon_class']:<12} | {entry['id']}"
        )


if __name__ == "__main__":
    main()
