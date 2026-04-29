from __future__ import annotations

from ciel_omega.ciel.engine import CielEngine
from ciel_omega.ciel.memory_prompt_context import summarize_sector_retrieval


def test_engine_exposes_memory_governor_and_governed_retrieval():
    engine = CielEngine()
    state = engine.step("Orbital memory should remember this trace.", context="orbital/test")
    gov = state.get("memory_governor")
    assert isinstance(gov, dict)
    assert gov["retrieval_top_k"] >= 1
    sector = state.get("sector_memory")
    assert isinstance(sector, dict)
    assert "governed_retrieval" in sector
    summary = summarize_sector_retrieval({"sector_memory": sector})
    assert isinstance(summary, dict)



def test_prompt_summary_exposes_ranked_holonomic_lines():
    engine = CielEngine()
    state = engine.step("Orbital memory should remember ranked context.", context="orbital/test")
    summary = summarize_sector_retrieval(state)
    assert "ranked" in summary
    assert summary["ranked"]
    assert any("hq=" in line and "pa=" in line for line in summary["ranked"])


def test_engine_exposes_consolidation_holonomy_and_applied_governor():
    engine = CielEngine()
    state = engine.step("Orbital consolidation should expose holonomy.", context="orbital/test")
    gov = state.get("memory_governor")
    assert isinstance(gov, dict)
    assert "consolidation_holonomy" in gov
    assert set(gov["consolidation_holonomy"].keys()) == {"semantic", "procedural", "affective"}
    sector = state.get("sector_memory")
    assert isinstance(sector, dict)
    assert "applied_memory_governor" in sector
    assert sector["event"].get("memory_governor")
