# 03. Pokój i integracja systemu

Stan: 2026-10-23. Podstawa: brief v0.6 i `DECYZJE_I_PYTANIA.md`; poniższe obliczenia są własne.
Obecny zakres obejmuje research i dokumentację do budowy, bez wykonywania budowy i pomiarów.
Procedury uruchomienia i strojenia opisują przyszły etap po wykonaniu prototypu; nie wybieramy teraz toru pomiarowego.

## 1. Ustalenia nadrzędne

| ID | Decyzja z 2026-10-23 | Znaczenie dla tego rozdziału |
| --- | --- | --- |
| U-001 | Użytkownik ma multimetr, oscyloskop i lutownicę | Nie zakładamy posiadania mikrofonu, interfejsu ani odpowiednich sond. |
| U-002 | Dobór i zakupy toru po zakończeniu budowy | Dzisiaj przygotowujemy metodę; aparatura nie jest warunkiem researchu. |
| U-003 | Pomiary wyłącznie w pokoju odsłuchowym | Wyniki akustyczne będą in-room, z ograniczeniami identyfikacji urządzenia. |
| U-004 | Teraz badania do budowy prototypu | Efektem jest pakiet projektowy i jawne niewiadome do przyszłych prób. |
| U-005 | Uwzględniamy opinie użytkowników i osób znających przetworniki | Doświadczenia służą hipotezom; nie zastępują pomiarów w tym pokoju. |

## 2. Geometria i granice wiedzy

Brief podaje orientacyjnie 4,6 × 3,7 × 2,5 m, betonowe ściany i krótszą ścianę przednią.
Część sufitu ma panele perforowane z wełną; pułapki narożne są planowane, a tył zajmują regały.
Stan istniejący i planowane zmiany trzeba rozdzielić w opisie konfiguracji; nie przypisywać ustrojom nieznanych parametrów.
Wymiary pozostają wejściem roboczym, a nie inwentaryzacją wykonawczą; sprawdzenie wymiarów może zmienić model.
Aktualizacja 2026-10-24: przyjmujemy oś x wzdłuż szerokości 3,7 m,
y wzdłuż głębokości 4,6 m, z pionowo na wysokość 2,5 m, zgodnie z
[konfiguracją pokoju](../dane/konfiguracje/pokoj_odsluchowy.json).
Wcześniejsza wersja rozdziału miała zamienione nazwy x/y; wartości wymiarów
nie zmieniły się. Starszy CSV modów używa kolejności długość/szerokość/wysokość.
Początek współrzędnych: narożnik przy ścianie przedniej i podłodze; na szkicu określić dodatnie kierunki osi.
Dokładne punkty źródeł, głowy, drzwi, regałów i mebli trzeba dopiero wpisać do tego układu.
Sam opis materiałów i wymiarów nie określa strat, szczelności pomieszczenia ani sprzężenia ze źródłem.
Nie znamy amplitud modów, RT ani room gain tego pokoju; nie przyjmujemy
stałego podbicia basu. Aktualizacja: [raport 013](../raporty/013_pokoj_i_realne_gabaryty.md)
bada jawne scenariusze zespolonego pola ze stratami; nie identyfikuje rzeczywistych parametrów.
Adaptacja nie jest dowodem rozwiązania problemów niskotonowych; jej rzeczywisty wpływ pozostaje do późniejszego sprawdzenia.

## 3. Własne obliczenie: idealny model częstotliwości modów

**Obliczenie modelowe, nie pomiar:** prostopadłościan o sztywnych granicach i jednorodnym ośrodku, `c = 343 m/s`.
Wartość c jest założeniem obliczeniowym; nie jest wynikiem pomiaru temperatury ani prędkości dźwięku w pokoju.
Dla nieujemnych liczb całkowitych n, m, k, nie wszystkich równych zeru, przyjmujemy:
`f(n,m,k) = (c/2) × sqrt[(n/Lx)² + (m/Ly)² + (k/Lz)²]`.
Dla pierwszego modu osiowego na danej osi pozostałe indeksy są zerowe, więc `f = c/(2L)`.

| Oś / indeks | Podstawienie w SI | Wynik własnego obliczenia | Status |
| --- | --- | --- | --- |
| y / (0,1,0) | `343/(2 × 4,6)` | około 37,28 Hz | Model idealny |
| x / (1,0,0) | `343/(2 × 3,7)` | około 46,35 Hz | Model idealny |
| z / (0,0,1) | `343/(2 × 2,5)` | około 68,60 Hz | Model idealny |

