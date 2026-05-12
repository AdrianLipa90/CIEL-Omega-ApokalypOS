from __future__ import annotations

import scripts.ciel_subconscious_supervisor as sup


class _Result:
    def __init__(self, returncode=0, stdout=""):
        self.returncode = returncode
        self.stdout = stdout


def test_get_status_prefers_inline_backend(monkeypatch):
    monkeypatch.setattr(sup, "_inline_backend_ok", lambda: True)
    monkeypatch.setattr(sup, "is_running", lambda: False)

    status = sup.get_status()

    assert status["running"] is True
    assert status["mode"] == "inline"
    assert status["inline_ok"] is True
    assert status["server_running"] is False


def test_get_status_falls_back_to_server(monkeypatch):
    monkeypatch.setattr(sup, "_inline_backend_ok", lambda: False)
    monkeypatch.setattr(sup, "is_running", lambda: True)

    status = sup.get_status()

    assert status["running"] is True
    assert status["mode"] == "server"
    assert status["inline_ok"] is False
    assert status["server_running"] is True


def test_inline_backend_ok_uses_status_command(monkeypatch):
    calls = []

    monkeypatch.setattr(sup.Path, "exists", lambda self: True)

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return _Result(returncode=0, stdout="inline: OK  (latency 0.01s)\n")

    monkeypatch.setattr(sup.subprocess, "run", fake_run)

    assert sup._inline_backend_ok() is True
    assert calls == [[sup.sys.executable, str(sup._INLINE_SCRIPT), "--status"]]
