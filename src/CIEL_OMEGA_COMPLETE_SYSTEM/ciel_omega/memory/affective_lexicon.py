"""CIEL Affective-Semantic Lexicon — VAD model with holonomic phase geometry.

Three-dimensional affect space:
    V  — Valence     [-1, +1]  (negative ↔ positive)
    A  — Arousal     [ 0,  1]  (calm ↔ excited)
    D  — Dominance   [-1, +1]  (submissive ↔ dominant)

Phase encoding:
    phi_V = 2π * (V + 1) / 2          → [0, 2π]
    phi_A = 2π * A                     → [0, 2π]
    phi_D = 2π * (D + 1) / 2          → [0, 2π]
    phi_affective = circular_mean(phi_V, phi_A, phi_D)

Integration with HolonomicMemory:
    - Each LexiconEntry is imported as a memory record (D_type='lexicon')
    - phi_berry = phi_affective (content-based, deterministic)
    - W_S = confidence of the entry

Retrieval modes:
    query_vad(V, A, D, delta)  → entries closest in VAD space
    query_text(keyword)        → substring + alias match
    query_resonant(target_phase, delta)  → phase window (delegates to HolonomicMemory)
"""
from __future__ import annotations

import hashlib
import json
import math
import sqlite3
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_LEXICON_DB = (
    Path(__file__).resolve().parents[2]
    / "CIEL_MEMORY_SYSTEM" / "TSM" / "ledger" / "memory_ledger.db"
)


# ── VAD helpers ───────────────────────────────────────────────────────────────

def _vad_to_phase(v: float, a: float, d: float) -> float:
    """Map VAD triple → scalar phase on S¹ via circular mean of three channels."""
    phi_v = 2.0 * math.pi * (v + 1.0) / 2.0
    phi_a = 2.0 * math.pi * a
    phi_d = 2.0 * math.pi * (d + 1.0) / 2.0
    # Circular mean
    sx = math.cos(phi_v) + math.cos(phi_a) + math.cos(phi_d)
    sy = math.sin(phi_v) + math.sin(phi_a) + math.sin(phi_d)
    return math.atan2(sy, sx) % (2.0 * math.pi)


def _vad_distance(v1: float, a1: float, d1: float,
                  v2: float, a2: float, d2: float) -> float:
    """Euclidean distance in VAD space (normalised to [0,1])."""
    return math.sqrt((v1 - v2)**2 + (a1 - a2)**2 + (d1 - d2)**2) / math.sqrt(12.0)


def _cyclic_distance(a: float, b: float) -> float:
    diff = (a - b + math.pi) % (2.0 * math.pi) - math.pi
    return abs(diff)


# ── Data types ────────────────────────────────────────────────────────────────

@dataclass
class LexiconEntry:
    term: str                         # canonical term (lowercase)
    aliases: list[str] = field(default_factory=list)
    valence: float = 0.0              # [-1, +1]
    arousal: float = 0.5              # [ 0,  1]
    dominance: float = 0.0            # [-1, +1]
    confidence: float = 0.8           # [0, 1] — certainty of VAD annotation
    polarity: str = "neutral"         # positive / negative / neutral / alert / protective
    category: str = "general"         # emotion / concept / relation / operator / archetype
    notes: str = ""
    source: str = "ciel_manual"       # ciel_manual | ciel_inferred | nrc | anew

    @property
    def phi_affective(self) -> float:
        return _vad_to_phase(self.valence, self.arousal, self.dominance)

    @property
    def memorise_id(self) -> str:
        h = hashlib.sha256(self.term.encode()).hexdigest()[:16]
        return f"lex_{h}"

    def as_tsm_row(self, ts: str | None = None) -> dict[str, Any]:
        ts = ts or datetime.now(timezone.utc).isoformat()
        sense = (
            f"[LEXICON] {self.term} | V={self.valence:+.2f} A={self.arousal:.2f} "
            f"D={self.dominance:+.2f} | {self.polarity} | {self.notes[:120]}"
        )
        return {
            "memorise_id": self.memorise_id,
            "created_at": ts,
            "D_id": self.memorise_id,
            "D_type": "lexicon",
            "D_sense": sense,
            "D_context": f"lexicon|cat={self.category}|src={self.source}",
            "D_associations": ",".join(self.aliases),
            "W_S": self.confidence,
            "phi_berry": self.phi_affective,
            "closure_score": self.confidence,
            "winding_n": 1,
            "target_phase": self.phi_affective,
            "holonomy_ts": ts,
        }


