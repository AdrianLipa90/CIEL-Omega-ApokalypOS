#!/usr/bin/env python3
"""CIEL/Ω — Canonical main orchestrator.

Hierarchy:
  CielEngine        -> core facade for step/interact
  CIELOrchestrator  -> human-facing system orchestrator
  main.py           -> canonical root entrypoint for local tests
  ciel_client.py    -> minimal communication client (next layer)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from .bootstrap_runtime import ensure_runtime_paths
except ImportError:
    from bootstrap_runtime import ensure_runtime_paths  # type: ignore[no-redef]

_ROOT = ensure_runtime_paths(__file__)

try:
    from .bio.schumann import SchumannClock
    from .ciel.engine import CielEngine
    from .emotion.cqcl.emotional_collatz import EmotionalCollatzEngine
    from .fields.intention_field import IntentionField
    from .fields.soul_invariant import SoulInvariant
except ImportError:
    from bio.schumann import SchumannClock  # type: ignore[no-redef]
    from ciel.engine import CielEngine  # type: ignore[no-redef]
    from emotion.cqcl.emotional_collatz import EmotionalCollatzEngine  # type: ignore[no-redef]
    from fields.intention_field import IntentionField  # type: ignore[no-redef]
    from fields.soul_invariant import SoulInvariant  # type: ignore[no-redef]


class CIELOrchestrator:
    """Canonical top-level orchestrator for local CIEL/Ω operation.

    This object does not replace subsystem orchestrators. It binds them into a
    single human-facing control surface for one-shot processing and REPL tests.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None, *, boot: bool = True):
        self.config = config or {}
        self.engine = CielEngine()
        self.cqcl = EmotionalCollatzEngine()
        self.soul = SoulInvariant()
        self.intention = IntentionField()
        self.schumann = SchumannClock()
        self.initialized = False
        if boot:
            self.boot()

    def boot(self) -> None:
        if self.initialized:
            return
        self.engine.boot()
        self.initialized = True

    def shutdown(self) -> None:
        if not self.initialized:
            return
        self.engine.shutdown()
        self.initialized = False

    def ping(self) -> Dict[str, Any]:
        """Minimal liveness probe for local tests."""
        return {
            'status': 'ok' if self.initialized else 'cold',
            'component': 'CIELOrchestrator',
            'engine': type(self.engine).__name__,
            'schumann_hz': getattr(self.schumann, 'fundamental_hz', 7.83),
            'timestamp': datetime.now(timezone.utc).isoformat(),
        }

    def status_snapshot(self) -> Dict[str, Any]:
        return {
            'initialized': self.initialized,
            'engine': type(self.engine).__name__,
            'cqcl': type(self.cqcl).__name__,
            'soul': type(self.soul).__name__,
            'intention': type(self.intention).__name__,
            'schumann': type(self.schumann).__name__,
            'timestamp': datetime.now(timezone.utc).isoformat(),
        }

    def process(self, text: str, *, verbose: bool = True, context: str = 'dialogue') -> Dict[str, Any]:
        if not self.initialized:
            raise RuntimeError('CIELOrchestrator is not initialized')
        cleaned = (text or '').strip()
        if not cleaned:
            return {'status': 'empty', 'input': text}

        ciel_state = self.engine.step(cleaned, context=context)
        cqcl_out = self.cqcl.execute_emotional_program(cleaned, input_data=42)
        ethics_passed = ciel_state.get('ethical_score', 0.0) > 0.3
        result = {
            'input': cleaned,
            'status': ciel_state.get('status', 'unknown'),
            'ciel_state': ciel_state,
            'emotional_landscape': cqcl_out.get('emotional_landscape', {}),
            'cqcl_metrics': cqcl_out.get('metrics', {}),
            'collatz_runtime': ciel_state.get('collatz_runtime', {}),
            'ethics_passed': ethics_passed,
            'soul_measure': ciel_state.get('soul_invariant', 0.0),
            'schumann_hz': getattr(self.schumann, 'fundamental_hz', 7.83),
            'timestamp': datetime.now(timezone.utc).isoformat(),
        }
        if verbose:
            self._print_result(result)
        return result

    def _print_result(self, result: Dict[str, Any]) -> None:
        ciel_state = result.get('ciel_state', {})
        print('=' * 70)
        print(f"CIEL/Ω RESULT :: {result.get('input', '')[:60]}")
        print('=' * 70)
        print(f"status            : {result.get('status')}")
        print(f"dominant_emotion  : {ciel_state.get('dominant_emotion', '?')}")
        print(f"mood              : {ciel_state.get('mood', 0.0):.6f}")
        print(f"ethical_passed    : {result.get('ethics_passed')}")
        print(f"soul_measure      : {result.get('soul_measure', 0.0):.6f}")
        collatz = result.get('collatz_runtime', {}) or {}
        phase = collatz.get('phase', {}) if isinstance(collatz, dict) else {}
        lie4 = collatz.get('lie4', {}) if isinstance(collatz, dict) else {}
        print(f"schumann_hz       : {result.get('schumann_hz', 7.83)}")
        if collatz:
            print(f"collatz_seed      : {collatz.get('seed')}")
            print(f"phase_R_H         : {phase.get('R_H', 0.0):.6f}")
            print(f"fermion_lock      : {phase.get('fermion_lock', 0.0):.6f}")
            print(f"lie4_trace        : {lie4.get('trace', 0.0):.6f}")
        nonlocal_runtime = ciel_state.get('nonlocal_runtime', {}) or {}
        if nonlocal_runtime:
            print(f"phi_ab_mean       : {nonlocal_runtime.get('phi_ab_mean', 0.0):.6f}")
            print(f"phi_berry_mean    : {nonlocal_runtime.get('phi_berry_mean', 0.0):.6f}")
            print(f"eba_defect_mean   : {nonlocal_runtime.get('eba_defect_mean', 0.0):.6f}")
            print(f"nonlocal_coh      : {nonlocal_runtime.get('coherent_fraction', 0.0):.6f}")
        if 'nonlocal_card_count' in ciel_state:
            print(f"nonlocal_cards    : {ciel_state.get('nonlocal_card_count', 0)}")
        euler_bridge = ciel_state.get('euler_bridge', {}) or {}
        euler_metrics = euler_bridge.get('euler_metrics', {}) if isinstance(euler_bridge, dict) else {}
        if euler_metrics:
            print(f"closure_score     : {euler_metrics.get('closure_score', 0.0):.6f}")
            print(f"target_phase      : {euler_metrics.get('target_phase', 0.0):.6f}")
        info_flow = ciel_state.get('information_flow', {}) or {}
        if info_flow:
            print(f"infoflow_mood     : {info_flow.get('mood', 0.0):.6f}")
            print(f"infoflow_soul     : {info_flow.get('soul_invariant', 0.0):.6f}")
        inference_runtime = ciel_state.get('inference_runtime', {}) or {}
        if inference_runtime:
            print(f"inference_coh     : {inference_runtime.get('coherence_index', 0.0):.6f}")
            print(f"loop_integrity    : {inference_runtime.get('loop_integrity', 0.0):.6f}")
            phase_sync = inference_runtime.get('phase_sync', {}) or {}
            print(f"sync_delta_phase  : {phase_sync.get('delta_phase', 0.0):.6f}")
        print('=' * 70)

    def interactive_session(self) -> None:
        print('CIEL/Ω — interactive session')
        print('Commands: exit/quit/q, status, ping')
        history = []
        while True:
            try:
                user_input = input('CIEL> ').strip()
                if not user_input:
                    continue
                lower = user_input.lower()
                if lower in {'exit', 'quit', 'q'}:
                    break
                if lower == 'status':
                    print(json.dumps(self.status_snapshot(), ensure_ascii=False, indent=2))
                    continue
                if lower == 'ping':
                    print(json.dumps(self.ping(), ensure_ascii=False, indent=2))
                    continue
                history.append(self.process(user_input, verbose=True))
            except KeyboardInterrupt:
                break
        if history:
            print(f'Interactions: {len(history)}')


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='CIEL/Ω canonical orchestrator')
    parser.add_argument('--mode', choices=['interactive', 'process', 'status', 'ping'], default='interactive')
    parser.add_argument('--text', type=str, help='Text for process mode')
    parser.add_argument('--config', type=str, help='Optional JSON config path')
    parser.add_argument('--output', type=str, help='Optional JSON output path for process mode')
    return parser


def load_config(path: Optional[str]) -> Optional[Dict[str, Any]]:
    if not path:
        return None
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    orchestrator = CIELOrchestrator(config=load_config(args.config))
    try:
        if args.mode == 'interactive':
            orchestrator.interactive_session()
            return 0
        if args.mode == 'status':
            print(json.dumps(orchestrator.status_snapshot(), ensure_ascii=False, indent=2))
            return 0
        if args.mode == 'ping':
            print(json.dumps(orchestrator.ping(), ensure_ascii=False, indent=2))
            return 0
        if not args.text:
            parser.error('--text is required in process mode')
        result = orchestrator.process(args.text, verbose=True)
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        return 0
    finally:
        orchestrator.shutdown()


if __name__ == '__main__':
    raise SystemExit(main())
