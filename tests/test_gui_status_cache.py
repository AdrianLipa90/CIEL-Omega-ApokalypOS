from __future__ import annotations

from pathlib import Path

import pytest
from flask import Flask

import src.ciel_sot_agent.gui.routes as routes


def test_load_memory_stats_uses_short_ttl_cache(monkeypatch, tmp_path):
    app = Flask(__name__)
    app.config['CIEL_ROOT'] = tmp_path

    monkeypatch.setattr(routes.Path, 'home', lambda: tmp_path)
    state_dir = tmp_path / 'Pulpit/CIEL_memories/state'
    state_dir.mkdir(parents=True)
    (state_dir / 'ciel_orch_state.pkl').write_bytes(b'stub')

    calls: list[list[str]] = []

    class Result:
        returncode = 0
        stdout = '{"m2_count":1,"m3_count":2,"identity_phase":0.1,"cycle":3}'

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return Result()

    monkeypatch.setattr(routes.subprocess, 'run', fake_run)
    monkeypatch.setattr(routes, '_MEMORY_STATS_CACHE', {})
    monkeypatch.setattr(routes, '_MEMORY_STATS_CACHE_TS', 0.0)
    monkeypatch.setattr(routes, '_MEMORY_STATS_CACHE_TTL_S', 60.0)

    with app.app_context():
        first = routes._load_memory_stats()
        second = routes._load_memory_stats()

    assert first == second
    assert len(calls) == 1
