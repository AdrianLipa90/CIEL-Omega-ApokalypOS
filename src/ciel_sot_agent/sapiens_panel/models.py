from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PanelSettings:
    identity: dict[str, Any]
    interaction_policy: dict[str, Any]
    orbital_runtime: dict[str, Any]
    reduction_policy: dict[str, Any]
    ui: dict[str, Any]


@dataclass
class PanelTabState:
    title: str
    summary: dict[str, Any] = field(default_factory=dict)
    actions: list[str] = field(default_factory=list)


@dataclass
class PanelSessionSummary:
    sapiens_id: str
    relation_label: str
    preferred_mode: str
    created_at: str
    updated_at: str
    turn_count: int


@dataclass
class PanelState:
    control: PanelTabState
    settings: PanelTabState
    communication: PanelTabState
    support: PanelTabState
    session: PanelSessionSummary
    state_sources: dict[str, Any] = field(default_factory=dict)
    manifest: dict[str, Any] = field(default_factory=dict)
