#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PKG_PARENT = ROOT.parent
for candidate in (PKG_PARENT, ROOT):
    candidate_str = str(candidate)
    if candidate_str not in sys.path:
        sys.path.insert(0, candidate_str)

from ciel_omega.ciel import CielEngine, build_default_bundle  # noqa: E402


def _json_default(obj: Any) -> Any:
    try:
        import numpy as np  # noqa: WPS433
        if isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        if isinstance(obj, (np.floating, np.integer)):
            return obj.item()
    except Exception:
        pass
    return str(obj)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run full CIEL local GGUF pipeline via bundled llama-server")
    parser.add_argument("text", nargs="?", default="Explain your current coherence state briefly.")
    parser.add_argument("--context", default="dialogue")
    parser.add_argument("--profile", choices=["lite", "standard", "science"], default="lite")
    parser.add_argument("--model-path", default="", help="Absolute path to an external GGUF model.")
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--ctx", type=int, default=1024)
    parser.add_argument("--skip-aux", action="store_true")
    args = parser.parse_args()

    if args.model_path:
        import os
        os.environ["CIEL_GGUF_MODEL_PATH"] = args.model_path

    bundle = build_default_bundle(
        backend="gguf",
        gguf_n_ctx=args.ctx,
        gguf_n_threads=args.threads,
        gguf_system_prompt=(
            "You are CIEL/Ω. Use the supplied state, preserve coherence, and answer directly."
        ),
    )
    engine = CielEngine(
        language_backend=bundle.primary_for(args.profile),
        aux_backend=None if args.skip_aux else bundle.analysis,
    )
    dialogue = [{"role": "user", "content": args.text}]
    result = engine.interact(args.text, dialogue, context=args.context, use_aux_analysis=not args.skip_aux)
    print(json.dumps(result, indent=2, ensure_ascii=False, default=_json_default))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
