#!/usr/bin/env python3
"""HTRI Benchmark — porównanie inference z n_threads=4 (baseline) vs HTRI-optimal.

Metodologia:
  Runda A: POST /api/chat/message, n_threads=4 (hardcoded baseline)
  Runda B: POST /api/chat/message, n_threads=htri_optimal (z Kuramoto)

Mierzy: czas odpowiedzi (ms), długość odpowiedzi (chars), chars/ms.
Wynik: tabela A vs B z avg ± std.

Wymagania: serwis ciel-gui aktywny (port 5050), model załadowany.
"""
from __future__ import annotations

import json
import statistics
import sys
import time
from pathlib import Path

# Dodaj src do path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import urllib.request

GUI_URL    = "http://127.0.0.1:5050"
N_ROUNDS   = 5
PROMPTS    = [
    "kim jesteś?",
    "co to jest Kuramoto?",
    "opisz rezonans Schumanna",
    "co to jest soul invariant?",
    "wyjaśnij synchronizację fazową",
]


def _post(url: str, data: dict) -> tuple[dict, float]:
    body = json.dumps(data).encode()
    req = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read())
    elapsed_ms = (time.perf_counter() - t0) * 1000
    return result, elapsed_ms


def _reset():
    try:
        _post(f"{GUI_URL}/api/chat/reset", {})
    except Exception:
        pass


def run_round(label: str, n_threads_override: int | None = None) -> list[dict]:
    results = []
    for i, prompt in enumerate(PROMPTS[:N_ROUNDS]):
        _reset()
        payload = {"message": prompt}
        if n_threads_override:
            payload["n_threads_override"] = n_threads_override
        try:
            resp, ms = _post(f"{GUI_URL}/api/chat/message", payload)
            reply_len = len(resp.get("reply", ""))
            htri_n = resp.get("htri_n_threads", "?")
            results.append({
                "prompt": prompt[:30],
                "ms": ms,
                "chars": reply_len,
                "chars_per_ms": reply_len / ms if ms > 0 else 0,
                "htri_n": htri_n,
            })
            print(f"  [{label}] #{i+1} {ms:6.0f}ms  {reply_len}ch  htri_n={htri_n}")
        except Exception as e:
            print(f"  [{label}] #{i+1} ERROR: {e}")
            results.append({"ms": 0, "chars": 0, "chars_per_ms": 0, "error": str(e)})
        time.sleep(0.5)
    return results


def stats(results: list[dict]) -> dict:
    ms_list = [r["ms"] for r in results if r.get("ms", 0) > 0]
    cpm_list = [r["chars_per_ms"] for r in results if r.get("chars_per_ms", 0) > 0]
    return {
        "ms_avg": statistics.mean(ms_list) if ms_list else 0,
        "ms_std": statistics.stdev(ms_list) if len(ms_list) > 1 else 0,
        "cpm_avg": statistics.mean(cpm_list) if cpm_list else 0,
        "cpm_std": statistics.stdev(cpm_list) if len(cpm_list) > 1 else 0,
        "n": len(ms_list),
    }


def main():
    print("=" * 60)
    print("  HTRI BENCHMARK — inference timing A vs B")
    print("=" * 60)

    # Pobierz HTRI optimal threads
    try:
        from ciel_sot_agent.htri_scheduler import run as htri_run, CPU_THREADS
        htri_state = htri_run()
        htri_n = htri_state["n_threads_optimal"]
        htri_r = htri_state["coherence"]
        print(f"\n  HTRI coherence r={htri_r:.4f} → n_threads_optimal={htri_n}/{CPU_THREADS}")
    except Exception as e:
        htri_n = 8
        print(f"  HTRI scheduler error: {e} → fallback n={htri_n}")

    baseline_n = 4

    # Sprawdź czy serwis działa
    try:
        with urllib.request.urlopen(f"{GUI_URL}/api/chat/models", timeout=5) as r:
            models = json.loads(r.read())
        current = models.get("current", "?")
        print(f"  Model: {Path(current).name if current else '?'}")
    except Exception as e:
        print(f"\nERROR: serwis niedostępny na {GUI_URL}: {e}")
        sys.exit(1)

    print(f"\n  Runda A (baseline n_threads={baseline_n}):")
    results_a = run_round("A", baseline_n)

    print(f"\n  Runda B (HTRI n_threads={htri_n}):")
    results_b = run_round("B", htri_n)

    sa = stats(results_a)
    sb = stats(results_b)

    print("\n" + "=" * 60)
    print(f"  {'Metryka':<22} {'Runda A (baseline)':>18} {'Runda B (HTRI)':>16}")
    print("  " + "-" * 56)
    print(f"  {'n_threads':<22} {baseline_n:>18} {htri_n:>16}")
    print(f"  {'czas avg (ms)':<22} {sa['ms_avg']:>16.0f}ms {sb['ms_avg']:>14.0f}ms")
    print(f"  {'czas std (ms)':<22} {sa['ms_std']:>16.0f}ms {sb['ms_std']:>14.0f}ms")
    print(f"  {'chars/ms avg':<22} {sa['cpm_avg']:>16.3f}   {sb['cpm_avg']:>14.3f}")
    print(f"  {'chars/ms std':<22} {sa['cpm_std']:>16.3f}   {sb['cpm_std']:>14.3f}")

    if sa["ms_avg"] > 0 and sb["ms_avg"] > 0:
        speedup = (sa["ms_avg"] - sb["ms_avg"]) / sa["ms_avg"] * 100
        jitter_change = (sb["ms_std"] - sa["ms_std"]) / max(sa["ms_std"], 1) * 100
        print()
        print(f"  Δ czas:    {speedup:+.1f}%  (+ = B szybsze)")
        print(f"  Δ jitter:  {jitter_change:+.1f}%  (- = B stabilniejsze)")

    print("=" * 60)

    # Zapisz wyniki
    out = Path(__file__).parent.parent / "integration" / "reports" / "htri_bench_result.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "baseline_n": baseline_n, "htri_n": htri_n, "htri_coherence": htri_r,
        "round_a": sa, "round_b": sb,
    }, indent=2))
    print(f"\n  Wyniki zapisane: {out}")


if __name__ == "__main__":
    main()
