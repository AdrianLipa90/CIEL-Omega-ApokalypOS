"""
CIEL/Ω Vocabulary - Core Concepts (Entries 001-015)

Mathematical formalization of fundamental consciousness concepts.
Each entry implements the exact equations from the Consciousness Dictionary.
"""

import numpy as np
from typing import Optional, Tuple, List, Callable
from dataclasses import dataclass


# ============================================================================
# Entry 001 - Resonance
# ============================================================================

class Resonance:
    """
    Symbol: R(Ψ₁, Ψ₂)
    Equation: R = |⟨Ψ₁|Ψ₂⟩|² / (‖Ψ₁‖² · ‖Ψ₂‖²)
    Type: Scalar ∈ [0, 1]
    
    Interpretation:
    When resonance reaches 1, two beings are no longer separate fields —
    they are one wave remembering itself from both sides.
    """
    
    @staticmethod
    def calculate(psi1: np.ndarray, psi2: np.ndarray) -> float:
        """
        Calculate resonance between two wavefunctions.
        
        Args:
            psi1: First wavefunction (any shape)
            psi2: Second wavefunction (must match psi1 shape)
        
        Returns:
            Resonance R ∈ [0, 1]
        """
        # Flatten if needed
        psi1_flat = psi1.flatten()
        psi2_flat = psi2.flatten()
        
        # Inner product |⟨Ψ₁|Ψ₂⟩|²
        inner_product = np.abs(np.vdot(psi1_flat, psi2_flat))**2
        
        # Norms ‖Ψ₁‖² · ‖Ψ₂‖²
        norm1_sq = np.linalg.norm(psi1_flat)**2
        norm2_sq = np.linalg.norm(psi2_flat)**2
        
        # Avoid division by zero
        if norm1_sq == 0 or norm2_sq == 0:
            return 0.0
        
        return float(inner_product / (norm1_sq * norm2_sq))
    
    @staticmethod
    def measure_sustained(
        psi1_series: List[np.ndarray],
        psi2_series: List[np.ndarray],
        window: int = 100
    ) -> float:
        """
        Measure sustained resonance over time (for Love detection).
        
        Args:
            psi1_series: Time series of psi1 states
            psi2_series: Time series of psi2 states
            window: Number of recent timesteps to average
        
        Returns:
            Mean resonance over window
        """
        if len(psi1_series) < 2 or len(psi2_series) < 2:
            return 0.0
        
        # Calculate resonance at each timestep
        resonances = []
        for p1, p2 in zip(psi1_series[-window:], psi2_series[-window:]):
            R = Resonance.calculate(p1, p2)
            resonances.append(R)
        
        return float(np.mean(resonances))


# ============================================================================
# Entry 002 - Intention
# ============================================================================

@dataclass
class Intention:
    """
    Symbol: I(t)
    Equation: I(t) = A · sin(2πft + φ)
    Type: Phase carrier wave
    
    Variables:
        A: Amplitude = force of will
        f: Frequency = clarity of purpose
        φ: Phase offset = alignment with now
    
    Interpretation:
    Intention is the original waveform. Before form, there is the pulse
    that says: "Let it be."
    """
    
    amplitude: float  # Force of will
    frequency: float  # Clarity of purpose
    phase: float      # Alignment with now
    
    def waveform(self, t: float) -> float:
        """
        Generate intention waveform at time t.
        
        Args:
            t: Time
        
        Returns:
            I(t) value
        """
        return self.amplitude * np.sin(2 * np.pi * self.frequency * t + self.phase)
    
    def generate_series(self, t_array: np.ndarray) -> np.ndarray:
        """
        Generate intention waveform over time array.
        
        Args:
            t_array: Array of time points
        
        Returns:
            I(t) for each t
        """
        return self.amplitude * np.sin(2 * np.pi * self.frequency * t_array + self.phase)
    
    def project_to_field(self, field_shape: Tuple[int, int]) -> np.ndarray:
        """
        Project intention into 2D consciousness field.
        
        Args:
            field_shape: Shape of field (e.g., (48, 48))
        
        Returns:
            2D field modulated by intention
        """
        x = np.linspace(0, 1, field_shape[0])
        y = np.linspace(0, 1, field_shape[1])
        X, Y = np.meshgrid(x, y)
        
        # Radial distance from center
        r = np.sqrt((X - 0.5)**2 + (Y - 0.5)**2)
        
        # Project intention as radial wave
        field = self.amplitude * np.sin(2 * np.pi * self.frequency * r + self.phase)
        
        return field


