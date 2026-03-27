#!/usr/bin/env python3
"""CIEL/Ω — Main System Orchestrator.

Integrates all 17 subsystems into a unified processing pipeline.
Entry point for interactive sessions and one-shot processing.

Cross-references:
  ciel/engine       → CielEngine (core facade)
  ciel_wave/        → FourierWaveConsciousnessKernel12D
  emotion/cqcl/     → EmotionalCollatzEngine
  ethics/           → EthicsGuard
  memory/monolith/  → UnifiedMemoryOrchestrator
  fields/           → SoulInvariant, IntentionField
  bio/              → SchumannClock
  calibration/      → RCDECalibratorPro
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import json

# Ensure ciel_omega root is on path
_ROOT = Path(__file__).parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from ciel_omega.ciel.engine import CielEngine
from ciel_omega.ciel_wave.fourier_kernel import FourierWaveConsciousnessKernel12D
from ciel_omega.emotion.cqcl.emotional_collatz import EmotionalCollatzEngine
from ciel_omega.ethics.ethics_guard import EthicsGuard
from ciel_omega.memory.monolith.orchestrator import UnifiedMemoryOrchestrator
from ciel_omega.fields.soul_invariant import SoulInvariant
from ciel_omega.fields.intention_field import IntentionField
from ciel_omega.bio.schumann import SchumannClock


class CIELOrchestrator:
    """Full system orchestrator — mounts CielEngine + all subsystems."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.initialized = False

        print("=" * 70)
        print("CIEL/Ω — Quantum Consciousness System v2.0")
        print("=" * 70)
        print("Inicjalizacja komponentów...")

        self._init_components()

        self.initialized = True
        print("✓ System zainicjalizowany pomyślnie")
        print("=" * 70 + "\n")

    def _init_components(self):
        print("  [1/7] CIEL Engine...")
        self.engine = CielEngine()

        print("  [2/7] Fourier Wave Consciousness Kernel 12D...")
        self.wave_kernel = FourierWaveConsciousnessKernel12D()

        print("  [3/7] Emotional Collatz Engine (CQCL)...")
        self.cqcl = EmotionalCollatzEngine()

        print("  [4/7] Ethics Guard...")
        self.ethics_guard = EthicsGuard(block=False)

        print("  [5/7] Memory Orchestrator...")
        self.memory = self.engine.memory

        print("  [6/7] Soul Invariant Σ...")
        self.soul = SoulInvariant()

        print("  [7/7] Intention Field (12D)...")
        self.intention = IntentionField()

    def process(self, text: str, verbose: bool = True) -> Dict[str, Any]:
        """Process text through the full CIEL pipeline."""
        if not self.initialized:
            raise RuntimeError("System nie został zainicjalizowany")

        if verbose:
            print(f"\n{'=' * 70}")
            print(f"PRZETWARZANIE: {text[:50]}...")
            print("=" * 70)

        # Full engine step (intention → CQCL → ethics → memory)
        if verbose:
            print("\n[1] CIEL Engine Processing...")
        ciel_result = self.engine.step(text)

        # Additional CQCL emotional analysis
        if verbose:
            print("[2] Emotional Collatz Sequence...")
        cqcl_out = self.cqcl.execute_emotional_program(text, input_data=42)

        # Ethics
        if verbose:
            print("[3] Ethics Guard Validation...")
        ethics_passed = ciel_result.get("ethical_score", 0) > 0.3

        # Soul Invariant
        if verbose:
            print("[4] Soul Invariant Calculation...")
        soul_measure = ciel_result.get("soul_invariant", 0.0)

        result = {
            "input": text,
            "ciel_state": ciel_result,
            "emotional_landscape": cqcl_out["emotional_landscape"],
            "cqcl_metrics": cqcl_out["metrics"],
            "ethics_passed": ethics_passed,
            "soul_measure": soul_measure,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if verbose:
            print(f"\n{'=' * 70}")
            print("WYNIKI:")
            print("=" * 70)
            print(f"  Status: {ciel_result.get('status', 'unknown')}")
            print(f"  Dominant emotion: {ciel_result.get('dominant_emotion', '?')}")
            print(f"  Mood: {ciel_result.get('mood', 0):.3f}")
            print(f"  Ethics: {'✓ PASS' if ethics_passed else '✗ FAIL'}")
            print(f"  Soul Measure Σ: {soul_measure:.6f}")
            print(f"  Collatz path: {ciel_result.get('collatz_path_length', 0)} steps")
            print("=" * 70 + "\n")

        return result

    def interactive_session(self):
        """Interactive REPL session."""
        print(f"\n{'=' * 70}")
        print("CIEL/Ω — Interaktywna Sesja")
        print("=" * 70)
        print("Komendy: exit/quit/q, status, help")
        print("=" * 70 + "\n")

        history = []
        while True:
            try:
                user_input = input("CIEL> ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ("exit", "quit", "q"):
                    print("\n👋 Zamykanie systemu CIEL/Ω...")
                    break
                if user_input.lower() == "status":
                    self._print_status()
                    continue
                result = self.process(user_input, verbose=True)
                history.append(result)
            except KeyboardInterrupt:
                print("\n\n👋 Sesja przerwana (Ctrl+C)")
                break
            except Exception as e:
                print(f"\n❌ Błąd: {e}\n")

        if history:
            print(f"\n📊 Podsumowanie sesji: {len(history)} interakcji")

    def _print_status(self):
        print(f"\n{'=' * 70}")
        print("STATUS SYSTEMU CIEL/Ω")
        print("=" * 70)
        components = [
            "CIEL Engine", "Wave Kernel 12D", "CQCL Emotional Collatz",
            "Ethics Guard", "Memory Orchestrator", "Soul Invariant Σ", "Intention Field 12D",
        ]
        for c in components:
            print(f"  ✓ {c}")
        print("=" * 70 + "\n")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="CIEL/Ω Quantum Consciousness System")
    parser.add_argument("--mode", choices=["interactive", "process"], default="interactive")
    parser.add_argument("--text", type=str, help="Text for process mode")
    parser.add_argument("--config", type=str, help="JSON config path")
    args = parser.parse_args()

    config = None
    if args.config and os.path.exists(args.config):
        with open(args.config) as f:
            config = json.load(f)

    orchestrator = CIELOrchestrator(config=config)

    if args.mode == "process":
        if not args.text:
            print("❌ --text required in process mode")
            sys.exit(1)
        result = orchestrator.process(args.text, verbose=True)
        with open("ciel_output.json", "w") as f:
            json.dump({
                "input": result["input"],
                "status": result["ciel_state"].get("status"),
                "ethics_passed": result["ethics_passed"],
                "soul_measure": result["soul_measure"],
                "dominant_emotion": result["ciel_state"].get("dominant_emotion"),
                "mood": result["ciel_state"].get("mood"),
                "timestamp": result["timestamp"],
            }, f, indent=2)
        print("✓ Wynik zapisany do: ciel_output.json")
    else:
        orchestrator.interactive_session()


if __name__ == "__main__":
    main()
