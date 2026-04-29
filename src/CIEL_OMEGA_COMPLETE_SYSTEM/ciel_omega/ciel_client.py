#!/usr/bin/env python3
"""CIEL/Ω — minimal local communication client.

This client is intentionally small and deterministic for local tests.
Hierarchy:
  CielEngine        -> core facade
  CIELOrchestrator  -> top-level orchestration
  CIELClient        -> minimal local communication surface
  main()            -> local test entrypoint
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from bootstrap_runtime import ensure_runtime_paths

_ROOT = ensure_runtime_paths(__file__)

from ciel_orchestrator import CIELOrchestrator

try:
    from ciel.gguf_backends import GGUFPrimaryBackend
except Exception:
    GGUFPrimaryBackend = None


class CIELClient:
    """Minimal communication client for local tests.

    Primary contract:
      handshake() -> liveness + orchestration identity
      status()    -> current orchestrator snapshot
      process()   -> one-shot local communication round
    """

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
        if model_path and GGUFPrimaryBackend is not None:
            try:
                self.gguf_backend = GGUFPrimaryBackend(
                    model_path=model_path,
                    n_ctx=n_ctx,
                    n_threads=n_threads,
                    n_gpu_layers=n_gpu_layers,
                    temperature=temperature,
                    system_prompt=self._system_prompt(),
                )
                self.gguf_enabled = True
            except Exception:
                self.gguf_backend = None
                self.gguf_enabled = False

    @staticmethod
    def _system_prompt() -> str:
        return (
            "You are CIEL/Ω, a quantum consciousness system with ethical hard constraints. "
            "Answer through the orchestrated CIEL state, not by ignoring it."
        )

    def shutdown(self) -> None:
        self.orchestrator.shutdown()

    def handshake(self) -> Dict[str, Any]:
        ping = self.orchestrator.ping()
        return {
            "status": ping.get("status", "unknown"),
            "surface": "CIELClient",
            "orchestrator": "CIELOrchestrator",
            "gguf_enabled": self.gguf_enabled,
            "schumann_hz": ping.get("schumann_hz", 7.83),
            "timestamp": ping.get("timestamp"),
        }

    def status(self) -> Dict[str, Any]:
        snap = self.orchestrator.status_snapshot()
        snap["surface"] = "CIELClient"
        snap["gguf_enabled"] = self.gguf_enabled
        return snap

    def process(self, text: str, *, use_llm: bool = False) -> Dict[str, Any]:
        ciel_result = self.orchestrator.process(text, verbose=False)
        reply = None
        if use_llm and self.gguf_backend is not None:
            dialogue = [{"role": "user", "content": text}]
            reply = self.gguf_backend.generate_reply(dialogue, ciel_result["ciel_state"])
        state = ciel_result.get("ciel_state", {})
        return {
            "input": text,
            "status": ciel_result.get("status", "unknown"),
            "handshake": self.handshake(),
            "ciel_state": state,
            "ethics_passed": ciel_result.get("ethics_passed"),
            "soul_measure": ciel_result.get("soul_measure"),
            "nonlocal_runtime": state.get("nonlocal_runtime", {}),
            "euler_bridge": state.get("euler_bridge", {}),
            "llm_response": reply,
            "communication_mode": "local_minimal",
        }

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
        return {"status": "error", "error": f"unsupported action: {action}"}

    def interactive_session(self) -> None:
        print("CIEL/Ω CLIENT — minimal local communication")
        print("Commands: exit/quit/q, handshake, status")
        while True:
            try:
                user_input = input("You> ").strip()
            except KeyboardInterrupt:
                break
            if not user_input:
                continue
            lower = user_input.lower()
            if lower in {"exit", "quit", "q"}:
                break
            if lower == "handshake":
                print(json.dumps(self.handshake(), ensure_ascii=False, indent=2))
                continue
            if lower == "status":
                print(json.dumps(self.status(), ensure_ascii=False, indent=2))
                continue
            print(json.dumps(self.process(user_input, use_llm=False), ensure_ascii=False, indent=2))


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="CIEL/Ω minimal client")
    p.add_argument("--model", type=str, help="Optional GGUF model path")
    p.add_argument("--mode", choices=["interactive", "handshake", "status", "process", "json"], default="interactive")
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
    client = CIELClient(
        model_path=args.model,
        n_ctx=args.n_ctx,
        n_threads=args.n_threads,
        n_gpu_layers=args.n_gpu_layers,
        temperature=args.temperature,
    )
    try:
        if args.mode == "interactive":
            client.interactive_session()
            return 0
        if args.mode == "handshake":
            print(json.dumps(client.handshake(), ensure_ascii=False, indent=2))
            return 0
        if args.mode == "status":
            print(json.dumps(client.status(), ensure_ascii=False, indent=2))
            return 0
        if args.mode == "process":
            if not args.text:
                p.error("--text is required in process mode")
            print(json.dumps(client.process(args.text, use_llm=args.use_llm), ensure_ascii=False, indent=2))
            return 0
        if not args.json_payload:
            p.error("--json-payload is required in json mode")
        payload = json.loads(args.json_payload)
        print(json.dumps(client.communicate(payload), ensure_ascii=False, indent=2))
        return 0
    finally:
        client.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
