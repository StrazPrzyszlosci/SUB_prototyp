# Modelowanie małosygnałowe i granice prognozy

Implementacja: [model_subwoofera.py](../skrypty/model_subwoofera.py).
Wyniki: [raport obliczeń](../raporty/002_obliczenia_wstepne.md).
Poniższe zależności są modelem skupionym, nie wynikiem pomiaru konkretnej sztuki.

## Jednostki i zestaw wejściowy

W kodzie: metry, sekundy, kilogramy, omy, wolty i ampery RMS. W pliku wejść
litry, cm², mm i mH mają nazwy z jednostką i są konwertowane jawnie.
Xmax przyjmujemy jako jednostronną amplitudę szczytową; definicję producenta
trzeba sprawdzić przed projektem ochrony. Dla sinusa Xpeak=√2·Xrms.

Zestaw pierwotny: Fs, Qes, Qms, Vas, Sd, Re i Le. Wartości pochodne:

```text
ωs = 2π Fs
Qts = 1 / (1/Qes + 1/Qms)
Cms = Vas / (ρ c² Sd²)
Mms = 1 / (ωs² Cms)
Rms = ωs Mms / Qms
BL = sqrt(ωs Mms Re / Qes)
```

ρ=1,2041 kg/m³ i c=343 m/s są przyjętymi stałymi powietrza, nie odczytami
termometru w mieszkaniu. Rms w tych wzorach oznacza mechaniczne tłumienie,
a nie sposób uśredniania napięcia. Użycie nadmiarowego pełnego katalogu bez
sprawdzenia wzajemnej spójności może wprowadzić sprzeczności. Dlatego katalogowe
Mms/Cms/BL/Qts są w osobnych kolumnach kontrolnych i nie nadpisują bazy.

## Zamknięta skrzynia w modelu idealnym

```text
α = Vas/Vb
Fc = Fs sqrt(1+α)
Qtc = Qts sqrt(1+α)
H(s) = s² / (s² + (2πFc/Qtc)s + (2πFc)²)
```

Vb to geometryczna objętość netto powietrza przy założeniu sztywnych ścian
i braku dodatkowego efektu wypełnienia. F3 rozwiązujemy z |H(j 2πf)|²=1/2.
F3=Fc zachodzi dla Qtc=1/√2. **Niższe Fc nie musi oznaczać niższego F3**:
przy niskim Qtc odpowiedź zaczyna opadać szerzej. To jeden z powodów,
aby porównywać pełne krzywe, a nie pojedynczy parametr.

Rzeczywista skrzynia ma straty, nieszczelności i podatne ścianki. Wypełnienie
może zmieniać podatność i tłumienie; stały „bonus litrów” nie jest gwarantowany.
Brakujące straty trzeba dopasować później do pomiarów zamiast zgadywać teraz.

## Model napięciowy i impedancja

```text
K = 1/Cms + ρ c² Sd²/Vb
Zm = Rms + j(ωMms − K/ω)
Ze = Re + jωLe
Zwe = Ze + BL²/Zm
I = V/Zwe
v = BL I/Zm
Xpeak = √2 |v|/ω
Pelektryczna = V² Re(1/Zwe)
Pcewki = |I|² Re
```

W powyższym zapisie `Re(...)` oznacza część rzeczywistą, a `Re` bez nawiasu
rezystancję cewki. Praktyczna implementacja rozdziela te operacje. Moc
elektryczna nie jest równa V²/Znom w całym paśmie. Strata I²Re jest składnikiem
grzania cewki, lecz bez modelu termicznego nie znamy temperatury ani kompresji.

Stałe Le odczytane przy 1 kHz jest uproszczeniem; realna indukcyjność zależy
od częstotliwości i położenia. Model jest szczególnie użyteczny do badań
niskiego pasma, ale nie opisuje rezonansów membrany w kilkuset hercach.

## Ciśnienie i normalizacja

W uproszczeniu dalekiego pola małego źródła:

```text
prms = ρ ω Sd |v| / (Ω r)
SPLrms = 20 log10(prms / 20 µPa)
Ω = 2π dla idealnej półprzestrzeni; 4π dla wolnej przestrzeni
```

Ta normalizacja nie jest pomiarem w pokoju ani pełnym modelem dyfrakcji
rzeczywistej skrzyni. Wartości RMS dla sinusa różnią się o 3,01 dB od jego
ciśnienia szczytowego. Nie dodawać 3 dB do dowolnego katalogowego „peak”,
gdy nie znamy definicji sygnału i czasu pomiaru.

## Granica modelu i czego nie nazywać max SPL

Kod dla każdej częstotliwości skaluje odpowiedź 1 Vrms do minimum:

```text
Vx = Xmax / Xpeak(1 Vrms)
Vi = Imax / Irms(1 Vrms)
Vrating_proxy = sqrt(Pe Znom)
Vlimit = min(Vx, Vi, Vwzmacniacza, Vrating_proxy)
```

`Vrating_proxy` jest wyłącznie uproszczonym ograniczeniem katalogowym.
Nie modeluje przebiegu normowego producenta, strat cewki ani długotrwałego
przegrzewania. Granica liniowa może leżeć znacznie ponad poziomem spełniającym
wymóg THD. Nie określamy jej jako potwierdzonego „maksymalnego użytecznego SPL”.

Krzywa obejmuje osobne sinusy. Muzyka wymaga wspólnego budżetu napięcia,
prądu, mocy, ruchu i crest factor. Nie można naraz uzyskać wszystkich punktów
takiej obwiedni, dodając je w sygnale wielotonowym.

## EQ i odpowiedź czasowa

Roboczy Linkwitz Transform zmienia mianownik modelu sealed na zadany cel:

```text
LT(s) = (s² + ωc/Qtc s + ωc²) / (s² + ωt/Qt s + ωt²)
```

Obecny przykład dodaje HP Butterwortha 2. rzędu i LP Linkwitz–Riley 4. rzędu.
To wzorzec analogowy, a nie gotowe współczynniki miniDSP. Implementacja
cyfrowa wymaga częstotliwości próbkowania, sprawdzenia konwencji Q, mapowania
filtrów i testu headroomu. Docelowy podział z monitorami pozostaje otwarty.

Wzrost o 6 dB wymaga około 2 × napięcia i 4 × mocy w tym samym obciążeniu.
Należy policzyć rzeczywiste nakładanie filtrów i zapas sumowania kanałów,
a nie tylko największą wartość jednej sekcji PEQ. Opóźnienie grupowe oblicza
się z −dφ/dω; samo nie wystarcza do oceny słyszalnej jakości.

## Niepewność i niezależna kontrola

Skrypt kontrolny porównuje model elektromechaniczny z analitycznym dla Le→0,
sprawdza bilans mocy, F3, limit Vb→∞ i skalowanie. To kontrola implementacji.
Nie zastępuje porównania z pomiarem ani drugim niezależnym narzędziem.

Przed zamknięciem R2 odtworzyć wybrane przypadki w drugim narzędziu lub
osobnym niezależnym arkuszu, z identyczną konwencją napięcia, przestrzeni i Xmax.
Rozbieżność wymaga wyjaśnienia, nie uśrednienia. Model nieliniowy wymaga
danych BL(x), Cms(x), Le(x), strat i termiki; nie wyprowadzimy ich z samych T/S.
