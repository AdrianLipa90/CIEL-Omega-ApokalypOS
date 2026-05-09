"""CIEL/Ω Memory Architecture - M7: Braid/Invariant Memory

Ultra-slow memory layer tracking geometric history, trajectories, and invariants.
Delegates loop execution and scar management to core/braid/BraidRuntime.

τ=120, r=0.15, g=0.92, δ_max=0.03π

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.
"""

from __future__ import annotations

import time
from typing import Any, Optional, Dict, List
import numpy as np
from dataclasses import dataclass, field

from .base import BaseMemoryChannel, PhaseState, CHANNEL_PARAMS

try:
    from ..core.braid.defaults import make_default_runtime
    from ..core.braid.runtime import BraidRuntime
    from ..core.braid.loops import LoopType
    _BRAID_RUNTIME_AVAILABLE = True
except Exception:
    _BRAID_RUNTIME_AVAILABLE = False
    BraidRuntime = None  # type: ignore


@dataclass
class BraidUnit:
    """Single node in braid memory field (geometric history)"""
    
    content: Any           # Stored content
    phase: float          # Phase at time of storage
    weight: float         # Significance weight
    timestamp: float      # When stored
    holonomy: complex     # Accumulated holonomy
    status: str = "open"  # open, closed, scarred
    
    def phasor(self) -> complex:
        """Returns μ * e^(iΦ)"""
        return self.weight * np.exp(1j * self.phase)


