"""HTRI Scheduler — adaptacyjny dense matrix scheduler.

Trzy poziomy mocy:
  cpu   — CPUHtri (12 oscylatorów, ~0.02s) — domyślny
  half  — CPUHtri + GPUHtri 50 kroków (~1s, numpy fallback)
  full  — LocalHTRI CPU+GPU=780 oscylatorów (~5s, numpy fallback / <0.1s z CuPy)

Automatyczna eskalacja: jeśli RAM > 3GB wolnego i brak wysokiego CPU load → half.
Pełna moc tylko na żądanie (power_mode='full') lub gdy CuPy dostępne.

Eksportuje: coherence r → n_threads_optimal dla llama.cpp.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

_STATE_PATH = Path.home() / "Pulpit/CIEL_memories/state/htri_state.json"
CPU_THREADS = 12
_HTRI_TIMEOUT = 3.0   # max sekund na run — fallback do cpu jeśli przekroczony


def _htri_path() -> str:
    p = Path(__file__).parent.parent / "CIEL_OMEGA_COMPLETE_SYSTEM"
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
    return str(p)


def _ram_free_gb() -> float:
    try:
        with open("/proc/meminfo", encoding="utf-8") as f:
            for line in f:
                if line.startswith("MemAvailable"):
                    return int(line.split()[1]) / (1024 ** 2)
    except Exception:
        pass
    return 2.0


def _cpu_load() -> float:
    try:
        with open("/proc/loadavg", encoding="utf-8") as f:
            return float(f.read().split()[0])
    except Exception:
        return 0.0


def _cuda_available() -> bool:
    try:
        import cupy  # noqa: F401
        return True
    except ImportError:
        return False


def _auto_power_mode() -> str:
    """cpu / half / full — dobrane wg zasobów."""
    if _cuda_available():
        return "full"
    ram = _ram_free_gb()
    load = _cpu_load()
    if ram < 2.0 or load > 6.0:
        return "cpu"
    if ram >= 3.0 and load < 3.0:
        return "half"
    return "cpu"


def run(n: int = CPU_THREADS, power_mode: str = "auto") -> dict:
    """Uruchom HTRI. power_mode: 'auto'|'cpu'|'half'|'full'."""
    _htri_path()

    if power_mode == "auto":
        power_mode = _auto_power_mode()

    t0 = time.time()
    coherence = soul = spectral = potential = 0.0
    gpu_coherence = gpu_soul = 0.0
    substrate = "CPU_i7-8750H_dense"
    n_osc = CPU_THREADS

    try:
        from ciel_omega.htri.htri_local import CPUHtri, GPUHtri, LocalHTRI

        if power_mode == "full":
            local = LocalHTRI()
            m = local.run(cpu_steps=300, gpu_steps=300)
            comb = m.get("combined", {})
            coherence = float(comb.get("coherence", 0.85))
            soul = float(comb.get("soul_invariant", 0.0))
            spectral = float(comb.get("spectral_radius", 0.0))
            potential = float(comb.get("potential", 0.0))
            n_osc = int(comb.get("total_oscillators", 780))
            substrate = m.get("gpu", {}).get("substrate", "LocalHTRI_full")

        elif power_mode == "half":
            cpu = CPUHtri()
            mc = cpu.run(steps=300)
            # GPU z limitem czasowym
            t_gpu = time.time()
            try:
                gpu = GPUHtri()
                mg = gpu.run(steps=50)
                if time.time() - t_gpu < _HTRI_TIMEOUT:
                    gpu_coherence = float(mg.get("coherence", 0.0))
                    gpu_soul = float(mg.get("soul_invariant", 0.0))
                    substrate = mg.get("substrate", "half")
            except Exception:
                pass
            w_cpu = CPU_THREADS / (CPU_THREADS + 768)
            w_gpu = 768 / (CPU_THREADS + 768)
            coherence = w_cpu * float(mc.get("coherence", 0.85)) + w_gpu * gpu_coherence
            soul = w_cpu * float(mc.get("soul_invariant", 0.0)) + w_gpu * gpu_soul
            spectral = float(mc.get("spectral_radius", 0.0))
            potential = float(mc.get("potential", 0.0))
            n_osc = CPU_THREADS + (768 if gpu_coherence > 0 else 0)
            if not substrate or substrate == "half":
                substrate = f"half_CPU+GPU(numpy)"

        else:  # cpu
            cpu = CPUHtri()
            mc = cpu.run(steps=300)
            coherence = float(mc.get("coherence", 0.85))
            soul = float(mc.get("soul_invariant", 0.0))
            spectral = float(mc.get("spectral_radius", 0.0))
            potential = float(mc.get("potential", 0.0))

    except Exception as e:
        print(f"[HTRI] unavailable ({power_mode}): {e}", file=sys.stderr)
        coherence = 0.85

    elapsed = time.time() - t0
    n_threads_optimal = max(1, round(coherence * CPU_THREADS))

    state = {
        "coherence": round(coherence, 6),
        "soul_invariant": round(soul, 6),
        "spectral_radius": round(spectral, 6),
        "potential": round(potential, 6),
        "n_oscillators": n_osc,
        "n_threads_optimal": n_threads_optimal,
        "power_mode": power_mode,
        "substrate": substrate,
        "elapsed_s": round(elapsed, 3),
        "timestamp": time.time(),
    }

    _STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _STATE_PATH.write_text(json.dumps(state))

    try:
        from .spreadsheet_db import append_htri_metrics
        append_htri_metrics(state)
    except Exception:
        pass

    return state


def get_state() -> dict:
    """Wczytaj stan. Jeśli nieaktualny (>60s) — przelicz w trybie auto."""
    if _STATE_PATH.exists():
        try:
            s = json.loads(_STATE_PATH.read_text())
            if time.time() - s.get("timestamp", 0) < 60:
                return s
        except Exception:
            pass
    return run()


def get_optimal_threads() -> int:
    return get_state()["n_threads_optimal"]


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["auto", "cpu", "half", "full"], default="auto")
    args = parser.parse_args()
    s = run(power_mode=args.mode)
    print(f"HTRI Scheduler [{s['power_mode']}] — {s['n_oscillators']} oscylatorów | {s['elapsed_s']}s")
    print(f"  coherence r      = {s['coherence']:.4f}")
    print(f"  soul_invariant   = {s['soul_invariant']:.4f}")
    print(f"  spectral_radius  = {s['spectral_radius']:.4f}")
    print(f"  n_threads_opt    = {s['n_threads_optimal']} / {CPU_THREADS}")
    print(f"  substrate        = {s['substrate']}")
    print(f"  → {_STATE_PATH}")
