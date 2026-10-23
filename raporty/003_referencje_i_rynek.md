# Raport 003 — referencje, kandydaci i stan rozpoznania rynku

Stan: 2026-10-23. Typ: odczyt danych producentów i rekomendacje badawcze.
**Sub12 i Sub15 zatwierdzone przez użytkownika w U-009.** Referencje monitorów
odłożone; A8H/S3V są tylko materiałem rozpoznawczym. Nie zakończono badania cen
i dostępności PL/UE; poniższa tabela nie jest listą zakupową.

## Propozycja referencji ADAM Audio

| Model i źródło | Deklaracja widoczna na stronie | Rola proponowana | Braki porównawcze |
|---|---|---|---|
| [Sub12](https://www.adam-audio.com/en/subwoofers/sub12/) |22–150 Hz, dolny punkt−3 dB22 Hz; max peak≥115 dB/1 m; wzmacniacz 200 W RMS | Podstawowy punkt odniesienia subwoofera studyjnego | Pasmo dla maxSPL, sygnał, czas, THD i geometria nieustalone w odczytanym opisie |
| [Sub15](https://www.adam-audio.com/en/subwoofers/sub15/) |20–150 Hz; maxSPL≥120 dB/1 m;1000 W RMS | Ambitniejszy cel headroomu i niskiego pasma | Nie utożsamiać liczby 120 dB z wynikiem przy 20 Hz lub mocą akustyczną ciągłą |
| [A8H](https://www.adam-audio.com/en/a-series/a8h/) | Aktywny 3-way;31 Hz–45 kHz przy−6 dB; summary: peak 105 dB/szt./1 m | Średnia/wyższa seriaA, trójdrożna architektura | Raport pomiarowy i definicja maxpeak wymagają odczytu; nie mieszać ze starszymi deklaracjami |
| [S3V](https://www.adam-audio.com/en/s-series/s3v/) | Aktywny 3-way; summary:≥124 dB/parę/1 m | Wyższy punkt odniesienia dla przyszłych monitorów | Dane dotyczą pary; strona linkuje pomiary i EIA-426 B, wymagają analizy |

Odczyt przez browser-harness, data dostępu 2026-10-23. Są to deklaracje
producenta, nie własne pomiary. SeriaA iS różnią się architekturą, przeznaczeniem
i protokołami; nie wolno wyznaczać rankingu z samych powyższych liczb.

Na stronie S3V skrót pasma 32 Hz–50 kHz pokazuje adnotację−20 dB. Trzeba
sprawdzić pełną specyfikację i wykresy przed użyciem tej wartości w kryterium
odbioru. Braku weryfikacji nie zastępujemy liczbą zapamiętaną z innej rewizji.

## Ilustracja samej zmiany odległości

Przy założeniu propagacji jak źródło w dalekim polu:
`L(r)=L(1m)−20log10(r/1m)`. Ta operacja nie odtwarza pokoju ani modów.

| Katalogowy poziom przy 1 m |2,5 m, przeliczenie [dB]|3 m, przeliczenie [dB]|
|---|---:|---:|
| Sub12:115 dB |107,04|105,46|
| Sub15:120 dB |112,04|110,46|

Znaki≥ są własnością deklaracji producenta; wartości w tabeli ilustrują
przeliczenie podanej liczby. Nie ustanawiają gwarantowanego minimum w pokoju.
Nie są też poziomami 20 Hz ani długotrwałymi. Dla monitorów celowo nie odejmujemy
arbitralnie 3 lub 6 dB od wyniku pary, aby udawać równoważną sztukę.

Do propozycji wymagań potrzebne będą pasmowe krzywe oraz definicje sygnałów,
czasów i progów zniekształceń. Poziomy S1/S2/S3 z planu są scenariuszami
projektowymi; ciągłego SPL nie wyprowadzamy z deklarowanego peak.

## Kandydaci do obliczeń

| Model | Rozmiar/impedancja |Fs [Hz]|Vas [l]|Qts katalogowe|Sd [cm²]| Ruch przyjęty w modelu | Pe katalogowe | Cena brutto/dostępnośćPL/UE |
|---|---|---:|---:|---:|---:|---|---|---|
| [RSS315HF-4](https://www.daytonaudio.com/product/121/rss315hf-4-12-reference-hf-subwoofer-4-ohm) |12″/4Ω|24,2|84,1|0,39|514,7|14,3 mm, założenie one-way|400 W|Do sprawdzenia|
| [RSS390HF-4](https://www.daytonaudio.com/product/126/rss390hf-4-15-reference-hf-subwoofer-4-ohm) |15″/4Ω|19,5|212|0,43|829,6|14,0 mm, założenie one-way|500 W|Do sprawdzenia|
| [RSS315HFA-8](https://www.daytonaudio.com/product/123/rss315hfa-8-12-reference-hf-subwoofer-8-ohm) |12″/8Ω|22,2|97,2|0,45|506,7|14,3 mm, założenie one-way|400 W|Do sprawdzenia|
| [SB34SWPL76-4](https://sbacoustics.com/wp-content/uploads/2022/03/12in-SB34SWPL76-4.pdf) |12″/4Ω|19|79|0,32|458|30 mm p-p→15 mm peak|300 W|Do sprawdzenia|

Pe nie porównuje automatycznie obciążalności w identycznych warunkach.
Katalogowe Qts jest zachowane; model liczy Qts zQes/Qms, stąd małe różnice.
Pełny zestawT/S, źródła i konflikty: [kandydaci.json](../dane/przetworniki/kandydaci.json).

RSS390HF-4 daje większeSd·Xmax, HFA8 daje odmienny kompromis napięcia i dobroci,
a SB ma pełną kartę z jawną definicją ruchu p-p. To powody włączenia do
porównania, a nie uzasadnienie zakupu. Nie znamy jeszcze porównywalnegoTHD,
kompresji i końcowych cen. Nie wykazano, że którykolwiek jest najtańszy wystarczający.

## DSP i napęd

[Aktualna strona Flex Eight](https://www.minidsp.com/products/minidsp-in-a-box/minidsp-flex-eight)
opisuje osiem wyjść analogowychRCA, wejścia cyfrowe i opcjonalną łącznośćDante.
Opis znaleziony 2026-10-23 różni się zakresem opcji od starszych materiałów.
Sprawdzić konkretną rewizję, instrukcję, routing, poziomy i ochronę; nie
zakładać dostępności zbalansowanych wyjść ani kompletu potrzebnych limiterów.

Hypex iICEpower pozostają rodzinami do researchu. W tej iteracji nie odczytano
kompletu kart konkretnych modułów i zasilaczy, więc nie rekomendujemy modelu
ani nie przypisujemy im hipotetycznego napędu 40 Vrms/12 Arms z symulacji.

## Uzupełnienie rynku

Każda oferta ma zawierać: sprzedawcę, model/rewizję/impedancję, cenę brutto,
walutę, kurs z datą, dostawę doPolski, stan magazynowy i termin, warunki serwisu
oraz datę odczytu. „Produkt na stronie” nie znaczy „dostępny od ręki”.

Najpierw wyznaczyć zbiór spełniający uzgodnione wymagania. Następnie liczyć
koszt kompletnego prototypu i wskazać Pareto: koszt kontra pasmowy headroom,
gabaryty, masa i niepewność. CenyUSA/MSRP nie są kosztorysemPLN.

## Najważniejsze otwarte decyzje

Zatwierdzone referencje: Sub12/Sub15. Nie oznacza to automatycznej akceptacji
wszystkich katalogowych parametrów jako wymagań. Progi pasmowe i protokoły
trzeba zaproponować osobno. Do wyboru referencji monitorów wrócimy później.
