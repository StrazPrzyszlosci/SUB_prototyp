# Program badań przed prototypem — 30 pakietów

Podstawa: program przekazany przez użytkownika, zachowany bez zmian w
[materiale źródłowym](dane/zrodla/materialy_uzytkownika/program_30_pakietow_20261023.txt).
Obowiązuje także [brief v0.6](brief_system_audio_DIY_v0.6.md) i późniejsze decyzje.
Oznaczenia P01–P30 odnoszą się do nowego programu; dawne N7 odpowiada P08,
a dawne N8 odpowiada P15. Nie zaczynamy ponownie wykonanych rachunków.

**Końcowy PDF dopiero po przejściu całego programu prac bez sprzętu.**
Ma wskazać jeden głośnik i jedną konstrukcję regulowanej obudowy, z materiałem,
grubościami, usztywnieniami, połączeniami i obliczeniowym doborem kleju.
Modele warunkowe mają ujawniać nieznane dane; nie zastępują badania urządzenia.

## Macierz pokrycia

„Częściowo” oznacza rzeczywisty wynik z niezamkniętym zakresem, nie procent
ukończenia. „Do wykonania” oznacza brak wymaganego eksperymentu. Nie zamykamy
pakietu samym stworzeniem planu, testów ani listy bibliotek.

| ID | Pakiet | Stan | Dowód i otwarty wynik |
|---|---|---|---|
| P01 | Literatura i rejestr twierdzeń | Częściowo | Źródła katalogowe; odczyt abstraktu Small1972 i dokumentacji KLIPPEL; dalsza bibliografia do weryfikacji |
| P02 | Wymagania i hipotezy | Częściowo | Brief, Sub12/Sub15 zatwierdzone; nadal brak porównywalnych progów pasmowych |
| P03 | T/S, Xmax, korelacje, identyfikowalność | Częściowo |24modele/11producentów, w tym4STX; dowód nieidentyfikowalności i syntetyczna identyfikacja z2Vb; zweryfikowane wzrokowo dane2próbekScan32; nieustalone tolerancje populacji |
| P04 | Formalne równania i granice | Częściowo | Model bazowy i N7; bilans/pasywność/stabilność, odrębne granice geometrii |
| P05 | Niezależna replikacja | Częściowo | N7: odrębny układ4równań, przestrzeń stanu i ODE; P07:algebra i odrębne oceny numeryczne; brak pełnej walidacji pomiarowej |
| P06 | Niepewność globalna i odporność wyboru | Do wykonania | Wcześniejsza lokalna czułość nie jest analizą globalną ani uzasadnionym MonteCarlo |
| P07 | Ciągła objętość | Częściowo |20–150l co1l oraz analityczne granice po wszystkichVb>0 dla pojedynczych sinusów, kontrolowane288przypadkami; optymalizacja całego pasma/DSP otwarta |
| P08 | N7 — przecieki i straty | Częściowo wykonane | ModelCab||Ra,1728rekordów; granice, sumowanie fazorowe,72progi pomocnicze; brak identyfikacji fizycznegoRa |
| P09 | Wypełnienie, lepkość i straty cieplne gazu | Do wykonania | Absorpcja nie jest utożsamiana z przeciekiem |
| P10 | Adiabatyczne/izotermiczne powietrze | Częściowo | Adiabatyczna siła przy zadanym ruchu; relaksacja cieplna otwarta |
| P11 | Obciążenie promieniowaniem i granice przestrzeni | Częściowo | Dwie monopole diagnostyczne; brak pełnej reakcji i dyfrakcji obudowy |
| P12 | BL(x),Cms(x),Le(x,i),Rms(v) | Częściowo — źródło | Obejrzano oryginalne krzyweKLIPPELScan32 i odczytano progi zeźródła; nie zdigitalizowano krzywych ani nie uruchomiono modelu nieliniowego |
| P13 | Sprzężony ruch nieliniowy i gaz | Do wykonania | Dotychczas siła gazu przy narzuconym ruchu, nie pełne równanie nieliniowe |
| P14 | THD i IMD | Do wykonania | Tylko po rozwiązaniu P12/P13, z kontrolą zbieżności i faz |
| P15 | N8 — model cieplny w czasie | Do wykonania | Re×1,25/1,5 to czułość; brak identyfikacjiRth/Cth |
| P16 | Sprzężenia cieplne i elektromechaniczne | Do wykonania | Potrzebne granice i scenariusze wymiany ciepła, bez fikcyjnych temperatur |
| P17 | Łączne granice użytecznego zakresu | Częściowo | Granice liniowe; warunkoweTHD i termika do połączenia |
| P18 | Płyty MDF: drgania, naprężenia, promieniowanie | Do wykonania | Najpierw płyty analityczne/2D, bez rozpoczynania pracy nad narzędziamiCAD |
| P19 | Usztywnienia, połączenia i klej | Do wykonania | Obowiązkowy dobór kleju: nośność spoiny iMDF, odrywanie, pełzanie, wilgotność, szczelina, zmęczenie |
| P20 | Regulacja objętości | Częściowo | Koncepcje i bilans brutto/netto; mechaniczna analiza porównawcza otwarta |
| P21 | Wewnętrzne pole i sprzężenie paneli | Do wykonania | Mody komory, ciśnienia lokalne; sprzężenie gdy uproszczenie nie wystarcza |
| P22 | Napęd, impedancja wyjściowa i clipping | Częściowo | Dotychczas idealne ograniczeniaV/I; dynamika i obciążenie rzeczywiste otwarte |
| P23 | Cyfrowa korekcja, faza i opóźnienia | Częściowo |216wzorców analogowych; realizacja dyskretna i stabilność otwarte |
| P24 | Dynamiczna ochrona | Do wykonania | Wychylenie, napięcie, prąd, cieplna pamięć i overshoot |
| P25 | Sygnały wielotonowe i realistyczne | Do wykonania | Sinusy nie zastępują sumy widma; legalne źródła lub sygnały syntetyczne |
| P26 | Zespolony model pokoju ze stratami | Częściowo | Rodzina modalna ze stratami i zerowym członem kompresji, 9 scenariuszy; niezależny Green 1D, pasywność i zbieżność; pozycje/straty rzeczywiste nadal nieznane, raport 013 |
| P27 | Jeden/dwa subwoofery i ustawienie | Częściowo | 4 scenariusze przy monitorach, 15 876 wierszy S0, 1512 diagnostycznych, 120 przypadków fazy i 48 koniecznych testów gabarytu; rzeczywiste ustawienie otwarte |
| P28 | Integracja monitorów i8wyjśćDSP | Do wykonania | Wyłącznie architektura i modele sekcji; zakup/model monitorów odłożony |
| P29 | Odporna optymalizacja wielokryterialna | Do wykonania | Szeroka pula ma24modele i wspólne obliczenia; pełny front i pojedynczy wybór po integracjiTHD/termiki/DSP/konstrukcji |
| P30 | Odtwarzalność i przyszły protokół | Częściowo | Kod, hashe i archiwa; pełny rejestr hipotez oraz eksperymentów rozróżniających do zamknięcia |

