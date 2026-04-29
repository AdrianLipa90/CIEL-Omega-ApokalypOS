"""GitHub coupling subsystem (v1) — live upstream-aware phase coupling.

Fetches current upstream HEAD SHAs for registered repositories, propagates
phase shifts through the coupling map, and emits a refreshed JSON coupling
report.  Invoked via the ``ciel-sot-gh-coupling`` console script.
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


def build_live_coupling(root: str | Path) -> dict[str, Any]:
    root = Path(root)
    registry_path   = resolve_existing_path(root, 'integration/registries/repository_registry.json',   'integration/repository_registry.json')
    couplings_path  = resolve_existing_path(root, 'integration/couplings/repository_couplings.json',   'integration/couplings.json')
    upstreams_path  = resolve_existing_path(root, 'integration/upstreams/gh_upstreams.json',           'integration/gh_upstreams.json')
    runtime_state_path = resolve_existing_path(root, 'integration/couplings/gh_coupling_state.json',   'integration/gh_coupling_state.json')
    live_registry_path = resolve_existing_path(root, 'integration/upstreams/gh_live_registry.json',    'integration/gh_live_registry.json')
    report_path = root / 'integration' / 'reports' / 'live_gh_coupling_report.json'
    report_path.parent.mkdir(parents=True, exist_ok=True)

    states = load_registry(registry_path)
    couplings = load_couplings(couplings_path)
    upstreams = load_upstreams(upstreams_path)
    runtime_state = load_runtime_state(runtime_state_path)
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
        'schema': 'ciel-sot-agent/live-gh-coupling-report/v0.1',
        'generated_at': datetime.now(timezone.utc).isoformat(),
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

    runtime_state_path.write_text(json.dumps(runtime_state_out, ensure_ascii=False, indent=2), encoding='utf-8')
    live_registry_path.write_text(json.dumps(live_registry, ensure_ascii=False, indent=2), encoding='utf-8')
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    return report


def main() -> int:
    root = resolve_project_root(Path(__file__))
    report = build_live_coupling(root)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
