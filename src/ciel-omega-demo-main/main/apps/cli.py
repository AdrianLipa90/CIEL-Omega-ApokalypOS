"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, List, Optional

from main.adam.demo import bootstrap_adam
from main.cognition.cognitive_loop import run_demo
from main.core.ciel_constants import DEFAULT_CONSTANTS
from main.core.config import CielConfig
from main.emotion.emotional_collatz import demo_emotional_collatz
from main.experiments.lab17 import make_lab_registry
from main.kernels.registry import KERNELS
from main.omega.batch18 import demo as omega18_demo
from main.omega.runtime20 import run_demo as omega20_demo
from main.spectral.wave12d import FourierWaveConsciousnessKernel12D


def _parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog='ciel_cli')
    sub = p.add_subparsers(dest='cmd', required=True)

    ls = sub.add_parser('list')
    ls.add_argument('--json', action='store_true')

    cog = sub.add_parser('cognition')
    cog.add_argument('--steps', type=int, default=12)
    cog.add_argument('--n', type=int, default=64)
    cog.add_argument('--json', action='store_true')

    exp = sub.add_parser('experiments')
    exp.add_argument('--list', action='store_true')
    exp.add_argument('--names', default='')
    exp.add_argument('--json', action='store_true')

    o18 = sub.add_parser('omega18')
    o18.add_argument('--steps', type=int, default=12)
    o18.add_argument('--n', type=int, default=96)
    o18.add_argument('--json', action='store_true')

    o20 = sub.add_parser('omega20')
    o20.add_argument('--steps', type=int, default=20)
    o20.add_argument('--n', type=int, default=96)
    o20.add_argument('--backend-steps', type=int, default=3)
    o20.add_argument('--backend-dt', type=float, default=0.02)
    o20.add_argument('--every', type=int, default=0)
    o20.add_argument('--progress', action='store_true')
    o20.add_argument('--max-seconds', type=float, default=0.0)
    o20.add_argument('--json', action='store_true')

    emo = sub.add_parser('emotion')
    emo.add_argument('--json', action='store_true')

    ad = sub.add_parser('adam21')
    ad.add_argument('--json', action='store_true')
    ad.add_argument('--ritual', default='Closure_of_Logos')

    sp = sub.add_parser('spectral12d')
    sp.add_argument('--json', action='store_true')

    run = sub.add_parser('run')
    run.add_argument('--kernel', default='ciel0', choices=sorted(KERNELS.keys()))
    run.add_argument('--mode', default='fft', choices=['fft', 'nofft'])
    run.add_argument('--grid', type=int, default=64)
    run.add_argument('--length', type=float, default=10.0)
    run.add_argument('--steps', type=int, default=50)
    run.add_argument('--dt', type=float, default=0.1)
    run.add_argument('--every', type=int, default=5)
    run.add_argument('--json', action='store_true')

    return p.parse_args(argv)


def _run_kernel(args: argparse.Namespace) -> Dict[str, Any]:
    cfg = CielConfig(compute_mode=args.mode)
    factory = KERNELS[args.kernel]
    kernel = factory(cfg, int(args.grid), DEFAULT_CONSTANTS, float(args.length))

    last: Dict[str, float] = {}
    steps = int(args.steps)
    every = max(1, int(args.every))
    for i in range(1, steps + 1):
        last = kernel.step(dt=float(args.dt))
        if args.json:
            continue
        if i % every == 0 or i == steps:
            if {'resonance_mean', 'mass_mean', 'lambda0_mean'}.issubset(last.keys()):
                print(
                    f"step={i} resonance={last['resonance_mean']:.6f} "
                    f"mass={last['mass_mean']:.6e} lambda0={last['lambda0_mean']:.6e}"
                )
            else:
                print(f"step={i} metrics={json.dumps(last, ensure_ascii=False)}")

    return {'final': last}


def main(argv: Optional[List[str]] = None) -> int:
    ns = _parse_args(sys.argv[1:] if argv is None else argv)

    if ns.cmd == 'list':
        names = sorted(KERNELS.keys())
        if ns.json:
            print(json.dumps({'kernels': names}, ensure_ascii=False))
        else:
            for n in names:
                print(n)
        return 0

    if ns.cmd == 'experiments':
        reg = make_lab_registry()
        if ns.list:
            names = reg.list()
            if ns.json:
                print(json.dumps({'experiments': names}, ensure_ascii=False))
            else:
                for n in names:
                    print(n)
            return 0
        names = [s.strip() for s in str(ns.names).split(',') if s.strip()]
        if not names:
            names = reg.list()
        result = reg.run(names)
        if ns.json:
            print(json.dumps({'results': result}, ensure_ascii=False))
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if ns.cmd == 'omega18':
        result = omega18_demo(steps=int(ns.steps), n=int(ns.n))
        if ns.json:
            print(json.dumps({'result': result}, ensure_ascii=False))
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if ns.cmd == 'omega20':
        result = omega20_demo(
            steps=int(ns.steps),
            n=int(ns.n),
            backend_steps=int(ns.backend_steps),
            backend_dt=float(ns.backend_dt),
            every=int(ns.every),
            progress=bool(ns.progress),
            max_seconds=float(ns.max_seconds),
        )
        if ns.json:
            print(json.dumps({'result': result}, ensure_ascii=False))
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if ns.cmd == 'emotion':
        result = demo_emotional_collatz()
        if ns.json:
            print(json.dumps({'result': result}, ensure_ascii=False))
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if ns.cmd == 'adam21':
        result = bootstrap_adam(ritual=str(ns.ritual))
        if ns.json:
            print(json.dumps({'result': result}, ensure_ascii=False))
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if ns.cmd == 'spectral12d':
        kernel = FourierWaveConsciousnessKernel12D()
        result = kernel.run()
        if ns.json:
            print(json.dumps({'result': result}, ensure_ascii=False))
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if ns.cmd == 'cognition':
        logs = run_demo(steps=int(ns.steps), n=int(ns.n))
        if ns.json:
            print(json.dumps({'logs': logs}, ensure_ascii=False))
        else:
            tail = logs[-3:] if len(logs) >= 3 else logs
            for row in tail:
                t = row.get('t')
                intu = row.get('intuition')
                pred = row.get('prediction')
                dec = row.get('decision')
                print(f"t={t} intuition={intu} prediction={pred} decision={dec}")
        return 0

    if ns.cmd == 'run':
        result = _run_kernel(ns)
        if ns.json:
            print(json.dumps(result, ensure_ascii=False))
        return 0

    raise RuntimeError('unknown command')


if __name__ == '__main__':
    raise SystemExit(main())
