#!/usr/bin/env python3
"""CIEL Hardware Monitor — CPU / RAM / GPU / VRAM / SWAP.

Mierzy zasoby sprzętowe i raportuje w kontekście CIEL:
- Czy HTRI może bezpiecznie uruchomić GPU steps?
- Czy swap jest pod presją (OOM risk)?
- Jaka jest faktyczna przepustowość obliczeniowa?

Usage:
    python3 scripts/ciel_hw_monitor.py           # one-shot snapshot
    python3 scripts/ciel_hw_monitor.py --watch    # continuous, odświeżaj co 5s
    python3 scripts/ciel_hw_monitor.py --json     # JSON output (dla pipeline)
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from pathlib import Path

# ── Hardware readers ──────────────────────────────────────────────────────────

def _read_cpu() -> dict:
    try:
        import psutil
        pct = psutil.cpu_percent(interval=0.5, percpu=False)
        freq = psutil.cpu_freq()
        count = psutil.cpu_count(logical=True)
        phys = psutil.cpu_count(logical=False)
        return {
            "usage_pct":   round(pct, 1),
            "freq_mhz":    round(freq.current, 0) if freq else None,
            "freq_max_mhz": round(freq.max, 0) if freq else None,
            "logical_cores": count,
            "physical_cores": phys,
        }
    except ImportError:
        # Fallback: /proc/stat
        with open("/proc/stat") as f:
            line = f.readline().split()
        idle = int(line[4])
        total = sum(int(x) for x in line[1:])
        return {"usage_pct": round(100 * (1 - idle / max(total, 1)), 1)}


def _read_ram() -> dict:
    try:
        import psutil
        vm = psutil.virtual_memory()
        sw = psutil.swap_memory()
        return {
            "total_mb":     round(vm.total / 1024**2),
            "used_mb":      round(vm.used / 1024**2),
            "available_mb": round(vm.available / 1024**2),
            "used_pct":     round(vm.percent, 1),
            "swap_total_mb": round(sw.total / 1024**2),
            "swap_used_mb":  round(sw.used / 1024**2),
            "swap_pct":      round(sw.percent, 1),
        }
    except ImportError:
        with open("/proc/meminfo") as f:
            lines = f.readlines()
        info = {}
        for line in lines:
            parts = line.split()
            if len(parts) >= 2:
                info[parts[0].rstrip(":")] = int(parts[1])
        total = info.get("MemTotal", 0)
        free = info.get("MemAvailable", 0)
        swap_total = info.get("SwapTotal", 0)
        swap_free = info.get("SwapFree", 0)
        return {
            "total_mb":      total // 1024,
            "available_mb":  free // 1024,
            "used_mb":       (total - free) // 1024,
            "used_pct":      round(100 * (1 - free / max(total, 1)), 1),
            "swap_total_mb": swap_total // 1024,
            "swap_used_mb":  (swap_total - swap_free) // 1024,
            "swap_pct":      round(100 * (1 - swap_free / max(swap_total, 1)), 1),
        }


def _read_gpu() -> dict | None:
    try:
        out = subprocess.check_output(
            ["nvidia-smi",
             "--query-gpu=name,memory.used,memory.total,utilization.gpu,"
             "utilization.memory,temperature.gpu,power.draw,power.limit",
             "--format=csv,noheader,nounits"],
            timeout=3, stderr=subprocess.DEVNULL
        ).decode().strip()
        if not out:
            return None
        parts = [p.strip() for p in out.split(",")]
        return {
            "name":           parts[0],
            "vram_used_mb":   int(parts[1]),
            "vram_total_mb":  int(parts[2]),
            "vram_used_pct":  round(int(parts[1]) / max(int(parts[2]), 1) * 100, 1),
            "gpu_util_pct":   int(parts[3]),
            "mem_util_pct":   int(parts[4]),
            "temp_c":         int(parts[5]),
            "power_w":        float(parts[6]) if parts[6] != "[N/A]" else None,
            "power_limit_w":  float(parts[7]) if parts[7] != "[N/A]" else None,
        }
    except Exception:
        return None


def _read_top_procs(n: int = 5) -> list[dict]:
    try:
        import psutil
        procs = []
        for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info", "cmdline"]):
            try:
                info = p.info
                cmd = " ".join(info["cmdline"] or [])
                # Only Python/CIEL processes
                if "python" not in cmd.lower() and "ciel" not in cmd.lower():
                    continue
                procs.append({
                    "pid":     info["pid"],
                    "name":    info["name"],
                    "cpu_pct": info["cpu_percent"],
                    "ram_mb":  round(info["memory_info"].rss / 1024**2),
                    "cmd":     cmd[50:100] if len(cmd) > 50 else cmd,
                })
            except Exception:
                continue
        procs.sort(key=lambda x: x["ram_mb"], reverse=True)
        return procs[:n]
    except ImportError:
        return []


# ── CIEL health assessment ────────────────────────────────────────────────────

def _assess(cpu: dict, ram: dict, gpu: dict | None) -> dict:
    """Determine safe operating mode for CIEL based on hardware state."""
    warnings = []
    mode = "deep"  # full autonomy

    swap_pct = ram.get("swap_pct", 0)
    ram_pct = ram.get("used_pct", 0)
    cpu_pct = cpu.get("usage_pct", 0)

    if swap_pct > 90:
        warnings.append("SWAP CRITICAL — ryzyko OOM, zatrzymaj ciężkie procesy")
        mode = "safe"
    elif swap_pct > 60:
        warnings.append("SWAP wysoki — ogranicz równoległe embeddingi")
        mode = "standard"

    if ram_pct > 92:
        warnings.append("RAM krytycznie zajęty")
        mode = "safe"
    elif ram_pct > 80:
        warnings.append("RAM pod presją")
        if mode == "deep":
            mode = "standard"

    if cpu_pct > 90:
        warnings.append("CPU nasycony")

    # HTRI feasibility
    htri_gpu_ok = False
    htri_cpu_ok = cpu_pct < 70
    if gpu:
        vram_free = gpu["vram_total_mb"] - gpu["vram_used_mb"]
        htri_gpu_ok = vram_free > 500 and gpu["gpu_util_pct"] < 80
        if gpu["temp_c"] > 85:
            warnings.append(f"GPU temperatura wysoka: {gpu['temp_c']}°C")
            htri_gpu_ok = False

    return {
        "mode":          mode,
        "warnings":      warnings,
        "htri_gpu_ok":   htri_gpu_ok,
        "htri_cpu_ok":   htri_cpu_ok,
        "oom_risk":      swap_pct > 80 or ram_pct > 90,
    }


# ── Display ───────────────────────────────────────────────────────────────────

def _render(cpu: dict, ram: dict, gpu: dict | None,
            procs: list[dict], assessment: dict,
            heisenberg: dict | None = None) -> str:
    lines = []
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    lines.append(f"\n═══ CIEL Hardware Monitor — {ts} ═══")

    # CPU
    bar_len = 20
    cpu_pct = cpu.get("usage_pct", 0)
    filled = int(cpu_pct / 100 * bar_len)
    bar = "█" * filled + "░" * (bar_len - filled)
    freq = f" @ {cpu['freq_mhz']:.0f}MHz" if cpu.get("freq_mhz") else ""
    cores = f"{cpu.get('physical_cores','?')}C/{cpu.get('logical_cores','?')}T"
    lines.append(f"CPU  [{bar}] {cpu_pct:5.1f}%  {cores}{freq}")

    # RAM
    ram_pct = ram.get("used_pct", 0)
    filled = int(ram_pct / 100 * bar_len)
    bar = "█" * filled + "░" * (bar_len - filled)
    used = ram.get("used_mb", 0)
    total = ram.get("total_mb", 1)
    lines.append(f"RAM  [{bar}] {ram_pct:5.1f}%  {used}MB / {total}MB")

    # SWAP
    swap_pct = ram.get("swap_pct", 0)
    filled = int(swap_pct / 100 * bar_len)
    bar = "█" * filled + "░" * (bar_len - filled)
    sw_used = ram.get("swap_used_mb", 0)
    sw_total = ram.get("swap_total_mb", 1)
    flag = " ⚠" if swap_pct > 60 else ""
    lines.append(f"SWAP [{bar}] {swap_pct:5.1f}%  {sw_used}MB / {sw_total}MB{flag}")

    # GPU
    if gpu:
        vram_pct = gpu["vram_used_pct"]
        filled = int(vram_pct / 100 * bar_len)
        bar = "█" * filled + "░" * (bar_len - filled)
        lines.append(f"VRAM [{bar}] {vram_pct:5.1f}%  {gpu['vram_used_mb']}MB / {gpu['vram_total_mb']}MB  util={gpu['gpu_util_pct']}%  {gpu['temp_c']}°C")
        pwr = f"  {gpu['power_w']:.0f}W/{gpu['power_limit_w']:.0f}W" if gpu.get("power_w") else ""
        lines.append(f"GPU  {gpu['name']}{pwr}")
    else:
        lines.append("GPU  n/a")

    # Assessment
    mode_emoji = {"deep": "✓", "standard": "~", "safe": "⚠"}
    lines.append(f"\nCIEL mode: {assessment['mode']} {mode_emoji.get(assessment['mode'],'')}")
    lines.append(f"HTRI:  GPU={'OK' if assessment['htri_gpu_ok'] else 'SKIP'}  CPU={'OK' if assessment['htri_cpu_ok'] else 'BUSY'}")
    if assessment["warnings"]:
        for w in assessment["warnings"]:
            lines.append(f"  ⚠  {w}")

    # Heisenberg clip
    if heisenberg:
        hw = heisenberg
        clip_bar_len = 20
        filled = int(hw["allowed_work_frac"] * clip_bar_len)
        clip_bar = "█" * filled + "░" * (clip_bar_len - filled)
        throttle_flag = " ⚠ THROTTLED" if hw["throttled"] else ""
        lines.append(f"\nHeisenberg clip: [{clip_bar}] {hw['allowed_work_frac']*100:.0f}%  sleep={hw['sleep_s']}s  Δr={hw['delta_resource']}{throttle_flag}")
        if hw["reason"] != "ok":
            lines.append(f"  pressure: {hw['reason']}")

    # Top procs
    if procs:
        lines.append("\nTop Python/CIEL processes:")
        for p in procs:
            lines.append(f"  [{p['pid']}] {p['ram_mb']:5d}MB  {p['cpu_pct']:5.1f}%  {p['cmd'][:60]}")

    return "\n".join(lines)


# ── Heisenberg soft-clip ─────────────────────────────────────────────────────
#
# Uncertainty principle for compute:  Δresource · Δwork ≥ ½
#
# Interpretation:
#   Δresource = fraction of resource FREE  (0=none, 1=all)
#   Δwork     = allowed batch fraction     (0=nothing, 1=full batch)
#   Constraint: Δresource × Δwork ≤ 0.5   → Δwork ≤ 0.5 / Δresource
#   Clamped to [0, 1].
#
# At 90% RAM used  → Δresource=0.10 → Δwork ≤ 5.0 → clamped to 1.0  (no throttle)
# At 50% RAM used  → Δresource=0.50 → Δwork ≤ 1.0  (no throttle)
# At 20% RAM used  → Δresource=0.20 → Δwork ≤ 2.5 → clamped to 1.0
# …so RAM alone never throttles until it's truly full.
#
# The CRITICAL dimension is the *combined* pressure: if both RAM and CPU are tight,
# the effective Δresource = min(ram_free_frac, cpu_free_frac) → triggers throttle.
#
# sleep_s = base_sleep × (1 / max(Δwork, 0.01))   — longer sleep when work shrinks

def heisenberg_clip(snap: dict | None = None) -> dict:
    """Compute Heisenberg soft-clip parameters from current HW state.

    Returns:
        {
          "allowed_work_frac": float,  # 0..1 — how much of a batch to run
          "sleep_s":           float,  # recommended sleep between heavy ops
          "throttled":         bool,   # True if below full capacity
          "reason":            str,
        }

    Usage:
        clip = heisenberg_clip()
        if clip["throttled"]:
            time.sleep(clip["sleep_s"])
        n_items = int(total * clip["allowed_work_frac"])
    """
    if snap is None:
        snap = snapshot()

    ram = snap["ram"]
    cpu = snap["cpu"]
    gpu = snap.get("gpu")

    ram_free = 1.0 - ram.get("used_pct", 50) / 100.0
    cpu_free = 1.0 - cpu.get("usage_pct", 50) / 100.0
    swap_free = 1.0 - ram.get("swap_pct", 0) / 100.0

    # Swap pressure is the hardest constraint — near-zero swap → near-zero work
    # GPU VRAM: if present, add as constraint
    vram_free = 1.0
    if gpu:
        vram_free = 1.0 - gpu.get("vram_used_pct", 0) / 100.0

    # Effective free resource: worst bottleneck drives the clip
    # Swap weighted ×2 because swap pressure → OOM quickly
    delta_resource = min(ram_free, cpu_free, swap_free * 0.5 + 0.5, vram_free)
    delta_resource = max(delta_resource, 1e-3)

    # Δwork ≤ 0.5 / Δresource, clamped to [0,1]
    delta_work = min(1.0, 0.5 / delta_resource)

    # sleep: 0 when full capacity, scales up as work fraction drops
    # sleep_s = 0.1 × (1/delta_work - 1)  → 0s at full, up to ~10s at 5% work
    sleep_s = round(0.1 * max(0.0, 1.0 / max(delta_work, 0.01) - 1.0), 2)
    sleep_s = min(sleep_s, 10.0)  # hard cap: never sleep more than 10s

    throttled = delta_work < 0.95

    reasons = []
    if ram_free < 0.15:
        reasons.append(f"RAM {ram.get('used_pct',0):.0f}%")
    if swap_free < 0.5:
        reasons.append(f"SWAP {ram.get('swap_pct',0):.0f}%")
    if cpu_free < 0.20:
        reasons.append(f"CPU {cpu.get('usage_pct',0):.0f}%")
    if gpu and vram_free < 0.10:
        reasons.append(f"VRAM {gpu.get('vram_used_pct',0):.0f}%")
    reason = ", ".join(reasons) if reasons else "ok"

    return {
        "allowed_work_frac": round(delta_work, 3),
        "sleep_s":           sleep_s,
        "throttled":         throttled,
        "reason":            reason,
        "delta_resource":    round(delta_resource, 3),
    }


# ── Entry point ───────────────────────────────────────────────────────────────

def snapshot() -> dict:
    cpu = _read_cpu()
    ram = _read_ram()
    gpu = _read_gpu()
    procs = _read_top_procs()
    assessment = _assess(cpu, ram, gpu)
    snap = {"cpu": cpu, "ram": ram, "gpu": gpu,
            "procs": procs, "assessment": assessment,
            "timestamp": time.time()}
    snap["heisenberg"] = heisenberg_clip(snap)
    return snap


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--watch", action="store_true", help="Continuous monitoring")
    ap.add_argument("--interval", type=int, default=5, help="Seconds between updates")
    ap.add_argument("--json", action="store_true", help="JSON output")
    args = ap.parse_args()

    if args.json:
        data = snapshot()
        print(json.dumps(data, indent=2))
        return

    try:
        while True:
            data = snapshot()
            text = _render(data["cpu"], data["ram"], data["gpu"],
                           data["procs"], data["assessment"],
                           data.get("heisenberg"))
            if args.watch:
                os.system("clear")
            print(text)
            if not args.watch:
                break
            time.sleep(args.interval)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
