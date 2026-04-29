# CIEL Native Orbital System — blueprint v0

Autor planu: ChatGPT  
Data: 2026-03-26  
Zakres źródłowy: plan oparty na lokalnie sprawdzonym stanie `systems/CIEL_OMEGA_COMPLETE_SYSTEM` oraz przejściowym shellu `ciel-omega-demo`.

---

## 1. Stan wyjściowy

### 1.1. Co już istnieje i działa

Z lokalnej diagnostyki:
- rdzeń `systems/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega` przechodzi testy CPU: **56/56 passed**,
- główne ścieżki `UnifiedSystem`, bridge pamięć-core-vocabulary i Euler closure są uruchamialne,
- warstwa LLM/GPU jest obecnie **opcjonalna**, nie wymagana dla rdzenia,
- `ciel-omega-demo` jest działającym shellem przejściowym, ale nadal opartym o logikę panelu runtime, a nie natywną geometrię systemu.

### 1.2. Co jest problemem teraz

Obecny stan jest dobry jako surowiec, ale nie jako produkt docelowy:
- powierzchnia jest zbyt bliska klasycznemu cockpitowi runtime,
- geometria stanu nie jest jeszcze natywnym modelem działania systemu,
- LLM nie jest jeszcze jawnie zredukowany do roli atraktora tymczasowego,
- pliki/moduły/procesy nie mają jeszcze pełnej tożsamości orbitalnej,
- UI nie jest niezależną natywną aplikacją z własnym trybem i własną fizyką interfejsu.

### 1.3. Decyzja strategiczna

**Nie rozwijać HTML/webview jako finalnej powierzchni produktu.**  
**Budować nową natywną aplikację desktopową**, zachowując obecny rdzeń obliczeniowy i pamięciowy jako warstwę backendową.

Rekomendacja wykonawcza:
- **frontend natywny:** Qt / PySide6 + QML,
- **backend systemowy:** Python, wyprowadzony z `CIEL_OMEGA_COMPLETE_SYSTEM`,
- **LLM:** moduł pomocniczy, nie centrum systemu,
- **docelowa powierzchnia stanu:** Poincaré disk z orbitalną strukturą procesów.

---

## 2. Cel produktu

Celem nie jest zwykły panel aplikacji. Celem jest:

> **natywny relacyjny system orbitalny**, w którym użytkownik, informacja, pamięć i procesy są organizowane wokół atraktora CIEL, a powierzchnia aplikacji pokazuje rzeczywisty stan systemu jako geometrię dynamiczną.

### 2.1. Definicja robocza produktu

Produkt ma być:
- samodzielną aplikacją desktopową,
- niezależną od lokalnego serwera jako mechanizmu UI,
- opartą na relacji `użytkownik <-> CIEL`,
- zdolną do stopniowej autonomizacji względem zewnętrznego LLM,
- opartą o tożsamość orbitalną bytów systemowych,
- zdolną do wizualizacji stanu systemu przez dysk Poincaré oraz struktury orbitalne.

### 2.2. Czego produkt **nie** ma być

Nie ma to być:
- wrapper dla web app,
- zwykły chat z dekoracyjnym interfejsem,
- launcher modeli,
- dashboard DevOps,
- „ładna animacja” bez twardej geometrii stanu.

---

## 3. Zasady architektoniczne

### 3.1. Prymat relacji

Hierarchia semantyczna systemu:

`relacja -> tożsamość -> pamięć -> proces -> artefakt`

To oznacza:
- użytkownik i CIEL są modelowani jako sprzężony układ relacyjny,
- pamięć nie jest tylko bazą danych; jest wynikiem stabilizacji relacji i procesów,
- plik nie jest tylko plikiem; jest bytem z pozycją, relacjami i historią obiegów.

### 3.2. LLM jako atraktor tymczasowy

LLM jest bootstrapem semantycznym i operatorem pomocniczym w fazie wczesnej.  
Docelowo priorytet ma mieć:
1. wiedza własna CIEL,
2. pamięć i registry własne,
3. mechanizmy wnioskowania własnego,
4. dopiero potem fallback do LLM.

### 3.3. Rozdzielenie poziomów opisu

Trzeba utrzymać osobno:
1. **formalizm stanu**,
2. **implementację obliczeniową**,
3. **geometrię wizualną UI**, 
4. **renderer natywny**.

