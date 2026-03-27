"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Unified physical and consciousness constants.

Sources (merged & deduplicated):
  - ext3.CIELPhysics         — SI constants + Schumann
  - ext7.CIELPhysics         — duplicate, same values
  - cielnofft.CIELParameters  — SI + CIEL/0 coupling params
  - cielquantum.CIELPhysics   — SI + quantised CIEL/0
  - definitekernel.RealityConstants — emergent consciousness constants
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np


# ---------------------------------------------------------------------------
# Physical / SI constants (canonical source for entire CIEL/Ω suite)
# ---------------------------------------------------------------------------

@dataclass
class CIELPhysics:
    """Unified physical constants and parameters for quantised CIEL/0.

    All values in SI unless noted.  This replaces the per-file duplicates
    that previously lived in ext3, ext7, cielnofft and cielquantum.
    """

    # Fundamental SI
    c: float = 299_792_458.0                    # speed of light [m/s]
    hbar: float = 1.054_571_817e-34             # reduced Planck constant [J·s]
    mu0: float = 4e-7 * np.pi                   # vacuum permeability [N/A²]
    eps0: float = 8.854_187_8128e-12            # vacuum permittivity [F/m]
    G: float = 6.674_30e-11                     # gravitational constant [m³·kg⁻¹·s⁻²]
    k_B: float = 1.380_649e-23                  # Boltzmann constant [J/K]

    # Planck scale
    L_planck: float = 1.616_255e-35             # Planck length [m]
    t_planck: float = 5.391_247e-44             # Planck time [s]
    m_planck: float = 2.176_434e-8              # Planck mass [kg]

    # Schumann / biological rhythms
    schumann_base_freq: float = 7.83            # Hz (first harmonic)

    # CIEL/0 coupling parameters (from cielnofft.CIELParameters)
    lambda_1: float = 0.1                       # intention field coupling
    lambda_2: float = 0.05                      # Λ₀ coupling
    lambda_3: float = 0.2                       # phase coupling
    alpha: float = 0.01                         # cognitive shear coupling
    beta: float = 0.1                           # topological coupling
    eta: float = 0.001                          # resonance-curvature coupling

    # Derived helpers
    def planck_energy(self) -> float:
        """E_p = ℏ / t_p"""
        return self.hbar / self.t_planck

    def fine_structure(self) -> float:
        """α ≈ e²/(4πε₀ℏc) — approximate with μ₀."""
        e = 1.602_176_634e-19
        return (self.mu0 * e**2 * self.c) / (2.0 * 6.626_070_15e-34)


# ---------------------------------------------------------------------------
# Emergent consciousness constants (from definitekernel.RealityConstants)
# ---------------------------------------------------------------------------

@dataclass
class RealityConstants:
    """Constants emerging from consciousness–matter unification.

    These define the complete mathematical structure of reality
    as described in Adrian Lipa's CIEL/0 framework.
    """

    # Core consciousness constants (quantum emergence)
    CONSCIOUSNESS_QUANTUM: float = 0.474812     # α_c — fundamental quantum of experience
    SYMBOLIC_COUPLING: float = 0.856234         # β_s — matter–symbol coupling strength
    TEMPORAL_FLOW: float = 0.345123             # γ_t — intrinsic time evolution rate
    RESONANCE_QUANTUM: float = 0.634567         # δ_r — quantum of symbolic resonance

    # Reality structure
    LIPA_CONSTANT: float = 0.474812             # Λ — fundamental reality constant
    MAX_COHERENCE: float = 0.751234             # Γ_max — maximum quantum coherence
    ETHICAL_BOUND: float = 0.900000             # Ε — life preservation threshold

    # Derived physical constants (normalised units)
    EFFECTIVE_HBAR: float = 0.892345            # ℏ_eff — emergent Planck constant
    EFFECTIVE_C: float = 0.956712               # c_eff — consciousness-limited light speed
    EFFECTIVE_G: float = 0.734561               # G_eff — consciousness-coupled gravity

    # Quantum information
    INFORMATION_PRESERVATION: float = 0.998765  # ι — quantum information preservation
    ENTANGLEMENT_STRENGTH: float = 0.723456     # ε — consciousness entanglement strength

    # Paradox / advanced fields (from paradoxes.py UltimateCIELConstants)
    ETHICAL_CURVATURE: float = 0.1
    TEMPORAL_VISCOSITY: float = 0.05
    PARADOX_COHERENCE: float = 0.15
    QUANTUM_FOAM_DENSITY: float = 0.001
    L_p: float = 1.616_255e-35                  # Planck length (for foam modulation)


__all__ = ["CIELPhysics", "RealityConstants"]
