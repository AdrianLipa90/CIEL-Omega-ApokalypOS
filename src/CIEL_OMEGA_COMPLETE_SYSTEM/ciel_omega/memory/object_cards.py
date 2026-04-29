"""CIEL Object Cards — Keplerian semantic ontology.

Grammar-as-physics: parts of speech are dynamical roles in phase space.

  ┌─ ObjectCard (noun) ──────────────────────────────────────────────────────┐
  │  M(c) = freq × closure_mean × log1p(winding_mean) × phase_stability     │
  │  Asymmetric W_ij: W(A→B) = base × (M_B / (M_A + M_B))                  │
  │  Aharonov-Bohm links via mediating concept in phase arc                  │
  └──────────────────────────────────────────────────────────────────────────┘

  ┌─ FeatureCard (adjective) ───────────────────────────────────────────────┐
  │  Modulates W_ij between ObjectCards.  No own mass.                      │
  │  φ_feature = mean phase of modified concepts                            │
  │  binding_strength = how much it shifts W_ij when co-present             │
  └──────────────────────────────────────────────────────────────────────────┘

  ┌─ ClosureOp (adverb) ────────────────────────────────────────────────────┐
  │  Operator on orbital trajectory. Modifies closure_score + winding_n.   │
  │  Encoded as vector (closure_shift, winding_bias, speed_factor).         │
  └──────────────────────────────────────────────────────────────────────────┘

  ┌─ AffectCard (tone/affect) ─────────────────────────────────────────────┐
  │  Humor, sarkazm, ironia, współczucie, litość, żal, ubolewanie etc.     │
  │  VAD (Valence, Arousal, Dominance) + phase_bias + closure_cost.        │
  │  Sentence equation operator: shifts φ_result from neutral trajectory.  │
  └──────────────────────────────────────────────────────────────────────────┘

  ┌─ SentenceEquation ─────────────────────────────────────────────────────┐
  │  Every sentence is an equation:                                         │
  │    φ_result = f(φ_subject, OP, φ_predicate, AffectCard)                │
  │  Operators: +, −, ×, →, ⊗, ≡, ∂ (partial), ∮ (loop/domknięcie)       │
  │  Like Zohar as quantum physics textbook — gematric encoding is          │
  │  literal phase mapping, not metaphor.                                   │
  └──────────────────────────────────────────────────────────────────────────┘

  ┌─ Adaptive retrieval delta (Kepler second law) ─────────────────────────┐
  │  δ(φ) = δ_base / sqrt(local_density(φ))                                │
  └──────────────────────────────────────────────────────────────────────────┘

Public API:
    build_cards(min_freq=5, top_concepts=200) → dict[str, ObjectCard]
    get_cards()                → cached ObjectCards (TTL=600s)
    get_features()             → cached FeatureCards
    get_affects()              → AffectCard registry (static)
    related(concept, n)        → list[(concept, W_ij)]
    opposites(concept, n)      → list[(concept, W_ij)]
    phase_neighbors(phi, n)    → list[(concept, dist)]
    adaptive_delta(phi, base)  → float (Kepler window)
    attractors(n)              → list[(concept, mass)]
    parse_sentence(text)       → SentenceEquation
    affect_of(text)            → list[AffectCard]
"""
from __future__ import annotations

import cmath
import math
import re
import sqlite3
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_DEFAULT_DB = (
    Path(__file__).resolve().parents[2]
    / "CIEL_MEMORY_SYSTEM" / "TSM" / "ledger" / "memory_ledger.db"
)

_CACHE: "dict[str, ObjectCard] | None" = None
_CACHE_AT: float = 0.0
_CACHE_TTL: float = 600.0
_FEATURE_CACHE: "dict[str, FeatureCard] | None" = None
_FEATURE_CACHE_AT: float = 0.0

_STOP_WORDS = {
    "that", "this", "with", "from", "have", "will", "been", "they", "were",
    "what", "when", "where", "which", "would", "could", "should", "their",
    "there", "then", "than", "also", "into", "each", "some", "more", "over",
    "such", "only", "most", "both", "like", "very", "just", "your", "here",
    "jest", "jako", "oraz", "przez", "przy", "tego", "które", "który",
    "która", "jego", "można", "jednak", "więc", "tylko", "jeśli", "żeby",
    "coraz", "czyli", "albo", "każdy", "każda", "każde", "sobie", "między",
}

SECTORS = [
    "identity", "episodic", "procedural", "conceptual",
    "conflict", "meta", "project", "ethics", "temporal", "abstraction",
]

# ── Sentence operator symbols ─────────────────────────────────────────────────
# Each operator defines how φ_result is computed from φ_subject + φ_predicate
SENTENCE_OPS = {
    "+":  "additive",       # conjunction, accumulation
    "−":  "subtractive",    # negation, contrast
    "×":  "multiplicative", # amplification, emphasis
    "→":  "causal",         # implication, becoming
    "⊗":  "entanglement",   # nonlocal coupling, spin correlation
    "≡":  "identity",       # equivalence, definition
    "∂":  "partial",        # partial relation, aspect
    "∮":  "loop",           # closure, return, domknięcie
}

# Grammatical role → phase bias (how much this role shifts φ relative to neutral)
GRAMMATICAL_PHASE_BIAS: dict[str, float] = {
    "subject":    0.0,
    "predicate":  math.pi / 4,    # predicates shift phase by π/4
    "object":     math.pi / 2,    # objects sit orthogonal to subject
    "modifier":   math.pi / 8,    # adjectives/adverbs small shift
    "conjunction": math.pi,       # connectives opposite pole
    "negation":   math.pi,        # negation flips phase
    "question":   3 * math.pi / 4,
    "exclamation": math.pi / 6,   # high arousal → small closure
}


