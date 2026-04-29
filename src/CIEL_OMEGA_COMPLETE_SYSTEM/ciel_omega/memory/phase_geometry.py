"""CIEL Phase Geometry — CP², Poincaré disk, hypertorus.

Replaces scalar S¹ phase arithmetic with full geometric state space:

  CP² — complex projective plane as 3-channel encoder state space
       (φ_semantic, φ_htri, φ_nonlocal) → [z₀:z₁:z₂] ∈ CP²
       Distance: Fubini-Study metric → geodesic arcs, not flat angles

  Poincaré disk D² — inference volume inside CP²
       Project CP² → D² via stereographic: z = z₁/z₀ (chart)
       Möbius transformations preserve hyperbolic metric
       |z| = coherence (0 = maximally coherent, 1 = boundary = incoherent)
       arg(z) = dominant semantic phase

  Hypertorus T³ — homotopy constraint from winding numbers
       winding_n per memory entry → class in π₁(T³) = Z³
       Entries in same homotopy class are topologically connected
       Euler constraint violation ↔ defect in T³ lattice

Usage:
    from phase_geometry import CP2State, PoincareDisk, HypertorusLattice

    state = CP2State.from_channels(phi_s, phi_h, phi_nl, kappa)
    disk_z = state.to_poincare()
    dist = CP2State.fubini_study(state_a, state_b)
"""
from __future__ import annotations

import cmath
import math
from dataclasses import dataclass, field
from typing import Sequence

import numpy as np


# ── CP² State ─────────────────────────────────────────────────────────────────

