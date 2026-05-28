"""Deterministic local manifest builder for NOEMA Holonomic Doctor."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

_DEFAULT_EXCLUDES = {
    ".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "node_modules", ".venv", "venv", "dist", "build",
}


@dataclass(frozen=True)
class ManifestEntry:
    path: str
    size: int
    sha256: str
    suffix: str


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _should_skip(path: Path, root: Path, excludes: set[str]) -> bool:
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        parts = path.parts
    return any(part in excludes for part in parts)


def noema_ls(root: str | Path, *, excludes: Iterable[str] | None = None) -> list[ManifestEntry]:
    """Build a deterministic local file manifest without shell ls/grep."""
    root_path = Path(root).resolve()
    skip = set(_DEFAULT_EXCLUDES)
    if excludes:
        skip.update(excludes)
    entries: list[ManifestEntry] = []
    for path in sorted(root_path.rglob("*")):
        if not path.is_file() or _should_skip(path, root_path, skip):
            continue
        try:
            data = path.read_bytes()
        except OSError:
            continue
        entries.append(
            ManifestEntry(
                path=path.relative_to(root_path).as_posix(),
                size=len(data),
                sha256=sha256_bytes(data),
                suffix=path.suffix,
            )
        )
    return entries


def manifest_digest(manifest: Iterable[ManifestEntry]) -> str:
    rows = [asdict(entry) for entry in manifest]
    data = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256_bytes(data)


__all__ = ["ManifestEntry", "manifest_digest", "noema_ls", "sha256_bytes"]