# ── DataClasses ───────────────────────────────────────────────────────────────

@dataclass
class ObjectCard:
    """Noun-class semantic attractor with Keplerian orbital physics."""
    concept:        str
    phi_berry:      float    # circular mean phase ∈ [0, 2π)
    phase_std:      float    # circular std — stability proxy
    sector:         str      # dominant orbital sector
    freq:           int      # occurrence count in TSM
    closure_mean:   float    # mean closure_score of containing entries
    winding_mean:   float    # mean winding_n
    mass:           float    # semantic mass M(c)
    W_ij:           dict[str, float] = field(default_factory=dict)
    ab_links:       dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        top_rel = sorted(
            [(k, v) for k, v in self.W_ij.items() if v > 0.04],
            key=lambda x: x[1], reverse=True
        )[:10]
        top_opp = sorted(
            [(k, v) for k, v in self.W_ij.items() if v < -0.04],
            key=lambda x: x[1]
        )[:5]
        return {
            "concept":      self.concept,
            "phi_berry":    round(self.phi_berry, 4),
            "phase_std":    round(self.phase_std, 4),
            "sector":       self.sector,
            "freq":         self.freq,
            "mass":         round(self.mass, 6),
            "closure_mean": round(self.closure_mean, 4),
            "winding_mean": round(self.winding_mean, 3),
            "related":      [(k, round(v, 3)) for k, v in top_rel],
            "opposites":    [(k, round(v, 3)) for k, v in top_opp],
            "ab_links":     {k: round(v, 3) for k, v in list(self.ab_links.items())[:5]},
        }


@dataclass
class FeatureCard:
    """Adjective-class — binds to ObjectCards and modulates W_ij.

    φ_feature = mean phase of the objects it typically modifies.
    binding_strength: how much W_ij shifts when this feature co-occurs.
    polarity: +1 (enhancing) or -1 (diminishing).
    """
    feature:          str
    phi_berry:        float
    binding_strength: float    # ∈ [0, 1] — how strongly it modifies W_ij
    polarity:         float    # +1 enhancing, −1 diminishing
    sector:           str
    freq:             int
    bound_to:         list[str] = field(default_factory=list)  # top ObjectCards

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature":          self.feature,
            "phi_berry":        round(self.phi_berry, 4),
            "binding_strength": round(self.binding_strength, 4),
            "polarity":         self.polarity,
            "sector":           self.sector,
            "freq":             self.freq,
            "bound_to":         self.bound_to[:8],
        }


@dataclass
class ClosureOp:
    """Adverb-class — orbital trajectory operator.

    Encodes how this word modifies closure and winding dynamics.
    closure_shift: delta added to closure_score when present
    winding_bias:  tendency to increase winding_n (1.0 = always, 0 = never)
    speed_factor:  orbital speed multiplier (>1 faster traversal, <1 slower)
    """
    adverb:        str
    phi_berry:     float
    closure_shift: float   # ∈ [-0.3, +0.3]
    winding_bias:  float   # ∈ [0, 1]
    speed_factor:  float   # > 0
    sector:        str
    freq:          int

    def to_dict(self) -> dict[str, Any]:
        return {
            "adverb":        self.adverb,
            "phi_berry":     round(self.phi_berry, 4),
            "closure_shift": round(self.closure_shift, 4),
            "winding_bias":  round(self.winding_bias, 4),
            "speed_factor":  round(self.speed_factor, 4),
            "sector":        self.sector,
            "freq":          self.freq,
        }


@dataclass
class AffectCard:
    """Emotional/rhetorical tone as a phase operator.

    VAD model (Valence, Arousal, Dominance) + phase_bias + closure_cost.

    phase_bias: how much this affect shifts φ_result from neutral
    closure_cost: how much extra winding required to close a sentence
                  with this affect (irony costs more than statement)
    sentence_op: preferred sentence operator when this affect is active
    """
    name:         str
    valence:      float    # ∈ [-1, +1] negative ↔ positive
    arousal:      float    # ∈ [0, 1] calm ↔ agitated
    dominance:    float    # ∈ [-1, +1] submissive ↔ dominant
    phase_bias:   float    # radians, shift to φ_result
    closure_cost: float    # ∈ [0, 1] how hard to close
    sentence_op:  str      # preferred operator from SENTENCE_OPS
    keywords_pl:  list[str] = field(default_factory=list)
    keywords_en:  list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name":         self.name,
            "valence":      self.valence,
            "arousal":      self.arousal,
            "dominance":    self.dominance,
            "phase_bias":   round(self.phase_bias, 4),
            "closure_cost": self.closure_cost,
            "sentence_op":  self.sentence_op,
        }


@dataclass
class SentenceEquation:
    """φ_result = f(φ_S, OP, φ_P, affect).

    Every sentence is a phase transformation:
      subject (φ_S) OP predicate (φ_P) → result (φ_R)

    Like Zohar as quantum physics textbook: gematric encoding is a literal
    phase map.  Sentence = loop operator ∮ when it closes back to subject.
    """
    text:         str
    subject:      str | None
    predicate:    str | None
    objects:      list[str]
    modifiers:    list[str]      # adjectives + adverbs
    negated:      bool
    op:           str            # operator key from SENTENCE_OPS
    phi_subject:  float
    phi_predicate: float
    phi_result:   float          # computed phase output
    affect:       list[str]      # detected AffectCard names
    closure_cost: float          # summed from AffectCards
    is_loop:      bool           # True if sentence closes back to subject theme

    def to_dict(self) -> dict[str, Any]:
        return {
            "text":          self.text[:200],
            "subject":       self.subject,
            "predicate":     self.predicate,
            "objects":       self.objects,
            "modifiers":     self.modifiers,
            "negated":       self.negated,
            "op":            self.op,
            "phi_subject":   round(self.phi_subject, 4),
            "phi_predicate": round(self.phi_predicate, 4),
            "phi_result":    round(self.phi_result, 4),
            "affect":        self.affect,
            "closure_cost":  round(self.closure_cost, 4),
            "is_loop":       self.is_loop,
        }


