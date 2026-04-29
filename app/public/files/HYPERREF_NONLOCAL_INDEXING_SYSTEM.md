# HYPERREF NONLOCAL INDEXING SYSTEM

## Status
Robocza ekstrakcja z materiału źródłowego.

## Zakres
System hyperref / nonlocal / indexing wyciągnięty z:
- `Hyperspace_260328_072141.txt`
- `Formalizm_heatmap_crossref_semantyczny-1.md`
- `new_repo_artifacts_bundle_unpacked/05_NONLOCAL_CROSSREF_HEATMAP_FORMALISM.md`
- `new_repo_artifacts_bundle_unpacked/07_NEW_REPO_ARTIFACT_MAP.md`
- `new_repo_artifacts_bundle_unpacked/08_IMPLEMENTATION_PATH.md`
- `new_repo_artifacts_bundle_unpacked/10_CSV_SCHEMAS.md`
- `new_repo_artifacts_bundle_unpacked/14_STRICTE_KANDYDAT_BRAK.md`
- `szkic_unpacked/03_HIERARCHIA_OBIEKTOW.md`
- `na_brudno_bundle_unpacked/uploaded_project_txt/Plan refaktoryzacji.txt`
- `na_brudno_bundle_unpacked/docs/INDEX.md`
- `CIEL_UNIVERSAL_TEMPLATE/*` w sektorach `indexing/`, `governance/ids/`, `docs/maps/`, `README.md`, `INTEGRATION_METHOD.md`, `SOURCE_PRIORITY.md`
- `CIEL_Orbital_Foundation_Packk/*` w częściach registry / blueprint / plan
- `CIEL_RELATIONAL_MECHANISM_REPO/docs/*` w częściach tabelarycznych

---

## 1. Definicja systemu

Hyperref nonlocal indexing system nie jest zwykłym spisem plików ani licznikiem linków.

Z materiału wynika, że jest to złożony system czterech powiązanych rzeczy:
1. **inwentarza fizycznego** repo,
2. **kart identyfikacyjnych obiektów**,
3. **grafu relacji lokalnych i nielokalnych**,
4. **warstwy audytu i raportowania niespójności**.

Jego zadaniem jest zamienić repo z luźnego zbioru plików w pole bytów z:
- trwałym ID,
- zakotwiczeniem lokalnym,
- zakotwiczeniem nielokalnym,
- śladem pochodzenia,
- relacjami zależności,
- relacjami zwrotnymi,
- mierzalnym stanem crossref.

---

## 2. Zasady twarde

Z materiału wynikają następujące reguły twarde:

### 2.1.
Każdy plik ma mieć:
- docelowe miejsce,
- hyperref,
- własną kartę.

### 2.2.
Każdy obiekt formalny ma mieć kartę identyfikacyjną.

Zakres obiektów formalnych podawany w materiale:
- stała,
- równanie,
- prawo,
- operator,
- definicja,
- tabela,
- manifest,
- skrypt,
- raport.

### 2.3.
Tabele nie mogą używać gołych nazw.
Mają używać **crosslink IDs**.

### 2.4.
Integracja ma być:
- relacyjna,
- audytowalna,
- mapowalna,
- automatyzowalna.

### 2.5.
Bez ID nie ma holonomii.
Nazwy mogą się zmieniać. ID nie.

### 2.6.
Repo nie może udawać kanonu bez mapy zależności.

### 2.7.
Nielokalny crossref nie może być liczony jako prosty licznik referencji.
Ma być ważony semantycznie, relacyjnie i kontraktowo.

---

## 3. Minimalna architektura systemu

Najprostsza poprawna architektura jest w materiale podana jako system 4 warstw.

## 3.1. Warstwa inwentarza
Ma mapować to, co istnieje fizycznie:
- pliki,
- foldery,
- rozmiary,
- hashe,
- typy,
- relacje parent/child.

To jest warstwa lokalna i topologiczna.

## 3.2. Warstwa kart
Ma tworzyć kartę dla każdego:
- pliku,
- obiektu formalnego,
- tabeli,
- parametru,
- równania,
- operatora.

To jest warstwa identyfikacyjna i semantyczna.

## 3.3. Warstwa hyperrefów
Ma budować graf relacji:
- `defines`
- `depends_on`
- `inherits_from`
- `uses`
- `referenced_by`

W innych plikach dochodzą też typy relacji:
- `derives_from`
- `anchors`
- `documents`
- `tests`
- `reports_about`
- `mentions`
- `historical/demo`

To jest warstwa grafowa i nielokalna.

