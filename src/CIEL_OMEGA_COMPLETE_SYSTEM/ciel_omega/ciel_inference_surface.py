#!/usr/bin/env python3
"""CIEL/Ω — canonical orbital-ethical inference surface.

This surface keeps inference outside InformationFlow while still grounding it in
canonical Omega state:
    CIELOrchestrator -> prepared state -> orbital/ethical inference surface

It supports a dry-run mode by default and only attempts GGUF-wrapped inference
when an explicit backend is available.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Optional

from bootstrap_runtime import ensure_runtime_paths

_ROOT = ensure_runtime_paths(__file__)

from ciel_orchestrator import CIELOrchestrator
from inference.middleware import build_orbital_ethical_inference_surface

try:
    from ciel.gguf_backends import GGUFPrimaryBackend
except Exception:  # pragma: no cover - optional local backend
    GGUFPrimaryBackend = None


class CIELInferenceSurface:
    """Canonical local surface for orbital-ethical inference."""

    def __init__(
        self,
        model_path: Optional[str] = None,
        *,
        n_ctx: int = 4096,
        n_threads: int = 8,
        n_gpu_layers: int = 0,
        temperature: float = 0.7,
        boot: bool = True,
    ) -> None:
        self.orchestrator = CIELOrchestrator(boot=boot)
        self.gguf_backend = None
        self.gguf_enabled = False
        self.gguf_backend_status = "disabled"
        if model_path and GGUFPrimaryBackend is not None:
            try:
                self.gguf_backend = GGUFPrimaryBackend(
                    model_path=model_path,
                    n_ctx=n_ctx,
                    n_threads=n_threads,
                    n_gpu_layers=n_gpu_layers,
                    temperature=temperature,
                    system_prompt=(
                        "You are CIEL/Ω inference surface. Stay aligned with the"
                        " orbital-ethical gate and do not override system state."
                    ),
                )
                self.gguf_enabled = True
                self.gguf_backend_status = "enabled"
            except Exception as exc:  # pragma: no cover - optional backend path
                self.gguf_backend = None
                self.gguf_enabled = False
                self.gguf_backend_status = f"unavailable:{type(exc).__name__}"

    def shutdown(self) -> None:
        self.orchestrator.shutdown()

    def handshake(self) -> Dict[str, Any]:
        ping = self.orchestrator.ping()
        return {
            "status": ping.get("status", "unknown"),
            "surface": "CIELInferenceSurface",
            "orchestrator": "CIELOrchestrator",
            "gguf_enabled": self.gguf_enabled,
            "gguf_backend_status": self.gguf_backend_status,
            "timestamp": ping.get("timestamp"),
        }

    def status(self) -> Dict[str, Any]:
        snap = self.orchestrator.status_snapshot()
        snap.update(
            {
                "surface": "CIELInferenceSurface",
                "gguf_enabled": self.gguf_enabled,
                "gguf_backend_status": self.gguf_backend_status,
            }
        )
        return snap

    def process(self, text: str, *, use_llm: bool = False) -> Dict[str, Any]:
        process_result = self.orchestrator.process(text, verbose=False)
        ciel_state = process_result.get("ciel_state", {}) or {}
        information_flow = ciel_state.get("information_flow", {}) or {}
        euler_bridge = ciel_state.get("euler_bridge", {}) or {}
        euler_metrics = euler_bridge.get("euler_metrics", {}) if isinstance(euler_bridge, dict) else {}
        target_phase = euler_metrics.get("target_phase", 0.0)
        ethical_score = float(ciel_state.get("ethical_score", 0.0) or 0.0)

        messages = None
        backend = None
        model = None
        if use_llm and self.gguf_backend is not None:
            backend = self.gguf_backend
            model = getattr(self.gguf_backend, "model_path", None) or str(getattr(self.gguf_backend, "model_name", "gguf-local"))
            messages = [{"role": "user", "content": text}]

        inference_runtime = build_orbital_ethical_inference_surface(
            flow_entry=information_flow,
            target_phase=target_phase,
            ethical_score=ethical_score,
            backend=backend,
            model=model,
            messages=messages,
            temperature=0.0,
            max_tokens=128,
        )

        return {
            "input": text,
            "status": process_result.get("status", "unknown"),
            "surface": "CIELInferenceSurface",
            "handshake": self.handshake(),
            "ethical_score": ethical_score,
            "orbital_context": {
                "target_phase": target_phase,
                "closure_score": euler_metrics.get("closure_score", 0.0),
            },
            "inference_runtime": inference_runtime,
            "gguf_enabled": self.gguf_enabled,
            "use_llm": bool(use_llm and self.gguf_enabled),
            "communication_mode": "orbital_ethical_inference_surface",
        }

    def communicate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        action = str(payload.get("action", "status")).strip().lower()
        if action == "handshake":
            return self.handshake()
        if action == "status":
            return self.status()
        if action == "process":
            return self.process(str(payload.get("text", "")), use_llm=bool(payload.get("use_llm", False)))
        return {"status": "error", "error": f"unsupported action: {action}", "surface": "CIELInferenceSurface"}


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="CIEL/Ω orbital-ethical inference surface")
    p.add_argument("--model", type=str, help="Optional GGUF model path")
    p.add_argument("--mode", choices=["handshake", "status", "process", "json"], default="handshake")
    p.add_argument("--text", type=str, help="Text for process mode")
    p.add_argument("--json-payload", type=str, help="JSON payload for json mode")
    p.add_argument("--n-ctx", type=int, default=4096)
    p.add_argument("--n-threads", type=int, default=8)
    p.add_argument("--n-gpu-layers", type=int, default=0)
    p.add_argument("--temperature", type=float, default=0.7)
    p.add_argument("--use-llm", action="store_true")
    return p


def main(argv: Optional[list[str]] = None) -> int:
    p = build_arg_parser()
    args = p.parse_args(argv)
    surface = CIELInferenceSurface(
        model_path=args.model,
        n_ctx=args.n_ctx,
        n_threads=args.n_threads,
        n_gpu_layers=args.n_gpu_layers,
        temperature=args.temperature,
    )
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