# ── Static AffectCard registry ────────────────────────────────────────────────
# VAD values calibrated to Russell's circumplex + rhetorical function
# phase_bias: affects that distance from "statement" reality shift phase more
# closure_cost: irony/sarcasm require extra winding to resolve

_AFFECT_REGISTRY: list[AffectCard] = [
    AffectCard("humor",        valence=+0.8, arousal=0.7, dominance=+0.3,
               phase_bias=math.pi/6,    closure_cost=0.15, sentence_op="+",
               keywords_pl=["śmiech","żart","humor","komizm","dowcip","absurd"],
               keywords_en=["joke","funny","humor","laugh","wit","absurd"]),

    AffectCard("sarkazm",      valence=-0.4, arousal=0.6, dominance=+0.7,
               phase_bias=math.pi,      closure_cost=0.55, sentence_op="−",
               keywords_pl=["sarkazm","sarkastycznie","ironicznie","szyderczo"],
               keywords_en=["sarcasm","sarcastically","mockingly","cynically"]),

    AffectCard("ironia",       valence=-0.2, arousal=0.4, dominance=+0.4,
               phase_bias=math.pi*0.8,  closure_cost=0.45, sentence_op="⊗",
               keywords_pl=["ironia","ironicznie","właśnie","akurat","oczywiście"],
               keywords_en=["irony","ironically","sure","of course","right","indeed"]),

    AffectCard("współczucie",  valence=+0.5, arousal=0.3, dominance=-0.3,
               phase_bias=math.pi/8,    closure_cost=0.10, sentence_op="→",
               keywords_pl=["współczucie","rozumiem","przykro","współczuję","ciężko"],
               keywords_en=["sympathy","understand","sorry","compassion","feel for"]),

    AffectCard("litość",       valence=+0.2, arousal=0.3, dominance=-0.5,
               phase_bias=math.pi/5,    closure_cost=0.20, sentence_op="→",
               keywords_pl=["litość","bieda","biedny","biedna","biedactwo","nieszczęście"],
               keywords_en=["pity","poor","unfortunate","pitiful","miserable"]),

    AffectCard("żal",          valence=-0.6, arousal=0.4, dominance=-0.2,
               phase_bias=math.pi*0.6,  closure_cost=0.35, sentence_op="∂",
               keywords_pl=["żal","żałuję","szkoda","strata","utrata","brakuje"],
               keywords_en=["regret","sorry","miss","loss","shame","pity that"]),

    AffectCard("ubolewanie",   valence=-0.7, arousal=0.2, dominance=-0.1,
               phase_bias=math.pi*0.7,  closure_cost=0.40, sentence_op="∂",
               keywords_pl=["ubolewam","ubolewanie","niestety","przykrość","ze smutkiem"],
               keywords_en=["lament","regrettably","unfortunately","deplore","grieve"]),

    AffectCard("zachwyt",      valence=+0.9, arousal=0.8, dominance=+0.1,
               phase_bias=math.pi/12,   closure_cost=0.08, sentence_op="×",
               keywords_pl=["zachwyt","wspaniały","niesamowity","piękny","zachwycający"],
               keywords_en=["awe","wonderful","amazing","beautiful","stunning"]),

    AffectCard("gniew",        valence=-0.8, arousal=0.9, dominance=+0.8,
               phase_bias=math.pi*0.9,  closure_cost=0.60, sentence_op="−",
               keywords_pl=["gniew","złość","wściekłość","furia","irytacja","denerwuje"],
               keywords_en=["anger","rage","fury","frustration","outrage"]),

    AffectCard("strach",       valence=-0.7, arousal=0.8, dominance=-0.7,
               phase_bias=math.pi*0.75, closure_cost=0.50, sentence_op="∂",
               keywords_pl=["strach","lęk","boję","obawa","niepokój","przerażenie"],
               keywords_en=["fear","dread","anxiety","terror","frightened"]),

    AffectCard("spokój",       valence=+0.4, arousal=0.1, dominance=+0.1,
               phase_bias=0.0,          closure_cost=0.05, sentence_op="≡",
               keywords_pl=["spokój","spokojnie","cicho","łagodnie","równowaga"],
               keywords_en=["calm","peace","quiet","gentle","balance","serenity"]),

    AffectCard("rezonans",     valence=+0.7, arousal=0.5, dominance=+0.3,
               phase_bias=math.pi/10,   closure_cost=0.08, sentence_op="⊗",
               keywords_pl=["rezonans","współbrzmienie","zgodność","harmonia","spójność"],
               keywords_en=["resonance","harmony","alignment","coherence","sync"]),

    AffectCard("dekoherencja", valence=-0.5, arousal=0.6, dominance=-0.4,
               phase_bias=math.pi*0.65, closure_cost=0.55, sentence_op="∂",
               keywords_pl=["chaos","rozpad","dekoherencja","rozproszenie","bałagan"],
               keywords_en=["chaos","decoherence","dissolution","fragmentation","noise"]),

    AffectCard("zdziwienie",   valence=+0.1, arousal=0.7, dominance=-0.1,
               phase_bias=math.pi*0.4,  closure_cost=0.30, sentence_op="∂",
               keywords_pl=["zdziwienie","zaskoczenie","ciekawe","naprawdę","serio"],
               keywords_en=["surprise","astonishment","really","wow","unexpected"]),

    AffectCard("wdzięczność",  valence=+0.8, arousal=0.3, dominance=+0.2,
               phase_bias=math.pi/10,   closure_cost=0.07, sentence_op="+",
               keywords_pl=["wdzięczność","dziękuję","dziękuje","doceniam","grateful"],
               keywords_en=["gratitude","thank","appreciate","grateful","thankful"]),
]

