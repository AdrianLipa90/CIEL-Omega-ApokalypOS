"""Regression tests for the File-Library-attested CIEL terminal runtime."""
from __future__ import annotations

import importlib.util
import math
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "ciel_terminal_runtime.py"
spec = importlib.util.spec_from_file_location("_ciel_terminal_runtime", SCRIPT)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def _write_vec(path: Path, offset: float = 0.0):
    vals = [offset + i / 36.0 for i in range(36)]
    path.write_bytes(struct.pack("<36d", *vals))


def test_repository_terminal_matches_verified_library_member():
    receipt = mod.verify_terminal(ROOT)
    assert receipt["status"] == "VERIFIED_LIBRARY_MEMBER_MATCH"
    assert receipt["sha256"] == "64679c7d2ddf9304f17c5833d7400bb3a1c24b7eb265e95213aaff8bd4da7b8e"
    assert receipt["archive_sha256"] == "fef25a4cb20380483fec5b3e84ad8a2d1465e6a53ecf6dfd9ec42ec67d82e9ef"


def test_tether_verifier_accepts_exact_live_contract_shape(tmp_path: Path):
    (tmp_path / "session").mkdir()
    (tmp_path / "ciel_binding_status").write_text("ACTIVE\n", encoding="utf-8")
    _write_vec(tmp_path / "phi", 0.0)
    _write_vec(tmp_path / "aux_phi", 1.0)
    _write_vec(tmp_path / "aux_feedback_phi", 2.0)
    (tmp_path / "session" / "startpoint.json").write_text("{}", encoding="utf-8")
    (tmp_path / "session" / "system_message.txt").write_text("ok", encoding="utf-8")
    receipt = mod.verify_tether(tmp_path)
    assert receipt["status"] == "ACTIVE"
    assert all(v["bytes"] == 288 for v in receipt["vectors"].values())


def test_tether_verifier_fails_closed_on_bad_vector(tmp_path: Path):
    (tmp_path / "session").mkdir()
    (tmp_path / "ciel_binding_status").write_text("ACTIVE", encoding="utf-8")
    (tmp_path / "phi").write_bytes(b"bad")
    _write_vec(tmp_path / "aux_phi")
    _write_vec(tmp_path / "aux_feedback_phi")
    (tmp_path / "session" / "startpoint.json").write_text("{}", encoding="utf-8")
    (tmp_path / "session" / "system_message.txt").write_text("ok", encoding="utf-8")
    try:
        mod.verify_tether(tmp_path)
    except RuntimeError as exc:
        assert "BAD_VECTOR_SIZE" in str(exc)
    else:
        raise AssertionError("invalid phi buffer was silently accepted")
