"""CQCL Compiler — re-export module.
The compiler is embedded in CIEL_Quantum_Engine.compile_program().
The program dataclass lives in cqcl_program.py.
"""
from emotion.cqcl.cqcl_program import CQCL_Program
from emotion.cqcl.quantum_engine import CIEL_Quantum_Engine as CQCL_Compiler