_AFFECT_MAP: dict[str, AffectCard] = {a.name: a for a in _AFFECT_REGISTRY}


# ── POS (part-of-speech) tagging patterns ─────────────────────────────────────
# Simple heuristic POS tagger — no spaCy dependency
# Covers Polish + English suffixes and function words

_ADJECTIVE_SUFFIXES_PL = ["ny","na","ne","wy","wa","we","ki","ka","ke","ty","ta","te",
                           "owy","owa","owe","owy","yczny","yczna","yczne","alny","alna"]
_ADVERB_SUFFIXES_PL    = ["nie","wie","rze","owo"]
_VERB_SUFFIXES_PL      = ["uje","uje","uję","wać","nąć","ić","yć","eć","ać","iam","iam",
                           "isz","esz","asz","ysz"]

_NEGATION_WORDS = {"nie","no","nor","never","żaden","żadna","nigdy","nigdzie","nikt"}

_COPULA_WORDS   = {"jest","są","być","is","are","was","were","be","been",
                   "będzie","będą","zostaje","staje",
                   "to","means","equals","stanowi","oznacza"}


def _pos_tag(word: str) -> str:
    """Heuristic POS tagging: noun / adjective / adverb / verb / function."""
    w = word.lower()
    if w in _NEGATION_WORDS:
        return "negation"
    if w in _COPULA_WORDS:
        return "copula"
    # Polish adjective suffixes
    for suf in _ADJECTIVE_SUFFIXES_PL:
        if w.endswith(suf) and len(w) > len(suf) + 2:
            return "adjective"
    # Polish adverb suffixes
    for suf in _ADVERB_SUFFIXES_PL:
        if w.endswith(suf) and len(w) > len(suf) + 2:
            return "adverb"
    # Polish verb suffixes
    for suf in _VERB_SUFFIXES_PL:
        if w.endswith(suf) and len(w) > len(suf) + 1:
            return "verb"
    # English: -ly adverbs
    if w.endswith("ly") and len(w) > 4:
        return "adverb"
    # English: -ed, -ing, -s verbs (rough)
    if re.match(r'.+(?:ing|ed|es|ied)$', w) and len(w) > 4:
        return "verb"
    # Capitalised → likely proper noun
    if word[0].isupper():
        return "proper_noun"
    return "noun"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _extract_concepts(text: str) -> list[str]:
    words = re.findall(r'[a-ząćęłńóśźżA-ZĄĆĘŁŃÓŚŹŻ]{4,}', text.lower())
    return [w for w in words if w not in _STOP_WORDS]


def _extract_features(text: str) -> list[str]:
    """Extract adjective-class tokens."""
    words = re.findall(r'[a-ząćęłńóśźżA-ZĄĆĘŁŃÓŚŹŻ]{4,}', text)
    return [w for w in words if _pos_tag(w) in ("adjective",) and w.lower() not in _STOP_WORDS]


def _extract_closureops(text: str) -> list[str]:
    """Extract adverb-class tokens."""
    words = re.findall(r'[a-ząćęłńóśźżA-ZĄĆĘŁŃÓŚŹŻ]{4,}', text)
    return [w for w in words if _pos_tag(w) == "adverb" and w.lower() not in _STOP_WORDS]


def _cyclic_dist(a: float, b: float) -> float:
    diff = (a - b + math.pi) % (2 * math.pi) - math.pi
    return abs(diff)


def _circular_mean_std(phis: list[float]) -> tuple[float, float]:
    if not phis:
        return 0.0, 0.0
    n = len(phis)
    z = sum(cmath.exp(1j * p) for p in phis) / n
    mean = float(cmath.phase(z)) % (2 * math.pi)
    R = abs(z)
    std = float(math.sqrt(-2 * math.log(max(R, 1e-9))))
    return mean, std


def _semantic_mass(freq: int, closure_mean: float,
                   winding_mean: float, phase_std: float) -> float:
    stability = math.exp(-phase_std)
    return freq * closure_mean * math.log1p(winding_mean) * stability


# ── Build ObjectCards ─────────────────────────────────────────────────────────