Wartości policzono w Pythonie jako `343.0 / (2.0 * L)` dla L równego kolejno 4.6, 3.7 i 2.5.
Dwie cyfry po przecinku pokazują wynik rachunku; dokładność geometrii i zgodność rzeczywistego pokoju nie są tak potwierdzone.
Tabela wskazuje obszary częstotliwości warte uwagi, bez prognozy wielkości szczytów, dołków i szerokości rezonansów.
To, co zostanie pobudzone i zarejestrowane, zależy także od miejsca źródła i odbioru oraz rzeczywistych warunków brzegowych.
Zbieżność częstotliwości zmierzonego problemu z tabelą będzie przesłanką diagnostyczną, nie jednoznaczną identyfikacją przyczyny.
Przy zmianie długości lub c przeliczyć model; dla małych zmian `δf/f ≈ δc/c − δL/L` w modelu osiowym.
Bez tolerancji wejść nie dopisywać przedziału ufności ani amplitudy; nie projektować gotowego filtra EQ z samej tabeli.

## 4. Jeden sweet spot i realne lokalizacje źródeł

Priorytetem jest S0: jedna pozycja głowy, orientacyjnie 2,5–3 m od systemu; dokładne odległości są do potwierdzenia.
Zapisać wysokość uszu i położenie S0 względem monitorów; nie wybierać miejsca wyłącznie według popularnego procentu długości pokoju.
Subwoofery mają stać przede wszystkim w pobliżu monitorów; układ przód–tył nie jest swobodnie dostępny.
Przygotować szkic kilku wykonalnych położeń wraz z gabarytem skrzyni, miejscem na przewody, dostępem serwisowym i osłoną.
Rozpatrzyć niewielkie przesunięcia w dostępnej strefie; nie wymuszać identycznej odległości subwooferów od ścian.
Pozycję monitorów oceniać również przez wymagania stereo; poprawa samego basu nie rozstrzyga całego ustawienia.
Nie wskazujemy dziś zwycięskiej lokalizacji ani zapasu SPL: model częstotliwości modów nie ma do tego wystarczających danych.
Docelowo mierzyć S0 osobno, a kilka bliskich punktów traktować jako diagnostykę wrażliwości na ruch głowy.
Przykładowa przyszła siatka to S0 oraz lewo/prawo i przód/tył w małej, jawnie zapisanej odległości; można dodać zmianę wysokości.
Wielkość przesunięć to parametr protokołu, nie norma ani próg akceptacji; nie uśredniać całej kanapy jako celu.

## 5. Co mogą dać dwa subwoofery

Dwa źródła mogą zmienić odpowiedź przestrzenną i rozdział obciążenia, ale korzyść zależy od położeń, fazy i dostępnej elektroniki.
Dla liniowej pracy w danym punkcie zespolone odpowiedzi sumują się: `p_sum(f) = p_A(f) + p_B(f)`.
Idealne podwojenie ciśnienia daje `20 log10(2) ≈ 6,02 dB` tylko dla równych, zgodnych w fazie wkładów w tym punkcie.
To warunkowa tożsamość, nie prognoza zysku dwóch subwooferów w pokoju ani gwarancja wzrostu maksimum użytecznego SPL.
Inne fazy, różne poziomy, zmiana ustawienia, wspólny zasilacz i limitery mogą zmienić korzyść lub prowadzić do lokalnego osłabienia.
Porównanie musi ujawniać, czy utrzymano pobudzenie każdego źródła, całkowite obciążenie i ustawienie głośności.
Po budowie mierzyć A, B oraz rzeczywiste A+B; przewidywana suma wymaga wspólnego czasu i zgodnej skali amplitudy.
Nie zakładać identycznego EQ i opóźnienia dla obu sztuk ani symetrii jako automatycznego optimum.
Pierwszy prototyp ma przygotować decyzję o drugiej sztuce; U-004 nie obejmuje teraz jej budowy ani pomiarów.

## 6. Przyszła kolejność integracji po budowie

