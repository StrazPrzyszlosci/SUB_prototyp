# Raport 070 — P24E: wieloczęstotliwościowa identyfikacja Re(T), BL i Le z U/I

**31.10.2026. Status:** 120 000 numerycznych prób z syntetyczną impedancją, 24 zestawy scenariusz×pasmo, generator pseudolosowy 20261031. To NIE są wyniki pomiarów rzeczywistego C02, pomiar z miniDSP ani bezpieczne nastawy zabezpieczeń.

## Cel i testowana hipoteza

P24C wykrył bardzo duży błąd wyznaczania temperatury na pojedynczej częstotliwości blisko rezonansu (40 Hz), szczególnie przy zmianie współczynnika napędowego BL. P24E sprawdza, czy zespolone dane U/I na dwóch lub większej liczbie częstotliwości pozwolą **oddzielić** wpływ przyrostu rezystancji cewki od wpływu zmiany BL i Le. Jednocześnie szukamy niewyznaczalnych wielkości mimo wielu częstotliwości.

Zakładamy hipotetyczny C02 RSS390HF-4 w 80 l według P24B: Re0=3 Ω, alpha=0,00393/K, BL0=15 Tm, Le0=0,92 mH, Fs=19,5 Hz i pozostające parametry nominalne P24B. Model zimnej i gorącej impedancji:

    Z(f,T)=Re0*(1+alpha*DeltaT)+j*omega*Le + BL^2/Zm(f)

Przy założeniu stałego Zm różnica gorąca–zimna:

    DeltaZ(f)=DeltaRe+Delta(BL^2)/Zm(f)+j*omega*DeltaLe

Dopasowujemy **trzy zmienne** metodą najmniejszych kwadratów do części rzeczywistej i urojonej DeltaZ na kilku częstotliwościach. Z pojedynczego f wyznaczamy dla porównania dawny, podatny na zmianę BL estymator DeltaT=real(DeltaZ)/(Re0*alpha).

**Istotny warunek:** wynik trójparametrowy nie rozdziela nieznanej rezystancji przewodów od rezystancji uzwojenia. Ponadto identyfikacja stałego Zm jest założeniem modelu: zmiana podatności Cms, Vb czy chłodzenia może prowadzić do błędów.

## Siatka wykonanych obliczeń

4 modele zmian:
1. stałe BL/Le/Cms i stałe przewody;
2. BL−3%, Le+10%, bez innych zmian;
3. dodatkowo Cms+5% (nieujęte w estymatorze);
4. dodatkowo dryft szeregowej rezystancji przewodów +0,1 Ω.

6 zestawów częstotliwości: [40], [80], [80,150], [20,40,80], [80,150,300], [20,40,80,150,300] Hz. Dla każdego 5000 prób: zimna i gorąca impedancja zakłócone niezależnym normalnym szumem amplitudy 0,5% i fazy 0,2°. Przyjęty rzeczywisty przyrost cewki to +80 K (wyłącznie do testu estymatora; nie jest bezpiecznym limitem). Razem **4 × 6 × 5000 = 120 000** prób.

## Rzeczywiście uzyskane wyniki

| Scenariusz | Pasmo [Hz] | Systematyczny błąd DeltaT [K] bez szumu | RMSE [K] przy założonym szumie |
|---|---|---:|---:|
| BL−3%, Le+10% | 40 | −53,620 | 54,494 |
| BL−3%, Le+10% | 80 | −0,954 | 2,472 |
| BL−3%, Le+10% | 80,150 | ≈0 | 1,513 |
| BL−3%, Le+10% | 80,150,300 | ≈0 | **1,241** |
| BL−3%, Le+10% | 20,40,80,150,300 | ≈0 | 1,427 |
| BL−3%, Le+10%, Cms+5% | 20,40,80 | −9,648 | 9,894 |
| BL−3%, Le+10%, Cms+5% | 80,150,300 | −0,015 | 1,254 |
| BL−3%, Le+10%, rezystancja przewodów +0,1 Ω | 80,150,300 | **+8,482** | 8,573 |
| Brak zmian parametru napędu | 80,150,300 | ≈0 | 1,260 |