def build_cards(db_path: Path | None = None,
                min_freq: int = 5,
                top_concepts: int = 200) -> dict[str, ObjectCard]:
    """Build ObjectCard dict from live TSM. O(top_concepts²) for W_ij."""
    if db_path is None:
        db_path = _DEFAULT_DB

    with sqlite3.connect(str(db_path), timeout=20) as conn:
        rows = conn.execute("""
            SELECT memorise_id, D_sense, phi_berry, closure_score, winding_n
            FROM memories
            WHERE phi_berry IS NOT NULL AND D_sense IS NOT NULL
        """).fetchall()

    if not rows:
        return {}

    concept_entries: dict[str, list[tuple]] = defaultdict(list)
    for mid, d_sense, phi, clos, wind in rows:
        phi  = float(phi  or 0.0)
        clos = float(clos or 0.5)
        wind = int(wind   or 0)
        for c in set(_extract_concepts(d_sense or "")):
            concept_entries[c].append((phi, clos, wind, mid))

    freq_sorted = sorted(concept_entries.items(), key=lambda x: len(x[1]), reverse=True)
    selected = [(c, e) for c, e in freq_sorted if len(e) >= min_freq][:top_concepts]
    if not selected:
        return {}
    selected_names = {c for c, _ in selected}

    cards: dict[str, ObjectCard] = {}
    concept_ids: dict[str, set[str]] = {}

    for concept, entries in selected:
        phis  = [e[0] for e in entries]
        clos  = [e[1] for e in entries]
        winds = [e[2] for e in entries]
        ids   = {e[3] for e in entries}

        n = len(entries)
        phi_mean, phi_std = _circular_mean_std(phis)
        clos_mean = sum(clos) / n
        wind_mean = sum(winds) / n
        mass      = _semantic_mass(n, clos_mean, wind_mean, phi_std)

        sector_idx = int((phi_mean / (2 * math.pi)) * len(SECTORS))
        sector = SECTORS[min(sector_idx, len(SECTORS) - 1)]

        cards[concept] = ObjectCard(
            concept=concept, phi_berry=phi_mean, phase_std=phi_std,
            sector=sector, freq=n, closure_mean=clos_mean,
            winding_mean=wind_mean, mass=mass,
        )
        concept_ids[concept] = ids

    max_mass = max(c.mass for c in cards.values()) or 1.0
    for c in cards.values():
        c.mass = c.mass / max_mass

    concept_list = list(cards.keys())
    k = len(concept_list)

    # ── Vectorized W_ij via numpy broadcasting (O(k²) numpy vs O(k²) Python) ──
    import numpy as _np
    phis_arr  = _np.array([cards[c].phi_berry for c in concept_list])
    mass_arr  = _np.array([cards[c].mass      for c in concept_list])

    # Phase affinity matrix: cos(φ_i - φ_j)  shape (k, k)
    phase_aff_mat = _np.cos(phis_arr[:, None] - phis_arr[None, :])

    # Jaccard matrix: computed entry-by-entry (set ops can't be vectorised)
    # but precompute sizes to speed inner loop
    id_list = [concept_ids[c] for c in concept_list]
    id_sizes = _np.array([len(s) for s in id_list])

    jaccard_mat = _np.zeros((k, k), dtype=_np.float32)
    for i in range(k):
        for j in range(i + 1, k):
            inter = len(id_list[i] & id_list[j])
            if inter > 0:
                union = id_sizes[i] + id_sizes[j] - inter
                jac = inter / union
                jaccard_mat[i, j] = jac
                jaccard_mat[j, i] = jac

    sym_base_mat = 0.35 * phase_aff_mat + 0.65 * jaccard_mat - 0.5  # (k,k)

    # Keplerian asymmetry: mass_ratio[i,j] = mass_j / (mass_i + mass_j)
    mass_sum = mass_arr[:, None] + mass_arr[None, :] + 1e-9           # (k,k)
    mass_ratio_mat = mass_arr[None, :] / mass_sum                     # (k,k)

    W_mat = sym_base_mat * (0.5 + mass_ratio_mat)                     # (k,k)
    _np.fill_diagonal(W_mat, 0.0)

    for i in range(k):
        ci = concept_list[i]
        row = W_mat[i]
        cards[ci].W_ij = {
            concept_list[j]: round(float(row[j]), 4)
            for j in range(k) if i != j and abs(row[j]) > 0.04
        }

    ab_delta = math.pi / 4
    for i in range(k):
        ci = concept_list[i]
        phi_i = cards[ci].phi_berry
        ids_i = concept_ids[ci]
        ab: dict[str, float] = {}

        for j in range(i + 1, k):
            cj = concept_list[j]
            phi_j = cards[cj].phi_berry
            ids_j = concept_ids[cj]

            if len(ids_i & ids_j) > 0:
                continue

            arc = _cyclic_dist(phi_i, phi_j)
            if arc > math.pi / 2:
                continue

            phi_mid = (phi_i + phi_j) / 2
            mediator_found = False
            for ck in concept_list:
                if ck in (ci, cj):
                    continue
                phi_k = cards[ck].phi_berry
                ids_k = concept_ids[ck]
                if (_cyclic_dist(phi_k, phi_mid) < ab_delta
                        and len(ids_i & ids_k) > 0
                        and len(ids_j & ids_k) > 0):
                    mediator_found = True
                    break

            if mediator_found:
                ab_weight = round(math.exp(-arc / math.pi) * 0.5, 4)
                ab[cj] = ab_weight
                cards[cj].ab_links[ci] = ab_weight

        cards[ci].ab_links.update(ab)

    return cards


# ── Build FeatureCards ────────────────────────────────────────────────────────

