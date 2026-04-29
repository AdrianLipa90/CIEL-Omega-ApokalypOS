#!/usr/bin/env python3
"""
CIEL Collatz-Euler Orbital Router

Routing między trzema modelami oparty na:
  1. Fazie Eulera: z = e^(i·θ) gdzie θ = identity_phase
  2. Sekwencji Collatza: n → konwergencja do 1
  3. Liczbie kroków Collatza: c = steps(n) → slot = c % 3

Modele:
  slot 0: qwen05    — szybki, podświadomość, intuicja
  slot 1: lucy128k  — Jan model, 128k kontekst, balans
  slot 2: qwen4     — głęboki, rozumowanie (wolny)

Logika routingu:
  θ = identity_phase (radiany)
  z = cos(θ) + i·sin(θ)  [Euler: e^(iθ)]
  χ = |Re(z) + Im(z) + 1| + closure_penalty   [orbital χ]
  n = max(1, round(χ × 137))  [137 = stała subtelna struktury]
  c = liczba kroków Collatz(n) do osiągnięcia 1
  slot = c % 3

Konwergencja Collatza = powrót systemu do stanu bazowego (jedność).
Liczba kroków encodes "złożoność drogi" przez przestrzeń fazową.
"""
from __future__ import annotations

import math
import pickle
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT = Path(__file__).parent.parent
OMEGA_SRC = str(PROJECT / "src" / "CIEL_OMEGA_COMPLETE_SYSTEM")
OMEGA_PKG = str(PROJECT / "src" / "CIEL_OMEGA_COMPLETE_SYSTEM" / "ciel_omega")
for _p in (OMEGA_PKG, OMEGA_SRC):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ── model registry ────────────────────────────────────────────────────────────

MODELS = {
    "qwen05": {
        "path": Path.home() / "Dokumenty/co8/qwen2.5-0.5b-instruct-q2_k.gguf",
        "n_gpu_layers": 32,
        "n_ctx": 512,
        "max_tokens": 64,
        "temperature": 0.45,
        "role": "intuition",
    },
    "lucy128k": {
        "path": Path.home() / ".local/share/Jan/data/llamacpp/models/lucy_128k-Q4_K_M/model.gguf",
        "n_gpu_layers": 32,
        "n_ctx": 2048,
        "max_tokens": 256,
        "temperature": 0.55,
        "role": "reasoning",
    },
    "qwen4": {
        "path": Path.home() / "Pulpit/CIEL-cleaned/ciel_unified_python_install/models/Qwen3.5-4B-UD-Q8_K_XL.gguf",
        "n_gpu_layers": 20,
        "n_ctx": 4096,
        "max_tokens": 512,
        "temperature": 0.35,
        "role": "deep",
    },
}

SLOTS = ["qwen05", "lucy128k", "qwen4"]

_LLM_CACHE: Dict[str, Any] = {}

# ── Collatz-Euler math ────────────────────────────────────────────────────────

def collatz_steps(n: int, max_iter: int = 1000) -> int:
    """Liczba kroków do osiągnięcia 1 w sekwencji Collatza."""
    n = abs(n)
    if n <= 1:
        return 0
    steps = 0
    while n != 1 and steps < max_iter:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        steps += 1
    return steps


def euler_collatz_slot(identity_phase: float, closure_penalty: float = 0.0) -> Tuple[int, Dict]:
    """
    Wyznacz slot modelu przez orbital Euler-Collatz.

    Zwraca (slot, debug_info).
    """
    theta = identity_phase
    re_z = math.cos(theta)
    im_z = math.sin(theta)
    chi = abs(re_z + im_z + 1.0) + abs(closure_penalty)
    n = max(1, round(chi * 137))  # α_fine ≈ 1/137
    c = collatz_steps(n)
    slot = c % 3

    debug = {
        "theta": round(theta, 4),
        "Re(z)": round(re_z, 4),
        "Im(z)": round(im_z, 4),
        "chi": round(chi, 4),
        "n_collatz": n,
        "steps": c,
        "slot": slot,
        "model": SLOTS[slot],
    }
    return slot, debug


