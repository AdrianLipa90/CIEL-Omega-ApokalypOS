"""Phased-state model for repository and file-level identity scoring.

Computes a deterministic phase value for each file/node based on its
content hash, size, and type weight (ALPHA/BETA/B0 constants).  Used by
the holonomic normalizer and index-validation pipeline.
"""
import hashlib
import math
from dataclasses import dataclass

ALPHA = 0.18
BETA = 0.12
B0 = 1024.0

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


def f_conn(r: int) -> float:
    return 1.0 + BETA * math.log(1.0 + r)


def f_seed(h: float) -> float:
    return 0.95 + 0.10 * h


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
    E_raw: float = 0.0
    E_norm: float = 0.0
    a: float = 0.0
    phi: float = 0.0


def compute_raw_energy(state: FileState) -> float:
    return (
        weight_type(state.ext)
        * weight_layer(state.layer)
        * f_size(state.size)
        * f_conn(state.r)
        * f_seed(state.h)
    )


def normalize(states):
    total = sum(s.E_raw for s in states)
    if total == 0:
        return
    for s in states:
        s.E_norm = s.E_raw / total
        s.a = math.sqrt(s.E_norm)


def compute_phase(h: float) -> float:
    return 2 * math.pi * h


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
        )

        state.E_raw = compute_raw_energy(state)
        states.append(state)

    normalize(states)

    for s in states:
        s.phi = compute_phase(s.h)

    return states