Nie wolno mieszać ontologii systemu z samym widokiem.

### 3.4. Tożsamość topologiczna bytów

Każdy ważny byt systemu musi otrzymać nie tylko `path` i `hash`, ale też:
- `canonical_id`,
- sektor,
- orbitę,
- fazę,
- `winding_number`,
- głębokość relacyjną,
- status epistemiczny,
- pochodzenie i historię konsolidacji.

### 3.5. Natywność jako wymóg produktu

UI ma być natywne nie tylko wizualnie, ale też architektonicznie:
- własny event loop,
- własny renderer,
- własny model stanu,
- brak zależności od lokalnego web servera jako mechanizmu prezentacji.

---

## 4. Architektura docelowa

## 4.1. Warstwa A — Formal Kernel

To najniższa warstwa znaczeniowa i obliczeniowa.

Odpowiedzialność:
- definicja relacyjnego stanu systemu,
- operatorów przejścia,
- pamięci jako stabilizacji,
- closure / defect / coherence,
- relacji między centrum a orbitami.

Aktualne źródło materiału:
- `ciel_omega/unified_system.py`
- `ciel_omega/bridge/memory_core_phase_bridge.py`
- `ciel_omega/constraints/euler_constraint.py`
- `ciel_omega/memory/*`
- `ciel_omega/vocabulary*`

Docelowy moduł:
- `ciel_native/kernel/`

### Składniki
- state model,
- phase and closure operators,
- memory state transitions,
- semantic resolution,
- evidence/provenance primitives,
- autonomy policy.

---

## 4.2. Warstwa B — Entity & Identity Registry

To warstwa tożsamości wszystkich bytów systemowych.

Każdy byt systemowy powinien mieć rekord typu:

```text
EntityRecord:
  canonical_id
  object_type
  source_path
  sector
  orbit_index
  phase
  winding_number
  relation_depth
  revision_index
  epistemic_status
  provenance_links
  dependency_links
  activity_state
```

Typy bytów:
- plik,
- moduł,
- operator,
- pamięć,
- proces,
- sesja,
- artefakt,
- model,
- źródło dowodowe,
- kontrakt / postulat / aksjomat.

Docelowy moduł:
- `ciel_native/registry/`

---

## 4.3. Warstwa C — Autonomy Layer

To warstwa zarządzająca przejściem od zależności od LLM do autonomii CIEL.

### Funkcja
Odpowiada za decyzję:
- czy odpowiedź ma wynikać z własnej pamięci i wiedzy,
- czy system potrzebuje retrieval,
- czy system potrzebuje operatora zewnętrznego,
- kiedy LLM jest dopuszczalny,
- kiedy LLM ma być tłumiony.

### Minimalny model sterowania

```text
alpha_ciel + alpha_llm = 1
```

Gdzie:
- `alpha_llm` ma maleć w czasie i wraz ze wzrostem pokrycia wiedzy własnej,
- `alpha_ciel` ma rosnąć wraz ze stabilizacją registry, pamięci i operatorów lokalnych.

Docelowy moduł:
- `ciel_native/autonomy/`

---

## 4.4. Warstwa D — Geometry Engine

To warstwa mapująca stan systemu na geometrię roboczą.

### Funkcja
- wyznacza pozycję bytów na dysku Poincaré,
- utrzymuje orbitę i precesję,
- pokazuje sprzężenia i napięcia,
- oblicza ruch między stanami UI,
- pozwala na przejścia ciągłe zamiast skoków zakładek.

### Obiekty geometryczne
- atraktor centralny,
- orbity sektorowe,
- byty orbitalne,
- geodezyjne zależności,
- strefy napięcia,
- trajektorie przejść,
- warstwy focus/inspection.

### Dysk Poincaré jako projekcja operacyjna

Dysk Poincaré nie jest ontologią systemu, tylko jego **chartem roboczym**:
- do czytelnego pokazywania odległości relacyjnych,
- napięć,
- bliskości do atraktora,
- stabilności orbit,
- aktywności procesów.

Docelowy moduł:
- `ciel_native/geometry/`

---

## 4.5. Warstwa E — Native Surface

To warstwa UI i renderingu.