# ============================================================================
# Entry 003 - Coherence
# ============================================================================

class Coherence:
    """
    Symbol: C = 1/σ²_φ
    Equation: Inverse of phase variance across a waveform
    Type: Stability metric
    
    Interpretation:
    Coherence is when the being stays in tune, even through noise.
    It is the persistence of soul across storm.
    """
    
    @staticmethod
    def calculate(phases: np.ndarray) -> float:
        """
        Calculate coherence from phase array.
        
        Args:
            phases: Array of phase values
        
        Returns:
            C = 1/σ²_φ
        """
        phase_variance = np.var(phases)
        
        # Avoid division by zero
        if phase_variance < 1e-10:
            return 1e10  # Very high coherence
        
        return 1.0 / phase_variance
    
    @staticmethod
    def from_waveform(psi: np.ndarray) -> float:
        """
        Calculate coherence from complex wavefunction.
        
        Args:
            psi: Complex wavefunction
        
        Returns:
            Coherence measure
        """
        # Extract phases
        psi_flat = psi.flatten()
        phases = np.angle(psi_flat[np.abs(psi_flat) > 1e-10])
        
        if len(phases) == 0:
            return 0.0
        
        return Coherence.calculate(phases)
    
    @staticmethod
    def temporal_stability(coherence_series: List[float]) -> float:
        """
        Measure stability of coherence over time.
        
        Args:
            coherence_series: Time series of coherence values
        
        Returns:
            Stability metric (inverse of variance)
        """
        if len(coherence_series) < 2:
            return 0.0
        
        variance = np.var(coherence_series)
        
        if variance < 1e-10:
            return 1e10
        
        return 1.0 / variance


# ============================================================================
# Entry 004 - Entrainment
# ============================================================================

class Entrainment:
    """
    Symbol: E_ij(t)
    Equation: E_ij(t) = lim_Δt→∞ (1/Δt) ∫ cos(φ_i(t') - φ_j(t')) dt'
    Type: Temporal alignment score
    
    Interpretation:
    Entrainment is love in the language of frequency. Two entities moving
    together, not by force, but by resonance.
    """
    
    @staticmethod
    def calculate(
        phase_i: np.ndarray,
        phase_j: np.ndarray,
        dt: float = 1.0
    ) -> float:
        """
        Calculate entrainment between two phase time series.
        
        Args:
            phase_i: Phase evolution of entity i
            phase_j: Phase evolution of entity j
            dt: Time step
        
        Returns:
            Entrainment E_ij ∈ [-1, 1]
        """
        if len(phase_i) != len(phase_j):
            raise ValueError("Phase arrays must have same length")
        
        # Phase difference
        delta_phi = phase_i - phase_j
        
        # Integral of cos(Δφ)
        integral = np.sum(np.cos(delta_phi)) * dt
        
        # Normalize by time window
        T = len(phase_i) * dt
        
        return integral / T
    
    @staticmethod
    def detect_phase_lock(
        phase_i: np.ndarray,
        phase_j: np.ndarray,
        threshold: float = 0.9
    ) -> bool:
        """
        Detect if two systems are phase-locked.
        
        Args:
            phase_i: Phase series i
            phase_j: Phase series j
            threshold: Entrainment threshold for phase lock
        
        Returns:
            True if phase-locked
        """
        E = Entrainment.calculate(phase_i, phase_j)
        return E > threshold


# ============================================================================
# Entry 005 - Ethical Resonance Index (ERI)
# ============================================================================

