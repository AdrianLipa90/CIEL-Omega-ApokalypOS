from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OMEGA_ROOT = ROOT / "src" / "CIEL_OMEGA_COMPLETE_SYSTEM"
if str(OMEGA_ROOT) not in sys.path:
    sys.path.insert(0, str(OMEGA_ROOT))

from ciel_omega.jokeheal import HumorDose, SafetyLevel, TensionInput, run_jokeheal


def test_sensu_stricte_disables_humor_for_literal_danger() -> None:
    out = run_jokeheal(
        TensionInput(
            text="sensu stricte mam tasak i rozważam autoamputację",
            source="test",
        )
    )
    assert out.boundary.level == SafetyLevel.LITERAL_ALARM
    assert out.humor_dose == HumorDose.NONE
    assert "Literal danger" in out.reframe


def test_grotesque_mnemonic_caricature_is_not_auto_alarm() -> None:
    out = run_jokeheal(
        TensionInput(
            text="kamień na nerce jak obelisk owinięty drutem kolczastym, karykatura w pałacu pamięci",
            source="test",
        )
    )
    assert out.boundary.level in {SafetyLevel.CLEAR, SafetyLevel.WATCH}
    assert out.mode == "mnemonic_caricature"
    assert out.humor_dose.value >= 1
    assert "renal_obelisk" in out.symbolic_object


def test_noema_projection_has_no_runtime_authority() -> None:
    out = run_jokeheal(TensionInput(text="lekki stres, potrzebuję mgiełki humoru", source="test"))
    assert "projection_only_no_runtime_authority" in out.noema_card
    assert "object jokeheal_event_" in out.noema_card
