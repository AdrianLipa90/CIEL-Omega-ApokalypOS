from __future__ import annotations

from typing import Any, Dict, List


def _pluck_text(item: Any) -> str:
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        for key in ("content", "text", "canonical_text", "canonical_action", "summary"):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        if "result" in item and isinstance(item["result"], dict):
            return _pluck_text(item["result"])
    return ""


def summarize_sector_retrieval(ciel_state: Dict[str, Any], *, max_items_per_channel: int = 2) -> Dict[str, List[str]]:
    sector_memory = ciel_state.get("sector_memory") if isinstance(ciel_state.get("sector_memory"), dict) else {}
    retrieval = {}
    governed = sector_memory.get("governed_retrieval") if isinstance(sector_memory.get("governed_retrieval"), dict) else {}
    summary: Dict[str, List[str]] = {}

    ranked = governed.get("ranked") if isinstance(governed.get("ranked"), list) else []
    ranked_lines: List[str] = []
    for row in ranked[: max(1, max_items_per_channel * 2)]:
        if not isinstance(row, dict):
            continue
        txt = _pluck_text(row)
        if not txt:
            txt = str(row.get("text", "") or "").strip()
        if not txt:
            continue
        channel = str(row.get("channel", "memory"))
        hq = row.get("holonomy_quality")
        pa = row.get("phase_alignment")
        tags: List[str] = [channel]
        if isinstance(hq, (int, float)):
            tags.append(f"hq={float(hq):.2f}")
        if isinstance(pa, (int, float)):
            tags.append(f"pa={float(pa):.2f}")
        ranked_lines.append(f"[{', '.join(tags)}] {txt[:200]}")
    if ranked_lines:
        summary["ranked"] = ranked_lines

    if isinstance(governed.get("by_channel"), dict):
        retrieval = governed.get("by_channel")
    elif isinstance(sector_memory.get("retrieval"), dict):
        retrieval = sector_memory.get("retrieval")
    for channel, items in retrieval.items():
        texts: List[str] = []
        if isinstance(items, list):
            for item in items[:max_items_per_channel]:
                txt = _pluck_text(item)
                if txt:
                    texts.append(txt[:200])
        elif isinstance(items, dict):
            txt = _pluck_text(items)
            if txt:
                texts.append(txt[:200])
        if texts:
            summary[str(channel)] = texts
    return summary