To wynik eksperymentu z **danymi wygenerowanymi przez ten sam model, którego używa estymator** (z wyjątkiem jawnie dodanych perturbacji). Dlatego bardzo mały błąd w wariancie zgodnym z modelem **nie przewiduje** precyzji sprzętowej.

### Fundamentalna nierozróżnialność rezystancji

W każdej częstotliwości przyrost zewnętrznej rezystancji szeregowej jest obserwowany jako ten sam składnik rzeczywisty DeltaZ co przyrost Re(T). W macierzy identyfikacyjnej obie wielkości mają identyczną kolumnę — **nieskończenie wiele par DeltaRe/DeltaRprzewody daje ten sam wynik**. Dla użytego modelu:

    0,1 Ω / (3 Ω × 0,00393 / K) = 8,482 K

Dopasowanie nawet pięciu częstotliwości **nie usuwa** tego błędu. Skrypt dodatkowo potwierdza równość różnic impedancji dla wszystkich pięciu f z tolerancją 1e−12 Ω. Potrzebny jest pomiar Kelvin/kompensacja przewodów, osobna kalibracja i monitoring dryftu, a nie tylko większa liczba punktów częstotliwości.

### Ograniczenia wyboru pasma

Powyższe 80–300 Hz okazało się lepsze od 40 Hz **wyłącznie w danym modelu, przy zadanym szumie**. Powyżej pasma subwoofera nie musi istnieć dość energii muzycznej do identyfikacji; celowy pilot pomiarowy wymaga osobnej oceny poziomu, emisji akustycznej, zniekształceń i ochrony. Nie wolno zakładać, że można wykonywać pełną sekwencję pomiarową co sekundę. Nie modelowano przerw w obserwacji, zmian T pomiędzy odczytami, opóźnień ADC, zawartości harmonicznych, kwantyzacji, tolerancji piezo/mikrofonu ani wyjściowego filtru wzmacniacza klasy D. Liczba uwarunkowania zależy od przyjętych jednostek/skali parametrów i nie może być porównywana poza tym modelem.

## Ocena i dalsze badania

**Wykazano warunkowo** zdolność rozdzielenia Re, BL² i Le z kilku spójnych fazowo pomiarów, ale **nie wykazano** oddzielenia Re od dryftu rezystancji toru. Należy rozwijać kontroler z przedziałami niepewności, kontrolą dopuszczalnego pobudzenia i trybem awaryjnym przy utracie identyfikowalności, a nie stosować oszacowanej temperatury jako pewnej wartości w limiterze P24D.

Otwarte bramki: rzeczywisty pomiar Z(f), prąd i napięcie na obciążeniu (izolowany tor do pracy z mostkową klasą D), równoległa niezależna kalibracja Re i temperatury, BL/Cms/Le zależne od x,T,f, hałas i niedostępność pobudzeń, walidacja po czasie, wykonalność obliczeń i opóźnień na wybranej platformie, eksperymenty dwutonowe i nieliniowe P25. Bez tego **nie zatwierdzać progu temperaturowego ani sprzętowej ochrony**.

## Odtwarzanie

Wymagania: Python 3 i NumPy. Kod: skrypty/p24e_wieloczestotliwosciowa_ident.py. Uruchomienie:

    python3 skrypty/p24e_wieloczestotliwosciowa_ident.py

Wygenerowany pełny wynik: wyniki/p24e_wieloczestotliwosciowa_ident_20261031.json; w repo utrwalono także wyniki/p24e_podsumowanie_20261031.json. Skrypt i raport zawierają wszystkie przyjęte założenia; wyniki są numeryczne, nie empiryczne.
