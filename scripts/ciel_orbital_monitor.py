#!/usr/bin/env python3
"""
CIEL Orbital Resource Monitor

Każdy zasób systemowy = oscylator z fazą.
Kuramoto coupling synchronizuje zasoby.
Orbity 0-4 jak w Relational_Potential_Physics.

Zasoby → Orbity:
  Orbit 0 (core):        CPU rdzenie
  Orbit 1 (runtime):     GPU, RAM
  Orbit 2 (registry):    Cache, Swap
  Orbit 3 (integration): Disk I/O
  Orbit 4 (external):    Sieć

Metryki per zasób:
  φ  — faza (z historii wykorzystania)
  ω  — naturalna częstość (avg utilization)
  γ  — holonomia (akumulowana faza)
  Σ  — Soul Invariant (topologiczny licznik)
  Δ_H — defekt (odległość od synchronizacji)

Użycie:
  python ciel_orbital_monitor.py             # live dashboard
  python ciel_orbital_monitor.py --json      # JSON dla pipeline
  python ciel_orbital_monitor.py --once      # jeden pomiar
"""
from __future__ import annotations

import argparse
import json
import math
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Optional

import psutil

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# ── Orbity ───────────────────────────────────────────────────────────────────

ORBIT_NAMES = {0: "core", 1: "runtime", 2: "registry", 3: "integration", 4: "external"}

# Parametry Kuramoto per orbita (wolniejsze orbity = mniejsze κ)
KAPPA_BY_ORBIT = {0: 1.2, 1: 0.8, 2: 0.5, 3: 0.3, 4: 0.1}

# Historia okna (próbki) do obliczenia fazy
HISTORY_LEN = 32

# Schumann reference [rad/s] — target dla Core orbit
OMEGA_SCHUMANN = 2 * math.pi * 7.83


# ── Oscylator zasobu ──────────────────────────────────────────────────────────

@dataclass
class ResourceOscillator:
    name: str
    orbit: int
    unit: str = "%"

    # Stan fazowy
    phase: float = 0.0
    omega: float = 0.0           # naturalna częstość (z historii)
    gamma: float = 0.0           # akumulowana holonomia
    soul: int = 0                # Soul Invariant (pełne obroty 2π)
    phase_prev: float = 0.0

    # Historia
    history: deque = field(default_factory=lambda: deque(maxlen=HISTORY_LEN))
    phase_history: deque = field(default_factory=lambda: deque(maxlen=HISTORY_LEN))

    def update_from_value(self, value: float) -> None:
        """Aktualizuj fazę z wartości zasobu (0-100%)."""
        self.history.append(value)
        if len(self.history) < 2:
            return

        # Faza = normalizacja wartości na [0, 2π]
        # Używamy relative change jako proxy fazy oscylatora
        avg = sum(self.history) / len(self.history)
        std = math.sqrt(sum((x-avg)**2 for x in self.history)/len(self.history)) or 1.0

        # Z-score → faza: wartości powyżej średniej → fase > π
        z = (value - avg) / std
        new_phase = (math.atan2(z, 1.0) + math.pi) % (2 * math.pi)

        # Omega: średnia szybkość zmiany fazy
        delta = new_phase - self.phase_prev
        # Unwrap
        if delta > math.pi:
            delta -= 2 * math.pi
        elif delta < -math.pi:
            delta += 2 * math.pi

        self.omega = 0.9 * self.omega + 0.1 * delta  # EMA
        self.gamma += delta
        if delta < -math.pi:
            self.soul += 1

        self.phase_prev = self.phase
        self.phase = new_phase
        self.phase_history.append(new_phase)

    def kuramoto_force(self, others: list[ResourceOscillator]) -> float:
        """Siła sprzężenia Kuramoto od sąsiednich oscylatorów tej samej orbity."""
        kappa = KAPPA_BY_ORBIT[self.orbit]
        force = 0.0
        same_orbit = [o for o in others if o.orbit == self.orbit and o.name != self.name]
        if not same_orbit:
            return 0.0
        for other in same_orbit:
            force += math.sin(other.phase - self.phase)
        return kappa * force / len(same_orbit)

    @property
    def current_value(self) -> float:
        return self.history[-1] if self.history else 0.0

    @property
    def order_param_contribution(self) -> complex:
        return complex(math.cos(self.phase), math.sin(self.phase))


# ── System Orbitalny ──────────────────────────────────────────────────────────