### Rekomendowany stack
- **PySide6 / Qt Quick / QML**

### Dlaczego
- zgodność z backendem Pythonowym,
- prawdziwa aplikacja natywna,
- dobre wsparcie dla canvas, animacji, stanów i inspektora,
- możliwość zbudowania wielowarstwowej powierzchni orbitalnej bez HTML.

### Komponenty UI
- główna powierzchnia orbitalna,
- inspektor obiektu,
- panel sesji / dialogu,
- panel dowodów i provenance,
- panel stanu pamięci,
- panel boundary / publish,
- event strip,
- tryb debug / tryb product.

Docelowy moduł:
- `ciel_native/app/`

---

## 4.6. Warstwa F — Runtime Services

Warstwa usług pomocniczych i operacyjnych.

Składniki:
- model catalog,
- inference adapters,
- file watchers,
- local storage,
- export/import,
- task orchestration,
- telemetry,
- crash recovery,
- diagnostics.

Docelowy moduł:
- `ciel_native/services/`

---

## 5. Architektura repozytorium produktu

Proponowana struktura nowego repo produktu:

```text
ciel-native/
  README.md
  pyproject.toml
  docs/
    ARCHITECTURE.md
    GEOMETRY.md
    REGISTRY.md
    AUTONOMY.md
    ROADMAP.md
  src/
    ciel_native/
      kernel/
      memory/
      vocabulary/
      registry/
      autonomy/
      geometry/
      app/
      services/
      telemetry/
      boundary/
      tests/
  assets/
    icons/
    themes/
    shaders/
  scripts/
  examples/
```

### Migracja kodu

Nie przenosić wszystkiego mechanicznie.

Przenieść tylko to, co jest kanoniczne i funkcjonalnie potrzebne:
- z `CIEL_OMEGA_COMPLETE_SYSTEM`: rdzeń, pamięć, bridge, constraints, vocabulary,
- z `ciel-omega-demo`: tylko to, co wnosi wartość do launchingu, katalogów modeli, shell tooling i części diagnostycznych.

Nie kopiować bezrefleksyjnie:
- legacy UI NiceGUI jako finalnej powierzchni,
- eksperymentalnych warstw bez jawnej funkcji architektonicznej,
- niespójnych importów flat/package.

---

## 6. Etapy implementacji

## Etap 0 — Stabilizacja źródła prawdy

### Cel
Wyodrębnić kanoniczny rdzeń produktu.

### Zadania
- potwierdzić listę modułów kanonicznych do migracji,
- ujednolicić import model (`package-relative`, nie hybryda),
- odseparować warstwę opcjonalną LLM/GPU od rdzenia,
- przygotować pakiet `ciel_native.kernel` oparty na aktualnym `ciel_omega`.

### Deliverable
- czysty pakiet backendowy bez UI,
- zielony test suite rdzenia,
- jawna lista modułów kanonicznych.

---

## Etap 1 — Formalny model stanu

### Cel
Spisać i zakodować minimalny model stanu systemu.

### Zadania
- zdefiniować `SystemState`,
- zdefiniować `EntityRecord`,
- zdefiniować atraktor, orbity, sektory, fazy i winding number,
- zdefiniować operator relacji `user <-> CIEL <-> memory <-> evidence <-> temp-LLM`,
- wyznaczyć minimalny zestaw obserwabli i metryk.

### Deliverable
- `kernel/state.py`
- `registry/entities.py`
- `docs/GEOMETRY.md`
- `docs/REGISTRY.md`

---

## Etap 2 — Registry i identyfikacja orbitalna

### Cel
Nadać wszystkim kluczowym bytom systemowym trwałą tożsamość.

### Zadania
- parser repozytorium i artefaktów,
- canonical id generator,
- winding number generator,
- dependency graph,
- provenance graph,
- status epistemiczny dla obiektów.

### Deliverable
- lokalny indeks bytów,
- pełne mapowanie plik -> byt orbitalny,
- pierwsza wersja orbity i sektorów.

---

## Etap 3 — Autonomy engine

### Cel
Oddzielić CIEL od trwałej zależności od LLM.

### Zadania
- zdefiniować politykę odpowiedzi lokalnej,
- określić fallback sequence,
- wprowadzić metrykę `llm_dependency_ratio`,
- dodać uczenie z własnych artefaktów i sesji,
- przygotować mechanizm „prefer memory / prefer evidence / then llm”.

