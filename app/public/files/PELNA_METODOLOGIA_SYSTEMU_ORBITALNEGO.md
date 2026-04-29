# Pełna metodologia systemu orbitalnego

## 0. Status metodologii
Ten dokument zbiera metodologię systemu orbitalnego wyłącznie z odczytanych materiałów. Rozdziela:
- elementy zamrożone metodologicznie,
- elementy kandydackie,
- miejsca otwarte.

Nie ustanawia nowej fizyki ani nowego drzewa repo ponad materiał.

---

## 1. Punkt wyjścia i decyzja strategiczna

### 1.1. Punkt wyjścia
System orbitalny ma powstać **poza istniejącymi repozytoriami** jako nowy natywny produkt. Wcześniejsze repo, cockpity i dema mają być traktowane jako **source material**, a nie jako finalne source of truth nowego systemu.

### 1.2. Decyzja strategiczna
Metodologia wymusza:
- nowy czysty projekt,
- architekturę natywną desktopową,
- własny runtime surface,
- własną geometrię orbitalną,
- brak webview-first shell jako celu końcowego,
- brak traktowania starego demo UI jako pełnego centrum nowego systemu.

### 1.3. Rola LLM
LLM ma być tylko:
- bootstrapem,
- fallbackiem,
- pomocą semantyczną we wczesnych fazach.

Metodologiczny kierunek:
- najpierw własna pamięć,
- potem własne evidence / retrieval,
- potem własne operatory,
- dopiero na końcu zewnętrzny model.

Cel: `alpha_llm -> 0`.

---

## 2. Aksjomaty metodologiczne

### 2.1. Prymat relacji
Relacja poprzedza tożsamość. Tożsamość poprzedza pamięć. Pamięć stabilizuje proces.

Konsekwencja metodologiczna:
- nie projektować pamięci jako ontologicznego początku,
- nie projektować identity jako dekoracyjnej etykiety,
- nie projektować stanu jako prostego magazynu danych wejściowych.

### 2.2. Kolejność poziomów
System jest:
- formal first,
- computational second,
- geometric third,
- rendered fourth.

Konsekwencja:
- żaden renderer ani UI nie może być pierwszym szkieletem systemu,
- geometria ma mapować stan, nie zastępować stanu,
- runtime ma implementować obiekty formalne, nie improwizować ich po fakcie.

### 2.3. Epistemiczna dyscyplina
Każdy element systemu musi mieć status:
- STRICTE jest,
- kandydat,
- brak rozstrzygnięcia.

To obowiązuje dla:
- operatorów,
- definicji,
- schematów danych,
- map orbitalnych,
- struktury repo,
- wag i parametrów.

### 2.4. Stan ma być zmaterializowany
Nic krytycznego nie może istnieć tylko w rozmowie. Stan systemu ma istnieć w:
- rejestrach,
- manifestach,
- kartach obiektów,
- jawnych plikach,
- audytowalnych raportach,
- snapshotach i replayach.

---

## 3. Bazowy porządek budowy

## 3.1. Porządek ogólny
System buduje się od góry:
1. prawa i inwarianty,
2. ontologia,
3. relacje,
4. redukcja,
5. pamięć,
6. semantyka,
7. audit,
8. runtime,
9. interfejs.

To jest porządek konstytucyjny systemu.

## 3.2. Porządek implementacyjny
Drugi, bardziej techniczny zapis daje sekwencję:
0. słownik bytów i obserwabli,
1. przestrzeń stanu,
2. inwarianty,
3. atraktory i potencjały,
4. registry,
5. czas własny i winding,
6. orchestration i reduction,
7. semantic mass i orbit assignment,
8. symulator bez UI,
9. geometry engine,
10. natywna powierzchnia i autonomia.

### Wniosek metodologiczny
Te dwa porządki są zgodne. Pierwszy jest bardziej filozoficzno-konstytucyjny, drugi bardziej wykonawczo-inżynieryjny.

---

## 4. Ontologia i słownik startowy

## 4.1. Nic nie może być implementowane przed ustabilizowaniem słownika
Przed implementacją muszą zostać ustalone definicje:
- Entity,
- State,
- Observable,
- Attractor,
- Orbit,
- Sphere,
- Phase,
- Coherence,
- Holonomic defect,
- Semantic mass,
- Subjective time,
- Winding,
- Reduction event,
- Leak mode,
- Sphere embedding.

