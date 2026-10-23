# Raport 002 — pierwsze obliczenia elektroakustyczne

Data: 2026-10-23. **Status: model liniowy przed budową, bez wyników pomiarów.**
Przebieg: 4 przetworniki dwóch producentów × 6 objętości = 24 konfiguracje;
144 wiersze pasmowe. Wejścia z [kart producentów](../baza_wiedzy/ZRODLA.md)
i [konfiguracji](../dane/konfiguracje/badania_wstepne.json).

## Założenia wspólne

Sealed, sztywne szczelne ściany, bez bonusu podatności wypełnienia. Objętość
netto 30/45/60/80/100/120 l. Napęd hipotetyczny 40 Vrms/12 Arms, dodatkowy orientacyjny
limit napięcia sqrt(Pe·Znom). Napięcie odniesienia 2,83 Vrms. Brak nagrzewania,
kompresji, BL(x), Cms(x), Le(x), THD i zidentyfikowanej transmitancji pokoju.

Wartości SPL to **RMS osobnego sinusa**, idealny mały monopól w półprzestrzeni
2π w odległości 1 m. Założenie geometrii nie jest wynikiem pomiaru ani symulacją
mieszkania. Przeliczenia 2,5–3 m i room gain 0/+3/+6 dB są osobnymi scenariuszami.

## Kontrola wejść

Tabela WWW RSS315HF-4 zawiera BL=1 Tm. Z wybranego zestawu parametrów modelu
Fs/Qes/Qms/Vas/Sd/Re wynika 14,22 Tm; przy katalogowym Mms 188 g także nie otrzymuje
się 1 Tm. Wartość 1 Tm odrzucono jako niespójną, a BL w modelu jest jawnie wyprowadzane.
Następnie Firecrawl odczytał oryginalny PDF: **BL=13,99Tm**. Kontrola
katalogowa używa teraz PDF; wartość 1Tm z WWW zachowano jako konflikt źródeł.
Model wyprowadza14,22Tm ze spójnego zestawu pierwotnego. Nie twierdzimy,
że którakolwiek z tych wartości jest pomiarem naszej sztuki.

Dla tego samego modelu Mms wyprowadzone 193,0 g różni się od katalogowego 188 g
o 2,66%. Rozbieżność zachowano; niewielkie zaokrąglenia, warunki powietrza
i nadmiarowość katalogowego zestawu mogą mieć znaczenie. Cała tabela:
[spojnosc_ts.csv](../wyniki/spojnosc_ts.csv).

SB34SWPL76-4 podaje **30 mm p-p** linear coil travel. W modelu użyto 15 mm
jednostronnie; nie 30 mm. Jest to inna informacja niż próg THD lub pomiar BL(x).
Katalogowy wykres SB przedstawia odpowiedź i impedancję w warunkach IEC baffle,
mikrofon 31,6 cm, SPL znormalizowany do 2,83 V/1 m; nie krzywą maksymalnego SPL.

## Porównanie 60 l netto

Wyniki Fc/Qtc/F3 dotyczą idealnego modelu 2. rzędu, bez Le. Kolumny SPL i prądu
w CSV pochodzą z pełniejszego modelu ze stałym Le.

| Kandydat | Fc [Hz] | Qtc | F3 [Hz] | Sd·Xmax [l] | Maks. gain przykładu DSP10–200 Hz [dB] |
|---|---:|---:|---:|---:|---:|
| Dayton RSS315HF-4 |37,50|0,602|45,18|0,736|4,81|
| Dayton RSS390HF-4 |41,52|0,913|34,15|1,161|4,49|
| Dayton RSS315HFA-8 |35,93|0,719|35,36|0,725|3,09|
| SB Acoustics SB34SWPL76-4 |28,92|0,482|47,37|0,687|3,68|

Przykład DSP: LT do 25 Hz/Q0,707 +HP Butterworth 2 przy 18 Hz +LP LR4 przy 80 Hz.
Te parametry służą badaniu kosztu korekcji; nie zostały zatwierdzone i nie są
gotowym presetem do wgrania. Maksimum gain dotyczy łącznej krzywej filtrów,
a nie samego LT. Cele należy rozszerzyć po uzgodnieniu wymagań.

## Granice modelu, 60 l, hipotetyczny napęd

| Kandydat |20 Hz SPL RMS 2π/1 m [dB]| Ograniczenie 20 Hz |40 Hz SPL RMS 2π/1 m [dB]| Ograniczenie 40 Hz |
|---|---:|---|---:|---|
| RSS315HF-4 |97,92|Xmax|109,59|40 Vrms|
| RSS390HF-4 |101,89|Xmax|113,14|40 Vrms|
| RSS315HFA-8 |97,79|Xmax|106,94|40 Vrms|
| SB34SWPL76-4 |97,33|Przyjęte 15 mm|106,57|Przybliżenie sqrt(Pe·Znom)|

