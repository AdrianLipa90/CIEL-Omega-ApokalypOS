"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Reality layer enumerations.

Sources:
  - ext1.RealityLayer          — field name mapping (simple)
  - lie4full.RealityLayer      — 10-layer Enum (v11)
  - paradoxes.UltimateRealityLayer — 20-layer Enum (v13)
"""

from __future__ import annotations

from enum import Enum


class RealityLayer(Enum):
    """Core taxonomy of reality layers (v11 — CIEL/0 + LIE₄)."""

    QUANTUM_WAVEFUNCTION    = "ψ(x,t) - Quantum amplitude"
    CYMATIC_RESONANCE       = "ζ(s) - Zeta resonance patterns"
    MATHEMATICAL_STRUCTURE  = "M - Prime/Ramanujan structures"
    SPACETIME_GEOMETRY      = "g_μν - Metric tensor"
    CONSCIOUSNESS_FIELD     = "I(x,t) - Intention field"
    INFORMATION_GEOMETRY    = "G_IJ - Information metric"
    TOPOLOGICAL_INVARIANTS  = "Σ - Soul/winding numbers"
    MEMORY_STRUCTURE        = "M_mem - Unified memory field"
    EMOTIONAL_RESONANCE     = "E - Emotional computation field"
    SEMANTIC_LAYER          = "S - Semantic computation space"


class UltimateRealityLayer(Enum):
    """Complete taxonomy of ALL reality layers (v13 — ultimate with paradoxes)."""

    QUANTUM_WAVEFUNCTION    = "ψ(x,t) - Quantum amplitude"
    CYMATIC_RESONANCE       = "ζ(s) - Zeta resonance patterns"
    MATHEMATICAL_STRUCTURE  = "M - Prime/Ramanujan structures"
    SPACETIME_GEOMETRY      = "g_μν - Metric tensor"
    INFORMATION_FIELD       = "I(x,t) - Information field"
    INFORMATION_GEOMETRY    = "G_IJ - Information metric"
    TOPOLOGICAL_INVARIANTS  = "Σ - Topological winding numbers"
    MEMORY_STRUCTURE        = "M_mem - Unified memory field"
    SEMANTIC_LAYER          = "S - Semantic computation space"
    CONSCIOUSNESS_FIELD     = "C(x,t) - Pure awareness field"
    ETHICAL_POTENTIAL        = "E - Moral curvature field"
    TEMPORAL_SUPERFLUID     = "T_s - Time as quantum fluid"
    CAUSAL_STRUCTURE        = "C_μ - Causal connections"
    PARADOX_RESONANCE       = "P_ij - Paradox interaction tensor"
    QUANTUM_GRAVITY_FOAM    = "G_foam - Spacetime microstructure"
    STRING_VIBRATION        = "S_vib - Fundamental vibration modes"
    DARK_ENERGY_FIELD       = "Λ_eff - Effective cosmological constant"
    HOLOGRAPHIC_BOUNDARY    = "H_bound - Projection surface"
    CREATION_OPERATOR       = "O_creat - Reality generation field"
    ANNIHILATION_OPERATOR   = "O_annih - Reality dissolution field"


# Backwards-compatible field name mapping (ext1 style)
FIELD_NAMES = {
    "consciousness_field": "Ψ(x,t)",
    "symbolic_field":      "S(x,t)",
    "temporal_field":      "τ(x,t)",
    "resonance_field":     "R(S,Ψ)",
    "mass_field":          "m(x,t)",
    "energy_field":        "E(x,t)",
}

__all__ = ["RealityLayer", "UltimateRealityLayer", "FIELD_NAMES"]
