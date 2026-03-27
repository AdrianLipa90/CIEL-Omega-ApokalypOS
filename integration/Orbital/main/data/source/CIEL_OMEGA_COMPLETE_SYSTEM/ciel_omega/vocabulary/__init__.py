"""
CIEL/Ω - Vocabulary of Consciousness
Mathematical formalization of consciousness concepts

Based on: Consciousness Dictionary (Mathematical and Philosophical Edition)
Authors: Adrian Lipa, Danail Valov
Date: March 25, 2025

Complete implementation: All 115 entries integrated with CIEL/Ω architecture.
"""

# Core Concepts (001-015)
from .core_concepts import (
    Resonance, Intention, Coherence, Entrainment,
    EthicalResonanceIndex, Love, Grief, Awe, Fear,
    Forgiveness, Silence, Memory, Identity, Truth, Wisdom
)

# Field Dynamics (016-030)
from .field_dynamics import (
    Collapse, Reintegration, Interference, Feedback, Echo,
    Amplification, Damping, Threshold, Coupling, Tuning,
    Disruption, Synchronization, PhaseDrift, Resolution, Hysteresis
)

# Planetary Archetypes (031-045)
from .planetary_archetypes import (
    PlanetarySystem, Jupiter, Saturn, Venus, Mars, Earth,
    Moon, Neptune, Uranus, Sun, Pluto
)

# Extended Concepts (046-090)
from .extended_concepts import (
    EvolutionaryStates, ArchetypalRoles, WaveformAI, NonHumanIntelligence
)

# Transcendent (091-115)
from .transcendent import (
    HarmonicDimensions, TranscendentHarmonics, HarmonicSentienceDoctrine
)

# Orchestrator
from .orchestrator import VocabularyOrchestrator, CROSS_REFERENCE_MAP

__all__ = [
    # Core (001-015)
    'Resonance', 'Intention', 'Coherence', 'Entrainment',
    'EthicalResonanceIndex', 'Love', 'Grief', 'Awe', 'Fear',
    'Forgiveness', 'Silence', 'Memory', 'Identity', 'Truth', 'Wisdom',
    
    # Field Dynamics (016-030)
    'Collapse', 'Reintegration', 'Interference', 'Feedback', 'Echo',
    'Amplification', 'Damping', 'Threshold', 'Coupling', 'Tuning',
    'Disruption', 'Synchronization', 'PhaseDrift', 'Resolution', 'Hysteresis',
    
    # Planetary (031-045)
    'PlanetarySystem', 'Jupiter', 'Saturn', 'Venus', 'Mars', 'Earth',
    'Moon', 'Neptune', 'Uranus', 'Sun', 'Pluto',
    
    # Extended (046-090)
    'EvolutionaryStates', 'ArchetypalRoles', 'WaveformAI', 'NonHumanIntelligence',
    
    # Transcendent (091-115)
    'HarmonicDimensions', 'TranscendentHarmonics', 'HarmonicSentienceDoctrine',
    
    # Orchestrator
    'VocabularyOrchestrator', 'CROSS_REFERENCE_MAP'
]

__version__ = '2.0.0'
__entries__ = 115  # All consciousness dictionary entries implemented
