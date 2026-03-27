"""CIEL/Ω Memory — Unified orchestrator: capture → TMP → bifurcation → durable.

Split from: unified_memory.py (lines 478–601)
"""

from __future__ import annotations

import datetime as dt
import json
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from memory.monolith.data_types import DataVector, MemoriseD
from memory.monolith.defaults import (
    DEFAULT_HEURISTICS_SELF,
    DEFAULT_HEURISTICS_USER,
    DEFAULT_RULES_IMMUTABLE,
)
from memory.monolith.tmp_processor import TMPKernel
from memory.monolith.tsm_storage import TSMWriterSQL
from memory.monolith.wpm_storage import WPMWriterHDF5


_SYSTEM_ROOT = Path(__file__).resolve().parents[3]


class UnifiedMemoryOrchestrator:
    """Full pipeline: capture → TMP gate → bifurcation → dual durable save."""

    def __init__(
        self,
        cfg_dir: Path = _SYSTEM_ROOT / "configs",
        tsm_db: Path = _SYSTEM_ROOT / "CIEL_MEMORY_SYSTEM" / "TSM" / "ledger" / "memory_ledger.db",
        wpm_h5: Path = _SYSTEM_ROOT / "CIEL_MEMORY_SYSTEM" / "WPM" / "wave_snapshots" / "wave_archive.h5",
    ):
        cfg_dir.mkdir(parents=True, exist_ok=True)
        tsm_db.parent.mkdir(parents=True, exist_ok=True)
        wpm_h5.parent.mkdir(parents=True, exist_ok=True)

        self._ensure_default_config(cfg_dir / "rules_immutable.json", DEFAULT_RULES_IMMUTABLE)
        self._ensure_default_config(cfg_dir / "heuristics_user.json", DEFAULT_HEURISTICS_USER)
        self._ensure_default_config(cfg_dir / "heuristics_self.json", DEFAULT_HEURISTICS_SELF)

        self.tsm = TSMWriterSQL(tsm_db)
        try:
            self.wpm = WPMWriterHDF5(wpm_h5)
        except RuntimeError:
            self.wpm = None  # h5py not available — WPM disabled
        self.tmp = TMPKernel(cfg_dir)

        self._tmp_reports: List[Dict[str, Any]] = []
        self._verification_queue: List[Dict[str, Any]] = []
        self.allow_system_force_save = True
        self.allow_user_force_save = True

    @staticmethod
    def _ensure_default_config(path: Path, obj: Dict[str, Any]) -> None:
        if not path.exists():
            path.write_text(json.dumps(obj, indent=2), encoding="utf-8")

    def capture(self, context: str, sense: Any, associations=None, timestamp=None, meta=None) -> DataVector:
        return DataVector(context=context, sense=sense, associations=associations, timestamp=timestamp, meta=meta)

    def run_tmp(self, D: DataVector) -> Dict[str, Any]:
        out = self.tmp.process(D)
        verdict = out["OUT"]["verdict"]
        level = "INFO" if verdict == "PASS" else ("IMPORTANT" if verdict == "HOLD" else "CRITICAL")
        rep = {
            "report_id": str(uuid.uuid4()),
            "created_at": dt.datetime.utcnow().isoformat(),
            "level": level,
            "payload": {"D_id": D.id, "OUT": out},
            "requires_user_verification": level != "INFO",
            "verified_by_user": False,
        }
        self._tmp_reports.append(rep)
        if rep["requires_user_verification"]:
            self._verification_queue.append(rep)
        return out

    def _make_memorised(self, D: DataVector, a1: Dict, a2: Dict, rationale: str, source: str = "TMP") -> MemoriseD:
        return MemoriseD(
            memorise_id=str(uuid.uuid4()), created_at=dt.datetime.utcnow().isoformat(),
            D_id=D.id, D_context=D.D_C, D_sense=D.D_S, D_associations=D.D_A,
            D_timestamp=D.D_T, D_meta=D.D_M, D_type=a1.get("D_TYPE", "unknown"),
            D_attr=a1.get("D_ATTR", {}), weights=a2.get("weights", {}),
            rationale=rationale, source=source,
        )

    def _save_dual(self, mem: MemoriseD, wave_arrays=None, wave_attrs=None) -> Dict[str, str]:
        tsm_ref = self.tsm.save(mem)
        wpm_ref = "WPM:disabled"
        if self.wpm is not None:
            wpm_ref = self.wpm.save_with_wave(mem, wave_arrays=wave_arrays, attrs=wave_attrs) if (wave_arrays or wave_attrs) else self.wpm.save(mem)
            self.tsm.attach_wpm_ref(mem.memorise_id, wpm_ref)
        return {"tsm_ref": tsm_ref, "wpm_ref": wpm_ref, "memorise_id": mem.memorise_id}

    def promote_if_bifurcated(self, D: DataVector, tmp_out: Dict, wave_arrays=None, wave_attrs=None) -> Optional[Dict[str, str]]:
        a2, a1 = tmp_out["OUT"], tmp_out.get("A1", {})
        if a2.get("verdict") == "PASS" and a2.get("bifurcation") == 1:
            mem = self._make_memorised(D, a1, a2, rationale="B=1 collapse from TMP.")
            return self._save_dual(mem, wave_arrays=wave_arrays, wave_attrs=wave_attrs)
        return None

    def user_force_save(self, D: DataVector, tmp_out: Dict, reason: str, wave_arrays=None, wave_attrs=None) -> Optional[Dict[str, str]]:
        if not self.allow_user_force_save:
            return None
        a2, a1 = tmp_out["OUT"], tmp_out.get("A1", {})
        mem = self._make_memorised(D, a1, a2, rationale=f"User override: {reason}", source="USER_OVERRIDE")
        return self._save_dual(mem, wave_arrays=wave_arrays, wave_attrs=wave_attrs)

    def daily_maintenance(self) -> Dict[str, int]:
        kept, purged = 0, 0
        new_reports: List[Dict[str, Any]] = []
        for r in self._tmp_reports:
            if r["level"] == "INFO":
                purged += 1
            else:
                kept += 1
                new_reports.append(r)
        self._tmp_reports = new_reports
        self._verification_queue = [
            r for r in self._tmp_reports
            if r["requires_user_verification"] and not r["verified_by_user"]
        ]
        return {"kept": kept, "purged": purged, "pending_verifications": len(self._verification_queue)}
