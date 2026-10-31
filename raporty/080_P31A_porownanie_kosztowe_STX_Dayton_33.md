# Raport 080 — P31A: porównanie 33 konfiguracji głośników, tanich STX i Dayton

**31.10.2026 — wykonano 1980 przeliczeń parametrycznych na 33 konfiguracjach, 100/120 l; to nie jest ranking zmierzonej jakości ani końcowe kryterium zakupu.**

## Cel
Po P29D (raport 075) na bazie zbioru 24+3 SB+6 nowych modeli zweryfikowanych T/S utworzono **33 konfiguracje**. Modele EMS/SUPRAVOX zostały wstrzymane jak w audycie źródeł; PURIFI nie dublowano. Na wszystkich zastosowano te same: idealną skrzynię zamkniętą, zespoloną impedancję, kinematykę membrany, ograniczenia napędu i umowne straty miedziane. Celem jest wskazanie kandydatów do próby równoważnego poziomu dźwięku przy niskim koszcie, NIE utożsamienie wysokiego SPL z małym THD.

## Równania
```text
Cms=Vas/(rho*c²*Sd²)
Mms≈1/((2πFs)² Cms), jeśli fabryczna Mms nieobecna
Rms=(2πFs*Mms)/Qms
BL²≈(2πFs*Mms*Re)/Qes, jeśli BL fabryczne nieobecne
Zm=Rms+j(ωMms−1/(ωCms)−Sd²rho*c²/(ωVb))
Z=Re+jωLe+BL²/Zm
I/U=1/|Z|; v/U=BL(I/U)/|Zm|; Xpeak=√2·|v|/ω
Ubound=min(40V,12A/(I/U),xf·Xmax/(Xpeak/U),sqrt(Pcu/(Re*(I/U)²)))
SPL_2π/1m = 20 log10(rho*f*Sd*|v|/20µPa)
```
Dla Le nieznanego w N01/N09 użyto 0 jako jawnej wartości zastępczej i ich **nie traktować jako pełnego rankingu**. Inne modele używają publikowanych Mms/BL, jeśli są dostępne, lub pochodnych spójności T/S. Sprawdzenie nieliniowości ruchu nie było możliwe.

`33 × 2 pojemności (100,120l) × 3 umowne marginesy X (0.5,0.7,1.0 Xmax) × 2 pułapy strat Pcu (50/100W) × 5 scenariuszy parametrów = 1980` przypadków, każdy obliczony na 9 częstotliwościach 20–80Hz. Nominalne dane i scenariusze stresu są w pliku JSON. Zmieniono BL −10/+10%, Re +5%, Mms +10% i Cms −15% jako jawne stresy. **Nie są to rozkłady z fabryki.**

## Porównanie wybranych modeli w 120l: x<=0.7Xmax, Pcu<=50W

| Model | Cena jednostkowa PL [zł] | Modelowy Vd [cm³] | Idealny 20Hz SPL nom. [dB] | Minimum najgorszego stresu 20–80 Hz [dB] |
|---|---:|---:|---:|---:|
| Dayton RSS390HF-4 | 1613 | 1161 | 98.76 | 98.69 |
| STX W.32.500.8.MC_v2 | 215 | 368 | 88.78 | 88.78 |
| STX W.32.800.8.FCX | 990 | 737 | 94.80 | 94.80 |
| STX W.38.800.8.MC | 578 | 680 | 94.11 | 94.11 |
| Dayton RSS390HE-22 seria | brak | 2171 | 96.30 | 95.36 |

**Ceny orientacyjne brutto w odczycie 31.10.2026:** Dayton RSS390HF-4 1613,33 zł ([polski sklep](https://loudspeakershop.eu/glosnik-dayton-audio-rss390hf-4-15-reference-sub-p-7660.html)), STX W.32.800.8.FCX 990 zł ([STX](https://stx.pl/manufacturer/stx/w-32-800-8-fcx.html)), STX W.38.800.8.MC 578 zł ([STX](https://stx.pl/w-38-800-8-mc.html)), STX W.32.500.8.MC_v2 215 zł ([STX](https://stx.pl/category/glosniki-niskotonowe)). Nie wyceniono całego toru, dodatkowej korekcji DSP, obudowy i modułów klasy D.

### O czym mówi wynik?
1. Ekonomiczny STX W.38.800.8.MC ma ok. 684 cm³ modelowego `Sd·Xmax`, C02 około 1161 cm³. Przy identycznym poziomie bardzo niskiego basu jego membrana musi pracować z większą frakcją deklarowanego Xmax. **Nie da się z tego wywieść wyższego THD**, ale ogranicza to zapas.
2. STX W.32.800.8.FCX ma 8Ω, nie 4Ω — rzeczywista dostępna moc i napięcie modułu muszą być porównane przy 8Ω, nie tylko z tymi samymi 40V/12A.
3. Wynik stresowy jest minimum na pięciu sprzężonych profilach; nie zastępuje zakresów P29A/C, identyfikacji serii ani pomiaru.
4. STX W.32.500.8.MC_v2 jest bardzo tani, ale jego nominalny Xmax 7.5mm i mniejsza membrana mocno ograniczają 20Hz. Nie wolno mylić wysokiej efektywności PA z niskim F3 w zamkniętej skrzyni.
5. Przy **poniżej docelowego SPL** alternatywy ekonomiczne mogą brzmieć równie dobrze. Dopiero pomiar **THD/IMD przy tej samej emisji 20/30/40/60/80Hz**, z kalibracją temperatury, pozwoli ocenić jakość.

## Co blokuje zakup?
Pomiary THD@equal SPL i IMD, skok rzeczywistej liniowości (nie tylko geometria cewki), `Rth/Cth`, właściwości wielotonowe, ceny kompletnych dwóch kanałów i konstrukcji. Dodatkowo brak zatwierdzonych docelowych progów SPL i pomieszczenia nie pozwala obiektywnie wybrać głośnika najtańszego spełniającego wszystkie wymagania.

**Decyzja:** zachować C02 jako warunkowy punkt odniesienia, pozostawić STX C06 oraz tani STX C08 w shortlist; nie zamawiać dwóch Daytonów przed testem zgodności jakości przy jednakowym SPL albo przed sprecyzowaniem, czy brakujące kilka dB zapasu jest konieczne. Pełne 33-konfiguracyjne robust THD/termika to nadal zadanie otwarte.

## Odtwarzanie
`node skrypty/p31a_koszt_i_wspolne_limity_33.js` — bez bibliotek, odtwarza `wyniki/p31a_33_konfiguracje_1980_przypadkow_20261031.json`.
