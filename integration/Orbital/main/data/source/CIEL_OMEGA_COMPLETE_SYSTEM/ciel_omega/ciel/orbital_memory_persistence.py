from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from ciel_omega.memory import HolonomicMemoryOrchestrator


def _system_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_orbital_memory_store() -> Path:
    root = _system_root() / "CIEL_MEMORY_SYSTEM" / "ORBITAL_MEMORY"
    root.mkdir(parents=True, exist_ok=True)
    return root / "sector_events.ndjson"


def _json_default(value: Any) -> Any:
    if hasattr(value, "tolist"):
        return value.tolist()
    if hasattr(value, "__dict__"):
        return value.__dict__
    return str(value)


def append_sector_event(path: Path, event: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False, default=_json_default) + "\n")


def iter_sector_events(path: Path) -> Iterable[Dict[str, Any]]:
    if not path.exists():
        return []
    events: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except Exception:
                continue
            if isinstance(payload, dict) and payload.get("content"):
                events.append(payload)
    return events


def restore_sector_memory(orchestrator: HolonomicMemoryOrchestrator, path: Optional[Path] = None, *, max_events: Optional[int] = None) -> int:
    store = path or default_orbital_memory_store()
    events = list(iter_sector_events(store))
    if max_events is not None:
        events = events[-int(max_events):]
    restored = 0
    for event in events:
        content = event.get("content", "")
        metadata = {k: v for k, v in event.items() if k != "content"}
        orchestrator.process_input(content, metadata=metadata)
        restored += 1
    return restored


class PersistentOrbitalSectorMemory:
    def __init__(self, orchestrator: Optional[HolonomicMemoryOrchestrator] = None, store_path: Optional[Path] = None, *, replay_limit: Optional[int] = 256) -> None:
        self.orchestrator = orchestrator or HolonomicMemoryOrchestrator()
        self.store_path = store_path or default_orbital_memory_store()
        self.replay_limit = replay_limit
        self.restored_events = restore_sector_memory(self.orchestrator, self.store_path, max_events=replay_limit)

    def record(self, event: Dict[str, Any]) -> Dict[str, Any]:
        content = event.get("content", "")
        metadata = {k: v for k, v in event.items() if k != "content"}
        cycle = self.orchestrator.process_input(content, metadata=metadata)
        append_sector_event(self.store_path, event)
        retrieval = self.orchestrator.retrieve(content, top_k=3)
        snapshot = self.orchestrator.snapshot()
        return {
            "event": event,
            "cycle": cycle,
            "snapshot": snapshot,
            "retrieval": retrieval,
            "store_path": str(self.store_path),
            "restored_events": self.restored_events,
        }

    def retrieve(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        return self.orchestrator.retrieve(query, top_k=top_k)

    def snapshot(self) -> Any:
        return self.orchestrator.snapshot()