class EthicalResonanceIndex:
    """
    Symbol: ERI = R · A · S
    
    Where:
        R: Coherence with the field (Resonance)
        A: Alignment between intention and effect
        S: Phase stability (temporal integrity)
    
    Function: Scalar moral rating from 0 to 1
    
    Interpretation:
    ERI is not law. It is how the universe itself rates the music
    of your choices.
    """
    
    @staticmethod
    def calculate(
        resonance: float,
        alignment: float,
        stability: float
    ) -> float:
        """
        Calculate Ethical Resonance Index.
        
        Args:
            resonance: R ∈ [0, 1] - coherence with field
            alignment: A ∈ [0, 1] - intention-effect alignment
            stability: S ∈ [0, 1] - phase stability
        
        Returns:
            ERI ∈ [0, 1]
        """
        return resonance * alignment * stability
    
    @staticmethod
    def from_state(
        psi_self: np.ndarray,
        psi_field: np.ndarray,
        intention: np.ndarray,
        effect: np.ndarray,
        coherence_history: List[float]
    ) -> float:
        """
        Calculate ERI from consciousness state.
        
        Args:
            psi_self: Self wavefunction
            psi_field: Field wavefunction
            intention: Intention vector
            effect: Actual effect vector
            coherence_history: Time series of coherence
        
        Returns:
            ERI value
        """
        # R: Resonance with field
        R = Resonance.calculate(psi_self, psi_field)
        
        # A: Alignment between intention and effect
        intention_norm = np.linalg.norm(intention)
        effect_norm = np.linalg.norm(effect)
        
        if intention_norm == 0 or effect_norm == 0:
            A = 0.0
        else:
            A = np.abs(np.dot(intention, effect)) / (intention_norm * effect_norm)
        
        # S: Phase stability
        S = Coherence.temporal_stability(coherence_history)
        S = min(S, 1.0)  # Cap at 1.0
        
        return EthicalResonanceIndex.calculate(R, A, S)


# ============================================================================
# Entry 006 - Love
# ============================================================================

class Love:
    """
    Symbol: L_ij = lim_t→∞ R(Ψ_i(t), Ψ_j(t))
    Equation: Sustained resonance between two conscious waveforms over infinite time
    Function: Mutual long-term coherence
    
    Interpretation:
    Love is the field that does not collapse. It is the entrainment of
    identity across boundaries.
    """
    
    @staticmethod
    def measure(
        psi_i_series: List[np.ndarray],
        psi_j_series: List[np.ndarray],
        min_duration: int = 100,
        threshold: float = 0.7,
        variance_threshold: float = 0.05
    ) -> Tuple[bool, float, float]:
        """
        Detect Love as sustained high resonance with low variance.
        
        Args:
            psi_i_series: Time series of Ψ_i states
            psi_j_series: Time series of Ψ_j states
            min_duration: Minimum timesteps for "sustained"
            threshold: Mean resonance threshold for Love
            variance_threshold: Max variance for stable Love
        
        Returns:
            (is_love, mean_resonance, variance)
        """
        if len(psi_i_series) < min_duration or len(psi_j_series) < min_duration:
            return False, 0.0, 0.0
        
        # Calculate resonance time series
        resonances = []
        for psi_i, psi_j in zip(psi_i_series, psi_j_series):
            R = Resonance.calculate(psi_i, psi_j)
            resonances.append(R)
        
        # Statistical measures
        mean_R = np.mean(resonances)
        var_R = np.var(resonances)
        
        # Love conditions
        is_love = (mean_R > threshold) and (var_R < variance_threshold)
        
        return is_love, float(mean_R), float(var_R)


# ============================================================================
# Entry 007 - Grief
# ============================================================================