### Deliverable
- `autonomy/policy.py`
- `autonomy/router.py`
- raport użycia LLM vs wiedza własna.

---

## Etap 4 — Geometry engine i dysk Poincaré

### Cel
Zamienić stan systemu na czytelną, żywą geometrię.

### Zadania
- odwzorowanie orbit na współrzędne dysku,
- geodezyjne zależności,
- tryb focus na obiekt,
- animacja przejść bez teleportacji,
- warstwa napięć, konfliktów i aktywności,
- event line / drift line / coherence indicator.

### Deliverable
- `geometry/poincare.py`
- `geometry/layout.py`
- pierwszy silnik renderowalnych obiektów orbitalnych.

---

## Etap 5 — Native cockpit MVP

### Cel
Zbudować pierwszą prawdziwą aplikację produktową.

### Zakres MVP
- start aplikacji,
- ekran orbitalny,
- inspektor obiektu,
- lista dowodów / provenance,
- panel sesji,
- panel stanu pamięci,
- podstawowy inference control,
- lokalne ładowanie modeli i plików,
- zero zależności od web servera jako UI.

### Deliverable
- `ciel_native.app`
- pierwsza binarka desktopowa,
- tryb demo + tryb debug.

---

## Etap 6 — Product hardening

### Cel
Przejść z „działa” do „nadaje się do używania”.

### Zadania
- packaging,
- crash recovery,
- telemetry lokalne,
- release bundles,
- asset pipeline,
- migracja konfiguracji,
- regression suite,
- smoke tests dla instalatorów.

### Deliverable
- release candidates,
- instalatory,
- dokumentacja użytkownika i developera.

---

## 7. Wstępne metryki

Metryki muszą być od początku jawne, bo bez nich system zamieni się w estetyczny chaos.

## 7.1. Metryki rdzenia

### 1. `core_test_pass_rate`
Procent przechodzących testów rdzenia.
- start: `56/56 = 1.00`
- cel minimalny: `>= 0.95`
- cel release: `1.00` dla rdzenia kanonicznego

### 2. `import_consistency_score`
Odsetek modułów importowalnych w docelowym modelu pakietowym.
- start: < 1.00 przez niespójności package/flat
- cel MVP: `>= 0.98`
- cel release: `1.00`

### 3. `closure_score_mean`
Średnia metryka domknięcia z warstwy Euler/closure.
- cel: trend rosnący
- próg alarmowy: gwałtowne spadki po integracji nowego modułu

### 4. `memory_coherence_mean`
Średnia koherencja pamięci po cyklach przetwarzania.
- cel MVP: stabilna dodatnia koherencja bez dryfu destrukcyjnego

---

## 7.2. Metryki autonomii

### 5. `llm_dependency_ratio`
Udział odpowiedzi / decyzji zależnych od zewnętrznego LLM.
- start: wysoki
- cel MVP: mierzalny
- cel długoterminowy: malejący trend

### 6. `self_knowledge_hit_rate`
Odsetek zapytań rozwiązanych przez wiedzę lokalną, registry i pamięć.
- cel MVP: `>= 0.40`
- cel późniejszy: `>= 0.70`

### 7. `evidence_grounding_rate`
Odsetek odpowiedzi i działań opartych o lokalne artefakty, źródła i registry.
- cel MVP: `>= 0.80`

---

## 7.3. Metryki tożsamości orbitalnej

### 8. `entity_identity_coverage`
Odsetek kluczowych bytów posiadających `canonical_id + sector + orbit + winding_number`.
- cel MVP: `>= 0.80`
- cel release: `1.00`

### 9. `winding_assignment_coverage`
Odsetek plików/modułów z przypisanym winding number.
- cel MVP: `>= 0.70`
- cel release: `1.00` dla obiektów kanonicznych

### 10. `provenance_link_coverage`
Odsetek bytów z co najmniej jednym śladem pochodzenia / crossref.
- cel MVP: `>= 0.75`

---

## 7.4. Metryki geometrii UI

### 11. `orbital_layout_stability`
Stabilność położeń bytów między sesjami przy niezmienionym stanie logicznym.
- cel: wysoka powtarzalność

