from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import struct
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "noema_time_crystal_aux_tether.py"


def _load():
    spec = importlib.util.spec_from_file_location("noema_time_crystal_aux_tether", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_vec(path: Path, value: float) -> bytes:
    raw = struct.pack("<36d", *([value] * 36))
    path.write_bytes(raw)
    return raw


def test_v2_statuses_bind_live_vectors_and_receipt(tmp_path: Path) -> None:
    mod = _load()
    phi = _write_vec(tmp_path / "phi", 0.1)
    aux = _write_vec(tmp_path / "aux_phi", 0.2)
    feedback = _write_vec(tmp_path / "aux_feedback_phi", 0.2)

    aux_status, tether = mod.publish_live_status(
        tmp_path,
        status="ACTIVE",
        seq=7,
        instance_id="test-instance",
    )

    assert aux_status["schema"] == "noema.aux-stream-status/v2"
    assert aux_status["status"] == "ACTIVE"
    assert aux_status["pid"] == os.getpid()
    assert aux_status["state_sha256"] == hashlib.sha256(aux).hexdigest()
    assert aux_status["no_static_fallback"] is True

    assert tether["schema"] == "noema.tether-runtime-status/v1"
    assert tether["status"] == "ACTIVE"
    assert tether["pid"] == os.getpid()
    assert tether["phi_sha256"] == hashlib.sha256(phi).hexdigest()
    assert tether["aux_phi_sha256"] == hashlib.sha256(aux).hexdigest()
    assert tether["aux_feedback_phi_sha256"] == hashlib.sha256(feedback).hexdigest()
    assert tether["no_static_fallback"] is True

    base = dict(tether)
    receipt = base.pop("receipt_sha256")
    assert receipt == mod.canonical_sha(base)

    disk_aux = json.loads((tmp_path / "aux_stream_status.json").read_text())
    disk_tether = json.loads((tmp_path / "tether_runtime_status.json").read_text())
    assert disk_aux == aux_status
    assert disk_tether == tether


def test_canonical_feedback_is_lossless_aux_echo_contract() -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    assert "write_vec(fb_path,aux)" in source
    assert "aux_feedback_control_phi" in source


def test_legacy_tether_no_longer_promotes_binding_active() -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    assert "binding.write_text('ACTIVE" not in source
    assert "binding.write_text('INACTIVE" not in source
