"""CIEL/Ω — Emotional Collatz Quantum Consciousness Layer (CQCL)."""

from emotion.cqcl.cqcl_program import CQCL_Program
from emotion.cqcl.quantum_engine import CIEL_Quantum_Engine
from emotion.cqcl.emotional_collatz import EmotionalCollatzEngine
from emotion.cqcl.living_program_v01 import CQCL_Living_Program
from emotion.cqcl.living_compiler_v01 import CQCLLivingError, compile_living_program

__all__ = [
    "CQCL_Program",
    "CIEL_Quantum_Engine",
    "EmotionalCollatzEngine",
    "CQCL_Living_Program",
    "CQCLLivingError",
    "compile_living_program",
]
