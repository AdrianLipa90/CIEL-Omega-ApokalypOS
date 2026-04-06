#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def repo_relative(repo_root: Path, path: Path) -> str:
    """
    Return a repository-relative POSIX-style string for a path when possible.
    
    Parameters:
        repo_root (Path): Repository root used as the base for relativization.
        path (Path): Path to convert to a repository-relative string.
    
    Returns:
        str: The path relative to `repo_root` with forward slashes, or the original path string if relativization fails.
    """
    try:
        return str(path.resolve().relative_to(repo_root.resolve())).replace('\\', '/')
    except Exception:
        return str(path)


def run_step(repo_root: Path, script_name: str, extra_args: list[str] | None = None) -> dict:
    """
    Run a script from the repository's scripts directory and collect its execution results.
    
    Parameters:
        repo_root (Path): Repository root used to locate the script at `scripts/<script_name>`.
        script_name (str): Filename of the script to execute.
        extra_args (list[str] | None): Additional command-line arguments to append to the script invocation.
    
    Returns:
        dict: A mapping with the following keys:
            - 'script' (str): The script name that was run.
            - 'returncode' (int): The process exit code.
            - 'stdout' (str): Captured standard output.
            - 'stderr' (str): Captured standard error.
            - 'ok' (bool): `true` if `returncode` is 0, `false` otherwise.
    """
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
        'ok': proc.returncode == 0,
    }


def main() -> int:
    """
    Orchestrates a sequence of repository scripts to build and validate the audio-orbital definition catalog and writes a JSON summary report.
    
    Parses command-line arguments `--repo-root`, `--skip-download`, and `--roots`; runs a fixed sequence of helper scripts, aggregates their results and selected artifact paths (made repository-relative), writes the aggregated summary to integration/registries/definitions/audio_orbital_hook_report.json, and prints the same JSON to stdout.
    
    Returns:
        int: `0` if all steps succeeded, `1` otherwise.
    """
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
    steps.append(run_step(repo_root, 'resolve_orbital_semantics.py'))
    steps.append(run_step(repo_root, 'build_nonlocal_definition_edges.py'))
    steps.append(run_step(repo_root, 'run_audio_orbital_probe.py'))

    ok = all(step['ok'] for step in steps)
    summary = {
        'schema': 'ciel/audio-orbital-catalog-hook/v0.1',
        'ok': ok,
        'steps': steps,
        'artifacts': {
            'audio_state': repo_relative(repo_root, repo_root / 'integration' / 'imports' / 'audio_orbital_stack' / 'state' / 'audio_orbital_stack_state.json'),
            'definition_registry': repo_relative(repo_root, repo_root / 'integration' / 'registries' / 'definitions' / 'definition_registry.json'),
            'orbital_registry': repo_relative(repo_root, repo_root / 'integration' / 'registries' / 'definitions' / 'orbital_definition_registry.json'),
            'orbital_report': repo_relative(repo_root, repo_root / 'integration' / 'registries' / 'definitions' / 'orbital_assignment_report.json'),
            'nonlocal_edges': repo_relative(repo_root, repo_root / 'integration' / 'registries' / 'definitions' / 'nonlocal_definition_edges.json'),
        },
    }

    out_path = repo_root / 'integration' / 'registries' / 'definitions' / 'audio_orbital_hook_report.json'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(summary, indent=2))
    return 0 f ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
