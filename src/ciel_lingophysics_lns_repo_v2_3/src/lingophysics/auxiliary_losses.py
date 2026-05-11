from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import json

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None


def load_auxiliary_tasks(path: str | Path) -> Dict[str, Any]:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if p.suffix.lower() in {".yaml", ".yml"}:
        if yaml is None:
            raise RuntimeError("PyYAML is required for YAML task files.")
        return yaml.safe_load(text)
    return json.loads(text)


def total_auxiliary_weight(tasks: Dict[str, Any]) -> float:
    return round(sum(float(t.get("weight", 0.0)) for t in tasks.get("tasks", [])), 6)


def weighted_total_loss(language_model_loss: float, task_losses: Dict[str, float], tasks: Dict[str, Any]) -> float:
    total = float(language_model_loss)
    for task in tasks.get("tasks", []):
        tid = task["id"]
        total += float(task.get("weight", 0.0)) * float(task_losses.get(tid, 0.0))
    return round(total, 6)


def missing_task_losses(task_losses: Dict[str, float], tasks: Dict[str, Any]) -> list[str]:
    return [t["id"] for t in tasks.get("tasks", []) if t["id"] not in task_losses]
