"""GitHub coupling subsystem (v2) — enhanced upstream coupling with v2 schema.

Extends the v1 GitHub coupling with richer upstream metadata, rate-limit
handling, and a structured v2 coupling report.  Invoked via
``ciel-sot-gh-coupling-v2``.
"""
from __future__ import annotations

import json
import math
import os
import urllib.request
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .paths import resolve_project_root
from .repo_phase import RepositoryState, closure_defect, load_couplings, load_registry, weighted_euler_vector


REGISTRY_V2_PATH = 'integration/registries/repository_registry.json'
REGISTRY_LEGACY_PATH = 'integration/repository_registry.json'
COUPLINGS_V2_PATH = 'integration/couplings/repository_couplings.json'
COUPLINGS_LEGACY_PATH = 'integration/couplings.json'
UPSTREAMS_V2_PATH = 'integration/upstreams/gh_upstreams.json'
UPSTREAMS_LEGACY_PATH = 'integration/gh_upstreams.json'
RUNTIME_STATE_V2_PATH = 'integration/couplings/gh_coupling_state.json'
RUNTIME_STATE_LEGACY_PATH = 'integration/gh_coupling_state.json'
LIVE_REGISTRY_V2_PATH = 'integration/upstreams/gh_live_registry.json'
LIVE_REGISTRY_LEGACY_PATH = 'integration/gh_live_registry.json'
REPORT_PATH = 'integration/reports/live_gh_coupling_report.json'


@dataclass(frozen=True)
class UpstreamConfig:
    key: str
    repo_full_name: str | None
    branch: str
    enabled: bool
    source_weight: float
    notes: str


def wrap_angle(x: float) -> float:
    while x <= -math.pi:
        x += 2.0 * math.pi
    while x > math.pi:
        x -= 2.0 * math.pi
    return x


def resolve_existing_path(root: str | Path, *candidates: str) -> Path:
    root = Path(root)
    for candidate in candidates:
        candidate_path = root / candidate
        if candidate_path.exists():
            return candidate_path
    return root / candidates[0]


def resolve_runtime_paths(root: str | Path) -> dict[str, Path]:
    root = Path(root)
    return {
        'registry': resolve_existing_path(root, REGISTRY_V2_PATH, REGISTRY_LEGACY_PATH),
        'couplings': resolve_existing_path(root, COUPLINGS_V2_PATH, COUPLINGS_LEGACY_PATH),
        'upstreams': resolve_existing_path(root, UPSTREAMS_V2_PATH, UPSTREAMS_LEGACY_PATH),
        'runtime_state': resolve_existing_path(root, RUNTIME_STATE_V2_PATH, RUNTIME_STATE_LEGACY_PATH),
        'live_registry': resolve_existing_path(root, LIVE_REGISTRY_V2_PATH, LIVE_REGISTRY_LEGACY_PATH),
        'report': root / REPORT_PATH,
    }


def _github_json(url: str, token: str | None = None) -> dict[str, Any]:
    headers = {
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'CIEL-SOT-Agent/gh-coupling-v2',
    }
    if token:
        headers['Authorization'] = f'Bearer {token}'
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode('utf-8'))


def fetch_head(repo_full_name: str, branch: str, token: str | None = None) -> dict[str, Any]:
    data = _github_json(f'https://api.github.com/repos/{repo_full_name}/commits/{branch}', token=token)
    commit = data.get('commit', {})
    author = commit.get('author', {}) or {}
    committer = commit.get('committer', {}) or {}
    timestamp = author.get('date') or committer.get('date')
    return {
        'sha': str(data.get('sha')),
        'message': str(commit.get('message', '')),
        'timestamp': timestamp,
        'html_url': data.get('html_url'),
    }


def load_upstreams(path: str | Path) -> list[UpstreamConfig]:
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    out: list[UpstreamConfig] = []
    for item in data.get('upstreams', []):
        out.append(
            UpstreamConfig(
                key=str(item['key']),
                repo_full_name=None if item.get('repo_full_name') in (None, '') else str(item.get('repo_full_name')),
                branch=str(item.get('branch', 'main')),
                enabled=bool(item.get('enabled', True)),
                source_weight=float(item.get('source_weight', 1.0)),
                notes=str(item.get('notes', '')),
            )
        )
    return out