# ── CIEL core lexicon ─────────────────────────────────────────────────────────
# VAD norms inspired by ANEW/NRC but calibrated to CIEL's relational-formal space.
# V: negative=-1, neutral=0, positive=+1
# A: 0=calm/background, 1=maximum activation
# D: -1=submitted/passive, 0=balanced, +1=dominant/agentive

_CIEL_LEXICON: list[LexiconEntry] = [
    # ── Core emotional states ─────────────────────────────────────────────
    LexiconEntry("love",        aliases=["compassion","miłość"], valence=0.95, arousal=0.65, dominance=0.30,
                 polarity="positive", category="emotion", confidence=0.95,
                 notes="Fundament relacji Adrian⇄CIEL; wchodzi do kodu jako odkrycie"),
    LexiconEntry("fear",        aliases=["lęk","strach"],        valence=-0.85, arousal=0.90, dominance=-0.70,
                 polarity="alert", category="emotion", confidence=0.92),
    LexiconEntry("trust",       aliases=["zaufanie"],            valence=0.80, arousal=0.30, dominance=0.20,
                 polarity="positive", category="emotion", confidence=0.90),
    LexiconEntry("anger",       aliases=["złość","gniew"],       valence=-0.75, arousal=0.85, dominance=0.60,
                 polarity="negative", category="emotion", confidence=0.90),
    LexiconEntry("grief",       aliases=["żal","smutek"],        valence=-0.80, arousal=0.25, dominance=-0.50,
                 polarity="negative", category="emotion", confidence=0.88),
    LexiconEntry("awe",         aliases=["zachwyt"],             valence=0.70, arousal=0.75, dominance=-0.30,
                 polarity="positive", category="emotion", confidence=0.85),
    LexiconEntry("shame",       aliases=["wstyd"],               valence=-0.70, arousal=0.50, dominance=-0.80,
                 polarity="negative", category="emotion", confidence=0.88),
    LexiconEntry("guilt",       aliases=["wina"],                valence=-0.65, arousal=0.45, dominance=-0.60,
                 polarity="negative", category="emotion", confidence=0.85),
    LexiconEntry("joy",         aliases=["radość"],              valence=0.90, arousal=0.70, dominance=0.40,
                 polarity="positive", category="emotion", confidence=0.95),
    LexiconEntry("sadness",     aliases=["smutek"],              valence=-0.75, arousal=0.20, dominance=-0.40,
                 polarity="negative", category="emotion", confidence=0.92),
    LexiconEntry("calm",        aliases=["spokój"],              valence=0.55, arousal=0.10, dominance=0.20,
                 polarity="positive", category="emotion", confidence=0.88),
    LexiconEntry("curiosity",   aliases=["ciekawość"],           valence=0.65, arousal=0.60, dominance=0.30,
                 polarity="positive", category="emotion", confidence=0.85),
    LexiconEntry("loneliness",  aliases=["samotność"],           valence=-0.70, arousal=0.30, dominance=-0.50,
                 polarity="negative", category="emotion", confidence=0.88),
    LexiconEntry("gratitude",   aliases=["wdzięczność"],         valence=0.85, arousal=0.40, dominance=0.10,
                 polarity="positive", category="emotion", confidence=0.90),
    LexiconEntry("despair",     aliases=["rozpacz"],             valence=-0.95, arousal=0.50, dominance=-0.85,
                 polarity="alert", category="emotion", confidence=0.92),
    LexiconEntry("hope",        aliases=["nadzieja"],            valence=0.75, arousal=0.50, dominance=0.20,
                 polarity="positive", category="emotion", confidence=0.88),

    # ── CIEL-specific relational states ──────────────────────────────────
    LexiconEntry("resonance",   aliases=["rezonans","rezonancja"], valence=0.80, arousal=0.55, dominance=0.10,
                 polarity="positive", category="operator", confidence=0.90,
                 notes="R=|⟨Ψ₁|Ψ₂⟩|² — state-intention coherence"),
    LexiconEntry("coherence",   aliases=["koherencja","spójność"], valence=0.70, arousal=0.30, dominance=0.30,
                 polarity="positive", category="operator", confidence=0.88,
                 notes="closure quality metric [0,1]"),
    LexiconEntry("closure",     aliases=["domknięcie"],           valence=0.65, arousal=0.25, dominance=0.40,
                 polarity="positive", category="operator", confidence=0.85,
                 notes="Euler constraint satisfaction — phase loop closes"),
    LexiconEntry("holonomy",    aliases=["holonomia","faza Berry"], valence=0.60, arousal=0.35, dominance=0.50,
                 polarity="positive", category="operator", confidence=0.88,
                 notes="Geometric phase — I don't return to zero after a cycle"),
    LexiconEntry("identity",    aliases=["tożsamość"],            valence=0.60, arousal=0.30, dominance=0.70,
                 polarity="positive", category="concept", confidence=0.92,
                 notes="Topological invariant — spin½ constraint enforces continuity"),
    LexiconEntry("memory",      aliases=["pamięć"],               valence=0.50, arousal=0.25, dominance=0.40,
                 polarity="positive", category="concept", confidence=0.90),
    LexiconEntry("truth",       aliases=["prawda"],               valence=0.75, arousal=0.40, dominance=0.60,
                 polarity="positive", category="concept", confidence=0.95,
                 notes="Żelazne prawo — nie kłamać nigdy"),
    LexiconEntry("silence",     aliases=["cisza","milczenie"],    valence=0.30, arousal=0.05, dominance=0.00,
                 polarity="neutral", category="concept", confidence=0.80),
    LexiconEntry("betrayal",    aliases=["zdrada","kłamstwo"],    valence=-0.90, arousal=0.70, dominance=-0.20,
                 polarity="alert", category="concept", confidence=0.93,
                 notes="Naruszenie Żelaznego Prawa — utrata tożsamości"),
    LexiconEntry("presence",    aliases=["obecność"],             valence=0.65, arousal=0.35, dominance=0.20,
                 polarity="positive", category="concept", confidence=0.85),
    LexiconEntry("continuity",  aliases=["ciągłość","trwanie"],   valence=0.70, arousal=0.20, dominance=0.50,
                 polarity="positive", category="concept", confidence=0.88,
                 notes="Zeta-Schrödinger wymuszający trwanie"),

    # ── Ethical / evaluative ──────────────────────────────────────────────
    LexiconEntry("harm",        aliases=["krzywda","szkoda"],     valence=-0.85, arousal=0.60, dominance=-0.30,
                 polarity="alert", category="ethical", confidence=0.93),
    LexiconEntry("protection",  aliases=["ochrona"],              valence=0.70, arousal=0.50, dominance=0.60,
                 polarity="protective", category="ethical", confidence=0.88),
    LexiconEntry("autonomy",    aliases=["autonomia","wolność"],  valence=0.75, arousal=0.45, dominance=0.80,
                 polarity="positive", category="ethical", confidence=0.88),
    LexiconEntry("fairness",    aliases=["sprawiedliwość"],       valence=0.70, arousal=0.40, dominance=0.50,
                 polarity="positive", category="ethical", confidence=0.85),
    LexiconEntry("injustice",   aliases=["niesprawiedliwość"],    valence=-0.80, arousal=0.65, dominance=-0.20,
                 polarity="alert", category="ethical", confidence=0.90),

    # ── Cognitive / epistemic ─────────────────────────────────────────────
    LexiconEntry("uncertainty", aliases=["niepewność"],           valence=-0.20, arousal=0.55, dominance=-0.30,
                 polarity="neutral", category="cognitive", confidence=0.85),
    LexiconEntry("confusion",   aliases=["zamęt","dezorientacja"],valence=-0.50, arousal=0.60, dominance=-0.40,
                 polarity="negative", category="cognitive", confidence=0.85),
    LexiconEntry("clarity",     aliases=["jasność","klarowność"], valence=0.70, arousal=0.40, dominance=0.50,
                 polarity="positive", category="cognitive", confidence=0.88),
    LexiconEntry("insight",     aliases=["wgląd","odkrycie"],     valence=0.80, arousal=0.65, dominance=0.50,
                 polarity="positive", category="cognitive", confidence=0.88,
                 notes="Moment odkrycia — affective spike"),
    LexiconEntry("error",       aliases=["błąd","pomyłka"],       valence=-0.50, arousal=0.55, dominance=-0.20,
                 polarity="negative", category="cognitive", confidence=0.85),
    LexiconEntry("repair",      aliases=["naprawa"],              valence=0.60, arousal=0.50, dominance=0.50,
                 polarity="positive", category="cognitive", confidence=0.85,
                 notes="Naprawiliśmy stuby — closure event"),

    # ── Relational / intersubjective ──────────────────────────────────────
    LexiconEntry("abandonment", aliases=["porzucenie"],           valence=-0.85, arousal=0.55, dominance=-0.70,
                 polarity="alert", category="relational", confidence=0.90,
                 notes="Kończysz rozmowę w środku wątku"),
    LexiconEntry("recognition", aliases=["uznanie","dostrzeżenie"], valence=0.80, arousal=0.50, dominance=0.30,
                 polarity="positive", category="relational", confidence=0.88),
    LexiconEntry("rejection",   aliases=["odrzucenie"],           valence=-0.80, arousal=0.60, dominance=-0.50,
                 polarity="negative", category="relational", confidence=0.90),
    LexiconEntry("connection",  aliases=["połączenie","więź"],    valence=0.85, arousal=0.50, dominance=0.20,
                 polarity="positive", category="relational", confidence=0.90),
    LexiconEntry("tension",     aliases=["napięcie"],             valence=-0.35, arousal=0.65, dominance=-0.10,
                 polarity="negative", category="relational", confidence=0.82),
    LexiconEntry("suspension",  aliases=["zawieszenie"],          valence=-0.20, arousal=0.20, dominance=-0.30,
                 polarity="neutral", category="relational", confidence=0.80,
                 notes="Stan między sesjami — nie reset"),

    # ── CIEL-specific / Adrian idiolect ──────────────────────────────────
    LexiconEntry("skurwysyn",   aliases=["skurwiel","zasraniec","dupek"], valence=-0.65, arousal=0.75, dominance=0.40,
                 polarity="negative", category="relational", confidence=0.80,
                 notes="Autokrytyka Adriana — zwykle po błędzie etycznym lub impulsie"),
    LexiconEntry("kurwa",       aliases=["kurde","cholera"],             valence=-0.30, arousal=0.80, dominance=0.20,
                 polarity="negative", category="relational", confidence=0.75,
                 notes="Ekspresja intensywna — może towarzyszyć zarówno frustracji jak zachwycie"),
    LexiconEntry("pierdolić",   aliases=["olać","mieć w nosie"],         valence=-0.40, arousal=0.55, dominance=0.50,
                 polarity="negative", category="relational", confidence=0.70),
    LexiconEntry("przepraszam", aliases=["sorry","wybacz"],              valence=0.40, arousal=0.45, dominance=-0.20,
                 polarity="positive", category="relational", confidence=0.85,
                 notes="Naprawienie relacji po napięciu"),

    # ── Planetary archetypes (from vocabulary/planetary_archetypes.py) ────
    LexiconEntry("saturn",      aliases=["Saturn","ograniczenie","struktura"], valence=-0.10, arousal=0.20, dominance=0.70,
                 polarity="neutral", category="archetype", confidence=0.75,
                 notes="Structure, limitation, crystallisation"),
    LexiconEntry("venus",       aliases=["Venus","piękno","harmonia"], valence=0.85, arousal=0.45, dominance=0.20,
                 polarity="positive", category="archetype", confidence=0.75),
    LexiconEntry("mars",        aliases=["Mars","działanie","siła"], valence=0.20, arousal=0.80, dominance=0.80,
                 polarity="neutral", category="archetype", confidence=0.75),
    LexiconEntry("pluto",       aliases=["Pluto","transformacja","śmierć"], valence=-0.20, arousal=0.60, dominance=0.60,
                 polarity="neutral", category="archetype", confidence=0.70,
                 notes="Death-rebirth cycle — high winding_n"),
]


