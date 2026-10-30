# Raport 050 — P21C0: płytka komora i przesunięte źródło

Data: 2026-10-29. **Nowe obliczenia modelowe, bez pomiaru urządzenia.**
Pierwszy krok P21C pod limit głębokości U-026. Nie zamyka P21C ani wyboru głośnika.

## Pytanie i wynik dla projektu

Czy wspólna objętość i częstotliwość pierwszego modu wystarczają do
zastąpienia płytkiej głównej komory jednym ciśnieniem? **Nie w całej
zbadanej rodzinie.** Przy zadanym ruchu skończonego tłoka ciśnienie
uśrednione po jego powierzchni zależy od proporcji skrzyni i położenia
źródła. Średnia po całej objętości nadal dokładnie odpowiada podatności 0D.
Nie są to te same wielkości.

**Rekomendacja:** do dalszej syntezy zachować przestrzenny port ciśnienie–ruch
na powierzchni źródła. Nie wybierać obudowy wyłącznie z litrów i warunku
„pierwszy mod powyżej 80 Hz”. Porównywać centralny głośnik z preferowanym
środkiem jednej z połów frontu przy tej samej geometrii.

## Dziedzina i jawne założenia

- 27 geometrii: puste wnętrze 60/100/150 l × głębokość zewnętrzna
  350/425/500 mm × wewnętrzne W/H = 1/1,5/2.
- Ścianki 22 mm są założeniem wyłącznie geometrycznym. W równaniach
  akustycznych wszystkie ściany są idealnie sztywne.
- Źródło kontrolne: równomiernie poruszający się kwadrat 200 lub 250 mm,
  na froncie y=0, z=H/2, x=W/2 albo W/4. To nie dane membrany ani
  otworu montażowego konkretnego głośnika.
- 108 konfiguracji źródła, z których 8 nie mieści całego kwadratu na
  froncie; 100 dopuszczonych geometrycznie × 6 częstotliwości = 600 punktów.
- Osobne sinusy 20/25/31,5/40/63/80 Hz. Liniowy iloraz odpowiedzi przy
  zadanym ruchu, bez założenia bezpiecznej amplitudy i czasu pracy.
- Gaz bezstratny, c=343 m/s. Brak włókniny, regulatora Vb, usztywnień,
  kosza, podatności ścian, podparcia i pokoju.

Objętość jest **pustym wnętrzem brutto**, nie docelowym Vb netto. W/H
nie są ograniczeniami użytkownika. Sprawdzenie kwadratu nie dowodzi
zmieszczenia kosza, śrub, maskownicy ani dostępu serwisowego.

## Równania i sposób obliczeń

Dla prostokątnej komory użyto ortogonalnych modów Neumanna:

\[
\phi_{nml}=\cos(n\pi x/W)\cos(m\pi y/D)\cos(l\pi z/H),\quad
k_{nml}^2=(n\pi/W)^2+(m\pi/D)^2+(l\pi/H)^2.
\]

Uśrednione sprzężenie skończonego tłoka kwadratowego jest iloczynem:

\[
b_{nl}=\cos(n\pi x_c/W)\operatorname{sinc}(na/2W)
\cos(l\pi z_c/H)\operatorname{sinc}(la/2H),
\]

gdzie sinc(t)=sin(πt)/(πt). Stosunek nacisku zwrotnego na tłok do
nacisku jednolitego gazu przy tym samym ruchu wynosi:

\[
R=1+\sum_{(n,m,l)\ne(0,0,0)}
\epsilon_n\epsilon_m\epsilon_l b_{nl}^2
\frac{k^2}{k^2-k_{nml}^2},\qquad
\epsilon_0=1,\;\epsilon_{j>0}=2.
\]

Wszystkie rozpatrywane punkty leżą poniżej pierwszego modu sztywnej
komory. Nie trafiamy w bezstratne bieguny. Wyższe mody nadal wnoszą
bezwładność i zmieniają lokalny port, nawet daleko poniżej własnego rezonansu.

**Mechanizm wpływu przesunięcia:** dla x_c=W/2 współczynnik cos(nπ/2)
zeruje sprzężenie z nieparzystymi modami szerokości. Dla x_c=W/4
pierwszy z tych modów ma już niezerowe sprzężenie. To wynika z symetrii
źródła w tym modelu; nie dowodzi automatycznie przewagi centralnego
montażu w pełnej konstrukcji z wypełnieniem i usztywnieniami.

Pierwotny potrójny szereg 10/20/40 wykazał zbyt wolną zbieżność w
kierunku głębokości. Zapis pilota zachowano w archiwum. Zamiast uznawać
ostatnią siatkę za wynik końcowy, zsumowano **cały kierunek głębokości**:

\[
\sum_{m=0}^{\infty}\frac{\epsilon_m}{q^2-(m\pi/D)^2}
=\frac{D}{q}\cot(qD).
\]

Dla q=iα stosuje się -D coth(αD)/α. Pozostałe dwa kierunki policzono
przy rzędach 40/80/160. Nie wprowadzono tłumienia w celu ukrycia błędu.

## Wyniki

Przykłady przy **D zewnętrznym 500 mm**, wewnętrznym W/H=1,5,
tłoku 200 mm i 80 Hz. R=1 oznacza model jednolitego gazu.

| Puste wnętrze | Wymiary zewnętrzne W × D × H | R, środek frontu | R, środek połowy frontu |
|---|---|---:|---:|
| 60 l | 488,3 × 500 × 340,2 mm | 0,74103 | 0,68116 |
| 100 l | 617,5 × 500 × 426,4 mm | 0,60268 | 0,52568 |
| 150 l | 746,4 × 500 × 512,3 mm | 0,41094 | 0,30939 |

