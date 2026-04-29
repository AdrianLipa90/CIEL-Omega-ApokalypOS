#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CIEL-Memory Monolith (Pro Core) — single-file edition
Author(s): Adrian Lipa, CIEL  |  Affiliation: Intention Lab (project patronage)
License: MIT (see LICENSE if split to repo)

Includes:
- TMP logic (A1/A2), RULE/HEUR with immutable/user/self + spectral multiplier γ in [-1,1] → [0,2]
- Durable: TSM (SQLite) + WPM (HDF5) with wave snapshots (amplitude/phase) + attrs
- Unified Orchestrator (capture → TMP → bifurcation → durable)
- CLI: status | run | verify | backup | export | wavesave
- Kernel adapter: capture_wave(amplitude, phase, attrs)
- Self-contained default configs (JSON embedded) with safe local paths

Note:
- HDF5 is attempted first. If `h5py` is unavailable, WPM explicitly falls back to JSONL.
- All file I/O stays local by design.
"""

from __future__ import annotations
import argparse
import dataclasses
import datetime as dt
import hashlib
import json
import os
import re
import sqlite3
import sys
import textwrap
import uuid
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from core.braid.adapter import KernelAdapter
    from core.braid.defaults import make_default_runtime
except Exception:  # pragma: no cover - package mode
    try:
        from ...core.braid.adapter import KernelAdapter  # type: ignore
        from ...core.braid.defaults import make_default_runtime  # type: ignore
    except Exception:  # pragma: no cover - keep memory usable without braid import
        KernelAdapter = None  # type: ignore
        make_default_runtime = None  # type: ignore

# ---------------------------
# Self-contained default configs (used if 'configs/*.json' files not found)
# ---------------------------

DEFAULT_RULES_IMMUTABLE = {
    "require_context": True,
    "require_sense": True,
    "ethical_gate": True,
    "forbidden_patterns": ["illegal", "harm", "exploit"]
}

DEFAULT_HEURISTICS_USER = {
    "weights": {"logic": 0.35, "semantic": 0.25, "context": 0.20, "emotion": 0.20},
    "boosts": {"novelty_hint": 0.15, "trusted_source": 0.10},
    "penalties": {"contradiction_flag": -0.25, "ethics_warning": -0.50}
}

DEFAULT_HEURISTICS_SELF = {
    "weights": {"logic": 0.30, "semantic": 0.25, "context": 0.25, "emotion": 0.20},
    "boosts": {"long_form": 0.10, "associations_present": 0.05},
    "penalties": {"too_short": -0.15}
}

# ---------------------------
# Utility: SI timestamp validation
# ---------------------------

ISO8601_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?$"
)

def is_iso8601(ts: str) -> bool:
    if not isinstance(ts, str):
        return False
    if ISO8601_RE.match(ts):
        return True
    try:
        _ = dt.datetime.fromisoformat(ts)
        return True
    except Exception:
        return False

def validate_timestamp(ts: Optional[str]) -> Tuple[bool, Optional[str]]:
    if not ts:
        return (False, None)
    if is_iso8601(ts):
        try:
            if ts.endswith("Z"):
                norm = dt.datetime.fromisoformat(ts.replace("Z", "+00:00")).isoformat()
            else:
                norm = dt.datetime.fromisoformat(ts).isoformat()
            return (True, norm)
        except Exception:
            return (True, ts)
    return (False, None)

def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))

# ---------------------------
# Spectral multiplier γ(D) with category spectrum in [-1, 1] (median → [0,2] around 1.0)
# ---------------------------

def spectral_categories(D: Dict[str, Any]) -> Dict[str, float]:
    sense = str(D.get("D_S", "") or "").strip()
    associations = D.get("D_A", []) or []
    meta = D.get("D_M", {}) or {}

    clarity = 0.4 if len(sense) >= 64 else (0.2 if len(sense) >= 16 else -0.2)
    relevance = 0.2 if associations else -0.1
    originality = 0.5 if meta.get("novelty_hint") else 0.0
    coherence = -0.6 if meta.get("contradiction_flag") else 0.1
    ethical = -0.7 if meta.get("ethics_warning") else 0.2
    return {
        "clarity": clarity,
        "relevance": relevance,
        "originality": originality,
        "coherence": coherence,
        "ethical_harmony": ethical,
    }

def gamma_from_categories(values: Dict[str, float]) -> float:
    if not values:
        return 1.0
    vals = [clamp(v, -1.0, 1.0) for v in values.values()]
    # median without numpy
    s = sorted(vals)
    n = len(s)
    med = s[n // 2] if n % 2 == 1 else 0.5 * (s[n // 2 - 1] + s[n // 2])
    g = 1.0 + med
    return clamp(g, 0.0, 2.0)

# ---------------------------
# Data types
# ---------------------------

@dataclass
class MemoriseD:
    memorise_id: str
    created_at: str
    D_id: str
    D_context: str
    D_sense: Any
    D_associations: List[Any]
    D_timestamp: str
    D_meta: Dict[str, Any]
    D_type: str
    D_attr: Dict[str, Any]
    weights: Dict[str, Any]
    rationale: str = ""
    source: str = "TMP"

class DataVector:
    def __init__(
        self,
        context: str,
        sense: Any,
        associations: Optional[List[Any]] = None,
        timestamp: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
    ):
        self.id = str(uuid.uuid4())
        self.D_C = context
        self.D_S = sense
        self.D_A = associations or []
        self.D_T = timestamp or dt.datetime.utcnow().isoformat()
        self.D_M = meta or {}

# ---------------------------
# RULE/HEUR engine
# ---------------------------

class RuleHeuristicsEngine:
    def __init__(self, cfg_dir: Path):
        self.cfg_dir = Path(cfg_dir)
        self.immutable = self._load_json("rules_immutable.json", DEFAULT_RULES_IMMUTABLE)
        self.user = self._load_json("heuristics_user.json", DEFAULT_HEURISTICS_USER)
        self.selfcfg = self._load_json("heuristics_self.json", DEFAULT_HEURISTICS_SELF)

    def _load_json(self, name: str, default_obj: Dict[str, Any]) -> Dict[str, Any]:
        try:
            p = self.cfg_dir / name
            if p.exists():
                return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
        return json.loads(json.dumps(default_obj))  # deep copy

    def ethical_gate(self, text: str) -> bool:
        if not self.immutable.get("ethical_gate", True):
            return True
        for pat in self.immutable.get("forbidden_patterns", []):
            if re.search(pat, text or "", flags=re.IGNORECASE):
                return False
        return True

    def weight(self, D_dict: Dict[str, Any]) -> Dict[str, float]:
        sense = str(D_dict.get("D_S", "")).strip()
        meta = D_dict.get("D_M", {}) or {}
        associations = D_dict.get("D_A", []) or []

        # base
        logic = 0.6 if len(sense) >= 32 else 0.4
        semantic = 0.6 if len(sense.split()) >= 5 else 0.4
        context = 0.55 if D_dict.get("D_C") else 0.30
        emotion = 0.50

        # user boosts/penalties
        u = self.user
        if meta.get("trusted_source"):
            logic += u["boosts"].get("trusted_source", 0.10)
        if meta.get("novelty_hint"):
            semantic += u["boosts"].get("novelty_hint", 0.15)
        if meta.get("contradiction_flag"):
            logic += u["penalties"].get("contradiction_flag", -0.25)
        if meta.get("ethics_warning"):
            semantic += u["penalties"].get("ethics_warning", -0.50)

        # self boosts/penalties
        s = self.selfcfg
        if len(sense) >= 120:
            logic += s["boosts"].get("long_form", 0.10)
        if associations:
            context += s["boosts"].get("associations_present", 0.05)
        if len(sense) < 8:
            semantic += s["penalties"].get("too_short", -0.15)

        def _cl(x: float) -> float:
            return clamp(x, 0.0, 1.0)

        return {"W_L": _cl(logic), "W_S": _cl(semantic), "W_K": _cl(context), "W_E": _cl(emotion)}

# ---------------------------
# TMP Kernel (A1/A2)
# ---------------------------

class TMPKernel:
    def __init__(self, cfg_dir: Path):
        self.rh = RuleHeuristicsEngine(cfg_dir)
        self.immutable_rules = {
            "require_context": True,
            "require_sense": True,
            "ethical_gate": True,
        }

    def first_analysis(self, D: DataVector) -> Dict[str, Any]:
        if self.immutable_rules["require_context"] and not D.D_C:
            return {"verdict": "FAIL", "response": "WTF? Missing context.", "bifurcation": 0}
        if self.immutable_rules["require_sense"] and not D.D_S:
            return {"verdict": "FAIL", "response": "WTF? Missing sense.", "bifurcation": 0}
        ok_ts, norm_ts = validate_timestamp(D.D_T)
        if not ok_ts:
            return {"verdict": "FAIL", "response": "WTF? Invalid timestamp.", "bifurcation": 0}
        D.D_T = norm_ts or D.D_T

        # Light typing
        if isinstance(D.D_S, str) and len(D.D_S.strip()) >= 4:
            return {"verdict": "PASS", "D_TYPE": "text", "D_ATTR": {"length": len(D.D_S)}, "bifurcation": 0}
        return {"verdict": "HOLD", "response": "WTF? Provide more details.", "bifurcation": 0}

    def second_analysis(self, D: DataVector, D_TYPE: str, D_ATTR: Dict[str, Any]) -> Dict[str, Any]:
        text = str(D.D_S or "")
        if self.immutable_rules["ethical_gate"] and not self.rh.ethical_gate(text):
            return {"verdict": "REJECT", "reason": "Ethical gate failed.", "bifurcation": 0}

        base = self.rh.weight({
            "D_C": D.D_C, "D_S": D.D_S, "D_A": D.D_A, "D_T": D.D_T,
            "D_M": D.D_M, "D_TYPE": D_TYPE, "D_ATTR": D_ATTR
        })
        cat = spectral_categories({
            "D_C": D.D_C, "D_S": D.D_S, "D_A": D.D_A, "D_T": D.D_T,
            "D_M": D.D_M, "D_TYPE": D_TYPE, "D_ATTR": D_ATTR
        })
        gamma = gamma_from_categories(cat)
        Wp = {k: (v * gamma if isinstance(v, float) else v) for k, v in base.items()}
        W_total = (Wp["W_L"] + Wp["W_S"] + Wp["W_K"] + Wp["W_E"]) / 4.0

        if W_total < 0.40:
            return {"verdict": "REJECT", "reason": "Too weak.", "weights": Wp, "gamma": gamma, "categories": cat, "bifurcation": 0}
        if W_total < 0.70:
            return {"verdict": "HOLD", "reason": "Needs clarification.", "weights": Wp, "gamma": gamma, "categories": cat, "bifurcation": 0}
        return {"verdict": "PASS", "weights": Wp, "gamma": gamma, "categories": cat, "bifurcation": 1}

    def process(self, D: DataVector) -> Dict[str, Any]:
        a1 = self.first_analysis(D)
        if a1["verdict"] != "PASS":
            return {"OUT": a1, "report": "A1 pending user context or failed."}
        a2 = self.second_analysis(D, a1["D_TYPE"], a1["D_ATTR"])
        return {
            "OUT": a2,
            "report": {"REJECT": "Blocked by RULE/HEUR.", "HOLD": "Awaiting user input.", "PASS": "Logical pass."}[a2["verdict"]],
            "A1": a1,
        }

# ---------------------------
# Durable: TSM (SQLite)
# ---------------------------

class TSMWriterSQL:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self):
        return sqlite3.connect(str(self.db_path))

    def _init_schema(self):
        with self._connect() as conn:
            conn.execute("""
