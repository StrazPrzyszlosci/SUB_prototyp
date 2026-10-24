# Raport 015 — niepewność globalna i odporność porównania

Stan: 2026-10-24. P06 wykonany dla zdefiniowanych liniowych rodzin modeli.
To raport cząstkowy programu, nie końcowy PDF ani wybór urządzenia.

## Wynik istotny dla wyboru

**Nominalne prowadzenie RSS390HF-4 przy 20 Hz nie daje uniwersalnej przewagi
w zbadanych rodzinach niepewności.** Dla 100 l i napędu 40 Vrms/12 Arms
kolejność C02/RSS390HF-4 oraz C11/RSS390HE-22 zmienia się przy wspólnym
ułamku katalogowego ruchu około **0.8639 X**.
Przy 1,0 X wynik wynosi odpowiednio 101,89 i 100,62 dB, przy 0,7 X —
98,79 i 100,62 dB, w jawnej normalizacji modelu 2π/1 m/RMS.
Przy 0,7 X przewaga C11 wynosi około 1,83 dB. To nie dowód niższego THD
ani lepszej jakości fizycznego RSS390HE. Katalogowe definicje X są różne.

Nawet przy ustalonym 1,0 X znaleziono dopuszczalny kontrprzykład dla
niezależnych zaburzeń parametrów przy **tym samym napędzie** obu modeli.
Mała różnica około 0,08 dB formalnie obala uniwersalną dominację w tej
dziedzinie, lecz nie jest argumentem odsłuchowym ani zakupowym.
Potrzebne są dane liniowości i integracja z termiką, DSP i konstrukcją.

## Co jest dane, a co założone

Nominały: 24 katalogowe zestawy z audytem źródeł w raporcie 010.
Zmienne pierwotne: Mms, Cms, BL, Rms, Re, Le, Sd, Vb oraz budżety V/I.
Fs, Qes, Qms, Vas i Qts wynikają z tych zmiennych; nie losowano niezależnie
wszystkich T/S. Obliczenia obejmują 60/100/150 l i dwa hipotetyczne napędy:
40 Vrms/12 Arms oraz 60 Vrms/20 Arms, przy 20 i 40 Hz.
Te litraże są scenariuszami porównania, a nie limitem gabarytu ani wyborem.

Zakresy poniżej są **umownymi zakresami stresowymi**. Nie są tolerancją
produkcji, przedziałem ufności ani dowodem objęcia wszystkich rzeczywistych
egzemplarzy. Są jawne, aby dało się sprawdzić zmianę wniosków przy ich zmianie.

| Czynnik | Zakres / nominał lub jednostka |
|---|---|
| Mms | 0.9–1.1 |
| Cms | 0.85–1.15 |
| BL | 0.9–1.1 |
| Rms | 0.7–1.3 |
| Re | 0.95–1.05 |
| Le | 0.8–1.2 |
| Sd | 0.98–1.02 |
| Vb | 0.97–1.03 |
| Vmax | 0.9–1 |
| Imax | 0.8–1 |
| fleak przy referencyjnych 100 l [Hz] | 0–3 |
| dodatkowy opór mechaniczny / Rms | 0–1 |
| ułamek katalogowej amplitudy X | 0.5–1 |

Rodzina **D** obejmuje parametry pierwotne i budżet napędu przy ustalonych
X = katalogowe X, zerowym przecieku i zerowym dodatkowym oporze.
Rodzina **L** obejmuje całą tabelę. Zakres 0,5–1,0 X nie jest gwarancją niskiego
THD: rzeczywisty próg może leżeć poza nim. Dodatkowy opór jest dodatnim
elementem modelowym, nie zmierzonym efektem konkretnej włókniny.

Przy zmianie Vb zachowano tę samą rezystancję przecieku Ra: jego częstotliwość
relaksacji zmienia się odwrotnie do Vb. Ciśnienie uwzględnia sumę przepływów
membrany i przecieku przy wspólnej fazie propagacji. Dla przecieku jest to
równoważny wskaźnik w umownej normalizacji 2π/1 m, a nie SPL dowolnego
rozmieszczenia otworów. Geometria i reakcja promieniowania pozostają P11.
Moc katalogowa nie jest wspólnym limitem termicznym i nie została nim zastąpiona.

## Metody i granice interpretacji

