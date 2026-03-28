from __future__ import annotations

from pathlib import Path

from src.ciel_sot_agent.sapiens_panel.controller import build_panel_state, run_sapiens_panel
from src.ciel_sot_agent.sapiens_panel.settings_store import load_panel_settings


def test_load_panel_settings_reads_defaults() -> None:
    root = Path(__file__).resolve().parents[1]
    settings = load_panel_settings(root)
    assert settings.ui['system_language'] == 'English'
    assert settings.identity['preferred_mode'] == 'guided'
    assert settings.reduction_policy['readiness_threshold'] == 0.62


def test_build_panel_state_exposes_four_tabs_and_reduction() -> None:
    root = Path(__file__).resolve().parents[1]
    state = build_panel_state(root, user_text='Test panel input', sapiens_id='tester')
    assert state.control.title == 'Control'
    assert state.settings.title == 'Settings'
    assert state.communication.title == 'Communication'
    assert state.support.title == 'Support'
    assert state.session.sapiens_id == 'tester'
    assert 'reduction_state' in state.control.summary
    assert 'memory_residue' in state.communication.summary


def test_run_sapiens_panel_returns_v2_schema() -> None:
    root = Path(__file__).resolve().parents[1]
    result = run_sapiens_panel(root, user_text='Hello panel', sapiens_id='tester')
    assert result['schema'] == 'ciel-sot-agent/sapiens-panel-run/v0.2'
    assert 'panel_state' in result
