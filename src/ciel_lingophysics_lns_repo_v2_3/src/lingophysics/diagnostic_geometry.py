from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None


def load_json(path: str | Path) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_yaml(path: str | Path) -> Dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML is required for YAML diagnostic configs.")
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def load_reconstruction_costs(path: str | Path) -> List[Dict[str, str]]:
    with Path(path).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def cost_lookup(rows: List[Dict[str, str]], source: str, target: str) -> float:
    for row in rows:
        if row.get("source_language") == source and row.get("target_language") == target:
            return float(row.get("grammar_gauge_distance", 0.0))
    raise KeyError(f"No reconstruction cost for {source}->{target}")


def max_cost(rows: List[Dict[str, str]]) -> float:
    return max(float(r.get("grammar_gauge_distance", 0.0)) for r in rows) if rows else 0.0


def load_conflict_registry(path: str | Path) -> Dict[str, Any]:
    return load_json(path)


def issue_counts_by_severity(registry: Dict[str, Any]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for issue in registry.get("issues", []):
        sev = issue.get("severity", "UNKNOWN")
        counts[sev] = counts.get(sev, 0) + 1
    return counts


def load_graph(path: str | Path) -> Dict[str, Any]:
    return load_json(path)


def graph_counts(graph: Dict[str, Any]) -> Tuple[int, int]:
    return len(graph.get("nodes", [])), len(graph.get("edges", []))


def diagnostic_pass(summary: Dict[str, Any], registry: Dict[str, Any]) -> bool:
    """Seed-level diagnostic pass: no BLOCKER severity and non-empty card/graph counts."""
    severities = issue_counts_by_severity(registry)
    return summary.get("cards_total", 0) > 0 and severities.get("BLOCKER", 0) == 0
