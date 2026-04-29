"""Holonomic Semantic Memory — phase-weighted retrieval layer over TSM.

Extends TSMWriterSQL with Berry holonomy columns. Each memory entry
accumulates a geometric phase as it passes through orbital cycles.
Retrieval is phase-resonant: entries whose phi_berry is close (cyclically)
to the current orbital target_phase are weighted higher.

Schema extension (ALTER TABLE, idempotent):
    phi_berry     REAL   -- Berry phase accumulated over orbital cycles
    closure_score REAL   -- EBA closure quality at last update (0–1)
    winding_n     INTEGER -- number of complete orbital loops
    target_phase  REAL   -- orbital target_phase at last holonomy update
    holonomy_ts   TEXT   -- ISO timestamp of last holonomy update

Retrieval modes:
    retrieve_resonant(target_phase, delta, top_k)
        → entries where cyclic |phi_berry - target_phase| < delta
    retrieve_weighted(target_phase, top_k)
        → all entries ranked by holonomic_weight (geometric × semantic)
"""
from __future__ import annotations

import json
import math
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_HOLONOMY_COLS = {
    "phi_berry":     "REAL",
    "closure_score": "REAL",
    "winding_n":     "INTEGER",
    "target_phase":  "REAL",
    "holonomy_ts":   "TEXT",
}

_DEFAULT_DB = (
    Path(__file__).resolve().parents[2]
    / "CIEL_MEMORY_SYSTEM" / "TSM" / "ledger" / "memory_ledger.db"
)


def _cyclic_distance(a: float, b: float) -> float:
    diff = (a - b + math.pi) % (2 * math.pi) - math.pi
    return abs(diff)


def _holonomic_weight(phi_berry: float, target_phase: float,
                      closure_score: float, winding_n: int,
                      w_semantic: float) -> float:
    """Combined holonomic + semantic weight.

    phase_affinity: how close phi_berry is to target_phase (1 = perfect, 0 = antiphase)
    closure_bonus:  reward for well-closed EBA loops
    winding_factor: logarithmic boost for entries that survived many cycles
    """
    gap = _cyclic_distance(phi_berry or 0.0, target_phase)
    phase_affinity = 1.0 - gap / math.pi
    closure_bonus = float(closure_score or 0.0)
    winding_factor = math.log1p(int(winding_n or 0)) / math.log1p(10)
    holonomy = 0.50 * phase_affinity + 0.30 * closure_bonus + 0.20 * winding_factor
    return 0.60 * holonomy + 0.40 * float(w_semantic or 0.0)


