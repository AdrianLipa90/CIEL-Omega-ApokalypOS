#!/usr/bin/env python3
"""
CIEL Graph Extractor — draft/experimental

Wyciąga podmioty i relacje z artykułów RSS i aktualizuje NEWS/GRAPH.md + subjects/*.md.

Słownik znaczeń, nie prawdopodobieństw:
  - węzeł = podmiot (państwo, osoba, organizacja, koncepcja)
  - krawędź = relacja (CONFLICT_WITH, ALLIED_WITH, NEGOTIATES_WITH, CAUSES, itd.)
  - waga krawędzi = liczba co-occurrence + typ relacji

EXPERIMENTAL = True  — nie wchodzi do pipeline bez walidacji.

Użycie:
    python ciel_graph_extractor.py --input NEWS/2026-04-15.AM.md
    python ciel_graph_extractor.py --live   # pobierz świeże RSS i wyciągnij
"""
from __future__ import annotations

EXPERIMENTAL = True

import argparse
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import NamedTuple

NEWS_DIR = Path.home() / "Pulpit/NEWS"
SUBJECTS_DIR = NEWS_DIR / "subjects"
GRAPH_FILE   = NEWS_DIR / "GRAPH.md"


# ── Słownik podmiotów (seed — rozszerzaj) ────────────────────────────────────

KNOWN_ENTITIES: dict[str, str] = {
    # Państwa
    "israel": "state", "israeli": "state",
    "iran": "state", "iranian": "state",
    "lebanon": "state", "lebanese": "state",
    "sudan": "state", "sudanese": "state",
    "usa": "state", "united states": "state", "america": "state", "american": "state",
    "russia": "state", "russian": "state",
    "china": "state", "chinese": "state",
    "ukraine": "state", "ukrainian": "state",
    "germany": "state", "german": "state",
    "france": "state", "french": "state",
    "poland": "state", "polish": "state",
    "turkey": "state", "turkish": "state",
    "saudi arabia": "state", "saudi": "state",
    "pakistan": "state", "pakistani": "state",
    "india": "state", "indian": "state",
    "north korea": "state",
    "south korea": "state",
    "syria": "state", "syrian": "state",
    "gaza": "territory",
    "west bank": "territory",
    # Organizacje
    "hamas": "org", "hezbollah": "org",
    "nato": "org", "eu": "org", "european union": "org",
    "un": "org", "united nations": "org",
    "iaea": "org", "who": "org", "imf": "org",
    "anthropic": "org", "openai": "org",
    # Koncepcje geopolityczne
    "g7": "org", "g20": "org", "brics": "org",
}

# Słownik relacji — wzorce słów kluczowych
RELATION_PATTERNS: list[tuple[str, list[str]]] = [
    ("CONFLICT_WITH",    ["war", "attack", "bomb", "missile", "strike", "killed", "conflict",
                          "fighting", "battle", "invasion", "offensive", "troops"]),
    ("NEGOTIATES_WITH",  ["talks", "negotiations", "deal", "agreement", "treaty", "ceasefire",
                          "diplomatic", "meeting", "summit"]),
    ("ALLIED_WITH",      ["ally", "alliance", "partner", "support", "backed", "coalition"]),
    ("SANCTIONS",        ["sanction", "embargo", "banned", "restricted", "tariff"]),
    ("AID_TO",           ["aid", "relief", "assistance", "humanitarian", "donation"]),
    ("ACCUSED_OF",       ["accused", "charged", "alleged", "misconduct", "corruption", "fraud"]),
    ("CAUSES",           ["cause", "trigger", "lead to", "result in", "response to"]),
    ("THREATENS",        ["threat", "warn", "ultimatum", "escalat"]),
]


# ── Typy ─────────────────────────────────────────────────────────────────────

class Entity(NamedTuple):
    name: str
    kind: str


class Relation(NamedTuple):
    source: str
    target: str
    rel_type: str
    evidence: str   # fragment tekstu
    date: str


# ── Ekstrakcja podmiotów ──────────────────────────────────────────────────────