CREATE TABLE IF NOT EXISTS memories (
    memorise_id TEXT PRIMARY KEY,
    created_at  TEXT NOT NULL,
    D_id        TEXT NOT NULL,
    D_context   TEXT,
    D_sense     TEXT,
    D_associations TEXT,
    D_timestamp TEXT,
    D_meta      TEXT,
    D_type      TEXT,
    D_attr      TEXT,
    W_L REAL, W_S REAL, W_K REAL, W_E REAL, W_F INTEGER,
    rationale   TEXT,
    source      TEXT,
    tsm_ref     TEXT,
    wpm_ref     TEXT
);
""")
            conn.commit()

    def save(self, record: MemoriseD) -> str:
        W = record.weights or {}
        with self._connect() as conn:
            conn.execute(
                """
INSERT OR REPLACE INTO memories (
  memorise_id, created_at, D_id, D_context, D_sense, D_associations, D_timestamp, D_meta, D_type, D_attr,
  W_L, W_S, W_K, W_E, W_F, rationale, source, tsm_ref, wpm_ref
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""",
                (
                    record.memorise_id,
                    record.created_at,
                    record.D_id,
                    record.D_context,
                    str(record.D_sense),
                    json.dumps(record.D_associations, ensure_ascii=False),
                    record.D_timestamp,
                    json.dumps(record.D_meta, ensure_ascii=False),
                    record.D_type,
                    json.dumps(record.D_attr, ensure_ascii=False),
                    float(W.get("W_L", 0.0)),
                    float(W.get("W_S", 0.0)),
                    float(W.get("W_K", 0.0)),
                    float(W.get("W_E", 0.0)),
                    1 if W.get("W_F", True) else 0,
                    record.rationale,
                    record.source,
                    f"TSM:{record.memorise_id}",
                    None,
                ),
            )
            conn.commit()
        return f"TSM:{record.memorise_id}"

    def attach_wpm_ref(self, memorise_id: str, wpm_ref: str) -> None:
        with self._connect() as conn:
            conn.execute("UPDATE memories SET wpm_ref = ? WHERE memorise_id = ?", (wpm_ref, memorise_id))
            conn.commit()

    def read_meta(self, ref_id: str) -> Dict[str, Any]:
        if not ref_id.startswith("TSM:"):
            return {}
        mid = ref_id.split(":", 1)[1]
        with self._connect() as conn:
            cur = conn.execute(
                "SELECT memorise_id, created_at, D_context, D_type, W_L, W_S, W_K, W_E FROM memories WHERE memorise_id = ?",
                (mid,),
            )
            row = cur.fetchone()
            return {} if not row else {
                "ref": ref_id,
                "memorise_id": row[0],
                "created_at": row[1],
                "context": row[2],
                "type": row[3],
                "W_L": row[4],
                "W_S": row[5],
                "W_K": row[6],
                "W_E": row[7],
            }

# ---------------------------
# Durable: WPM (HDF5 with JSONL fallback)
# ---------------------------

class WPMWriterHDF5:
    def __init__(self, h5_path: Path):
        self.h5_path = Path(h5_path)
        self.h5_path.parent.mkdir(parents=True, exist_ok=True)
        self._jsonl_fallback_path = self.h5_path.with_suffix('.jsonl')
        self._use_hdf5 = self._detect_hdf5_support()

        if self._use_hdf5:
            import h5py
            with h5py.File(self.h5_path, "a") as h5:
                if "memories" not in h5:
                    h5.create_group("memories")
        else:
            self._jsonl_fallback_path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _detect_hdf5_support() -> bool:
        try:
            import h5py  # noqa: F401
        except Exception:
            return False
        return True

    def _record_payload(self, record: MemoriseD) -> Dict[str, Any]:
        return {
            "created_at": record.created_at,
            "D_id": record.D_id,
            "D_context": record.D_context,
            "D_sense": str(record.D_sense),
            "D_associations": record.D_associations,
            "D_timestamp": record.D_timestamp,
            "D_meta": record.D_meta,
            "D_type": record.D_type,
            "D_attr": record.D_attr,
            "weights": record.weights,
            "rationale": record.rationale,
            "source": record.source,
        }

    def _save_jsonl_fallback(
        self,
        record: MemoriseD,
        wave_arrays: Optional[Dict[str, Any]] = None,
        attrs: Optional[Dict[str, Any]] = None,
    ) -> str:
        payload = self._record_payload(record)
        payload["memorise_id"] = record.memorise_id
        payload["storage_mode"] = "jsonl_fallback"
        if wave_arrays:
            payload["wave_arrays"] = {
                name: {
                    "shape": list(getattr(arr, 'shape', [])),
                    "dtype": str(getattr(arr, 'dtype', type(arr).__name__)),
                }
                for name, arr in wave_arrays.items()
            }
        if attrs:
            payload["attrs"] = attrs
        with self._jsonl_fallback_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload, ensure_ascii=False) + "\n")
        return f"WPM:{record.memorise_id}"

    def save(self, record: MemoriseD) -> str:
        if not self._use_hdf5:
            return self._save_jsonl_fallback(record)
        import h5py
        with h5py.File(self.h5_path, "a") as h5:
            grp = h5["memories"].create_group(record.memorise_id) if record.memorise_id not in h5["memories"] else h5["memories"][record.memorise_id]
            def _set_key(name: str, val: Any):
                if name in grp:
                    del grp[name]
                grp.create_dataset(name, data=str(val))
            def _set_json(name: str, obj: Any):
                if name in grp:
                    del grp[name]
                grp.create_dataset(name, data=json.dumps(obj, ensure_ascii=False))
            for key, value in self._record_payload(record).items():
                if isinstance(value, (dict, list)):
                    _set_json(key, value)
                else:
                    _set_key(key, value)
        return f"WPM:{record.memorise_id}"

    def save_with_wave(
        self,
        record: MemoriseD,
        wave_arrays: Optional[Dict[str, "np.ndarray"]] = None,
        attrs: Optional[Dict[str, Any]] = None,
    ) -> str:
        if not self._use_hdf5:
            return self._save_jsonl_fallback(record, wave_arrays=wave_arrays, attrs=attrs)
        import h5py
        import numpy as np  # noqa
        with h5py.File(self.h5_path, "a") as h5:
            root = h5["memories"]
            grp = root.create_group(record.memorise_id) if record.memorise_id not in root else root[record.memorise_id]
            def _set_key(name: str, val: Any):
                if name in grp:
                    del grp[name]
                grp.create_dataset(name, data=str(val))
            def _set_json(name: str, obj: Any):
                if name in grp:
                    del grp[name]
                grp.create_dataset(name, data=json.dumps(obj, ensure_ascii=False))
            for key, value in self._record_payload(record).items():
                if isinstance(value, (dict, list)):
                    _set_json(key, value)
                else:
                    _set_key(key, value)

            if wave_arrays:
                waves = grp.create_group("waves") if "waves" not in grp else grp["waves"]
                for name, arr in wave_arrays.items():
                    if name in waves:
                        del waves[name]
                    waves.create_dataset(name, data=arr)
            if attrs:
                for k, v in attrs.items():
                    try:
                        grp.attrs[k] = v
                    except Exception:
                        grp.attrs[k] = str(v)
        return f"WPM:{record.memorise_id}"

# ---------------------------
# Unified Orchestrator
# ---------------------------

_SYSTEM_ROOT = Path(__file__).resolve().parents[3]


class BraidLedgerJSONL:
    """Persist braid-side memory traces next to durable memory backends.

    This is the file-level bifurcation point for braid memory: the braid runtime
    computes symbolic loop / scar information before storage, and this writer
    materializes the trace as a local JSONL ledger.
    """

    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, memorise_id: str, payload: Dict[str, Any]) -> str:
        entry = {
            "memorise_id": memorise_id,
            "created_at": dt.datetime.utcnow().isoformat(),
            **payload,
        }
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return f"BRAID:{memorise_id}"


class UnifiedMemoryOrchestrator:
    def __init__(
        self,
        cfg_dir: Path = _SYSTEM_ROOT / "configs",
        tsm_db: Path = _SYSTEM_ROOT / "CIEL_MEMORY_SYSTEM" / "TSM" / "ledger" / "memory_ledger.db",
        wpm_h5: Path = _SYSTEM_ROOT / "CIEL_MEMORY_SYSTEM" / "WPM" / "wave_snapshots" / "wave_archive.h5",
        braid_ledger: Path = _SYSTEM_ROOT / "CIEL_MEMORY_SYSTEM" / "BRAID" / "ledger" / "braid_ledger.jsonl",
    ):
        # Ensure local dirs exist
        cfg_dir.mkdir(parents=True, exist_ok=True)
        tsm_db.parent.mkdir(parents=True, exist_ok=True)
        wpm_h5.parent.mkdir(parents=True, exist_ok=True)
        braid_ledger.parent.mkdir(parents=True, exist_ok=True)

        # Write defaults if missing
        self._ensure_default_config(cfg_dir / "rules_immutable.json", DEFAULT_RULES_IMMUTABLE)
        self._ensure_default_config(cfg_dir / "heuristics_user.json", DEFAULT_HEURISTICS_USER)
        self._ensure_default_config(cfg_dir / "heuristics_self.json", DEFAULT_HEURISTICS_SELF)

        self.tsm = TSMWriterSQL(tsm_db)
        self.wpm = WPMWriterHDF5(wpm_h5)
        self.braid_ledger = BraidLedgerJSONL(braid_ledger)
        self.tmp = TMPKernel(cfg_dir)

        self._braid_adapter = None
        self._last_braid_trace: Optional[Dict[str, Any]] = None
        if KernelAdapter is not None and make_default_runtime is not None:
            try:
                self._braid_adapter = KernelAdapter(make_default_runtime())
            except Exception:
                self._braid_adapter = None
        if self._braid_adapter is None:
            try:
                omega_root = str(_SYSTEM_ROOT / "ciel_omega")
                if omega_root not in sys.path:
                    sys.path.insert(0, omega_root)
                from core.braid.adapter import KernelAdapter as _KernelAdapter  # type: ignore
                from core.braid.defaults import make_default_runtime as _make_default_runtime  # type: ignore
                self._braid_adapter = _KernelAdapter(_make_default_runtime())
            except Exception:
                self._braid_adapter = None

        self._tmp_reports: List[Dict[str, Any]] = []
        self._verification_queue: List[Dict[str, Any]] = []
        self.allow_system_force_save = True
        self.allow_user_force_save = True

    def _ensure_default_config(self, path: Path, obj: Dict[str, Any]) -> None:
        if not path.exists():
            path.write_text(json.dumps(obj, indent=2), encoding="utf-8")

    def _capture_braid_trace(self, D: DataVector) -> Optional[Dict[str, Any]]:
        if self._braid_adapter is None:
            self._last_braid_trace = None
            return None
        try:
            loop = self._braid_adapter.submit_prompt(str(D.D_S), context={"context": D.D_C, "meta": D.D_M})
            snapshot = self._braid_adapter.step(max_loops=1)
            trace = {
                "loop_id": loop.loop_id,
                "coherence": float(snapshot.get("coherence", 0.0)),
                "avg_contradiction": float(snapshot.get("avg_contradiction", 0.0)),
                "E": float(snapshot.get("E", 0.0)),
                "scar_residual": float(snapshot.get("scar_residual", 0.0)),
                "scar_count": int(snapshot.get("scar_count", 0)),
                "executed": snapshot.get("executed", []),
            }
            self._last_braid_trace = trace
            return trace
        except Exception as exc:
            self._last_braid_trace = {"error": str(exc)}
            return self._last_braid_trace

    @staticmethod
    def _merge_braid_meta(base_meta: Dict[str, Any], braid_trace: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        merged = dict(base_meta or {})
        if braid_trace is not None:
            merged["braid_trace"] = braid_trace
        return merged

    def capture(self, context: str, sense: Any, associations=None, timestamp=None, meta=None) -> DataVector:
        D = DataVector(context=context, sense=sense, associations=associations, timestamp=timestamp, meta=meta)
        self._capture_braid_trace(D)
        D.D_M = self._merge_braid_meta(D.D_M, self._last_braid_trace)
        return D

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

    def _make_memorised(
        self, D: DataVector, a1: Dict[str, Any], a2: Dict[str, Any], rationale: str, source: str = "TMP"
    ) -> MemoriseD:
        return MemoriseD(
            memorise_id=str(uuid.uuid4()),
            created_at=dt.datetime.utcnow().isoformat(),
            D_id=D.id,
            D_context=D.D_C,
            D_sense=D.D_S,
            D_associations=D.D_A,
            D_timestamp=D.D_T,
            D_meta=D.D_M,
            D_type=a1.get("D_TYPE", "unknown"),
            D_attr=a1.get("D_ATTR", {}),
            weights=a2.get("weights", {}),
            rationale=rationale,
            source=source,
        )

    def _save_dual(
        self,
        mem: MemoriseD,
        wave_arrays: Optional[Dict[str, "np.ndarray"]] = None,
        wave_attrs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, str]:
        braid_trace = None
        if isinstance(mem.D_meta, dict):
            braid_trace = mem.D_meta.get("braid_trace")

        tsm_ref = self.tsm.save(mem)

        merged_wave_attrs = dict(wave_attrs or {})
        if braid_trace is not None:
            merged_wave_attrs.setdefault("braid_loop_id", braid_trace.get("loop_id"))
            merged_wave_attrs.setdefault("braid_coherence", braid_trace.get("coherence"))
            merged_wave_attrs.setdefault("braid_scar_residual", braid_trace.get("scar_residual"))

        if wave_arrays or merged_wave_attrs:
            wpm_ref = self.wpm.save_with_wave(mem, wave_arrays=wave_arrays, attrs=merged_wave_attrs)
        else:
            wpm_ref = self.wpm.save(mem)
        self.tsm.attach_wpm_ref(mem.memorise_id, wpm_ref)

        braid_payload = {
            "context": mem.D_context,
            "source": mem.source,
            "rationale": mem.rationale,
            "trace": braid_trace or {},
            "wpm_ref": wpm_ref,
            "tsm_ref": tsm_ref,
        }
        braid_ref = self.braid_ledger.append(mem.memorise_id, braid_payload)
        return {
            "tsm_ref": tsm_ref,
            "wpm_ref": wpm_ref,
            "braid_ref": braid_ref,
            "memorise_id": mem.memorise_id,
        }

    def promote_if_bifurcated(
        self,
        D: DataVector,
        tmp_out: Dict[str, Any],
        wave_arrays: Optional[Dict[str, "np.ndarray"]] = None,
        wave_attrs: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, str]]:
        a2, a1 = tmp_out["OUT"], tmp_out.get("A1", {})
        if a2.get("verdict") == "PASS" and a2.get("bifurcation") == 1:
            mem = self._make_memorised(D, a1, a2, rationale="B=1 collapse from TMP.")
            return self._save_dual(mem, wave_arrays=wave_arrays, wave_attrs=wave_attrs)
        return None

    def user_force_save(
        self,
        D: DataVector,
        tmp_out: Dict[str, Any],
        reason: str,
        wave_arrays: Optional[Dict[str, "np.ndarray"]] = None,
        wave_attrs: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, str]]:
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
            r for r in self._tmp_reports if r["requires_user_verification"] and not r["verified_by_user"]
        ]
        return {"kept": kept, "purged": purged, "pending_verifications": len(self._verification_queue)}

# ---------------------------
# Kernel wave adapter
# ---------------------------

def capture_wave(amplitude, phase=None, attrs: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
    """
    Plug-in adapter for external kernels:
      - amplitude: np.ndarray (float32 recommended)
      - phase: optional np.ndarray
      - attrs: dict of metadata (grid, units, etc.)
    Saves via USER override to ensure explicit provenance.
    """
    try:
        import numpy as np  # noqa
    except Exception:
        raise RuntimeError("NumPy required to pass arrays to wave archive.")

    orch = UnifiedMemoryOrchestrator()
    D = orch.capture(context="kernel-wave", sense="wave snapshot", meta={"trusted_source": True})
    out = orch.run_tmp(D)
    wave = {"amplitude": amplitude}
    if phase is not None:
        wave["phase"] = phase
    refs = orch.user_force_save(D, out, reason="kernel_adapter", wave_arrays=wave, wave_attrs=attrs or {})
    if not refs:
        raise RuntimeError("Wave save failed (no refs).")
    return refs

# ---------------------------
# CLI
# ---------------------------

def _cli_status(args) -> int:
    print("[CIEL-Memory] status OK")
    print("DB:", (_SYSTEM_ROOT / "CIEL_MEMORY_SYSTEM" / "TSM" / "ledger" / "memory_ledger.db").resolve())
    print("H5:", (_SYSTEM_ROOT / "CIEL_MEMORY_SYSTEM" / "WPM" / "wave_snapshots" / "wave_archive.h5").resolve())
    return 0

def _cli_run(args) -> int:
    orch = UnifiedMemoryOrchestrator()
    D = orch.capture(context=args.context, sense=args.sense, meta={"novelty_hint": args.novelty})
    out = orch.run_tmp(D)
    print("TMP OUT:", json.dumps(out["OUT"], indent=2, ensure_ascii=False))
    if args.promote:
        refs = orch.promote_if_bifurcated(D, out)
        if not refs and args.override:
            refs = orch.user_force_save(D, out, reason="cli-override")
        print("Durable:", refs)
    return 0

def _cli_verify(args) -> int:
    orch = UnifiedMemoryOrchestrator()
    stats = orch.daily_maintenance()
    print("Verification queue stats:", stats)
    return 0

def _cli_backup(args) -> int:
    target = Path(args.output or "ciel_memory_backup.zip")
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
        for base in [_SYSTEM_ROOT / "CIEL_MEMORY_SYSTEM", _SYSTEM_ROOT / "configs"]:
            for root, _, files in os.walk(base):
                for f in files:
                    p = Path(root) / f
                    z.write(p, p.relative_to(_SYSTEM_ROOT).as_posix())
    sha = hashlib.sha256(target.read_bytes()).hexdigest()
    print("Backup:", target, "SHA256:", sha)
    return 0

def _cli_export(args) -> int:
    out = Path(args.output or "export")
    out.mkdir(parents=True, exist_ok=True)
    src_db = _SYSTEM_ROOT / "CIEL_MEMORY_SYSTEM" / "TSM" / "ledger" / "memory_ledger.db"
    if src_db.exists():
        (out / "memory_ledger.db").write_bytes(src_db.read_bytes())
    (out / "README.txt").write_text("Export bundle for CIEL-Memory.\n", encoding="utf-8")
    print("Export ready at:", out.resolve())
    return 0

def _cli_wavesave(args) -> int:
    try:
        import numpy as np
    except Exception:
        print("NumPy required for wavesave demo. pip install numpy", file=sys.stderr)
        return 2
    orch = UnifiedMemoryOrchestrator()
    D = orch.capture(context="wave", sense="wave snapshot demo", meta={"trusted_source": True})
    out = orch.run_tmp(D)
    amp = (np.random.rand(64, 64)).astype("float32")
    ph = (np.random.rand(64, 64)).astype("float32")
    refs = orch.user_force_save(D, out, reason="wavesave", wave_arrays={"amplitude": amp, "phase": ph}, wave_attrs={"grid": "64x64"})
    print("Wave saved:", refs)
    return 0

def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="cielmem", description="CIEL-Memory Monolith CLI")
    sub = p.add_subparsers(dest="cmd")

    s = sub.add_parser("status", help="Show status and local paths"); s.set_defaults(func=_cli_status)

    r = sub.add_parser("run", help="Run TMP and optionally promote/override")
    r.add_argument("--context", required=True)
    r.add_argument("--sense", required=True)
    r.add_argument("--novelty", action="store_true")
    r.add_argument("--promote", action="store_true")
    r.add_argument("--override", action="store_true")
    r.set_defaults(func=_cli_run)

    v = sub.add_parser("verify", help="Daily maintenance / verification")
    v.set_defaults(func=_cli_verify)

    b = sub.add_parser("backup", help="Create ZIP backup + checksum")
    b.add_argument("-o", "--output")
    b.set_defaults(func=_cli_backup)

    e = sub.add_parser("export", help="Export durable memory bundle")
    e.add_argument("-o", "--output")
    e.set_defaults(func=_cli_export)

    w = sub.add_parser("wavesave", help="Demo: save wave arrays (requires numpy + h5py)")
    w.set_defaults(func=_cli_wavesave)

    args = p.parse_args(argv)
    if not getattr(args, "cmd", None):
        p.print_help()
        return 1
    return int(args.func(args))

if __name__ == "__main__":
    sys.exit(main())