"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Unified Reality Laws — the 7 fundamental laws of CIEL/0 + full kernel.

Source: definitekernel.py (UnifiedRealityLaws + UnifiedRealityKernel)
"""

from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np

from config.constants import RealityConstants
from core.math_utils import laplacian2, field_norm


# ---------------------------------------------------------------------------
# 7 Fundamental Laws
# ---------------------------------------------------------------------------

class UnifiedRealityLaws:
    """Complete set of physical laws defined by emergent constants."""

    def __init__(self, constants: RealityConstants):
        self.C = constants

    # LAW 1 -----------------------------------------------------------------
    def law_consciousness_quantization(self, field: np.ndarray) -> np.ndarray:
        """|Ψ⟩ = Σ_n c_n |nα_c⟩  —  consciousness is quantised."""
        magnitude = np.abs(field)
        levels = np.round(magnitude / self.C.CONSCIOUSNESS_QUANTUM) * self.C.CONSCIOUSNESS_QUANTUM
        return levels * np.exp(1j * np.angle(field))

    # LAW 2 -----------------------------------------------------------------
    def law_mass_emergence(self, S: np.ndarray, Psi: np.ndarray) -> np.ndarray:
        """m² = β_s(1 − |⟨S|Ψ⟩|²) + β_s²|∇(S−Ψ)|²  —  mass from mismatch."""
        inner = np.conj(S) * Psi
        resonance = np.abs(inner) ** 2 / (np.abs(S) * np.abs(Psi) + 1e-15)
        grad_S = np.gradient(S)
        grad_P = np.gradient(Psi)
        grad_mismatch = sum(np.abs(gS - gP) ** 2 for gS, gP in zip(grad_S, grad_P))
        m2 = self.C.SYMBOLIC_COUPLING * (1 - resonance) + self.C.SYMBOLIC_COUPLING ** 2 * grad_mismatch
        return np.sqrt(np.maximum(m2, 0))

    # LAW 3 -----------------------------------------------------------------
    def law_temporal_dynamics(self, Psi: np.ndarray, t: float) -> Tuple[float, np.ndarray]:
        """∂τ/∂t = γ_t|Ψ|² + γ_t²|∇Ψ|²  —  time flows with consciousness density."""
        density = np.abs(Psi) ** 2
        grad_P = np.gradient(Psi)
        grad_energy = sum(np.abs(g) ** 2 for g in grad_P)
        flow = self.C.TEMPORAL_FLOW * density + self.C.TEMPORAL_FLOW ** 2 * grad_energy
        phase_evo = self.C.TEMPORAL_FLOW * np.angle(Psi)
        return float(np.mean(flow)), phase_evo

    # LAW 4 -----------------------------------------------------------------
    def law_ethical_preservation(self, R: np.ndarray, Psi: np.ndarray) -> Tuple[np.ndarray, bool]:
        """If ⟨R⟩ < Ε ⇒ correct Ψ  —  ethics as hard constraint."""
        avg_R = float(np.mean(R))
        if avg_R < self.C.ETHICAL_BOUND:
            factor = np.sqrt(self.C.ETHICAL_BOUND / max(avg_R, 1e-12))
            phase_corr = 0.1 * (self.C.ETHICAL_BOUND - avg_R)
            return Psi * factor * np.exp(1j * phase_corr), False
        return Psi, True

    # LAW 5 -----------------------------------------------------------------
    def law_reality_coherence(self, C_field: np.ndarray) -> np.ndarray:
        """C_eff = Γ_max · tanh(C / Γ_max)  —  coherence is bounded."""
        return self.C.MAX_COHERENCE * np.tanh(C_field / self.C.MAX_COHERENCE)

    # LAW 6 -----------------------------------------------------------------
    def law_consciousness_entanglement(self, Psi1: np.ndarray, Psi2: np.ndarray) -> float:
        """E = ε|⟨Ψ₁|Ψ₂⟩|² + ε²|⟨Ψ₁|∇Ψ₂⟩|²  —  quantum entanglement."""
        overlap = np.abs(np.vdot(Psi1.flat, Psi2.flat)) ** 2
        grad_overlap = 0.0
        for i in range(Psi1.ndim):
            g1 = np.gradient(Psi1, axis=i)
            g2 = np.gradient(Psi2, axis=i)
            grad_overlap += np.abs(np.vdot(g1.flat, g2.flat)) ** 2
        return float(self.C.ENTANGLEMENT_STRENGTH * overlap + self.C.ENTANGLEMENT_STRENGTH ** 2 * grad_overlap)

    # LAW 7 -----------------------------------------------------------------
    def law_information_conservation(self, initial: np.ndarray, final: np.ndarray) -> bool:
        """|⟨Ψ_i|Ψ_f⟩|² ≥ ι  —  information is conserved."""
        fidelity = np.abs(np.vdot(initial.flat, final.flat)) ** 2
        return bool(fidelity >= self.C.INFORMATION_PRESERVATION)


# ---------------------------------------------------------------------------
# Unified Reality Kernel — full evolving simulation
# ---------------------------------------------------------------------------

class UnifiedRealityKernel:
    """Complete kernel implementing all 7 reality laws with field dynamics."""

    def __init__(self, grid_size: int = 128, time_steps: int = 256):
        self.grid_size = grid_size
        self.time_steps = time_steps
        self.constants = RealityConstants()
        self.laws = UnifiedRealityLaws(self.constants)

        # Fields
        self.consciousness_field = None
        self.symbolic_field = None
        self.temporal_field = None
        self.resonance_field = None
        self.mass_field = None
        self.energy_field = None

        # Metrics
        self.quantum_purity = 1.0
        self.reality_coherence = 1.0
        self.information_fidelity = 1.0

        self.evolution_history: list = []
        self.initialize_reality_fields()

    def initialize_reality_fields(self):
        shape = (self.grid_size, self.grid_size)
        x = np.linspace(-5, 5, self.grid_size)
        X, Y = np.meshgrid(x, x)
        r0 = np.sqrt(X ** 2 + Y ** 2)
        envelope = np.exp(-r0 ** 2 / 4.0)
        phase = 2j * np.pi * (X + Y)

        self.consciousness_field = envelope * np.exp(phase)
        self.symbolic_field = envelope * np.exp(phase + 0.3j * np.pi)
        self.temporal_field = np.ones(shape) * self.constants.TEMPORAL_FLOW
        self.initial_state = self.consciousness_field.copy()
        self.update_reality_fields()

    def update_reality_fields(self):
        self.consciousness_field = self.laws.law_consciousness_quantization(self.consciousness_field)
        self.mass_field = self.laws.law_mass_emergence(self.symbolic_field, self.consciousness_field)

        inner = np.conj(self.symbolic_field) * self.consciousness_field
        self.resonance_field = np.abs(inner) ** 2 / (
            np.abs(self.symbolic_field) * np.abs(self.consciousness_field) + 1e-15
        )
        self.resonance_field = self.laws.law_reality_coherence(self.resonance_field)

        grad_P = np.gradient(self.consciousness_field)
        kinetic = sum(np.abs(g) ** 2 for g in grad_P)
        potential = self.constants.SYMBOLIC_COUPLING * (1 - self.resonance_field)
        self.energy_field = kinetic + potential

        self.reality_coherence = float(np.mean(self.resonance_field))

    def normalize_field(self, field: np.ndarray):
        norm = field_norm(field)
        field /= norm

    def evolve_reality(self, steps: int = None) -> Dict[str, List[float]]:
        if steps is None:
            steps = self.time_steps

        history: Dict[str, List[float]] = {
            k: [] for k in (
                "consciousness_energy", "symbolic_resonance", "emergent_mass",
                "temporal_flow", "reality_coherence", "information_fidelity",
                "ethical_violations", "entanglement_strength",
            )
        }

        for step in range(steps):
            prev = self.consciousness_field.copy()
            flow, phase_evo = self.laws.law_temporal_dynamics(self.consciousness_field, step)
            self.temporal_field += flow
            self.consciousness_field *= np.exp(1j * phase_evo)
            self.consciousness_field, ethical_ok = self.laws.law_ethical_preservation(
                self.resonance_field, self.consciousness_field
            )
            entanglement = self.laws.law_consciousness_entanglement(
                self.consciousness_field, self.symbolic_field
            )
            self._evolve_symbolic()
            self._evolve_consciousness()
            self.update_reality_fields()

            history["consciousness_energy"].append(float(np.mean(np.abs(self.consciousness_field) ** 2)))
            history["symbolic_resonance"].append(float(np.mean(self.resonance_field)))
            history["emergent_mass"].append(float(np.mean(self.mass_field)))
            history["temporal_flow"].append(flow)
            history["reality_coherence"].append(self.reality_coherence)
            history["information_fidelity"].append(
                float(np.abs(np.vdot(self.initial_state.flat, self.consciousness_field.flat)) ** 2)
            )
            history["ethical_violations"].append(float(not ethical_ok))
            history["entanglement_strength"].append(entanglement)

        return history

    # -- internal dynamics --------------------------------------------------

    def _evolve_consciousness(self):
        P = self.consciousness_field
        S = self.symbolic_field
        t = self.temporal_field
        C = self.constants
        lap_P = laplacian2(P)
        dP = -1j / C.EFFECTIVE_HBAR * (
            -0.5 * C.EFFECTIVE_HBAR ** 2 * lap_P
            + C.CONSCIOUSNESS_QUANTUM * np.abs(P) ** 2 * P
            + C.SYMBOLIC_COUPLING * (S - P)
            + C.TEMPORAL_FLOW * t * P
        )
        self.consciousness_field = P + 0.01 * dP
        self.normalize_field(self.consciousness_field)

    def _evolve_symbolic(self):
        S = self.symbolic_field
        P = self.consciousness_field
        attraction = self.constants.SYMBOLIC_COUPLING * (P - S)
        diffusion = 0.1 * laplacian2(S)
        self.symbolic_field = S + 0.01 * (attraction + diffusion)
        self.normalize_field(self.symbolic_field)


__all__ = ["UnifiedRealityLaws", "UnifiedRealityKernel"]