class BraidInvariantMemory(BaseMemoryChannel):
    """M7: Slowest, deepest layer of memory system.
    
    Records geometric history of the system:
    - Phase trajectories over long timescales
    - Topological invariants
    - Defects and scars
    - Loop closures and holonomy violations
    
    This is the most inertial channel - requires very long observation
    windows to update, but provides deep insight into system drift.
    
    Already existed as BraidMemory in old repo - this wraps it with
    full phase dynamics integration.
    """
    
    def __init__(self, initial_state: Optional[PhaseState] = None):
        params = CHANNEL_PARAMS[7]  # M7
        super().__init__(params, initial_state)

        # Braid memory storage (BraidUnit for phase-channel layer)
        self.units: List[BraidUnit] = []

        # Trajectory tracking
        self.phase_history: List[float] = []
        self.holonomy_history: List[complex] = []

        # Defect tracking (legacy — also delegated to runtime.scars)
        self.detected_loops: List[Dict] = []
        self.scars: List[Dict] = []

        # Integration window (very long for M7)
        self.integration_window = int(params.tau * 10)  # 1200 steps

        # BraidRuntime — silnik wykonawczy pętli i blizn
        self._runtime: Optional[BraidRuntime] = (
            make_default_runtime() if _BRAID_RUNTIME_AVAILABLE else None
        )
        
    def compute_input_force(self, input_data: Any) -> float:
        """Compute force from input.
        
        M7 barely responds to individual inputs - it integrates over
        very long timescales. Input force is nearly zero unless there's
        sustained directional pressure.
        """
        if len(self.phase_history) < self.integration_window:
            # Not enough history yet
            return 0.0
        
        # Look at trend over integration window
        recent_phases = self.phase_history[-self.integration_window:]
        
        # Compute phase drift rate
        if len(recent_phases) >= 2:
            drift_rate = np.mean(np.diff(recent_phases))
            # Very gentle force proportional to sustained drift
            return 0.01 * drift_rate
        
        return 0.0
    
    def store(self, content: Any, metadata: Optional[Dict] = None) -> None:
        """Store content in braid memory.
        
        Only stores if:
        1. Sufficient time has passed since last storage
        2. Content represents significant geometric change
        3. No conflicting holonomy violation
        """
        metadata = metadata or {}
        
        # Compute holonomy from phase history
        holonomy = self._compute_holonomy()
        
        # Create unit
        unit = BraidUnit(
            content=content,
            phase=self.state.phase,
            weight=self.state.amplitude,
            timestamp=metadata.get('timestamp', len(self.units)),
            holonomy=holonomy,
            status="open"
        )
        
        self.units.append(unit)
        
        # Check for loop closure
        if len(self.units) > 10:
            self._detect_loops()
    
    def retrieve(self, query: Any) -> Any:
        """Retrieve from braid memory.
        
        For M7, retrieval is typically by:
        - Time window
        - Phase region
        - Holonomy signature
        """
        if isinstance(query, dict):
            if 'time_window' in query:
                return self._retrieve_by_time(query['time_window'])
            elif 'phase_region' in query:
                return self._retrieve_by_phase(query['phase_region'])
            elif 'recent' in query:
                n = query['recent']
                return self.units[-n:] if len(self.units) >= n else self.units
        
        # Default: return all
        return self.units
    
    def _retrieve_by_time(self, time_window: tuple) -> List[BraidUnit]:
        """Retrieve units within time window"""
        start, end = time_window
        return [u for u in self.units 
                if start <= u.timestamp <= end]
    
    def _retrieve_by_phase(self, phase_region: tuple) -> List[BraidUnit]:
        """Retrieve units within phase region"""
        phase_min, phase_max = phase_region
        return [u for u in self.units
                if phase_min <= u.phase <= phase_max]
    
    def _compute_holonomy(self) -> complex:
        """Compute accumulated holonomy from phase trajectory.
        
        For closed loop: H = exp(i ∮ A·dr) where A is connection
        Here we use simplified: H = Σ e^(iγ_k)
        """
        if len(self.phase_history) < 10:
            return 1.0 + 0j
        
        # Use last 100 steps or all available
        recent = self.phase_history[-100:]
        holonomy = sum(np.exp(1j * p) for p in recent) / len(recent)
        
        return holonomy
    
    def _detect_loops(self) -> None:
        """Detect loop closures in phase trajectory.
        
        A loop is detected when trajectory returns close to a previous
        phase with similar amplitude, indicating cyclic behavior.
        """
        if len(self.units) < 20:
            return
        
        current_unit = self.units[-1]
        
        # Look for previous units with similar phase
        for i, old_unit in enumerate(self.units[:-20]):
            phase_diff = abs(current_unit.phase - old_unit.phase)
            phase_diff = min(phase_diff, 2*np.pi - phase_diff)
            
            if phase_diff < 0.1:  # Close in phase
                # Check holonomy defect
                holonomy_diff = abs(current_unit.holonomy - old_unit.holonomy)
                
                loop_info = {
                    'start_index': i,
                    'end_index': len(self.units) - 1,
                    'phase_diff': phase_diff,
                    'holonomy_defect': holonomy_diff,
                    'is_closed': holonomy_diff < 0.1,
                }
                
                self.detected_loops.append(loop_info)
                
                # If holonomy defect is large, mark as scar
                if holonomy_diff > 0.5:
                    self._mark_scar(i, len(self.units) - 1, holonomy_diff)
    
    def _mark_scar(self, start_idx: int, end_idx: int, defect: float) -> None:
        """Mark topological scar from failed loop closure"""
        scar = {
            'start': start_idx,
            'end': end_idx,
            'defect': defect,
            'timestamp': len(self.units),
        }
        self.scars.append(scar)
        
        # Mark units in this region
        for i in range(start_idx, min(end_idx + 1, len(self.units))):
            self.units[i].status = "scarred"
    
    def compute_coherence(self) -> float:
        """Compute coherence of braid memory.
        
        C(t) = |Σ μ_i e^(iΦ_i)|
        
        Higher coherence means units are phase-aligned.
        """
        if not self.units:
            return 0.0
        
        total_phasor = sum(u.phasor() for u in self.units)
        return abs(total_phasor) / len(self.units)
    
    def mean_phasor(self) -> complex:
        """Weighted mean phasor of all units"""
        if not self.units:
            return 0 + 0j
        
        total_weight = sum(u.weight for u in self.units)
        if total_weight < 1e-10:
            return 0 + 0j
        
        weighted_sum = sum(u.phasor() for u in self.units)
        return weighted_sum / total_weight
    
    def update_phase_history(self) -> None:
        """Record current phase in trajectory history"""
        self.phase_history.append(self.state.phase)
        
        # Limit history length to avoid unbounded growth
        max_history = self.integration_window * 2
        if len(self.phase_history) > max_history:
            self.phase_history = self.phase_history[-max_history:]
    
    def compute_drift_signature(self) -> Dict:
        """Compute long-term drift signature.
        
        Returns metrics about geometric drift over integration window.
        """
        if len(self.phase_history) < 100:
            return {'status': 'insufficient_history'}
        
        recent = self.phase_history[-self.integration_window:]
        
        # Linear trend
        times = np.arange(len(recent))
        coeffs = np.polyfit(times, recent, 1)
        drift_rate = coeffs[0]
        
        # Variance around trend
        trend = np.polyval(coeffs, times)
        residuals = np.array(recent) - trend
        variance = np.var(residuals)
        
        # Detect periodicity
        fft = np.fft.fft(residuals)
        power = np.abs(fft[:len(fft)//2])**2
        dominant_freq_idx = np.argmax(power[1:]) + 1  # Skip DC
        
        return {
            'status': 'computed',
            'drift_rate': drift_rate,
            'variance': variance,
            'dominant_period': len(recent) / dominant_freq_idx if dominant_freq_idx > 0 else None,
            'num_loops': len(self.detected_loops),
            'num_scars': len(self.scars),
            'coherence': self.compute_coherence(),
        }


    def weave_state(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """Tka węzeł warkoczy z bieżącego stanu systemowego.

        Przyjmuje bogaty snapshot z pipeline (nie tylko kilka liczb).
        Deleguje wykonanie pętli do BraidRuntime.
        Zwraca słowo warkoczy + subconscious_note gotowe do pipeline raportu.

        snapshot powinien zawierać (wszystkie opcjonalne, graceful fallback):
          coherence_index, closure_penalty, system_health, dominant_emotion,
          topological_charge, soul_invariant, identity_phase, cycle_index,
          kuramoto_r (order parameter), htri_coherence
        """
        t_utc = time.time()
        cycle = int(snapshot.get("cycle_index", 0))
        tau_ciel = (t_utc, cycle)

        # Nici warkoczy — cztery wymiary stanu
        phi_system = float(snapshot.get("identity_phase", self.state.phase))
        q_topological = float(snapshot.get("topological_charge", 0.0))
        sigma_soul = float(snapshot.get("soul_invariant", 0.0))
        affect = str(snapshot.get("dominant_emotion", "unknown"))
        coherence = float(snapshot.get("coherence_index", 0.0))
        kuramoto_r = float(snapshot.get("kuramoto_r", 0.0))
        htri = float(snapshot.get("htri_coherence", 0.0))

        # Kontradikcja = odległość od spójności (1 = chaos, 0 = harmonia)
        contradiction = float(np.clip(1.0 - coherence, 0.0, 1.0))

        # Deleguj do BraidRuntime jeśli dostępny
        runtime_result: Dict[str, Any] = {}
        if self._runtime is not None:
            # Aktualizuj fazę runtime z bieżącego stanu
            self._runtime.phase_field.global_phase = phi_system
            loop = self._runtime.submit_intention(
                magnitude=max(sigma_soul, 0.1),
                phase_offset=q_topological,
                domain=affect,
                loop_type=LoopType.LB,
            )
            results = self._runtime.step(max_loops=1)
            if results:
                executed_loop, success = results[0]
                runtime_result = {
                    "loop_id": executed_loop.loop_id,
                    "loop_closed": executed_loop.closed,
                    "glyph": executed_loop.glyph.name,
                    "post_coherence": executed_loop.meta.get("post_C", coherence),
                    "scar_count": len(self._runtime.scars.scars),
                    "scar_residual": self._runtime.scars.residual_curvature(),
                }

        # Słowo warkoczy — formalny zapis splotu nici
        braid_word = (
            f"σ(φ={phi_system:.3f})"
            f"·σ(Q={q_topological:+.3f})"
            f"·σ(Σ={sigma_soul:.3f})"
            f"·σ({affect})"
        )

        # Zapisz jako BraidUnit w warstwie fazowej M7
        holonomy = self._compute_holonomy()
        unit = BraidUnit(
            content={"braid_word": braid_word, "snapshot": snapshot, "runtime": runtime_result},
            phase=phi_system,
            weight=max(coherence, 0.05),
            timestamp=t_utc,
            holonomy=holonomy,
            status="closed" if runtime_result.get("loop_closed") else "open",
        )
        self.units.append(unit)
        self.phase_history.append(phi_system)

        # subconscious_note — fragment gotowy do pipeline raportu
        scar_info = ""
        if runtime_result.get("scar_count", 0) > 0:
            scar_info = f" [{runtime_result['scar_count']} blizn, κ={runtime_result.get('scar_residual', 0):.3f}]"

        note = (
            f"{braid_word} "
            f"| R={kuramoto_r:.3f} htri={htri:.4f} "
            f"| τ=({cycle}){scar_info}"
        )

        return {
            "braid_word": braid_word,
            "subconscious_note": note,
            "tau_ciel": tau_ciel,
            "runtime": runtime_result,
            "unit_count": len(self.units),
        }


__all__ = ['BraidInvariantMemory', 'BraidUnit']