To **nie ranking głośników i nie zmiana zewnętrznego SPL**. Mniejszy
nacisk zwrotny przy zadanym ruchu nie oznacza automatycznie lepszego basu,
mniejszych zniekształceń lub bezpieczniejszej pracy.

Największa korekta w badanej rodzinie: 150 l, głębokość 350 mm,
W/H=2, tłok 200 mm w x=W/4. Wymiary zewnętrzne około
1034,1 × 350 × 539,1 mm; pierwszy mod sztywnego gazu 173,21 Hz.
Przy 80 Hz R=0,2248316, czyli nacisk zwrotny jest około 77,52% mniejszy
od wartości 0D. Jest to świadek niewystarczalności kryterium pierwszego
modu, **nie propozycja finalnej obudowy**.

![Porównanie pustych płytkich komór](../wyniki/95_P21C0_plytka_komora.png)

## Niepewność numeryczna i kontrole

Największa zmiana R przy zwiększeniu rzędu 80→160 wynosi 0,00018617.
Wyprowadzono także analityczną granicę pominiętych modów poprzecznych:
poniżej pierwszego modu wszystkie pominięte składniki mają znak ujemny.
Użyto Parsevala (suma kwadratów sprzężeń = długość/rozmiar źródła),
ograniczenia sinc² oraz sumy n^-2 ≤ 1/N. Suma ograniczeń dwóch pasów
pominiętych indeksów zawyża narożnik, co jest bezpieczne dla tej granicy.

Największa obliczona granica ogona wynosi **0,00049427 jednostki R**.
Dla wskazanego skrajnego przypadku daje to przedział ucięcia około
**[0,2243373; 0,2248316]**, przed osobnym uwzględnieniem zaokrągleń.
To analityczna granica ucięcia oceniona float, nie certyfikat arytmetyki
przedziałowej i nie niepewność rzeczywistej skrzyni.

Kontrole obejmują:

- pełny tłok na całym froncie: niezależna funkcja kD cot(kD), sześć testów;
- całkowanie powierzchni źródła kwadraturą zamiast wzoru sinc, pięć testów;
- potrójny szereg zbieżny do rozwiązania z analitycznie zsumowaną głębokością;
- pięć świadków analitycznej granicy ogona;
- obrót pustej geometrii wraz ze źródłem: równość odpowiedzi wszystkich
  dopuszczonych konfiguracji; nie dotyczy ciężaru, podpór lub pokoju;
- odrębny model objętości skończonych Helmholtza, bez modów cosinusowych
  w rozwiązywanym układzie: wyniki w `p21c0_niezalezna_FV.json`.

Kontrola FV wymaga rekonstrukcji ciśnienia na powierzchni tłoka z warunku
Neumanna. Sam odczyt ze środka pierwszej komórki nie jest tą samą
wielkością co średni nacisk na tłok. Pierwsze próby na siatkach 12/24/36
nie spełniły roboczego progu 0,002 jednostki R; zachowano próg i
rozwinięto kontrolę na drobniejsze siatki.

Końcowe siatki FV: 12×8×8, 24×16×16, 48×32×32 i 96×64×64.
Przy 80 Hz w komorze 600×400×400 mm różnice dla źródła centralnego
wyniosły kolejno 0,047793 / 0,015364 / 0,004724 / **0,001413**.
Dla źródła w środku połowy frontu: 0,047124 / 0,015195 / 0,004681 /
**0,001403**. Oba przypadki spełniły pierwotny próg 0,002 na ostatniej
siatce. Nie jest to niezależna walidacja każdego z 600 punktów: FV kontroluje
jedną geometrię i jedną częstotliwość.

## Co ten wynik zmienia

1. P21C musi używać skończonej powierzchni i położenia źródła, nie tylko Vb.
2. Przed syntezą z napędem uzgodnić Mmd/Mms i masę promieniowania:
   **nie dodawać bez sprawdzenia całego nowego portu do katalogowego Mms**,
   które może już obejmować obciążenie powietrzem. Ten raport nie wykonuje
   jeszcze takiej integracji.
3. Następnie dodać rzeczywiste rozmieszczenie regulacji i włókniny,
   a potem podatność ścian. Porównać nie tylko średnią objętościową,
   ale pracę portu membrany i lokalne obciążenia modułów.
4. Potwierdzenie geometrii w obu orientacjach wymaga nadal mechaniki,
   mocowania, dostępu i miejsca w pokoju. Inwariancja pustego gazu
   przy obrocie nie zamyka tego wymagania.

## Odtworzenie i pochodzenie

Obliczenia wyprowadzono z równania Helmholtza i warunku pracy ciśnienie–ruch,
zgodnie z wewnętrzną bazą P21B. Nie pozyskano nowych danych producentów.
Wszystkie nowe liczby są obliczeniami lub jawnymi założeniami.

```bash
OPENBLAS_NUM_THREADS=1 python3 skrypty/pilot_P21C_geometria.py
OPENBLAS_NUM_THREADS=1 python3 skrypty/sprawdz_P21C_FV.py
```

Wejścia: `dane/konfiguracje/p21c0_geometria.json`. Tabele:
`wyniki/p21c0_geometria_i_port.csv`, `wyniki/p21c0_zbieznosc.csv`.
Podsumowanie i hashe: `wyniki/p21c0_podsumowanie.json`.