@dataclass
class CP2State:
    """Point in CP² represented as normalised homogeneous coordinates [z₀:z₁:z₂].

    z₀ = exp(i·φ_semantic) × sqrt(w_s)
    z₁ = exp(i·φ_htri)     × sqrt(w_h)
    z₂ = exp(i·φ_nonlocal) × sqrt(w_nl)
    |z₀|² + |z₁|² + |z₂|² = 1  (normalised)

    Channel weights default: w_s=0.78, w_h=0.12, w_nl=0.10
    (match _HTRI_ALPHA and _NONLOCAL_ALPHA in ciel_encoder.py)
    """
    z: np.ndarray  # shape (3,) complex128 — normalised homogeneous coords

    # Channel weight fallbacks (overridden by live calibration at construction time)
    W_SEMANTIC  = 0.78
    W_HTRI      = 0.12
    W_NONLOCAL  = 0.10

    @staticmethod
    def _calibrated_weights() -> tuple[float, float, float]:
        """Return (w_semantic, w_htri, w_nonlocal) from live TSM calibration."""
        try:
            import importlib.util as _ilu, sys as _sys
            from pathlib import Path as _Path
            _cal_path = _Path(__file__).parent / "ciel_calibration.py"
            if "ciel_calibration_pg" not in _sys.modules:
                _spec = _ilu.spec_from_file_location("ciel_calibration_pg", _cal_path)
                _mod = _ilu.module_from_spec(_spec)
                _sys.modules["ciel_calibration_pg"] = _mod
                _spec.loader.exec_module(_mod)
            else:
                _mod = _sys.modules["ciel_calibration_pg"]
            cal = _mod.get_calibration()
            return float(cal.w_semantic), float(cal.w_htri), float(cal.w_nonlocal)
        except Exception:
            return 0.78, 0.12, 0.10

    @classmethod
    def from_channels(
        cls,
        phi_semantic: float,
        phi_htri: float = 0.0,
        phi_nonlocal: float = 0.0,
        coherence: float = 1.0,
    ) -> "CP2State":
        """Build CP² state from three phase channels and local coherence."""
        ws, wh, wn = cls._calibrated_weights()
        z0 = cmath.exp(1j * phi_semantic) * math.sqrt(ws)
        z1 = cmath.exp(1j * phi_htri)     * math.sqrt(wh)
        z2 = cmath.exp(1j * phi_nonlocal) * math.sqrt(wn)
        arr = np.array([z0, z1, z2], dtype=np.complex128)
        norm = np.linalg.norm(arr)
        if norm > 1e-12:
            arr /= norm
        return cls(z=arr)

    @classmethod
    def from_phase(cls, phi: float) -> "CP2State":
        """Minimal CP² state from scalar phase (z₁=z₂=0 limit)."""
        return cls.from_channels(phi_semantic=phi)

    # ── Geometry ──────────────────────────────────────────────────────────────

    @staticmethod
    def fubini_study(a: "CP2State", b: "CP2State") -> float:
        """Fubini-Study geodesic distance d_FS(a,b) ∈ [0, π/2].

        d_FS = arccos(|⟨a|b⟩|)
        Invariant under U(3) rotations — the natural metric on CP².
        """
        inner = float(abs(np.dot(a.z.conj(), b.z)))
        inner = min(inner, 1.0)  # numerical clamp
        return float(np.arccos(inner))

    def dominant_phase(self) -> float:
        """Dominant S¹ phase: arg of the largest-magnitude component."""
        idx = int(np.argmax(np.abs(self.z)))
        return float(cmath.phase(complex(self.z[idx]))) % (2 * math.pi)

    def mean_phase(self) -> float:
        """Circular mean of all three channel phases, weighted by |z_i|²."""
        weights = np.abs(self.z) ** 2
        angles = np.array([cmath.phase(complex(zi)) for zi in self.z])
        z_mean = np.sum(weights * np.exp(1j * angles))
        return float(cmath.phase(complex(z_mean))) % (2 * math.pi)

    def channel_coherence(self) -> float:
        """Inter-channel coherence ∈ [0,1].
        Kuramoto order parameter: |mean(exp(i·φ_k))| weighted by |z_k|².
        1 = all channels phase-aligned, 0 = maximally dispersed.
        """
        weights = np.abs(self.z) ** 2
        angles = np.array([cmath.phase(complex(zi)) for zi in self.z])
        r = complex(np.sum(weights * np.exp(1j * angles)))
        return float(min(abs(r), 1.0))

    # ── Poincaré projection ───────────────────────────────────────────────────

    def to_poincare(self) -> complex:
        """Stereographic chart z₁/z₀: CP² → D² (Poincaré disk).

        |result| ∈ [0,1):  0 = pole (z₀ dominant), boundary = z₀→0
        arg(result) = relative phase φ_htri - φ_semantic
        Möbius automorphisms of D² preserve this chart's metric.
        """
        z0 = complex(self.z[0])
        z1 = complex(self.z[1])
        if abs(z0) < 1e-12:
            return complex(1.0, 0.0)  # boundary point
        w = z1 / z0
        # Project into open unit disk via Cayley-like map if |w| >= 1
        if abs(w) >= 1.0:
            w = w / (abs(w) + 1e-9) * 0.999
        return w

    def to_poincare_full(self) -> tuple[complex, complex]:
        """Both charts: (z₁/z₀, z₂/z₀) — full CP² → D²×D² projection."""
        z0 = complex(self.z[0])
        z1 = complex(self.z[1])
        z2 = complex(self.z[2])
        if abs(z0) < 1e-12:
            return (complex(1.0), complex(1.0))
        w1 = z1 / z0
        w2 = z2 / z0
        def _clamp(w: complex) -> complex:
            m = abs(w)
            return w / m * 0.999 if m >= 1.0 else w
        return _clamp(w1), _clamp(w2)

    # ── Möbius transform ──────────────────────────────────────────────────────

    @staticmethod
    def mobius(z: complex, a: complex) -> complex:
        """Möbius automorphism of D²: T_a(z) = (z - a) / (1 - ā·z).

        Used for: shifting reference point (a) in inference volume
        without changing the hyperbolic metric structure.
        """
        denom = 1.0 - a.conjugate() * z
        if abs(denom) < 1e-12:
            return complex(1.0)
        return (z - a) / denom

    def poincare_distance(self, other: "CP2State") -> float:
        """Hyperbolic distance in Poincaré disk between two states.

        d_hyp(z₁,z₂) = 2 arctanh(|T_{z₁}(z₂)|)
        This is the natural distance for inference in D².
        """
        w1 = self.to_poincare()
        w2 = other.to_poincare()
        diff = self.mobius(w2, w1)
        return 2.0 * float(np.arctanh(min(abs(diff), 0.9999)))

    def __repr__(self) -> str:
        ph = self.mean_phase()
        coh = self.channel_coherence()
        d = self.to_poincare()
        return f"CP2State(φ={ph:.3f}, coh={coh:.3f}, |d|={abs(d):.3f})"


# ── Poincaré Disk inference volume ────────────────────────────────────────────

class PoincareDisk:
    """Inference volume: retrieval in hyperbolic metric instead of flat S¹.

    In the Poincaré model:
    - centre D = 0 corresponds to high-coherence "orbital ground state"
    - boundary |z|→1 = incoherent / maximal entropy states
    - geodesics = arcs orthogonal to boundary circle
    - equal-distance balls = hyperbolic circles (smaller near boundary)

    Retrieval: given query point q ∈ D², find all memory states within
    hyperbolic radius r_h. This gives tighter retrieval near coherent centre
    and looser retrieval near incoherent boundary — naturally matching
    the Euler/EBA closure behaviour.
    """

    def __init__(self, radius: float = 1.5):
        self.radius = radius  # hyperbolic retrieval radius

    def in_ball(self, query: CP2State, candidate: CP2State) -> bool:
        return candidate.poincare_distance(query) <= self.radius

    def distance(self, a: CP2State, b: CP2State) -> float:
        return a.poincare_distance(b)

    def retrieval_weight(self, query: CP2State, candidate: CP2State,
                         w_s: float = 1.0) -> float:
        """Holonomic weight in hyperbolic metric.

        w = w_s × exp(-d_hyp² / σ²) × channel_coherence
        σ = radius / 2 — Gaussian kernel in hyperbolic space
        """
        d = self.distance(query, candidate)
        sigma = self.radius / 2.0
        geo_weight = math.exp(-(d ** 2) / (sigma ** 2 + 1e-9))
        coh = candidate.channel_coherence()
        return w_s * geo_weight * coh