def extract_entities(text: str) -> list[Entity]:
    """Wyciąga znane podmioty z tekstu."""
    found: dict[str, str] = {}
    lower = text.lower()

    # Multi-word first (longer matches have priority)
    for key in sorted(KNOWN_ENTITIES.keys(), key=len, reverse=True):
        if key in lower and key not in found:
            # Normalize to canonical form (first word capitalized)
            canonical = key.title().replace(" Of ", " of ").replace(" The ", " the ")
            found[canonical] = KNOWN_ENTITIES[key]

    return [Entity(name=k, kind=v) for k, v in found.items()]


# ── Ekstrakcja relacji ────────────────────────────────────────────────────────

def extract_relations(text: str, entities: list[Entity], date: str) -> list[Relation]:
    """Wykrywa relacje między podmiotami na podstawie wzorców."""
    relations: list[Relation] = []
    entity_names = [e.name for e in entities]

    if len(entity_names) < 2:
        return relations

    lower = text.lower()
    sentences = re.split(r'[.!?]\s+', text)

    for sent in sentences:
        sent_lower = sent.lower()
        sent_entities = [e for e in entity_names if e.lower() in sent_lower]

        if len(sent_entities) < 2:
            continue

        # Wykryj typ relacji z wzorców
        detected_rel = "CO_OCCURS"
        for rel_type, keywords in RELATION_PATTERNS:
            if any(kw in sent_lower for kw in keywords):
                detected_rel = rel_type
                break

        # Dodaj relację dla każdej pary podmiotów w tym zdaniu
        for i, src in enumerate(sent_entities):
            for tgt in sent_entities[i+1:]:
                evidence = sent.strip()[:120]
                relations.append(Relation(src, tgt, detected_rel, evidence, date))

    return relations


# ── Aktualizacja plików grafu ─────────────────────────────────────────────────

def update_subject_file(entity: Entity, relations: list[Relation]) -> None:
    """Tworzy lub aktualizuje plik podmiotu w subjects/."""
    SUBJECTS_DIR.mkdir(parents=True, exist_ok=True)
    fname = entity.name.replace(" ", "_").replace("/", "-") + ".md"
    path = SUBJECTS_DIR / fname

    today = datetime.now().strftime("%Y-%m-%d")

    # Istniejące relacje
    existing_lines: list[str] = []
    existing_events: list[str] = []
    if path.exists():
        content = path.read_text(encoding="utf-8")
        in_rel = in_ev = False
        for line in content.splitlines():
            if "## Relacje" in line:
                in_rel, in_ev = True, False
            elif "## Zdarzenia" in line:
                in_rel, in_ev = False, True
            elif in_rel and line.startswith("- "):
                existing_lines.append(line)
            elif in_ev and line.startswith("- "):
                existing_events.append(line)

    # Nowe relacje (deduplicated by target+type)
    new_rel_map: dict[str, str] = {}
    for r in relations:
        other = r.target if r.source == entity.name else r.source
        key = f"{r.rel_type}:{other}"
        if key not in new_rel_map:
            new_rel_map[key] = f"- **{r.rel_type}**: {other} — _{r.evidence}_"

    # Merge existing + new
    all_rel_lines = list(dict.fromkeys(existing_lines + list(new_rel_map.values())))

    # Nowe zdarzenie
    new_event = f"- **{today}** — (z raportu RSS)"
    all_events = list(dict.fromkeys(existing_events + [new_event]))

    content = f"""# Podmiot: {entity.name}

```yaml
type: {entity.kind}
first_seen: {today}
last_updated: {today}
```

## Relacje

{chr(10).join(all_rel_lines) if all_rel_lines else "_(brak wykrytych relacji)_"}

## Zdarzenia

{chr(10).join(all_events[-20:])}
"""
    path.write_text(content, encoding="utf-8")