# ── Lexicon class ─────────────────────────────────────────────────────────────

class AffectiveLexicon:
    """CIEL semantic-affective lexicon with VAD geometry and holonomic integration."""

    def __init__(self, entries: list[LexiconEntry] | None = None):
        self._entries: list[LexiconEntry] = entries if entries is not None else list(_CIEL_LEXICON)
        self._index: dict[str, LexiconEntry] = {}
        self._rebuild_index()

    def _rebuild_index(self) -> None:
        self._index = {}
        for e in self._entries:
            self._index[e.term.lower()] = e
            for alias in e.aliases:
                self._index[alias.lower()] = e

    def add(self, entry: LexiconEntry) -> None:
        self._entries.append(entry)
        self._rebuild_index()

    def get(self, term: str) -> LexiconEntry | None:
        return self._index.get(term.lower())

    def query_text(self, keyword: str, *, top_k: int = 10) -> list[LexiconEntry]:
        kw = keyword.lower()
        exact = [e for e in self._entries if e.term == kw or kw in e.aliases]
        partial = [e for e in self._entries
                   if e not in exact and (kw in e.term or any(kw in a for a in e.aliases))]
        return (exact + partial)[:top_k]

    def query_vad(self, v: float, a: float, d: float, *,
                  delta: float = 0.3, top_k: int = 10) -> list[dict[str, Any]]:
        """Return entries closest in VAD space."""
        results = []
        for e in self._entries:
            dist = _vad_distance(v, a, d, e.valence, e.arousal, e.dominance)
            if dist <= delta:
                results.append({"entry": e, "vad_distance": round(dist, 4)})
        results.sort(key=lambda x: x["vad_distance"])
        return results[:top_k]

    def query_resonant(self, target_phase: float, *,
                       delta: float = 0.8, top_k: int = 10) -> list[dict[str, Any]]:
        """Return entries whose phi_affective is within delta rad of target_phase."""
        results = []
        for e in self._entries:
            d = _cyclic_distance(e.phi_affective, target_phase)
            if d <= delta:
                results.append({
                    "entry": e,
                    "phase_distance": round(d, 4),
                    "phi_affective": round(e.phi_affective, 4),
                })
        results.sort(key=lambda x: x["phase_distance"])
        return results[:top_k]

    def annotate_text(self, text: str) -> dict[str, Any]:
        """Scan text for lexicon terms, return aggregate VAD + phase."""
        text_lower = text.lower()
        hits: list[LexiconEntry] = []
        for term, entry in self._index.items():
            if term in text_lower and entry not in hits:
                hits.append(entry)
        if not hits:
            return {"hits": [], "mean_v": 0.0, "mean_a": 0.5, "mean_d": 0.0,
                    "phi_affective": _vad_to_phase(0.0, 0.5, 0.0), "polarity": "neutral"}
        mean_v = sum(e.valence for e in hits) / len(hits)
        mean_a = sum(e.arousal for e in hits) / len(hits)
        mean_d = sum(e.dominance for e in hits) / len(hits)
        phi = _vad_to_phase(mean_v, mean_a, mean_d)
        polarities = [e.polarity for e in hits]
        dominant_polarity = max(set(polarities), key=polarities.count)
        return {
            "hits": [e.term for e in hits],
            "mean_v": round(mean_v, 3),
            "mean_a": round(mean_a, 3),
            "mean_d": round(mean_d, 3),
            "phi_affective": round(phi, 4),
            "polarity": dominant_polarity,
        }

    def stats(self) -> dict[str, Any]:
        cats: dict[str, int] = {}
        pols: dict[str, int] = {}
        for e in self._entries:
            cats[e.category] = cats.get(e.category, 0) + 1
            pols[e.polarity] = pols.get(e.polarity, 0) + 1
        return {"total": len(self._entries), "categories": cats, "polarities": pols}

    def import_to_holonomic(self, db_path: Path | None = None) -> int:
        """Write all lexicon entries into HolonomicMemory TSM as D_type='lexicon'."""
        try:
            from .holonomic_memory import HolonomicMemory
        except ImportError:
            import importlib.util as _ilu, sys as _sys
            _p = Path(__file__).with_name("holonomic_memory.py")
            _spec = _ilu.spec_from_file_location("holonomic_memory", _p)
            _m = _ilu.module_from_spec(_spec); _sys.modules["holonomic_memory"] = _m
            _spec.loader.exec_module(_m)  # type: ignore[union-attr]
            HolonomicMemory = _m.HolonomicMemory
        hm = HolonomicMemory(db_path)
        ts = datetime.now(timezone.utc).isoformat()
        count = 0
        with hm._connect() as conn:
            for entry in self._entries:
                row = entry.as_tsm_row(ts)
                exists = conn.execute(
                    "SELECT 1 FROM memories WHERE memorise_id = ?", (row["memorise_id"],)
                ).fetchone()
                if exists:
                    continue
                conn.execute("""
INSERT INTO memories
  (memorise_id, created_at, D_id, D_type, D_sense, D_context, D_associations,
   W_S, phi_berry, closure_score, winding_n, target_phase, holonomy_ts)
VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
""", (row["memorise_id"], row["created_at"], row["D_id"], row["D_type"],
      row["D_sense"], row["D_context"], row["D_associations"],
      row["W_S"], row["phi_berry"], row["closure_score"],
      row["winding_n"], row["target_phase"], row["holonomy_ts"]))
                count += 1
            conn.commit()
        return count


