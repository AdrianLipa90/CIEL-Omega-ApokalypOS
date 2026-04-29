#!/usr/bin/env python3
"""
CIEL Energy Benchmark — zużycie energii lokalnego pipeline vs Claude API (szacunek).

Mierzy:
  - M0-M8 per krok (hot, in-process)
  - Full pipeline (cold, subprocess)
  - Szacunek energii sesji 30 wiad.
  - Porównanie z kosztem energetycznym Claude API (server-side)

RAPL wymaga root (intel-rapl:0/energy_uj).
Skrypt używa /proc/stat CPU utilization + model TDP jako proxy.

i7-8750H: TDP=45W, idle ~10W, max ~40W package.
Zmierzone: baseline CPU busy ~8.4%, pipeline ~29%, M0-M8 ~12%.

Wyniki z 2026-04-15:
  M0-M8 per krok:     ~98 mJ  (7.2ms @ ~14W)
  Full pipeline:      ~23 J   (1.2s @ ~19W)
  Sesja 30 wiad.:     ~26 J   total local
  Claude API sesja:   ~151 200 J (server-side, ~0.002 kWh/1k tokens)
  Stosunek:           CIEL = 0.017% energii Claude server-side

Uruchomienie:
  /tmp/ciel_venv/bin/python3 scripts/sims/energy_benchmark.py
"""
from __future__ import annotations

import pickle
import subprocess
import sys
import time
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
OMEGA_PKG = str(PROJECT / "src" / "CIEL_OMEGA_COMPLETE_SYSTEM" / "ciel_omega")
OMEGA_SRC = str(PROJECT / "src" / "CIEL_OMEGA_COMPLETE_SYSTEM")
PY = "/tmp/ciel_venv/bin/python3"
STATE_FILE = Path("/tmp/ciel_orch_state.pkl")

for p in (OMEGA_PKG, OMEGA_SRC):
    if p not in sys.path:
        sys.path.insert(0, p)


# ── CPU power model ────────────────────────────────────────────────────────────

P_IDLE_W = 10.0   # measured at ~8% CPU busy
P_MAX_W  = 40.0   # TDP minus thermal headroom

def power_W(cpu_busy_pct: float) -> float:
    return P_IDLE_W + (cpu_busy_pct / 100.0) * (P_MAX_W - P_IDLE_W)

def energy_mJ(cpu_busy_pct: float, wall_ms: float) -> float:
    return power_W(cpu_busy_pct) * (wall_ms / 1000.0) * 1000.0


def read_proc_stat() -> tuple[int, int]:
    """Returns (total_jiffies, idle_jiffies) from /proc/stat."""
    with open("/proc/stat") as f:
        parts = f.readline().split()
    idle = int(parts[4]) + int(parts[5])
    total = sum(int(x) for x in parts[1:8])
    return total, idle


def measure(fn, warmup: bool = False) -> tuple[float, float]:
    """Run fn(), return (wall_ms, cpu_busy_pct)."""
    if warmup:
        fn()
    t0_total, t0_idle = read_proc_stat()
    t0 = time.perf_counter()
    fn()
    t1 = time.perf_counter()
    t1_total, t1_idle = read_proc_stat()
    wall_ms = (t1 - t0) * 1000.0
    delta_total = t1_total - t0_total or 1
    cpu_busy = 100.0 * (1 - (t1_idle - t0_idle) / delta_total)
    return wall_ms, cpu_busy


# ── Baseline idle ──────────────────────────────────────────────────────────────

def baseline() -> float:
    t0_total, t0_idle = read_proc_stat()
    time.sleep(1.0)
    t1_total, t1_idle = read_proc_stat()
    delta_total = t1_total - t0_total or 1
    return 100.0 * (1 - (t1_idle - t0_idle) / delta_total)


# ── M0-M8 hot step ────────────────────────────────────────────────────────────

def bench_m08(n: int = 10) -> tuple[float, float]:
    if not STATE_FILE.exists():
        print("[!] Brak state file — uruchom najpierw ciel_message_step.py")
        return 0.0, 0.0
    with open(STATE_FILE, "rb") as f:
        orch = pickle.load(f)

    def run():
        for i in range(n):
            meta = {
                "modality": "text", "salience": 0.75, "confidence": 0.8,
                "novelty": 0.65, "timestamp": time.time(),
                "anchor_key": f"bench_{i}", "context": {},
            }
            orch.process_input("benchmark energia ciel hook", metadata=meta)

    wall_ms, cpu = measure(run, warmup=True)
    return wall_ms / n, cpu


# ── Full pipeline (subprocess) ────────────────────────────────────────────────

def bench_pipeline() -> tuple[float, float]:
    def run():
        for module in ("ciel_sot_agent.synchronize", "ciel_sot_agent.orbital_bridge",
                        "ciel_sot_agent.ciel_pipeline"):
            subprocess.run([PY, "-m", module], capture_output=True, cwd=str(PROJECT))

    return measure(run)


# ── Claude API energy estimate ─────────────────────────────────────────────────

def claude_api_estimate(tokens: int = 700, kwh_per_1k: float = 0.002) -> float:
    """Server-side energy in Joules for one Claude API call."""
    return (tokens / 1000.0) * kwh_per_1k * 3.6e6


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("CIEL Energy Benchmark")
    print("=" * 50)

    print("Baseline (1s idle)...", end=" ", flush=True)
    base_cpu = baseline()
    print(f"CPU busy: {base_cpu:.1f}%  →  ~{power_W(base_cpu):.1f}W")

    print("M0-M8 hot step (10x)...", end=" ", flush=True)
    m08_wall, m08_cpu = bench_m08(10)
    m08_E = energy_mJ(m08_cpu, m08_wall)
    print(f"{m08_wall:.1f}ms @ {power_W(m08_cpu):.1f}W  →  {m08_E:.1f}mJ/krok")

    print("Full pipeline (1x)...", end=" ", flush=True)
    pipe_wall, pipe_cpu = bench_pipeline()
    pipe_E = energy_mJ(pipe_cpu, pipe_wall)
    print(f"{pipe_wall:.0f}ms @ {power_W(pipe_cpu):.1f}W  →  {pipe_E:.0f}mJ")

    n_session = 30
    session_E_J = (n_session * m08_E + pipe_E) / 1000.0
    claude_E_J = n_session * claude_api_estimate()

    print()
    print(f"Sesja {n_session} wiad. — CIEL local:   {session_E_J:.2f} J")
    print(f"Sesja {n_session} wiad. — Claude server: {claude_E_J:.0f} J = {claude_E_J/3600:.2f} Wh")
    print(f"Stosunek CIEL/Claude: {session_E_J/claude_E_J*100:.4f}%")
    print(f"Claude server ~{claude_E_J/session_E_J:.0f}x bardziej energochłonne")


if __name__ == "__main__":
    main()