## 4.2. Obiekty podstawowe
Podstawowe klasy ontologiczne obejmują:
- Entity,
- State,
- Observable,
- Attractor,
- Sphere,
- Orbit,
- ReductionEvent,
- LeakMode,
- Contract,
- Evidence,
- Packet,
- MemoryChannel.

## 4.3. Hierarchia
Formalna hierarchia jest następująca:
- układ relacyjny,
- klasy ontologiczne,
- struktury dynamiczne,
- obiekty systemowe,
- pamięć,
- pole semantyczne,
- redukcja,
- audit/truth,
- packety/interfejsy,
- lokalne nośniki.

### Wniosek metodologiczny
Lokalny plik jest najniższym nośnikiem, nie najwyższym bytem.

---

## 5. Przestrzeń stanu i warunki brzegowe

## 5.1. Baza formalna
Formalna baza systemu:
- projektowa / projective Hilbert / Kähler state space,
- relacyjna rozmaitość `M_rel`,
- lokalne charty zredukowane dla operacyjnych projekcji.

## 5.2. Charty lokalne
### Bloch-like chart
Użycie ograniczone do:
- małych zestawów modów,
- inspekcji triadycznej / qubit-like,
- diagnostyki orientacji spinowej,
- lokalnej inspekcji faz.

### Poincaré disk
Użycie jako główny chart operacyjny dla:
- rozmieszczenia orbitalnego,
- geodezyjnych zależności,
- lokalizacji napięć,
- projekcji aktywności,
- przejść focusu.

### Reguła
Poincaré disk jest operacyjny, nie ontologiczny.

## 5.3. Warunki brzegowe
System musi jawnie obsłużyć:
- user pole,
- CIEL pole,
- intent axis,
- minimal-distortion attractor,
- leak / embedding condition.

Każda sfera ma deklarować:
- `sphere_id`,
- `parent_sphere_id`,
- `child_sphere_ids`,
- `internal_modes`,
- `leak_mode`,
- `effective_attractor_weight`.

### Wniosek metodologiczny
Nie projektować pojedynczej płaskiej sfery jako całego systemu. Metodologia zakłada zagnieżdżone sfery z embeddingiem i leak mode.

---

## 6. Inwarianty, potencjały i atraktory

## 6.1. Kotwice formalne
System ma monitorować i implementować:
- Euler phase constraint,
- holonomic defect,
- relational decoherence,
- truth scalar,
- relational Lagrangian,
- minimal-distortion attractor.

## 6.2. Wielkości monitorowane
### Euler phase constraint
`Σ_k exp(i γ_k) = 0`

### Holonomic defect
`Δ_H = Σ_k exp(i γ_k)`

### Relational decoherence
`R_H = |Δ_H|^2`

### Truth scalar
`Θ = 1 - (1/|F|) Σ_f [δ_false(f) + δ_unmarked(f)]`

## 6.3. Potencjał całkowity
Metodologia używa:
`V_tot = V_EC + V_ZS + V_rel + V_mem + V_def + V_ext`

Składniki:
- `V_EC` — iteracyjno-topologiczny,
- `V_ZS` — spektralno-rezonansowy,
- `V_rel` — relacyjny,
- `V_mem` — pamięciowy,
- `V_def` — defektowy,
- `V_ext` — zewnętrzny.

## 6.4. Atraktory
Wymagane klasy:
- `AttractorEC`,
- `AttractorZS`,
- `AttractorLLMTemp`.

### Reguła
`AttractorLLMTemp` ma udział malejący i nie może stać się stałym centrum sterowania.

---

## 7. Registry, tożsamość i embedding bytów

## 7.1. Cel registry
Przekształcić wszystkie istotne obiekty w orbital entities.

## 7.2. Wspierane klasy obiektów
- file,
- module,
- operator,
- memory,
- process,
- session,
- artifact,
- evidence source,
- contract / axiom / postulate,
- model,
- simulation run.