## 3.4. Warstwa audytu
Ma wykrywać:
- obiekty bez parametrów,
- tabele bez crosslinków,
- martwe hyperrefy,
- osierocone obiekty,
- niespójności dziedziczenia,
- orphan cards,
- tables with plain names,
- objects without IDs,
- objects without source,
- dead links,
- duplicate semantic objects.

To jest warstwa kontrolna.

---

## 4. Jednostka podstawowa: obiekt z kartą

Z materiału wynika, że trwały byt systemu ma mieć kartę.
Z różnych plików da się złożyć minimalny wspólny rdzeń takiej karty.

## 4.1. Pola stabilne
Powtarzające się pola:
- `canonical_id`
- `path`
- `object_type`
- `role`
- `layer`
- `dependencies`
- `provenance_links`
- `semantic_mass`
- `density`
- `pressure`
- `orbit_index`
- `sphere_id`
- `winding_seed`
- `truth_anchor`
- `local_anchor`
- `status`

## 4.2. Pola z wersji hyperspace
Dodatkowe pola z przykładowej karty YAML:
- `kind`
- `label`
- `defined_in`
- `path_refs`
- `symbol`
- `own_parameters`
- `inherited_parameters`
- `depends_on`
- `used_by`
- `tests`
- `hyperrefs`
- `notes`

## 4.3. Wniosek
Karta obiektu w tym systemie nie jest tylko metadanymi pliku.
Jest jednocześnie:
- identyfikatorem,
- nośnikiem semantyki,
- nośnikiem zależności,
- nośnikiem pochodzenia,
- lokalnym punktem wejścia do grafu relacji.

---

## 5. System ID

## 5.1. Reguła ogólna
Każdy trwały obiekt potrzebuje canonical ID.

## 5.2. Przykładowe rodziny ID jawnie podane
- `FILE-SOT-...`
- `DIR-SOT-...`
- `PARAM-SOT-...`
- `OP-SOT-...`

## 5.3. Rodziny ID do zdefiniowania według template
- contracts
- object cards
- registry entries
- memory objects
- reports
- reduction events
- evidence objects
- interfaces
- extensions

## 5.4. Status
Materiał jest zgodny, że **system ID jest konieczny**.
Materiał nie zamraża finalnego systemu ID.
W `STRICTE / kandydat / brak` stoi wprost:
- finalny system ID = **kandydat**

---

## 6. Lokalne i nielokalne osadzenie obiektu

Formalizm heatmapy definiuje obiekt repozytoryjny jako byt:
- z lokalizacją w hyperspace,
- z lokalnym stanem orbitalnym,
- z masą semantyczną,
- z lokalnym osadzeniem w splocie nielokalnym,
- z indeksem orbity,
- z character class,
- z nonlocal neighborhood.

Minimalna postać:
- `ℓ_i` — lokalizacja w hyperspace
- `ψ_i` — lokalny stan orbitalny
- `m_i` — masa semantyczna
- `τ_i` — lokalne osadzenie w splocie nielokalnym
- `o_i` — orbit index
- `χ_i` — character class
- `N_i` — nonlocal neighborhood

To znaczy, że indexing system ma przechowywać nie tylko ścieżkę pliku, ale także jego osadzenie nielokalne.

---

## 7. Graf relacji i sprzężeń

## 7.1. Relacje jawne
System hyperrefów musi przechowywać relacje semantyczne, nie tylko ścieżki.
Stabilny rdzeń relacji:
- `defines`
- `depends_on`
- `inherits_from`
- `uses`
- `referenced_by`

Rozszerzenia z formalizmu:
- `derives_from`
- `anchors`
- `documents`
- `tests`
- `reports_about`
- `mentions`
- `historical/demo`

## 7.2. Reprezentacja sprzężenia
Między obiektami definiowane jest sprzężenie:
- `W_ij = ω_ij e^(i δ_ij)`

Z punktu widzenia danych oznacza to potrzebę przechowywania:
- typu relacji,
- wagi relacji,
- offsetu fazowego,
- części rzeczywistej i urojonej sprzężenia,
- proxy podobieństwa semantycznego,
- proxy alignmentu prawdy.

## 7.3. Nośniki tabelaryczne
Minimalne nośniki dla grafu:
- `couplings.csv`
- `orchestrator_graph_edges.csv`
- `phase_couplings.csv`
- katalog cross-reference
- registry index
- dependency graph
- crossref graph
- coupling graph
- sphere graph
- leak graph

---

## 8. Contractual crossref completeness

Formalizm heatmapy wprowadza kontraktową kompletność powiązań.

Każdy obiekt powinien mieć:
- `global_crossrefs`
- `nonlocal_hyperlinks`
- `memory_binding`
- `local_registry_anchor`
- `global_truth_anchor`

Na tej podstawie liczona jest kompletność kontraktowa:
- obiekt może mieć znaczenie semantyczne,
- ale niski stan kompletności kontraktowej,
- co ma dawać alarm.

