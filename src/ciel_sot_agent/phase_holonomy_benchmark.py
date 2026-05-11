from __future__ import annotations

"""Phase-holonomy Monte Carlo benchmark for CIELingo frames.

Measures how stable the phase projection / tau bridge remain under prompt
perturbations that preserve or lightly disturb deictic anchors.
"""

from dataclasses import dataclass
import math
import random
import re
from typing import Any, Iterable

from .cielingo_bridge import build_lingo_frame

_SECTOR_LABELS = ("proximal", "liminal", "distal", "open")
_SECTOR_CENTERS = (0.0, math.pi / 2.0, math.pi, 3.0 * math.pi / 2.0)
_DEICTIC_CANON = {
    "here": "proximal",
    "now": "proximal",
    "this": "proximal",
    "there": "distal",
    "then": "distal",
    "that": "distal",
    "somewhere": "liminal",
    "sometime": "liminal",
    "somehow": "liminal",
    "anywhere": "open",
    "anytime": "open",
    "never": "distal",
    "tu": "proximal",
    "tutaj": "proximal",
    "tam": "distal",
    "teraz": "proximal",
    "wtedy": "distal",
}
_PERTURB_FILLERS = ("briefly", "carefully", "quietly", "again", "later", "locally")
_DEFAULT_CASES = [
    {
        "name": "tolkien_propagation",
        "prompt": (
            "Here Tolkien wrote a text that later carried a whole language there "
            "into many minds, and now readers still extend it."
        ),
        "language": "en",
    },
    {
        "name": "ab_phase",
        "prompt": (
            "Now a phase can carry cold information there even when the field "
            "stays quiet and the particle path looks unchanged."
        ),
        "language": "en",
    },
    {
        "name": "mobius_tau",
        "prompt": (
            "Here the path bends, then returns there with a twist, while tau and "
            "lambda keep the drift on a closed relation."
        ),
        "language": "en",
    },
]


@dataclass(frozen=True)
class PhaseStudy:
    name: str
    prompt: str
    language: str | None = None


def _wrap_phase(angle: float) -> float:
    return float(angle % (2.0 * math.pi))


def _angular_distance(a: float, b: float) -> float:
    diff = (a - b + math.pi) % (2.0 * math.pi) - math.pi
    return float(abs(diff))


def _sector_label(angle: float) -> str:
    angle = _wrap_phase(angle)
    nearest = min(range(len(_SECTOR_CENTERS)), key=lambda i: _angular_distance(angle, _SECTOR_CENTERS[i]))
    return _SECTOR_LABELS[nearest]


def _sector_distance(a: float, b: float) -> float:
    return float(min(_angular_distance(a, b), 2.0 * math.pi - _angular_distance(a, b)))


def _token_key(token: str) -> str:
    return re.sub(r"[^a-ząćęłńóśźż]+", "", token.lower())


def _perturb_prompt(prompt: str, rng: random.Random, *, strength: float) -> str:
    tokens = prompt.split()
    if not tokens:
        return prompt

    out = list(tokens)
    deictic_idx = {i for i, tok in enumerate(out) if _token_key(tok) in _DEICTIC_CANON}
    mutable_idx = [i for i in range(len(out)) if i not in deictic_idx]

    # Insert lightweight filler words away from deictic anchors.
    if mutable_idx and rng.random() < strength:
        idx = rng.choice(mutable_idx)
        out.insert(idx, rng.choice(_PERTURB_FILLERS))

    # Remove one non-anchor token with small probability.
    mutable_now = [i for i, tok in enumerate(out) if _token_key(tok) not in _DEICTIC_CANON]
    if len(mutable_now) > 4 and rng.random() < strength * 0.6:
        del out[rng.choice(mutable_now)]

    # Shuffle a middle slice, leaving the anchors in place.
    if len(out) > 6 and rng.random() < strength * 0.5:
        indices = [i for i, tok in enumerate(out) if _token_key(tok) not in _DEICTIC_CANON]
        if len(indices) >= 3:
            shuffled = [out[i] for i in indices]
            rng.shuffle(shuffled)
            for idx, tok in zip(indices, shuffled):
                out[idx] = tok

    # Rarely swap a deictic for an equivalent same-sector anchor.
    if deictic_idx and rng.random() < strength * 0.25:
        idx = rng.choice(sorted(deictic_idx))
        sector = _DEICTIC_CANON.get(_token_key(out[idx]), "proximal")
        candidates = [tok for tok, sec in _DEICTIC_CANON.items() if sec == sector]
        if candidates:
            out[idx] = rng.choice(candidates)

    return " ".join(out)


def _case_rows(cases: Iterable[dict[str, Any] | PhaseStudy]) -> list[PhaseStudy]:
    rows: list[PhaseStudy] = []
    for case in cases:
        if isinstance(case, PhaseStudy):
            rows.append(case)
            continue
        name = str(case.get("name") or "case").strip() or "case"
        prompt = str(case.get("prompt") or "").strip()
        if not prompt:
            continue
        language = case.get("language")
        rows.append(PhaseStudy(name=name, prompt=prompt, language=str(language) if language else None))
    return rows


def _build_case_frame(study: PhaseStudy) -> dict[str, Any]:
    return build_lingo_frame(
        study.prompt,
        ciel_state={"language": study.language},
        language=study.language,
    )


