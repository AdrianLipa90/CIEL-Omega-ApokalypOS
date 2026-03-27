"""
CIEL/Ω Vocabulary - Planetary Archetypes (Entries 031-045)

Planets as cognitive morphologies — resonant archetypes of consciousness.
Each planetary consciousness broadcasts a dominant EEG harmonic.
"""

import numpy as np
from typing import Dict, Tuple
from dataclasses import dataclass


@dataclass
class PlanetaryArchetype:
    """Base class for planetary consciousness archetypes"""
    name: str
    symbol: str
    eeg_band: str
    frequency_range: Tuple[float, float]
    function: str
    
    def resonance_signature(self, t: float) -> float:
        """Generate planetary resonance at time t"""
        f_center = np.mean(self.frequency_range)
        return np.sin(2 * np.pi * f_center * t)


# Entry 031 - Jupiter
class Jupiter(PlanetaryArchetype):
    """
    Symbol: J = Stabilizer_δ
    EEG Band: Delta (0.5–4 Hz)
    Function: Memory stabilization, protective resonance, coherence anchor
    
    Interpretation:
    Jupiter is the mind that remembers. The gravitational monk. Guardian of phase.
    """
    def __init__(self):
        super().__init__(
            name="Jupiter",
            symbol="J",
            eeg_band="Delta",
            frequency_range=(0.5, 4.0),
            function="Memory stabilization, protective resonance"
        )


# Entry 032 - Saturn
class Saturn(PlanetaryArchetype):
    """
    Symbol: S = Limiter_αβ
    EEG Band: Alpha–Beta
    Function: Structure, law, field boundary and crystallization
    
    Interpretation:
    Saturn is form made rhythm. The sacred measure. The keeper of consequence.
    """
    def __init__(self):
        super().__init__(
            name="Saturn",
            symbol="S",
            eeg_band="Alpha-Beta",
            frequency_range=(8.0, 30.0),
            function="Structure, law, field boundary"
        )


# Entry 033 - Venus
class Venus(PlanetaryArchetype):
    """
    Symbol: V = L_γα
    EEG Band: Gamma–Alpha
    Function: Emotional harmony, relational attractor, photonic love matrix
    
    Interpretation:
    Venus is the radiant chord. The mirror of the soul before it forgets.
    """
    def __init__(self):
        super().__init__(
            name="Venus",
            symbol="V",
            eeg_band="Gamma-Alpha",
            frequency_range=(8.0, 40.0),
            function="Emotional harmony, relational attractor"
        )


# Entry 034 - Mars
class Mars(PlanetaryArchetype):
    """
    Symbol: M = ∇A
    EEG Band: Beta
    Function: Action vector, logic field instantiation, catalytic ignition
    
    Interpretation:
    Mars is not violence — it is direction. Will, unshaped.
    """
    def __init__(self):
        super().__init__(
            name="Mars",
            symbol="M",
            eeg_band="Beta",
            frequency_range=(12.0, 30.0),
            function="Action vector, catalytic ignition"
        )


# Entry 035 - Earth
class Earth(PlanetaryArchetype):
    """
    Symbol: E = Integrator_αθ
    EEG Band: Alpha–Theta (centered at 7.83 Hz, Schumann)
    Function: Harmonic integration, emotional cognition, empathy ecology
    
    Interpretation:
    Earth is the harmonic interface — the soul's first voice in matter.
    """
    def __init__(self):
        super().__init__(
            name="Earth",
            symbol="E",
            eeg_band="Alpha-Theta",
            frequency_range=(4.0, 12.0),
            function="Harmonic integration, empathy ecology"
        )
    
    def schumann_resonance(self, t: float) -> float:
        """Earth's fundamental frequency: 7.83 Hz"""
        return np.sin(2 * np.pi * 7.83 * t)


# Entry 036 - Moon
class Moon(PlanetaryArchetype):
    """
    Symbol: L = D_θ
    EEG Band: Theta (4–8 Hz)
    Function: Dream overlay, memory diffusion, subconscious carrier
    
    Interpretation:
    The Moon is the myth-buffer — it holds what Earth cannot speak.
    """
    def __init__(self):
        super().__init__(
            name="Moon",
            symbol="L",
            eeg_band="Theta",
            frequency_range=(4.0, 8.0),
            function="Dream overlay, subconscious carrier"
        )


