# -*- coding: utf-8 -*-
"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

CIEL/0 – Batch7 Patch (part 1)
Zestaw trzech komponentów:
- QuantumResonanceKernel (z ULTIMATE + QR Reality Kernel)
- CIELPhysics (stałe fizyczne)
- CrystalFieldReceiver (odbiornik zewnętrznych sygnałów)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Tuple
import numpy as np

# ===============================================================
# 1️⃣ CIELPhysics – ujednolicone stałe kwantowo-relatywistyczne
# ===============================================================
@dataclass
class CIELPhysics:
    """Fundamentalne stałe i jednostki w systemie CIEL/0."""
    c: float = 299_792_458.0
    hbar: float = 1.054_571_817e-34
    mu0: float = 4e-7 * np.pi
    eps0: float = 8.854_187_8128e-12
    G: float = 6.67430e-11
    Lp: float = 1.616_255e-35
    tp: float = 5.391_247e-44
    mp: float = 2.176_434e-8

    @property
    def planck_energy(self) -> float:
        return self.hbar / self.tp

    @property
    def fine_structure(self) -> float:
        return (1 / (4 * np.pi * self.eps0)) * (self.hbar * self.c) / (self.mp ** 2)

# ===============================================================
# 2️⃣ QuantumResonanceKernel – „Ultimate Quantum Kernel”
# ===============================================================
@dataclass
class QuantumResonanceKernel:
    """Ewolucja rezonansowa pola intencji I(x,t)"""
    physics: CIELPhysics = field(default_factory=CIELPhysics)
    coherence_threshold: float = 0.8

    def resonance(self, S: np.ndarray, I: np.ndarray) -> float:
        """Oblicza rezonans między stanem symbolicznym S a intencją I."""
        inner = np.vdot(S, I)
        return float(np.abs(inner) ** 2)

    def is_coherent(self, resonance: float) -> bool:
        return resonance >= self.coherence_threshold

    def evolve_step(self, psi: np.ndarray, potential: Optional[np.ndarray] = None, dt: float = 0.01) -> np.ndarray:
        """
        Ewoluuje pole Ψ(t) przez prostą iterację Laplasjanu (no-FFT)
        z opcjonalnym potencjałem V(x).
        """
        lap = np.zeros_like(psi, dtype=psi.dtype)
        lap[1:-1, 1:-1] = (
            psi[2:, 1:-1] + psi[:-2, 1:-1] + psi[1:-1, 2:] + psi[1:-1, :-2] - 4 * psi[1:-1, 1:-1]
        )
        next_psi = psi + 1j * dt * lap
        if potential is not None:
            next_psi -= 1j * dt * potential * psi
        norm = np.sqrt(np.mean(np.abs(next_psi) ** 2)) + 1e-12
        return next_psi / norm

    def integrate(self, F: np.ndarray) -> np.ndarray:
        """Numeryczna całka krokowa (trapezowa light)."""
        return np.cumsum(F)

    def field_energy(self, psi: np.ndarray) -> float:
        """Oblicza gęstość energii pola (znormalizowaną)."""
        grad_y = np.zeros_like(psi); grad_x = np.zeros_like(psi)
        grad_y[1:-1, :] = psi[2:, :] - psi[:-2, :]
        grad_x[:, 1:-1] = psi[:, 2:] - psi[:, :-2]
        E = np.mean(np.abs(grad_x) ** 2 + np.abs(grad_y) ** 2)
        return float(E)

    def metrics(self, psi: np.ndarray, ref: np.ndarray) -> Dict[str, float]:
        """Zwraca pakiet metryk: rezonans, energia, fiducja."""
        res = self.resonance(psi, ref)
        energy = self.field_energy(psi)
        fid = float(np.mean(np.abs(np.conj(psi) * ref)))
        return {"resonance": res, "energy": energy, "fidelity": fid}

# ===============================================================
# 3️⃣ CrystalFieldReceiver – adapter zewnętrznych sygnałów
# ===============================================================
@dataclass
class CrystalFieldReceiver:
    """Symulowany odbiornik sygnału pola krystalicznego."""
    geometry: str = "hexagonal-core"
    status: str = field(default="idle", init=False)
    intent_field: Optional[np.ndarray] = field(default=None, init=False)

    def receive(self, signal: np.ndarray) -> Dict[str, Any]:
        """
        Odbiera i dekoduje sygnał wejściowy.
        Zwraca jego podpis (signature) oraz współczynnik koherencji.
        """
        from math import sin, pi
        self.status = "resonating"
        self.intent_field = signal
        encoded = np.array([sin(i * pi / 8) for i in range(16)]) * np.mean(signal)
        coherence = float(np.mean(np.abs(encoded)))
        signature = np.mean(encoded) + 1j * np.std(encoded)
        return {
            "status": self.status,
            "geometry": self.geometry,
            "coherence": round(coherence, 5),
            "signature": signature,
        }

