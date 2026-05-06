"""Orbital shell model for CIEL memory — M0-M8 as atomic shells.

Identity = centre of Bloch sphere (fixed attractor under SU(2)), not a point
on its surface.  Each memory record carries orbital coordinates:
  - shell      : int 0-8  (K=M0 … S=M8)
  - E_bind     : binding energy to the attractor  E = -G_sem * M_att / r²
  - L_phase    : angular momentum  L = r × p_phase  (Kepler conserved quantity)
  - r_phase    : phase distance from attractor

Retrieve = inter-shell transition (not sequential stack scan).
Pauli exclusion: two records with identical (shell, modal_hash) cannot coexist.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
G_SEM: float = 0.42        # semantic gravitational constant (tuned empirically)
M_ATTRACTOR: float = 1.0   # attractor mass — normalised; scales with identity coherence
_PAULI_BINS: int = 256     # phase-space bins for Pauli exclusion check

# Shell names (spectroscopic analogy)
SHELL_NAMES = {0: "K", 1: "L", 2: "M", 3: "N", 4: "O", 5: "P", 6: "Q", 7: "R", 8: "S"}
# Max records per shell — outermost shell (S=M8) most easily ionised
SHELL_CAPACITY = {0: 2, 1: 8, 2: 18, 3: 32, 4: 32, 5: 18, 6: 8, 7: 4, 8: 2}


# ---------------------------------------------------------------------------
# Core geometry helpers
# ---------------------------------------------------------------------------

def phase_distance(phi_a: float, phi_b: float) -> float:
    """Circular distance in [0, π]."""
    d = abs((phi_a - phi_b + math.pi) % (2 * math.pi) - math.pi)
    return d


def compute_E_bind(r_phase: float, G_sem: float = G_SEM, M_att: float = M_ATTRACTOR) -> float:
    """Keplerian binding energy E = -G_sem * M_att / r²  (negative = bound).

    r_phase is the circular phase distance from the attractor (identity centre).
    Clipped to avoid singularity at r=0.
    """
    r = max(r_phase, 1e-6)
    return -G_sem * M_att / (r * r)


def compute_angular_momentum(r_phase: float, p_phase: float) -> float:
    """L = r × p_phase — conserved under Keplerian orbit."""
    return r_phase * p_phase


def shell_from_E_bind(E_bind: float) -> int:
    """Map binding energy to shell index 0-8.

    Deeper binding (more negative E) → inner shell (lower index).
    Phase distances are bounded by [r_min, π]; we use linear spacing
    across this physically reachable range.
    """
    if E_bind >= 0.0:
        return 8  # unbound → outermost / audit shell
    # E = -G/r²  →  r = sqrt(G/|E|) = sqrt(G/(-E_bind))
    r = math.sqrt(G_SEM * M_ATTRACTOR / (-E_bind))
    # Map r ∈ [r_min, π] linearly to shell 0-8
    # Small r (close to attractor) → shell 0; large r → shell 8
    r_min, r_max = 0.02, math.pi
    r_clipped = max(r_min, min(r_max, r))
    frac = (r_clipped - r_min) / (r_max - r_min)
    return min(8, int(frac * 9))


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class OrbitalRecord:
    """A memory record situated in the orbital shell model.

    Wraps arbitrary memory content with its orbital coordinates.
    Compatible with existing Episode / SemanticMemoryItem etc. — wrap, don't replace.
    """
    # Identity
    record_id: str
    content: Any                        # original memory object (Episode, semantic item…)
    modal_hash: int                     # coarse phase-space bin for Pauli exclusion

    # Orbital coordinates
    r_phase: float                      # phase distance from attractor
    E_bind: float                       # binding energy (negative = bound)
    L_phase: float                      # angular momentum
    shell: int                          # 0-8

    # Provenance
    source_module: str = "unknown"      # which M_k deposited this record
    confidence: float = 0.5
    timestamp: float = 0.0

    # BEC condensation flag — set when record resonates with attractor phase
    condensed: bool = False

    @classmethod
    def from_phase(
        cls,
        record_id: str,
        content: Any,
        phi_record: float,
        phi_attractor: float,
        p_phase: float = 0.0,
        source_module: str = "unknown",
        confidence: float = 0.5,
        timestamp: float = 0.0,
    ) -> "OrbitalRecord":
        r = phase_distance(phi_record, phi_attractor)
        E = compute_E_bind(r)
        L = compute_angular_momentum(r, p_phase)
        shell = shell_from_E_bind(E)
        modal_hash = int(((phi_record + math.pi) / (2 * math.pi)) * _PAULI_BINS) % _PAULI_BINS
        return cls(
            record_id=record_id,
            content=content,
            modal_hash=modal_hash,
            r_phase=r,
            E_bind=E,
            L_phase=L,
            shell=shell,
            source_module=source_module,
            confidence=confidence,
            timestamp=timestamp,
        )


# ---------------------------------------------------------------------------
# Shell index
# ---------------------------------------------------------------------------

@dataclass
class OrbitalShellIndex:
    """Index of OrbitalRecords organised by shell.

    Enforces:
    - Capacity limits per shell (SHELL_CAPACITY)
    - Pauli exclusion: no two records share (shell, modal_hash)

    When a shell is full, the record with the highest r_phase (loosest binding)
    is evicted — analogous to ionisation.
    """
    _shells: Dict[int, List[OrbitalRecord]] = field(default_factory=lambda: {i: [] for i in range(9)})
    _id_index: Dict[str, OrbitalRecord] = field(default_factory=dict)

    # Attractor phase — updated externally from identity_phase
    attractor_phase: float = 0.0

    def insert(self, record: OrbitalRecord) -> Optional[OrbitalRecord]:
        """Insert record.  Returns evicted record if shell was full, else None."""
        shell = record.shell
        bucket = self._shells[shell]

        # Pauli exclusion check
        for existing in bucket:
            if existing.modal_hash == record.modal_hash:
                # Same phase bin already occupied — condense to lower shell if possible
                record = self._condense_down(record)
                shell = record.shell
                bucket = self._shells[shell]
                break

        evicted: Optional[OrbitalRecord] = None
        cap = SHELL_CAPACITY[shell]
        if len(bucket) >= cap:
            # Evict loosest-bound record (highest r_phase)
            loosest = max(bucket, key=lambda r: r.r_phase)
            bucket.remove(loosest)
            del self._id_index[loosest.record_id]
            evicted = loosest

        bucket.append(record)
        self._id_index[record.record_id] = record
        return evicted

    def _condense_down(self, record: OrbitalRecord) -> OrbitalRecord:
        """Try to place record one shell inward (BEC condensation)."""
        target_shell = max(0, record.shell - 1)
        # Recompute with slightly reduced r (condensation shifts phase closer to attractor)
        new_r = record.r_phase * 0.85
        new_E = compute_E_bind(new_r)
        from dataclasses import replace
        condensed = replace(record, shell=target_shell, r_phase=new_r, E_bind=new_E, condensed=True)
        return condensed

    def retrieve(self, phi_query: float, n: int = 5, prefer_shell: Optional[int] = None) -> List[OrbitalRecord]:
        """Retrieve top-n records closest in phase to query.

        Inter-shell transition: starts from the shell closest to query energy,
        then expands outward — like an electron transition probing adjacent shells.
        """
        r_query = phase_distance(phi_query, self.attractor_phase)
        E_query = compute_E_bind(r_query)
        target_shell = shell_from_E_bind(E_query) if prefer_shell is None else prefer_shell

        visited: set[int] = set()
        candidates: List[OrbitalRecord] = []
        # Scan target shell first, then neighbours expanding outward
        for delta in range(9):
            for s in (target_shell - delta, target_shell + delta):
                if 0 <= s <= 8 and s not in visited:
                    visited.add(s)
                    candidates.extend(self._shells[s])
            if len(candidates) >= n * 3:
                break

        # Rank by phase proximity to query
        r_query = phase_distance(phi_query, self.attractor_phase)
        candidates.sort(key=lambda r: abs(r.r_phase - r_query))
        # Deduplicate by record_id (safety)
        seen: set[str] = set()
        unique = [r for r in candidates if not (r.record_id in seen or seen.add(r.record_id))]  # type: ignore[func-returns-value]
        return unique[:n]

    def get(self, record_id: str) -> Optional[OrbitalRecord]:
        return self._id_index.get(record_id)

    def shell_summary(self) -> Dict[str, Any]:
        return {
            SHELL_NAMES[i]: {
                "count": len(self._shells[i]),
                "capacity": SHELL_CAPACITY[i],
                "mean_E_bind": (
                    sum(r.E_bind for r in self._shells[i]) / len(self._shells[i])
                    if self._shells[i] else None
                ),
            }
            for i in range(9)
        }