W danych jest to reprezentowane przez:
- `contract_crossref_completeness`
- `heat_contractual_crossref`

To jest centralny element systemu, bo łączy:
- indexing,
- memory,
- registry,
- truth surface,
- audit.

---

## 9. Nośniki danych systemu

Z materiału wynikają następujące minimalne nośniki danych.

## 9.1. Inwentarz i registry
- `integration/hyperspace_index.json`
- `integration/index_registry.yaml`
- registry index
- object catalog
- cross-reference catalog
- memory object index

## 9.2. Karty
- object cards
- file/object indexing card

## 9.3. Dane stanu obiektów
`objects_state.csv`:
- `id`
- `path`
- `type`
- `layer`
- `size_bytes`
- `content_hash`
- `density`
- `pressure`
- `weight`
- `frequency`
- `semantic_mass`
- `norm_energy`
- `amplitude`
- `phase`
- `orbit_index`
- `character`
- `state_vector`
- `seed`
- `crossref_in`
- `crossref_out`
- `contract_crossref_completeness`

## 9.4. Dane relacyjne
`couplings.csv`:
- `source`
- `target`
- `relation_type`
- `coupling_weight`
- `phase_offset`
- `W_ij_real`
- `W_ij_imag`
- `semantic_similarity`
- `truth_alignment_proxy`

## 9.5. Dane map cieplnych
`heatmaps.csv`:
- `source`
- `target`
- `semantic_action_cost`
- `holonomic_cost`
- `truth_cost`
- `heat_semantic_action`
- `heat_holonomic_tension`
- `heat_contractual_crossref`

## 9.6. Raporty
System ma produkować:
- defect reports
- audit and truth surfaces
- indexing reports
- machine-readable reports
- repo mapping report
- state snapshots
- heatmaps
- triple reports

---

## 10. Kolejność budowy systemu

Z materiału wynika jedna spójna kolejność.

## 10.1. Kolejność ogólna
1. zamrozić prawa, ontologię, obserwable, state space, boundary conditions  
2. zamrozić governance, schemy, IDs, statuses, registry shapes  
3. postawić kernel, orbital, orchestrators, semantic engine, memory  
4. postawić indexing i file/object cards  
5. postawić interfaces  
6. postawić runtime ports  
7. postawić ops i tests  
8. dopiero wtedy wydobywać wzorce kodu z repo referencyjnych

## 10.2. Kolejność orbitalna
1. słownik bytów i obserwabli  
2. przestrzeń stanu  
3. inwarianty  
4. atraktory i potencjały  
5. registry  
6. czas własny i winding  
7. orchestration i reduction  
8. semantic mass i orbit assignment  
9. symulator bez UI  
10. geometry engine  
11. natywna powierzchnia i autonomia

## 10.3. Wniosek
Indexing system nie jest dodatkiem po fakcie.
Ma być zbudowany przed interfejsami i przed runtime portami, a po ontologii, governance i schemach.

---

## 11. Pipeline operacyjny dla hyperref indexing

Na podstawie materiału da się złożyć taki pipeline.

## Faza A — skan topologii
Dla każdego elementu:
- policzyć hash,
- rozpoznać typ,
- przypisać ID,
- zapisać do inventory,
- zapisać parent/child.

## Faza B — ekstrakcja obiektów
Z każdego pliku wydzielić:
- obiekty formalne,
- parametry,
- tabele,
- równania,
- operatory,
- manifesty,
- raporty.

## Faza C — budowa kart
Dla każdego bytu:
- utworzyć object card,
- przypiąć path,
- przypiąć source,
- przypiąć dependencies,
- przypiąć provenance,
- przypiąć anchors,
- przypiąć status.

## Faza D — budowa relacji
Dla każdego obiektu i pliku:
- wyciągnąć linki i odwołania,
- zmapować na ID,
- zbudować relacje `defines`, `depends_on`, `inherits_from`, `uses`, `referenced_by`,
- zapisać relacje do grafów i coupling tables.

## Faza E — liczenie parametrów semantycznych
Dla każdego obiektu:
- policzyć `crossref_in`
- policzyć `crossref_out`
- oszacować `density`
- oszacować `pressure`
- oszacować `semantic_mass`
- przypisać `orbit_index`
- zbudować `state_vector`

## Faza F — liczenie warstwy kontraktowej
Sprawdzić obecność:
- `global_crossrefs`
- `nonlocal_hyperlinks`
- `memory_binding`
- `local_registry_anchor`
- `global_truth_anchor`

Z tego policzyć:
- `contract_crossref_completeness`
- `heat_contractual_crossref`

