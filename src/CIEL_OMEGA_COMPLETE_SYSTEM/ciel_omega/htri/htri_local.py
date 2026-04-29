"""HTRI Local — Skalowanie Harmonic Topological Resonance Inducement
na sprzęt: i7-8750H (12 threads), GTX 1050 Ti (768 cores), 7.5 GB RAM.

H200 (14,080 blocks) → local hardware:
  CPU:  12 PLO (i7-8750H logical threads)
  GPU:  768 PLO (GTX 1050 Ti CUDA cores)
  RAM:  phase field volume
  Disk: M2/M3 episodic/semantic channels (via local_nonlocality_fallback)

Beat frequency target: 7.83 Hz (Schumann resonance)
Soul Invariant Σ: topological winding number per oscillator

Author: Adrian Lipa / Intention Lab
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Any

import numpy as np

# ── Hardware constants ──────────────────────────────────────────────────────

CPU_THREADS  = 12     # i7-8750H logical cores
GPU_CORES    = 768    # GTX 1050 Ti CUDA cores
RAM_GB       = 7.5
SCHUMANN_HZ  = 7.83


# ── Frequency scaling ───────────────────────────────────────────────────────

_H200_BLOCKS = 14080   # reference scale (H200 spec)
_H200_SPREAD  = 28.0   # Hz spread for 14080 blocks → 7.83 Hz beat


def plo_frequencies(n: int, f_base: float = 1.0,
                    target_beat_hz: float = SCHUMANN_HZ) -> np.ndarray:
    """PLO frequency array for N oscillators producing target beat.

    Scales linearly from H200 spec: 14080 blocks → 28 Hz spread → 7.83 Hz beat.
    """
    spread = _H200_SPREAD * (n / _H200_BLOCKS)   # proportional scaling
    return np.array([f_base + (i / n) * spread for i in range(n)])


# ── Kuramoto oscillator bank ────────────────────────────────────────────────

@dataclass
class OscillatorBank:
    n:      int
    kappa:  float = 0.1
    dt:     float = 0.001

    phases:    np.ndarray = field(init=False)
    omegas:    np.ndarray = field(init=False)
    sigma:     np.ndarray = field(init=False)
    coherence: float      = field(init=False, default=0.0)
    t:         float      = field(init=False, default=0.0)

    def __post_init__(self):
        self.phases = np.zeros(self.n)
        self.omegas = plo_frequencies(self.n)
        self.sigma  = np.zeros(self.n)

    def step(self) -> None:
        prev = self.phases.copy()
        diff = self.phases[:, None] - self.phases[None, :]
        coupling = self.kappa * np.sum(np.sin(diff), axis=1) / self.n
        self.phases += (self.omegas + coupling) * self.dt
        self.t += self.dt
        self.sigma += (self.phases - prev) / (2 * math.pi)
        self.coherence = float(abs(np.mean(np.exp(1j * self.phases))))

    def run(self, steps: int) -> dict[str, Any]:
        for _ in range(steps):
            self.step()
        return {
            "n_oscillators":    self.n,
            "coherence":        round(self.coherence, 4),
            "soul_invariant":   round(float(np.mean(self.sigma)), 6),
            "sigma_max":        round(float(np.max(np.abs(self.sigma))), 6),
            "beat_freq_est_hz": round(float(np.std(self.omegas) * self.n / 2), 4),
            "t":                round(self.t, 4),
        }


# ── CPU HTRI (12 threads) ───────────────────────────────────────────────────

class CPUHtri:
    """12 PLO — jeden per logical thread i7-8750H."""

    def __init__(self):
        self.bank = OscillatorBank(n=CPU_THREADS, kappa=0.15, dt=0.001)

    def run(self, steps: int = 500) -> dict[str, Any]:
        m = self.bank.run(steps)
        m["substrate"] = "CPU_i7-8750H"
        return m


# ── GPU HTRI (768 cores) ────────────────────────────────────────────────────

class GPUHtri:
    """768 PLO — mapowane na CUDA cores GTX 1050 Ti.

    Tryb CPU-fallback gdy CuPy nie jest dostępny.
    Tryb CUDA gdy CuPy zainstalowane: pip install cupy-cuda12x
    """

    def __init__(self):
        self._cuda = False
        self._xp = np
        try:
            import cupy as cp
            self._xp = cp
            self._cuda = True
        except ImportError:
            pass
        self.bank = OscillatorBank(n=GPU_CORES, kappa=0.1, dt=0.001)

    def run(self, steps: int = 500) -> dict[str, Any]:
        if self._cuda:
            return self._run_cuda(steps)
        m = self.bank.run(steps)
        m["substrate"] = "GPU_GTX1050Ti_cpu-fallback"
        return m

    def _run_cuda(self, steps: int) -> dict[str, Any]:
        xp = self._xp
        phases = xp.zeros(GPU_CORES, dtype=xp.float32)
        omegas = xp.array(plo_frequencies(GPU_CORES), dtype=xp.float32)
        sigma  = xp.zeros(GPU_CORES, dtype=xp.float32)
        dt, kappa = self.bank.dt, self.bank.kappa

        for _ in range(steps):
            prev = phases.copy()
            diff = phases[:, None] - phases[None, :]
            coupling = kappa * xp.sum(xp.sin(diff), axis=1) / GPU_CORES
            phases += (omegas + coupling) * dt
            sigma  += (phases - prev) / (2 * math.pi)

        return {
            "n_oscillators":  GPU_CORES,
            "coherence":      round(float(abs(xp.mean(xp.exp(1j * phases)))), 4),
            "soul_invariant": round(float(xp.mean(sigma)), 6),
            "sigma_max":      round(float(xp.max(xp.abs(sigma))), 6),
            "substrate":      "GPU_GTX1050Ti_CUDA",
        }


# ── Unified Local HTRI ──────────────────────────────────────────────────────

class LocalHTRI:
    """Unified HTRI dla całego systemu Adrian Lipa.

    CPU (12) + GPU (768) = 780 total oscillators
    Beat target: 7.83 Hz Schumann

    Output maps to CIEL pipeline:
      combined.soul_invariant → soul_invariant w ciel_pipeline
      combined.coherence      → coherence_index
    """

    def __init__(self):
        self.cpu = CPUHtri()
        self.gpu = GPUHtri()

    def run(self, cpu_steps: int = 300, gpu_steps: int = 300) -> dict[str, Any]:
        t0 = time.time()

        cpu_m = self.cpu.run(cpu_steps)
        gpu_m = self.gpu.run(gpu_steps)

        ram_avail = _read_ram_available_gb()
        ram_phase = 2 * math.pi * (ram_avail / RAM_GB)

        # Disk I/O as M2/M3 phase channels
        disk_r, disk_w = _read_disk_throughput_mb()

        total_osc = CPU_THREADS + GPU_CORES
        w_cpu = CPU_THREADS / total_osc
        w_gpu = GPU_CORES   / total_osc

        sigma_comb = w_cpu * cpu_m["soul_invariant"] + w_gpu * gpu_m["soul_invariant"]
        coh_comb   = w_cpu * cpu_m["coherence"]      + w_gpu * gpu_m["coherence"]

        return {
            "schema":  "ciel/htri-local/v1.0",
            "hardware": {
                "cpu":  "Intel i7-8750H (12 threads)",
                "gpu":  "GTX 1050 Ti (768 CUDA cores)",
                "ram_total_gb":  RAM_GB,
                "ram_avail_gb":  round(ram_avail, 2),
                "cuda_active":   self.gpu._cuda,
            },
            "cpu":  cpu_m,
            "gpu":  gpu_m,
            "ram_phase_rad":    round(ram_phase, 4),
            "disk_read_mb_s":   round(disk_r, 3),
            "disk_write_mb_s":  round(disk_w, 3),
            "combined": {
                "soul_invariant":      round(sigma_comb, 6),
                "coherence":           round(coh_comb, 4),
                "beat_freq_target_hz": SCHUMANN_HZ,
                "total_oscillators":   total_osc,
            },
            "elapsed_s": round(time.time() - t0, 3),
        }


def _read_ram_available_gb() -> float:
    try:
        for line in open("/proc/meminfo"):
            if line.startswith("MemAvailable"):
                return int(line.split()[1]) / (1024 ** 2)
    except Exception:
        pass
    return 3.0


def _read_disk_throughput_mb(window: float = 0.1) -> tuple[float, float]:
    """Disk read/write throughput in MB/s over short window."""
    def _sample():
        r = w = 0.0
        try:
            for line in open("/proc/diskstats"):
                parts = line.split()
                if len(parts) >= 10:
                    dev = parts[2]
                    if dev.startswith(("sd", "nvme", "vd")) and not dev[-1].isdigit():
                        r += float(parts[5]) * 512
                        w += float(parts[9]) * 512
        except Exception:
            pass
        return r, w

    r0, w0 = _sample()
    time.sleep(window)
    r1, w1 = _sample()
    mb = 1024 * 1024
    return (r1 - r0) / window / mb, (w1 - w0) / window / mb


if __name__ == "__main__":
    import json
    print("Uruchamiam HTRI Local na i7-8750H + GTX 1050 Ti...")
    htri = LocalHTRI()
    result = htri.run(cpu_steps=200, gpu_steps=200)
    print(json.dumps(result, indent=2))