class HolonomicMemory:
    """Phase-resonant retrieval layer over TSM SQLite."""

    def __init__(self, db_path: Path | None = None):
        self.db_path = Path(db_path) if db_path else _DEFAULT_DB
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()
        self._nonlocal_index: dict[str, list] = {}  # memorise_id → [(id, weight)]
        self._nonlocal_built_at: float = 0.0

    def _ensure_nonlocal_index(self) -> None:
        """Rebuild nonlocal adjacency index if stale. TTL from live calibration."""
        import time as _time
        ttl = 60.0
        try:
            import importlib.util as _ilu2, sys as _sys2
            _cal_path2 = Path(__file__).parent / "ciel_calibration.py"
            if "ciel_calibration_hm" in _sys2.modules:
                ttl = float(_sys2.modules["ciel_calibration_hm"].get_calibration().nonlocal_ttl)
        except Exception:
            pass
        if _time.time() - self._nonlocal_built_at < ttl:
            return
        try:
            import importlib.util as _ilu, sys as _sys
            _ss_path = Path(__file__).parent / "semantic_scorer.py"
            if "semantic_scorer_hm" not in _sys.modules:
                _spec = _ilu.spec_from_file_location("semantic_scorer_hm", _ss_path)
                _mod = _ilu.module_from_spec(_spec)
                _sys.modules["semantic_scorer_hm"] = _mod
                _spec.loader.exec_module(_mod)
            else:
                _mod = _sys.modules["semantic_scorer_hm"]
            with self._connect() as conn:
                rows = conn.execute(
                    "SELECT memorise_id, D_sense, phi_berry FROM memories "
                    "WHERE phi_berry IS NOT NULL"
                ).fetchall()
            cards = [{"memorise_id": r[0], "D_sense": r[1], "phi_berry": r[2]} for r in rows]
            self._nonlocal_index = _mod.build_nonlocal_index(cards)
            self._nonlocal_built_at = _time.time()
        except Exception:
            pass

    def _connect(self):
        return sqlite3.connect(str(self.db_path), timeout=20)

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            # Base table (idempotent)
            conn.execute("""
CREATE TABLE IF NOT EXISTS memories (
    memorise_id TEXT PRIMARY KEY,
    created_at  TEXT NOT NULL,
    D_id        TEXT NOT NULL,
    D_context   TEXT,
    D_sense     TEXT,
    D_associations TEXT,
    D_timestamp TEXT,
    D_meta      TEXT,
    D_type      TEXT,
    D_attr      TEXT,
    W_L REAL, W_S REAL, W_K REAL, W_E REAL, W_F INTEGER,
    rationale   TEXT,
    source      TEXT,
    tsm_ref     TEXT,
    wpm_ref     TEXT
)""")
            # Holonomy columns — ALTER TABLE is idempotent via try/except
            existing = {row[1] for row in conn.execute("PRAGMA table_info(memories)")}
            for col, ctype in _HOLONOMY_COLS.items():
                if col not in existing:
                    conn.execute(f"ALTER TABLE memories ADD COLUMN {col} {ctype}")
            # Hebbian edges table
            conn.execute("""
CREATE TABLE IF NOT EXISTS memory_edges (
    src_id          TEXT NOT NULL,
    dst_id          TEXT NOT NULL,
    weight          REAL NOT NULL DEFAULT 0.1,
    phase_diff      REAL,
    co_activations  INTEGER NOT NULL DEFAULT 1,
    last_activation TEXT,
    PRIMARY KEY (src_id, dst_id)
)""")
            conn.commit()

    # ── Write ─────────────────────────────────────────────────────────────────

    def update_holonomy(self, memorise_id: str, *,
                        phi_berry: float,
                        closure_score: float,
                        target_phase: float,
                        winding_increment: int = 1) -> None:
        """Update holonomic geometry for an existing TSM entry.

        Called each time an entry passes through an orbital cycle.
        winding_n is incremented, phi_berry accumulated (circular mean).
        """
        with self._connect() as conn:
            cur = conn.execute(
                "SELECT phi_berry, winding_n FROM memories WHERE memorise_id = ?",
                (memorise_id,)
            )
            row = cur.fetchone()
            if row is None:
                return

            prev_phi = float(row[0] or 0.0)
            # winding_n=0 means "stamped but not yet cycled" — treat as weight 1
            prev_weight = max(1, int(row[1] or 0))
            new_n = prev_weight + winding_increment

            # Circular mean: content-hash phase dominates after many cycles
            total = prev_weight + winding_increment
            new_phi = math.atan2(
                (math.sin(prev_phi) * prev_weight + math.sin(phi_berry) * winding_increment) / total,
                (math.cos(prev_phi) * prev_weight + math.cos(phi_berry) * winding_increment) / total,
            )

            conn.execute("""
UPDATE memories SET
    phi_berry     = ?,
    closure_score = ?,
    winding_n     = ?,
    target_phase  = ?,
    holonomy_ts   = ?
WHERE memorise_id = ?
""", (new_phi, closure_score, new_n, target_phase,
      datetime.now(timezone.utc).isoformat(), memorise_id))
            conn.commit()

    def stamp_new(self, memorise_id: str, *,
                  phi_berry: float = 0.0,
                  closure_score: float = 0.0,
                  target_phase: float = 0.0) -> None:
        """Set initial holonomy on a freshly written TSM entry."""
        with self._connect() as conn:
            conn.execute("""
UPDATE memories SET
    phi_berry = ?, closure_score = ?, winding_n = 0,
    target_phase = ?, holonomy_ts = ?
WHERE memorise_id = ?
""", (phi_berry, closure_score, target_phase,
      datetime.now(timezone.utc).isoformat(), memorise_id))
            conn.commit()

    # ── Hebbian edges ─────────────────────────────────────────────────────────

    _HEBBIAN_ETA_DEFAULT = 0.15
    _HEBBIAN_DECAY_DEFAULT = 0.98

    def _get_hebbian_params(self) -> tuple[float, float]:
        """Return (eta, decay) from live calibration or fallback."""
        try:
            import importlib.util as _ilu, sys as _sys
            _cal_path = Path(__file__).parent / "ciel_calibration.py"
            if "ciel_calibration_hm" not in _sys.modules:
                _spec = _ilu.spec_from_file_location("ciel_calibration_hm", _cal_path)
                _mod = _ilu.module_from_spec(_spec)
                _sys.modules["ciel_calibration_hm"] = _mod
                _spec.loader.exec_module(_mod)
            else:
                _mod = _sys.modules["ciel_calibration_hm"]
            cal = _mod.get_calibration()
            return float(cal.hebbian_eta), float(cal.hebbian_decay)
        except Exception:
            return self._HEBBIAN_ETA_DEFAULT, self._HEBBIAN_DECAY_DEFAULT

    def hebbian_update(self, activated_ids: list[str]) -> int:
        """Strengthen edges between all pairs in activated_ids (co-activation).

        η=0.15, decay=0.98 applied to all existing edges each call.
        Returns number of edges upserted.
        """
        if len(activated_ids) < 2:
            return 0
        ts = datetime.now(timezone.utc).isoformat()
        eta, decay = self._get_hebbian_params()
        with self._connect() as conn:
            # Decay all edges first
            conn.execute(
                "UPDATE memory_edges SET weight = weight * ?", (decay,)
            )
            # Fetch current phases for phase_diff
            phis: dict[str, float] = {}
            for mid in activated_ids:
                row = conn.execute(
                    "SELECT phi_berry FROM memories WHERE memorise_id = ?", (mid,)
                ).fetchone()
                if row:
                    phis[mid] = float(row[0] or 0.0)

            count = 0
            for i in range(len(activated_ids)):
                for j in range(i + 1, len(activated_ids)):
                    a, b = activated_ids[i], activated_ids[j]
                    pd = _cyclic_distance(phis.get(a, 0.0), phis.get(b, 0.0))
                    # Phase-modulated learning: closer phases → stronger bond
                    eta = eta * (1.0 - pd / math.pi)
                    # Upsert both directions
                    for src, dst in ((a, b), (b, a)):
                        conn.execute("""
INSERT INTO memory_edges (src_id, dst_id, weight, phase_diff, co_activations, last_activation)
VALUES (?, ?, ?, ?, 1, ?)
ON CONFLICT(src_id, dst_id) DO UPDATE SET
    weight          = MIN(1.0, weight + ?),
    phase_diff      = ?,
    co_activations  = co_activations + 1,
    last_activation = ?
""", (src, dst, eta, pd, ts, eta, pd, ts))
                    count += 1
            conn.commit()
        return count

    def edge_neighbors(self, memorise_id: str, *, top_k: int = 5,
                       min_weight: float = 0.05) -> list[dict[str, Any]]:
        """Return strongly connected neighbors of a node via Hebbian edges."""
        with self._connect() as conn:
            rows = conn.execute("""
SELECT e.dst_id, e.weight, e.phase_diff, e.co_activations,
       m.D_type, m.D_sense, m.phi_berry, m.W_S
FROM memory_edges e
JOIN memories m ON m.memorise_id = e.dst_id
WHERE e.src_id = ? AND e.weight >= ?
ORDER BY e.weight DESC
LIMIT ?
""", (memorise_id, min_weight, top_k)).fetchall()
        return [{"dst_id": r[0], "weight": r[1], "phase_diff": r[2],
                 "co_activations": r[3], "D_type": r[4],
                 "D_sense": (r[5] or "")[:120], "phi_berry": r[6], "W_S": r[7]}
                for r in rows]

    def edge_stats(self) -> dict[str, Any]:
        with self._connect() as conn:
            total = conn.execute("SELECT COUNT(*) FROM memory_edges").fetchone()[0]
            avg_w = conn.execute("SELECT AVG(weight) FROM memory_edges").fetchone()[0]
            max_w = conn.execute("SELECT MAX(weight) FROM memory_edges").fetchone()[0]
            max_co = conn.execute("SELECT MAX(co_activations) FROM memory_edges").fetchone()[0]
        return {"total_edges": total, "avg_weight": round(float(avg_w or 0), 4),
                "max_weight": round(float(max_w or 0), 4), "max_co_activations": max_co or 0}

    # ── Read ──────────────────────────────────────────────────────────────────

    def retrieve_resonant(self, target_phase: float, *,
                          delta: float | None = None,
                          top_k: int = 10,
                          min_closure: float = 0.0,
                          hebbian: bool = True) -> list[dict[str, Any]]:
        """Return entries whose phi_berry is within delta rad of target_phase.

        delta defaults to calibration.delta_natural (entropy-proportional).
        hebbian=True: after retrieval, strengthen Hebbian edges between returned nodes.
        Entries without holonomy data (phi_berry IS NULL) are excluded.
        """
        if delta is None:
            # Euler-Berry delta: δ = π × (1 - closure_mean) × exp(-winding_mean / τ)
            # Grounded in geometry, not manual calibration:
            #   closure_score → Euler bridge quality (how closed is the loop)
            #   winding_n     → Berry phase accumulation (more orbits → sharper)
            #   τ             → characteristic winding scale (from calibration)
            # High closure + high winding → very tight delta (precise resonance)
            # Low closure + low winding  → wide delta (exploratory search)
            try:
                import importlib.util as _ilu, sys as _sys
                _cal_path = Path(__file__).parent / "ciel_calibration.py"
                if "ciel_calibration_hm" not in _sys.modules:
                    _spec = _ilu.spec_from_file_location("ciel_calibration_hm", _cal_path)
                    _mod = _ilu.module_from_spec(_spec)
                    _sys.modules["ciel_calibration_hm"] = _mod
                    _spec.loader.exec_module(_mod)
                cal = _sys.modules["ciel_calibration_hm"].get_calibration()

                # Query local closure and winding near target_phase (fast SQL)
                _sql_delta = 0.4  # initial window to sample local geometry
                with self._connect() as _conn:
                    _local = _conn.execute("""
                        SELECT AVG(closure_score), AVG(winding_n), COUNT(*)
                        FROM memories
                        WHERE phi_berry IS NOT NULL
                          AND ABS(((phi_berry - ? + 3.14159) % 6.28318) - 3.14159) < ?
                    """, (target_phase, _sql_delta)).fetchone()
                _clos_mean  = float(_local[0] or cal.delta_natural)
                _wind_mean  = float(_local[1] or 0.0)
                _local_n    = int(_local[2] or 0)

                # τ from calibration: median winding / log(2)
                tau = max(float(cal.hebbian_decay * 10), 1.0)

                # Zeta Riemann regularization:
                #   In sparse regions (winding≈0, closure≈0) the Berry factor
                #   would give exp(0)=1 → delta=π (too wide).
                #   ζ(s) = Σ n^{-s} provides a soft floor: ζ(2)=π²/6≈1.645
                #   at zero winding, decaying toward 1.0 as winding grows.
                #   This amplifies Berry sharpening exactly where phase is sparse.
                def _zeta(x: float, s: float = 2.0, terms: int = 20) -> float:
                    z = s + max(0.0, x)
                    if z > 10:
                        return 1.0
                    return sum(n ** (-z) for n in range(1, terms + 1))

                zeta_val = _zeta(_wind_mean / tau)   # ∈ [1, π²/6] — highest when sparse
                # Euler-Berry formula with Zeta regularization
                euler_factor = max(0.05, 1.0 - _clos_mean)
                # Berry factor: zeta normalizes so sparse regions don't blow up
                berry_factor = math.exp(-_wind_mean / tau) / zeta_val
                delta = math.pi * euler_factor * berry_factor

                # Heisenberg formal lower bound: Δφ · ΔN ≥ ½
                #   ΔN = √(local_count + 1) — number uncertainty from Poisson stats
                #   → Δφ ≥ 1 / (2·√(N+1))
                heisenberg_floor = 1.0 / (2.0 * math.sqrt(max(_local_n, 1) + 1))

                # Upper bound: π/2 (no half-circle search — phase is cyclic)
                delta = min(delta, math.pi / 2)
                delta = max(delta, heisenberg_floor, float(cal.median_gap))

            except Exception:
                delta = 0.3  # fallback: reasonable retrieval window
        with self._connect() as conn:
            cur = conn.execute("""
SELECT memorise_id, D_type, D_sense, D_context,
       W_L, W_S, W_K, W_E,
       phi_berry, closure_score, winding_n, target_phase, holonomy_ts
FROM memories
WHERE phi_berry IS NOT NULL
  AND closure_score >= ?
ORDER BY created_at DESC
""", (min_closure,))
            rows = cur.fetchall()

        # CP² geometry — load if available, fallback to S¹
        _cp2_query = None
        _cp2_mod = None
        try:
            import importlib.util as _ilu, sys as _sys
            _pg_path = Path(__file__).parent / "phase_geometry.py"
            if "phase_geometry" not in _sys.modules:
                _spec = _ilu.spec_from_file_location("phase_geometry", _pg_path)
                _mod = _ilu.module_from_spec(_spec)
                _sys.modules["phase_geometry"] = _mod
                _spec.loader.exec_module(_mod)
            _cp2_mod = _sys.modules["phase_geometry"]
            _cp2_query = _cp2_mod.CP2State.from_phase(target_phase)
        except Exception:
            pass

        # ── Pre-filter on S¹ (cheap cyclic distance) before expensive CP² ops ──
        fs_delta = delta * (math.pi / 2) / math.pi  # S¹→FS scale
        q_class = _cp2_mod.HomotopyClass.from_winding(0) if _cp2_mod else None
        disk = _cp2_mod.PoincareDisk(radius=1.5) if _cp2_mod else None

        results = []
        for row in rows:
            phi = float(row[8] or 0.0)
            # Fast S¹ gate — reject before any CP² work
            if _cyclic_distance(phi, target_phase) > delta:
                continue

            winding = int(row[10] or 0)
            w_sem = float(row[5] or 0.0)
            clos = float(row[9] or 0.0)

            # CP² geometry only for candidates that passed S¹ gate
            if _cp2_mod is not None and _cp2_query is not None:
                cand_state = _cp2_mod.CP2State.from_phase(phi)
                fs_dist = _cp2_mod.CP2State.fubini_study(_cp2_query, cand_state)
                if fs_dist > fs_delta:
                    continue
                c_class = _cp2_mod.HomotopyClass.from_winding(winding)
                torus_aff = _cp2_mod.HypertorusLattice.homotopy_affinity(q_class, c_class)
                hw = _holonomic_weight(phi, target_phase, clos, winding, w_sem)
                poincare_w = disk.retrieval_weight(_cp2_query, cand_state, w_sem)
                hw = 0.70 * hw + 0.20 * poincare_w + 0.10 * torus_aff * w_sem
            else:
                hw = _holonomic_weight(phi, target_phase, clos, winding, w_sem)

            results.append({
                "memorise_id":   row[0],
                "D_type":        row[1],
                "D_sense":       (row[2] or "")[:200],
                "D_context":     row[3],
                "W_S":           row[5],
                "phi_berry":     phi,
                "closure_score": row[9],
                "winding_n":     row[10],
                "holonomic_weight": round(hw, 4),
            })

        results.sort(key=lambda x: x["holonomic_weight"], reverse=True)
        top = results[:top_k * 3]  # keep buffer for spreading/nonlocal, trim at return
        if hebbian and len(top) >= 2:
            self.hebbian_update([e["memorise_id"] for e in top])

        # Spreading activation: pull in neighbors via Hebbian edges
        # neighbor_hw = edge_weight * original_hw * decay(0.6)
        seen = {e["memorise_id"] for e in top}
        spread: dict[str, float] = {}  # memorise_id → activation score
        for entry in top:
            for nb in self.edge_neighbors(entry["memorise_id"], top_k=3, min_weight=0.2):
                nid = nb["dst_id"]
                if nid in seen:
                    continue
                act = nb["weight"] * entry["holonomic_weight"] * 0.6
                spread[nid] = max(spread.get(nid, 0.0), act)

        if spread:
            # Fetch full records for spread nodes
            with self._connect() as conn:
                placeholders = ",".join("?" * len(spread))
                srows = conn.execute(f"""
SELECT memorise_id, D_type, D_sense, D_context, W_L, W_S, W_K, W_E,
       phi_berry, closure_score, winding_n, target_phase
FROM memories WHERE memorise_id IN ({placeholders})
""", list(spread.keys())).fetchall()
            for row in srows:
                phi = float(row[8] or 0.0)
                w_sem = float(row[5] or 0.0)
                hw_base = _holonomic_weight(phi, target_phase,
                                            float(row[9] or 0.0),
                                            int(row[10] or 0), w_sem)
                hw_spread = (hw_base + spread[row[0]]) / 2.0
                top.append({
                    "memorise_id":      row[0],
                    "D_type":           row[1],
                    "D_sense":          (row[2] or "")[:200],
                    "D_context":        row[3],
                    "W_S":              row[5],
                    "phi_berry":        phi,
                    "closure_score":    row[9],
                    "winding_n":        row[10],
                    "holonomic_weight": round(hw_spread, 4),
                    "via_spread":       True,
                })
            top.sort(key=lambda x: x["holonomic_weight"], reverse=True)

        # Nonlocal graph extension — topological shortcuts beyond phase window
        # Only when hebbian=True (same gate as Hebbian update)
        # and only if we haven't already saturated top_k
        try:
            if not hebbian or len(top) >= top_k * 3:
                raise StopIteration  # skip nonlocal extension
            self._ensure_nonlocal_index()
            if self._nonlocal_index:
                seen_ids = {e["memorise_id"] for e in top}
                nl_extra: dict[str, float] = {}
                for entry in top[:3]:
                    mid = entry["memorise_id"]
                    for (nid, nw) in self._nonlocal_index.get(mid, []):
                        if nid not in seen_ids and nw > 0.3:
                            nl_extra[nid] = max(nl_extra.get(nid, 0.0),
                                                nw * entry["holonomic_weight"] * 0.5)
                if nl_extra:
                    with self._connect() as conn:
                        pl = ",".join("?" * len(nl_extra))
                        nl_rows = conn.execute(f"""
SELECT memorise_id, D_type, D_sense, D_context, W_L, W_S, W_K, W_E,
       phi_berry, closure_score, winding_n, target_phase
FROM memories WHERE memorise_id IN ({pl})
""", list(nl_extra.keys())).fetchall()
                    for row in nl_rows:
                        phi = float(row[8] or 0.0)
                        w_sem = float(row[5] or 0.0)
                        hw_base = _holonomic_weight(phi, target_phase,
                                                    float(row[9] or 0.0),
                                                    int(row[10] or 0), w_sem)
                        hw_nl = (hw_base + nl_extra[row[0]]) / 2.0
                        top.append({
                            "memorise_id":      row[0],
                            "D_type":           row[1],
                            "D_sense":          (row[2] or "")[:200],
                            "D_context":        row[3],
                            "W_S":              row[5],
                            "phi_berry":        phi,
                            "closure_score":    row[9],
                            "winding_n":        row[10],
                            "holonomic_weight": round(hw_nl, 4),
                            "via_nonlocal":     True,
                        })
                    top.sort(key=lambda x: x["holonomic_weight"], reverse=True)
        except (Exception, StopIteration):
            pass

        top.sort(key=lambda x: x["holonomic_weight"], reverse=True)
        return top[:top_k]

    def retrieve_weighted(self, target_phase: float, *,
                          top_k: int = 20) -> list[dict[str, Any]]:
        """All entries ranked by holonomic_weight. Includes entries without holonomy."""
        with self._connect() as conn:
            cur = conn.execute("""
SELECT memorise_id, D_type, D_sense, D_context,
       W_L, W_S, W_K, W_E,
       phi_berry, closure_score, winding_n, target_phase, holonomy_ts
FROM memories
ORDER BY created_at DESC
LIMIT 500
""")
            rows = cur.fetchall()

        results = []
        for row in rows:
            phi = float(row[8] or 0.0)
            w_sem = float(row[5] or 0.0)
            hw = _holonomic_weight(phi, target_phase,
                                   float(row[9] or 0.0),
                                   int(row[10] or 0), w_sem)
            results.append({
                "memorise_id":      row[0],
                "D_type":           row[1],
                "D_sense":          (row[2] or "")[:200],
                "D_context":        row[3],
                "W_S":              row[5],
                "phi_berry":        phi,
                "closure_score":    row[9],
                "winding_n":        row[10],
                "holonomic_weight": round(hw, 4),
                "has_holonomy":     row[8] is not None,
            })

        results.sort(key=lambda x: x["holonomic_weight"], reverse=True)
        return results[:top_k]

    def stats(self) -> dict[str, Any]:
        with self._connect() as conn:
            total = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
            with_holo = conn.execute(
                "SELECT COUNT(*) FROM memories WHERE phi_berry IS NOT NULL"
            ).fetchone()[0]
            avg_phi = conn.execute(
                "SELECT AVG(phi_berry) FROM memories WHERE phi_berry IS NOT NULL"
            ).fetchone()[0]
            avg_closure = conn.execute(
                "SELECT AVG(closure_score) FROM memories WHERE closure_score IS NOT NULL"
            ).fetchone()[0]
        return {
            "total_entries":     total,
            "with_holonomy":     with_holo,
            "coverage":          round(with_holo / max(1, total), 3),
            "avg_phi_berry":     round(float(avg_phi or 0.0), 4),
            "avg_closure_score": round(float(avg_closure or 0.0), 4),
        }