def run_phase_holonomy_benchmark(
    cases: Iterable[dict[str, Any] | PhaseStudy] | None = None,
    *,
    n_trials: int = 64,
    strength: float = 0.12,
    seed: int = 42,
) -> dict[str, Any]:
    studies = _case_rows(cases or _DEFAULT_CASES)
    rng = random.Random(seed)
    case_reports: list[dict[str, Any]] = []
    all_fits = 0
    all_trials = 0
    all_phase_drifts: list[float] = []
    all_tau_gradients: list[float] = []
    all_imaginal_drive: list[float] = []

    for study in studies:
        baseline = _build_case_frame(study)
        baseline_phase = float((baseline.get("phase_projection") or {}).get("target_phase", 0.0) or 0.0)
        baseline_sector = _sector_label(baseline_phase)
        baseline_confidence = float((baseline.get("phase_projection") or {}).get("phase_confidence", 0.0) or 0.0)

        samples: list[dict[str, Any]] = []
        fit_count = 0
        phase_drifts: list[float] = []
        tau_gradients: list[float] = []
        imaginal_drive: list[float] = []

        for trial in range(n_trials):
            noisy_prompt = _perturb_prompt(study.prompt, rng, strength=strength)
            noisy_frame = build_lingo_frame(
                noisy_prompt,
                ciel_state={"language": study.language},
                language=study.language,
            )
            phase_projection = noisy_frame.get("phase_projection") if isinstance(noisy_frame.get("phase_projection"), dict) else {}
            tau_bridge = noisy_frame.get("tau_bridge") if isinstance(noisy_frame.get("tau_bridge"), dict) else {}
            phase = float(phase_projection.get("target_phase", 0.0) or 0.0)
            sector = _sector_label(phase)
            drift = _sector_distance(phase, baseline_phase)
            sector_fit = sector == baseline_sector
            fit = sector_fit and drift <= (math.pi / 4.0)

            fit_count += int(fit)
            all_fits += int(fit)
            all_trials += 1
            phase_drifts.append(drift)
            all_phase_drifts.append(drift)

            tau_g = float(tau_bridge.get("tau_gradient_mean", 0.0) or 0.0)
            imaginal = float(tau_bridge.get("imaginal_drive", 0.0) or 0.0)
            tau_gradients.append(tau_g)
            imaginal_drive.append(imaginal)
            all_tau_gradients.append(tau_g)
            all_imaginal_drive.append(imaginal)

            samples.append(
                {
                    "trial": trial,
                    "prompt": noisy_prompt,
                    "sector": sector,
                    "phase": round(phase, 6),
                    "drift": round(drift, 6),
                    "fit": fit,
                    "phase_confidence": round(float(phase_projection.get("phase_confidence", 0.0) or 0.0), 4),
                    "tau_gradient_mean": round(tau_g, 6),
                    "imaginal_drive": round(imaginal, 4),
                }
            )

        case_report = {
            "name": study.name,
            "prompt": study.prompt,
            "baseline": {
                "sector": baseline_sector,
                "phase": round(baseline_phase, 6),
                "phase_confidence": round(baseline_confidence, 4),
            },
            "n_trials": n_trials,
            "strength": round(strength, 4),
            "fit_rate": round(fit_count / max(1, n_trials), 4),
            "mean_phase_drift": round(sum(phase_drifts) / max(1, len(phase_drifts)), 6),
            "median_phase_drift": round(sorted(phase_drifts)[len(phase_drifts) // 2], 6),
            "mean_tau_gradient_mean": round(sum(tau_gradients) / max(1, len(tau_gradients)), 6),
            "mean_imaginal_drive": round(sum(imaginal_drive) / max(1, len(imaginal_drive)), 4),
            "samples": samples,
        }
        case_reports.append(case_report)

    mean_fit_rate = sum(report["fit_rate"] for report in case_reports) / max(1, len(case_reports))
    mean_phase_drift = sum(all_phase_drifts) / max(1, len(all_phase_drifts))
    summary = {
        "case_count": len(case_reports),
        "sample_count": all_trials,
        "n_trials": n_trials,
        "strength": round(strength, 4),
        "seed": seed,
        "mean_fit_rate": round(mean_fit_rate, 4),
        "global_fit_rate": round(all_fits / max(1, all_trials), 4),
        "mean_phase_drift": round(mean_phase_drift, 6),
        "mean_tau_gradient_mean": round(sum(all_tau_gradients) / max(1, len(all_tau_gradients)), 6),
        "mean_imaginal_drive": round(sum(all_imaginal_drive) / max(1, len(all_imaginal_drive)), 4),
        "target_fit_rate": 0.99,
        "pass": mean_fit_rate >= 0.99,
    }
    return {"summary": summary, "cases": case_reports}


def load_cases(path: str | None) -> list[dict[str, Any]]:
    if path is None:
        return list(_DEFAULT_CASES)
    import json
    from pathlib import Path

    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(raw, list):
        return [item for item in raw if isinstance(item, dict) and str(item.get("prompt", "")).strip()]
    if isinstance(raw, dict) and isinstance(raw.get("cases"), list):
        return [item for item in raw["cases"] if isinstance(item, dict) and str(item.get("prompt", "")).strip()]
    raise ValueError("Unsupported case file format; expected list or {cases: [...]} object.")
