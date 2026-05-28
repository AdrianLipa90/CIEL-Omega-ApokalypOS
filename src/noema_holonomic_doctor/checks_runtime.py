"""Runtime-oriented static checks for NOEMA Holonomic Doctor."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .manifest import ManifestEntry

_TEXT_SUFFIXES = {".py", ".md", ".txt", ".json", ".jsonl", ".yaml", ".yml", ".toml", ".diff", ".patch"}
_RH = "R" + "_H"
_MINUS_RH = "1 - " + _RH
_SNAP_RH = "1.0 - snap.get(" + repr(_RH)
_SNAPSHOT_RH = "1.0 - snapshot.get(" + repr(_RH)


@dataclass(frozen=True)
class Finding:
    code: str
    severity: str
    message: str
    path: str | None = None
    evidence: dict[str, Any] = field(default_factory=dict)


def path_kind(path: str) -> str:
    """Classify paths before turning textual matches into runtime findings."""
    if path.startswith("tests/") or "/tests/" in path:
        return "test_fixture"
    if path == "src/noema_holonomic_doctor/constraints.py":
        return "rule_text"
    if path.endswith((".md", ".rst", ".txt")):
        return "documentation"
    if path.endswith((".diff", ".patch")) or path.startswith("patches/"):
        return "patch_candidate"
    return "runtime_code"


def _read_text(root: Path, entry: ManifestEntry, max_bytes: int) -> str | None:
    if entry.suffix not in _TEXT_SUFFIXES or entry.size > max_bytes:
        return None
    try:
        return (root / entry.path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def check_inverted_rh(root: Path, manifest: list[ManifestEntry], *, max_bytes: int = 256_000) -> list[Finding]:
    findings: list[Finding] = []
    for entry in manifest:
        kind = path_kind(entry.path)
        if kind != "runtime_code":
            continue
        text = _read_text(root, entry, max_bytes)
        if text is None or _RH not in text:
            continue
        suspicious = _MINUS_RH in text or _SNAP_RH in text or _SNAPSHOT_RH in text
        uses_helper = "rh_defect_score" in text or "rh_coherence_score" in text or "bounded_holonomic_coherence" in text
        if suspicious and not uses_helper:
            findings.append(
                Finding(
                    code="rh_orientation_candidate",
                    severity="high",
                    message="Raw holonomic metric appears converted without a bounded helper.",
                    path=entry.path,
                    evidence={"constraint": "no_unbounded_rh_metric", "path_kind": kind},
                )
            )
    return findings


def check_rh_pipeline_hook(root: Path, manifest: list[ManifestEntry], *, max_bytes: int = 256_000) -> list[Finding]:
    paths = {entry.path for entry in manifest}
    if "src/ciel_sot_agent/rh_pipeline_jfunctional.py" not in paths:
        return []
    pipeline_entry = next((entry for entry in manifest if entry.path == "src/ciel_sot_agent/ciel_pipeline.py"), None)
    if pipeline_entry is None:
        return []
    text = _read_text(root, pipeline_entry, max_bytes) or ""
    if "compute_pipeline_j_functional" in text:
        return []
    return [
        Finding(
            code="rh_pipeline_hook_pending",
            severity="medium",
            message="R_H pipeline adapter exists, but ciel_pipeline.py is not hooked yet.",
            path="src/ciel_sot_agent/ciel_pipeline.py",
        )
    ]


def run_static_checks(root: str | Path, manifest: list[ManifestEntry], *, max_bytes: int = 256_000) -> list[Finding]:
    root_path = Path(root).resolve()
    findings: list[Finding] = []
    findings.extend(check_inverted_rh(root_path, manifest, max_bytes=max_bytes))
    findings.extend(check_rh_pipeline_hook(root_path, manifest, max_bytes=max_bytes))
    return findings


__all__ = ["Finding", "check_inverted_rh", "check_rh_pipeline_hook", "path_kind", "run_static_checks"]
