from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Iterable, List, Optional


class EpistemicStatus(str, Enum):
    CANONICAL = 'canonical'
    PROVISIONAL = 'provisional'
    DRAFT = 'draft'
    IMPORTED = 'imported'
    ARCHIVED = 'archived'
    RUNTIME_ONLY = 'runtime-only'
    PRIVATE_ONLY = 'private-only'
    PUBLIC_EXPORTED = 'public-exported'


class OrbitId(int, Enum):
    IDENTITY = 0
    CONSTITUTIVE = 1
    DYNAMIC = 2
    INTERACTION = 3
    OBSERVATION = 4
    BOUNDARY = 5
    EDUCATION = 6


@dataclass(frozen=True)
class WhiteThread:
    source: str
    target: str
    relation: str
    strength: float = 1.0
    freshness: Optional[float] = None
    canonical_agreement: Optional[float] = None


@dataclass(frozen=True)
class OrbitalNode:
    key: str
    label: str
    orbit: OrbitId
    description: str
    default_status: EpistemicStatus
    children: tuple[str, ...] = ()


@dataclass
class IdentityState:
    identity_profile: str = 'omega-local'
    coherence: Optional[float] = None
    resonance: Optional[float] = None
    ethics_gate: str = 'unknown'
    active_contract: Optional[str] = None
    active_canon_export: Optional[str] = None
    active_operator_set: Optional[str] = None
    session_phase: Optional[str] = None
    publication_boundary: Optional[str] = None
    warnings: List[str] = field(default_factory=list)


@dataclass
class CockpitTopology:
    identity: IdentityState = field(default_factory=IdentityState)
    nodes: Dict[str, OrbitalNode] = field(default_factory=dict)
    threads: List[WhiteThread] = field(default_factory=list)

    def orbit_nodes(self, orbit: OrbitId) -> List[OrbitalNode]:
        return [n for n in self.nodes.values() if n.orbit == orbit]

    def get(self, key: str) -> Optional[OrbitalNode]:
        return self.nodes.get(key)

    def add_node(self, node: OrbitalNode) -> None:
        self.nodes[node.key] = node

    def add_thread(self, thread: WhiteThread) -> None:
        self.threads.append(thread)

    def related_threads(self, key: str) -> List[WhiteThread]:
        return [t for t in self.threads if t.source == key or t.target == key]


