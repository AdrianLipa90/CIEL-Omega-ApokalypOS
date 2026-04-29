from __future__ import annotations

from pathlib import Path

from ciel_omega.ciel.orbital_memory_persistence import PersistentOrbitalSectorMemory


def test_persistent_orbital_sector_memory_replays_events(tmp_path: Path):
    store = tmp_path / "sector_events.ndjson"
    mem1 = PersistentOrbitalSectorMemory(store_path=store)
    out1 = mem1.record({
        "content": "orbital trace alpha",
        "modality": "orbital_text",
        "phase": 0.3,
        "salience": 0.8,
        "confidence": 0.7,
        "novelty": 0.6,
        "identity_impact": 0.7,
        "context": {"control_mode": "standard"},
    })
    assert store.exists()
    assert out1["snapshot"].counts["m2_episodes"] >= 1

    mem2 = PersistentOrbitalSectorMemory(store_path=store)
    assert mem2.restored_events >= 1
    retrieval = mem2.retrieve("orbital trace alpha", top_k=2)
    episodic = retrieval.get("episodic") or []
    assert episodic

