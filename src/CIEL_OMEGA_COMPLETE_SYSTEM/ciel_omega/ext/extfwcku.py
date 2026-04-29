"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Test-friendly stub for the spectral wave field module.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import List

# Canonical imports replacing duplicate local definitions
from ciel_wave.fourier_kernel import FourierWaveConsciousnessKernel12D, SpectralWaveField12D
from config.ciel_config import SimConfig

__all__ = ["SpectralWaveField12D", "FourierWaveConsciousnessKernel12D", "SimConfig"]
