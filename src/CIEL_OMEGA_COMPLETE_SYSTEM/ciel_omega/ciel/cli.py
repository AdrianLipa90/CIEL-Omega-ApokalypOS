"""Canonical CLI helpers routed through the Omega communication surface.

The CLI no longer bypasses the orchestrator by talking directly to the engine.
It uses the canonical local communication client for one-shot calls and smoke
probes.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

import numpy as np

_OMEGA_ROOT = Path(__file__).resolve().parents[1]
if str(_OMEGA_ROOT) not in sys.path:
    sys.path.insert(0, str(_OMEGA_ROOT))

from ciel_client import CIELClient


def _run_client(text: str) -> Dict[str, Any]:
    client = CIELClient()
    try:
        return client.process(text, use_llm=False)
    finally:
        client.shutdown()


def _json_default(obj: Any) -> Any:
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (np.floating, np.integer)):
        return obj.item()
    return str(obj)


def run_engine() -> None:
    parser = argparse.ArgumentParser(description="Run the canonical CIEL/Ω local client over a prompt")
    parser.add_argument(
        "text",
        nargs="?",
        default="hello from CIEL",
        help="Input text to feed into the canonical local communication surface",
    )
    args = parser.parse_args()
    result = _run_client(args.text)
    print(json.dumps(result, indent=2, sort_keys=True, default=_json_default, ensure_ascii=False))


def smoke_test() -> None:
    client = CIELClient()
    try:
        result = client.handshake()
    finally:
        client.shutdown()
    ok = result.get("status") in {"ok", "cold"}
    print(json.dumps({
        "status": "OK" if ok else "FAILED",
        "surface": result.get("surface", "CIELClient"),
        "orchestrator": result.get("orchestrator", "CIELOrchestrator"),
        "engine": result.get("engine"),
        "schumann_hz": result.get("schumann_hz", 7.83),
    }, indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    run_engine()