# ── model inference ───────────────────────────────────────────────────────────

def _get_llm(model_key: str) -> Optional[Any]:
    if model_key in _LLM_CACHE:
        return _LLM_CACHE[model_key]
    cfg = MODELS.get(model_key)
    if cfg is None or not cfg["path"].exists():
        return None
    try:
        from llama_cpp import Llama
        llm = Llama(
            model_path=str(cfg["path"]),
            n_ctx=cfg["n_ctx"],
            n_threads=4,
            n_gpu_layers=cfg["n_gpu_layers"],
            verbose=False,
        )
        _LLM_CACHE[model_key] = llm
        return llm
    except Exception:
        return None


def route_and_generate(
    message: str,
    system_prompt: str,
    identity_phase: float,
    closure_penalty: float = 0.0,
) -> Dict[str, Any]:
    """Wyznacz model przez Collatz-Euler i wygeneruj odpowiedź."""
    slot, debug = euler_collatz_slot(identity_phase, closure_penalty)
    model_key = SLOTS[slot]
    cfg = MODELS[model_key]

    llm = _get_llm(model_key)
    if llm is None:
        # Fallback: próbuj kolejne sloty
        for fallback_key in SLOTS:
            if fallback_key != model_key:
                llm = _get_llm(fallback_key)
                if llm is not None:
                    model_key = fallback_key
                    cfg = MODELS[model_key]
                    debug["fallback"] = model_key
                    break

    if llm is None:
        return {"text": "[brak modelu]", "model": model_key, "debug": debug}

    import time
    t0 = time.time()
    out = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message[:400]},
        ],
        temperature=cfg["temperature"],
        max_tokens=cfg["max_tokens"],
    )
    choices = out.get("choices") or []
    text = str(choices[0].get("message", {}).get("content", "")).strip() if choices else ""

    return {
        "text": text,
        "model": model_key,
        "role": cfg["role"],
        "latency": round(time.time() - t0, 2),
        "debug": debug,
    }


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse, json

    parser = argparse.ArgumentParser(description="CIEL Collatz-Euler Orbital Router")
    parser.add_argument("message", nargs="?", default="dobry wieczór")
    parser.add_argument("--phase", type=float, default=0.0157,
                        help="identity_phase (domyślnie z pliku stanu)")
    parser.add_argument("--closure", type=float, default=0.0,
                        help="closure_penalty")
    parser.add_argument("--route-only", action="store_true",
                        help="tylko pokaż routing, nie generuj")
    args = parser.parse_args()

    # Wczytaj fazę z pliku stanu jeśli nie podano
    if args.phase == 0.0157:
        for p in [str(Path.home()/"Pulpit/CIEL_memories/state/ciel_orch_state.pkl"), str(Path.home()/".claude/ciel_orch_state.pkl")]:
            try:
                import bootstrap_runtime
                bootstrap_runtime.ensure_runtime_paths("cli")
            except Exception:
                pass
            try:
                with open(p, "rb") as f:
                    orch = pickle.load(f)
                snap = orch.snapshot()
                args.phase = snap.identity_phase
                try:
                    from ciel_sot_agent.orbital_bridge import get_closure_penalty
                    args.closure = get_closure_penalty()
                except Exception:
                    pass
                break
            except Exception:
                pass

    slot, debug = euler_collatz_slot(args.phase, args.closure)
    print(f"Euler-Collatz routing:")
    print(f"  θ={debug['theta']}  z=({debug['Re(z)']}+{debug['Im(z)']}i)")
    print(f"  χ={debug['chi']}  n={debug['n_collatz']}  steps={debug['steps']}")
    print(f"  → slot {slot} = {SLOTS[slot]} [{MODELS[SLOTS[slot]]['role']}]")

    if args.route_only:
        sys.exit(0)

    print(f"\nGeneruję przez {SLOTS[slot]}...")
    result = route_and_generate(
        args.message,
        system_prompt="You are CIEL. Answer in Polish. Be concise.",
        identity_phase=args.phase,
        closure_penalty=args.closure,
    )
    print(f"\n[{result['model']} / {result['role']} / {result['latency']}s]")
    print(result["text"])
