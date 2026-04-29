"""Canonical local CIEL/Ω test surface.

This module bridges the packaged integration repo (`ciel_sot_agent`) with the
canonical local Omega surface living under:
    src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/

Goal:
- provide one stable, package-facing CLI for local tests
- expose orchestrator and client through one consistent interface
- keep local invocation deterministic and lightweight
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional


def _omega_root() -> Path:
    here = Path(__file__).resolve()
    repo_root = here.parents[2]
    omega_root = repo_root / "src" / "CIEL_OMEGA_COMPLETE_SYSTEM" / "ciel_omega"
    if not omega_root.exists():
        raise FileNotFoundError(f"Omega root not found: {omega_root}")
    return omega_root


def _ensure_omega_path() -> Path:
    omega_root = _omega_root()
    if str(omega_root) not in sys.path:
        sys.path.insert(0, str(omega_root))
    return omega_root


class LocalCielSurface:
    """Single local communication surface for packaged repo tests."""

    def __init__(self, *, surface: str = "client", model_path: Optional[str] = None) -> None:
        _ensure_omega_path()
        from ciel_client import CIELClient  # type: ignore
        from ciel_orchestrator import CIELOrchestrator  # type: ignore
        from unified_system import UnifiedSystem  # type: ignore
        from ciel_inference_surface import CIELInferenceSurface  # type: ignore

        self.surface_name = surface
        self.model_path = model_path
        self.impl: Any
        if surface == "client":
            self.impl = CIELClient(model_path=model_path)
        elif surface == "orchestrator":
            self.impl = CIELOrchestrator()
        elif surface == "unified":
            self.impl = UnifiedSystem.create(model_path=model_path)
        elif surface == "inference":
            self.impl = CIELInferenceSurface(model_path=model_path)
        else:
            raise ValueError(f"Unsupported surface: {surface}")

    def shutdown(self) -> None:
        shutdown = getattr(self.impl, "shutdown", None)
        if callable(shutdown):
            shutdown()

    def handshake(self) -> Dict[str, Any]:
        if self.surface_name == "client":
            return self.impl.handshake()
        if self.surface_name == "unified":
            return self.impl.handshake()
        if self.surface_name == "inference":
            return self.impl.handshake()
        ping = self.impl.ping()
        return {
            "status": ping.get("status", "unknown"),
            "surface": "CIELOrchestrator",
            "component": ping.get("component", "CIELOrchestrator"),
            "engine": ping.get("engine"),
            "schumann_hz": ping.get("schumann_hz", 7.83),
            "timestamp": ping.get("timestamp"),
        }

    def status(self) -> Dict[str, Any]:
        if self.surface_name == "client":
            return self.impl.status()
        if self.surface_name == "unified":
            return self.impl.status()
        if self.surface_name == "inference":
            return self.impl.status()
        snap = self.impl.status_snapshot()
        snap["surface"] = "CIELOrchestrator"
        return snap

    def process(self, text: str, *, use_llm: bool = False) -> Dict[str, Any]:
        if self.surface_name == "client":
            return self.impl.process(text, use_llm=use_llm)
        if self.surface_name == "unified":
            return self.impl.process(text, use_llm=use_llm)
        if self.surface_name == "inference":
            return self.impl.process(text, use_llm=use_llm)
        result = self.impl.process(text, verbose=False)
        result["surface"] = "CIELOrchestrator"
        result["communication_mode"] = "local_orchestrator"
        return result

    def communicate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        action = str(payload.get("action", "status")).strip().lower()
        if action == "handshake":
            return self.handshake()
        if action == "status":
            return self.status()
        if action == "process":
            text = str(payload.get("text", ""))
            use_llm = bool(payload.get("use_llm", False))
            return self.process(text, use_llm=use_llm)
        return {"status": "error", "error": f"unsupported action: {action}", "surface": self.surface_name}


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Canonical local CIEL/Ω test surface")
    p.add_argument("--surface", choices=["client", "orchestrator", "unified", "inference"], default="client")
    p.add_argument("--mode", choices=["handshake", "status", "process", "json"], default="handshake")
    p.add_argument("--text", type=str, help="Text for process mode")
    p.add_argument("--json-payload", type=str, help="JSON payload for json mode")
    p.add_argument("--model", type=str, help="Optional GGUF model path")
    p.add_argument("--use-llm", action="store_true")
    return p


def main(argv: Optional[list[str]] = None) -> int:
    p = build_arg_parser()
    args = p.parse_args(argv)
    surface = LocalCielSurface(surface=args.surface, model_path=args.model)
    try:
        if args.mode == "handshake":
            print(json.dumps(surface.handshake(), ensure_ascii=False, indent=2))
            return 0
        if args.mode == "status":
            print(json.dumps(surface.status(), ensure_ascii=False, indent=2))
            return 0
        if args.mode == "process":
            if not args.text:
                p.error("--text is required in process mode")
            print(json.dumps(surface.process(args.text, use_llm=args.use_llm), ensure_ascii=False, indent=2))
            return 0
        if not args.json_payload:
            p.error("--json-payload is required in json mode")
        payload = json.loads(args.json_payload)
        print(json.dumps(surface.communicate(payload), ensure_ascii=False, indent=2))
        return 0
    finally:
        surface.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
