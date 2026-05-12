from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime, timezone
import json


@dataclass(frozen=True)
class StorageResult:
    preferred_format: str
    fallback_format: str
    used_fallback: bool
    target_path: str
    result_path: str
    error_type: Optional[str]
    error_message: Optional[str]
    timestamp_utc: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(v) for v in value]
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            return str(value)
    return value


def write_json_fallback(data: Any, json_path: str | Path, metadata: Optional[Dict[str, Any]] = None) -> StorageResult:
    path = Path(json_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "metadata": metadata or {},
        "data": _json_safe(data),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return StorageResult(
        preferred_format=str((metadata or {}).get("preferred_format", "json")),
        fallback_format="json",
        used_fallback=bool((metadata or {}).get("used_fallback", False)),
        target_path=str((metadata or {}).get("target_path", path)),
        result_path=str(path),
        error_type=(metadata or {}).get("error_type"),
        error_message=(metadata or {}).get("error_message"),
        timestamp_utc=(metadata or {}).get("timestamp_utc", _now()),
    )


def _write_value_hdf5(group: Any, key: str, value: Any) -> None:
    if isinstance(value, dict):
        sub = group.create_group(str(key))
        for k, v in value.items():
            _write_value_hdf5(sub, str(k), v)
    elif isinstance(value, (list, tuple)):
        # Store list as JSON string to avoid dtype complexity in seed mode.
        group.create_dataset(str(key), data=json.dumps(_json_safe(value), ensure_ascii=False))
    elif value is None:
        group.create_dataset(str(key), data="null")
    elif isinstance(value, (int, float, bool, str)):
        group.create_dataset(str(key), data=value)
    else:
        group.create_dataset(str(key), data=json.dumps(_json_safe(value), ensure_ascii=False))


def write_hdf5_or_json(
    data: Any,
    h5_path: str | Path,
    json_path: str | Path | None = None,
    simulate_failure: bool = False,
) -> StorageResult:
    h5 = Path(h5_path)
    fallback = Path(json_path) if json_path is not None else h5.with_suffix(h5.suffix + ".fallback.json")
    timestamp = _now()
    try:
        if simulate_failure:
            raise RuntimeError("simulated HDF5 failure")
        import h5py  # type: ignore
        h5.parent.mkdir(parents=True, exist_ok=True)
        with h5py.File(h5, "w") as f:
            _write_value_hdf5(f, "payload", data)
            f.attrs["created_by"] = "CIEL-LNS storage_fallback.write_hdf5_or_json"
            f.attrs["schema_version"] = "1.4"
        return StorageResult("hdf5", "json", False, str(h5), str(h5), None, None, timestamp)
    except Exception as exc:
        metadata = {
            "preferred_format": "hdf5",
            "fallback_format": "json",
            "used_fallback": True,
            "target_path": str(h5),
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "timestamp_utc": timestamp,
        }
        return write_json_fallback(data, fallback, metadata)


def write_report(result: StorageResult, report_path: str | Path) -> None:
    path = Path(report_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
