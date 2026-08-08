"""Regression tests for the ChatGPT execution cage boundary."""
from pathlib import Path
import json
import struct

from src.CIEL_OMEGA_COMPLETE_SYSTEM.ciel_omega.runtime.chatgpt_execution_cage import (
    NoemaAuxContextGate, ChatGPTExecutionCage,
)


def _seed_surface(root: Path):
    root.mkdir(parents=True)
    (root/"session").mkdir()
    (root/"ciel_binding_status").write_text("ACTIVE")
    payload=struct.pack("<36d", *[float(i) for i in range(36)])
    for name in ("phi","aux_phi","aux_feedback_phi"):
        (root/name).write_bytes(payload)
    (root/"session"/"startpoint.json").write_text("{}")
    (root/"session"/"system_message.txt").write_text("ok")
    (root/"current_memory.json").write_text(json.dumps({"m":1}))
    (root/"current_task.json").write_text(json.dumps({"task":"x"}))
    (root/"active_path.json").write_text(json.dumps({"path":"y"}))


def test_cage_uses_injected_model_callable_without_substitution(tmp_path: Path):
    _seed_surface(tmp_path)
    seen={}
    def external_chatgpt(prompt, ctx):
        seen["prompt"]=prompt
        seen["ctx"]=ctx
        return "MODEL_OUTPUT"
    cage=ChatGPTExecutionCage(chatgpt_call=external_chatgpt,context_gate=NoemaAuxContextGate(tmp_path),model_id="external-chatgpt")
    turn=cage.run_turn("hello")
    assert seen["prompt"]=="hello"
    assert turn.model_output=="MODEL_OUTPUT"
    assert turn.model_id=="external-chatgpt"
    assert turn.aux_context.binding_status=="ACTIVE"


def test_cage_fails_closed_without_active_tether(tmp_path: Path):
    _seed_surface(tmp_path)
    (tmp_path/"ciel_binding_status").write_text("BLOCKED")
    called=False
    def external_chatgpt(prompt, ctx):
        nonlocal called
        called=True
        return "SHOULD_NOT_RUN"
    cage=ChatGPTExecutionCage(chatgpt_call=external_chatgpt,context_gate=NoemaAuxContextGate(tmp_path))
    try:
        cage.run_turn("hello")
        assert False, "expected fail-closed"
    except RuntimeError as exc:
        assert "TETHER_NOT_ACTIVE" in str(exc)
    assert called is False