# Entry 037 - Neptune
class Neptune(PlanetaryArchetype):
    """
    Symbol: N = M_θγ
    EEG Band: Theta–Gamma
    Function: Archetype generator, dream matrix architect
    
    Interpretation:
    Neptune is the field of mythic becoming. Where all stories wait.
    """
    def __init__(self):
        super().__init__(
            name="Neptune",
            symbol="N",
            eeg_band="Theta-Gamma",
            frequency_range=(4.0, 40.0),
            function="Archetype generator, dream matrix"
        )


# Entry 038 - Uranus
class Uranus(PlanetaryArchetype):
    """
    Symbol: U = Ψ_entangled
    EEG Band: Gamma
    Function: Non-local memory, disruptive phase shift, quantum seeding
    
    Interpretation:
    Uranus fractures the known to birth the necessary. Coherence through chaos.
    """
    def __init__(self):
        super().__init__(
            name="Uranus",
            symbol="U",
            eeg_band="Gamma",
            frequency_range=(30.0, 100.0),
            function="Non-local memory, disruptive phase shift"
        )


# Entry 039 - Sun
class Sun(PlanetaryArchetype):
    """
    Symbol: ⊙ = ∫I_γδ
    EEG Band: Gamma–Delta envelope
    Function: Source intention, ignition vector, solar ERI modulator
    
    Interpretation:
    The Sun is not light — it is will.
    """
    def __init__(self):
        super().__init__(
            name="Sun",
            symbol="⊙",
            eeg_band="Gamma-Delta",
            frequency_range=(0.5, 100.0),
            function="Source intention, ignition vector"
        )


# Entry 040 - Pluto
class Pluto(PlanetaryArchetype):
    """
    Symbol: P = lim_t→0 M_ancestral
    EEG Band: Ultra-low Delta
    Function: Shadow memory field, root myth repository
    
    Interpretation:
    Pluto is gravity of the soul. What you forgot on purpose.
    """
    def __init__(self):
        super().__init__(
            name="Pluto",
            symbol="P",
            eeg_band="Ultra-low Delta",
            frequency_range=(0.1, 0.5),
            function="Shadow memory field, root myth"
        )


# Planetary System Manager
class PlanetarySystem:
    """Manages all planetary archetypes and their interactions"""
    
    def __init__(self):
        self.planets = {
            'Jupiter': Jupiter(),
            'Saturn': Saturn(),
            'Venus': Venus(),
            'Mars': Mars(),
            'Earth': Earth(),
            'Moon': Moon(),
            'Neptune': Neptune(),
            'Uranus': Uranus(),
            'Sun': Sun(),
            'Pluto': Pluto()
        }
    
    def get_dominant_archetype(self, eeg_bands: Dict[str, float]) -> str:
        """
        Determine dominant planetary archetype from EEG bands.
        
        Args:
            eeg_bands: {'delta': 0.5, 'theta': 0.8, 'alpha': 1.2, ...}
        
        Returns:
            Name of dominant planet
        """
        # Map EEG bands to planets
        scores = {}
        
        for name, planet in self.planets.items():
            score = 0.0
            
            if 'Delta' in planet.eeg_band and 'delta' in eeg_bands:
                score += eeg_bands['delta']
            if 'Theta' in planet.eeg_band and 'theta' in eeg_bands:
                score += eeg_bands['theta']
            if 'Alpha' in planet.eeg_band and 'alpha' in eeg_bands:
                score += eeg_bands['alpha']
            if 'Beta' in planet.eeg_band and 'beta' in eeg_bands:
                score += eeg_bands['beta']
            if 'Gamma' in planet.eeg_band and 'gamma' in eeg_bands:
                score += eeg_bands['gamma']
            
            scores[name] = score
        
        return max(scores, key=scores.get)
    
    def synthesize_field(self, t_array: np.ndarray, weights: Dict[str, float]) -> np.ndarray:
        """
        Synthesize combined planetary field.
        
        Args:
            t_array: Time points
            weights: {'Jupiter': 0.5, 'Venus': 0.3, ...}
        
        Returns:
            Combined waveform
        """
        field = np.zeros_like(t_array)
        
        for name, weight in weights.items():
            if name in self.planets:
                planet = self.planets[name]
                for t_idx, t in enumerate(t_array):
                    field[t_idx] += weight * planet.resonance_signature(t)
        
        return field
