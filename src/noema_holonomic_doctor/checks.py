"""Static diagnostic checks for NOEMA Holonomic Doctor."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .manifest import ManifestEntry

_TEXT_SUFFIXES = {".py", ".md", ".txt", ".json", ".jsonl", ".yaml", ".yml", ".toml", ".diff", ".patch"}


@dataclass(frozen=True)
class Finding:
    code: str
    severity: str
    message: str
    path: str | None = None
    evidence: dict[str, Any] = field(default_factory=dict)


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
        text = _read_text(root, entry, max_bytes)
        if text is None or "R_H" not in text:
            continue
        suspicious = "1 - R_H" in text or "1.0 - snap.get(\"R_H\"" in text or "1.0 - snapshot.get(\"R_H\"" in text
        uses_helper = "rh_defect_score" in text or "rh_coherence_score" in text
        if suspicious and not uses_helper:
            findings.append(
                Finding(
                    code="inverted_rh_metric_candidate",
                    severity="high",
                    message="Raw R_H appears converted through 1 - R_H without the canonical bounded helper.",
                    path=entry.path,
                    evidence={"constraint": "no_inverted_rh_metric"},
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
    if "patches/fix_rh_jfunctional_pipeline_hook.diff" in paths:
        return [
            Finding(
                code="rh_pipeline_hook_pending",
                severity="medium",
                message="R_H pipeline adapter exists, but ciel_pipeline.py is not hooked yet; patch candidate is present.",
                path="src/ciel_sot_agent/ciel_pipeline.py",
                evidence={"patch": "patches/fix_rh_jfunctional_pipeline_hook.diff"},
            )
        ]
    return [
        Finding(
            code="dead_rh_pipeline_adapter",
            severity="medium",
            message="R_H pipeline adapter exists, but no runtime hook or patch candidate was found.",
            path="src/ciel_sot_agent/rh_pipeline_jfunctional.py",
        )
    ]


def run_static_checks(root: str | Path, manifest: list[ManifestEntry], *, max_bytes: int = 256_000) -> list[Finding]:
    root_path = Path(root).resolve()
    findings: list[Finding] = []
    findings.extend(check_inverted_rh(root_path, manifest, max_bytes=max_bytes))
    findings.extend(check_rh_pipeline_hook(root_path, manifest, max_bytes=max_bytes))
    return findings


__all__ = ["Finding", "check_inverted_rh", "check_rh_pipeline_hook", "run_static_checks"]
