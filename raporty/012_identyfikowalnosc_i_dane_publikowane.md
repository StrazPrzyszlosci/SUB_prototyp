# Raport 012 — identyfikowalność i opublikowane parametry

Stan:2026-10-24. Kod:[audyt_identyfikowalnosci.py](../skrypty/audyt_identyfikowalnosci.py).
Rozdzielamy dowód modelowy, dane opublikowane i eksperyment syntetyczny.

## Nieidentyfikowalność z samej impedancji w wolnym powietrzu

```text
Z(s)=Re+s*Le+(B²/M)*s/(s²+(R/M)*s+K/M)
```

Przekształcenie B→sqrt(alpha)B, M→alpha*M, R→alpha*R, K→alpha*K
nie zmienia tej funkcji. Jakobian kombinacji B²/M,R/M,K/M ma rząd 3
dla 4 niewiadomych. Symbolicznie sprawdzono wektor zerowy[B/2,M,R,K].
Nie wolno więc uważać wszystkich parametrów mechanicznych wyprowadzonych
z jednej impedancji za niezależnie zmierzone.

Gdy Re,Le,Sd są znane, dwa idealne znane Vb przełamują tę swobodę:
różnica zidentyfikowanych współczynników Keff/M jest równa
`(Kb1-Kb2)/M`. Wykonano osobne dopasowanie liniowego układu równań
do syntetycznych zespolonych impedancji 60/100 l dla 24 modeli.
Maksymalny względny błąd odzyskania Mms: 4.77e-15.
To nie jest próba z szumem ani pomiar egzemplarzy. Współczynników nie
odczytuje się po prostu z położenia szczytu impedancji.

Przy nieznanym Sd istnieje dalsza swoboda: równoległa zmiana Sd i parametrów
mechanicznych może zachować zarówno impedancję znanej skrzyni, jak i SPL,
zmieniając faktyczny ruch. Test numeryczny potwierdził taki kontrprzykład.
Do identyfikacji potrzebna jest dodatkowa informacja geometryczna, masa
lub niezależny pomiar ruchu. Nie dodajemy fikcyjnych wartości do danych.

## Dane publikowane Scan-Speak 32W/4878T00

Obejrzano strony 2–5 oryginalnego skanuVoiceCoil z 2013 roku,
[źródło](https://www.scan-speak.dk/datasheet/reviews/32W-4878T00-VoiceCoil_2013-3.pdf).
Zachowano wspólne zestawy dwóch próbek i metodTSL/LTD. Nie zrobiono
z dwóch egzemplarzy rozkładu tolerancji produkcyjnej. Tekst podaje ograniczenia
XBl 70%=14.9 mm iXC50%=12.3 mm dla przyjętego tam kryterium 20%.
Nie oznacza to niskiego THD przy 12.3 mm. Nie przyjęto automatycznych tablic
wartości z wykresów, w tym niezweryfikowanegoTHD20 Hz z ekstrakcji.

Policzono 30 klasycznych projekcji kształtu
odpowiedzi 2.rzędu dla tabeli źródłowej i aktualnej karty. Nie jest to odtworzenie
częstotliwościowo zależnegoLEAP5LTD ani jego modeli wypełnienia.
Dla 50 l fabryczny zestaw dajeF3 około 40.39 Hz, a dwie klasyczne projekcje
zmierzonychTSL około 37.38 i 38.81 Hz. Ta różnica jest większa od błędu
numerycznego samego rozwiązania; nie wolno nadawać ostatnim cyfrom znaczenia
większego niż jakość danych.

Wnioski dla prototypu: porównywać wspólne zestawy parametrów, rozróżniać
metodę i egzemplarz, kontrolowaćSd i rzeczywisty litraż, badać szczelność
przed identyfikacją podatności. Znana geometria i sterowalna objętość mają
wartość identyfikacyjną; nie zastępują późniejszego pomiaru.

Dane:[publikacja](../dane/zrodla/pomiary_opublikowane/scan32_voicecoil_2013.json).
Wyniki:[identyfikacja](../wyniki/p03_identyfikacja_syntetyczna.csv),
[projekcje](../wyniki/p03_scan32_zestawy_opublikowane.csv),
[kontrole](../wyniki/p03_identyfikowalnosc.json).
