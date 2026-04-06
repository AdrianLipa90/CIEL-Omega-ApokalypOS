from __future__ import annotations

from pathlib import Path

from integration.Orbital.main.bootstrap import ensure_orbital_manifests, ensure_orbital_report_dirs
from integration.Orbital.main.global_pass import run_global_pass
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
    assert summary['schema'] == 'ciel-sot-agent/orbital-bridge-report/v0.1'

    bridge_dir = root / 'integration' / 'reports' / 'orbital_bridge'
    orbital_reports_root = orbital_root / 'reports' / 'global_orbital_coherence_pass'

    assert (bridge_dir / 'orbital_bridge_report.json').exists()
    assert (bridge_dir / 'orbital_bridge_report.md').exists()
    assert (bridge_dir / 'orbital_state_manifest.json').exists()
    assert (bridge_dir / 'orbital_health_manifest.json').exists()
    assert (orbital_reports_root / 'summary.json').exists()
    assert (orbital_reports_root / 'summary.md').exists()
    assert (orbital_reports_root / 'real_geometry.json').exists()
    assert summary['source_paths']['reports_root'] == str(orbital_reports_root)