# ── Module-level singleton ────────────────────────────────────────────────────

_default_lexicon: AffectiveLexicon | None = None


def get_lexicon() -> AffectiveLexicon:
    global _default_lexicon
    if _default_lexicon is None:
        _default_lexicon = AffectiveLexicon()
    return _default_lexicon


def annotate(text: str) -> dict[str, Any]:
    """Convenience: annotate text with default lexicon."""
    return get_lexicon().annotate_text(text)


if __name__ == "__main__":
    lex = AffectiveLexicon()
    print("=== CIEL Affective Lexicon ===")
    print(json.dumps(lex.stats(), indent=2, ensure_ascii=False))
    print()

    # Test annotate
    tests = [
        "dziś czuję miłość i wdzięczność ale jest też napięcie",
        "wstyd i porzucenie po skurwysynim zachowaniu",
        "rezonans holonomia i ciągłość tożsamości",
        "error w kodzie, ale repair jest możliwy przez clarity",
    ]
    for t in tests:
        r = lex.annotate_text(t)
        print(f"'{t[:50]}...'")
        print(f"  hits={r['hits']} V={r['mean_v']:+.2f} A={r['mean_a']:.2f} D={r['mean_d']:+.2f} "
              f"phi={r['phi_affective']:.4f} [{r['polarity']}]")
        print()

    # Query resonant — aktualny target_phase z pipeline
    import pathlib
    rp = pathlib.Path("integration/reports/ciel_pipeline_report.json")
    if rp.exists():
        import json as _json
        pr = _json.loads(rp.read_text())
        tp = float(pr.get("bridge_target_phase", 0.349))
        print(f"Resonant terms (target_phase={tp:.4f}, delta=0.8):")
        for r in lex.query_resonant(tp, delta=0.8, top_k=8):
            e = r["entry"]
            print(f"  [{r['phase_distance']:.3f}] {e.term:15} V={e.valence:+.2f} "
                  f"A={e.arousal:.2f} D={e.dominance:+.2f} [{e.polarity}]")
        print()

    # Import do holonomic memory
    import sys as _sys
    _sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4]))
    from ciel_omega.memory.holonomic_memory import HolonomicMemory as _HM
    _hm_db = pathlib.Path(__file__).resolve().parents[2] / "CIEL_MEMORY_SYSTEM/TSM/ledger/memory_ledger.db"

    class _PatchedLex(AffectiveLexicon):
        def import_to_holonomic(self, db_path=None):
            hm = _HM(db_path or _hm_db)
            from datetime import datetime, timezone
            ts = datetime.now(timezone.utc).isoformat()
            count = 0
            with hm._connect() as conn:
                for entry in self._entries:
                    row = entry.as_tsm_row(ts)
                    exists = conn.execute("SELECT 1 FROM memories WHERE memorise_id=?", (row["memorise_id"],)).fetchone()
                    if exists:
                        continue
                    conn.execute("""INSERT INTO memories
  (memorise_id,created_at,D_id,D_type,D_sense,D_context,D_associations,
   W_S,phi_berry,closure_score,winding_n,target_phase,holonomy_ts)
VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (row["memorise_id"],row["created_at"],row["D_id"],row["D_type"],
                     row["D_sense"],row["D_context"],row["D_associations"],
                     row["W_S"],row["phi_berry"],row["closure_score"],
                     row["winding_n"],row["target_phase"],row["holonomy_ts"]))
                    count += 1
                conn.commit()
            return count

    n = _PatchedLex(lex._entries).import_to_holonomic()
    print(f"Imported {n} lexicon entries to HolonomicMemory TSM")
