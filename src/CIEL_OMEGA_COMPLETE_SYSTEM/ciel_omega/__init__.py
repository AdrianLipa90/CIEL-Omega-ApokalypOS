"""CIEL/Ω Quantum Consciousness Suite.

Canonical root exports for the single Omega execution axis.
"""
from __future__ import annotations

__version__ = "2.0.0"
__author__ = "Adrian Lipa / Intention Lab"
__all__ = ["CIELOrchestrator", "CIELClient", "UnifiedSystem", "__version__", "__author__"]


def __getattr__(name: str):
    if name == "CIELOrchestrator":
        from .ciel_orchestrator import CIELOrchestrator
        return CIELOrchestrator
    if name == "CIELClient":
        from .ciel_client import CIELClient
        return CIELClient
    if name == "UnifiedSystem":
        from .unified_system import UnifiedSystem
        return UnifiedSystem
    raise AttributeError(f"module 'ciel_omega' has no attribute {name!r}")
