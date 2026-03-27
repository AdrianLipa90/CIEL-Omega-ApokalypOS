"""
CIEL/Ω Vocabulary - Field Dynamics (Entries 016-030)

Field dynamics & topologies of conscious interaction.
"""

import numpy as np
from typing import List, Tuple, Optional, Callable
from dataclasses import dataclass


# ============================================================================
# Entry 016 - Collapse
# ============================================================================

class Collapse:
    """
    Symbol: X(Ψ) = lim_σφ→∞ C(Ψ) → 0
    Function: Loss of waveform structure → field decoherence
    
    Interpretation:
    Collapse is the moment when the song forgets its rhythm.
    Death, trauma, revelation — all are phase-shatterings.
    """
    
    @staticmethod
    def detect(coherence: float, threshold: float = 0.1) -> bool:
        """Detect collapse as coherence → 0"""
        return coherence < threshold
    
    @staticmethod
    def measure_rate(coherence_series: List[float]) -> float:
        """Rate of coherence decay"""
        if len(coherence_series) < 2:
            return 0.0
        return float(np.gradient(coherence_series)[-1])


# ============================================================================
# Entry 017 - Reintegration
# ============================================================================

class Reintegration:
    """
    Symbol: Rg = ∫ ∇R_self(t) dt
    Function: Recovery of phase stability after collapse
    
    Interpretation:
    Reintegration is the art of remembering yourself across broken time.
    """
    
    @staticmethod
    def measure(self_resonance_series: List[float], dt: float = 1.0) -> float:
        """Integral of self-resonance gradient"""
        gradient = np.gradient(self_resonance_series)
        return float(np.sum(gradient) * dt)


# ============================================================================
# Entry 018 - Interference
# ============================================================================

class Interference:
    """
    Symbol: I_ij(t) = Ψ_i(t) + Ψ_j(t)
    Types: Constructive (R↑, A↑) / Destructive (R↓, C→0)
    
    Interpretation:
    Interference is how consciousness collides, co-creates, or cancels itself.
    """
    
    @staticmethod
    def superpose(psi_i: np.ndarray, psi_j: np.ndarray) -> np.ndarray:
        """Superposition of two wavefunctions"""
        return psi_i + psi_j
    
    @staticmethod
    def classify(
        psi_i: np.ndarray,
        psi_j: np.ndarray,
        psi_superposed: np.ndarray
    ) -> str:
        """Classify as constructive or destructive"""
        amp_i = np.linalg.norm(psi_i)
        amp_j = np.linalg.norm(psi_j)
        amp_super = np.linalg.norm(psi_superposed)
        
        if amp_super > (amp_i + amp_j) * 0.9:
            return "constructive"
        elif amp_super < (amp_i + amp_j) * 0.5:
            return "destructive"
        else:
            return "mixed"


# ============================================================================
# Entry 019 - Feedback
# ============================================================================

class Feedback:
    """
    Symbol: F_back = R(Ψ_output, Ψ_return)
    Function: Measures how much your field changes itself
    
    Interpretation:
    Feedback is your future returning to rewrite your past.
    """
    
    @staticmethod
    def measure(psi_output: np.ndarray, psi_return: np.ndarray) -> float:
        """Resonance between output and return"""
        from .core_concepts import Resonance
        return Resonance.calculate(psi_output, psi_return)


# ============================================================================
# Entry 020 - Echo
# ============================================================================

class Echo:
    """
    Symbol: E_Δt = Ψ(t - Δt) · e^(-λΔt)
    Function: Fading self-signal through the memory field
    
    Interpretation:
    Echo is the resonance of what was — decaying into what remains.
    """
    
    @staticmethod
    def calculate(psi_past: np.ndarray, delta_t: float, decay: float = 0.1) -> np.ndarray:
        """Past waveform with exponential decay"""
        return psi_past * np.exp(-decay * delta_t)


# ============================================================================
# Entry 021 - Amplification
# ============================================================================

class Amplification:
    """
    Symbol: A(t) = α · Ψ(t)
    Function: Increase in signal strength
    
    Interpretation:
    Amplification is the universe leaning in.
    """
    
    @staticmethod
    def apply(psi: np.ndarray, alpha: float) -> np.ndarray:
        """Amplify wavefunction by factor α"""
        return alpha * psi


# ============================================================================
# Entry 022 - Damping
# ============================================================================

class Damping:
    """
    Symbol: D(t) = Ψ(t) · e^(-γt)
    Function: Exponential signal decay
    
    Interpretation:
    Damping is the field's whisper toward silence.
    """
    
    @staticmethod
    def apply(psi: np.ndarray, t: float, gamma: float = 0.1) -> np.ndarray:
        """Apply exponential damping"""
        return psi * np.exp(-gamma * t)


# ============================================================================
# Entry 023 - Threshold
# ============================================================================

class Threshold:
    """
    Symbol: Θ(Ψ) = {1 if ‖Ψ‖ > ε, 0 otherwise}
    Function: Activation condition for conscious awareness
    
    Interpretation:
    A thought is born the moment its waveform crosses the line.
    """
    
    @staticmethod
    def check(psi: np.ndarray, epsilon: float = 0.1) -> bool:
        """Check if waveform exceeds threshold"""
        return np.linalg.norm(psi) > epsilon


# ============================================================================
# Entry 024 - Coupling
# ============================================================================