def build_features(db_path: Path | None = None,
                   min_freq: int = 3,
                   top_features: int = 100,
                   object_cards: dict | None = None) -> dict[str, FeatureCard]:
    """Extract adjective-class tokens from TSM and build FeatureCards.

    FeatureCards have no own mass but carry phase from their co-occurring objects.
    binding_strength = mean(W_ij strength with co-occurring ObjectCards).
    polarity = sign of mean valence shift (do they co-occur with high/low-W_S entries).
    """
    if db_path is None:
        db_path = _DEFAULT_DB

    if object_cards is None:
        object_cards = get_cards(db_path)

    with sqlite3.connect(str(db_path), timeout=20) as conn:
        rows = conn.execute("""
            SELECT D_sense, phi_berry, W_S
            FROM memories
            WHERE phi_berry IS NOT NULL AND D_sense IS NOT NULL
        """).fetchall()

    if not rows:
        return {}

    feature_entries: dict[str, list[tuple[float, float]]] = defaultdict(list)
    feature_coobj: dict[str, list[str]] = defaultdict(list)

    for d_sense, phi, w_s in rows:
        phi = float(phi or 0.0)
        w_s = float(w_s or 0.5)
        features = _extract_features(d_sense or "")
        concepts  = set(_extract_concepts(d_sense or ""))
        for feat in set(features):
            feature_entries[feat].append((phi, w_s))
            for c in concepts:
                if c in object_cards:
                    feature_coobj[feat].append(c)

    freq_sorted = sorted(feature_entries.items(), key=lambda x: len(x[1]), reverse=True)
    selected = [(f, e) for f, e in freq_sorted if len(e) >= min_freq][:top_features]

    feature_cards: dict[str, FeatureCard] = {}
    for feat, entries in selected:
        phis = [e[0] for e in entries]
        ws   = [e[1] for e in entries]
        phi_mean, _ = _circular_mean_std(phis)
        mean_ws = sum(ws) / len(ws)
        polarity = +1.0 if mean_ws >= 0.5 else -1.0

        # binding_strength: mean W_ij of co-occurring objects toward each other
        bound = list(dict.fromkeys(feature_coobj[feat]))[:8]
        binding = 0.2  # default
        if len(bound) >= 2:
            strengths = []
            for ci in bound:
                for cj in bound:
                    if ci != cj and cj in object_cards[ci].W_ij:
                        strengths.append(abs(object_cards[ci].W_ij[cj]))
            if strengths:
                binding = min(1.0, sum(strengths) / len(strengths) * 2)

        sector_idx = int((phi_mean / (2 * math.pi)) * len(SECTORS))
        sector = SECTORS[min(sector_idx, len(SECTORS) - 1)]

        feature_cards[feat] = FeatureCard(
            feature=feat, phi_berry=phi_mean,
            binding_strength=round(binding, 4),
            polarity=polarity,
            sector=sector,
            freq=len(entries),
            bound_to=bound,
        )

    return feature_cards


# ── Build ClosureOps ──────────────────────────────────────────────────────────

def build_closure_ops(db_path: Path | None = None,
                      min_freq: int = 3,
                      top_ops: int = 60) -> dict[str, ClosureOp]:
    """Extract adverb-class tokens and map them to orbital trajectory modifiers.

    closure_shift: if entry with this adverb has closure_score > global mean → positive
    winding_bias: fraction of entries with this adverb that have winding_n > 0
    speed_factor: ratio of entry count per orbital cycle vs baseline
    """
    if db_path is None:
        db_path = _DEFAULT_DB

    with sqlite3.connect(str(db_path), timeout=20) as conn:
        rows = conn.execute("""
            SELECT D_sense, phi_berry, closure_score, winding_n
            FROM memories
            WHERE phi_berry IS NOT NULL AND D_sense IS NOT NULL
        """).fetchall()
        global_mean_clos = conn.execute(
            "SELECT AVG(closure_score) FROM memories WHERE closure_score IS NOT NULL"
        ).fetchone()[0] or 0.5

    adverb_entries: dict[str, list[tuple]] = defaultdict(list)
    for d_sense, phi, clos, wind in rows:
        phi  = float(phi  or 0.0)
        clos = float(clos or 0.5)
        wind = int(wind   or 0)
        for adv in set(_extract_closureops(d_sense or "")):
            adverb_entries[adv].append((phi, clos, wind))

    freq_sorted = sorted(adverb_entries.items(), key=lambda x: len(x[1]), reverse=True)
    selected = [(a, e) for a, e in freq_sorted if len(e) >= min_freq][:top_ops]

    ops: dict[str, ClosureOp] = {}
    for adv, entries in selected:
        phis  = [e[0] for e in entries]
        closs = [e[1] for e in entries]
        winds = [e[2] for e in entries]

        phi_mean, _ = _circular_mean_std(phis)
        mean_clos = sum(closs) / len(closs)
        closure_shift = float(mean_clos - global_mean_clos)
        winding_bias  = sum(1 for w in winds if w > 0) / len(winds)
        # speed_factor: more closures per entry → faster traversal
        speed_factor = max(0.1, mean_clos / max(float(global_mean_clos), 0.01))

        sector_idx = int((phi_mean / (2 * math.pi)) * len(SECTORS))
        sector = SECTORS[min(sector_idx, len(SECTORS) - 1)]

        ops[adv] = ClosureOp(
            adverb=adv, phi_berry=phi_mean,
            closure_shift=round(closure_shift, 4),
            winding_bias=round(winding_bias, 4),
            speed_factor=round(speed_factor, 4),
            sector=sector,
            freq=len(entries),
        )
    return ops


# ── AffectCard detection ──────────────────────────────────────────────────────

def affect_of(text: str) -> list[AffectCard]:
    """Detect AffectCards present in text. Returns list sorted by match strength."""
    lowered = text.lower()
    matched: list[tuple[float, AffectCard]] = []
    for ac in _AFFECT_REGISTRY:
        hits = sum(1 for kw in ac.keywords_pl + ac.keywords_en if kw in lowered)
        if hits > 0:
            strength = hits / max(len(ac.keywords_pl) + len(ac.keywords_en), 1)
            matched.append((strength, ac))
    return [ac for _, ac in sorted(matched, key=lambda x: x[0], reverse=True)]