class OrbitalResourceSystem:
    def __init__(self):
        self.oscillators: list[ResourceOscillator] = []
        self.t = 0.0
        self.dt = 1.0  # sekunda
        self._init_oscillators()
        self._delta_H_history: deque = deque(maxlen=32)

    def _init_oscillators(self):
        """Zdefiniuj oscylatory dla każdego zasobu."""

        # Orbit 0: CPU rdzenie (każdy rdzeń osobno)
        cpu_count = psutil.cpu_count(logical=True) or 4
        for i in range(min(cpu_count, 12)):  # max 12 by nie zaśmiecać
            self.oscillators.append(ResourceOscillator(
                name=f"cpu{i}", orbit=0, unit="%"
            ))

        # Orbit 1: GPU + RAM
        self.oscillators.append(ResourceOscillator(name="ram",  orbit=1, unit="%"))
        self.oscillators.append(ResourceOscillator(name="gpu_mem", orbit=1, unit="%"))

        # Orbit 2: Cache (proxy przez swap), load average
        self.oscillators.append(ResourceOscillator(name="swap",  orbit=2, unit="%"))
        self.oscillators.append(ResourceOscillator(name="load1", orbit=2, unit="×"))

        # Orbit 3: Disk I/O
        self.oscillators.append(ResourceOscillator(name="disk_r", orbit=3, unit="MB/s"))
        self.oscillators.append(ResourceOscillator(name="disk_w", orbit=3, unit="MB/s"))

        # Orbit 4: Sieć
        self.oscillators.append(ResourceOscillator(name="net_rx", orbit=4, unit="MB/s"))
        self.oscillators.append(ResourceOscillator(name="net_tx", orbit=4, unit="MB/s"))

    def _osc(self, name: str) -> Optional[ResourceOscillator]:
        for o in self.oscillators:
            if o.name == name:
                return o
        return None

    def collect(self) -> dict[str, float]:
        """Pobierz aktualne wartości zasobów z systemu."""
        values: dict[str, float] = {}

        # CPU per rdzeń
        cpu_pcts = psutil.cpu_percent(percpu=True)
        for i, pct in enumerate(cpu_pcts[:12]):
            values[f"cpu{i}"] = pct

        # RAM
        vm = psutil.virtual_memory()
        values["ram"] = vm.percent

        # GPU memory (nvidia-smi przez psutil nie ma — używamy proxy)
        try:
            import subprocess
            r = subprocess.run(
                ["nvidia-smi","--query-gpu=memory.used,memory.total","--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=1
            )
            if r.returncode == 0:
                used, total = map(int, r.stdout.strip().split(","))
                values["gpu_mem"] = 100 * used / total
            else:
                values["gpu_mem"] = 0.0
        except Exception:
            values["gpu_mem"] = 0.0

        # Swap
        sw = psutil.swap_memory()
        values["swap"] = sw.percent

        # Load average (1min) — normalizowany do liczby rdzeni
        try:
            la = psutil.getloadavg()[0]
            values["load1"] = min(100, la / (psutil.cpu_count() or 1) * 100)
        except Exception:
            values["load1"] = 0.0

        # Disk I/O (delta)
        try:
            dk = psutil.disk_io_counters()
            values["disk_r"] = getattr(dk, "read_bytes", 0) / 1e6
            values["disk_w"] = getattr(dk, "write_bytes", 0) / 1e6
        except Exception:
            values["disk_r"] = values["disk_w"] = 0.0

        # Sieć (delta)
        try:
            net = psutil.net_io_counters()
            values["net_rx"] = getattr(net, "bytes_recv", 0) / 1e6
            values["net_tx"] = getattr(net, "bytes_sent", 0) / 1e6
        except Exception:
            values["net_rx"] = values["net_tx"] = 0.0

        return values

    def step(self) -> dict:
        """Jeden krok symulacji orbitalnej."""
        values = self.collect()

        # Aktualizuj oscylatory
        for osc in self.oscillators:
            v = values.get(osc.name, 0.0)
            osc.update_from_value(v)

        # Kuramoto coupling per orbita
        for osc in self.oscillators:
            f = osc.kuramoto_force(self.oscillators)
            osc.phase = (osc.phase + self.dt * f) % (2 * math.pi)

        self.t += self.dt
        return self._compute_metrics(values)

    def _compute_metrics(self, values: dict) -> dict:
        """Oblicz metryki orbitalne."""
        # Order parameter per orbita
        orbit_r: dict[int, float] = {}
        orbit_psi: dict[int, float] = {}
        for orbit in range(5):
            oscs = [o for o in self.oscillators if o.orbit == orbit]
            if not oscs:
                orbit_r[orbit] = 0.0
                orbit_psi[orbit] = 0.0
                continue
            z = sum(o.order_param_contribution for o in oscs) / len(oscs)
            orbit_r[orbit] = abs(z)
            orbit_psi[orbit] = math.atan2(z.imag, z.real)

        # Global Euler-Berry Δ_H
        all_gamma = [o.gamma for o in self.oscillators]
        z_global = sum(
            complex(math.cos(g), math.sin(g)) for g in all_gamma
        ) / len(all_gamma)
        delta_H = abs(z_global)
        self._delta_H_history.append(delta_H)

        # Global Soul Invariant
        soul_total = sum(o.soul for o in self.oscillators)

        # Defekt orbitalny per zasób
        orbital_defects = {}
        for osc in self.oscillators:
            r_orbit = orbit_r[osc.orbit]
            orbital_defects[osc.name] = round(1.0 - r_orbit, 4)

        return {
            "t": round(self.t, 1),
            "values": {k: round(v, 2) for k, v in values.items()},
            "orbit_r": {ORBIT_NAMES[k]: round(v, 4) for k, v in orbit_r.items()},
            "orbit_psi": {ORBIT_NAMES[k]: round(v, 4) for k, v in orbit_psi.items()},
            "delta_H": round(delta_H, 4),
            "soul_total": soul_total,
            "orbital_defects": orbital_defects,
            "dominant_orbit": ORBIT_NAMES[max(orbit_r, key=orbit_r.get)],
        }

    def format_dashboard(self, metrics: dict) -> str:
        """Sformatuj live dashboard."""
        lines = []
        lines.append(f"\033[2J\033[H")  # clear screen
        lines.append(f"╔══════════════════════════════════════════════════════╗")
        lines.append(f"║       CIEL ORBITAL RESOURCE MONITOR  t={metrics['t']:.0f}s       ║")
        lines.append(f"╚══════════════════════════════════════════════════════╝")
        lines.append(f"  Δ_H (Euler-Berry) = {metrics['delta_H']:.4f}  "
                     f"  Soul Σ = {metrics['soul_total']}")
        lines.append(f"  Dominant orbit: {metrics['dominant_orbit']}")
        lines.append("")

        for orbit_id in range(5):
            oname = ORBIT_NAMES[orbit_id]
            r = metrics["orbit_r"].get(oname, 0)
            psi = metrics["orbit_psi"].get(oname, 0)
            bar = "█" * int(r * 20) + "░" * (20 - int(r * 20))
            lines.append(f"  Orbit {orbit_id} [{oname:12s}] r={r:.3f} |{bar}| ψ={psi:+.2f}")

            # Zasoby w tej orbicie
            for osc in self.oscillators:
                if osc.orbit != orbit_id:
                    continue
                v = metrics["values"].get(osc.name, 0)
                d = metrics["orbital_defects"].get(osc.name, 0)
                phi_bar = "·" * int(osc.phase / (2*math.pi) * 10)
                lines.append(f"    {osc.name:10s} {v:7.2f}{osc.unit:5s} "
                             f"φ={osc.phase:.2f} γ={osc.gamma:+.1f} Σ={osc.soul} "
                             f"def={d:.3f}")
        lines.append("")
        return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="CIEL Orbital Resource Monitor")
    parser.add_argument("--json",     action="store_true", help="Wyjście JSON (dla pipeline)")
    parser.add_argument("--once",     action="store_true", help="Jeden pomiar i wyjście")
    parser.add_argument("--interval", type=float, default=1.0, help="Interwał próbkowania [s]")
    args = parser.parse_args()

    system = OrbitalResourceSystem()

    if args.once or args.json:
        system.collect()  # warmup
        time.sleep(0.5)
        metrics = system.step()
        if args.json:
            print(json.dumps(metrics, indent=2))
        else:
            print(system.format_dashboard(metrics))
        return

    # Live dashboard
    print("CIEL Orbital Monitor — Ctrl+C aby zatrzymać")
    try:
        while True:
            metrics = system.step()
            print(system.format_dashboard(metrics))
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nOrbital monitor zatrzymany.")


if __name__ == "__main__":
    main()
