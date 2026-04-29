"""GitHub coupling subsystem (v2) — enhanced upstream coupling with v2 schema.

Extends the v1 GitHub coupling with richer upstream metadata, rate-limit
handling, and a structured v2 coupling report.  Invoked via
``ciel-sot-gh-coupling-v2``.
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .paths import resolve_existing_path, resolve_project_root
from .repo_phase import closure_defect, load_couplings, load_registry, weighted_euler_vector
from ._gh_utils import (
    UpstreamConfig as UpstreamConfig,
    fetch_head,
    load_runtime_state,
    load_upstreams,
    propagate_phase_changes,
    wrap_angle as wrap_angle,
)

_LOG = logging.getLogger(__name__)

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

        head = fetch_head(
            upstream.repo_full_name,
            upstream.branch,
            token=token,
            user_agent="CIEL-SOT-Agent/gh-coupling-v2",
        )
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