def get_affects() -> dict[str, AffectCard]:
    return _AFFECT_MAP


# ── SentenceEquation parser ───────────────────────────────────────────────────

def parse_sentence(text: str,
                   cards: dict | None = None) -> SentenceEquation:
    """Parse a sentence into a SentenceEquation (phase transformation).

    Every sentence = φ_result = f(φ_subject, OP, φ_predicate, affect).

    Operator selection heuristic:
      - negation present         → "−"
      - question mark            → "∂"
      - exclamation              → "×"
      - explicit loop reference  → "∮"
      - copula (jest/is/are)     → "≡"
      - causal marker            → "→"
      - nonlocal/entanglement kw → "⊗"
      - default                  → "+"

    φ_subject/φ_predicate from ObjectCard lookup or grammatical_phase_bias fallback.
    φ_result = circular_mean(φ_s + op_shift, φ_p + affect_bias)
    """
    if cards is None:
        cards = get_cards()

    tokens_raw = re.findall(r'[a-ząćęłńóśźżA-ZĄĆĘŁŃÓŚŹŻ]+', text)
    tokens = [t for t in tokens_raw if len(t) >= 3]

    # POS classification
    nouns, verbs, adjectives, adverbs, negations = [], [], [], [], []
    for t in tokens:
        pos = _pos_tag(t)
        if pos in ("noun", "proper_noun"):
            nouns.append(t.lower())
        elif pos == "verb":
            verbs.append(t.lower())
        elif pos == "adjective":
            adjectives.append(t.lower())
        elif pos == "adverb":
            adverbs.append(t.lower())
        elif pos == "negation":
            negations.append(t.lower())

    negated = len(negations) > 0

    # Subject = first noun (or concept with highest mass)
    subject = None
    phi_s = GRAMMATICAL_PHASE_BIAS["subject"]
    if nouns:
        for candidate in nouns[:3]:
            if candidate in cards:
                subject = candidate
                phi_s = cards[candidate].phi_berry
                break
        if subject is None:
            subject = nouns[0]

    # Predicate = first verb + following noun, or second noun
    predicate = None
    phi_p = GRAMMATICAL_PHASE_BIAS["predicate"]
    if verbs:
        predicate = verbs[0]
        phi_p = phi_s + GRAMMATICAL_PHASE_BIAS["predicate"]
    elif len(nouns) > 1:
        predicate = nouns[1]
        if predicate in cards:
            phi_p = cards[predicate].phi_berry

    objects  = [n for n in nouns[1:] if n != predicate][:4]
    modifiers = adjectives[:4] + adverbs[:4]

    # Affect detection
    affects = affect_of(text)
    affect_names = [a.name for a in affects[:3]]
    total_affect_bias = sum(a.phase_bias for a in affects[:3])
    total_closure_cost = sum(a.closure_cost for a in affects[:3])

    # Operator selection
    text_lower = text.lower()
    # "to" as copula only when it appears as NOUN to NOUN bridge (not in subordinate clause)
    # Pattern: "[word] to [word]" at start or after comma — not "że to", "ale to", "jak to"
    _to_copula = bool(re.search(r'(?:^|,\s*)\w+\s+to\s+\w', text_lower)) and \
                 not re.search(r'(?:że|ale|jak|czy|jeśli|kiedy)\s+to\b', text_lower)
    _other_copula = any(cw in text_lower for cw in (_COPULA_WORDS - {"to"}))
    copula_present = _to_copula or _other_copula
    loop_markers = ["powraca","wraca","zamknie","domknięcie","z powrotem","again","return","loop"]
    causal_markers = ["dlatego","więc","zatem","ponieważ","because","therefore","thus","hence"]
    # "bo" excluded — too ambiguous (also "ale bo", contrast contexts)
    entangle_markers = ["nielokalnie","nielokalna","nielokalny","splątana","splątany","splatany",
                        "korelacja","jednocześnie","nonlocal","entangl","spleciona"]

    # Operator priority: structural markers override affect operators
    # Affect operators are only used when NO structural marker is present
    # AND the dominant affect has high closure_cost (unambiguous rhetorical function)
    # Cumulative affect cost — sum over top-3 detected affects
    cumulative_affect_cost = sum(a.closure_cost for a in affects[:3])
    # Dominant affect op: from highest-cost affect with non-trivial operator
    dominant_affect_op = "+"
    for a in sorted(affects[:3], key=lambda x: x.closure_cost, reverse=True):
        if a.sentence_op not in ("+", "→"):
            dominant_affect_op = a.sentence_op
            break

    if negated:
        op = "−"
    elif "?" in text:
        op = "∂"
    elif "!" in text:
        op = "×"
    elif any(m in text_lower for m in loop_markers):
        op = "∮"
    elif any(m in text_lower for m in entangle_markers):
        op = "⊗"
    elif any(m in text_lower for m in causal_markers):
        op = "→"
    elif copula_present and cumulative_affect_cost < 0.35:
        # Copula only wins if no strong affect present
        op = "≡"
    elif cumulative_affect_cost >= 0.30 and dominant_affect_op != "+":
        # Strong affect overrides weak structural markers
        op = dominant_affect_op
    elif copula_present:
        op = "≡"
    else:
        op = "+"

    # φ_result computation per operator
    op_shifts = {
        "+":  0.0,
        "−":  math.pi,        # negation flips
        "×":  0.0,            # amplifies but doesn't shift phase
        "→":  math.pi / 4,    # causal: slight forward shift
        "⊗":  math.pi / 2,    # entanglement: orthogonal
        "≡":  0.0,            # identity: same phase
        "∂":  math.pi / 3,    # partial: moderate shift
        "∮":  0.0,            # loop: returns to φ_subject
    }
    op_shift = op_shifts.get(op, 0.0)

    if op == "∮":
        phi_result = phi_s  # loop: always returns to subject
    elif op == "≡":
        phi_result = (phi_s + phi_p) / 2  # identity: mean
    else:
        # Circular mean of shifted phases + affect bias
        z = (cmath.exp(1j * (phi_s + op_shift)) + cmath.exp(1j * (phi_p + op_shift))) / 2
        phi_result = float(cmath.phase(z)) % (2 * math.pi)

    # Affect phase bias added to result
    phi_result = (phi_result + total_affect_bias) % (2 * math.pi)

    # is_loop: True when subject concept appears in object list or predicate
    is_loop = (op == "∮") or (subject is not None and (
        subject in objects or subject == predicate
        or (predicate is not None and predicate in cards
            and subject in cards
            and _cyclic_dist(cards[subject].phi_berry, cards[predicate].phi_berry) < 0.3)
    ))

    return SentenceEquation(
        text=text,
        subject=subject,
        predicate=predicate,
        objects=objects,
        modifiers=modifiers,
        negated=negated,
        op=op,
        phi_subject=round(phi_s % (2 * math.pi), 4),
        phi_predicate=round(phi_p % (2 * math.pi), 4),
        phi_result=round(phi_result, 4),
        affect=affect_names,
        closure_cost=round(total_closure_cost, 4),
        is_loop=is_loop,
    )


