"""Phased-state model for repository and file-level identity scoring.

Computes a deterministic identity phase for each file/node from its
hash-derived fraction and computes selection energy from explicit
relational metadata such as size, type, layer, connectivity, anchors,
and upstream/downstream structure. Used by the holonomic normalizer and
index-validation pipeline.

Domain contracts:
- ``compute_phase(h)`` expects a finite real hash fraction in ``[0.0, 1.0)``.
- ``f_conn(r)`` expects a non-negative integer connection count.
These contracts are intentionally strict so invalid upstream state is
rejected explicitly instead of being normalized silently.

Phase-C separation rule:
- identity phase comes only from the deterministic hash-derived fraction ``h``
- selection/amplitude comes from explicit relational metadata rather than from ``h``
"""
import hashlib
import math
from dataclasses import dataclass

ALPHA = 0.18
BETA = 0.12
B0 = 1024.0
ANCHOR_BETA = 0.08
FLOW_BETA = 0.06

TYPE_WEIGHTS = {
    "py": 1.30,
    "ipynb": 1.20,
    "json": 1.10,
    "yaml": 1.10,
    "yml": 1.10,
    "toml": 1.05,
    "md": 1.00,
    "txt": 0.90,
    "pdf": 0.85,
    "sh": 1.00,
    "bash": 1.00,
    "png": 0.60,
    "jpg": 0.60,
    "jpeg": 0.60,
    "svg": 0.60,
    "zip": 0.40,
    "tar.gz": 0.40,
    "bin": 0.40,
    "gguf": 0.40,
}

LAYER_WEIGHTS = {
    "src/core": 1.40,
    "src/support": 1.20,
    "contracts": 1.35,
    "integration": 1.25,
    "docs/science": 1.15,
    "docs/general": 1.00,
    "scripts": 0.95,
    "tests": 0.85,
    "assets": 0.60,
    "archives": 0.40,
}


def sha256_seed(path: str, size: int, content: bytes) -> bytes:
    h = hashlib.sha256()
    h.update(path.encode("utf-8"))
    h.update(str(size).encode("utf-8"))
    h.update(content)
    return h.digest()


def frac64(seed: bytes) -> float:
    val = int.from_bytes(seed[:8], "big")
    return val / float(2**64)


def f_size(B: int) -> float:
    return 1.0 + ALPHA * math.log(1.0 + B / B0)


def _require_finite_real(name: str, value) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a finite real number")
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be a finite real number")
    return value


def _require_hash_fraction(h: float) -> float:
    value = _require_finite_real("h", h)
    if not 0.0 <= value < 1.0:
        raise ValueError("h must be in [0.0, 1.0)")
    return value


def _require_connection_count(r: int) -> int:
    if isinstance(r, bool) or not isinstance(r, int):
        raise TypeError("r must be a non-negative integer")
    if r < 0:
        raise ValueError("r must be a non-negative integer")
    return r


def _require_non_negative_count(name: str, value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be a non-negative integer")
    if value < 0:
        raise ValueError(f"{name} must be a non-negative integer")
    return value


def _require_positive_weight(name: str, value) -> float:
    weight = _require_finite_real(name, value)
    if weight <= 0.0:
        raise ValueError(f"{name} must be a positive finite real number")
    return weight


def f_conn(r: int) -> float:
    connection_count = _require_connection_count(r)
    return 1.0 + BETA * math.log(1.0 + connection_count)


def f_anchor(anchor_count: int) -> float:
    anchors = _require_non_negative_count("anchor_count", anchor_count)
    return 1.0 + ANCHOR_BETA * math.log(1.0 + anchors)


def f_flow(upstream_count: int, downstream_count: int) -> float:
    upstream = _require_non_negative_count("upstream_count", upstream_count)
    downstream = _require_non_negative_count("downstream_count", downstream_count)
    return 1.0 + FLOW_BETA * math.log(1.0 + upstream + downstream)


def weight_type(ext: str) -> float:
    return TYPE_WEIGHTS.get(ext.lower(), 0.75)


def weight_layer(layer: str) -> float:
    return LAYER_WEIGHTS.get(layer, 0.90)


@dataclass
class FileState:
    path: str
    size: int
    ext: str
    layer: str
    r: int
    h: float
    provenance_weight: float = 1.0
    anchor_count: int = 0
    upstream_count: int = 0
    downstream_count: int = 0
    sector_role_weight: float = 1.0
    selection_weight: float = 0.0
    E_raw: float = 0.0
    E_norm: float = 0.0
    a: float = 0.0
    phi: float = 0.0


def relational_relevance(state: FileState) -> float:
    provenance_weight = _require_positive_weight("provenance_weight", state.provenance_weight)
    sector_role_weight = _require_positive_weight("sector_role_weight", state.sector_role_weight)
    return (
        weight_type(state.ext)
        * weight_layer(state.layer)
        * f_size(state.size)
        * f_conn(state.r)
        * provenance_weight
        * sector_role_weight
        * f_anchor(state.anchor_count)
        * f_flow(state.upstream_count, state.downstream_count)
    )


def compute_raw_energy(state: FileState) -> float:
    return relational_relevance(state)


def normalize(states):
    total = sum(s.E_raw for s in states)
    if total == 0:
        return
    for s in states:
        s.E_norm = s.E_raw / total
        s.a = math.sqrt(s.E_norm)


def compute_phase(h: float) -> float:
    hash_fraction = _require_hash_fraction(h)
    return 2 * math.pi * hash_fraction


def build_states(file_entries):
    states = []

    for entry in file_entries:
        seed = sha256_seed(entry["path"], entry["size"], entry["content"])
        h = frac64(seed)

        state = FileState(
            path=entry["path"],
            size=entry["size"],
            ext=entry["ext"],
            layer=entry["layer"],
            r=entry.get("r", 0),
            h=h,
            provenance_weight=entry.get("provenance_weight", 1.0),
            anchor_count=entry.get("anchor_count", 0),
            upstream_count=entry.get("upstream_count", 0),
            downstream_count=entry.get("downstream_count", 0),
            sector_role_weight=entry.get("sector_role_weight", 1.0),
        )

        state.selection_weight = relational_relevance(state)
        state.E_raw = state.selection_weight
        states.append(state)

    normalize(states)

    for s in states:
        s.phi = compute_phase(s.h)

    return states
