"""CIEL/NOEMA execution cage around an external ChatGPT runtime.

The cage does NOT replace, emulate, retrain, intercept internals of, or mutate
ChatGPT. It controls only the project-side boundary around model I/O and
persistent state.

Pipeline
--------
INPUT
  -> NOEMA/AUX context gate (read-only)
  -> external ChatGPT call (opaque model boundary)
  -> Doctor/Oracle policy gate
  -> Actuator-proxied memory/stream writes

Invariant
---------
CHATGPT_CORE_UNTOUCHED = True
CIEL_NOEMA_ROLE = execution_cage
MODEL_INFERENCE = external_opaque
PERSISTENT_MUTATION = Oracle -> Doctor -> Actuator only
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Optional
import hashlib
import json
import math
import struct
import time


DIM = 36
LE_F64_BYTES = DIM * 8


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_f64_36(path: Path) -> tuple[float, ...]:
    data = path.read_bytes()
    if len(data) != LE_F64_BYTES:
        raise RuntimeError(f"INVALID_36D_BUFFER:{path}:{len(data)}")
    values = struct.unpack("<36d", data)
    if not all(math.isfinite(x) for x in values):
        raise RuntimeError(f"NONFINITE_36D_BUFFER:{path}")
    return tuple(float(x) for x in values)


@dataclass(frozen=True)
class AuxContextSnapshot:
    root: str
    binding_status: str
    phi: tuple[float, ...]
    aux_phi: tuple[float, ...]
    aux_feedback_phi: tuple[float, ...]
    current_memory: Mapping[str, Any]
    current_task: Mapping[str, Any]
    active_path: Mapping[str, Any]
    captured_ns: int
    snapshot_sha256: str


class NoemaAuxContextGate:
    """Read-only pre-inference gate over the verified live NOEMA/AUX surface."""

    def __init__(self, root: str | Path = "/dev/shm/ciel_noema"):
        self.root = Path(root)

    def verify_and_snapshot(self) -> AuxContextSnapshot:
        root = self.root
        binding = (root / "ciel_binding_status").read_text(encoding="utf-8").strip()
        if binding != "ACTIVE":
            raise RuntimeError(f"TETHER_NOT_ACTIVE:{binding!r}")

        required_session = [
            root / "session" / "startpoint.json",
            root / "session" / "system_message.txt",
        ]
        for p in required_session:
            if not p.is_file():
                raise RuntimeError(f"MISSING_SESSION_FILE:{p}")

        phi = _read_f64_36(root / "phi")
        aux_phi = _read_f64_36(root / "aux_phi")
        aux_feedback_phi = _read_f64_36(root / "aux_feedback_phi")

        def read_json(name: str) -> Mapping[str, Any]:
            p = root / name
            if not p.is_file():
                return {}
            value = json.loads(p.read_text(encoding="utf-8"))
            return value if isinstance(value, dict) else {"value": value}

        body = {
            "root": str(root),
            "binding_status": binding,
            "phi": phi,
            "aux_phi": aux_phi,
            "aux_feedback_phi": aux_feedback_phi,
            "current_memory": read_json("current_memory.json"),
            "current_task": read_json("current_task.json"),
            "active_path": read_json("active_path.json"),
            "captured_ns": time.time_ns(),
        }
        digest = _sha256(json.dumps(body, sort_keys=True, separators=(",", ":"), default=list).encode("utf-8"))
        return AuxContextSnapshot(**body, snapshot_sha256=digest)


@dataclass(frozen=True)
class CageTurn:
    user_input: str
    aux_context: AuxContextSnapshot
    model_output: str
    model_id: Optional[str]
    turn_sha256: str


class ChatGPTExecutionCage:
    """Boundary controller around an externally supplied ChatGPT callable.

    `chatgpt_call` is deliberately injected. The cage does not instantiate a
    substitute model. Whatever callable the host provides remains the model.
    """

    def __init__(
        self,
        *,
        chatgpt_call: Callable[[str, AuxContextSnapshot], str],
        context_gate: Optional[NoemaAuxContextGate] = None,
        memory_proxy: Any = None,
        model_id: Optional[str] = None,
    ):
        self.chatgpt_call = chatgpt_call
        self.context_gate = context_gate or NoemaAuxContextGate()
        self.memory_proxy = memory_proxy
        self.model_id = model_id

    def run_turn(self, user_input: str) -> CageTurn:
        ctx = self.context_gate.verify_and_snapshot()
        output = str(self.chatgpt_call(str(user_input), ctx))

        body = {
            "user_input": str(user_input),
            "aux_snapshot_sha256": ctx.snapshot_sha256,
            "model_output": output,
            "model_id": self.model_id,
        }
        turn_sha = _sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8"))
        turn = CageTurn(str(user_input), ctx, output, self.model_id, turn_sha)

        if self.memory_proxy is not None:
            event = {
                "schema": "noema.chatgpt-cage-turn/v1",
                "kind": "CHATGPT_CAGE_TURN",
                "model_boundary": "EXTERNAL_OPAQUE_CHATGPT",
                "chatgpt_core_untouched": True,
                "aux_snapshot_sha256": ctx.snapshot_sha256,
                "turn_sha256": turn_sha,
                "user_input": str(user_input),
                "model_output": output,
                "model_id": self.model_id,
                "write_path": "Oracle->Doctor->Actuator",
            }
            # Expected interface of the existing AUX memory proxy: append_event(event)
            self.memory_proxy.append_event(event)

        return turn


__all__ = [
    "AuxContextSnapshot",
    "NoemaAuxContextGate",
    "CageTurn",
    "ChatGPTExecutionCage",
]