## Faza G — audit
Wygenerować:
- dead links
- orphan cards
- objects without IDs
- objects without source
- tables with plain names
- duplicate semantic objects
- inconsistency reports

## Faza H — aktualizacja indeksów globalnych
Zaktualizować:
- `docs/INDEX.md`
- `integration/hyperspace_index.json`
- `integration/index_registry.yaml`

Materiał `Plan refaktoryzacji.txt` mówi o tym wprost po relokacjach.

---

## 12. Rola docs/INDEX i indeksów machine-readable

`docs/INDEX.md` ma być warstwą ludzką:
- topologia repo,
- core vs non-core,
- linki do sektorów,
- cross-reference anchors.

`integration/hyperspace_index.json` ma być warstwą maszynową:
- machine-readable cross-reference registry.

`integration/index_registry.yaml` ma przechowywać:
- nową geometrię repo,
- nowe ścieżki,
- statusy:
  - canonical
  - legacy
  - external
  - experimental
  - archive

To jest istotne: system ma mieć równoległy indeks:
- czytelny dla człowieka,
- czytelny dla maszyny.

---

## 13. Rola template

Template potwierdza istnienie następujących sektorów dla systemu indeksowania:
- `indexing/cards/`
- `indexing/catalogs/`
- `indexing/graphs/`
- `indexing/reports/`

i przypisuje im role:

### cards
karty plików i obiektów.

### catalogs
global catalogs and registries:
- object catalog
- cross-reference catalog
- registry index
- memory object index

### graphs
- dependency graph
- crossref graph
- coupling graph
- sphere graph
- leak graph

### reports
raporty audytowe i diagnostyczne dla indexingu.

Template dodaje też:
- `docs/maps/` dla map systemowych,
- `governance/ids/` dla rodzin ID,
- `data/catalogs/` i `data/reports/` jako trwałe nośniki wyników.

---

## 14. Metryki i sens semantyczny

System indeksowania nie ma być wyłącznie administracyjny.
Ma zasilać dalszą dynamikę systemu.

Z materiału wynika, że z indexingu mają wypływać:
- semantic mass,
- density,
- pressure,
- phase,
- amplitude,
- orbit assignment,
- nonlocal neighborhood,
- truth alignment proxy,
- heatmaps.

To znaczy:
indexing system jest zarazem warstwą:
- identyfikacyjną,
- semantyczną,
- orbitalną,
- audytową.

---

## 15. Kontradykcje i niedomknięcia

## 15.1. Finalny system ID
Konieczny, ale nie zamrożony.
Status:
- istnieje wymóg,
- brak finalnej wersji.

## 15.2. Finalna tabela typów relacji
System wymaga typów relacji i ich wag.
Status:
- potrzeba jest jawna,
- finalna tabela relacji nie jest zamrożona.

## 15.3. Finalna mapa wszystkich obiektów na orbity
System wymaga `orbit_index`.
Status:
- pole jest wszędzie obecne,
- finalna globalna mapa nie jest rozstrzygnięta.

## 15.4. Finalna polityka prezentacji heatmap
System wymaga heatmap.
Status:
- warstwy są zdefiniowane,
- finalny sposób prezentacji nie jest rozstrzygnięty.

## 15.5. Finalne drzewo repo
Template i artifact map dają zgodne sektory, ale nie zamrażają jednej ostatecznej geometrii folderów.
Status:
- sektory są stabilne,
- finalne drzewo pozostaje kandydatem.

---

## 16. Najkrótszy rdzeń systemu

Hyperref nonlocal indexing system =

**ID + karty + katalogi + grafy + anchors + crossref + provenance + audit + heatmapa + registry machine-readable**

a nie:
- zwykły indeks plików,
- zwykły licznik linków,
- zwykłe README.

Jest to system, w którym:
- każdy trwały obiekt dostaje canonical ID,
- każdy trwały obiekt dostaje object card,
- każda relacja jest mapowana do grafu,
- każda relacja może być liczona semantycznie i kontraktowo,
- stan globalny jest widoczny w indeksach i raportach,
- martwe lub osierocone elementy są wykrywane automatycznie.

---

## 17. Werdykt roboczy

To, co jest już stabilne:
- konieczność ID,
- konieczność object cards,
- konieczność catalogs/graphs/reports,
- konieczność machine-readable indeksu,
- konieczność nielokalnych crossref,
- konieczność contract completeness,
- konieczność audit layer.

To, co pozostaje otwarte:
- finalny system ID,
- finalna tabela relacji i wag,
- finalna orbityzacja wszystkich obiektów,
- finalny sposób prezentacji heatmap,
- finalne drzewo repo.

To jest pełny rdzeń hyperref nonlocal indexing system wyciągnięty z materiału.