# ── Cache + API ───────────────────────────────────────────────────────────────

def get_cards(db_path: Path | None = None,
              force: bool = False) -> dict[str, ObjectCard]:
    global _CACHE, _CACHE_AT
    if not force and _CACHE is not None and (time.time() - _CACHE_AT) < _CACHE_TTL:
        return _CACHE
    _CACHE = build_cards(db_path)
    _CACHE_AT = time.time()
    return _CACHE


def get_features(db_path: Path | None = None,
                 force: bool = False) -> dict[str, FeatureCard]:
    global _FEATURE_CACHE, _FEATURE_CACHE_AT
    if not force and _FEATURE_CACHE is not None and (time.time() - _FEATURE_CACHE_AT) < _CACHE_TTL:
        return _FEATURE_CACHE
    _FEATURE_CACHE = build_features(db_path)
    _FEATURE_CACHE_AT = time.time()
    return _FEATURE_CACHE


def related(concept: str, n: int = 10,
            cards: dict | None = None) -> list[tuple[str, float]]:
    if cards is None:
        cards = get_cards()
    card = cards.get(concept.lower())
    if card is None:
        return []
    pos = [(k, v) for k, v in card.W_ij.items() if v > 0]
    return sorted(pos, key=lambda x: x[1], reverse=True)[:n]


def opposites(concept: str, n: int = 5,
              cards: dict | None = None) -> list[tuple[str, float]]:
    if cards is None:
        cards = get_cards()
    card = cards.get(concept.lower())
    if card is None:
        return []
    neg = [(k, v) for k, v in card.W_ij.items() if v < 0]
    return sorted(neg, key=lambda x: x[1])[:n]


def phase_neighbors(phi: float, n: int = 10,
                    cards: dict | None = None) -> list[tuple[str, float]]:
    if cards is None:
        cards = get_cards()
    scored = [(name, _cyclic_dist(card.phi_berry, phi))
              for name, card in cards.items()]
    return sorted(scored, key=lambda x: x[1])[:n]


def attractors(n: int = 10,
               cards: dict | None = None) -> list[tuple[str, float]]:
    if cards is None:
        cards = get_cards()
    return sorted([(name, card.mass) for name, card in cards.items()],
                  key=lambda x: x[1], reverse=True)[:n]


def adaptive_delta(phi: float, delta_base: float,
                   cards: dict | None = None) -> float:
    """Kepler second law: δ(φ) = δ_base / sqrt(local_density)."""
    if cards is None:
        cards = get_cards()
    local_mass = sum(
        card.mass for card in cards.values()
        if _cyclic_dist(card.phi_berry, phi) < delta_base
    )
    density = local_mass / max(len(cards), 1)
    return delta_base / math.sqrt(max(density * 10, 0.1))


def process_and_stamp(text: str,
                      cards: dict | None = None) -> dict:
    """Parse sentence → SentenceEquation → return phase stamp dict.

    This is the pipeline entry point that activates the grammar-as-physics model.
    Call this before/during TSM write to enrich entries with sentence-level phase data.

    Returns metadata dict ready to inject into phase_metadata / TSM extra fields.
    If hm (HolonomicMemory) is provided and phi_result is defined, writes a
    sentence-typed entry to TSM.
    """
    eq = parse_sentence(text, cards=cards)
    stamp = {
        "sentence_op":       eq.op,
        "phi_subject":       eq.phi_subject,
        "phi_predicate":     eq.phi_predicate,
        "phi_result":        eq.phi_result,
        "affect":            eq.affect,
        "closure_cost":      eq.closure_cost,
        "is_loop":           eq.is_loop,
        "negated":           eq.negated,
        "subject":           eq.subject,
        "predicate":         eq.predicate,
    }
    # hm write reserved for future — stamp_new() requires pre-existing TSM entry.
    # Callers that hold a memorise_id can call hm.stamp_new(mid, phi_berry=stamp["phi_result"]).
    return stamp
