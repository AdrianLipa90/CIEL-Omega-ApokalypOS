from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict
import json

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None


@dataclass(frozen=True)
class CaseMapping:
    case: str
    operator: str
    equation: str
    strategy: str
    loss_risk: float


def load_case_gauge(path: str | Path) -> Dict[str, Any]:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if p.suffix.lower() in {".yaml", ".yml"}:
        if yaml is None:
            raise RuntimeError("PyYAML is required for YAML case gauge files.")
        return yaml.safe_load(text)
    return json.loads(text)


def map_polish_case_to_language(case: str, target_language: str, gauge: Dict[str, Any]) -> CaseMapping:
    case = case.strip().capitalize()
    lang = target_language.strip().lower()
    if lang not in {"en", "de", "fr", "es"}:
        raise ValueError(f"Unsupported target language: {target_language}")
    for row in gauge["case_roles"]:
        if row["ud"] == case:
            return CaseMapping(
                case=row["ud"],
                operator=row["canonical_operator"],
                equation=row["equation"],
                strategy=row[f"{lang}_strategy"],
                loss_risk=float(row["loss_risk"]),
            )
    raise KeyError(f"Unknown case: {case}")


def decode_case_role(case: str) -> str:
    c = case.strip().capitalize()
    mapping = {
        "Nom": "SubjectOrIdentity(x)",
        "Acc": "DirectPatient(x)",
        "Gen": "OfPossessionSourcePartitive(x,y)",
        "Dat": "RecipientBeneficiaryTarget(x)",
        "Ins": "InstrumentMeansComitativeRole(x)",
        "Loc": "LocationTopicFrame(x)",
        "Voc": "Address(x)",
    }
    if c not in mapping:
        raise KeyError(c)
    return mapping[c]


def reconstruction_cost(case: str, target_language: str) -> float:
    """Deterministic seed proxy, not corpus statistics.

    Higher means a case-rich Slavic signal needs more surface scaffolding in the target language.
    German is lower because it still preserves productive case morphology.
    """
    base = {"Nom":0.10,"Acc":0.15,"Gen":0.35,"Dat":0.20,"Ins":0.25,"Loc":0.30,"Voc":0.15}
    adj = {"en":0.25,"de":-0.10,"fr":0.20,"es":0.18}
    c = case.strip().capitalize(); l = target_language.strip().lower()
    if c not in base or l not in adj:
        raise KeyError((case,target_language))
    return max(0.0, min(1.0, base[c] + adj[l]))
