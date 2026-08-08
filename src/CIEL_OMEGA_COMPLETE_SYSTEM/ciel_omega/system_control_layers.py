"""NOEMA/CIEL system control layers: Oracle -> Doctor -> Actuator.

Oracle is read-only and creates a deterministic file mutation plan.
Doctor is the fail-closed execution gate.
Actuator is the only file mutation layer and performs atomic writes with
post-write verification, rollback support and hash-chained receipts.

Invariant: READ != DECIDE != MUTATE.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, Sequence
import hashlib
import json
import os
import tempfile
import time


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


class Verdict(str, Enum):
    CONTINUE = "CONTINUE"
    CONTINUE_PROXY = "CONTINUE_PROXY"
    CONTINUE_RESEARCH = "CONTINUE_RESEARCH"
    WARN_REVIEW_REQUIRED = "WARN_REVIEW_REQUIRED"
    STAGE_ONLY = "STAGE_ONLY"
    QUARANTINE = "QUARANTINE"
    STOP_CRITICAL = "STOP_CRITICAL"
    DENY_CANON = "DENY_CANON"
    DENY_CURRENT = "DENY_CURRENT"
    DENY_DESTRUCTIVE_APPLY = "DENY_DESTRUCTIVE_APPLY"


@dataclass(frozen=True)
class FileMutationPlan:
    target: str
    operation: str
    existed: bool
    current_sha256: Optional[str]
    proposed_sha256: str
    expected_sha256: Optional[str]
    byte_length: int
    allowed_root: Optional[str]
    path_within_scope: bool
    target_is_symlink: bool
    oracle_status: str
    oracle_findings: tuple[str, ...]
    plan_sha256: str


@dataclass(frozen=True)
class DoctorDecision:
    verdict: Verdict
    findings: tuple[str, ...]
    plan_sha256: str
    authority_id: Optional[str]
    allow_apply: bool


@dataclass(frozen=True)
class ActuationReceipt:
    schema: str
    timestamp_ns: int
    target: str
    operation: str
    before_sha256: Optional[str]
    after_sha256: str
    plan_sha256: str
    doctor_verdict: str
    authority_id: Optional[str]
    atomic_replace: bool
    rollback_supported: bool
    rollback_performed: bool
    verified: bool
    predecessor_receipt_sha256: Optional[str]
    receipt_sha256: str


class FileOracle:
    """Read-only planner. Never mutates target files."""

    def __init__(self, allowed_roots: Sequence[str | Path]):
        self.allowed_roots = tuple(Path(p).resolve() for p in allowed_roots)
        if not self.allowed_roots:
            raise ValueError("at least one allowed root is required")

    def _scope(self, target: Path) -> tuple[bool, Optional[Path]]:
        resolved = target.resolve(strict=False)
        for root in self.allowed_roots:
            try:
                resolved.relative_to(root)
                return True, root
            except ValueError:
                pass
        return False, None

    def inspect(self, target: str | Path, proposed_content: bytes, *, expected_sha256: Optional[str] = None) -> FileMutationPlan:
        p = Path(target)
        in_scope, root = self._scope(p)
        existed = p.exists()
        is_link = p.is_symlink()
        current_sha = None
        findings: list[str] = []

        if existed:
            if not p.is_file():
                findings.append("TARGET_NOT_REGULAR_FILE")
            elif not is_link:
                current_sha = sha256_bytes(p.read_bytes())

        proposed_sha = sha256_bytes(proposed_content)
        if not in_scope:
            findings.append("PATH_OUTSIDE_ALLOWED_ROOT")
        if is_link:
            findings.append("TARGET_IS_SYMLINK")
        if expected_sha256 is not None and current_sha != expected_sha256:
            findings.append("EXPECTED_SHA_MISMATCH")

        operation = "NOOP" if existed and current_sha == proposed_sha and not is_link else ("UPDATE" if existed else "CREATE")
        body = {
            "target": str(p.resolve(strict=False)),
            "operation": operation,
            "existed": existed,
            "current_sha256": current_sha,
            "proposed_sha256": proposed_sha,
            "expected_sha256": expected_sha256,
            "byte_length": len(proposed_content),
            "allowed_root": None if root is None else str(root),
            "path_within_scope": in_scope,
            "target_is_symlink": is_link,
            "oracle_status": "PASS" if not findings else "BLOCKED",
            "oracle_findings": tuple(findings),
        }
        return FileMutationPlan(**body, plan_sha256=sha256_bytes(canonical_json(body)))


class Doctor:
    """Fail-closed gate. Never edits files."""

    def evaluate(self, plan: FileMutationPlan, *, authority_id: Optional[str], explicit_write_authority: bool) -> DoctorDecision:
        findings = list(plan.oracle_findings)
        if plan.operation == "NOOP":
            return DoctorDecision(Verdict.CONTINUE, tuple(findings + ["NOOP_IDENTICAL_CONTENT"]), plan.plan_sha256, authority_id, True)
        if not explicit_write_authority:
            return DoctorDecision(Verdict.STAGE_ONLY, tuple(findings + ["WRITE_AUTHORITY_MISSING"]), plan.plan_sha256, authority_id, False)
        hard = {"PATH_OUTSIDE_ALLOWED_ROOT", "TARGET_IS_SYMLINK", "TARGET_NOT_REGULAR_FILE", "EXPECTED_SHA_MISMATCH"}
        if any(x in hard for x in findings):
            return DoctorDecision(Verdict.DENY_DESTRUCTIVE_APPLY, tuple(findings), plan.plan_sha256, authority_id, False)
        return DoctorDecision(Verdict.CONTINUE, tuple(findings), plan.plan_sha256, authority_id, True)


class ReceiptLedger:
    """Append-only hash-chained JSONL receipts."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def _tail_sha(self) -> Optional[str]:
        if not self.path.is_file() or self.path.stat().st_size == 0:
            return None
        last = None
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    last = json.loads(line)
        return None if last is None else last.get("receipt_sha256")

    def append(self, body: dict) -> dict:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        entry = dict(body)
        entry["predecessor_receipt_sha256"] = self._tail_sha()
        entry["receipt_sha256"] = sha256_bytes(canonical_json(entry))
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, sort_keys=True, ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())
        return entry


