from __future__ import annotations

from pathlib import Path

from integration.Orbital.main.bootstrap import ensure_orbital_manifests, ensure_orbital_report_dirs
from integration.Orbital.main.dynamics import step
from integration.Orbital.main.global_pass import run_global_pass
from integration.Orbital.main.registry import load_system
from src.ciel_sot_agent.orbital_bridge import build_orbital_bridge


def test_ensure_orbital_manifests_creates_defaults(tmp_path: Path) -> None:
    info = ensure_orbital_manifests(tmp_path)
    assert Path(info['sectors_path']).exists()
    assert Path(info['couplings_path']).exists()


def test_ensure_orbital_report_dirs_creates_expected_paths(tmp_path: Path) -> None:
    info = ensure_orbital_report_dirs(tmp_path)
    assert Path(info['reports_root']).exists()
    assert info['summary_json'].endswith('summary.json')
    assert info['summary_md'].endswith('summary.md')
    assert info['real_geometry_json'].endswith('real_geometry.json')


def test_run_global_pass_returns_minimal_result() -> None:
    result = run_global_pass(steps=2)
    assert result['engine'] == 'global_orbital_coherence_pass_v63_euler_df257'
    assert result['steps'] == 2
    assert 'initial' in result
    assert 'final' in result
    assert 'R_H' in result['final']


def test_run_global_pass_respects_explicit_repo_root(tmp_path: Path) -> None:
    orbital_root = tmp_path / 'integration' / 'Orbital' / 'main'
    orbital_root.mkdir(parents=True, exist_ok=True)
    ensure_orbital_manifests(orbital_root)

    result = run_global_pass(steps=2, repo_root=orbital_root)

    reports_root = orbital_root / 'reports' / 'global_orbital_coherence_pass'
    manifests_root = orbital_root / 'manifests'

    assert result['engine'] == 'global_orbital_coherence_pass_v63_euler_df257'
    assert reports_root.exists()
    assert (reports_root / 'summary.json').exists()
    assert (reports_root / 'summary.md').exists()
    assert (reports_root / 'real_geometry.json').exists()
    assert (manifests_root / 'sectors_global.json').exists()
    assert (manifests_root / 'couplings_global.json').exists()
    assert not (manifests_root / 'orbital').exists()


def test_build_orbital_bridge_writes_bridge_outputs(tmp_path: Path) -> None:
    root = tmp_path
    orbital_root = root / 'integration' / 'Orbital' / 'main'
    orbital_root.mkdir(parents=True, exist_ok=True)
    summary = build_orbital_bridge(root)
    assert summary['schema'] == 'ciel-sot-agent/orbital-bridge-report/v0.2'

    bridge_dir = root / 'integration' / 'reports' / 'orbital_bridge'
    orbital_reports_root = orbital_root / 'reports' / 'global_orbital_coherence_pass'

    assert (bridge_dir / 'orbital_bridge_report.json').exists()
    assert (bridge_dir / 'orbital_bridge_report.md').exists()
    assert (bridge_dir / 'orbital_state_manifest.json').exists()
    assert (bridge_dir / 'orbital_health_manifest.json').exists()
    assert (bridge_dir / 'subsystem_sync_manifest.json').exists()
    assert (bridge_dir / 'runtime_gating.json').exists()
    assert (orbital_reports_root / 'summary.json').exists()
    assert (orbital_reports_root / 'summary.md').exists()
    assert (orbital_reports_root / 'real_geometry.json').exists()
    assert summary['source_paths']['reports_root'] == str(orbital_reports_root)


def test_step_with_orbital_law_v0_updates_sector_fields(tmp_path: Path) -> None:
    orbital_root = tmp_path / 'integration' / 'Orbital' / 'main'
    orbital_root.mkdir(parents=True, exist_ok=True)
    info = ensure_orbital_manifests(orbital_root)
    system = load_system(
        info['sectors_path'],
        info['couplings_path'],
        params={'use_orbital_law_v0': True},
    )

    nxt = step(system, dt=0.01)
    sector = next(iter(nxt.sectors.values()))

    assert sector.mu_eff > 0.0
    assert sector.tau_orbit > 0.0
    assert isinstance(sector.phase_slip_ready, bool)
    assert isinstance(sector.winding, int)
    assert 0.0 < sector.orbit_stability <= 1.0


def test_run_global_pass_with_orbital_law_v0_exposes_orbital_metrics() -> None:
    result = run_global_pass(steps=2, params={'use_orbital_law_v0': True})

    assert result['params']['use_orbital_law_v0'] is True
    assert result['final']['orbital_law_v0_enabled'] is True
    assert 'orbital_mu_eff_mean' in result['final']
    assert 'orbital_tau_orbit_mean' in result['final']
    assert 'orbital_phase_slip_ready_count' in result['final']
