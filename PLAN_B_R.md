# Plan B+R prototypu subwoofera — wydanie 0.1

**Bieżący zakres zawężony w U-010 do tematów naukowych.** Aktywna kolejność:
[PLAN_BADAN_NAUKOWYCH.md](PLAN_BADAN_NAUKOWYCH.md). Dobór handlowy, wyceny,
zakupy i narzędzia CAD opisane poniżej pozostają odłożonymi etapami.

Data: 2026-10-23. Status: plan roboczy; rozpoczęto badania przed budową.
Podstawa: [brief v0.6](brief_system_audio_DIY_v0.6.md) i doprecyzowania użytkownika
z 2026-10-23 zapisane w [rejestrze decyzji](DECYZJE_I_PYTANIA.md).

Aktualizacja: **Sub12 i Sub15 zatwierdzone jako referencje (U-009)**.
Aktualizacja U-021: **front stały, niedemontowalny, pod jeden docelowo
wybrany przetwornik**. Regulacja objętości pozostaje aktualna.
Referencje monitorów odłożone; liczbowe progi nadal do wyprowadzenia.
Narzędzia CAD i ich MCP odłożone. Firecrawl dopuszczony obok browser-harness.

## 1. Wynik obecnego etapu

Celem jest pakiet pozwalający świadomie rozpocząć budowę pierwszego prototypu:
wybór przetwornika i alternatywy, porównanie objętości, projekt regulowanej
szczelnej skrzyni, dobór zewnętrznego napędu i DSP, kosztorys oraz dokumentacja
do CNC. Obecna praca obejmuje research, obliczenia i projektowanie. Samo
wykonanie skrzyni i badania gotowego produktu są następnymi etapami.

Użytkownik ma multimetr, oscyloskop i lutownicę. Dobór oraz zakup toru
pomiarowego odkładamy do zakończenia budowy. Nie uzależniamy researchu od
zakupu mikrofonu ani interfejsu. Późniejsze pomiary będą możliwe wyłącznie
w pokoju odsłuchowym; zakres twierdzeń o osiągach trzeba dostosować do tej sytuacji.

Projekt nie ma ustalonego limitu budżetu ani gabarytów. Optymalizujemy koszt
spełnienia wymagań, a nie najniższą cenę samego głośnika. Porównanie musi
pokazać użyteczne 20–40 Hz i headroom w basie elektronicznym, bez deklarowania
nieograniczonego SPL przy 20 Hz. Dwie sztuki i monitory trójdrożne są przyszłym
systemem; pierwszy prototyp ma dostarczyć wiedzy potrzebnej do tej decyzji.

## 2. Pytania badawcze i możliwe rozstrzygnięcia

| ID | Pytanie | Metoda obecnego etapu | Co zmieni decyzję |
|---|---|---|---|
| H1 | Czy pojedynczy 12″ wystarczy w wymaganym basie? | Krzywe granic wychylenia/napięcia/prądu, porównanie z 15″ | Niedobór przy 20–40 Hz mimo rozsądnej zmiany litrażu |
| H2 | Czy 15″ daje uzasadnioną korzyść kosztową? | Sd·Xmax, zapotrzebowanie na napięcie, masa i kompletna cena | Dopłata do napędu i skrzyni przewyższa korzyść albo mniejszy wariant spełnia wymagania |
| H3 | Jaki zakres regulacji objętości jest informacyjnie użyteczny? | Siatka Vb, czułość Fc/Qtc/F3/EQ, wykonalność wkładów | Dwie objętości mają zbyt podobną odpowiedź albo wymagają niepraktycznej konstrukcji |
| H4 | Ile kosztuje zejście ku 20 Hz? | Wariant bez EQ, łagodny cel, cel głębszy + HP i ograniczenia napędu | EQ wyczerpuje napięcie/Xmax wcześniej niż daje wymagany SPL |
| H5 | Co ogranicza konfigurację? | Osobne limity mechaniczne i elektryczne; brakujące dane cieplne jawne | Mocniejszy wzmacniacz nie pomaga przy ograniczeniu Xmax |
| H6 | Czy opinie ujawniają powtarzalny problem? | Relacje z pierwszej ręki, modele i warunki, kontrprzykłady | Potwierdzone powtarzalne awarie/hałas/rozrzut wymagają innego kandydata |
| H7 | Czy architektura rozwinie się do 8 torów? | Schemat routingu, poziomy, filtry, eksport, dostępne wyjścia | Wybrane DSP ma za mało niezależnych wyjść albo niewystarczającą ochronę |