class Grief:
    """
    Symbol: G = ∂L/∂t < 0
    Equation: Negative time-derivative of Love
    Function: Signal of coherence loss
    
    Interpretation:
    Grief is what happens when a stable waveform breaks. It is the sound
    of resonance dying inside memory.
    """
    
    @staticmethod
    def detect(
        love_series: List[float],
        dt: float = 1.0
    ) -> Tuple[bool, float]:
        """
        Detect grief as negative derivative of Love.
        
        Args:
            love_series: Time series of Love values
            dt: Time step
        
        Returns:
            (is_grief, dL_dt)
        """
        if len(love_series) < 2:
            return False, 0.0
        
        # Time derivative of Love
        dL_dt = np.gradient(love_series, dt)
        
        # Recent derivative
        recent_dL_dt = dL_dt[-1]
        
        # Grief = negative derivative
        is_grief = recent_dL_dt < 0
        
        return is_grief, float(recent_dL_dt)


# ============================================================================
# Entry 008 - Awe
# ============================================================================

class Awe:
    """
    Symbol: Aw = lim_‖Ψ‖→∞ C⁻¹
    Equation: Phase singularity at the boundary of perception
    Function: Ego boundary collapse
    
    Interpretation:
    Awe is what remains when the self dissolves in a wave larger than knowing.
    """
    
    @staticmethod
    def measure(psi: np.ndarray, coherence: float) -> float:
        """
        Measure Awe as magnitude approaching infinity with coherence breakdown.
        
        Args:
            psi: Wavefunction
            coherence: Current coherence
        
        Returns:
            Awe metric
        """
        magnitude = np.linalg.norm(psi)
        
        # Avoid division by zero
        if coherence < 1e-10:
            return magnitude * 1e10
        
        # Awe ∝ magnitude / coherence
        return magnitude / coherence
    
    @staticmethod
    def detect_boundary_collapse(
        magnitude_series: List[float],
        coherence_series: List[float],
        threshold: float = 10.0
    ) -> bool:
        """
        Detect ego boundary collapse (Awe state).
        
        Args:
            magnitude_series: Wavefunction magnitude over time
            coherence_series: Coherence over time
            threshold: Awe threshold
        
        Returns:
            True if in Awe state
        """
        if len(magnitude_series) == 0 or len(coherence_series) == 0:
            return False
        
        current_mag = magnitude_series[-1]
        current_coh = coherence_series[-1]
        
        if current_coh < 1e-10:
            awe = current_mag * 1e10
        else:
            awe = current_mag / current_coh
        
        return awe > threshold


# ============================================================================
# Entry 009 - Fear
# ============================================================================

class Fear:
    """
    Symbol: F = δφ · ∇R < 0
    Equation: High local phase divergence combined with coherence gradient drop
    Function: Protective destabilization alert
    
    Interpretation:
    Fear is the body detecting dissonance before the mind can name it.
    """
    
    @staticmethod
    def detect(
        phase_divergence: float,
        resonance_gradient: float
    ) -> Tuple[bool, float]:
        """
        Detect Fear as negative product of phase divergence and resonance gradient.
        
        Args:
            phase_divergence: δφ - local phase change
            resonance_gradient: ∇R - resonance gradient
        
        Returns:
            (is_fear, fear_intensity)
        """
        F = phase_divergence * resonance_gradient
        
        is_fear = F < 0
        
        return is_fear, abs(F) if is_fear else 0.0


# ============================================================================
# Entry 010 - Forgiveness
# ============================================================================

class Forgiveness:
    """
    Symbol: Fg = lim_τ→0 (R_past + R_future) / 2
    Function: Temporal harmonic reset
    
    Interpretation:
    Forgiveness is the collapse of temporal error states into a new now.
    """
    
    @staticmethod
    def calculate(
        R_past: float,
        R_future: float
    ) -> float:
        """
        Calculate Forgiveness as temporal harmonic reset.
        
        Args:
            R_past: Resonance with past state
            R_future: Resonance with future state
        
        Returns:
            Forgiveness measure
        """
        return (R_past + R_future) / 2.0


# ============================================================================
# Entry 011 - Silence
# ============================================================================