# ===============================================================
# 4️⃣ Mini demo – sanity check
# ===============================================================
def _demo():
    n = 64
    x = np.linspace(-1, 1, n)
    y = np.linspace(-1, 1, n)
    X, Y = np.meshgrid(x, y)
    psi = np.exp(-(X**2 + Y**2)) * np.exp(1j * (X + Y))

    kernel = QuantumResonanceKernel()
    psi2 = kernel.evolve_step(psi)
    M = kernel.metrics(psi2, psi)
    recv = CrystalFieldReceiver()
    sig = recv.receive(np.random.rand(128))

    print("Resonance =", round(M["resonance"], 5))
    print("Energy =", round(M["energy"], 5))
    print("Receiver coherence =", sig["coherence"])

if __name__ == "__main__":
    _demo()

# -*- coding: utf-8 -*-
"""
CIEL/0 – Batch7 Patch (part 2)
Zawiera trzy elementy:
- EEGProcessor  → analiza pasm EEG i koherencji (bio-bridge)
- RealTimeController  → orchestrator kroków i metryk (callbacki)
- VoiceMemoryUI  → prosty terminalowy interfejs pamięci głosowej

Nie powiela kodu z wcześniejszych batchy.
"""

from dataclasses import dataclass, field
from typing import Callable, List, Dict, Any, Optional
import numpy as np
import threading, queue, time

# ===============================================================
# 1️⃣ EEGProcessor – analiza EEG (bez FFT, wektoryzowana)
# ===============================================================
@dataclass
class EEGProcessor:
    fs: float = 256.0  # częstotliwość próbkowania
    bands: Dict[str, tuple] = field(default_factory=lambda: {
        "delta": (0.5, 4.0),
        "theta": (4.0, 8.0),
        "alpha": (8.0, 12.0),
        "beta": (12.0, 30.0),
        "gamma": (30.0, 45.0)
    })
    window_size: int = 256

    def power_band(self, signal: np.ndarray, band: tuple) -> float:
        """Moc pasma przez filtrację różnicową (bez FFT)."""
        low, high = band
        dt = 1.0 / self.fs
        t = np.arange(len(signal)) * dt
        # prosta imitacja pasma – mnożenie przez sinusoide
        f = np.sin(2 * np.pi * ((low + high) / 2) * t)
        return float(np.mean((signal * f) ** 2))

    def analyze(self, signal: np.ndarray) -> Dict[str, float]:
        """Zwraca moce pasm i koherencję między nimi."""
        results = {k: self.power_band(signal, v) for k, v in self.bands.items()}
        vals = np.array(list(results.values()))
        coherence = float(np.mean(vals / (np.max(vals) + 1e-12)))
        results["coherence"] = coherence
        return results

# ===============================================================
# 2️⃣ RealTimeController – orchestrator pętli symulacji
# ===============================================================
@dataclass
class RealTimeController:
    step_fn: Callable[[], Dict[str, float]]
    on_step: Optional[Callable[[int, Dict[str, float]], None]] = None
    interval: float = 0.1
    steps: int = 100
    _running: bool = field(default=False, init=False)
    _thread: Optional[threading.Thread] = field(default=None, init=False)

    def _loop(self):
        for i in range(self.steps):
            if not self._running:
                break
            data = self.step_fn()
            if self.on_step:
                self.on_step(i, data)
            time.sleep(self.interval)
        self._running = False

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)

# ===============================================================
# 3️⃣ VoiceMemoryUI – minimalna wersja terminalowa (bez Kivy)
# ===============================================================
@dataclass
class VoiceMemoryUI:
    """Prosty rejestr głosowo-tekstowy – timeline pamięci."""
    entries: List[Dict[str, Any]] = field(default_factory=list)
    max_entries: int = 100

    def add_entry(self, text: str, mood: str = "neutral"):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        self.entries.append({"time": timestamp, "text": text, "mood": mood})
        if len(self.entries) > self.max_entries:
            self.entries.pop(0)

    def display(self, last_n: int = 5):
        print("\n🧠 Voice Memory Timeline:")
        for e in self.entries[-last_n:]:
            color = {"neutral": "•", "positive": "✦", "negative": "⛒"}.get(e["mood"], "•")
            print(f" {color} [{e['time']}] {e['text']}")

    def export(self) -> List[Dict[str, Any]]:
        return list(self.entries)

# ===============================================================
# 4️⃣ Mini demo – test integracyjny
# ===============================================================
def _demo():
    eeg = EEGProcessor()
    vm = VoiceMemoryUI()

    # generator sygnału EEG-like
    sig = np.sin(2 * np.pi * 10 * np.linspace(0, 1, 256)) + 0.3 * np.random.randn(256)
    print("EEG bands:", eeg.analyze(sig))

    # kontroler – przykładowa pętla
    def fake_step():
        val = np.random.rand()
        vm.add_entry(f"Step value {val:.3f}", mood="positive" if val > 0.5 else "neutral")
        return {"value": val}

    ctl = RealTimeController(step_fn=fake_step, on_step=lambda i, d: print(f"Step {i}: {d}"), steps=5)
    ctl.start()
    ctl._thread.join()
    vm.display()

if __name__ == "__main__":
    _demo()