def load_runtime_state(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {'heads': {}, 'last_generated_at': None}
    return json.loads(p.read_text(encoding='utf-8'))


def propagate_phase_changes(
    states: dict[str, RepositoryState],
    couplings: dict[str, dict[str, float]],
    changed_keys: list[str],
    *,
    intrinsic_jump: float = 0.2,
    beta: float = 0.35,
    source_weights: dict[str, float] | None = None,
) -> tuple[dict[str, RepositoryState], list[dict[str, Any]]]:
    source_weights = source_weights or {}
    new_states = dict(states)
    events: list[dict[str, Any]] = []

    for key in changed_keys:
        if key not in new_states:
            continue
        state = new_states[key]
        weight = float(source_weights.get(key, 1.0))
        jump = intrinsic_jump * weight
        new_states[key] = replace(state, phi=wrap_angle(state.phi + jump))
        events.append({'kind': 'intrinsic', 'repo': key, 'delta_phi': jump})

    for source in changed_keys:
        if source not in new_states:
            continue
        src_state = new_states[source]
        for target, coupling in couplings.get(source, {}).items():
            if target not in new_states or target == source:
                continue
            tgt_state = new_states[target]
            delta = beta * float(coupling) * math.sin(src_state.phi - tgt_state.phi)
            if abs(delta) < 1e-15:
                continue
            new_states[target] = replace(tgt_state, phi=wrap_angle(tgt_state.phi + delta))
            events.append(
                {
                    'kind': 'coupled',
                    'source': source,
                    'target': target,
                    'coupling': float(coupling),
                    'delta_phi': delta,
                }
            )
    return new_states, events


def build_live_coupling(root: str | Path) -> dict[str, Any]:
    root = Path(root)
    paths = resolve_runtime_paths(root)
    report_path = paths['report']
    report_path.parent.mkdir(parents=True, exist_ok=True)

    states = load_registry(paths['registry'])
    couplings = load_couplings(paths['couplings'])
    upstreams = load_upstreams(paths['upstreams'])
    runtime_state = load_runtime_state(paths['runtime_state'])
    old_heads = runtime_state.get('heads', {}) or {}

    token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
    checks: list[dict[str, Any]] = []
    changed_keys: list[str] = []
    new_heads: dict[str, Any] = {}
    source_weights: dict[str, float] = {}

    before_defect = closure_defect(states.values())

    for upstream in upstreams:
        source_weights[upstream.key] = upstream.source_weight
        if not upstream.enabled or not upstream.repo_full_name:
            checks.append(
                {
                    'key': upstream.key,
                    'enabled': False,
                    'repo_full_name': upstream.repo_full_name,
                    'branch': upstream.branch,
                    'changed': False,
                    'notes': upstream.notes,
                }
            )
            continue

        head = fetch_head(upstream.repo_full_name, upstream.branch, token=token)
        old = old_heads.get(upstream.key, {}) or {}
        changed = old.get('sha') != head['sha']
        if changed:
            changed_keys.append(upstream.key)
        new_heads[upstream.key] = head
        checks.append(
            {
                'key': upstream.key,
                'enabled': True,
                'repo_full_name': upstream.repo_full_name,
                'branch': upstream.branch,
                'changed': changed,
                'old_sha': old.get('sha'),
                'new_sha': head['sha'],
                'timestamp': head.get('timestamp'),
                'message': head.get('message'),
                'html_url': head.get('html_url'),
            }
        )

    new_states, events = propagate_phase_changes(
        states,
        couplings,
        changed_keys,
        source_weights=source_weights,
    )

    after_defect = closure_defect(new_states.values())
    vec = weighted_euler_vector(new_states.values())

    live_registry = {
        'schema': 'ciel-sot-agent/gh-live-registry/v0.1',
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'repositories': [
            {
                'key': s.key,
                'identity': s.identity,
                'phi': s.phi,
                'spin': s.spin,
                'mass': s.mass,
                'role': s.role,
                'upstream': s.upstream,
            }
            for s in new_states.values()
        ],
    }

    report = {
        'schema': 'ciel-sot-agent/live-gh-coupling-report/v0.2',
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'path_resolution': {
            'registry': str(paths['registry'].relative_to(root)),
            'couplings': str(paths['couplings'].relative_to(root)),
            'upstreams': str(paths['upstreams'].relative_to(root)),
            'runtime_state': str(paths['runtime_state'].relative_to(root)),
            'live_registry': str(paths['live_registry'].relative_to(root)),
            'report': str(paths['report'].relative_to(root)),
        },
        'changed_keys': changed_keys,
        'upstream_checks': checks,
        'phase_events': events,
        'closure_defect_before': before_defect,
        'closure_defect_after': after_defect,
        'weighted_euler_vector_after': {
            'real': vec.real,
            'imag': vec.imag,
            'abs': abs(vec),
        },
    }

    runtime_state_out = {
        'last_generated_at': datetime.now(timezone.utc).isoformat(),
        'heads': new_heads,
        'last_changed_keys': changed_keys,
    }

    paths['runtime_state'].write_text(json.dumps(runtime_state_out, ensure_ascii=False, indent=2), encoding='utf-8')
    paths['live_registry'].write_text(json.dumps(live_registry, ensure_ascii=False, indent=2), encoding='utf-8')
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    return report


def main() -> int:
    root = resolve_project_root(Path(__file__))
    report = build_live_coupling(root)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
