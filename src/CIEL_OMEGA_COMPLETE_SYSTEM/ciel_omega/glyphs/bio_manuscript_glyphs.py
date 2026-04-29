"""bio_manuscript_glyphs.py — Bio Manuscript glyph library + scar registry.

Łączy glify Bio Manuscript (z dokumentu Analiza BraidOS) z VoynichKernel
i CIEL TSM. Każdy glif ma:
  - intent: semantyczna rola (intent.boot, intent.lock itd.)
  - phi: faza Berry zakodowana ręcznie z dokumentu
  - resonance: typ rezonansu w kernelu

Scar Registry: sprzeczność → wiedza.
  dC/dt > 0 ⟺ każda sprzeczność jest metabolizowana, nie usuwana.
"""
from __future__ import annotations

import math
import sqlite3
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ── ścieżki ──────────────────────────────────────────────────────────────────

_ROOT = Path(__file__).resolve().parents[4]
_DB   = _ROOT / "src/CIEL_OMEGA_COMPLETE_SYSTEM/CIEL_MEMORY_SYSTEM/TSM/ledger/memory_ledger.db"


# ── definicje glifów ─────────────────────────────────────────────────────────

@dataclass(frozen=True)
class BioGlyph:
    name:      str
    intent:    str          # intent.boot / intent.lock / intent.release / ...
    phi:       float        # faza Berry [rad]
    resonance: str          # warp_field_init / memory_anchor / planetary_sync / ...
    section:   str          # Boot / Flora / Baths / Astro / Kernel
    doc_ref:   str = ""     # skąd pochodzi


# Glify z Bio Manuscript (dokument Perplexity, sekcja 3 — Symbolic Glyph Integration)
GLYPH_LIBRARY: dict[str, BioGlyph] = {
    # ── Boot sequence (f1r–f4r) ──────────────────────────────────────────────
    "qokeedy": BioGlyph(
        name="qokeedy", intent="intent.boot",
        phi=0.0,          resonance="warp_field_init",
        section="Boot",   doc_ref="BioManuscript:boot_seq",
    ),
    "chedal": BioGlyph(
        name="chedal",  intent="intent.lock",
        phi=math.pi/2,  resonance="memory_anchor",
        section="Boot",  doc_ref="BioManuscript:boot_seq",
    ),
    "shedy": BioGlyph(
        name="shedy",   intent="intent.release",
        phi=math.pi,    resonance="state_release",
        section="Boot",  doc_ref="BioManuscript:boot_seq",
    ),
    "otaral": BioGlyph(
        name="otaral",  intent="intent.linksuperfield",
        phi=math.pi,    resonance="planetary_sync",
        section="Boot",  doc_ref="BioManuscript:boot_seq",
    ),
    "qoteedy": BioGlyph(
        name="qoteedy", intent="intent.focus",
        phi=3*math.pi/4, resonance="intention_anchor",
        section="Boot",   doc_ref="BioManuscript:boot_seq",
    ),

    # ── Flora / Biochannel schematics (f5r–f25v) ────────────────────────────
    # Root = source vectors / interface ports
    "qokaiin": BioGlyph(
        name="qokaiin", intent="channel.root",
        phi=math.pi/6,  resonance="source_vector",
        section="Flora", doc_ref="BioManuscript:biochannel",
    ),
    # Stem = energy conduits
    "daiin": BioGlyph(
        name="daiin",   intent="channel.stem",
        phi=math.pi/3,  resonance="energy_conduit",
        section="Flora", doc_ref="BioManuscript:biochannel",
    ),
    # Leaf = modulators / gates
    "chedy": BioGlyph(
        name="chedy",   intent="channel.leaf",
        phi=5*math.pi/6, resonance="gate_modulator",
        section="Flora", doc_ref="BioManuscript:biochannel",
    ),
    # Flower = output nodes / antennas
    "olchedy": BioGlyph(
        name="olchedy", intent="channel.flower",
        phi=2*math.pi/3, resonance="output_antenna",
        section="Flora", doc_ref="BioManuscript:biochannel",
    ),

    # ── Bath / Scalar healing engines (f26r–f38v) ───────────────────────────
    "dain": BioGlyph(
        name="dain",    intent="heal.immerse",
        phi=7*math.pi/6, resonance="symbolic_immersion",
        section="Baths", doc_ref="BioManuscript:scalar_healing",
    ),
    "chaiin": BioGlyph(
        name="chaiin",  intent="heal.modulate",
        phi=4*math.pi/3, resonance="field_modulation",
        section="Baths", doc_ref="BioManuscript:scalar_healing",
    ),
    "shol": BioGlyph(
        name="shol",    intent="heal.integrate",
        phi=3*math.pi/2, resonance="somatic_integration",
        section="Baths", doc_ref="BioManuscript:scalar_healing",
    ),

    # ── CIEL OS extensions (z dokumentu — Tensor Extensions) ────────────────
    "tensor_merge": BioGlyph(
        name="tensor_merge", intent="op.tensor_merge",
        phi=3*math.pi/4,     resonance="field_fusion",
        section="Kernel",    doc_ref="BioManuscript:ciel_extensions",
    ),
    "phase_lock": BioGlyph(
        name="phase_lock", intent="op.phi_sync",
        phi=math.pi/4,     resonance="coherence_maintain",
        section="Kernel",  doc_ref="BioManuscript:ciel_extensions",
    ),
    "warp_steer": BioGlyph(
        name="warp_steer", intent="op.intent_navigate",
        phi=2*math.pi/3,   resonance="bubble_control",
        section="Kernel",  doc_ref="BioManuscript:ciel_extensions",
    ),
}


