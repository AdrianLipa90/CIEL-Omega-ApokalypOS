"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Runtime configuration dataclasses.

Sources:
  - ext1.CielConfig   — GPU / logging / ethics / dataset params
  - extfwcku.SimConfig — grid / steps / dt for wave simulations
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class CielConfig:
    """Runtime parameters — carried outside code for flexibility."""

    enable_gpu: bool = True
    enable_numba: bool = True
    log_path: str = "logs/reality.jsonl"
    ethics_min_coherence: float = 0.4
    ethics_block_on_violation: bool = True
    dataset_path: Optional[str] = None       # e.g. CVOS_GliphSigils.json
    memory_vendor: str = "repo"              # repo | pro | ultimate
    verbose: bool = False


@dataclass
class SimConfig:
    """Simulation parameters for the Fourier / wave kernels."""

    grid_size: int = 64
    time_steps: int = 200
    dt: float = 0.01
    dimensions: int = 12                     # spectral dimensions (FWCK-12D)


__all__ = ["CielConfig", "SimConfig"]