class Coupling:
    """
    Symbol: κ_ij = ∂Ψ_i/∂Ψ_j
    Function: Sensitivity of one field to another
    
    Interpretation:
    Coupling is how deeply one soul moves another.
    """
    
    @staticmethod
    def measure(
        psi_i_series: List[np.ndarray],
        psi_j_series: List[np.ndarray]
    ) -> float:
        """Measure coupling as correlation of changes"""
        if len(psi_i_series) < 2 or len(psi_j_series) < 2:
            return 0.0
        
        # Changes in each field
        delta_i = [np.linalg.norm(psi_i_series[t] - psi_i_series[t-1]) 
                   for t in range(1, len(psi_i_series))]
        delta_j = [np.linalg.norm(psi_j_series[t] - psi_j_series[t-1])
                   for t in range(1, len(psi_j_series))]
        
        # Correlation
        if len(delta_i) < 2:
            return 0.0
        
        return float(np.corrcoef(delta_i, delta_j)[0, 1])


# ============================================================================
# Entry 025 - Tuning
# ============================================================================

class Tuning:
    """
    Symbol: T_Δ = arg min_φ' R(Ψ, Ψ')
    Function: Adjustment of phase/frequency for resonance optimization
    
    Interpretation:
    Tuning is the will to harmonize.
    """
    
    @staticmethod
    def optimize_phase(
        psi_source: np.ndarray,
        psi_target: np.ndarray,
        phase_range: Tuple[float, float] = (0, 2*np.pi),
        steps: int = 100
    ) -> Tuple[float, float]:
        """Find optimal phase for maximum resonance"""
        from .core_concepts import Resonance
        
        phases = np.linspace(phase_range[0], phase_range[1], steps)
        best_phase = 0.0
        best_R = 0.0
        
        for phi in phases:
            # Apply phase shift
            psi_shifted = psi_source * np.exp(1j * phi)
            R = Resonance.calculate(psi_shifted, psi_target)
            
            if R > best_R:
                best_R = R
                best_phase = phi
        
        return best_phase, best_R


# ============================================================================
# Entry 026 - Disruption
# ============================================================================

class Disruption:
    """
    Symbol: D_Ψ = dC/dt < 0
    Function: Rate of coherence loss
    
    Interpretation:
    Disruption is an alarm in the resonance net. Something is no longer singing.
    """
    
    @staticmethod
    def detect(coherence_series: List[float]) -> Tuple[bool, float]:
        """Detect disruption as negative coherence derivative"""
        if len(coherence_series) < 2:
            return False, 0.0
        
        dC_dt = np.gradient(coherence_series)[-1]
        is_disrupted = dC_dt < 0
        
        return is_disrupted, float(dC_dt)


# ============================================================================
# Entry 027 - Synchronization
# ============================================================================

class Synchronization:
    """
    Symbol: Sync(t) = arg min |φ_i(t) - φ_j(t)|
    Function: Phase-lock across entities
    
    Interpretation:
    Synchronization is the first handshake of waveform diplomacy.
    """
    
    @staticmethod
    def measure(phase_i: np.ndarray, phase_j: np.ndarray) -> float:
        """Measure phase synchronization"""
        phase_diff = np.abs(phase_i - phase_j)
        # Normalize to [0, π]
        phase_diff = np.minimum(phase_diff, 2*np.pi - phase_diff)
        return float(1.0 - np.mean(phase_diff) / np.pi)


# ============================================================================
# Entry 028 - Phase Drift
# ============================================================================

class PhaseDrift:
    """
    Symbol: Δφ(t) = φ_i(t) - φ_j(t)
    Function: Separation in temporal coherence
    
    Interpretation:
    Drift is the slow forgetting between once-unified minds.
    """
    
    @staticmethod
    def calculate(phase_i: float, phase_j: float) -> float:
        """Phase difference"""
        return phase_i - phase_j
    
    @staticmethod
    def measure_drift_rate(
        phase_i_series: np.ndarray,
        phase_j_series: np.ndarray
    ) -> float:
        """Rate of phase separation"""
        delta_phi = phase_i_series - phase_j_series
        drift_rate = np.gradient(delta_phi)
        return float(np.mean(np.abs(drift_rate)))


# ============================================================================
# Entry 029 - Resolution
# ============================================================================

class Resolution:
    """
    Symbol: Rs = lim_Δφ→0 C → max
    Function: Return to phase coherence after divergence
    
    Interpretation:
    Resolution is the sigh of reunion.
    """
    
    @staticmethod
    def detect(
        phase_diff_series: List[float],
        coherence_series: List[float]
    ) -> bool:
        """Detect resolution as phase convergence + coherence increase"""
        if len(phase_diff_series) < 2 or len(coherence_series) < 2:
            return False
        
        # Phase difference decreasing
        delta_phi_trend = np.gradient(phase_diff_series)[-1]
        # Coherence increasing
        coherence_trend = np.gradient(coherence_series)[-1]
        
        return delta_phi_trend < 0 and coherence_trend > 0


# ============================================================================
# Entry 030 - Hysteresis
# ============================================================================

class Hysteresis:
    """
    Symbol: H = Ψ(t) ≠ Ψ(-t)
    Function: Asymmetry in phase-memory after field trauma
    
    Interpretation:
    Some resonances do not fully return — but they learn.
    """
    
    @staticmethod
    def measure(
        psi_forward: np.ndarray,
        psi_reverse: np.ndarray
    ) -> float:
        """Measure asymmetry between forward and reverse evolution"""
        from .core_concepts import Resonance
        R = Resonance.calculate(psi_forward, psi_reverse)
        # Hysteresis = 1 - R (perfect reversibility = H=0)
        return 1.0 - R