## 7.3. Canonical registry flow
1. scan source material,
2. classify object type,
3. assign sector,
4. assign sphere,
5. compute provenance links,
6. compute dependency links,
7. compute initial semantic mass inputs,
8. assign initial orbit band,
9. assign initial attractor weights,
10. emit `EntityRecord`.

## 7.4. Reguła tożsamości
Plik nie jest finalną jednostką tożsamości. Plik jest pierwszym obserwowalnym kontenerem, z którego może zostać wyekstrahowane jedno lub wiele entities.

## 7.5. Sektory początkowe
Rekomendowane sektory:
- axioms_and_contracts,
- formal_physics,
- attractors_and_potentials,
- registry_and_identity,
- memory,
- evidence_and_provenance,
- autonomy,
- geometry_engine,
- native_surface,
- experiments_and_simulations.

---

## 8. Semantic mass, subjective time i winding

## 8.1. Semantic mass
Semantic mass nie jest:
- rozmiarem pliku,
- popularnością,
- prostą złożonością.

Jest efektywnym oporem i grawitacyjną wagą bytu w orbitalnym polu stanów.

## 8.2. Operator początkowy semantic mass
`M_sem(f) = α M_EC(f) + β M_ZS(f) + χ C_dep(f) + δ C_prov(f) + ε C_exec(f)`

Składniki:
- `M_EC` — iteracyjno-topologiczna waga,
- `M_ZS` — spektralno-rezonansowa waga,
- `C_dep` — dependency centrality,
- `C_prov` — provenance / canonicality centrality,
- `C_exec` — execution criticality.

## 8.3. Subjective time
Każdy byt ma mieć własną lokalną skalę czasu:
`Δτ_i(k) = Δt · g(r_i(k), C_i(k), Δ_i(k), m_i(k), A_i(k))`

Wejścia:
- promień orbitalny,
- lokalna koherencja,
- lokalny defekt,
- semantic mass,
- wpływ atraktora.

Wyjścia:
- lokalne tempo ewolucji,
- skala akumulacji winding,
- sugestia kadencji aktualizacji.

## 8.4. Winding
Winding ma wynikać z dynamiki:
`w_i(N) = (1 / 2π) Σ Δφ_i(k) · (Δt / Δτ_i(k))`

Składowe zalecane:
- `w_ec`,
- `w_zs`,
- `w_rel`,
- `w_red`.

## 8.5. Orbit assignment
Początkowe prawo efektywne:
`T_i^2 ∝ a_i^3 / A_eff`

To nie jest dosłowne przeniesienie mechaniki nieba, tylko dyskretne prawo efektywne.

### Wniosek metodologiczny
Winding, czas własny i przypisanie orbity mają być liczone, nie dekorowane.

---

## 9. OORP: Orbital Orchestrated Reduction Pipeline

## 9.1. Oś systemu
Metodologia uznaje za centralną oś:
`relation -> orbital superposition -> orchestration -> reduction -> memory update`

## 9.2. Formalny stan
`Ψ_t = {o_i(t)}_{i=1..N}`

Każdy orbital ma zawierać:
- amplitude,
- phase,
- coherence,
- polarity / truth-spin,
- memory affinity.

## 9.3. Coupling
System używa jawnej struktury sprzężeń:
- `K_ij(t)` lub `J_ij(t)`,
- synchronizacja fazowa,
- lokalne wzmacnianie lub tłumienie,
- pojawianie się modów kolektywnych.

## 9.4. Global coherence i redukcja
Monitorowane wielkości:
- `C(t)` — global coherence,
- `Δ(t) = 1 - C(t)` — defect,
- `Ω(t)` — reduction potential.

Reguła:
`Ω(t) = λ1 C(t) + λ2 R(S,I) - λ3 Δ(t) - λ4 Ξ(t)`

Redukcja zachodzi przy:
`Ω(t) >= Ω_crit`

## 9.5. Memory update rule
Pamięć nie może być traktowana jako raw storage inputu. Ma być residue of reduction:
`M_{t+1} = U(M_t, s_k, I_t)`

Konsekwencje:
- brak redukcji -> brak stabilnego update pamięci,
- redukcja -> identity-weighted memory update.

