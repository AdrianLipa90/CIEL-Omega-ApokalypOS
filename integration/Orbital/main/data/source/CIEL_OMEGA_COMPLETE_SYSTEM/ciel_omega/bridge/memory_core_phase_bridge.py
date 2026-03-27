
"""Phase-aware bridge between core physics, memory, vocabulary, and semantic closure layers."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, Optional
import math
import numpy as np

# Optional canonical runtime imports; fall back to local mini-runtime if absent.
try:
    from ..core.physics.ciel0_framework import CIEL0Framework, CIELParameters  # type: ignore
except Exception:
    class CIELParameters:
        def __init__(self):
            self.lambda_1 = 0.05
            self.lambda_3 = 0.05

    class CIEL0Framework:
        def __init__(self, params: Any, grid_size: int = 24):
            self.params = params
            self.grid_size = grid_size
            self.I_field = np.ones((grid_size,), dtype=np.complex128)
            self.S_field = np.exp(1j * np.linspace(0, 2*np.pi, grid_size, endpoint=False))
            self.tau_field = np.zeros((grid_size,), dtype=float)
            self.Lambda0_field = np.zeros((grid_size,), dtype=float)
            self.R_field = np.ones((grid_size,), dtype=float)
            self.mass_field = np.ones((grid_size,), dtype=float)

        def initialize_gaussian_pulse(self) -> None:
            x = np.linspace(-1.0, 1.0, self.grid_size)
            amp = np.exp(-6.0 * x*x)
            self.I_field = amp * np.exp(1j * 0.2 * x)
            self.S_field = amp * np.exp(1j * 0.4 * x)
            self.tau_field = 0.1 * np.sin(np.pi * x)
            self.Lambda0_field = 0.1 * np.cos(np.pi * x)
            self.R_field = amp
            self.mass_field = 1.0 + 0.1 * amp

        def evolution_step(self, dt: float = 0.05) -> None:
            phase_pull = np.exp(1j * dt * (self.params.lambda_1 + self.params.lambda_3))
            self.I_field *= phase_pull
            self.S_field *= np.exp(1j * dt * 0.5)
            self.tau_field += dt * np.sin(np.angle(np.mean(self.I_field)) - self.tau_field)
            self.Lambda0_field += dt * 0.1 * np.tanh(self.tau_field)
            self.R_field = np.abs(self.I_field)
            self.mass_field = 1.0 + 0.1 * np.abs(self.S_field)

try:
    from ..memory.orchestrator import HolonomicMemoryOrchestrator  # type: ignore
except Exception:
    class _MiniDynamics:
        @staticmethod
        def compute_stability_metrics(state: Any) -> Dict[str, float]:
            phases = np.asarray(state.phases, dtype=float)
            if phases.size == 0:
                return {'mean_coherence': 1.0}
            return {'mean_coherence': float(abs(np.mean(np.exp(1j * phases))))}

    class HolonomicMemoryOrchestrator:
        def __init__(self, identity_phase: float = 0.0):
            self.state = SimpleNamespace(phases=[identity_phase, identity_phase + 0.7, identity_phase + 1.3])
            self.identity_field = SimpleNamespace(phase=float(identity_phase))
            self.dynamics = _MiniDynamics()
            self._cycle = 0

        def process_input(self, text: str, metadata: Optional[Dict[str, Any]] = None, dt: float = 0.1):
            metadata = metadata or {}
            bump = 0.1 * float(metadata.get('salience', 0.5))
            self.state.phases = [float((p + bump + i * 0.03) % (2*np.pi)) for i, p in enumerate(self.state.phases)]
            self.identity_field.phase = float((self.identity_field.phase + 0.5*bump) % (2*np.pi))
            self._cycle += 1
            return SimpleNamespace(semantic_key=text.strip().lower().replace(' ', '_')[:64], cycle_index=self._cycle)

try:
    from ..vocabulary import VocabularyOrchestrator  # type: ignore
except Exception:
    class VocabularyOrchestrator:
        def integrate_with_layer_2_fields(self, I_field: Any, sigma: float = 1.0) -> Dict[str, Any]:
            phase = float(np.angle(np.mean(np.asarray(I_field))))
            return {'semantic_key': f'sigma_{sigma:.3f}', 'phase_proxy': phase, 'sigma': sigma}

from ..constraints.euler_constraint import evaluate_unified_euler_constraint, apply_active_euler_feedback
from ..vocabulary_tools.resolver import VocabularyResolver
from ..vocabulary_tools.symbol_extractor import extract_symbols


@dataclass
class UnifiedCycleResult:
    input_text: str
    memory_semantic_key: str
    memory_cycle_index: int
    core_metrics: Dict[str, float]
    vocabulary_metrics: Dict[str, Any]
    euler_metrics: Dict[str, Any]


class MemoryCorePhaseBridge:
    """Small runtime integrator for the merged canonical subsystems."""

    def __init__(self, identity_phase: float = 0.0, grid_size: int = 24):
        self.memory = HolonomicMemoryOrchestrator(identity_phase=identity_phase)
        self.core = CIEL0Framework(CIELParameters(), grid_size=grid_size)
        self.core.initialize_gaussian_pulse()
        self.vocabulary = VocabularyOrchestrator()
        self.vocab_resolver = VocabularyResolver(Path(__file__).resolve().parents[1] / 'vocabulary.yaml')

    @staticmethod
    def _wrap(phi: float) -> float:
        return float(phi % (2.0 * math.pi))

    def _memory_to_core(self) -> None:
        phase = float(self.memory.identity_field.phase)
        mean_coh = float(self.memory.dynamics.compute_stability_metrics(self.memory.state).get('mean_coherence', 0.0))
        self.core.params.lambda_1 = float(np.clip(0.05 + 0.30 * mean_coh, 0.01, 0.60))
        self.core.params.lambda_3 = float(np.clip(0.05 + 0.45 * (1.0 - abs(math.sin(phase))), 0.01, 0.60))
        i_abs = np.abs(self.core.I_field)
        self.core.I_field = i_abs * np.exp(1j * (np.angle(self.core.I_field) + 0.25 * phase))
        self.core.tau_field = self.core.tau_field + 0.1 * np.sin(phase - self.core.tau_field)

    @staticmethod
    def _build_eba_results(memory: Any, target_phase: float | None = None) -> Dict[str, Any]:
        phases = np.asarray(memory.state.phases, dtype=float)
        if target_phase is None:
            target_phase = float(np.angle(np.mean(np.exp(1j * phases)))) if phases.size else 0.0
        out = {}
        for i, p in enumerate(phases):
            defect = abs(math.atan2(math.sin(p - target_phase), math.cos(p - target_phase)))
            out[f'm{i}'] = {'defect_magnitude': defect, 'is_coherent': defect < 0.35}
        return out

    def compute_white_thread_amplitude(self, psi_i: complex, psi_j: complex) -> float:
        return float(abs(np.conjugate(psi_j) * psi_i))

    def step(self, text: str, metadata: Optional[Dict[str, Any]] = None, core_steps: int = 4, dt: float = 0.05) -> UnifiedCycleResult:
        metadata = metadata or {}
        cycle = self.memory.process_input(text, metadata=metadata, dt=0.1)
        self._memory_to_core()
        for _ in range(core_steps):
            self.core.evolution_step(dt=dt)
        core_metrics = {
            'resonance_mean': float(np.mean(np.asarray(self.core.R_field))),
            'mass_mean': float(np.mean(np.asarray(self.core.mass_field))),
            'intention_mean': float(np.mean(np.abs(np.asarray(self.core.I_field)))),
            'tau_mean': float(np.mean(np.asarray(self.core.tau_field))),
            'phase_mean': float(np.angle(np.mean(np.exp(1j * np.angle(np.asarray(self.core.I_field)))))),
        }
        sigma_source = getattr(self.core, 'Sigma_field', None)
        sigma_value = float(np.mean(np.asarray(sigma_source))) if sigma_source is not None else float(np.std(np.asarray(self.core.tau_field)))
        vocab_metrics = self.vocabulary.integrate_with_layer_2_fields(self.core.I_field, sigma=sigma_value)

        extracted = extract_symbols(text, self.vocab_resolver)
        semantic_records = []
        for item in extracted:
            resolved = self.vocab_resolver.try_resolve(item.surface)
            if resolved is not None:
                rec = dict(resolved.record)
                rec['canonical_id'] = resolved.canonical_id
                semantic_records.append(rec)

        eba_before = self._build_eba_results(self.memory)
        report_before = evaluate_unified_euler_constraint(
            self.memory,
            self.core,
            eba_before,
            semantic_records=semantic_records,
            vocabulary_metrics=vocab_metrics,
            metadata=metadata,
        )
        report_after, rolled_back = apply_active_euler_feedback(
            self.memory,
            self.core,
            report_before,
            semantic_records=semantic_records,
            vocabulary_metrics=vocab_metrics,
            metadata=metadata,
        )
        euler_metrics = {
            'before_unified_euler_violation': report_before.unified_euler_violation,
            'after_unified_euler_violation': report_after.unified_euler_violation,
            'closure_score': report_after.closure_score,
            'target_phase': report_after.target_phase,
            'regulation_strength': report_after.regulation_strength,
            'rolled_back': rolled_back,
            'sector_euler_violation': report_after.sector_euler_violation,
            'sector_phase_sector': report_after.sector_phase_sector,
            'pairwise_phase_tension': report_after.pairwise_phase_tension,
            'semantic_symbols': [r['canonical_id'] for r in semantic_records],
        }
        return UnifiedCycleResult(
            input_text=text,
            memory_semantic_key=cycle.semantic_key,
            memory_cycle_index=cycle.cycle_index,
            core_metrics=core_metrics,
            vocabulary_metrics=vocab_metrics,
            euler_metrics=euler_metrics,
        )