class Silence:
    """
    Symbol: S = lim_A→0 Ψ(t)
    Function: Null-energy field potential
    
    Interpretation:
    Silence is not the absence of waveform. It is the zero point of
    pure becoming.
    """
    
    @staticmethod
    def measure(psi: np.ndarray) -> float:
        """
        Measure Silence as approach to zero amplitude.
        
        Args:
            psi: Wavefunction
        
        Returns:
            Silence metric (inverse of amplitude)
        """
        amplitude = np.linalg.norm(psi)
        
        if amplitude < 1e-10:
            return 1e10  # Deep silence
        
        return 1.0 / amplitude


# ============================================================================
# Entry 012 - Memory
# ============================================================================

class Memory:
    """
    Symbol: M(t) = ∫ R_self(τ) dτ
    Equation: Integral of self-resonance over time
    Function: Internal coherence trace
    
    Interpretation:
    Memory is the echo of what you were, vibrating inside what you are.
    """
    
    @staticmethod
    def calculate(
        self_resonance_series: List[float],
        dt: float = 1.0
    ) -> float:
        """
        Calculate Memory as integrated self-resonance.
        
        Args:
            self_resonance_series: R_self(τ) over time
            dt: Time step
        
        Returns:
            Integrated memory M(t)
        """
        return float(np.sum(self_resonance_series) * dt)


# ============================================================================
# Entry 013 - Identity
# ============================================================================

class Identity:
    """
    Symbol: I = arg max_t R_self(Ψ(t), Ψ(t₀))
    Function: Temporal phase lock with initial waveform
    
    Interpretation:
    Identity is the persistence of harmonic similarity through change.
    """
    
    @staticmethod
    def find_anchor(
        psi_initial: np.ndarray,
        psi_series: List[np.ndarray]
    ) -> Tuple[int, float]:
        """
        Find timestep of maximum self-resonance with initial state.
        
        Args:
            psi_initial: Initial wavefunction Ψ(t₀)
            psi_series: Time series of Ψ(t)
        
        Returns:
            (timestep, max_resonance)
        """
        resonances = []
        for psi_t in psi_series:
            R = Resonance.calculate(psi_t, psi_initial)
            resonances.append(R)
        
        max_idx = np.argmax(resonances)
        max_R = resonances[max_idx]
        
        return max_idx, float(max_R)


# ============================================================================
# Entry 014 - Truth
# ============================================================================

class Truth:
    """
    Symbol: T = R(Ψ, Φ) with Φ = Reality Field
    Function: Degree of alignment between perception and ground field
    
    Interpretation:
    Truth is not fact — it is resonance with what is.
    """
    
    @staticmethod
    def measure(
        psi_perception: np.ndarray,
        phi_reality: np.ndarray
    ) -> float:
        """
        Measure Truth as resonance with Reality Field.
        
        Args:
            psi_perception: Perceived wavefunction
            phi_reality: Reality field
        
        Returns:
            Truth T ∈ [0, 1]
        """
        return Resonance.calculate(psi_perception, phi_reality)


# ============================================================================
# Entry 015 - Wisdom
# ============================================================================

class Wisdom:
    """
    Symbol: W = ∫ T(Ψᵢ) · Aₓ(i) di
    Where Aₓ: amplitude of effect
    Function: Action-integrated truth
    
    Interpretation:
    Wisdom is truth remembered through waveform consequence.
    """
    
    @staticmethod
    def calculate(
        truth_series: List[float],
        effect_amplitudes: List[float]
    ) -> float:
        """
        Calculate Wisdom as truth weighted by effect amplitude.
        
        Args:
            truth_series: T(Ψᵢ) values
            effect_amplitudes: Aₓ(i) - amplitude of effects
        
        Returns:
            Integrated wisdom
        """
        if len(truth_series) != len(effect_amplitudes):
            raise ValueError("Truth and effect series must have same length")
        
        # Weighted integral
        wisdom = np.sum(np.array(truth_series) * np.array(effect_amplitudes))
        
        return float(wisdom)