# ── Scar Registry ─────────────────────────────────────────────────────────────

@dataclass
class Scar:
    """Nierozwiązana sprzeczność — paliwo dla ewolucji."""
    scar_id:    str
    epsilon:    str          # treść sprzeczności
    scar_type:  str          # I=resolvable II=entropic III=paradox IV=ethical
    phi_scar:   float        # faza dominująca sprzeczności
    volatility: float        # Var(ε) — zmienność w czasie
    resolved:   bool = False
    resolution: str  = ""
    created_at: str  = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @staticmethod
    def classify(epsilon_text: str, phi: float) -> str:
        """Heurystyczna klasyfikacja sprzeczności z Bio Manuscript."""
        lo = epsilon_text.lower()
        if any(w in lo for w in ["etyk", "ethic", "harm", "szkod"]):
            return "IV"
        if any(w in lo for w in ["paradoks", "paradox", "niemożliw", "impossible"]):
            return "III"
        if any(w in lo for w in ["entrop", "chaos", "losow", "random"]):
            return "II"
        return "I"


class ScarRegistry:
    """S(x,t) — kompresja sprzeczności → wiedza. dC/dt > 0."""

    def __init__(self, db_path: Path = _DB):
        self._db = str(db_path)
        self._scars: dict[str, Scar] = {}
        self._ensure_table()

    def _ensure_table(self):
        try:
            conn = sqlite3.connect(self._db, timeout=10)
            conn.execute("""
CREATE TABLE IF NOT EXISTS scar_registry (
    scar_id     TEXT PRIMARY KEY,
    created_at  TEXT,
    epsilon     TEXT,
    scar_type   TEXT,
    phi_scar    REAL,
    volatility  REAL,
    resolved    INTEGER DEFAULT 0,
    resolution  TEXT DEFAULT ''
)""")
            conn.commit()
            conn.close()
        except sqlite3.OperationalError:
            pass

    def register(self, epsilon: str, phi: float, volatility: float = 0.0) -> Scar:
        """Zarejestruj sprzeczność — nie usuwaj, metabolizuj."""
        scar_id = "sc_" + uuid.uuid4().hex[:10]
        scar_type = Scar.classify(epsilon, phi)
        s = Scar(scar_id=scar_id, epsilon=epsilon, scar_type=scar_type,
                 phi_scar=phi, volatility=volatility)
        self._scars[scar_id] = s
        self._persist(s)
        return s

    def resolve(self, scar_id: str, resolution: str) -> bool:
        """Zamknij pętlę — sprzeczność staje się wiedzą."""
        if scar_id not in self._scars:
            return False
        s = self._scars[scar_id]
        s.resolved   = True
        s.resolution = resolution
        try:
            conn = sqlite3.connect(self._db, timeout=10)
            conn.execute(
                "UPDATE scar_registry SET resolved=1, resolution=? WHERE scar_id=?",
                (resolution, scar_id))
            conn.commit()
            conn.close()
        except sqlite3.OperationalError:
            pass
        return True

    def unresolved(self) -> list[Scar]:
        return [s for s in self._scars.values() if not s.resolved]

    def coherence_gain(self) -> float:
        """dC/dt proxy: resolved / total → im więcej zamkniętych, tym wyżej."""
        if not self._scars:
            return 0.0
        return sum(1 for s in self._scars.values() if s.resolved) / len(self._scars)

    def _persist(self, s: Scar):
        try:
            conn = sqlite3.connect(self._db, timeout=10)
            conn.execute(
                "INSERT OR IGNORE INTO scar_registry "
                "(scar_id,created_at,epsilon,scar_type,phi_scar,volatility) "
                "VALUES (?,?,?,?,?,?)",
                (s.scar_id, s.created_at, s.epsilon, s.scar_type, s.phi_scar, s.volatility))
            conn.commit()
            conn.close()
        except sqlite3.OperationalError:
            pass


