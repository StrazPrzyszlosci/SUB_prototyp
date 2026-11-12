# S15. Ugięcie membrany a ciśnienie w stałej komorze 102 l

Data: 12.11.2026. Dotyczy tylko osobnego frontu badawczego i głośnika RSS390HF-4. Status: model analityczny, nie rzeczywisty pomiar, bez zatwierdzenia CNC.

## Dane i źródła pierwotne

- Dayton Audio: Sd = 829,6 cm², Xmax = 14 mm jednostronne, Vd = 1161,4 cm³. Karta producenta: https://www.daytonaudio.com/images/resources/295-468-dayton-audio-rss390hf-4-specifications-46176.pdf
- NIST: standardowe ciśnienie odniesienia 101325 Pa: https://www.nist.gov/pml/special-publication-330/sp-330-appendix-1
- NASA Glenn: współczynnik adiabatyczny powietrza 1,4 i relacja p2/p1=(V1/V2)^gamma w przemianie izentropowej: https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/isentrophic-compression/
- Wariant konstrukcyjny: S06 (101,9861 l nominalnie, 102 l celu); modele porównawcze ścian: S02/S03 przy 1 kPa.

Zmianę objętości obliczono z Sd × x. Dla x=14 mm: 1161,44 cm³ = 1,16144 l, czyli około 1,139% całej komory 102 l. Jest to wychylenie szczytowe jednostronne, NIE RMS ani automatycznie dopuszczalny sygnał DSP. Różnica 0,04 cm³ względem katalogu wynika z zaokrąglenia.

## Dwa idealne warunki termiczne

Zakładamy gaz idealny w doskonale szczelnej i sztywnej objętości powietrza, jednolity stan ciśnienia i brak strat. Przypadki:
- gamma = 1,0, izotermiczny;
- gamma = 1,4, adiabatyczny (bez wymiany ciepła w cyklu).

Wzór na NADCIŚNIENIE przy ruchu membrany do środka: dp+ = p0 [(V/(V - Sd×x))^gamma -1]. Przy ruchu na zewnątrz: dp- = p0 [(V/(V + Sd×x))^gamma -1]. To przypadki idealne. W rzeczywistym subwooferze o efektywnej podatności wypełnienia, odkształceniu ścian, przeciekach i rozkładzie temperatur żaden z nich nie jest uniwersalnym ograniczeniem gwarantowanym.

| Netto | Nadciśnienie, izotermicznie | Nadciśnienie, adiabatycznie | Podciśnienie adiabatyczne |
|---|---:|---:|---:|
| 99 l | 1,203 kPa | 1,688 kPa | -1,641 kPa |
| 102 l | 1,167 kPa | 1,638 kPa | -1,594 kPa |
| 105 l | 1,133 kPa | 1,590 kPa | -1,549 kPa |

Tabela dotyczy x=14 mm, nie rzeczywistego poziomu odtwarzania. Dodatkowo skrypt liczy wychylenia 5, 10 i 14 mm oraz łączne pola i siły.

## Siły na elementach i odniesienie do S03

Dla nominalnych 102 l przy idealnej adiabacie:
- nadciśnienie około 1638 Pa;
- iloczyn nadciśnienia i Sd głośnika daje około 136 N (zastępcza siła od sprężyny powietrznej, NIE całkowita siła wzbudzenia kosza);
- iloczyn ciśnienia i geometrycznego światła tylnej płyty 772,8 × 429,3 mm wynosi około 543 N (rozłożone obciążenie, NIE wypadkowa siła przekazana do stóp).
- S03 dla oddzielnej płyty tylnej miał 0,043 mm/kPa z utwierdzeniem i 0,162 mm/kPa z podparciem przegubowym. Proste skalowanie STATYCZNE daje odpowiednio około 0,070 i 0,265 mm przy 1,638 kPa.

Takie przeliczenie nie wyznacza amplitudy drgań dynamicznych. Przy zbliżeniu do częstotliwości własnej, zmianie sztywności spoin, reakcji mechanicznej napędu, zróżnicowaniu ciśnień i przenoszeniu na meble wyniki mogą być znacząco inne. Nie wynika z niego żaden poziom THD, SPL, wytrzymałość połączeń ani bezpieczeństwo modułu. Nie wolno uznawać nadciśnienia w komorze za ciśnienie akustyczne na zewnątrz urządzenia.

## Co zmienia się w ścieżce M5

1. Przy każdym kolejnym modelu całego korpusu sprawdzać zakres co najmniej 1,0-1,7 kPa jako PORÓWNANIE hipotetycznych stanów szczytowych; przypadek pomiarowy wyznaczać według faktycznie zmierzonego X(t), a nie katalogowego Xmax.
2. Osobno ocenić nacisk na spoiny, wkręty, pierścień i wręgę oraz wymuszenie od kosza. Samo ciśnienie równomierne nie opisuje pełnej reakcji napędu.
3. Zmierzyć rzeczywistą impedancję przy rosnącym, bezpiecznym poziomie i ocenić przecieki. Ciśnienie wewnątrz można mierzyć opcjonalnie skalibrowanym czujnikiem w szczelnym przepuście odpowiednim do niskich częstotliwości. Instalacja czujnika nie może niekontrolowanie zwiększać nieszczelności.
4. Zmiana objętości o kilka litrów nie rozstrzyga sama poziomu obciążenia, jeżeli nie są znane parametry egzemplarza, wypełnienie i rzeczywiste przemieszczenie membrany.

Wyniki są odtwarzalne przez python wariant_staly/s15_cisnienie.py oraz python wariant_staly/sprawdz_s15_s16.py. CNC HOLD. Główny README bez zmian.