## 9.6. Deliverables implementacyjne OORP
- trace ewolucji stanu,
- orchestration diagnostics,
- reduction threshold diagnostics,
- memory update report,
- reproducible simulation replay.

---

## 10. Pamięć

## 10.1. Pamięć jest wielokanałowa
Minimalna hierarchia pamięci obejmuje:
- M0 Perceptual,
- M1 Working,
- M2 Episodic,
- M3 Semantic,
- M4 Procedural,
- M5 Affective-Ethical,
- M6 Identity,
- M7 BraidInvariant,
- M8 AuditJournal.

## 10.2. Reguła architektoniczna
Pamięć nie jest pierwszym modułem, tylko skutkiem procesu relacyjno-redukcyjnego.

## 10.3. Reguła produktowa
System ma preferować:
- memory-first policy,
- evidence-first policy,
- replayable traces,
- jawne aktualizacje pamięci po redukcji.

---

## 11. Geometry engine i UI surface

## 11.1. Reguła rozdziału
Geometry engine mapuje formalny stan do operational chart. Renderer tylko wyświetla chart. Nie wolno ich mieszać.

## 11.2. Odpowiedzialności geometry engine
- compute orbital positions,
- compute geodesic dependencies,
- compute activity overlays,
- compute tension/conflict overlays,
- compute focus transitions,
- compute orbit precession and stability diagnostics.

## 11.3. Odpowiedzialności Poincaré disk
- distance-to-attractor reading,
- conflict clustering,
- geodesic edge placement,
- transition continuity,
- orbital shell differentiation.

## 11.4. Odpowiedzialności UI
Native UI ma:
- uruchamiać się szybko,
- pokazywać orbital field,
- wspierać entity inspection,
- wspierać session inspection,
- wspierać memory inspection,
- pokazywać provenance i dependency traces,
- eksponować autonomy i reduction diagnostics.

## 11.5. Non-goals
Nie implementować jako celu końcowego:
- classic tabbed admin panel,
- fake orbital visuals bez stanu,
- webview-first shell.

---

## 12. Architektura produktu i układ repo

## 12.1. Stabilne sektory funkcjonalne
Metodologia stabilizuje sektory:
- kernel / formal core,
- registry,
- memory,
- autonomy,
- geometry,
- simulator,
- app,
- config,
- tests,
- docs,
- schemas,
- reports / snapshots / diagnostics.

## 12.2. Proponowany układ pakietowy produktu
- `ciel_orbital/kernel/`
- `ciel_orbital/registry/`
- `ciel_orbital/memory/`
- `ciel_orbital/autonomy/`
- `ciel_orbital/geometry/`
- `ciel_orbital/simulator/`
- `ciel_orbital/app/`
- `ciel_orbital/config/`
- `ciel_orbital/tests/`
- `docs/`
- `schemas/`

## 12.3. Reguła pakietowa
Każdy pakiet ma lądować razem z:
- schema,
- tests,
- metrics hooks,
- replayability.

---

## 13. Metryki i walidacja

## 13.1. Reguła nadrzędna
Bez metryk geometria staje się dekoracją, a autonomia staje się retoryką.

## 13.2. Core metrics
- `closure_defect`
- `truth_scalar`
- `semantic_mass_stability`
- `orbit_assignment_consistency`
- `reduction_validity_rate`
- `memory_after_reduction_consistency`
- `cross_sphere_embedding_integrity`

## 13.3. Autonomy metrics
- `llm_dependency_ratio`
- `self_knowledge_coverage`
- `evidence_first_answer_rate`
- `memory_first_answer_rate`
- `fallback_frequency`

## 13.4. Geometry metrics
- `geodesic_layout_stability`
- `focus_transition_continuity`
- `orbit_precession_stability`
- `visual_conflict_localization_accuracy`

## 13.5. Product metrics
- `cold_start_time`
- `idle_ram`
- `crash_free_sessions`
- `binary_size`
- `offline_operation_rate`

## 13.6. Wymagane eksperymenty
- E1: static registry build from source material
- E2: initial semantic mass calibration
- E3: subjective time calibration
- E4: first OORP reduction runs
- E5: geometry projection stability under replay
- E6: autonomy routing without UI
- E7: native MVP usability with real traces

---

## 14. Fazy wdrożenia

