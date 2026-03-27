"""CIEL/Ω Memory — WPM durable store (HDF5 wave archive).

Split from: unified_memory.py (lines 394–472)
Requires h5py (optional dependency).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from ciel_omega.memory.monolith.data_types import MemoriseD


class WPMWriterHDF5:
    """Wave-Persistent Memory — HDF5 backend for wave snapshots."""

    def __init__(self, h5_path: Path):
        try:
            import h5py  # noqa
        except ImportError:
            raise RuntimeError("h5py is required for WPMWriterHDF5. pip install h5py")
        self.h5_path = Path(h5_path)
        self.h5_path.parent.mkdir(parents=True, exist_ok=True)
        import h5py
        with h5py.File(self.h5_path, "a") as h5:
            if "memories" not in h5:
                h5.create_group("memories")

    def _write_fields(self, grp, record: MemoriseD):
        """Write common metadata fields into an HDF5 group."""
        def _set(name, val):
            if name in grp:
                del grp[name]
            grp.create_dataset(name, data=str(val))

        def _set_json(name, obj):
            if name in grp:
                del grp[name]
            grp.create_dataset(name, data=json.dumps(obj, ensure_ascii=False))

        _set("created_at", record.created_at)
        _set("D_id", record.D_id)
        _set("D_context", record.D_context)
        _set("D_sense", str(record.D_sense))
        _set_json("D_associations", record.D_associations)
        _set("D_timestamp", record.D_timestamp)
        _set_json("D_meta", record.D_meta)
        _set("D_type", record.D_type)
        _set_json("D_attr", record.D_attr)
        _set_json("weights", record.weights)
        _set("rationale", record.rationale)
        _set("source", record.source)

    def save(self, record: MemoriseD) -> str:
        import h5py
        with h5py.File(self.h5_path, "a") as h5:
            root = h5["memories"]
            grp = root.create_group(record.memorise_id) if record.memorise_id not in root else root[record.memorise_id]
            self._write_fields(grp, record)
        return f"WPM:{record.memorise_id}"

    def save_with_wave(
        self,
        record: MemoriseD,
        wave_arrays: Optional[Dict[str, Any]] = None,
        attrs: Optional[Dict[str, Any]] = None,
    ) -> str:
        import h5py
        with h5py.File(self.h5_path, "a") as h5:
            root = h5["memories"]
            grp = root.create_group(record.memorise_id) if record.memorise_id not in root else root[record.memorise_id]
            self._write_fields(grp, record)
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