class FileActuator:
    """Atomic file editor. Executes only Doctor-approved plans."""

    def __init__(self, ledger: ReceiptLedger):
        self.ledger = ledger

    def apply(self, plan: FileMutationPlan, decision: DoctorDecision, proposed_content: bytes) -> ActuationReceipt:
        if decision.plan_sha256 != plan.plan_sha256:
            raise PermissionError("DOCTOR_PLAN_BINDING_MISMATCH")
        if decision.verdict != Verdict.CONTINUE or not decision.allow_apply:
            raise PermissionError(f"DOCTOR_DENIED:{decision.verdict.value}")
        if sha256_bytes(proposed_content) != plan.proposed_sha256:
            raise ValueError("PROPOSED_CONTENT_SHA_MISMATCH")

        target = Path(plan.target)
        if target.is_symlink():
            raise PermissionError("ACTUATOR_REFUSES_SYMLINK")

        if plan.operation == "NOOP":
            after = sha256_bytes(target.read_bytes())
            entry = self.ledger.append({
                "schema": "noema.file-actuation/v1", "timestamp_ns": time.time_ns(),
                "target": str(target), "operation": "NOOP", "before_sha256": plan.current_sha256,
                "after_sha256": after, "plan_sha256": plan.plan_sha256,
                "doctor_verdict": decision.verdict.value, "authority_id": decision.authority_id,
                "atomic_replace": False, "rollback_supported": True, "rollback_performed": False,
                "verified": after == plan.proposed_sha256,
            })
            return ActuationReceipt(**entry)

        target.parent.mkdir(parents=True, exist_ok=True)
        old_bytes = target.read_bytes() if target.exists() else None
        old_sha = sha256_bytes(old_bytes) if old_bytes is not None else None
        if plan.expected_sha256 is not None and old_sha != plan.expected_sha256:
            raise PermissionError("ACTUATOR_EXPECTED_SHA_MISMATCH")

        tmp_name = None
        try:
            fd, tmp_name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".noema-stage", dir=str(target.parent))
            with os.fdopen(fd, "wb") as f:
                f.write(proposed_content)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_name, target)
            tmp_name = None
            dir_fd = os.open(str(target.parent), os.O_RDONLY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
            after_sha = sha256_bytes(target.read_bytes())
            if after_sha != plan.proposed_sha256:
                raise IOError("POST_WRITE_SHA_MISMATCH")
        except Exception:
            if tmp_name is not None:
                Path(tmp_name).unlink(missing_ok=True)
            if old_bytes is None:
                target.unlink(missing_ok=True)
            else:
                fd, restore = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".noema-rollback", dir=str(target.parent))
                with os.fdopen(fd, "wb") as f:
                    f.write(old_bytes)
                    f.flush()
                    os.fsync(f.fileno())
                os.replace(restore, target)
            raise

        entry = self.ledger.append({
            "schema": "noema.file-actuation/v1", "timestamp_ns": time.time_ns(),
            "target": str(target), "operation": plan.operation, "before_sha256": old_sha,
            "after_sha256": after_sha, "plan_sha256": plan.plan_sha256,
            "doctor_verdict": decision.verdict.value, "authority_id": decision.authority_id,
            "atomic_replace": True, "rollback_supported": True, "rollback_performed": False,
            "verified": True,
        })
        return ActuationReceipt(**entry)


class FileEditControlPlane:
    """Oracle -> Doctor -> Actuator orchestration."""

    def __init__(self, *, allowed_roots: Sequence[str | Path], ledger_path: str | Path):
        self.oracle = FileOracle(allowed_roots)
        self.doctor = Doctor()
        self.actuator = FileActuator(ReceiptLedger(ledger_path))

    def edit(self, target: str | Path, content: str | bytes, *, authority_id: Optional[str], explicit_write_authority: bool, expected_sha256: Optional[str] = None):
        payload = content.encode("utf-8") if isinstance(content, str) else bytes(content)
        plan = self.oracle.inspect(target, payload, expected_sha256=expected_sha256)
        decision = self.doctor.evaluate(plan, authority_id=authority_id, explicit_write_authority=explicit_write_authority)
        receipt = self.actuator.apply(plan, decision, payload) if decision.allow_apply else None
        return plan, decision, receipt


__all__ = [
    "Verdict", "FileMutationPlan", "DoctorDecision", "ActuationReceipt",
    "FileOracle", "Doctor", "ReceiptLedger", "FileActuator", "FileEditControlPlane",
]