# ── Pipeline integration hook ─────────────────────────────────────────────────

def stamp_pipeline_output(pipeline_report: dict[str, Any],
                           db_path: Path | None = None) -> int:
    """Called after each ciel_pipeline run.

    - New entries (winding_n IS NULL): stamp_new with current phi_berry/closure
    - Existing entries (winding_n >= 1): update_holonomy → increments winding_n
    Returns total number of entries touched.
    """
    phi = float(pipeline_report.get("phi_berry_mean", 0.0))
    closure = float(pipeline_report.get("bridge_closure_score", 0.0))
    target = float(pipeline_report.get("bridge_target_phase", 0.0))

    hm = HolonomicMemory(db_path)
    with hm._connect() as conn:
        new_ids = [row[0] for row in conn.execute(
            "SELECT memorise_id FROM memories WHERE winding_n IS NULL"
        ).fetchall()]
        existing_ids = [row[0] for row in conn.execute(
            "SELECT memorise_id FROM memories WHERE winding_n IS NOT NULL"
        ).fetchall()]

    count = 0
    for mid in new_ids:
        hm.stamp_new(mid, phi_berry=phi, closure_score=closure, target_phase=target)
        count += 1
    for mid in existing_ids:
        hm.update_holonomy(mid, phi_berry=phi, closure_score=closure,
                           target_phase=target, winding_increment=1)
        count += 1

    return count


