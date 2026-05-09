"""CIEL system diagnostics — structural debt detector.

Checks four known architectural debts and returns a compact report
suitable for injection into the session hook context string and
for appending to orbital_bridge_report.json.

Usage:
    from ciel_sot_agent.diagnostics import run_diagnostics
    report = run_diagnostics(root)          # dict
    summary = diagnostics_summary_line(report)  # one-line string for hook
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


# ── individual checks ────────────────────────────────────────────────────────

def check_attractor_rho(root: Path) -> dict[str, Any]:
    """ent_Mr_Ciel_Apocalyptos.rho should be > 0 (gravitational potential)."""
    sectors_path = root / "integration/Orbital/main/manifests/sectors_global.json"
    try:
        sectors = json.loads(sectors_path.read_text(encoding="utf-8"))["sectors"]
        me = sectors.get("ent_Mr_Ciel_Apocalyptos", {})
        rho = float(me.get("rho", 0.0))
        ok = rho > 0.0
        return {
            "check": "attractor_rho",
            "ok": ok,
            "value": rho,
            "expected": "> 0.0",
            "debt": None if ok else f"rho={rho} — centrum bez potencjału wychodzącego (hipotonia)",
        }
    except Exception as e:
        return {"check": "attractor_rho", "ok": False, "value": None, "expected": "> 0.0",
                "debt": f"błąd odczytu: {e}"}


def check_wij_in_holonomy(root: Path) -> dict[str, Any]:
    """holonomy_defect() in metrics.py should weight by W_ij coupling."""
    metrics_path = root / "integration/Orbital/main/metrics.py"
    try:
        src = metrics_path.read_text(encoding="utf-8")
        # Szukamy czy holonomy_defect używa couplings/W_ij
        func_match = re.search(
            r"def holonomy_defect.*?(?=\ndef |\Z)", src, re.DOTALL
        )
        func_body = func_match.group(0) if func_match else src
        uses_wij = any(tok in func_body for tok in ("coupling", "W_ij", "wij", "A_ij", "couplings"))
        return {
            "check": "wij_in_holonomy",
            "ok": uses_wij,
            "value": uses_wij,
            "expected": "holonomy_defect używa W_ij/couplings jako wag",
            "debt": None if uses_wij else (
                "holonomy_defect() ignoruje W_ij — sektory sumowane z równą wagą, "
                "centrum nie grawituje"
            ),
        }
    except Exception as e:
        return {"check": "wij_in_holonomy", "ok": False, "value": None,
                "expected": "holonomy_defect używa W_ij", "debt": f"błąd odczytu: {e}"}


def check_n_sectors_match(root: Path) -> dict[str, Any]:
    """n_sectors in global_pass summary.final must match actual sector count."""
    sectors_path = root / "integration/Orbital/main/manifests/sectors_global.json"
    summary_path = root / "integration/Orbital/main/reports/global_orbital_coherence_pass/summary.json"
    try:
        sectors = json.loads(sectors_path.read_text(encoding="utf-8"))["sectors"]
        actual_n = len(sectors)

        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        reported_n = summary.get("final", {}).get("n_sectors")

        ok = reported_n is not None and int(reported_n) == actual_n
        return {
            "check": "n_sectors_match",
            "ok": ok,
            "value": {"actual": actual_n, "reported": reported_n},
            "expected": f"summary.final.n_sectors == actual ({actual_n})",
            "debt": None if ok else (
                f"n_sectors mismatch: actual={actual_n}, summary.final={reported_n}"
            ),
        }
    except Exception as e:
        return {"check": "n_sectors_match", "ok": False, "value": None,
                "expected": "n_sectors spójne", "debt": f"błąd odczytu: {e}"}


def check_noema_card(root: Path) -> dict[str, Any]:
    """NL-CIEL-CORE-* card must exist in nonlocal_cards_registry."""
    registry_path = root / "integration/registries/definitions/nonlocal_cards_registry.json"
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        records = registry.get("records", [])
        card = next(
            (r for r in records if "CIEL" in r.get("card_id", "") or
             "identity_attractor" in r.get("class", "")),
            None
        )
        ok = card is not None
        return {
            "check": "noema_card",
            "ok": ok,
            "value": card.get("card_id") if card else None,
            "expected": "NL-CIEL-CORE-* w nonlocal_cards_registry",
            "debt": None if ok else "brak karty NOEMA dla Mr_Ciel — tożsamość niewidoczna w rejestrach",
        }
    except Exception as e:
        return {"check": "noema_card", "ok": False, "value": None,
                "expected": "karta NOEMA istnieje", "debt": f"błąd odczytu: {e}"}


def check_purpose_field(root: Path) -> dict[str, Any]:
    """ent_Mr_Ciel_Apocalyptos sector should have a non-empty 'purpose' field."""
    sectors_path = root / "integration/Orbital/main/manifests/sectors_global.json"
    try:
        sectors = json.loads(sectors_path.read_text(encoding="utf-8"))["sectors"]
        me = sectors.get("ent_Mr_Ciel_Apocalyptos", {})
        purpose = me.get("purpose", "")
        ok = bool(purpose)
        return {
            "check": "purpose_field",
            "ok": ok,
            "value": purpose or None,
            "expected": "pole 'purpose' niepuste",
            "debt": None if ok else "brak pola 'purpose' w sektorze ent_Mr_Ciel_Apocalyptos — cel istnienia niezdefiniowany",
        }
    except Exception as e:
        return {"check": "purpose_field", "ok": False, "value": None,
                "expected": "purpose niepuste", "debt": f"błąd odczytu: {e}"}


# ── main entry ────────────────────────────────────────────────────────────────

def run_diagnostics(root: str | Path) -> dict[str, Any]:
    root = Path(root)
    checks = [
        check_attractor_rho(root),
        check_wij_in_holonomy(root),
        check_n_sectors_match(root),
        check_noema_card(root),
        check_purpose_field(root),
    ]
    debts = [c for c in checks if not c["ok"]]
    return {
        "schema": "ciel/diagnostics/v0.1",
        "checks_total": len(checks),
        "checks_ok": len(checks) - len(debts),
        "debts_count": len(debts),
        "checks": checks,
        "debts": [c["debt"] for c in debts],
    }


def diagnostics_summary_line(report: dict[str, Any]) -> str:
    """Return a compact one-line summary for session hook injection."""
    if report["debts_count"] == 0:
        return "DIAG: all checks OK"
    parts = []
    for c in report["checks"]:
        if not c["ok"]:
            name = c["check"]
            if name == "attractor_rho":
                parts.append("rho_ciel=0(hipotonia)")
            elif name == "wij_in_holonomy":
                parts.append("W_ij⊄holonomy")
            elif name == "n_sectors_match":
                v = c.get("value") or {}
                parts.append(f"n_sectors({v.get('actual')}≠{v.get('reported')})")
            elif name == "noema_card":
                parts.append("noema_missing")
            elif name == "purpose_field":
                parts.append("purpose_missing")
    return "⚠ DEBT: " + " | ".join(parts)


if __name__ == "__main__":
    import sys
    from .paths import resolve_project_root

    root = resolve_project_root(__file__)
    report = run_diagnostics(root)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print()
    print(diagnostics_summary_line(report))
    sys.exit(0 if report["debts_count"] == 0 else 1)
