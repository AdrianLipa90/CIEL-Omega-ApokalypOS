# 07. Data Ingestion: PWN, Oxford and Open Lexical Sources

## Rule zero

Do not scrape or redistribute proprietary dictionary content unless the license explicitly permits it.

## PWN

PWN dictionaries are high-quality Polish lexical sources, but their data should be treated as proprietary unless a written license or approved API/export says otherwise.

Use pattern:

```text
data/external/pwn/          ignored by Git
configs/sources/pwn.yaml    metadata only
src/adapters/pwn_adapter.py local/licensed adapter only
```

## Oxford

Oxford Dictionaries data should be accessed through the official Oxford Dictionaries API or another licensed Oxford Languages/OUP channel.

Use pattern:

```text
data/external/oxford/           ignored by Git
configs/sources/oxford.yaml     API metadata only
src/adapters/oxford_adapter.py  licensed adapter only
```

## Open bootstrap alternatives

Recommended for first implementation:

- Open English WordNet for English synsets and relations.
- Princeton WordNet where compatible.
- plWordNet/Słowosieć for Polish synsets and relations.
- Universal Dependencies treebanks for POS/dependency calibration.
- Wiktionary dumps for multilingual lexical hints, with strict license handling.

## Import target format

Every lexical entry should normalize to:

```yaml
id: string
language: en|pl
lemma: string
surface_forms: []
pos: NOUN|VERB|ADJ|ADV|...
definitions: []
synsets: []
relations: []
axes: {}
phase: {}
semantic_mass: {}
provenance: {}
license: {}
audit: []
```

## Derived features

Do not assume derived vectors are legally safe. Some licenses treat derived databases as derivative works. Keep a provenance trail and separate proprietary-derived artifacts from open redistributable artifacts.