def update_graph_index(all_entities: list[Entity], all_relations: list[Relation]) -> None:
    """Aktualizuje GRAPH.md — indeks całego grafu."""
    today = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Deduplicate entities
    entity_map: dict[str, Entity] = {}
    for e in all_entities:
        entity_map[e.name] = e

    # Edges summary
    edge_counts: dict[tuple[str,str,str], int] = defaultdict(int)
    for r in all_relations:
        edge_counts[(r.source, r.rel_type, r.target)] += 1

    entity_rows = "\n".join(
        f"| {e.name} | {e.kind} | "
        f"[subjects/{e.name.replace(' ','_')}.md](subjects/{e.name.replace(' ','_')}.md) | {today} |"
        for e in sorted(entity_map.values(), key=lambda x: x.name)
    )

    top_edges = sorted(edge_counts.items(), key=lambda x: -x[1])[:20]
    edge_rows = "\n".join(
        f"| {src} | {rel} | {tgt} | {cnt} |"
        for (src, rel, tgt), cnt in top_edges
    )

    content = f"""# NEWS GRAPH — indeks podmiotów i relacji

*Aktualizacja automatyczna: {today}*

---

## Podmioty aktywne

| Podmiot | Typ | Plik | Ostatnia aktywność |
|---------|-----|------|--------------------|
{entity_rows}

## Top relacje (by frequency)

| Source | Relacja | Target | n |
|--------|---------|--------|---|
{edge_rows}

---
*CIEL Graph Extractor — słownik znaczeń i powiązań semantyczno-logicznych*
"""
    GRAPH_FILE.write_text(content, encoding="utf-8")


# ── Pipeline ──────────────────────────────────────────────────────────────────

def process_report(report_text: str, date: str) -> tuple[list[Entity], list[Relation]]:
    """Przetwarza tekst raportu, zwraca podmioty i relacje."""
    entities = extract_entities(report_text)
    relations = extract_relations(report_text, entities, date)
    return entities, relations


def run_live(count: int = 6) -> None:
    """Pobierz świeże RSS i wyciągnij graf na żywo."""
    import sys, os
    sys.path.insert(0, str(Path(__file__).parent))

    from ciel_news_reader import collect_articles, fetch_article_text

    print("[GRAPH] Pobieram artykuły...")
    articles = collect_articles(count=count, lang=None)

    all_entities: list[Entity] = []
    all_relations: list[Relation] = []
    date = datetime.now().strftime("%Y-%m-%d")

    for art in articles:
        text = f"{art.title} {art.summary}"
        if art.link:
            full = fetch_article_text(art.link)
            if full:
                text += " " + full

        ents, rels = process_report(text, date)
        all_entities.extend(ents)
        all_relations.extend(rels)

        if ents:
            print(f"  [{art.source}] {art.title[:60]}...")
            print(f"    Podmioty: {', '.join(e.name for e in ents)}")
            if rels:
                print(f"    Relacje:  {', '.join(f'{r.source}→{r.rel_type}→{r.target}' for r in rels[:3])}")

    # Aktualizuj pliki
    entity_map: dict[str, Entity] = {}
    for e in all_entities:
        entity_map[e.name] = e

    entity_relations: dict[str, list[Relation]] = defaultdict(list)
    for r in all_relations:
        entity_relations[r.source].append(r)
        entity_relations[r.target].append(r)

    for name, entity in entity_map.items():
        update_subject_file(entity, entity_relations[name])

    update_graph_index(list(entity_map.values()), all_relations)

    print(f"\n[GRAPH] Zaktualizowano:")
    print(f"  Podmioty: {len(entity_map)}")
    print(f"  Relacje:  {len(all_relations)}")
    print(f"  Pliki:    {SUBJECTS_DIR} + {GRAPH_FILE}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="CIEL Graph Extractor [EXPERIMENTAL]")
    parser.add_argument("--live",    action="store_true", help="Pobierz RSS i wyciągnij na żywo")
    parser.add_argument("--input",   type=str,            help="Plik .md raportu do przetworzenia")
    parser.add_argument("--count",   type=int, default=6, help="Liczba artykułów (--live)")
    args = parser.parse_args()

    print(f"[GRAPH] EXPERIMENTAL = {EXPERIMENTAL}")

    if args.live:
        run_live(count=args.count)
    elif args.input:
        p = Path(args.input)
        text = p.read_text(encoding="utf-8")
        date = datetime.now().strftime("%Y-%m-%d")
        ents, rels = process_report(text, date)
        print(f"Podmioty ({len(ents)}): {[e.name for e in ents]}")
        print(f"Relacje  ({len(rels)}): {[(r.source, r.rel_type, r.target) for r in rels[:10]]}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
