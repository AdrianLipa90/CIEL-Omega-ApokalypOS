from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .orbital_cockpit import CockpitTopology, OrbitId, build_default_topology, orbit_navigation_groups


@dataclass(frozen=True)
class NavigationSection:
    title: str
    orbit: OrbitId
    items: List[Dict[str, Any]]


def build_navigation_sections(topology: Optional[CockpitTopology] = None) -> List[NavigationSection]:
    topology = topology or build_default_topology()
    groups = orbit_navigation_groups(topology)

    ordered: list[tuple[OrbitId, str]] = [
        (OrbitId.IDENTITY, 'Identity Attractor'),
        (OrbitId.CONSTITUTIVE, 'Constitutive Layers'),
        (OrbitId.DYNAMIC, 'Dynamic Layers'),
        (OrbitId.INTERACTION, 'Interaction Layers'),
        (OrbitId.OBSERVATION, 'Observation Layers'),
        (OrbitId.BOUNDARY, 'Boundary Layers'),
        (OrbitId.EDUCATION, 'Educational Layers'),
    ]

    sections: List[NavigationSection] = []
    for orbit, title in ordered:
        nodes = sorted(groups.get(orbit, []), key=lambda n: n.label.lower())
        sections.append(
            NavigationSection(
                title=title,
                orbit=orbit,
                items=[
                    {
                        'key': node.key,
                        'label': node.label,
                        'status': node.default_status.value,
                        'description': node.description,
                        'children': list(node.children),
                    }
                    for node in nodes
                ],
            )
        )
    return sections


def build_identity_snapshot(
    *,
    topology: Optional[CockpitTopology] = None,
    active_model: Optional[str] = None,
    active_kernel: Optional[str] = None,
    ethics_gate: Optional[str] = None,
    export_package: Optional[str] = None,
    publication_boundary: Optional[str] = None,
    coherence: Optional[float] = None,
    resonance: Optional[float] = None,
    warnings: Optional[List[str]] = None,
) -> Dict[str, Any]:
    topology = topology or build_default_topology()
    identity = topology.identity

    out = {
        'identity_profile': identity.identity_profile,
        'coherence': identity.coherence if coherence is None else coherence,
        'resonance': identity.resonance if resonance is None else resonance,
        'ethics_gate': ethics_gate or identity.ethics_gate,
        'active_contract': identity.active_contract,
        'active_canon_export': export_package or identity.active_canon_export,
        'active_operator_set': identity.active_operator_set,
        'session_phase': identity.session_phase,
        'publication_boundary': publication_boundary or identity.publication_boundary,
        'active_model': active_model,
        'active_kernel': active_kernel,
        'warnings': list(identity.warnings) + list(warnings or []),
    }
    return out


def build_event_strip(
    *,
    active_kernel: Optional[str] = None,
    active_model: Optional[str] = None,
    export_package: Optional[str] = None,
    ethics_state: Optional[str] = None,
    boundary_mode: Optional[str] = None,
    dirty_state: Optional[bool] = None,
    failing_tests: Optional[int] = None,
    recent_artifact: Optional[str] = None,
) -> List[Dict[str, Any]]:
    return [
        {'label': 'Kernel', 'value': active_kernel or '(none)'},
        {'label': 'Model', 'value': active_model or '(none)'},
        {'label': 'Export', 'value': export_package or '(none)'},
        {'label': 'Ethics', 'value': ethics_state or 'unknown'},
        {'label': 'Boundary', 'value': boundary_mode or 'unknown'},
        {'label': 'Dirty', 'value': 'yes' if dirty_state else 'no'},
        {'label': 'Failing tests', 'value': 0 if failing_tests is None else int(failing_tests)},
        {'label': 'Recent artifact', 'value': recent_artifact or '(none)'},
    ]
