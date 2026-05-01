"""HTRI Local - dense matrix phase dynamics for local hardware.

This version replaces the scalar Kuramoto step with a fully vectorized dense
phase network: explicit coupling matrix, explicit pairwise potential, and a
winding-number accumulator for the topological memory trace.

The model remains classical. The matrices are phase-space bookkeeping, not
quantum operators.
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from .htri_matrix import DensePhaseNetwork, plo_frequencies

# ── Hardware constants ──────────────────────────────────────────────────────

CPU_THREADS = 12     # i7-8750H logical cores
GPU_CORES = 768      # GTX 1050 Ti CUDA cores
RAM_GB = 7.5
SCHUMANN_HZ = 7.83

# ── Frequency scaling ───────────────────────────────────────────────────────

_H200_BLOCKS = 14080   # reference scale (H200 spec)
_H200_SPREAD = 28.0    # Hz spread for 14080 blocks → 7.83 Hz beat


def plo_frequencies_local(n: int, f_base: float = 1.0,
                          target_beat_hz: float = SCHUMANN_HZ) -> np.ndarray:
    """Backward-compatible alias for the local frequency ladder."""
    _ = target_beat_hz  # diagnostic only
    spread = _H200_SPREAD * (n / _H200_BLOCKS)
    return np.array([f_base + (i / max(n, 1)) * spread for i in range(n)], dtype=np.float64)


# ── Dense phase network wrapper ─────────────────────────────────────────────

@dataclass
class OscillatorBank:
    n: int
    kappa: float = 0.1
    dt: float = 0.001
    topology: str = "all_to_all"
    field_strength: float = 0.0
    ring_nearest: int = 1
    ring_decay: float = 1.0
    grid_shape: tuple[int, int] | None = None

    phases: np.ndarray = field(init=False)
    omegas: np.ndarray = field(init=False)
    sigma: np.ndarray = field(init=False)
    coherence: float = field(init=False, default=0.0)
    potential: float = field(init=False, default=0.0)
    t: float = field(init=False, default=0.0)

    def __post_init__(self) -> None:
        self._network = DensePhaseNetwork(
            n=self.n,
            dt=self.dt,
            kappa=self.kappa,
            topology=self.topology,  # type: ignore[arg-type]
            field_strength=self.field_strength,
            ring_nearest=self.ring_nearest,
            ring_decay=self.ring_decay,
            grid_shape=self.grid_shape,
        )
        # Keep a stable, explicit state mirror for downstream callers.
        self.phases = self._network.phases
        self.omegas = self._network.omegas
        self.sigma = self._network.sigma

    def step(self) -> None:
        self._network.step()
        self._sync(self._network.snapshot())

    def run(self, steps: int) -> dict[str, Any]:
        snapshot = self._network.run(int(steps))
        self._sync(snapshot)
        return {
            "n_oscillators": self.n,
            "coherence": round(self.coherence, 6),
            "potential": round(self.potential, 6),
            "soul_invariant": round(float(np.mean(self.sigma)), 6),
            "sigma_max": round(float(np.max(np.abs(self.sigma))), 6),
            "beat_freq_est_hz": round(float(np.std(self.omegas) * self.n / 2), 4),
            "spectral_radius": round(float(snapshot["spectral_radius"]), 6),
            "field_norm": round(float(snapshot["field_norm"]), 6),
            "t": round(self.t, 4),
        }

    def _sync(self, snapshot: dict[str, Any]) -> None:
        self.phases = self._network.phases
        self.omegas = self._network.omegas
        self.sigma = self._network.sigma
        self.coherence = float(snapshot.get("coherence", self.coherence))
        self.potential = float(snapshot.get("potential", self.potential))
        self.t = float(snapshot.get("t", self.t))


# ── CPU HTRI (12 threads) ───────────────────────────────────────────────────

class CPUHtri:
    """12 PLO - one per logical thread of the i7-8750H."""

    def __init__(self):
        self.bank = OscillatorBank(n=CPU_THREADS, kappa=0.15, dt=0.001)

    def run(self, steps: int = 500) -> dict[str, Any]:
        m = self.bank.run(steps)
        m["substrate"] = "CPU_i7-8750H"
        return m


# ── GPU HTRI (768 cores) ────────────────────────────────────────────────────

class GPUHtri:
    """768 PLO - mapped to CUDA cores of the GTX 1050 Ti.

    CUDA is optional. If CuPy is missing, the dense numpy network remains the
    authoritative execution path.
    """

    def __init__(self):
        self._cuda = False
        self._xp = np
        try:
            import cupy as cp
            # Warm-up probe — catches missing nvcc/nvrtc before first real kernel
            _probe = cp.array([1.0, 2.0], dtype=cp.float32)
            _ = float(cp.sum(_probe))   # forces JIT compilation
            self._xp = cp
            self._cuda = True
        except Exception:
            pass  # numpy fallback remains active
        self.bank = OscillatorBank(n=GPU_CORES, kappa=0.1, dt=0.001)

    def run(self, steps: int = 500) -> dict[str, Any]:
        if self._cuda:
            try:
                return self._run_cuda(steps)
            except Exception:
                self._cuda = False  # trwały fallback na numpy dla tej instancji
        m = self.bank.run(steps)
        m["substrate"] = "GPU_GTX1050Ti_cpu-fallback"
        return m

    def _run_cuda(self, steps: int) -> dict[str, Any]:
        xp = self._xp
        phases = xp.asarray(self.bank.phases, dtype=xp.float32)
        omegas = xp.asarray(self.bank.omegas, dtype=xp.float32)
        sigma = xp.asarray(self.bank.sigma, dtype=xp.float32)
        K = xp.asarray(self.bank._network.matrix, dtype=xp.float32)
        field_phase = xp.asarray(self.bank._network.field_phase, dtype=xp.float32)
        dt = self.bank.dt

        for _ in range(int(steps)):
            prev = phases.copy()
            diff = phases[:, None] - phases[None, :]
            coupling = xp.sum(K * xp.sin(diff), axis=1) / GPU_CORES
            field = self.bank.field_strength * xp.sin(field_phase - phases)
            phases = (phases + (omegas + coupling + field) * dt) % (2 * math.pi)
            delta = phases - prev
            delta = xp.arctan2(xp.sin(delta), xp.cos(delta))
            sigma = sigma + delta / (2 * math.pi)

        # sync back to CPU mirror
        self.bank._network.phases = xp.asnumpy(phases) if hasattr(xp, "asnumpy") else np.asarray(phases)
        self.bank._network.sigma = xp.asnumpy(sigma) if hasattr(xp, "asnumpy") else np.asarray(sigma)
        self.bank._network.coherence = float(abs(xp.mean(xp.exp(1j * phases))))
        self.bank._network.potential = float(0.5 * xp.sum(K * (1.0 - xp.cos(phases[:, None] - phases[None, :]))).item() / GPU_CORES)
        self.bank._network.t += steps * dt
        m = self.bank.run(0)
        m["substrate"] = "GPU_GTX1050Ti_CUDA"
        return m


# ── Unified Local HTRI ──────────────────────────────────────────────────────

class LocalHTRI:
    """Unified HTRI for the local system.

    CPU (12) + GPU (768) = 780 total oscillators.
    The combined result exposes coherence, potential, spectral radius, and the
    topological winding-number trace.
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
        w_gpu = GPU_CORES / total_osc

        sigma_comb = w_cpu * cpu_m["soul_invariant"] + w_gpu * gpu_m["soul_invariant"]
        coh_comb = w_cpu * cpu_m["coherence"] + w_gpu * gpu_m["coherence"]
        pot_comb = w_cpu * cpu_m["potential"] + w_gpu * gpu_m["potential"]
        spec_comb = w_cpu * cpu_m["spectral_radius"] + w_gpu * gpu_m["spectral_radius"]

        return {
            "schema": "ciel/htri-local/v2.0-dense",
            "hardware": {
                "cpu": "Intel i7-8750H (12 threads)",
                "gpu": "GTX 1050 Ti (768 CUDA cores)",
                "ram_total_gb": RAM_GB,
                "ram_avail_gb": round(ram_avail, 2),
                "cuda_active": self.gpu._cuda,
            },
            "cpu": cpu_m,
            "gpu": gpu_m,
            "ram_phase_rad": round(ram_phase, 4),
            "disk_read_mb_s": round(disk_r, 3),
            "disk_write_mb_s": round(disk_w, 3),
            "combined": {
                "soul_invariant": round(sigma_comb, 6),
                "coherence": round(coh_comb, 4),
                "potential": round(pot_comb, 6),
                "spectral_radius": round(spec_comb, 6),
                "beat_freq_target_hz": SCHUMANN_HZ,
                "total_oscillators": total_osc,
            },
            "elapsed_s": round(time.time() - t0, 3),
        }


def _read_ram_available_gb() -> float:
    try:
        with open("/proc/meminfo", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("MemAvailable"):
                    return int(line.split()[1]) / (1024 ** 2)
    except Exception:
        pass
    return 3.0


def _read_disk_throughput_mb(window: float = 0.1) -> tuple[float, float]:
    """Disk read/write throughput in MB/s over a short window."""

    def _sample() -> tuple[float, float]:
        r = w = 0.0
        try:
            with open("/proc/diskstats", encoding="utf-8") as fh:
                for line in fh:
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
