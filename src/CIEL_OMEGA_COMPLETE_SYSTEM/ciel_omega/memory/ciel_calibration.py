"""CIEL Calibration — emergent parameter inference from TSM.

Philosophy: no hardcoded constants. Every parameter is a measurement of the
living TSM distribution. The system calibrates itself from what it has learned.

    φ is relational, not absolute.
    Weights are eigenvectors, not design choices.
    Delta is entropy, not a radius.
    Sectors are data clusters, not category names.

Public API:
    calibrate(db_path=None, force=False) → CIELCalibration
    get_calibration() → CIELCalibration   (cached, TTL=300s)
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

_CACHE: "CIELCalibration | None" = None
_CACHE_AT: float = 0.0
_CACHE_TTL: float = 300.0  # re-calibrate every 5 minutes


@dataclass
class CIELCalibration:
    """All system parameters derived from TSM, no hardcoded constants."""

    # ── Phase geometry ────────────────────────────────────────────────────────
    phase_entropy: float         # H(φ) / H_max ∈ [0,1] — how spread are phases
    phase_mean: float            # circular mean of φ_berry
    phase_std: float             # circular std
    median_gap: float            # median inter-entry phase gap (sorted TSM)

    # ── Retrieval window (replaces hardcoded delta=0.5) ───────────────────────
    delta_tight: float           # 25th percentile gap × N_neighbors — tight resonance
    delta_wide: float            # 75th percentile gap × N_neighbors — broad resonance
    delta_natural: float         # entropy-proportional: 2π × H/H_max × 0.25

    # ── Channel weights (replaces W_SEMANTIC=0.78 etc.) ───────────────────────
    # Derived from PCA on [phi_semantic, phi_htri_proxy, phi_nonlocal_proxy]
    # or from explained variance in closure_score prediction
    w_semantic: float            # weight of semantic channel
    w_htri: float                # weight of HTRI channel
    w_nonlocal: float            # weight of nonlocal channel

    # ── Hebbian learning (replaces fixed eta=0.15, decay=0.98) ───────────────
    hebbian_eta: float           # 1 / sqrt(edge_count + 1)
    hebbian_decay: float         # 1 - 1/max(1, mean_winding)

    # ── Sector geometry (replaces fixed k=10) ─────────────────────────────────
    n_sectors: int               # optimal k from silhouette on TSM embeddings
    sector_centroids: np.ndarray | None  # (k, 384) if encoder available

    # ── Nonlocal index TTL ────────────────────────────────────────────────────
    nonlocal_ttl: float          # mean inter-write interval in seconds

    # ── Metadata ──────────────────────────────────────────────────────────────
    n_entries: int
    computed_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "phase_entropy": round(self.phase_entropy, 4),
            "phase_mean": round(self.phase_mean, 4),
            "phase_std": round(self.phase_std, 4),
            "median_gap": round(self.median_gap, 6),
            "delta_tight": round(self.delta_tight, 4),
            "delta_wide": round(self.delta_wide, 4),
            "delta_natural": round(self.delta_natural, 4),
            "w_semantic": round(self.w_semantic, 4),
            "w_htri": round(self.w_htri, 4),
            "w_nonlocal": round(self.w_nonlocal, 4),
            "hebbian_eta": round(self.hebbian_eta, 6),
            "hebbian_decay": round(self.hebbian_decay, 6),
            "n_sectors": self.n_sectors,
            "nonlocal_ttl": round(self.nonlocal_ttl, 1),
            "n_entries": self.n_entries,
        }


def calibrate(db_path: Path | None = None, force: bool = False) -> CIELCalibration:
    """Compute CIELCalibration from live TSM. Cached for TTL seconds."""
    global _CACHE, _CACHE_AT
    if not force and _CACHE is not None and (time.time() - _CACHE_AT) < _CACHE_TTL:
        return _CACHE

    _CACHE = _compute(db_path)
    _CACHE_AT = time.time()
    return _CACHE


def get_calibration() -> CIELCalibration:
    return calibrate()


def _compute(db_path: Path | None) -> CIELCalibration:
    import sqlite3, importlib.util as ilu, sys

    # ── Load TSM ──────────────────────────────────────────────────────────────
    if db_path is None:
        db_path = (
            Path(__file__).resolve().parents[2]
            / "CIEL_MEMORY_SYSTEM/TSM/ledger/memory_ledger.db"
        )

    with sqlite3.connect(str(db_path), timeout=15) as conn:
        rows = conn.execute("""
            SELECT phi_berry, closure_score, winding_n, W_S,
                   created_at
            FROM memories
            WHERE phi_berry IS NOT NULL
            ORDER BY created_at ASC
        """).fetchall()
        edge_count = conn.execute("SELECT COUNT(*) FROM memory_edges").fetchone()[0]

    if len(rows) < 3:
        return _fallback()

    phis = np.array([float(r[0]) for r in rows], dtype=np.float64)
    closures = np.array([float(r[1] or 0) for r in rows], dtype=np.float64)
    windings = np.array([int(r[2] or 0) for r in rows], dtype=np.float64)
    timestamps = [r[4] for r in rows if r[4]]

    n = len(phis)

    # ── Phase distribution ────────────────────────────────────────────────────
    # Circular mean
    c_mean = math.atan2(np.mean(np.sin(phis)), np.mean(np.cos(phis))) % (2 * math.pi)
    # Circular std via resultant length R
    R = float(np.abs(np.mean(np.exp(1j * phis))))
    c_std = float(np.sqrt(-2 * math.log(max(R, 1e-9))))

    # Phase entropy over 32 bins
    hist, _ = np.histogram(phis, bins=32, range=(-math.pi, math.pi))
    hist = hist.astype(float)
    p = hist / (hist.sum() + 1e-9)
    p = p[p > 1e-12]
    entropy = float(-np.sum(p * np.log(p)))
    max_entropy = math.log(32)
    phase_entropy = entropy / max_entropy

    # Inter-entry gaps (sorted)
    sorted_phis = np.sort(phis % (2 * math.pi))
    gaps = np.diff(sorted_phis)
    if len(gaps) == 0:
        gaps = np.array([0.1])

    median_gap = float(np.median(gaps))
    p25 = float(np.percentile(gaps, 25))
    p75 = float(np.percentile(gaps, 75))

    # Natural delta: entropy-proportional window
    # Low entropy (clustered) → tight window; high entropy (spread) → wider
    delta_natural = 2 * math.pi * phase_entropy * 0.20  # max = 0.2 × 2π ≈ 1.26 rad
    delta_tight = max(p25 * 20, 0.05)    # 20 nearest neighbors at p25 gap
    delta_wide = max(p75 * 20, 0.15)

    # ── Channel weights — normalised entropy contribution ─────────────────────
    # Problem: raw variance is scale-dependent (winding ∈ [0,152], phi ∈ [0,2π]).
    # Solution: measure each channel's *information content* via normalised
    # differential entropy H_norm = H / H_max (32-bin histogram, [0,1]).
    # Channels that are more spread (higher entropy) carry more information
    # and should receive higher weight.
    def _norm_entropy(arr: np.ndarray) -> float:
        lo, hi = float(arr.min()), float(arr.max())
        if hi - lo < 1e-12:
            return 0.0
        hist, _ = np.histogram(arr, bins=32, range=(lo, hi))
        p = hist.astype(float)
        p /= p.sum() + 1e-9
        p = p[p > 1e-12]
        h = float(-np.sum(p * np.log(p)))
        return h / math.log(32)  # normalise to [0,1]

    h_phi  = _norm_entropy(phis)     + 1e-6   # semantic channel
    h_wind = _norm_entropy(windings) + 1e-6   # HTRI/winding channel
    h_clos = _norm_entropy(closures) + 1e-6   # nonlocal/closure channel
    h_total = h_phi + h_wind + h_clos
    w_semantic = h_phi  / h_total
    w_htri     = h_wind / h_total
    w_nonlocal = h_clos / h_total

    # ── Hebbian parameters ────────────────────────────────────────────────────
    # eta scales inversely with network density
    hebbian_eta = 1.0 / math.sqrt(max(edge_count, 1) + 1)
    # decay from winding distribution: more winding → slower forgetting
    mean_winding = float(np.mean(windings)) if windings.mean() > 0 else 10.0
    hebbian_decay = 1.0 - 1.0 / max(mean_winding, 1.0)
    hebbian_decay = float(np.clip(hebbian_decay, 0.90, 0.999))

    # ── Optimal sector count ──────────────────────────────────────────────────
    n_sectors = _optimal_k(phis, k_range=(4, 16))

    # ── Nonlocal TTL from inter-write interval ────────────────────────────────
    nonlocal_ttl = _inter_write_interval(timestamps)

    return CIELCalibration(
        phase_entropy=phase_entropy,
        phase_mean=c_mean,
        phase_std=c_std,
        median_gap=median_gap,
        delta_tight=delta_tight,
        delta_wide=delta_wide,
        delta_natural=delta_natural,
        w_semantic=w_semantic,
        w_htri=w_htri,
        w_nonlocal=w_nonlocal,
        hebbian_eta=hebbian_eta,
        hebbian_decay=hebbian_decay,
        n_sectors=n_sectors,
        sector_centroids=None,
        nonlocal_ttl=nonlocal_ttl,
        n_entries=n,
    )


def _optimal_k(phis: np.ndarray, k_range: tuple[int, int] = (4, 16)) -> int:
    """Estimate optimal cluster count from phase distribution via gap statistic proxy.

    Uses variance of intra-cluster gaps to find the elbow.
    No sklearn required — pure numpy.
    """
    n = len(phis)
    if n < k_range[0] * 3:
        return k_range[0]

    # Subsample for speed — sector geometry stable at 256 points
    if n > 256:
        idx = np.random.default_rng(42).choice(n, 256, replace=False)
        phis = phis[idx]
        n = 256

    # Represent phases as 2D points on unit circle
    X = np.column_stack([np.cos(phis), np.sin(phis)])

    best_k = k_range[0]
    best_score = -1.0

    for k in range(k_range[0], min(k_range[1] + 1, n // 3)):
        # Simple k-means on unit circle (few iterations)
        indices = np.linspace(0, n - 1, k, dtype=int)
        centroids = X[indices]
        for _ in range(10):
            dists = np.linalg.norm(X[:, None, :] - centroids[None, :, :], axis=2)
            labels = np.argmin(dists, axis=1)
            new_centroids = np.array([
                X[labels == j].mean(axis=0) if (labels == j).any() else centroids[j]
                for j in range(k)
            ])
            norms = np.linalg.norm(new_centroids, axis=1, keepdims=True)
            centroids = new_centroids / (norms + 1e-9)

        # Vectorized intra-cluster distances
        dists_to_centroid = np.linalg.norm(X - centroids[labels], axis=1)
        intra_per_cluster = np.array([
            dists_to_centroid[labels == j].mean() if (labels == j).sum() > 1 else 0.0
            for j in range(k)
        ])
        intra = intra_per_cluster.mean()
        # Vectorized inter-centroid distances (upper triangle)
        diff = centroids[:, None, :] - centroids[None, :, :]   # (k,k,2)
        cdist = np.linalg.norm(diff, axis=2)                   # (k,k)
        mask = np.triu(np.ones((k, k), dtype=bool), k=1)
        inter = cdist[mask].mean() if k > 1 else 1.0

        score = inter / (intra + 1e-9)
        if score > best_score:
            best_score = score
            best_k = k

    return best_k


def _inter_write_interval(timestamps: list[str]) -> float:
    """Mean time between TSM writes in seconds. Fallback=60s."""
    from datetime import datetime
    if len(timestamps) < 2:
        return 60.0
    parsed = []
    for t in timestamps[-100:]:  # last 100 entries
        try:
            parsed.append(datetime.fromisoformat(t.replace("Z", "+00:00")).timestamp())
        except Exception:
            continue
    if len(parsed) < 2:
        return 60.0
    intervals = np.diff(sorted(parsed))
    intervals = intervals[intervals > 0]
    if len(intervals) == 0:
        return 60.0
    median_interval = float(np.median(intervals))
    # TTL = ~10× inter-write (index valid for 10 cycles)
    return float(np.clip(median_interval * 10, 30.0, 600.0))


def _fallback() -> CIELCalibration:
    """Minimal calibration when TSM is empty."""
    return CIELCalibration(
        phase_entropy=0.5,
        phase_mean=math.pi,
        phase_std=1.0,
        median_gap=0.1,
        delta_tight=0.3,
        delta_wide=0.8,
        delta_natural=0.5,
        w_semantic=0.78,
        w_htri=0.12,
        w_nonlocal=0.10,
        hebbian_eta=0.15,
        hebbian_decay=0.98,
        n_sectors=10,
        sector_centroids=None,
        nonlocal_ttl=60.0,
        n_entries=0,
    )