## Bramka końcowego raportu

Każdy pakiet wymaga: hipotezy, równań, wejść i jednostek, eksperymentu,
niezależnej kontroli, analizy zbieżności/granic, niepewności, wyniku i wpływu
na decyzję. Brak danych uruchamia poszukiwanie źródeł i badanie identyfikowalności;
nie upoważnia do podania fikcyjnych wyników ani do pominięcia pakietu.

Wykonane warunkowe rodziny modeli można zamknąć jako wynik naukowy,
jeżeli ich dziedzina, ograniczenia i zależność decyzji od nieznanych parametrów
są faktycznie zbadane. RzeczywisteTHD, temperatura i pokój pozostają odrębną
walidacją po budowie. Końcowy wybór dotyczy najlepszego eksperymentu/prototypu
w świetle wykonanych badań, z jawnym uzasadnieniem ryzyka.

## Najbliższa sekwencja

N7/P08 wykonano w modelu zredukowanym, szeroką pulę rozszerzono i policzono.
W odpowiedzi na przypomnienie o wymiarach pokoju rozpoczęto niezależnie P26/P27
(raport 013); nie zastępuje to pozostałych pakietów. Kontynuować P06 jako
najbliższy krok oraz dane nieliniowe, następnie modeleP09–P17,
mechanikęP18–P21 z doborem kleju,
czasoweDSP/napędP22–P25, pokójP26–P28 i integracjaP29/P30.
Poszukiwanie danych materiałowych i nieliniowych może toczyć się równolegle
z obliczeniami niewymagającymi tych danych. Nie wykonywać zakupów.
