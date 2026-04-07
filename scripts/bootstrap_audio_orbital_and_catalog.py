#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def repo_relative(repo_root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve())).replace('\\', '/')
    except Exception:
        return str(path)


def relativize_json_paths(repo_root: Path, value: Any) -> Any:
    if isinstance(value, dict):
        return {k: relativize_json_paths(repo_root, v) for k, v in value.items()}
    if isinstance(value, list):
        return [relativize_json_paths(repo_root, v) for v in value]
    if isinstance(value, str):
        try:
            candidate = Path(value)
            if candidate.is_absolute():
                return repo_relative(repo_root, candidate)
        except Exception:
            return value
    return value


def maybe_parse_json(repo_root: Path, text: str) -> dict[str, Any] | list[Any] | None:
    if not text or not text.strip():
        return None
    try:
        return relativize_json_paths(repo_root, json.loads(text))
    except Exception:
        return None


def load_json_if_exists(repo_root: Path, path: Path) -> dict[str, Any] | list[Any] | None:
    if not path.exists():
        return None
    try:
        return relativize_json_paths(repo_root, json.loads(path.read_text(encoding='utf-8')))
    except Exception:
        return None


def run_step(repo_root: Path, script_name: str, extra_args: list[str] | None = None) -> dict:
    script_path = repo_root / 'scripts' / script_name
    cmd = [sys.executable, str(script_path), '--repo-root', str(repo_root)]
    if extra_args:
        cmd.extend(extra_args)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return {
        'script': script_name,
        'returncode': proc.returncode,
        'stdout': proc.stdout,
        'stderr': proc.stderr,
        'summary_json': maybe_parse_json(repo_root, proc.stdout),
        'ok': proc.returncode == 0,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo-root', default='.')
    ap.add_argument('--skip-download', action='store_true')
    ap.add_argument('--roots', nargs='*', default=['src', 'scripts', 'integration'])
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    steps = []
    bootstrap_args: list[str] = []
    if args.skip_download:
        bootstrap_args.append('--skip-download')
    steps.append(run_step(repo_root, 'bootstrap_audio_orbital_stack.py', bootstrap_args))
    roots_args = ['--roots', *args.roots] if args.roots else []
    steps.append(run_step(repo_root, 'build_orbital_definition_registry.py', roots_args))
    steps.append(run_step(repo_root, 'normalize_definition_registry.py'))
    steps.append(run_step(repo_root, 'resolve_orbital_semantics.py'))
    steps.append(run_step(repo_root, 'build_subsystem_sync_registry.py'))
    steps.append(run_step(repo_root, 'build_nonlocal_definition_edges.py'))
    steps.append(run_step(repo_root, 'build_definition_db_library.py'))
    steps.append(run_step(repo_root, 'verify_orbital_registry_integrity.py'))
    steps.append(run_step(repo_root, 'run_audio_orbital_probe.py'))

    ok = all(step['ok'] for step in steps)
    artifacts = {
        'audio_state': repo_relative(repo_root, repo_root / 'integration' / 'imports' / 'audio_orbital_stack' / 'state' / 'audio_orbital_stack_state.json'),
        'definition_registry': repo_relative(repo_root, repo_root / 'integration' / 'registries' / 'definitions' / 'definition_registry.json'),
        'orbital_registry': repo_relative(repo_root, repo_root / 'integration' / 'registries' / 'definitions' / 'orbital_definition_registry.json'),
        'internal_card_registry': repo_relative(repo_root, repo_root / 'integration' / 'registries' / 'definitions' / 'internal_subsystem_cards.json'),
        'horizon_policy_matrix': repo_relative(repo_root, repo_root / 'integration' / 'registries' / 'definitions' / 'horizon_policy_matrix.json'),
        'subsystem_sync_registry': repo_relative(repo_root, repo_root / 'integration' / 'registries' / 'definitions' / 'subsystem_sync_registry.json'),
        'subsystem_sync_report': repo_relative(repo_root, repo_root / 'integration' / 'registries' / 'definitions' / 'subsystem_sync_report.json'),
        'verification_report': repo_relative(repo_root, repo_root / 'integration' / 'registries' / 'definitions' / 'verification_report.json'),
        'orbital_report': repo_relative(repo_root, repo_root / 'integration' / 'registries' / 'definitions' / 'orbital_assignment_report.json'),
        'nonlocal_edges': repo_relative(repo_root, repo_root / 'integration' / 'registries' / 'definitions' / 'nonlocal_definition_edges.json'),
        'db_manifest': repo_relative(repo_root, repo_root / 'integration' / 'registries' / 'definitions' / 'db_library' / 'manifest.json'),
        'orbital_card_system_manifest': repo_relative(repo_root, repo_root / 'integration' / 'registries' / 'definitions' / 'orbital_card_system_integration_manifest.json'),
    }
    artifact_snapshots = {
        'audio_state': load_json_if_exists(repo_root, repo_root / artifacts['audio_state']),
        'orbital_report': load_json_if_exists(repo_root, repo_root / artifacts['orbital_report']),
        'internal_card_registry': load_json_if_exists(repo_root, repo_root / artifacts['internal_card_registry']),
        'horizon_policy_matrix': load_json_if_exists(repo_root, repo_root / artifacts['horizon_policy_matrix']),
        'subsystem_sync_registry': load_json_if_exists(repo_root, repo_root / artifacts['subsystem_sync_registry']),
        'subsystem_sync_report': load_json_if_exists(repo_root, repo_root / artifacts['subsystem_sync_report']),
        'verification_report': load_json_if_exists(repo_root, repo_root / artifacts['verification_report']),
        'db_manifest': load_json_if_exists(repo_root, repo_root / artifacts['db_manifest']),
        'orbital_card_system_manifest': load_json_if_exists(repo_root, repo_root / artifacts['orbital_card_system_manifest']),
    }
    summary = {
        'schema': 'ciel/audio-orbital-catalog-hook/v0.7',
        'ok': ok,
        'steps': steps,
        'artifacts': artifacts,
        'artifact_snapshots': artifact_snapshots,
    }
    out_path = repo_root / 'integration' / 'registries' / 'definitions' / 'audio_orbital_hook_report.json'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(summary, indent=2))
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
