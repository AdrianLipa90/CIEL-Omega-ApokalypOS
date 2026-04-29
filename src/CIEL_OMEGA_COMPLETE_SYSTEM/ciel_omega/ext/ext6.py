"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.
"""
from __future__ import annotations

# Canonical imports replacing duplicate local definitions
from core.physics.reality_expander import RealityExpander
from fields.psych_field import PsychField
from fields.unified_sigma_field import UnifiedSigmaField

"""
CIEL/0 – Batch6 Patch (no-FFT, only NEW pieces)
Dodaje wyłącznie brakujące elementy z Batch 6:
- RealityExpander: wektorowy „rozrost rzeczywistości” (dyfuzja nieliniowa)
- UnifiedSigmaField: żywe Σ(x,t) (czasoprzestrzenny niezmiennik duszy)
- PsychField: empatyczna interakcja pól (rezonans między-systemowy)

Nie dubluje niczego z wcześniejszych patchy.
"""
from dataclasses import dataclass, field
from typing import Optional, Tuple
import numpy as np
def _demo():
    n = 96
    x = np.linspace(-2, 2, n); y = np.linspace(-2, 2, n)
    X, Y = np.meshgrid(x, y)
    seed = np.exp(-(X**2 + Y**2)) * np.exp(1j * (X + 0.3 * Y))

    # RealityExpander
    rex = RealityExpander(alpha=0.7, kappa=0.1, steps=12)
    psi_expanded = rex.expand(seed)

    # UnifiedSigmaField
    usf = UnifiedSigmaField(shape=(n, n), omega=0.9, damping=0.03, dt=0.04)
    fields, scal = usf.evolve(T=32)

    # PsychField
    pf = PsychField(empathy=0.65, phase_lock=0.25)
    C = pf.interact(seed, psi_expanded)

    print("Expanded field norm:", float(np.sqrt(np.mean(np.abs(psi_expanded)**2))))
    print("UnifiedSigmaField last Σ:", f"{scal[-1]:.4f}")
    print("PsychField mix norm:", float(np.sqrt(np.mean(np.abs(C)**2))))
if __name__ == "__main__":
    _demo()