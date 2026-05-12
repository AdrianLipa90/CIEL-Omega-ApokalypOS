from pathlib import Path
import json
import sqlite3
import yaml

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / 'data' / 'concept_cards' / 'batch01_foundational_36x5'


def test_batch01_has_36_cards_and_5_languages():
    index = yaml.safe_load((BATCH / 'batch01_index.yaml').read_text(encoding='utf-8'))
    assert index['batch']['concept_count'] == 36
    assert index['batch']['languages'] == ['pl', 'en', 'de', 'fr', 'es']
    assert len(index['cards']) == 36
    for card in index['cards']:
        assert card['card_type'] == 'CONCEPT_CARD'
        assert set(card['languages'].keys()) == {'pl', 'en', 'de', 'fr', 'es'}
        assert card['operator_hooks']


def test_function_words_are_not_batch_concepts():
    index = yaml.safe_load((BATCH / 'batch01_index.yaml').read_text(encoding='utf-8'))
    labels = {card['canonical_label_en'] for card in index['cards']}
    forbidden = {'inside', 'contains', 'have', 'not', 'and', 'or', 'if', 'then', 'how', 'as', 'like'}
    assert labels.isdisjoint(forbidden)


def test_sqlite_batch_counts():
    db = ROOT / 'data' / 'sqlite' / 'cielingo_batch01_v1_0.sqlite'
    assert db.exists()
    conn = sqlite3.connect(db)
    try:
        cur = conn.cursor()
        assert cur.execute('select count(*) from concepts').fetchone()[0] == 36
        assert cur.execute('select count(*) from language_panels').fetchone()[0] == 180
        assert cur.execute('select count(*) from operator_links').fetchone()[0] >= 100
    finally:
        conn.close()


def test_graph_artifacts_exist():
    assert (ROOT / 'data' / 'graphs' / 'batch01_concept_operator_graph.json').exists()
    assert (ROOT / 'data' / 'graphs' / 'batch01_concept_operator_graph.graphml').exists()
    assert (ROOT / 'outputs' / 'heatmaps' / 'batch01_concept_operator_incidence.png').exists()
    assert (ROOT / 'outputs' / 'heatmaps' / 'batch01_grammar_gauge_distance.png').exists()