DEFAULT_NODES: tuple[OrbitalNode, ...] = (
    OrbitalNode(
        key='identity',
        label='Identity Attractor',
        orbit=OrbitId.IDENTITY,
        description='Central coherence, export, ethics, memory, and identity state.',
        default_status=EpistemicStatus.RUNTIME_ONLY,
    ),
    OrbitalNode(
        key='theory',
        label='Theory',
        orbit=OrbitId.CONSTITUTIVE,
        description='Axioms, definitions, derivations, and formal objects.',
        default_status=EpistemicStatus.PROVISIONAL,
        children=('operators', 'constants', 'constraints', 'memory_topology'),
    ),
    OrbitalNode(
        key='operators',
        label='Operators',
        orbit=OrbitId.CONSTITUTIVE,
        description='Executable and formal operators exported from theory.',
        default_status=EpistemicStatus.PROVISIONAL,
    ),
    OrbitalNode(
        key='constants',
        label='Constants',
        orbit=OrbitId.CONSTITUTIVE,
        description='Active constant sets and runtime-imported values.',
        default_status=EpistemicStatus.RUNTIME_ONLY,
    ),
    OrbitalNode(
        key='constraints',
        label='Constraints',
        orbit=OrbitId.CONSTITUTIVE,
        description='Runtime and theory constraints, ethics gates, and invariants.',
        default_status=EpistemicStatus.PROVISIONAL,
    ),
    OrbitalNode(
        key='memory_topology',
        label='Memory Topology',
        orbit=OrbitId.CONSTITUTIVE,
        description='Memory channels, identity dependencies, provenance topology.',
        default_status=EpistemicStatus.DRAFT,
    ),
    OrbitalNode(
        key='execution',
        label='Execution',
        orbit=OrbitId.DYNAMIC,
        description='Kernel runs, orchestration, scheduler, and runtime state.',
        default_status=EpistemicStatus.RUNTIME_ONLY,
        children=('kernel', 'planner', 'session_dynamics', 'command_routing'),
    ),
    OrbitalNode(
        key='kernel',
        label='Kernel',
        orbit=OrbitId.DYNAMIC,
        description='Kernel registry, active backend, runtime stepping, metrics.',
        default_status=EpistemicStatus.RUNTIME_ONLY,
    ),
    OrbitalNode(
        key='planner',
        label='Planner',
        orbit=OrbitId.DYNAMIC,
        description='Task planning and orchestration surface.',
        default_status=EpistemicStatus.DRAFT,
    ),
    OrbitalNode(
        key='session_dynamics',
        label='Session Dynamics',
        orbit=OrbitId.DYNAMIC,
        description='Temporal state evolution for active execution/session chains.',
        default_status=EpistemicStatus.DRAFT,
    ),
    OrbitalNode(
        key='command_routing',
        label='Command Routing',
        orbit=OrbitId.DYNAMIC,
        description='Routing from system intent to executable runtime pathways.',
        default_status=EpistemicStatus.DRAFT,
    ),
    OrbitalNode(
        key='agent',
        label='Agent',
        orbit=OrbitId.INTERACTION,
        description='Agent shell, chat, tools, memory hooks, and I/O routing.',
        default_status=EpistemicStatus.RUNTIME_ONLY,
        children=('chat', 'tools', 'files', 'models'),
    ),
    OrbitalNode(
        key='chat',
        label='Chat',
        orbit=OrbitId.INTERACTION,
        description='Dialogue surface inside the broader agent module.',
        default_status=EpistemicStatus.RUNTIME_ONLY,
    ),
    OrbitalNode(
        key='tools',
        label='Tool Interface',
        orbit=OrbitId.INTERACTION,
        description='Tooling surface and external action adapters.',
        default_status=EpistemicStatus.DRAFT,
    ),
    OrbitalNode(
        key='files',
        label='Files',
        orbit=OrbitId.INTERACTION,
        description='Working files, previews, and local document interaction.',
        default_status=EpistemicStatus.RUNTIME_ONLY,
    ),
    OrbitalNode(
        key='models',
        label='Models',
        orbit=OrbitId.INTERACTION,
        description='GGUF models and active runtime model state.',
        default_status=EpistemicStatus.RUNTIME_ONLY,
    ),
    OrbitalNode(
        key='evidence',
        label='Evidence',
        orbit=OrbitId.OBSERVATION,
        description='Logs, tests, audit, provenance, and diagnostics.',
        default_status=EpistemicStatus.RUNTIME_ONLY,
        children=('observability', 'tests', 'audit', 'provenance', 'crossrefs'),
    ),
    OrbitalNode(
        key='observability',
        label='Observability',
        orbit=OrbitId.OBSERVATION,
        description='Live runtime metrics, logs, errors, and diagnostics.',
        default_status=EpistemicStatus.RUNTIME_ONLY,
    ),
    OrbitalNode(
        key='tests',
        label='Tests',
        orbit=OrbitId.OBSERVATION,
        description='Executable validation layer and coverage surface.',
        default_status=EpistemicStatus.PROVISIONAL,
    ),
    OrbitalNode(
        key='audit',
        label='Audit',
        orbit=OrbitId.OBSERVATION,
        description='Audit trail, evidence integrity, and run trace review.',
        default_status=EpistemicStatus.DRAFT,
    ),
    OrbitalNode(
        key='provenance',
        label='Provenance',
        orbit=OrbitId.OBSERVATION,
        description='Source-of-truth, lineage, and artifact traceability.',
        default_status=EpistemicStatus.DRAFT,
    ),
    OrbitalNode(
        key='crossrefs',
        label='Crossrefs',
        orbit=OrbitId.OBSERVATION,
        description='Formal and implementation cross-references across system layers.',
        default_status=EpistemicStatus.DRAFT,
    ),
    OrbitalNode(
        key='boundary',
        label='Publication Boundary',
        orbit=OrbitId.BOUNDARY,
        description='Public/private separation, export manifests, and sanitization state.',
        default_status=EpistemicStatus.PRIVATE_ONLY,
    ),
    OrbitalNode(
        key='analogies',
        label='Analogies',
        orbit=OrbitId.EDUCATION,
        description='Educational analogy layer translating formal concepts into mnemonic images.',
        default_status=EpistemicStatus.PUBLIC_EXPORTED,
        children=('analogy_registry', 'truth_attractor_analogies', 'mnemonic_book'),
    ),
    OrbitalNode(
        key='analogy_registry',
        label='Analogy Registry',
        orbit=OrbitId.EDUCATION,
        description='Registry mapping formal concepts to mnemonic images and the limits of each analogy.',
        default_status=EpistemicStatus.PUBLIC_EXPORTED,
    ),
    OrbitalNode(
        key='truth_attractor_analogies',
        label='Truth Attractor Analogies',
        orbit=OrbitId.EDUCATION,
        description='Analogy set for truth as attractor, convergence, nodes, and white threads.',
        default_status=EpistemicStatus.PUBLIC_EXPORTED,
    ),
    OrbitalNode(
        key='mnemonic_book',
        label='Mnemonic Book For Kids',
        orbit=OrbitId.EDUCATION,
        description='Child-safe mnemonic guide for Omega concepts and cockpit language.',
        default_status=EpistemicStatus.PUBLIC_EXPORTED,
    ),
)


