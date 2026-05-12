from __future__ import annotations


import scripts.ciel_session_hook as hook


def test_ensure_subconscious_daemon_checks_inline_status(monkeypatch, tmp_path):
    calls: list[list[str]] = []

    monkeypatch.setattr(hook, "PROJECT", str(tmp_path))
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "ciel_subconscious.py").write_text("# stub\n", encoding="utf-8")

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        class Result:
            returncode = 0
        return Result()

    monkeypatch.setattr(hook.subprocess, "run", fake_run)

    hook.ensure_subconscious_daemon()

    assert calls == [[hook.PY, str(scripts_dir / "ciel_subconscious.py"), "--status"]]


def test_ensure_memory_consolidator_daemon_spawns_detached_process(monkeypatch, tmp_path):
    calls: list[tuple[list[str], bool]] = []

    monkeypatch.setattr(hook, "PROJECT", str(tmp_path))
    monkeypatch.setattr(hook.Path, "home", lambda: tmp_path)

    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    consolidator = scripts_dir / "ciel_memory_consolidator.py"
    consolidator.write_text("# stub\n", encoding="utf-8")

    def fake_popen(cmd, **kwargs):
        calls.append((cmd, kwargs.get("start_new_session", False)))
        class Proc:
            pid = 12345
        return Proc()

    monkeypatch.setattr(hook.subprocess, "Popen", fake_popen)

    hook.ensure_memory_consolidator_daemon(interval=123)

    assert calls
    cmd, detached = calls[0]
    assert cmd == [hook.PY, str(consolidator), "--daemon", "--interval", "123"]
    assert detached is True
    assert (tmp_path / "Pulpit/CIEL_memories/logs").exists()
