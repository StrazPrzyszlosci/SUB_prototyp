# Raport 038 — SB Acoustics: rozszerzenie i porównywalne obliczenia

Stan: 2026-10-26. **Dane producenta i symulacja liniowa**, bez pomiarów
urządzenia. Do C04 SB34SWPL76-4 dodano dwa produkty: C25 SB34SWNRX-S75-6
i C26 SB34SWPL76-3-DV. C26 ma osobno połączenie równoległe C26P i szeregowe
C26S. Pula liczy teraz **26 produktów od 11 producentów, 27 konfiguracji
elektrycznych; trzy produkty SB Acoustics**. Cztery STX pozostają w puli.
Historyczne duże kampanie obejmują nadal pierwotne 24 bazy.

## Co zmienia rozszerzenie

**Wynik modelu:** C25 ma mniejsze katalogowe Sd·Xmax od C04, choć większe Sd
i mniejsze Le. W przyjętym eksperymencie traci około 1,60 dB granicy ruchu
przy 20 Hz, ale przy 80 Hz osiąga wyższą granicę liniową niż C04. C26P
i C26S zachowują ten sam skok objętościowy; zmieniają wymagania prądu
i napięcia. Nie ma jednego zwycięzcy całego briefu na podstawie tych danych.

**Rekomendacja badawcza:** zachować wszystkie trzy produkty SB do porównania,
z osobną kwalifikacją połączeń C26. C25 jest wartościowym kontrprzykładem
wyboru wyłącznie według Sd lub Le. Nie zmienia to U-021: prototyp otrzyma
jeden stały front po końcowym wyborze, a nie front do zamiany głośników.

## Dane pierwotne i konflikty

Oryginalne PDF pobrano przez browser-harness i obejrzano po wyrenderowaniu
strony 1: tabelę, rysunek, wykresy, legendy i przypisy. Firecrawl służył
do wyszukania i ekstrakcji tekstu. **Automatyczne tablice punktów krzywych
odrzucono**; nie przeprowadzano digitalizacji tych wykresów.