DEFAULT_THREADS: tuple[WhiteThread, ...] = (
    WhiteThread('theory', 'operators', 'exports', strength=0.95),
    WhiteThread('operators', 'kernel', 'drives', strength=0.95),
    WhiteThread('kernel', 'agent', 'feeds', strength=0.80),
    WhiteThread('agent', 'memory_topology', 'depends_on', strength=0.78),
    WhiteThread('evidence', 'boundary', 'validates', strength=0.90),
    WhiteThread('constants', 'kernel', 'parameterizes', strength=0.85),
    WhiteThread('constraints', 'execution', 'bounds', strength=0.88),
    WhiteThread('theory', 'analogies', 'teaches', strength=0.74),
    WhiteThread('analogies', 'agent', 'explains', strength=0.68),
    WhiteThread('analogies', 'evidence', 'bridges', strength=0.61),
)


def build_default_topology() -> CockpitTopology:
    topology = CockpitTopology()
    for node in DEFAULT_NODES:
        topology.add_node(node)
    for thread in DEFAULT_THREADS:
        topology.add_thread(thread)
    return topology


def orbit_navigation_groups(topology: Optional[CockpitTopology] = None) -> Dict[OrbitId, List[OrbitalNode]]:
    topology = topology or build_default_topology()
    return {
        OrbitId.IDENTITY: topology.orbit_nodes(OrbitId.IDENTITY),
        OrbitId.CONSTITUTIVE: topology.orbit_nodes(OrbitId.CONSTITUTIVE),
        OrbitId.DYNAMIC: topology.orbit_nodes(OrbitId.DYNAMIC),
        OrbitId.INTERACTION: topology.orbit_nodes(OrbitId.INTERACTION),
        OrbitId.OBSERVATION: topology.orbit_nodes(OrbitId.OBSERVATION),
        OrbitId.BOUNDARY: topology.orbit_nodes(OrbitId.BOUNDARY),
        OrbitId.EDUCATION: topology.orbit_nodes(OrbitId.EDUCATION),
    }


def flatten_navigation(topology: Optional[CockpitTopology] = None) -> List[OrbitalNode]:
    topology = topology or build_default_topology()
    nodes: List[OrbitalNode] = []
    for orbit in OrbitId:
        nodes.extend(sorted(topology.orbit_nodes(orbit), key=lambda n: n.label.lower()))
    return nodes


def labels(nodes: Iterable[OrbitalNode]) -> List[str]:
    return [n.label for n in nodes]
