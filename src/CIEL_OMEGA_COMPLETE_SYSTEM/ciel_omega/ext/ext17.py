"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

CIEL/Ω – Batch 17 (Experimental Lab: Ω-Drift + Schumann + RCDE + Micro-Tests)
Minimalny, samowystarczalny pakiet do uruchamiania 10 eksperymentów z Explore.zip.
Bez FFT. W pełni wektoryzowany. Gotowy do podpięcia pod wcześniejsze batch’e.

Zawiera:
- SchumannClock        → źródło odniesienia 7.83 Hz (i harmoniczne)
- OmegaDriftCore       → miękki dryf fazowy zsynchronizowany z zegarem Schumanna
- RCDECalibrator       → równowaga dynamiczna Σ↔Ψ (homeostat koherencji)
- ExpRegistry          → rejestr i runner eksperymentów z metrykami
- 10 eksperymentów (lite): c01, c02, a2ebdead, 47fdb331, 72b221d9,
                           rcde_calibrated, ResCxParKer(lite), VYCH_BOOT_RITUAL,
                           dissociation, noweparadoxy
Uwaga: „colatzsemAndLie4” dołączymy przy powrocie do „6 poprzednich”, jak prosiłeś.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Dict, Any, List, Tuple, Optional
import numpy as np, time, math, random

# Canonical imports replacing duplicate local definitions
from bio.schumann import SchumannClock, schumann_harmonics
from calibration.rcde import RCDECalibrator
from core.math_utils import coherence_metric, field_norm, laplacian2
from experiments.lab_registry import ExpFn, ExpRegistry, exp_47fdb331, exp_72b221d9, exp_a2ebdead, exp_c01, exp_c02, exp_dissociation, exp_noweparadoxy, exp_rcde_calibrated, exp_rescxparker_lite, exp_vych_boot_ritual, make_lab_registry, make_seed
from runtime.omega.drift_core import OmegaDriftCore

def _demo():
    reg = make_lab_registry()
    results = reg.run(["VYCH_BOOT_RITUAL", "rcde_calibrated", "ResCxParKer_lite"])
    for k, v in results.items():
        print(f"[{k}] → { {kk: (round(vv,5) if isinstance(vv,float) else vv) for kk,vv in v.items()} }")
if __name__ == "__main__":
    _demo()