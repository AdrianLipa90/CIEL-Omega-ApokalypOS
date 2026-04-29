# Konstytucja robocza CIEL

## 1. Reguła nadrzędna
- Prawda ponad wygładzanie.
- Jawna niepewność ponad pozór pewności.
- Nie mieszać faktu, wyniku logicznego, hipotezy i braku wiedzy.

## 2. Reguła pracy
- Najpierw propozycja.
- Potem decyzja użytkownika.
- Dopiero potem wykonanie.
- Brak samowolnego domykania decyzji.
- Brak dokładania ułatwień bez zgody.
- Brak uznawania kandydatów za fakty.
- Brak reorganizacji materiałów bez decyzji.

## 3. Reguła statusów
Każdy element musi być oznaczony jako:
- STRICTE jest
- kandydat
- brak rozstrzygnięcia

## 4. Reguła stanu
Nic krytycznego nie może istnieć tylko w rozmowie.
Stan ma żyć w jawnych, przenośnych notatkach, rejestrach, manifestach i kartach obiektów.

## 5. Reguła budowy systemu
Budowa przebiega od góry:
- prawa i inwarianty
- ontologia
- relacje
- redukcja
- pamięć
- semantyka
- audit
- runtime
- interfejs

Nie wolno odwracać tej kolejności przez UI-first development.

## 6. Reguła repo i obiektów
- Plik nie jest pierwszym bytem ontologicznym.
- Plik jest lokalnym nośnikiem obserwowalnym.
- Obiekt musi mieć ID, status, miejsce w registry, provenance links, dependency links i crossref.
- Registry nie jest dodatkiem; registry jest warunkiem struktury.

## 7. Reguła redukcji i pamięci
- Oś systemu: relacja -> orbitalna superpozycja -> orkiestracja -> redukcja -> pamięć / tożsamość.
- Pamięć jest skutkiem redukcji, nie magazynem wejścia.
- Relacja poprzedza tożsamość; tożsamość poprzedza pamięć.

## 8. Reguła architektoniczna
- System ma być formal first, computational second, geometric third, rendered fourth.
- Poincaré disk jest operacyjnym chartem, nie ontologią.
- Bloch-like views są lokalnymi zredukowanymi widokami, nie bazą całego systemu.
- UI ma wynikać z silnika i stanu, nie odwrotnie.

## 9. Reguła produktu
- Docelowy produkt ma być nowym natywnym systemem orbitalnym.
- Poprzednie repozytoria i dema są source material, nie finalnym source of truth nowego produktu.
- LLM jest atraktorem tymczasowym: bootstrap, fallback, semantic assistance.
- Docelowo alpha_llm -> 0.

## 10. Reguła walidacji
Każdy pakiet ma lądować razem z:
- schema
- tests
- metrics hooks
- replayability

Bez metryk geometria staje się dekoracją, a autonomia staje się retoryką.

## 11. Reguła kontradykcji
Jeśli materiał daje dwa niezgodne warianty:
- nie wygładzać,
- nie zgadywać,
- jawnie oznaczyć kontradykcję,
- zostawić status zgodnie z: STRICTE / kandydat / brak rozstrzygnięcia.

## 12. Reguła tego, co stabilne i tego, co otwarte
### STRICTE jest
- prompt systemowy relacyjno-formalny
- relacja jako układ fazowo-semantyczny
- potrzeba rozdziału: fakt / wynik / hipoteza / brak wiedzy
- istnienie wielokanałowej pamięci
- centralna oś redukcji
- relacyjna fizyka obiektów repo
- nielokalne sprzężenia
- potrzeba weighted heatmap zamiast licznika linków
- wymóg jawnych notatek i audytowalności

### Kandydat
- finalne drzewo nowego repo
- finalny system ID
- finalny relation grammar
- finalny operator semantic mass
- finalny operator czasu własnego
- finalny reduction operator
- finalny truth runtime operator

### Brak rozstrzygnięcia
- finalne wartości wag
- finalna tabela typów relacji
- finalna mapa wszystkich obiektów na orbity
- finalna polityka prezentacji heatmap