[JCGM 101:2008](https://www.bipm.org/documents/20126/2071204/JCGM_101_2008_E.pdf)
wymaga przypisania rozkładów wejściowych na podstawie wiedzy oraz wspólnego
rozkładu dla zależnych wielkości. Obecne dane nie uzasadniają rozkładu populacji
produktów. Dlatego MC/QMC i Sobol opisują wyłącznie zadeklarowaną jednostajną
**miarę obliczeniową** zakresów. Nie podajemy prawdopodobieństwa, że dany
głośnik będzie najlepszy, ani przedziału pokrycia rzeczywistego produktu.

Indeksy pierwszego i całkowitego rzędu wyznaczono metodą Saltelliego przez
[SciPy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.sobol_indices.html),
dla niezależnych czynników tej miary. Osobno użyto kopul gaussowskich Mms/Cms
z parametrem 0/+0,8/−0,8 przy zachowaniu tych samych jednostajnych marginesów.
To scenariusze korelacji, nie jej pomiar. Dla tych zależnych profili nie
interpretujemy klasycznych indeksów jako udziałów niezależnych parametrów.

Obwiednie obliczono arytmetyką przedziałową w mpmath przy 40 cyfrach dziesiętnych,
z podziałem każdej dziedziny na 24 rozłączne wnętrzami prostopadłościany.
Pokrywają zadane zakresy, a nie jedynie punkty MC. Obejmują rzeczywiste działania
na zamrożonych binarnych stałych modelu nominalnego; nie certyfikują ich zgodności
z fizycznymi głośnikami. Ciśnienie ograniczano przed przeliczeniem na dB.
Porównania dominacji wykonano na końcach przedziałów ciśnienia, nie na
zaokrąglonych liczbach w tabeli. Logarytmy dB są prezentacją IEEE.

[Dokumentacja mpmath](https://mpmath.org/doc/current/contexts.html#arbitrary-precision-interval-arithmetic-iv)
opisuje śledzenie błędów przedziałami i oznacza obsługę IV jako eksperymentalną.
Użyto wyłącznie podstawowych działań, kwadratu i dodatniego pierwiastka;
sprawdzono podział dziedziny, redukcję i pokrycie próbek oraz niezależny model.
To warunkowy wynik analizy przedziałowej, nie formalna certyfikacja biblioteki.

## Wyniki obwiedni całych zadanych dziedzin

Poniższe liczby dotyczą 100 l, budżetu 40 Vrms/12 Arms i 20 Hz.
Przedziały mogą być szersze od zbioru osiągalnych wyników. Brak separacji
obwiedni sam w sobie nie obala dominacji; do tego potrzebny jest kontrprzykład.

| Model | Rodzina D [dB] | Rodzina L [dB] |
|---|---:|---:|
| C02 Dayton RSS390HF-4 | 100.87–102.06 | 95.59–102.06 |
| C06 STX W.32.800.8.FCX | 96.51–98.10 | 91.63–98.10 |
| C11 Dayton RSS390HE-22 seria | 97.74–102.38 | 96.74–102.50 |
| C19 Dayton RSS390HO-4 | 99.86–100.72 | 94.25–100.72 |
| C20 Dayton UMII12-22 seria | 96.48–101.55 | 94.18–101.65 |
| C21 Dayton UMII15-22 seria | 96.46–102.45 | 95.11–102.60 |
| C24 Eminence LAB15 6ohm | 98.46–100.51 | 94.04–100.51 |

Łącznie: **576 obwiedni** i **6624 kierunkowych porównań**
w 12 wariantach rodziny/litrażu/napędu. Separacja przedziałów wskazała
**1069 relacji dominacji** jednocześnie w dwóch
kryteriach 20/40 Hz, warunkowo w tym modelu i dziedzinie. To nie są relacje
dominacji całego briefu: nie obejmują rzeczywistego THD, masy, kleju ani termiki.
Nie powstał na tej podstawie finalny zwycięzca.

## Wspólne zaburzenia a niezależne egzemplarze

W rodzinie D przy 100 l/40 Vrms C02 wygrał wszystkie 8192 wspólne scenariusze
20 Hz dla każdego z trzech profili korelacji. Taki test przypisuje obu modelom
te same względne zmiany parametrów. Nie sprawdza wszystkich niezależnych par
możliwych parametrów i nie dowodzi 100% szans przewagi.

Optymalizacja adwersarialna znalazła dopuszczalne pary przy wspólnym napędzie
40 Vrms/12 Arms. Zapisano pełne współrzędne i odtworzono je osobnym układem
trzech równań elektryka/ruch/komora. Największa różnica od implementacji
kampanii wynosi **1.42e-14 dB**.
Optymalizacja nie musi znaleźć globalnego ekstremum, aby taki dopuszczalny
świadek obalał twierdzenie o uniwersalnej dominacji.

| Rodzina | Para porównania | SPL A [dB] | SPL B [dB] | A−B [dB] |
|---|---|---:|---:|---:|
| D | C02 kontra C11 | 101.712 | 101.794 | -0.082 |
| D | C11 kontra C02 | 99.053 | 102.059 | -3.007 |
| L | C02 kontra C11 | 95.588 | 101.794 | -6.205 |
| L | C11 kontra C02 | 98.156 | 102.059 | -3.903 |

W rodzinie L bez kopuli C11 miał największy wynik w 4580/8192 wspólnych
scenariuszy, C02 w 3601, C21 w 11. To **liczniki punktów umownego projektu**,
nie częstość przewagi w produkcji. Dla decyzji ważniejsza jest wykazana
zależność kolejności od nieznanego kryterium ruchu niż pozorna precyzja tych udziałów.

## Co wskazuje globalna wrażliwość

Przy 20 Hz i nominalnych parametrach C02 ogranicza ruch, a C11 napięcie.
W miarze D całkowity indeks Sd dla C02 jest około 1: sam ruch nie zależy
wprost od BL/Cms, dopóki napęd wystarcza. W miarze L udział czynnika X dla
C02 wynosi około 0,996. Jest to konsekwencja zadanego szerokiego zakresu X,
a nie pomiar niepewności tego konkretnego produktu.

Dla C11 w D dominują Cms i budżet Vmax, z indeksami całkowitymi około
0,439 i 0,368. W L udział mają też dodatkowy opór i Rms. Oznacza to, że
w tej rodzinie zwiększanie samego katalogowego X nie pomaga tak jak zmiana
napędu, podatności lub strat. Te wnioski są zależne od pasma i zakresów.

Zapisano **4992 wartości indeksów** i kontrolę dwóch niezależnych
scrambli dla N=4096/16384. Maksymalna różnica po zwiększeniu N wynosi około
0,0327; między scramblami przy dużym N — około 0,0099. Próg przeglądu
numerycznego 0,04 przeszedł; to umowny próg obliczeń, nie dokładność produktu.
MC i QMC dla tej samej miary różnią się średnią odpowiedzi o maksymalnie
**0.0096 dB**. Zgodność całkowania nie potwierdza rozkładu wejść.

## Korelacje opublikowanych zestawów Scan32

Dwa wspólne zestawy TSL z obejrzanego oryginału Voice Coil 2013 dają przy
50 l klasyczne projekcje F3 **37,38–38,81 Hz**. Sztuczne mieszanie minimalnych
i maksymalnych składowych tych samych dwóch zestawów daje **34,93–41,53 Hz**.
To pokazuje skutek zniszczenia informacji o współwystępowaniu parametrów.
Mieszane narożniki nie są dodatkowymi zmierzonymi egzemplarzami.

Użyto wspólnego uproszczenia Le=0 dla tych projekcji; nie imputowano
nieopublikowanych wartości Le. Nie jest to pełny model LTD/LEAP5 ani rozkład
tolerancji wszystkich Scan32. Źródło i ograniczenia są w raporcie 012.

## Weryfikacja i wpływ na następny eksperyment

Porównanie z odrębnym N7: **144 przypadki**, największa
różnica względna lub dB **2.93e-14**.
Bilans mocy ma maksymalny względny błąd **6.84e-16**.
Sprawdzono limity V/I/X, dodatniość, Le=0, monotoniczność progu X oraz
49 152 punkty wewnątrz globalnych obwiedni. Wzorzec addytywny Sobola z
analitycznymi indeksami daje maksymalny błąd około 3.27e-06.
Punkty są kontrolą implementacji; pokrycie dziedziny wynika z działań
przedziałowych, a nie z samej ich liczby.

Pokój pozostaje około **4,6 × 3,7 × 2,5 m**, front 3,7 m, odsłuch 2,5–3 m.
U-017: użytkownik nie ma obecnie dokładnych pozycji monitorów i głowy.
Nie przyjęto ani stałego room gain, ani swobodnego ustawienia przód/tył.
Litraże trzeba powiązać z dwoma rzeczywistymi gabarytami; raport 013 pokazuje,
że nawet poprawna objętość netto nie wyznacza wykonalnej pozycji frontu.

Wniosek konstrukcyjny: zachować regulację Vb i możliwość identyfikacji strat,
nie wybierać zwycięzcy z jednej nominalnej kolumny. Priorytetem danych są
porównywalna liniowość ruchu, podatność i straty oraz wymagania napędu.
Najbliższy krok: **P09/P10 — pasywny model relaksacji cieplnej gazu i wypełnienia**,
z oddzieleniem nieszczelności, izotermiczności i dodatkowego oporu. P06 trzeba
potem rozszerzyć na nowe modele, termikę i konstrukcję w integracji P29.

![Obwiednie i zmiana kolejności](../wyniki/11_niepewnosc_i_kolejnosc.png)

Wejścia: [zakresy](../dane/konfiguracje/p06_niepewnosc.json).
Kod: [model](../skrypty/model_niepewnosci.py),
[przedziały](../skrypty/przedzialy_niepewnosci.py),
[kampania](../skrypty/analiza_niepewnosci.py),
[poszukiwanie świadków](../skrypty/analiza_adwersarialna.py),
[niezależna kontrola świadków](../skrypty/sprawdz_swiadkow_p06.py).
Wyniki: [obwiednie](../wyniki/p06_obwiednie_przedzialowe.csv),
[Sobol](../wyniki/p06_indeksy_sobola.csv),
[zbieżność](../wyniki/p06_sobol_zbieznosc.csv),
[korelacje](../wyniki/p06_korelacje_miary.csv),
[liczniki scenariuszy](../wyniki/p06_ranking_scenariuszy.csv),
[świadkowie](../wyniki/p06_swiadkowie_niezaleznych_zaburzen.json),
[podsumowanie](../wyniki/p06_podsumowanie.json).