| Model | Źródło producenta | Istotne rozróżnienie |
|---|---|---|
| C25 SB34SWNRX-S75-6 | [PDF REV. 0, 17.10.2012](https://sbacoustics.com/wp-content/uploads/2020/11/12in-SB34SWNRX-S75-6.pdf) | PDF: 22,5 mm p-p; [strona WWW](https://sbacoustics.com/product/12in-sb34swnrx-s75-6-norex/): 22 mm p-p. Model używa 11,25 mm peak z PDF; alternatywa 11 mm jest zachowana |
| C26 SB34SWPL76-3-DV | [PDF REV. 1, 03.10.2017](https://sbacoustics.com/wp-content/uploads/2020/03/12in-SB34SWPL76-3-DV.pdf) | Re = 2 × 2,5 Ω; Le parallel/series = 1,4/6,1 mH. Moc 300 W w PDF ma dopisek **ser.**; brak osobnego potwierdzonego limitu parallel |

Różnica 11/11,25 mm odpowiada **0,195 dB** samego pułapu ruchu, kiedy
aktywny jest X. Nie jest to tolerancja egzemplarzy ani dokładność fizycznego
Xmax. Dla C25 wyprowadzone Mms różni się od tabeli o +1,57%, a Cms o −2,48%;
dla C26 odpowiednio +0,20% i +3,36%. Zachowano jeden spójny zestaw bazowy
Fs/Qes/Qms/Vas/Sd/Re zamiast mieszać zaokrąglone wartości pochodne.

Le series/parallel ma stosunek około 4,36 zamiast dokładnie 4. Dwa wpisy
katalogowe zachowano oddzielnie. Nie odtworzono z nich wspólnej macierzy
cewek, nie skorygowano tabeli i nie zidentyfikowano zależności Le(x,f,i).

## Metoda i dziedzina obliczeń

Policzono **5832 punkty**: 27 konfiguracji × 9 Vb × 6 częstotliwości ×
2 budżety napędu × 2 udziały skoku katalogowego. Vb netto powietrza:
20/30/45/60/80/100/120/150/200 l. Częstotliwości: 20/25/31,5/40/63/80 Hz.
Budżety: 40 V RMS/12 A RMS i 60 V RMS/20 A RMS; skok 0,7 lub 1,0 Xmax.
Wariant 0,7 nie oznacza zidentyfikowanej granicy niskiego THD.

Każdy punkt jest **osobnym sinusem ustalonym**, bez ograniczenia czasu
w liniowym modelu. Nie potwierdza to możliwości ciągłej pracy fizycznego
głośnika. Ciśnienie jest RMS idealnego monopola 2π, 1 m; Xmax jest peak.
Nie ma sumowania dwóch subwooferów, pokoju, wypełnienia, podatności ścian,
limitu Pe, kompresji cieplnej, clippingu i ochrony dynamicznej.

Zachowano równania modelu bazowego:

    K = 1/Cms + rho*c²*Sd²/Vb
    Zm = Rms + j*(omega*Mms - K/omega)
    Z = Re + j*omega*Le + BL²/Zm
    I = U/Z; v = BL*I/Zm; x_peak = sqrt(2)*abs(v)/omega
    p_RMS = rho*omega*Sd*abs(v)/(2*pi*r)
    U_allowed = min(Umax, Imax/abs(I_at_1V), Xallowed/x_peak_at_1V)

C26P: Re=1,25 Ω, nominalnie 1,5 Ω; C26S: Re=5 Ω, nominalnie 6 Ω.
Qes pozostaje wspólne zgodnie z tabelą. BL wyprowadzono ze spójnych T/S,
a wartości katalogowe porównano w audycie. Nie uzupełniano nieznanej mocy
parallel. Adapter obliczeniowy nie ma pola limitu termicznego.

## Czytelny wycinek wyników

Wspólne **100 l netto, 40 V RMS/12 A RMS, Xpeak ≤ katalogowe Xmax**;
osobne sinusy, RMS, 2π/1 m. Liczby nie są wymaganiami briefu lub SPL w pokoju.

| Konfiguracja | Sd·Xmax [l] | Qtc, wzorzec Le=0 | 20 Hz [dB; limit] | 40 Hz [dB; limit] | 80 Hz [dB; limit] |
|---|---:|---:|---|---|---|
| C04 SB34SWPL76-4 | 0,687 | 0,423 | 97,33; X | 107,79; V | 111,49; V |
| C25 SB34SWNRX-S75-6 | 0,572 | 0,517 | 95,73; X | 107,77; X | 112,93; V |
| C26P SB34SWPL76-3-DV parallel | 0,687 | 0,569 | 97,33; X | 109,37; X | 108,55; I |
| C26S SB34SWPL76-3-DV series | 0,687 | 0,569 | 97,33; X | 106,59; V | 110,44; V |

W C26P przy 80 Hz wiąże prąd, w C26S napięcie. Żadne połączenie nie jest
automatycznie najlepsze przy wszystkich częstotliwościach i napędach.
Niższe F3 samego wzorca Le=0 nie rozstrzyga zapasu po EQ i ograniczeniach.
Plateau 20 Hz po zwiększaniu Vb pojawia się po osiągnięciu granicy ruchu:
dalszy litraż nie zwiększa Sd·Xmax. Dziewięć Vb nie dowodzi globalnego
optimum ani monotoniczności dowolnej odpowiedzi w ciągłej przestrzeni projektu.

![Porównanie dodatkowych SB z odniesieniami C01 i C02](../wyniki/61_SB_porownanie_i_objetosc.png)

Identyfikatory C01/C02 na lewym panelu to Dayton RSS315HF-4/RSS390HF-4.
Pełne zestawienie wszystkich konfiguracji jest w CSV, a nie w gęstej galerii
27 linii. Nie przeniesiono wyników do pokoju 4,6 × 3,7 × 2,5 m.

## Niezależne kontrole i przypadki graniczne

- **1458 punktów** sprawdzono przez bezpośredni układ trzech równań I/v/x,
  zamiast eliminacji Zm; największa względna różnica około 5,4e−15.
- Bilans wejścia Re(U·conj(I)) = Re·|I|² + Rms·|v|²: względna reszta
  około 2,2e−15. Obejmuje model efektywnych strat, nie identyfikację ciepła.
- Le=0 redukuje się do analitycznego modelu drugiego rzędu: różnica około
  2,0e−15. Qtc/F3 w tabelach oznaczają właśnie ten wzorzec.
- W idealnym modelu identycznych cewek przełączenie parallel→series przy
  podwojonym U zachowuje ruch, gdy Re i Le rosną czterokrotnie, a BL dwukrotnie.
  Sprawdzono 2000 częstotliwości 0,01–20 000 Hz. To kontrola algebraiczna,
  **nie prognoza pasma tłokowego do 20 kHz**. Wariant używa Le_series=5,6 mH
  wyłącznie do tej tożsamości; właściwe obliczenia zachowują katalogowe 6,1 mH.
- Historyczne 24 konfiguracje przy 100 l i 20/40 Hz odtworzono bez zmiany
  liczb. Nie ponawiano dawnych wielkich kampanii. Każdy nowy punkt spełnia
  własne limity V/I/X w granicach precyzji numerycznej.

Niepewność rzeczywistych T/S, BL/Kms/Le, chłodzenia i użytecznego skoku
pozostaje otwarta. Ta kampania nie jest rozszerzeniem obwiedni P06 ani
modelem nieliniowym P12–P16 dla nowych produktów.

## Opinie i ograniczenia źródeł

**C25:** na stronie sklepu znaleziono jedną relację kupującego z 19.09.2016,
opisującą pozytywnie pracę w istniejącej obudowie wentylowanej. Nie jest to
test laboratorium lub wniosek o jakości sealed. Rekomendacja litrażu przez
sklep to odrębny tekst handlowy, nie pomiar właściciela.
[Źródło relacji](https://www.madisoundspeakerstore.com/approx-12-subwoofers/sb-acoustics-sb34swnrx-s75-12-woofer/).

**C26:** odczytany fragment dyskusji zawiera pytanie o dokładny model,
nie udokumentowany wynik użytkowania.
[Dyskusja DIYMobileAudio](https://www.diymobileaudio.com/threads/best-budget-items-in-car-audio.140112/page-3).
Forum Zelfbouwaudio zwróciło **503 i dostęp tylko dla zalogowanych**;
nie uznano tekstu z wyniku wyszukiwarki za przeczytany wątek.
[Niedostępny wątek](https://zelfbouwaudio.nl/forum/viewtopic.php?t=31643&start=25).

**Porównanie C04/C25:** znaleziony wątek pyta o THD w 180 l sealed;
widoczne odpowiedzi dotyczą przeniesienia pytania do właściwego działu.
Nie ma tam odczytanego testu porównawczego.
[Dyskusja diyAudio](https://www.diyaudio.com/community/threads/differences-between-sba-sb34swpl76-4-and-sb34swnrx-s75-6.435577/).
Brak odczytanej odpowiedzi nie dowodzi nieistnienia danych gdzie indziej.

## Geometria, dalsza decyzja i artefakty

Oba dodatkowe modele mają w rysunkach nominalny zewnętrzny obrys Ø346,2 mm
i korpus Ø305,2 mm. C25 ma masę netto 5,85 kg i głębokość całkowitą 156 mm;
C26 7,7 kg i 166,7 mm. Nie wolno przenieść masy ani sztywności kosza C04
do ich modeli mechanicznych bez osobnej aktualizacji. Rysunki nie ustalają
luzu technologicznego otworu lub miejsca obu skrzyń przy monitorach.

**Następny krok tej gałęzi:** zbadać odporność porównania nowych SB na
niepewność oraz wspólne wymagania V/I/X/chłodzenia, zanim powstanie krótka
lista. Główny otwarty krok mechaniczny pozostaje lokalna geometria stałego
połączenia front–korpus, potem regulacja Vb i pełna integracja programu.

- [Nowe wejścia](../dane/przetworniki/rozszerzenie_SB_20261025.json),
  [pochodzenie i ocena opinii](../dane/zrodla/SB_rozszerzenie_pochodzenie.json).
- [5832 punkty](../wyniki/sb_rozszerzenie_scenariusze.csv),
  [podsumowanie 27 konfiguracji](../wyniki/sb_rozszerzenie_podsumowanie.csv),
  [audyt T/S](../wyniki/sb_rozszerzenie_spojnosc_TS.csv),
  [kontrole i hashe](../wyniki/sb_rozszerzenie_weryfikacja.json).
- Odtworzenie: `OPENBLAS_NUM_THREADS=1 python3 skrypty/analiza_rozszerzenia_SB.py`.
  Bez zmiany briefu, dawnych danych i fizycznej kwalifikacji wzmacniacza.
