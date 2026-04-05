"""Shared GitHub API utilities for the coupling subsystems.

Provides the ``UpstreamConfig`` dataclass, HTTP helpers, upstream loading,
runtime-state loading, and the phase-propagation algorithm that are shared
between ``gh_coupling`` (v1) and ``gh_coupling_v2``.
"""
from __future__ import annotations

import json
import logging
import math
import urllib.request
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from .repo_phase import RepositoryState

_LOG = logging.getLogger(__name__)


@dataclass(frozen=True)
class UpstreamConfig:
    key: str
    repo_full_name: str | None
    branch: str
    enabled: bool
    source_weight: float
    notes: str


def wrap_angle(x: float) -> float:
    """Wrap *x* into (-pi, pi]."""
    while x <= -math.pi:
        x += 2.0 * math.pi
    while x > math.pi:
        x -= 2.0 * math.pi
    return x


def _github_json(
    url: str,
    token: str | None = None,
    *,
    user_agent: str = "CIEL-SOT-Agent/gh-coupling",
) -> dict[str, Any]:
    """Fetch a GitHub API endpoint and return the parsed JSON response."""
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": user_agent,
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_head(
    repo_full_name: str,
    branch: str,
    token: str | None = None,
    *,
    user_agent: str = "CIEL-SOT-Agent/gh-coupling",
) -> dict[str, Any]:
    """Return the latest commit metadata for *repo_full_name*/*branch*."""
    data = _github_json(
        f"https://api.github.com/repos/{repo_full_name}/commits/{branch}",
        token=token,
        user_agent=user_agent,
    )
    commit = data.get("commit", {})
    author = commit.get("author", {}) or {}
    committer = commit.get("committer", {}) or {}
    timestamp = author.get("date") or committer.get("date")
    return {
        "sha": str(data.get("sha")),
        "message": str(commit.get("message", "")),
        "timestamp": timestamp,
        "html_url": data.get("html_url"),
    }


def load_upstreams(path: str | Path) -> list[UpstreamConfig]:
    """Parse an upstreams JSON file into a list of :class:`UpstreamConfig`."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    out: list[UpstreamConfig] = []
    for item in data.get("upstreams", []):
        out.append(
            UpstreamConfig(
                key=str(item["key"]),
                repo_full_name=(
                    None
                    if item.get("repo_full_name") in (None, "")
                    else str(item.get("repo_full_name"))
                ),
                branch=str(item.get("branch", "main")),
                enabled=bool(item.get("enabled", True)),
                source_weight=float(item.get("source_weight", 1.0)),
                notes=str(item.get("notes", "")),
            )
        )
    return out


def load_runtime_state(path: str | Path) -> dict[str, Any]:
    """Load persisted coupling runtime state; return defaults if missing."""
    p = Path(path)
    if not p.exists():
        _LOG.debug("Runtime state file not found at %s; using defaults", p)
        return {"heads": {}, "last_generated_at": None}
    return json.loads(p.read_text(encoding="utf-8"))


def propagate_phase_changes(
    states: dict[str, RepositoryState],
    couplings: dict[str, dict[str, float]],
    changed_keys: list[str],
    *,
    intrinsic_jump: float = 0.2,
    beta: float = 0.35,
    source_weights: dict[str, float] | None = None,
) -> tuple[dict[str, RepositoryState], list[dict[str, Any]]]:
    """Propagate phase shifts triggered by upstream changes.

    Each changed repository receives an intrinsic phase jump
    (``intrinsic_jump * source_weight``), then its phase-coupled neighbours
    are updated via the Kuramoto-style term ``beta * coupling * sin(Δφ)``.

    Returns the updated states dict and a list of per-event dicts.
    """
    source_weights = source_weights or {}
    new_states = dict(states)
    events: list[dict[str, Any]] = []

    for key in changed_keys:
        if key not in new_states:
            _LOG.debug("Changed key %r not in states; skipping", key)
            continue
        state = new_states[key]
        weight = float(source_weights.get(key, 1.0))
        jump = intrinsic_jump * weight
        new_states[key] = replace(state, phi=wrap_angle(state.phi + jump))
        events.append({"kind": "intrinsic", "repo": key, "delta_phi": jump})

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
                    "kind": "coupled",
                    "source": source,
                    "target": target,
                    "coupling": float(coupling),
                    "delta_phi": delta,
                }
            )

    return new_states, events
