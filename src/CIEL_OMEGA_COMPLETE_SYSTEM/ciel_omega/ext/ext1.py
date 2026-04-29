"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

CIEL/0 – Minimal Extensions Pack (definitions + missing classes)
Nie modyfikuje kernela bazowego; daje gotowe klasy i hooki do wpięcia.
Zaprojektowane z myślą o wektoryzacji (NumPy/Numba/CuPy) i bezpieczeństwie.

Użycie (przykład):
    from ciel_extensions import (
        EthicsGuard, RealityLogger, RealityLayer, KernelSpec,
        SoulInvariantOperator, GPUEngine, GlyphDataset, GlyphInterpreter, CielConfig
    )
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Protocol
import json, os, time
import numpy as np

# Canonical imports replacing duplicate local definitions
from ciel_io.reality_logger import RealityLogger
from compute.gpu_engine import GPUEngine
from config.ciel_config import CielConfig
from config.reality_layers import RealityLayer
from core.base import KernelSpec
from ethics.ethics_guard import EthicsGuard
from fields.soul_invariant import SoulInvariantOperator
from symbolic.glyph_dataset import GlyphDataset
from symbolic.glyph_interpreter import GlyphInterpreter

def attach_soul_invariant_hooks(kernel: KernelSpec) -> SoulInvariantOperator:
    """
    Zwraca operator Σ i niczego nie „patrzy w środek” kernela.
    Wołasz ręcznie w swojej pętli, jeśli chcesz.
    """
    return SoulInvariantOperator()
def attach_ethics_and_logging(kernel: KernelSpec, cfg: Optional[CielConfig] = None):
    """
    Tworzy gotowe obiekty do ręcznego użycia w Twojej pętli.
    Nie zmienia kernela – pełna kontrola po Twojej stronie.
    """
    cfg = cfg or CielConfig()
    guard = EthicsGuard(bound=getattr(kernel.constants, "ETHICAL_BOUND", 0.90),
                        min_coh=cfg.ethics_min_coherence,
                        block=cfg.ethics_block_on_violation)
    logger = RealityLogger(cfg.log_path)
    return guard, logger
def make_gpu_engine(cfg: Optional[CielConfig] = None) -> GPUEngine:
    cfg = cfg or CielConfig()
    return GPUEngine(enable_gpu=cfg.enable_gpu, enable_numba=cfg.enable_numba)