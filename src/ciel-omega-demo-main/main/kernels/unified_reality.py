from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple

import numpy as np

from ..core.ciel_constants import CIELConstants, DEFAULT_CONSTANTS


ComputeMode = Literal['fft', 'nofft']


@dataclass(frozen=True)
class RealityConstants:
    base: CIELConstants = DEFAULT_CONSTANTS

    def __getattr__(self, name: str):
        return getattr(self.base, name)


class UnifiedRealityLaws:
    def __init__(self, constants: RealityConstants, gradient_fn: Callable[[np.ndarray], List[np.ndarray]]):
        self.C = constants
        self._grad = gradient_fn

    def law_consciousness_quantization(self, field: np.ndarray) -> np.ndarray:
        field_magnitude = np.abs(field)
        quantum_levels = field_magnitude / float(self.C.CONSCIOUSNESS_QUANTUM)
        quantized_levels = np.round(quantum_levels) * float(self.C.CONSCIOUSNESS_QUANTUM)
        return quantized_levels * np.exp(1j * np.angle(field))

    def law_mass_emergence(self, symbolic_field: np.ndarray, consciousness_field: np.ndarray) -> np.ndarray:
        inner_product = np.conj(symbolic_field) * consciousness_field
        resonance = np.abs(inner_product) ** 2 / (
            np.abs(symbolic_field) * np.abs(consciousness_field) + 1e-15
        )

        grad_S = self._grad(symbolic_field)
        grad_P = self._grad(consciousness_field)
        gradient_mismatch = sum(np.abs(gS - gP) ** 2 for gS, gP in zip(grad_S, grad_P))

        mass_squared = (
            float(self.C.SYMBOLIC_COUPLING) * (1.0 - resonance)
            + float(self.C.SYMBOLIC_COUPLING) ** 2 * gradient_mismatch
        )
        return np.sqrt(np.maximum(mass_squared, 0.0))

    def law_temporal_dynamics(self, consciousness_field: np.ndarray) -> Tuple[float, np.ndarray]:
        consciousness_density = np.abs(consciousness_field) ** 2
        grad_P = self._grad(consciousness_field)
        gradient_energy = sum(np.abs(g) ** 2 for g in grad_P)

        time_flow = (
            float(self.C.TEMPORAL_FLOW) * consciousness_density
            + float(self.C.TEMPORAL_FLOW) ** 2 * gradient_energy
        )
        phase_evolution = float(self.C.TEMPORAL_FLOW) * np.angle(consciousness_field)
        return float(np.mean(time_flow)), phase_evolution

    def law_ethical_preservation(self, resonance_field: np.ndarray, consciousness_field: np.ndarray) -> Tuple[np.ndarray, bool]:
        avg_resonance = float(np.mean(resonance_field))
        bound = float(self.C.ETHICAL_BOUND)
        if avg_resonance < bound:
            correction_factor = np.sqrt(bound / max(avg_resonance, 1e-12))
            ethical_phase = 0.1 * (bound - avg_resonance)
            corrected_field = consciousness_field * correction_factor * np.exp(1j * ethical_phase)
            return corrected_field, False
        return consciousness_field, True


class UnifiedRealityKernel:
    def __init__(
        self,
        *,
        constants: CIELConstants = DEFAULT_CONSTANTS,
        grid_size: int = 128,
        compute_mode: ComputeMode = 'nofft',
        length: float = 10.0,
    ) -> None:
        self.constants = RealityConstants(constants)
        self.grid_size = int(grid_size)
        self.compute_mode = compute_mode
        self.length = float(length)

        self._k0: Optional[np.ndarray] = None
        self._k1: Optional[np.ndarray] = None
        if self.compute_mode == 'fft':
            self._k0, self._k1 = self._make_k_grids(self.grid_size, self.length)

        self.laws = UnifiedRealityLaws(self.constants, self._gradients)

        self.consciousness_field: np.ndarray
        self.symbolic_field: np.ndarray
        self.temporal_field: np.ndarray
        self.resonance_field: np.ndarray
        self.mass_field: np.ndarray

        self.initialize_reality_fields()

    def _make_k_grids(self, n: int, length: float) -> Tuple[np.ndarray, np.ndarray]:
        dx = length / float(n)
        k0 = 2.0 * np.pi * np.fft.fftfreq(n, d=dx)
        k1 = 2.0 * np.pi * np.fft.fftfreq(n, d=dx)
        K1, K0 = np.meshgrid(k1, k0)
        return K0.astype(float), K1.astype(float)

    def _gradients(self, field: np.ndarray) -> List[np.ndarray]:
        if self.compute_mode != 'fft':
            grads = np.gradient(field)
            return list(grads)

        if self._k0 is None or self._k1 is None:
            self._k0, self._k1 = self._make_k_grids(self.grid_size, self.length)

        F = np.fft.fft2(field)
        d0 = np.fft.ifft2(1j * self._k0 * F)
        d1 = np.fft.ifft2(1j * self._k1 * F)
        return [d0, d1]

    def initialize_reality_fields(self) -> None:
        n = self.grid_size
        x = np.linspace(-5.0, 5.0, n)
        X, Y = np.meshgrid(x, x)
        r = np.sqrt(X**2 + Y**2)
        envelope = np.exp(-r**2 / 4.0)

        phase = 2j * np.pi * (X + Y)
        self.consciousness_field = envelope * np.exp(phase)
        self.symbolic_field = envelope * np.exp(1j * (X - Y))
        self.temporal_field = np.zeros((n, n), dtype=float)
        self.resonance_field = np.zeros((n, n), dtype=float)
        self.mass_field = np.zeros((n, n), dtype=float)

    def step(self, *, dt: float = 0.1) -> Dict[str, float]:
        _ = dt
        self.consciousness_field = self.laws.law_consciousness_quantization(self.consciousness_field)

        inner = np.conj(self.symbolic_field) * self.consciousness_field
        self.resonance_field = (np.abs(inner) ** 2 / (np.abs(self.symbolic_field) * np.abs(self.consciousness_field) + 1e-15)).real

        self.mass_field = self.laws.law_mass_emergence(self.symbolic_field, self.consciousness_field)

        time_flow, phase_evo = self.laws.law_temporal_dynamics(self.consciousness_field)
        self.temporal_field = (self.temporal_field + phase_evo).astype(float)

        self.consciousness_field, ethical_ok = self.laws.law_ethical_preservation(self.resonance_field, self.consciousness_field)

        return {
            'resonance_mean': float(np.mean(self.resonance_field)),
            'mass_mean': float(np.mean(self.mass_field)),
            'time_flow_mean': float(time_flow),
            'ethical_ok': 1.0 if ethical_ok else 0.0,
        }

    def run(self, *, steps: int = 50) -> Dict[str, Any]:
        last: Dict[str, float] = {}
        for _ in range(int(steps)):
            last = self.step()
        return {'final': last}