Nie przyjmujemy hipotezy, że Qtc=0,707 jest zawsze optymalne, że większa moc
zawsze daje większy użyteczny SPL ani że obudowa zamknięta automatycznie ma
niższe zniekształcenia. Są to kwestie zależne od projektu i warunków.

## 3. Łańcuch prac do budowy

### R0 — wymagania, źródła i referencje

Wejścia: brief, aktualne uwagi użytkownika, katalogowe karty referencji.
Zadania: macierz wymagań, wybór kandydatów referencyjnych ADAM Audio,
opis peak/RMS, odległości, pasma i sygnału; lista danych niepublikowanych.
Nie zamieniamy katalogowego pojedynczego max SPL w wymaganie SPL przy 20 Hz.

Wynik: [macierz wymagań](WYMAGANIA.md), [referencje](raporty/003_referencje_i_rynek.md),
[rejestr źródeł](baza_wiedzy/ZRODLA.md). Do przedstawienia użytkownikowi:
modele referencyjne oraz progi, które da się uzasadnić. Akceptacja zamyka
specyfikację; research, obliczenia i analiza alternatyw trwają równolegle.

Scenariusze poziomu w sweet spocie: S1 = 6 dB poniżej przeliczonej referencji,
S2 = poziom referencji, S3 = 3 dB powyżej. Wartości −6/+3 dB są roboczymi
odstępami projektowymi, a nie kryteriami audytywnymi. Jeśli warunki referencji
są niepełne, scenariusz jest wyłącznie ilustracją odległości. Każdy scenariusz
ma osobne wiersze 20/25/31,5/40/63/80 Hz, burst i dłuższy sygnał. Niepublikowane
wartości pozostają puste do ustalenia; nie wyprowadzamy ich z jednej liczby max SPL.

### R1 — dane kandydatów i opinie

Porównać minimum trzy realne modele: 12″, 15″ i alternatywę. W rozszerzeniu
krótkiej listy uwzględnić co najmniej drugiego producenta, żeby porównanie
nie ograniczyło się do rodziny Dayton. RSS315HF-4 jest punktem odniesienia.

Dla każdego: karta T/S i rysunek, definicja Xmax, impedancja i temperatura,
status produkcji, cena brutto PLN/UE, dostępność, dostawa, gwarancja, reklamacje,
źródła pomiarowe i opinie. Sprawdzić spójność wzorami T/S; konflikt źródeł
zachować zamiast uśredniać. Recenzje sklepu nie są niezależnym laboratorium.

Opinie zbierać według [metody](baza_wiedzy/08_opinie_i_ocena_dowodow.md).
Minimum robocze dla finalisty: dwie niezależne relacje właścicieli lub jawny
brak takich relacji, plus dostępny test techniczny lub jawny jego brak.
Nie odrzucać głośnika wyłącznie z powodu małej popularności.

Wyjście R1: tabela porównawcza z lukami, dane maszynowe, rejestr sprzeczności.
Stop: brak kluczowych T/S uniemożliwia pełną symulację danego kandydata;
można kontynuować pozostałych. Brak ceny blokuje ocenę kosztu, nie analizę fizyczną.

### R2 — model i porównanie obudów

Wybrano na obecne polecenie użytkownika otwarty model Python: NumPy/SciPy,
wykresy Matplotlib, kontrola tożsamości w SymPy. Uruchomienie opisuje README.
Nie trzeba instalować każdej wymienionej biblioteki, aby poprawnie policzyć model.

1. Sprawdzić model na analitycznym rezonansie, granicy Vb→∞, zależnościach
   6 dB dla podwojenia napięcia i odległości oraz redukcji do modelu 2. rzędu.
2. Przeskanować Vb netto 30/45/60/80/100/120 l. To siatka startowa, nie limit
   gabarytów. Rozszerzyć, gdy krzywa korzyści nie została uchwycona.
3. Wyznaczyć Fc/Qtc/F3, odpowiedź napięciową, impedancję, Xpeak, prąd,
   moc rzeczywistą i stratę I²Re dla jawnych napięć.
4. Policzyć oddzielne granice Xmax, napięcia i prądu wzmacniacza. Moc katalogową
   stosować tylko jako przybliżony wskaźnik; model nie zna kompresji cieplnej.
5. Porównać brak EQ, cel umiarkowany i głęboki; włączyć HP, LP oraz headroom
   cyfrowy i analogowy. Pokazać również niespełnienie wymagań.
