from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.ciel_sot_agent.cielingo_bridge import build_lingo_frame, render_lingo_summary


def _baseline_payload(prompt: str) -> Dict[str, Any]:
    text = prompt.strip()
    return {
        "text": text,
        "length": len(text),
        "deictic_count": 0,
        "unresolved_count": 0,
        "projection_confidence": 0.0,
    }


def _enhanced_payload(prompt: str, *, language: str | None = None) -> Dict[str, Any]:
    frame = build_lingo_frame(prompt, ciel_state={"language": language}, language=language)
    summary = render_lingo_summary(frame)
    text = f"{prompt.strip()} || {summary}" if prompt.strip() else summary
    return {
        "text": text,
        "length": len(text),
        "deictic_count": int(frame.get("deictic_frame", {}).get("anchor_count", 0) or 0),
        "unresolved_count": len(frame.get("unresolved", []) or []),
        "projection_confidence": float(frame.get("projection_confidence", 0.0)),
        "composition_valid": bool(frame.get("composition_valid", False)),
        "noema_confidence": float((frame.get("noema_route") or {}).get("confidence", 0.0) or 0.0),
        "summary": summary,
    }


def run_ablation_benchmark(samples: Iterable[str], *, language: str | None = None) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    for sample in samples:
        baseline = _baseline_payload(sample)
        enhanced = _enhanced_payload(sample, language=language)
        rows.append(
            {
                "prompt": sample,
                "baseline": baseline,
                "enhanced": enhanced,
                "delta": {
                    "length": enhanced["length"] - baseline["length"],
                    "deictic_count": enhanced["deictic_count"] - baseline["deictic_count"],
                    "unresolved_count": enhanced["unresolved_count"] - baseline["unresolved_count"],
                    "projection_confidence": round(enhanced["projection_confidence"] - baseline["projection_confidence"], 4),
                },
            }
        )

    mean_length_delta = 0.0
    mean_projection_confidence = 0.0
    if rows:
        mean_length_delta = sum(row["delta"]["length"] for row in rows) / len(rows)
        mean_projection_confidence = sum(row["enhanced"]["projection_confidence"] for row in rows) / len(rows)

    return {
        "sample_count": len(rows),
        "mean_length_delta": round(mean_length_delta, 2),
        "mean_projection_confidence": round(mean_projection_confidence, 4),
        "rows": rows,
    }


def _load_samples(path: Path | None) -> List[str]:
    if path is None:
        return [
            "Here now we ask about memory and truth.",
            "Spotkajmy się gdzieś kiedyś.",
            "The glass contains water and the speaker is here now.",
        ]
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return [str(item) for item in data if str(item).strip()]
    if isinstance(data, dict) and isinstance(data.get("samples"), list):
        return [str(item) for item in data["samples"] if str(item).strip()]
    raise ValueError("Unsupported sample file format; expected JSON list or {samples: [...]} object.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a CIELingo CQCL ablation benchmark.")
    parser.add_argument("--samples", type=Path, default=None, help="Optional JSON file with prompt samples.")
    parser.add_argument("--language", default=None, help="Optional language code passed to CIELingo.")
    parser.add_argument("--output", type=Path, default=None, help="Optional JSON report path.")
    args = parser.parse_args()

    report = run_ablation_benchmark(_load_samples(args.samples), language=args.language)
    payload = json.dumps(report, indent=2, ensure_ascii=False)

    if args.output is not None:
        args.output.write_text(payload, encoding="utf-8")
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
