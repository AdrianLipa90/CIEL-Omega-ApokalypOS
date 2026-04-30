#!/usr/bin/env python3
"""Build word cards registry from docs/object_cards/words/*.md

Generates:
  integration/registries/words/word_cards_registry.json
  integration/registries/words/word_semantic_edges.json
"""
import json
import re
import sys
from pathlib import Path

PROJECT = Path(__file__).parent.parent
WORDS_DIR = PROJECT / "docs" / "object_cards" / "words"
OUT_DIR = PROJECT / "integration" / "registries" / "words"


def parse_word_card(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    card = {"card_id": path.stem, "source_file": str(path.relative_to(PROJECT))}

    # Title line: # WORD-XX-0001 — name
    if lines and lines[0].startswith("#"):
        m = re.match(r"#\s+(WORD-\S+)\s+[—–-]+\s+(.+)", lines[0])
        if m:
            card["card_id"] = m.group(1)
            card["name"] = m.group(2).strip()

    def get_field(key: str) -> str:
        for line in lines:
            m = re.match(rf"^\s*-\s+{re.escape(key)}:\s+(.+)", line)
            if m:
                return m.group(1).strip()
        return ""

    def get_list_field(key: str) -> list:
        raw = get_field(key)
        if not raw:
            return []
        raw = raw.strip("[]")
        return [x.strip().strip("'\"") for x in raw.split(",") if x.strip()]

    for f in ["language", "semantic_class", "root_meaning", "resonance_orbit",
              "berry_phase_signature", "origin", "root"]:
        v = get_field(f)
        if v:
            card[f] = v

    card["semantic_tags"] = get_list_field("semantic_tags")

    # translations: collect lang→value pairs (skip WORD-* refs, keep plain words)
    translations = {}
    in_translations = False
    for line in lines:
        if line.strip() == "## Translations":
            in_translations = True
            continue
        if in_translations and line.startswith("##"):
            break
        if in_translations:
            m = re.match(r"^\s*-\s+(\w+):\s+(.+)", line)
            if m:
                lang, val = m.group(1), m.group(2).strip()
                translations[lang] = val
    card["translations"] = translations

    # relations
    for rel in ["synonyms", "antonyms", "hyponyms", "kanji_components", "composed_into"]:
        card[rel] = get_list_field(rel)
    card["hypernym"] = get_field("hypernym")

    # translation edges: links to WORD-* cards
    translation_links = [v for v in translations.values() if v.startswith("WORD-")]
    card["translation_card_links"] = translation_links

    return card


def build_edges(cards: list[dict]) -> list[dict]:
    edges = []
    seen = set()

    def add_edge(src, tgt, rel, weight=1.0):
        key = (src, tgt, rel)
        if key not in seen and src != tgt:
            seen.add(key)
            edges.append({"source": src, "target": tgt, "relation": rel, "weight": weight})

    for card in cards:
        cid = card["card_id"]
        for link in card.get("translation_card_links", []):
            add_edge(cid, link, "translation", 1.0)
            add_edge(link, cid, "translation", 1.0)
        for syn in card.get("synonyms", []):
            if syn.startswith("WORD-"):
                add_edge(cid, syn, "synonym", 0.9)
        for ant in card.get("antonyms", []):
            if ant.startswith("WORD-"):
                add_edge(cid, ant, "antonym", 0.5)
        for hypo in card.get("hyponyms", []):
            if hypo.startswith("WORD-"):
                add_edge(cid, hypo, "hyponym", 0.7)
        if card.get("hypernym", "").startswith("WORD-"):
            add_edge(cid, card["hypernym"], "hypernym", 0.7)
        for comp in card.get("kanji_components", []):
            if comp.startswith("WORD-"):
                add_edge(cid, comp, "kanji_component", 0.8)

    return edges


def update_index(cards: list[dict]) -> None:
    index_path = WORDS_DIR / "INDEX.md"
    rows = []
    for c in sorted(cards, key=lambda x: x["card_id"]):
        tags = ", ".join(c.get("semantic_tags", [])[:3])
        rows.append(f"| {c['card_id']} | {c.get('name','')} | {c.get('language','')} | {tags} |")

    content = (
        "# Word Cards Index\n\n"
        "> Karty semantyczne słów — system Starlight.\n"
        "> Format: WORD-{LANG}-{XXXX} — każda karta to węzeł w sieci znaczeń.\n"
        "> Relacje: translations, synonyms, hypernym/hyponyms, kanji_components.\n\n"
        "## words\n\n"
        "| card_id | name | language | semantic_tags |\n"
        "|---------|------|----------|---------------|\n"
        + "\n".join(rows) + "\n"
    )
    index_path.write_text(content, encoding="utf-8")


def main():
    if not WORDS_DIR.exists():
        print(f"[ERROR] {WORDS_DIR} does not exist", file=sys.stderr)
        sys.exit(1)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    cards = []
    for md in sorted(WORDS_DIR.glob("*.md")):
        if md.name == "INDEX.md":
            continue
        card = parse_word_card(md)
        cards.append(card)
        print(f"  parsed: {card['card_id']} — {card.get('name', '?')}")

    edges = build_edges(cards)

    registry = {
        "schema": "ciel/word-cards-registry/v0.1",
        "count": len(cards),
        "cards": cards,
    }
    edges_out = {
        "schema": "ciel/word-semantic-edges/v0.1",
        "count": len(edges),
        "edges": edges,
    }

    (OUT_DIR / "word_cards_registry.json").write_text(
        json.dumps(registry, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_DIR / "word_semantic_edges.json").write_text(
        json.dumps(edges_out, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    update_index(cards)

    print(f"\n[OK] {len(cards)} cards, {len(edges)} edges")
    print(f"     → {OUT_DIR}/word_cards_registry.json")
    print(f"     → {OUT_DIR}/word_semantic_edges.json")


if __name__ == "__main__":
    main()