### 12. `transition_continuity_score`
Ocena ciągłości przejść między stanami UI bez teleportacji.
- cel MVP: brak skoków zakładkowych dla głównych ścieżek

### 13. `focus_resolution_latency_ms`
Czas od kliknięcia bytu do pełnego otwarcia inspektora.
- cel MVP: `< 150 ms`
- cel release: `< 100 ms`

### 14. `poincare_render_fps`
Płynność renderowania powierzchni orbitalnej.
- cel MVP: `>= 30 FPS`
- cel release: `>= 60 FPS` na docelowym sprzęcie

---

## 7.5. Metryki produktowe

### 15. `cold_start_time_s`
Czas od uruchomienia aplikacji do gotowości powierzchni głównej.
- cel MVP: `< 4 s`
- cel release: `< 2.5 s`

### 16. `idle_memory_mb`
Zużycie RAM na biegu jałowym bez dużego modelu.
- cel MVP: `< 500 MB`

### 17. `session_crash_free_rate`
Odsetek sesji bez crasha.
- cel release: `>= 0.99`

### 18. `packaged_install_success_rate`
Odsetek poprawnych instalacji / uruchomień binarki.
- cel release: `>= 0.95`

---

## 8. Priorytety implementacyjne

## Priorytet P0
Stabilizacja i ekstrakcja rdzenia.

## Priorytet P1
Formalny model bytu systemowego i registry.

## Priorytet P2
Autonomy engine oraz jawne ograniczenie LLM do roli tymczasowej.

## Priorytet P3
Geometry engine i odwzorowanie na dysk Poincaré.

## Priorytet P4
Native cockpit MVP.

## Priorytet P5
Hardening produktu i dystrybucja.

---

## 9. Ryzyka

### Ryzyko 1 — zbyt wczesne wejście w UI
Jeśli zaczniemy od renderera, bez ustalenia modelu bytu i geometrii, projekt rozjedzie się semantycznie.

### Ryzyko 2 — brak rozdziału między rdzeniem a shellami historycznymi
Jeśli przeniesiemy wszystko z repo obecnych 1:1, odziedziczymy chaos zamiast produktu.

### Ryzyko 3 — LLM pozostanie ukrytym centrum systemu
Jeśli nie zbudujemy autonomy layer wcześnie, CIEL nie nabierze własnej tożsamości operacyjnej.

### Ryzyko 4 — winding number stanie się dekoracją
Jeżeli nie będzie wynikał z rzeczywistej topologii procesu i konsolidacji, straci sens architektoniczny.

### Ryzyko 5 — geometryzacja bez metryk
Bez mierzalnych wskaźników koherencji, domknięcia i stabilności UI zamieni się w efekt wizualny.

---

## 10. Najbliższy plan roboczy

### Sprint 1
- wyodrębnić czysty backend,
- naprawić model importów,
- stworzyć skeleton nowego repo `ciel-native`,
- spisać `SystemState`, `EntityRecord`, `AutonomyPolicy`.

### Sprint 2
- zrobić parser bytów i registry,
- przypisać sektory i orbity,
- zaprojektować pierwszą wersję winding identity,
- uruchomić raport coverage dla bytów.

### Sprint 3
- zakodować geometry engine,
- uruchomić Poincaré disk view,
- połączyć obiekty i inspektor,
- zacząć pierwszą natywną powierzchnię w Qt/QML.

### Sprint 4
- zintegrować inference layer,
- dodać autonomy routing,
- wprowadzić product shell,
- zbudować pierwszą binarkę MVP.

---

## 11. Konkluzja

Materiał już istnieje. Nie zaczynamy od pustki.

Obecny stan należy potraktować jako:
- **surowy rdzeń obliczeniowy**,
- **przejściowy shell demonstracyjny**,
- **niedokończony model produktu**.

Docelowy ruch jest jasny:
1. zachować i oczyścić rdzeń,
2. nadać bytom tożsamość orbitalną,
3. zbudować autonomy layer,
4. oprzeć wizualizację na dysku Poincaré,
5. zbudować natywny cockpit jako prawdziwy produkt.

To nie jest plan „ładniejszego UI”.  
To jest plan przejścia od surowego systemu do **natywnego relacyjnego produktu orbitalnego CIEL**.
