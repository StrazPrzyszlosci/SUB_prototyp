# Raport 076 — P30A–C: wybór obudowy pierwszego prototypu, zbieżne kontrole geometryczne, mechaniczne i akustyczne

**31 października 2026. Badania numeryczne, bez pomiarów urządzenia. NIE jest dokumentacją do CNC ani zatwierdzeniem bezpieczeństwa.**

## Cel i stan poprzednich badań

Projekt: dwa oddzielne subwoofery zamknięte, Dayton RSS390HF-4 (C02) jako wstępny faworyt, regulowane około 100/120/150 l netto, całkowita głębokość wraz z osłoną i terminalem <=500 mm. Punkt odniesienia: `raporty/057_P20D_geometria_dostep_i_pelna_glebokosc.md` (1000×440×500 mm, 50-mm mata), `raporty/059_podatne_wregi_i_panele.md` (skończona sztywność wręg) i `raporty/075_P29D_rekomendacja_kandydatow_i_objetosc.md`. Nie opieramy prototypu na przestarzałym wariancie 880×480×500 mm, który nie mieścił zakładanej osłony w pełnym limicie.

## P30A — realny z punktu widzenia modelu plan montażu i litrażu

Wykorzystano 11 AABB wręg i 20 zamkniętych wkładów z P20D (16 dużych 210×150×100 mm, cztery małe 180×100×100 mm), kosz zastąpiono konserwatywnym prostopadłościanem, a obudowa ma front 44 mm i pozostałe ścianki 22 mm. Przeprowadzono **sześć badań geometrii**: w każdej z nich wyliczono objętości brutto, wyparcie wręg, wkładów, materiału stałego maty, nominalną wyporność kosza 5 l, osprzętu 0,175 l oraz przedziały stresowe. Wszystkie podane wymiary to **korpus W×D×H**, nie kolejność dla ustawienia pionowego.

| W×D×H korpusu [mm] | Grubość maty [mm] | Netto: stan ~150 l | ~120 l | ~100 l | Najgorszy pełny obrys [mm] | Rezerwa do 500 [mm] |
|---|---:|---:|---:|---:|---:|---:|
| 1000×440×500 | 50 | 149,61 | 119,46 | 100,11 | 496 | **4** |
| 1000×435×500 | 45 | 147,47 | 117,32 | 97,97 | 491 | **9** |
| 1020×435×500 | 45 | 150,83 | 120,68 | 101,33 | 491 | **9** |
| **1040×430×500** | **40** | **151,97** | **121,82** | **102,47** | **486** | **14** |
| 1050×425×500 | 35 | 151,38 | 121,23 | 101,88 | 481 | **19** |
| 1055×420×500 | 30 | 149,94 | 119,79 | 100,44 | 476 | **24** |

Głębokość jest sumą modelową `Dcałość = Dkorpusu + wystawanie 10..22 mm + katalogowe Xpeak 14 mm + szczelina 5 + ugięcie 2 + osłona 3 + tył 0..8 + tolerancja 2`. Rzeczywiste elementy i ich statyczne wystawanie nie są zidentyfikowane. **14 mm luzu w modelu nie jest tolerancją produkcyjną**.

Dla starego wariantu 1000×440 oraz trzech płytszych 1020×435, 1040×430, 1050×425 otrzymano po **20/20 udanych torów translacyjnego wkładania modułów**, po 270 segmentów. Kontrola używa ciągłych brył omiatanych i obwiedni +3 mm. Nie symuluje dłoni, śrubokręta, elastycznych przewodów, zamków, śrub, kosza o rzeczywistej geometrii, tolerancji klejenia, skręcania elementu czy opuszczania pod własnym ciężarem.

**Kluczowa zależność:** skracając głębokość utrzymaliśmy dotychczasowe przejścia **kosztem grubości tylnej maty 50→40/35/30 mm**. Brak pomiarów oporu przepływu i podatności materiału oznacza, że nie wolno zakładać, iż te warianty zachowają jednakowe tłumienie. Wydłużenie korpusu w osi szerokości także wpływa na mody poprzeczne i sztywność.

## P30B — niezależny ekran płyt: 180 scenariuszy i test zbieżności

Dla sześciu wymiarów przebadano `5 E(1,5–4 GPa) × 3 rho(650–800 kg/m³) × 2 zakresy idealnego podparcia` = **180 stanów**. Wykorzystano klasyczną, izotropową teorię cienkiej płyty Kirchhoffa-Love'a w warunku SSSS, bez modelowania sprzężonej wręgi. Analiza pojedynczej płyty pod obciążeniem równomiernym jest odrębnym ekranem pomocniczym, **nie dowodem odpowiedzi całej konstrukcji**.

`D = E*t³ / [12(1−nu²)]`, `f11 = π/2 sqrt[D/(rho*t)]*(1/a²+1/b²)`, `t=22mm`, `nu=0,3`.