6. Osobno pokazać idealne 2π/1 m, przeliczenie 2,5–3 m i hipotetyczny wpływ
   pokoju. Scenariusze room gain nie są prognozą konkretnego mieszkania.
7. Czułość: Fs ±5%, Vas/Qes ±10% jako zakresy projektowe, nie zmierzone tolerancje.
   Nie udawać, że niezależne zmiany parametrów tworzą rozkład populacji produktów.

Wyjście R2: CSV, wykresy, manifest wejść i kodu, raport ograniczeń. Kandydat
wykonalny warunkowo, jeśli nie narusza jawnych ograniczeń modelu; niskie THD
pozostaje hipotezą do sprawdzenia po budowie. Obliczenia samych liniowych T/S
nie mogą rozstrzygnąć pełnej jakości użytkowej.

### R3 — koncepcja regulowanej skrzyni i wybór eksperymentu

Porównać MDF i sklejkę, masę, podatność dużych paneli oraz stałe połączenie
frontu z korpusem, serwis i osłonę. Według U-021 front będzie niedemontowalny,
pod jeden docelowy model. Warianty 12″/15″ porównujemy przed wyborem,
z odpowiednim zakresem Vb; nie wymagamy jednego frontu do kilku głośników.

Rekomendowany mechanizm do rozpatrzenia: maksymalna przestrzeń robocza
z mocowanymi sztywnymi modułami wypornościowymi; alternatywa: szczelna
przegroda montowana w kilku pozycjach. Zważyć stabilność, szczelność i dostęp.
Luźne miękkie wypełnienie nie jest regulacją geometrycznego litrażu.

Wyjście R3: 2–3 warianty geometrii, bilans brutto/netto, rozmieszczenie wręg,
zakres regulacji, masa orientacyjna i najmocniejszy argument przeciw każdemu.
Rysunki poglądowe nie są jeszcze plikami do zamówienia CNC.

### R4 — elektronika, DSP i koszt całego rozwiązania

Wybór napędu wynika z wymaganych Vrms/Ipeak, Z(f), zasilacza i chłodzenia.
Porównać moduły Hypex/ICEpower i sensowne alternatywy z dokumentacją.
Sprawdzić, czy moduł dostępny jest dla konstruktora jednostkowego.
Wszystko w zewnętrznej obudowie; porty, przewody i zabezpieczenia są częścią BOM.

miniDSP ma zapewniać docelowe 8 niezależnych wyjść. Sprawdzić rzeczywiste
wejścia, wersje analogowe/cyfrowe, napięcia, szum, routing, eksport i limitery.
Jeśli DSP nie realizuje potrzebnej ochrony, trzeba zaprojektować ją w innym
elemencie albo ograniczyć sygnał. Sam HP nie zapewnia pełnej ochrony.

Kosztorys: przetwornik + skrzynia/CNC + napęd/zasilacz/obudowa + DSP +
okablowanie + dostawa. Tor pomiarowy: pozycja odłożona po budowie, bez bieżącej
rekomendacji zakupowej. Każda cena ma URL, datę, VAT, walutę i warunki dostawy.
Brak danych zostaje jako „do wyceny”, bez pozornego kompletnego totalu.

Wyjście R4: koszt–osiągi/Pareto, najtańszy wariant spełniający uzgodnione
wymagania i konkretna korzyść dopłaty. Gdy żaden wariant ich nie spełnia,
zaproponować zmianę celu, większe Sd·Xmax lub rozdzielenie zadań na dwa subwoofery.

### R5 — pakiet gotowości do budowy

Warunki zamknięcia:

- Wybrany przetwornik, źródło zakupu i alternatywa; istotne braki ujawnione.
- Zaakceptowane referencje i priorytety wymagań; wyniki modelu odniesione do nich.
- Rysunek zewnętrzny/wewnętrzny, przekroje, netto i brutto, wręgi, moduły regulacji.
- Rysunek montażowy producenta sprawdzony; tolerancje uzgodnione z wykonawcą.
- DXF/STEP lub równoważna dokumentacja, rozpiska płyt, połączeń, uszczelek i śrub.
- BOM z wycenami, zewnętrzna elektronika, schemat połączeń, wersjonowane ustawienia DSP.
- Analiza ryzyk i uczciwy zakres tego, co prototyp ma zweryfikować po wykonaniu.

Nie zlecamy CNC na podstawie średnicy nominalnej ani przykładowej geometrii
z obecnego raportu. Pakiet wykonawczy jest osobnym rezultatem dalszych prac,
po porównaniu kandydatów. Aktualny raport inicjalny nie oznacza zamknięcia R5.

