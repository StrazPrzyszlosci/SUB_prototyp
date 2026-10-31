# Import badań Work — 31 października 2026

Źródło: `SUB_prototyp_badania_postep_20261031.zip`
z manifestem oryginalnych plików SHA-256 i archiwum uzupełniającym
`SUB_prototyp_uzupelnienie_23_20261031.zip`.

**Stan:** import do gałęzi `badania/work-postep-20261031` kompletny
na poziomie wszystkich **57 nowych oryginalnych artefaktów**.
Pozostałe trzy tekstowe dokumenty występujące w źródłowym
pakiecie 60 plików (`README.md`, `AGENTS.md`,
`PROGRAM_30_BADAN.md`) połączono z aktualnymi wersjami
na GitHubie, zamiast je nadpisywać starszą treścią.

Oryginalne pliki przekazano przez natywne API GitHub jako blobs;
**wszystkie 57 SHA Git blobów** zgadzały się z identyfikatorami
oryginalnych źródłowych plików sprawdzonymi podczas importu.
Archiwum Work zweryfikowało sumy SHA-256 wszystkich 60
materiałów wobec `MANIFEST_SHA256.json`.
Nie twierdzimy, że nowe symulacje zostały powtórnie uruchomione
na niezależnym środowisku.

### Wniesione badania

- 056: macierz luk i plan zamknięcia warunkowych rodzin modeli.
- 057 / P20D: konstrukcja 1000×440×500 mm, geometria wkładów
  i tory montażowe w założonych warunkach.
- 058 / P25C: 216 przebiegów i matematyczny limit bariery energii
  dla uproszczonego modelu 0D; **nie gotowy limiter**.
- 059 / P18E: redukcyjny model podatnych wręg i podparć;
  **nie pełny MES docelowej obudowy**.
- 060 / P21D: model 3D gazu, wręg, wkładów i napędu;
  **nie pełne sprzężenie z podatnymi ścianami**.
- 061 / P26D–P27D: dwa subwoofery, odwrócenie/obrót brył
  i niepewność strat pokoju; **nie pomiary pokoju**.

README pełni funkcję tematycznego przewodnika. Wykresy
P20D, P18E, P21D, P25C i P26D umieszczono w rozdziałach
poświęconych ich wynikom. Zmiana zakresu badań jest udokumentowana
w programie P01–P30, indeksie raportów i AGENTS.

### Kontrola końcowa i ograniczenia

Po zapisaniu commitu zweryfikować: liczbę ścieżek, zgodność Git blob
SHA i kompletność referencji, które wskazują na nowe pliki.
Analiza pozostaje komputerowa, bez pomiarów prototypu.
Nie zatwierdza produkcji CNC, zakupu głośników, końcowego
preseta DSP, raportu PDF ani Release 1.