To granice matematycznego modelu, **nie potwierdzony użyteczny maxSPL**.
Brak THD i termiki uniemożliwia ocenę jakości przy tych poziomach.
Porównanie przy wspólnym 40 Vrms nie jest jednocześnie porównaniem przy wspólnej
mocy znamionowej, szczególnie dla wariantu 8Ω. Moc i prąd są w CSV oddzielnie.

Idealne odejmowanie odległości: −7,96 dB dla 2,5 m i−9,54 dB dla 3 m względem 1 m.
Nie daje to prognozy sweet spotu w pokoju. Dla dwóch źródeł suma zależy od
fazy i transmitancji; nie dodajemy automatycznie 6 dB do całego pasma.

## Wnioski modelowe

1. RSS390HF-4 ma ok.1,58× większe Sd·Xmax niż RSS315HF-4, co w idealnej
   granicy ruchu odpowiada około 3,96 dB przewagi. Nie gwarantuje podobnej różnicy
   niskiego THD, odporności cieplnej ani kosztu.
2. 60 l dla 15″ daje Qtc≈0,913. Należy porównać 80–120 l, zanim ustali się litraż
   platformy. W120 l uzyskamy łagodniejszą dobroć, lecz większą skrzynię.
3. Samo niskieFs nie rozstrzygaF3. SB przy 60 l ma niższeFc, ale silne tłumienie
   daje szerzej opadającą odpowiedź i F3≈47,37 Hz. Wymaga oceny z korekcją.
4. Powiększanie skrzyni nie zwiększa Sd·Xmax. W dolnym paśmie może zmniejszyć
   potrzebne napięcie i przesunąć aktywny limit; nie tworzy dodatkowego ruchu.
5. DużeLeSB wymaga ostrożności w wyższym paśmie. Obecny model stałej
   indukcyjności nie zastąpi zmierzonej impedancji.

Rekomendacja obecnej iteracji: utrzymać porównanie 12″/15″, sprawdzić katalogowe
braki i ceny, następnie zawęzić litraż z rzeczywistym napędem. Nie ma jeszcze
podstaw do wskazania najtańszego wariantu spełniającego niezatwierdzone progi.

## Geometria poglądowa i wykonawca

| Wariant | Wewnętrzne W×H×D [mm] | Zewnętrzne [mm] | Brutto wewnętrzne [l] | Założone wyparcie głośnik+wręgi [l] | Netto przed modułami [l] |
|---|---|---|---:|---:|---:|
| K1 |400×400×450|436×436×504|72,000|4+3|65,000|
| K2 |460×460× 640|496×496× 694|135,424|6+5|124,424|

Płyty 18 mm, front 36 mm jako 2×18. Wyporności są **założeniami projektowymi**,
nie objętościami ze sprawdzonego modelu kosza. Skrzynie nie są zoptymalizowane,
rozpisane na formatki ani gotowe do CNC. W K1 zmiana netto 65→45 l wymaga
20 l dodatkowego sztywnego wyparcia; K2 pozwala badać większy zakres za cenę
masy i gabarytów. Szczegóły technologiczne: [wykonawca](../WYKONAWCA_CNC.md).

## Pokój i wrażliwość

Prostopadłościan 4,6×3,7×2,5 m, c 343 m/s: pierwsze mody osiowe 37,28/46,35/68,60 Hz.
To częstotliwości modelu idealnego, bez amplitud, szerokości i czasów zaniku.
Nie znamy rzeczywistego room gain ani wpływu perforowanego sufitu i mebli.

[Tabela czułości](../wyniki/wrazliwosc_ts.csv): zmianyFs±5%, Qes/Vas±10%
jednego parametru pierwotnego naraz, przy ponownym wyprowadzeniu pozostałych.
Są to założone zakresy do badania odporności projektu, nie tolerancje producentów
ani przedziały ufności. W tej iteracji nie wykonano MonteCarlo.

## Weryfikacja i odtwarzanie

`python3 skrypty/sprawdz_model.py`: **54 kontrole** skalowania, bilansu energii,
zgodności z modelem analitycznym dlaLe→0, granic napięcia/prądu/Xmax i wzorów.
Nie jest to walidacja fizycznego produktu ani niezależny pomiar.

```bash
python3 skrypty/odtworz_wszystko.py
```

- [Porównanie24obudów](../wyniki/porownanie_obudow.csv).
- [Pasma, EQ, wychylenie, prądy i granice](../wyniki/pasma_i_limity.csv).
- [Odpowiedzi i granice modelu PNG](../wyniki/01_objetosc_i_granice_modelu.png).
- [Przykład DSP PNG](../wyniki/03_przyklad_dsp.png).
- [Mody pokoju](../wyniki/mody_pokoju.csv).
- [Manifest przebiegu](../wyniki/manifest.json).

Do niezależnego sprawdzenia w następnej iteracji: osobny kalkulator/narzędzie
z identycznymi wejściami, definicjami i geometrią. Zgodność własnego kodu z
własnymi kontrolami nie dowodzi poprawności wszystkich założeń.