# ── Hypertorus homotopy lattice ────────────────────────────────────────────────

@dataclass
class HomotopyClass:
    """Homotopy class in π₁(T³) = Z³ determined by winding numbers.

    winding = (n_s, n_h, n_nl) ∈ Z³
    Two entries are in the same class ↔ same winding triple.
    Entries in the same class have topological affinity regardless of φ.
    """
    n_semantic:  int = 0
    n_htri:      int = 0
    n_nonlocal:  int = 0

    @classmethod
    def from_winding(cls, winding_n: int,
                     n_htri: int = 0,
                     n_nonlocal: int = 0) -> "HomotopyClass":
        return cls(n_semantic=winding_n, n_htri=n_htri, n_nonlocal=n_nonlocal)

    def same_class(self, other: "HomotopyClass") -> bool:
        return (self.n_semantic == other.n_semantic and
                self.n_htri == other.n_htri and
                self.n_nonlocal == other.n_nonlocal)

    def lattice_distance(self, other: "HomotopyClass") -> float:
        """L2 distance in Z³ lattice (0 = same class)."""
        return math.sqrt(
            (self.n_semantic - other.n_semantic) ** 2 +
            (self.n_htri - other.n_htri) ** 2 +
            (self.n_nonlocal - other.n_nonlocal) ** 2
        )

    def euler_defect(self) -> float:
        """Topological defect: deviation from trivial winding (0,0,0).
        Maps to euler_constraint violation proxy.
        """
        return self.lattice_distance(HomotopyClass(0, 0, 0))


class HypertorusLattice:
    """T³ homotopy constraint enforcement for memory retrieval.

    During retrieval: entries in closer homotopy classes get a boost.
    During Euler check: large lattice_distance → topological defect signal.
    """

    @staticmethod
    def homotopy_affinity(a: HomotopyClass, b: HomotopyClass,
                          sigma: float = 2.0) -> float:
        """Affinity ∈ [0,1] based on Z³ lattice distance.
        sigma = characteristic distance (classes within sigma are strongly connected)
        """
        d = a.lattice_distance(b)
        return math.exp(-(d ** 2) / (sigma ** 2))

    @staticmethod
    def from_db_entry(winding_n: int | None) -> HomotopyClass:
        """Build homotopy class from TSM winding_n (single-channel legacy)."""
        return HomotopyClass.from_winding(winding_n or 0)

    @staticmethod
    def euler_violation_from_classes(classes: Sequence[HomotopyClass]) -> float:
        """Aggregate Euler defect: mean pairwise lattice distance.
        High value → topological tension in memory → closure penalty.
        """
        if len(classes) < 2:
            return 0.0
        total = 0.0
        count = 0
        for i in range(len(classes)):
            for j in range(i + 1, len(classes)):
                total += classes[i].lattice_distance(classes[j])
                count += 1
        return total / count if count > 0 else 0.0


# ── Combined retrieval weight (Poincaré + Hypertorus) ─────────────────────────

def cp2_retrieval_weight(
    query_state: CP2State,
    candidate_state: CP2State,
    query_class: HomotopyClass,
    candidate_class: HomotopyClass,
    w_s: float = 1.0,
    disk_radius: float = 1.5,
    torus_sigma: float = 2.0,
    alpha_disk: float = 0.7,
    alpha_torus: float = 0.3,
) -> float:
    """Full geometric retrieval weight combining Poincaré + Hypertorus.

    w = alpha_disk × w_poincare + alpha_torus × w_torus
    w_poincare = Gaussian kernel in hyperbolic D² metric × coherence
    w_torus    = homotopy affinity in Z³ lattice
    """
    disk = PoincareDisk(radius=disk_radius)
    w_p = disk.retrieval_weight(query_state, candidate_state, w_s)
    w_t = HypertorusLattice.homotopy_affinity(query_class, candidate_class, torus_sigma)
    return alpha_disk * w_p + alpha_torus * w_t * w_s


# ── Integration helpers ───────────────────────────────────────────────────────

def encoder_result_to_cp2(enc_result: "Any", htri_phi: float = 0.0,
                           nonlocal_phi: float = 0.0) -> CP2State:
    """Convert EncoderResult → CP2State."""
    return CP2State.from_channels(
        phi_semantic=enc_result.phase,
        phi_htri=htri_phi,
        phi_nonlocal=nonlocal_phi,
        coherence=enc_result.coherence,
    )


def db_row_to_cp2(phi_berry: float, winding_n: int = 0) -> CP2State:
    """Convert legacy TSM row (phi_berry scalar) → CP2State (single-channel)."""
    return CP2State.from_channels(
        phi_semantic=phi_berry,
        phi_htri=0.0,
        phi_nonlocal=0.0,
    )


__all__ = [
    "CP2State",
    "PoincareDisk",
    "HomotopyClass",
    "HypertorusLattice",
    "cp2_retrieval_weight",
    "encoder_result_to_cp2",
    "db_row_to_cp2",
]