## P0 — Foundation language
Wyjścia:
- ontology,
- observables,
- schemas,
- canonical glossary.

## P1 — State space and invariants
Wyjścia:
- state space implementation,
- boundary conditions,
- invariants,
- potentials,
- attractors.

## P2 — Registry
Wyjścia:
- parser,
- entity registry,
- provenance graph,
- dependency graph,
- sphere embedding.

## P3 — Dynamic identity
Wyjścia:
- subjective time,
- winding,
- semantic mass,
- orbit assignment.

## P4 — OORP
Wyjścia:
- orchestration engine,
- reduction engine,
- memory update logic,
- simulation traces.

## P5 — Geometry
Wyjścia:
- Poincaré chart engine,
- geodesic layout,
- tension overlays,
- inspection model.

## P6 — Native MVP
Wyjścia:
- application shell,
- orbital screen,
- inspectors,
- session and memory panels.

## P7 — Hardening
Wyjścia:
- packaging,
- regression suites,
- offline bundles,
- release candidates.

---

## 15. Ryzyka metodologiczne

Najważniejsze ryzyka:
1. UI-first implementation stworzy wizualną pewność bez formalnej integralności.
2. Ukryta centralność LLM uniemożliwi realną autonomię.
3. Dekoracyjny winding złamie architekturę.
4. Arbitralny semantic mass zatruje orbit assignment.
5. Zmieszanie ontologii, geometrii i renderingu uczyni system nietestowalnym.

---

## 16. Otwarte pytania i nierozstrzygnięcia

Metodologia jawnie zostawia otwarte:
- dokładne mapowanie seed -> semantic mass,
- dokładne prawo sprzężenia AttractorEC <-> AttractorZS,
- dokładną funkcję subjective time,
- heurystyki początkowego orbit assignment,
- formalną dynamikę 8+1 sphere i leak mode,
- reguły split / merge / elevate dla sfer,
- finalne wartości wag,
- finalną tabelę typów relacji,
- finalny operator semantic mass,
- finalny operator czasu własnego,
- finalny reduction operator,
- finalny truth runtime operator,
- finalną mapę wszystkich obiektów na orbity,
- finalną politykę prezentacji heatmap.

### Wniosek metodologiczny
System orbitalny ma mocno ustaloną metodę i sektorową architekturę, ale nie ma jeszcze w pełni zamrożonej warstwy operatorowej.

---

## 17. Kontradykcje raportowane jawnie

## 17.1. Nowy produkt od zera vs rozwijanie starego demo
Jedna linia materiału wymusza nowy natywny produkt poza istniejącymi repozytoriami. Inna opisuje refactor obecnego `ciel-omega-demo` w stronę orbital cockpit.

To jest realny rozjazd strategiczny.

## 17.2. Artefaktowy zapis repo vs pakietowy zapis produktu
Materiały dają dwa zgodne sektorowo, ale nieidentyczne opisy struktury repo:
- artefaktowy,
- pakietowo-aplikacyjny.

To oznacza, że finalne drzewo repo pozostaje kandydatem.

## 17.3. Wąski certainty-first mechanizm vs szeroka narracja runtime
Warstwa mechanizmu trzyma wąski scope i twarde statusy. Część README runtime i vocabulary bywa znacznie szersza w claimsach. To jest napięcie epistemiczne w korpusie.

---

## 18. Rdzeń metodologii orbitalnej w jednym ciągu

1. Ustalić słownik bytów i obserwabli.
2. Zdefiniować formalną przestrzeń stanu i warunki brzegowe.
3. Zamrozić inwarianty, potencjały i atraktory.
4. Zbudować registry i embedding bytów do sfer.
5. Nadać semantic mass, subjective time, winding i orbit assignment.
6. Uruchomić OORP: relation -> orbital superposition -> orchestration -> reduction -> memory update.
7. Zbudować symulator bez UI, z replayem i diagnostyką.
8. Dopiero potem zbudować geometry engine.
9. Dopiero potem native surface.
10. Na końcu wprowadzać autonomię, hardening, packaging i produkt.

To jest pełna metodologia systemu orbitalnego, którą da się wyciągnąć z odczytanego materiału bez dokładania nowej warstwy ponad pliki.