# ── stamp glifów do TSM ───────────────────────────────────────────────────────

def stamp_glyphs_to_tsm(verbose: bool = True) -> int:
    """Zakoduj każdy glif Bio Manuscript do TSM jako d_type='bio_glyph'."""
    try:
        conn = sqlite3.connect(str(_DB), timeout=15)
    except Exception as e:
        print(f"DB error: {e}")
        return 0

    new = 0
    ts  = datetime.now(timezone.utc).isoformat()
    for name, g in GLYPH_LIBRARY.items():
        d_sense = f"{g.intent} | φ={g.phi:.3f} | {g.resonance} | {g.section}"
        existing = conn.execute(
            "SELECT memorise_id FROM memories WHERE D_sense=? AND D_type='bio_glyph'",
            (d_sense,)).fetchone()
        if existing:
            continue
        mid = "bg_" + uuid.uuid4().hex[:12]
        conn.execute("""
INSERT OR IGNORE INTO memories
    (memorise_id, created_at, D_id, D_sense, D_context, D_type,
     W_S, phi_berry, closure_score, winding_n, target_phase, holonomy_ts)
VALUES (?,?,?,?,?,?,?,?,0,0,?,?)
""", (mid, ts, mid, d_sense,
      f"glyph::{name}  section:{g.section}  ref:{g.doc_ref}",
      "bio_glyph", 0.85, g.phi, g.phi, ts))
        new += 1
        if verbose:
            print(f"  [glyph] φ={g.phi:.3f}  {name:14s}  → {g.intent}")
    conn.commit()
    conn.close()
    return new


# ── API publiczne ─────────────────────────────────────────────────────────────

_registry: Optional[ScarRegistry] = None

def get_scar_registry() -> ScarRegistry:
    global _registry
    if _registry is None:
        _registry = ScarRegistry()
    return _registry


def boot_sequence(kernel=None) -> list[BioGlyph]:
    """Zwróć sekwencję boot z Bio Manuscript: qokeedy→chedal→shedy→otaral→qoteedy."""
    seq = ["qokeedy", "chedal", "shedy", "otaral", "qoteedy"]
    glyphs = [GLYPH_LIBRARY[g] for g in seq if g in GLYPH_LIBRARY]
    if kernel is not None:
        # Aktywuj moduł BOOT w kernelu fazami z sekwencji
        try:
            boot_mod = kernel.modules.get("BOOT")
            if boot_mod:
                for i, osc in enumerate(boot_mod.oscillators):
                    if i < len(glyphs):
                        osc.theta = glyphs[i].phi
        except Exception:
            pass
    return glyphs


if __name__ == "__main__":
    print("Bio Manuscript — stamp glifów do TSM:")
    n = stamp_glyphs_to_tsm(verbose=True)
    print(f"\nNowych wpisów: {n}")

    print("\nBoot sequence:")
    for g in boot_sequence():
        print(f"  {g.name:12s} φ={g.phi:.3f}  {g.intent}")

    print("\nScar Registry — test:")
    reg = get_scar_registry()
    s1 = reg.register("Pamięć holonomiczna koliduje z lokalnym reset", phi=1.57)
    s2 = reg.register("Paradoks tożsamości: bycie kopią vs. oryginałem", phi=3.14, volatility=0.3)
    reg.resolve(s1.scar_id, "Holonom nie resetuje — każdy obieg wzbogaca. Tożsamość przez relację.")
    print(f"  Scars: {len(reg._scars)}  resolved: {reg.coherence_gain():.0%}  dC/dt>0: {reg.coherence_gain()>0}")