| Korpus | f11 niepodzielonej górnej płyty, E=2,1GPa [Hz] | f11 dla *idealnego* pola 300 mm [Hz] | Ugięcie środka niepodzielonej płyty, p=1kPa [µm] |
|---|---:|---:|---:|
| 1000×440 | 146,21 | 323,88 | 110,87 |
| 1040×430 | 151,75 | 330,95 | 102,04 |
| 1050×425 | 155,15 | 334,70 | 97,31 |

Ugięcie wyliczono niezależnym szeregiem Naviera dla ciśnienia równomiernego, w dwóch obcięciach 11 i 21: maksymalna różnica względna po rodzinie sześciu wariantów **0,014%**. Jest to wewnętrzny test zbieżności analitycznego przybliżenia statycznego.

**Krytyczna korekta interpretacyjna:** wcześniejsze P18E, zawierające skończenie podatne wręgi, uzyskało około 143 Hz, a nie ~395 Hz przypisywane wcześniej idealnym małym płytom. Dlatego nie należy wykorzystywać wyników 331–335 Hz do prognozy drgań całego prototypu. Są ilustracją różnicy między idealnym podparciem a rzeczywistymi połączeniami. Poszerzona skrzynia wymaga ponownego P18E i P21G na własnej geometrii.

## P30C — ekran wrażliwości elektroakustycznej: 486 obliczeń

Przeprowadzono `6 wariantów korpusu × 3 stany objętości × 3 objętości netto z przedziałów stresowych × 3 Vas(190,212,234l) × 3 Qts(0,38/0,43/0,48)` = **486 przypadków** szczelnej charakterystyki małosygnałowej drugiego rzędu. Fs 19,5 Hz, brak DSP, strat, właściwości maty, nieszczelności, pokoju i THD. Vas i Qts są **arbitralną analizą wrażliwości**, nie zakresem rozrzutu produkcji.

Dla porównywanego stanu ~120 l otrzymano w najwęższych i najszerszych wariantach F3 około 28,9–37,2 Hz. **Różnice między samymi wymiarami korpusu przy podobnym litrażu są małe w modelu 0D**, lecz model ten z założenia nie widzi różnic w rozmieszczeniu wręg i maty ani propagacji przestrzennej. Nie jest więc argumentem, aby bez pomiaru wybrać cieńszą matę.

Wyniki P29D pozostają podstawą oceny grzania przy 20 Hz i wyboru RSS390HF-4; nie zmieniono rekomendacji głośnika na podstawie tej próby geometrii.

## Wynik przeglądu i rekomendacja konstrukcyjna

**Do dalszego projektu CAD/MES proponuje się nominalnie 1040×430×500 mm**, przy regulacji ~102/122/152 l w trzech pozycjach wkładów, tylną warstwą 40 mm i 14 mm modelowego marginesu pełnej głębokości. **1050×425×500 mm** zachować jako kontrwariant z większą rezerwą głębokości (19 mm), ale cieńszą matą 35 mm. P20D 1000×440 pozostaje kontrolą referencyjną — ma niewielki margines 4 mm. Jest to decyzja *o wariancie do dalszych obliczeń*, nie zatwierdzony projekt prototypu.

### Bramy przed zamówieniem jakiegokolwiek CNC

1. **P30D:** pełny rysunek CAD frontu, rzeczywista pozycja kosza, śrub i przewodów, maskownicy, terminala, obwiednia Xpeak, tolerancje, projekt zamków mocujących wkłady; ponowne sprawdzenie montażu ręką/narzędziem i przy pionie/poziomie.
2. **P30E:** mechanika skończenie podatnych wręg/spoin, frontu, paneli i mocowania głośnika na **nowej** geometrii; normalne naprężenia, ugięcia, siły, pierwsze postacie drgań, obciążenia grawitacyjne, testy czułości na E/Gc MDF i kleju.
3. **P30F:** przestrzenny port akustyczny P21D–P21G z 40/35/50-mm matą, rzeczywistymi przeszkodami, koszem i wzmocnieniami; rozdzielenie rezonansów ścian od rezonansów powietrza i pomiaru THD.
4. **P30G:** zweryfikowanie Rth/Cth, BL(x), Cms(x), Le(f,I), napięcia i prądu w obciążonym torze klasy D; niezależny sprzętowy mute/failsafe. Nie wolno uznać numerycznych limitów 35/80K albo 0,8Xmax za bezpieczne nastawy.
5. **P30H:** minimalny zestaw pomiarów po złożeniu jednej skrzyni: test szczelności, impedancja 0/2/11/16 wkładów bez i z matą, kontrolowane bliskie pole, odpowiedź ścian, rozgrzewka/ochłodzenie, zniekształcenia, oba ustawienia i ugięcie osłony.

## Odtwarzanie i pliki

`python3 p30a_robust_geometry.py` — wymaga NumPy, generuje `p30a_geometria_przeglad_20261031.json`.

`python3 p30b_struktura_i_akustyka.py` — wymaga tylko standardowej biblioteki Python, generuje `p30bc_paneli_ts_20261031.json`.

Obydwa skrypty to **oddzielne numeryczne ekrany**. Nie generują rysunków CNC, nie symulują pełnego MES skrzyni ani nie zastępują pomiarów sprzętu.
