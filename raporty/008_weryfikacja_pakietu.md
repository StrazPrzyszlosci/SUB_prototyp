# Weryfikacja pierwszego pakietu naukowego

Data: 2026-10-23. Zakres: implementacja, spójność dokumentacji i odtwarzanie;
nie walidacja fizycznego prototypu.

- Pełny przebieg `python3 skrypty/odtworz_wszystko.py` zakończył się poprawnie.
- Zaliczono 54 kontrole modelu bazowego: skalowanie, bilans energii, granica
  analityczna, F3, napięcie, prąd i ruch membrany.
- Dodatkowe kontrole: szereg Taylora i zbieżność FFT sprężyny gazowej,
  zachowanie mechaniki/BL przy zmianie Re, limity na siatce 216 wariantów DSP.
- Liczby wierszy: 24 obudowy, 144 rekordy pasmowe, 216 wariantów DSP,
  72 przypadki gazu i 72 rekordy scenariuszy rezystancji.
- Dziewięć tabel CSV identycznych bajtowo z migawką sprzed ostatniego przebiegu.
  To sprawdzenie odtwarzalności, nie niezależny dowód modelu fizycznego.
- Sprawdzono składnię skryptów, poprawność JSON i istnienie lokalnych odsyłaczy.
- Obejrzano wykresy własne oraz wszystkie dziewięć załączników analizowanego wątku.
- [Manifest](../wyniki/manifest.json) wiąże 26 wejść i 22 wyniki przez SHA-256.
  Brief zachował pierwotny hash; wyniki poprzedniego stanu są w archiwum.

Statyczny przegląd fizyki nie wykazał materialnych błędów RMS/szczyt w obecnych
obliczeniach. W planowanym N7 wykryto potrzebę sumowania promieniowania
membrany i przecieku; [plan naukowy](../PLAN_BADAN_NAUKOWYCH.md) uzupełniono
o zespolone przepływy, geometrię i kontrolę znoszenia w niskim paśmie.
N7 nie został jeszcze wykonany.

Matplotlib zgłasza lokalny problem projekcji 3D. Bieżące wykresy są 2D,
zostały wygenerowane i obejrzane; globalnego środowiska nie zmieniano.

Pozostają otwarte: realne THD, temperatura i kompresja w czasie, rozrzut
egzemplarzy, straty skrzyni, odpowiedź rzeczywistego pokoju i limity użytkowe.
Żadna z powyższych kontroli nie potwierdza tych osiągów gotowego urządzenia.
