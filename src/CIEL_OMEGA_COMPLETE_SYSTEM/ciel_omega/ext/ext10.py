"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

CIEL/0 – Batch10 Patch (Cognitive Loop: Perception → Intuition → Prediction → Decision)
Nowe elementy, bez duplikatów i bez FFT:
- PerceptiveLayer      → sensoryczna mapa pól: Percept = Σ * (Re(Ψ) + |Im(Ψ)|)
- IntuitiveCortex      → intuicyjna synteza wejść (entropijne ważenie)
- PredictiveCore       → nieliniowa predykcja (ważona pamięć, bez uczenia)
- DecisionCore         → wybór akcji: score = intent * ethic * confidence
- CognitionOrchestrator→ pętla poznawcza z hookami (pre/post), logi kroków

Kompatybilne z wcześniejszymi patchami (Σ, ColorMap, EEG, Ethics), ale od nich niezależne.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np

# Canonical imports replacing duplicate local definitions
from cognition.decision import DecisionCore
from cognition.intuition import IntuitiveCortex
from cognition.orchestrator import CognitionOrchestrator
from cognition.perception import PerceptiveLayer
from cognition.prediction import PredictiveCore

def _demo():
    # sztuczne pola Ψ i Σ
    n = 64
    x = np.linspace(-2, 2, n); y = np.linspace(-2, 2, n)
    X, Y = np.meshgrid(x, y)
    psi0 = np.exp(-(X**2 + Y**2)) * np.exp(1j * (X + 0.3 * Y))
    sigma0 = np.exp(-(X**2 + Y**2) / 2.0)

    # dostawcy
    def psi_supplier(t: int):
        return psi0 * np.exp(1j * 0.05 * t)

    def sigma_supplier(t: int):
        return np.clip(sigma0 * (0.95 + 0.05 * np.cos(0.1 * t)), 0.0, 1.0)

    def options_supplier(t: int, intuition: float, prediction: float):
        # przykładowe trzy działania: help / wait / risky
        base_ethic = 0.9
        return {
            "help":  {"intent": max(0.0, intuition),           "ethic": base_ethic,     "confidence": 0.7 + 0.2*prediction},
            "wait":  {"intent": 0.4 + 0.3*(1 - abs(intuition)),"ethic": 0.8,            "confidence": 0.6},
            "risky": {"intent": 0.6*prediction,                 "ethic": 0.4 + 0.2*t%2, "confidence": 0.5},
        }

    # instancje
    percept = PerceptiveLayer()
    cortex  = IntuitiveCortex(entropy_map=np.ones(n*n))
    pred    = PredictiveCore(tau=10.0)
    decide  = DecisionCore(min_score=0.2)
    cog     = CognitionOrchestrator(percept, cortex, pred, decide)

    logs = cog.run_cycle(steps=12, psi_supplier=psi_supplier, sigma_supplier=sigma_supplier, options_supplier=options_supplier)
    # zwięzłe podsumowanie
    print("Last 3 steps:")
    for row in logs[-3:]:
        print(f"t={row['t']:02d}  intu={row['intuition']:.3f}  pred={row['prediction']:.3f}  choice={row['decision']}")
if __name__ == "__main__":
    _demo()