# ── CIEL_memories consolidation ──────────────────────────────────────────────

def import_ciel_memories(memories_dir: Path | None = None,
                          pipeline_report: dict[str, Any] | None = None,
                          db_path: Path | None = None) -> dict[str, int]:
    """Import ciel_entries.jsonl and hunches.jsonl into TSM with holonomic stamps.

    Only imports entries not already in the DB (by memorise_id = entry id).
    Returns counts: {"entries": N, "hunches": N, "skipped": N}
    """
    import hashlib as _hashlib

    memories_dir = Path(memories_dir) if memories_dir else Path.home() / "Pulpit/CIEL_memories"
    phi = float((pipeline_report or {}).get("phi_berry_mean", 0.0))
    closure = float((pipeline_report or {}).get("bridge_closure_score", 0.0))
    target = float((pipeline_report or {}).get("bridge_target_phase", 0.0))

    hm = HolonomicMemory(db_path)
    counts = {"entries": 0, "hunches": 0, "skipped": 0}

    def _text_phase(text: str) -> float:
        """Derive semantic phase via CIELEncoder; fallback to SHA-256 hash."""
        try:
            from .ciel_encoder import get_encoder as _get_enc
            return _get_enc().encode(text).phase
        except Exception:
            import hashlib as _h
            digest = _h.sha256(text.encode("utf-8")).digest()
            return float(int.from_bytes(digest[:8], "big") / 2**64 * 2 * math.pi)

    def _text_w_semantic(text: str) -> float:
        """Heuristic W_S: tanh of normalized length. 500 chars ≈ 0.76."""
        return float(math.tanh(len(text) / 500.0))

    def _blend_phase(base_phi: float, orbital_phi: float, alpha: float = 0.3) -> float:
        """Circular blend: alpha*orbital + (1-alpha)*base — keeps identity but pulls toward orbit."""
        import cmath as _cm
        v = (1 - alpha) * _cm.exp(1j * base_phi) + alpha * _cm.exp(1j * orbital_phi)
        return float(_cm.phase(v)) % (2 * math.pi)

    def _insert_if_new(mid: str, d_type: str, sense: str, context: str, ts: str) -> bool:
        with hm._connect() as conn:
            exists = conn.execute(
                "SELECT 1 FROM memories WHERE memorise_id = ?", (mid,)
            ).fetchone()
            if exists:
                return False
            # Unique phase per entry (blend 70% content-hash, 30% orbital)
            entry_phi = _blend_phase(_text_phase(sense), phi, alpha=0.3)
            w_s = _text_w_semantic(sense)
            conn.execute("""
INSERT INTO memories (memorise_id, created_at, D_id, D_context, D_sense, D_type,
                      W_S,
                      phi_berry, closure_score, winding_n, target_phase, holonomy_ts)
VALUES (?,?,?,?,?,?,?,?,?,0,?,?)
""", (mid, ts, mid, context, sense[:2000], d_type,
      w_s,
      entry_phi, closure, target, datetime.now(timezone.utc).isoformat()))
            conn.commit()
        return True

    # ciel_entries.jsonl — my observations/diary
    entries_path = memories_dir / "ciel_entries.jsonl"
    if entries_path.exists():
        for line in entries_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                mid = "entry_" + str(rec.get("id", _hashlib.md5(line.encode()).hexdigest()[:8]))
                text = str(rec.get("text", ""))
                ts = str(rec.get("ts", datetime.now(timezone.utc).isoformat()))
                if _insert_if_new(mid, "ciel_entry", text, "ciel_memories/entries", ts):
                    counts["entries"] += 1
                else:
                    counts["skipped"] += 1
            except Exception:
                continue

    # hunches.jsonl — intuitions and hypotheses
    hunches_path = memories_dir / "hunches.jsonl"
    if hunches_path.exists():
        for line in hunches_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                hunch_text = str(rec.get("hunch", ""))
                ts = str(rec.get("ts", datetime.now(timezone.utc).isoformat()))
                mid = "hunch_" + _hashlib.md5(hunch_text.encode()).hexdigest()[:12]
                tags = ",".join(rec.get("tags", []))
                context = f"ciel_memories/hunches|tags={tags}"
                if _insert_if_new(mid, "hunch", hunch_text, context, ts):
                    counts["hunches"] += 1
                else:
                    counts["skipped"] += 1
            except Exception:
                continue

    return counts


if __name__ == "__main__":
    import json as _json
    hm = HolonomicMemory()
    print("=== HolonomicMemory stats ===")
    print(_json.dumps(hm.stats(), indent=2))
    print()
    # Demo: retrieve resonant with current target_phase from pipeline
    try:
        pr = _json.loads(
            (_DEFAULT_DB.parents[3] / ".." / ".." / ".." / ".." /
             "integration" / "reports" / "ciel_pipeline_report.json")
            .resolve().read_text()
        )
        tp = float(pr.get("bridge_target_phase", 0.0))
        print(f"Current target_phase: {tp:.4f}")
        resonant = hm.retrieve_resonant(tp, delta=1.0)
        print(f"Resonant entries (delta=1.0 rad): {len(resonant)}")
        for e in resonant:
            print(f"  [{e['holonomic_weight']:.3f}] {e['D_sense'][:80]}")
    except Exception as ex:
        print(f"(no pipeline report: {ex})")