1. Ustalić wtedy tor pomiarowy zgodnie z U-002 i potwierdzić zakres jego wiarygodności; nie dobierać go w tym rozdziale.
2. Zapisać konfigurację bazową: skrzynia, położenia, routing, poziomy, filtry ochronne, stan termiczny oraz tło pokoju.
3. Zmierzyć prototyp bez korekcji modów, przy małym pobudzeniu, w S0 i pomocniczo nearfield; zachować dane źródłowe.
4. Porównać wykonalne położenia, zmieniając jeden czynnik; po każdej zmianie zachować osobny identyfikator konfiguracji.
5. Gdy istnieją pozostałe sekcje, mierzyć je osobno, ustalić podział, poziomy, polaryzację i opóźnienia oraz sprawdzić rzeczywistą sumę.
6. Przy UMIK lub innym mikrofonie USB potwierdzić referencję czasu i obsługę oddzielnych zegarów; brak synchronizacji ogranicza wnioski fazowe.
7. Dopiero po ustawieniu i integracji stosować korekcję pokoju; zachować preset bazowy i każdą wersję pośrednią.
8. Zweryfikować S0 oraz sąsiednie punkty i później sprawdzić headroom, kompresję oraz zniekształcenia z docelowym presetem.

Nearfield pomaga diagnostycznie, ale nie ustanawia wolnego pola; podłoga tego pokoju nie tworzy warunków referencyjnego ground-plane.
Zgodnie z U-003 ground-plane pozostaje brakującą metodą odniesienia, bez obowiązku wykonania i bez blokowania researchu lub budowy.
SPL w pokoju zawsze otrzymuje point_id, pasmo, sygnał, czas, peak/RMS, stan termiczny i kryterium zakończenia próby.
Nie przenosić wyniku między punktami pokoju przez samo `20 log10(r2/r1)` ani nie zestawiać go bezwarunkowo z katalogowym wolnym polem.

## 7. EQ na końcu: pytania i ograniczenia

Przed korekcją rozróżnić problem źródła, podziału, polaryzacji, położenia i pomieszczenia; pojedynczy dołek nie wskazuje przyczyny.
Nie próbować usuwać głębokiego lokalnego znoszenia przez duży boost bez danych o jego stabilności i koszcie w headroomie.
Każde EQ opisać częstotliwością, wzmocnieniem, dobrocią i torem; ocenić również sumaryczny szczyt wzmocnienia całego łańcucha.
Filtry ochronne nie są korekcją modów i mogą być niezbędne od uruchomienia; ich obecność musi być jawna we wszystkich porównaniach.
Wyrównana odpowiedź przy małym sygnale nie dowodzi zapasu napięcia, wychylenia ani niskich zniekształceń przy dużym poziomie.
Nie obiecywać skrócenia zaniku na podstawie spłaszczenia wykresu; odpowiedź czasową trzeba później sprawdzić odrębną analizą.
Docelową krzywą i progi przedstawić do zatwierdzenia; w tym rozdziale nie ustalamy liczbowego ideału płaskości ani SPL.
Wynik strojenia S0 zachować oddzielnie od diagnostyki sąsiedztwa, aby nie ukryć wrażliwości przez uśrednianie.

## 8. Dokumentacja, stop i wynik obecnego etapu

Rejestrować szkic z osiami, dostępne położenia, wymiary wejściowe, założone c i wersję wzoru; wskazać źródło każdej wielkości.
Dla przyszłych sesji zachować pliki surowe, konfiguracje, preset DSP, czas odniesienia, zdjęcia, środowisko i manifest hashy.
Przerwać interpretację jako cechy urządzenia, gdy zmienia się pokój lub geometria bez porównywalnych danych; zawęzić wniosek do konfiguracji.
Nie kończyć strojenia na jednej korzystnej krzywej: sprawdzić powtarzalność S0, sąsiedztwo oraz wpływ korekcji na wymagane poziomy.
Jeśli ograniczenie toru lub niestabilny timing uniemożliwia odpowiedź, oznaczyć pytanie jako otwarte zamiast dopasowywać fazę do oczekiwań.
Wynik pierwszej wersji to mapa założeń i wykonalnych eksperymentów.
Wersję obliczeniową P26/P27 rozwijają [rozdział 09](09_zespolony_model_pokoju.md)
i raport 013; nadal nie mamy pomiaru odpowiedzi, RT, room gain ani maksymalnego SPL.
Pakiet do budowy powinien zachować możliwość przesunięcia skrzyni, odtworzenia konfiguracji i późniejszej kalibracji w innym pokoju.
Dalszą walidację opisuje `06_metrologia_i_walidacja.md`; organizację dowodów i decyzji rozwija `07_niepewnosc_i_organizacja_badan.md`.