## 4. Kolejność i nakład

| Pakiet | Zależność | Orientacyjny nakład pracy | Kryterium końca |
|---|---|---|---|
| R0 | Brief | 0,5–1 dnia roboczego | Uzgodniony zakres i opisane braki referencji |
| R1 | R0 częściowo | 2–4 dni | Dane ≥3 modeli, rynek, opinie, sprzeczności |
| R2 | Dane R1 | 1–3 dni | Zweryfikowany model i porównanie wariantów |
| R3 | R2 | 1–3 dni | Uzasadniona geometria i regulacja |
| R4 | R2; równolegle z R3 | 1–3 dni | Dopasowany napęd/DSP i kosztorys |
| R5 | R0–R4 | 2–4 dni | Komplet wykonawczy do decyzji o budowie |

Nakłady są założeniami planistycznymi, nie obietnicą dat ani godzin pracy agenta.
Nie sumować bez uwzględnienia równoległości, odpowiedzi dostawców i iteracji.

## 5. Etapy po obecnym zakresie

P1: budowa mechaniczna, dokumentacja zdjęciowa, rzeczywiste wymiary i masa,
kontrole montażu, szczelności i podłączeń. P2: dopiero po budowie wybór toru
pomiarowego i wykonanie procedur z [bazy metrologii](baza_wiedzy/06_metrologia_i_walidacja.md).
P3: kalibracja sweet spotu, ocena stabilności w sąsiedztwie, integracja drugiej sztuki.
P4: aktywne monitory trójdrożne i całość systemu. P5: powtarzalność i pilotaż
w innych pokojach, ewentualna komercjalizacja z osobnym planem zgodności.

Każdy raport z pomiarów ma zawierać również wyniki negatywne, temperaturę,
ustawienia, surowe pliki i ograniczenia. Pomiary tylko w pokoju nie pozwalają
bez dodatkowych metod przypisać wynikowi warunków wolnego pola. Nie określamy
produktu jako masteringowy ani gotowy do sprzedaży na podstawie obecnej symulacji.

## 6. Najbliższy krok

Aktualizacja 2026-10-26: N7, rodziny gazu/promieniowania, nieliniowości
i pamięci mają wykonane zakresy z raportów 009–021. Kampania dwutonowa
P14B i rodziny cieplne P15B są zakończone w swoich dziedzinach (026/027);
P17 łączy warunkowe wymagania V/I/X/chłodzenia (028). Nie ponawiać tych
kampanii bez nowej hipotezy zmieniającej decyzję.

Mechanika doszła do frontu, styku w czasie i pełnej ramy 3D (033–036),
a P19E wyznacza wymagania sztywności stałego frontu (037). **Najbliższy
krok mechaniczny po P19F: zgodny lokalny podmodel front–dno–listwa
30 mm, porównanie 20 mm, zagęszczenie sąsiedniego MDF i wpływ odległości
granicy**, potem regulacja Vb i pole przestrzenne P20/P21.
Screening odspojenia nadal nie jest zbieżną prognozą odporności na pękanie.

Raport 040 ma 20 wariantów listwy i 40 obciążeń pełnej ramy. Nowa droga
siły odciąża pierwotną spoinę, lecz może skoncentrować naprężenia w nowych.
Pola naprężeń nadal różnią się o 17–27% przy N14/N18 dla 30 mm; globalny
spadek C około 2,6% nie zamyka nośności. Pole N14/B30 zachowano do podmodelu.

Raport 038 rozszerza pulę do 26 produktów / 27 konfiguracji elektrycznych,
w tym trzech SB Acoustics. Nowe SB mają odrębne obliczenia liniowe;
potrzebują analizy odporności i wspólnych wymagań, zanim wejdą do syntezy
finalistów. Dawne kampanie dla 24 baz nie stają się ich wynikami.

Raport 039 dodaje obliczenia ilości i położenia wypełnienia: masę,
porowatość, objętość gazu oraz 17 820 punktów napędu z warstwami 1D.
Dobór materiału i jego rozmieszczenia ma wejść do końcowej rekomendacji;
potrzebne jest powiązanie z przestrzenną komorą i regulacją Vb. Nie
utożsamiać porowatego tłumienia ze sztywnymi wkładami wypornościowymi.

Obowiązuje [program 30 pakietów](PROGRAM_30_BADAN.md); przewodnik po
wynikach to [README](README.md). P22–P30, pojedynczy wybór i końcowy PDF
pozostają otwarte. Oferty i dobór handlowy odłożono w U-010.
