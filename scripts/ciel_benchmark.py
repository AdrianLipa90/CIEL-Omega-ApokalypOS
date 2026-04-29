#!/usr/bin/env python3
"""
CIEL Benchmark — pomiar energii i jakości modeli GGUF

Metryki:
  - Czas generacji (s)
  - Tokeny/sekundę
  - CPU% podczas generacji (proxy energii)
  - Energia = czas × avg_cpu% (arbitrarne jednostki)
  - Jakość: długość sensownej odpowiedzi, brak powtórzeń, spójność

Użycie:
  python scripts/ciel_benchmark.py
"""
from __future__ import annotations

import time
import threading
import statistics
from pathlib import Path

import psutil

MODELS = {
    "TinyLlama-1.1B": Path.home() / ".local/share/ciel/models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
    "Lucy-128k":       Path.home() / ".local/share/Jan/data/llamacpp/models/lucy_128k-Q4_K_M/model.gguf",
}

PROMPTS = [
    "Wyjaśnij w jednym zdaniu czym jest holonomia Berry'ego.",
    "Co to jest relacja semantyczna między podmiotami w grafie wiedzy?",
    "Jak Kuramoto model opisuje synchronizację oscylatorów?",
]

MAX_TOKENS = 80
N_GPU_LAYERS = 0  # CPU only dla równego porównania


def measure_cpu_during(fn, interval=0.2):
    """Uruchom fn() i mierz CPU% co interval sekund. Zwróć (result, cpu_samples)."""
    cpu_samples = []
    stop = threading.Event()

    def _poll():
        while not stop.is_set():
            cpu_samples.append(psutil.cpu_percent(interval=interval))

    t = threading.Thread(target=_poll, daemon=True)
    t.start()
    result = fn()
    stop.set()
    t.join()
    return result, cpu_samples


def quality_score(text: str) -> float:
    """
    Prosty scoring jakości odpowiedzi (0-1):
    - długość (więcej = lepiej, do limitu)
    - brak powtórzeń słów (uniq/total)
    - brak śmieciowych tokenów
    """
    if not text or len(text) < 10:
        return 0.0
    words = text.lower().split()
    if not words:
        return 0.0
    uniqueness = len(set(words)) / len(words)
    length_score = min(len(words) / 40, 1.0)  # 40 słów = max
    garbage = sum(1 for w in words if len(w) > 20) / len(words)
    return round((uniqueness * 0.5 + length_score * 0.4 - garbage * 0.1), 3)


def benchmark_model(name: str, path: Path) -> dict:
    from llama_cpp import Llama

    print(f"\n{'='*60}")
    print(f"  Ładuję: {name} ({path.stat().st_size/1024**3:.2f}GB)")

    t_load_start = time.time()
    llm = Llama(model_path=str(path), n_ctx=512,
                n_gpu_layers=N_GPU_LAYERS, verbose=False)
    t_load = time.time() - t_load_start
    print(f"  Czas ładowania: {t_load:.1f}s")

    results = []
    for i, prompt in enumerate(PROMPTS):
        messages = [{"role": "user", "content": prompt}]
        print(f"  Prompt {i+1}/{len(PROMPTS)}: {prompt[:50]}...")

        def _infer():
            return llm.create_chat_completion(
                messages=messages, max_tokens=MAX_TOKENS, stream=False
            )

        t0 = time.time()
        result, cpu_samples = measure_cpu_during(_infer)
        t_gen = time.time() - t0

        text = result["choices"][0]["message"]["content"]
        n_tokens = result["usage"]["completion_tokens"]
        tok_per_sec = n_tokens / t_gen if t_gen > 0 else 0
        avg_cpu = statistics.mean(cpu_samples) if cpu_samples else 0
        energy = t_gen * avg_cpu  # czas × CPU% — proxy zużycia energii
        q = quality_score(text)

        print(f"    → {n_tokens} tokenów | {tok_per_sec:.1f} tok/s | "
              f"CPU {avg_cpu:.0f}% | energia={energy:.1f} | jakość={q:.3f}")
        print(f"    Odpowiedź: {text[:80]}...")

        results.append({
            "prompt": prompt,
            "tokens": n_tokens,
            "tok_per_sec": tok_per_sec,
            "t_gen": t_gen,
            "avg_cpu_pct": avg_cpu,
            "energy_proxy": energy,
            "quality": q,
            "text": text,
        })

    del llm  # zwolnij RAM

    avg = lambda key: statistics.mean(r[key] for r in results)
    return {
        "model": name,
        "size_gb": path.stat().st_size / 1024**3,
        "t_load_s": round(t_load, 1),
        "avg_tok_per_sec": round(avg("tok_per_sec"), 1),
        "avg_energy": round(avg("energy_proxy"), 1),
        "avg_quality": round(avg("quality"), 3),
        "avg_cpu_pct": round(avg("avg_cpu_pct"), 1),
        "results": results,
    }


def print_summary(benchmarks: list[dict]) -> None:
    print(f"\n{'='*60}")
    print("  SUMMARY")
    print(f"{'='*60}")
    print(f"{'Model':<20} {'Rozmiar':>8} {'tok/s':>7} {'Energia':>8} {'Jakość':>7} {'CPU%':>6}")
    print(f"{'-'*60}")
    for b in benchmarks:
        print(f"{b['model']:<20} {b['size_gb']:>7.2f}G "
              f"{b['avg_tok_per_sec']:>7.1f} "
              f"{b['avg_energy']:>8.1f} "
              f"{b['avg_quality']:>7.3f} "
              f"{b['avg_cpu_pct']:>6.1f}%")

    if len(benchmarks) == 2:
        a, b = benchmarks[0], benchmarks[1]
        print(f"\n  Stosunek energii:  {a['model']} / {b['model']} = "
              f"{a['avg_energy']/b['avg_energy']:.2f}×")
        print(f"  Stosunek jakości:  {a['model']} / {b['model']} = "
              f"{a['avg_quality']/b['avg_quality']:.2f}×")
        winner_energy  = a['model'] if a['avg_energy']  < b['avg_energy']  else b['model']
        winner_quality = a['model'] if a['avg_quality'] > b['avg_quality'] else b['model']
        print(f"\n  Oszczędniejszy:  {winner_energy}")
        print(f"  Lepsza jakość:   {winner_quality}")


if __name__ == "__main__":
    print("CIEL Benchmark — energia i jakość modeli GGUF")
    print(f"GPU layers: {N_GPU_LAYERS} (CPU only), max_tokens: {MAX_TOKENS}")

    available = {k: v for k, v in MODELS.items() if v.exists()}
    if not available:
        print("Brak modeli! Sprawdź ścieżki.")
        raise SystemExit(1)

    print(f"Modele do testu: {list(available.keys())}")

    benchmarks = []
    for name, path in available.items():
        b = benchmark_model(name, path)
        benchmarks.append(b)

    print_summary(benchmarks)
