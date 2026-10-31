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

U-024: po ukończeniu końcowego PDF opublikować **Release 1** na GitHub,
dołączyć raport i jego SHA-256 oraz wskazać sprawdzony commit. To warunek
końcowej publikacji, nie polecenie tworzenia wydania w obecnym etapie.

U-021,2026-10-25: front prototypu ma być stały, niedemontowalny,
pod jeden docelowo wybrany przetwornik. Zastępuje to wcześniejszy plan
wymiennego frontu; porównania kandydatów i regulacja Vb pozostają w zakresie.

Rozszerzenie SB, 2026-10-26: 26 produktów / 27 konfiguracji elektrycznych,
11 producentów, w tym trzy produkty SB i cztery STX. Raport 038 dodaje
5832 punkty liniowe. Historyczne kampanie dla 24 baz nie obejmują
automatycznie nowych produktów; ich niepewność i pełna integracja są otwarte.

Wypełnienie, raport039/P09C:18geometrii masy/porowatości,55modeli warstw
wtrzechpołożeniach i17820punktów dla27konfiguracji,80odrębnychrozwiązańFV.
Geometria wyklejenia5/6ścian nie jest tą samą geometrią co warstwa1D.
Dobór produktu,rzeczywistejmasy i rozmieszczenia oraz sprzężenie3D pozostają
częścią końcowej rekomendacji;sztywne wkładyVb są odrębnymP20.

## Macierz pokrycia

U-026,2026-10-27: głębokość zewnętrzna≤500mm,praca pionowo/poziomo
w zabudowie i preferowany głośnik w jednej z połów frontu. Dawne684mm
głębokości jest odniesieniem historycznym,nie wariantem dopuszczonym.
Nowa geometria musi wejść do P18–P21,P26–P29;dotychczasowych wyników
nie przepisujemy jako analizy nowej skrzyni.

„Częściowo” oznacza rzeczywisty wynik z niezamkniętym zakresem, nie procent
ukończenia. „Do wykonania” oznacza brak wymaganego eksperymentu. Nie zamykamy
pakietu samym stworzeniem planu, testów ani listy bibliotek.

| ID | Pakiet | Stan | Dowód i otwarty wynik |
|---|---|---|---|
| P01 | Literatura i rejestr twierdzeń | Częściowo | Źródła katalogowe; odczyt abstraktu Small1972 i dokumentacji KLIPPEL; dalsza bibliografia do weryfikacji |
| P02 | Wymagania i hipotezy | Częściowo | Brief, Sub12/Sub15 zatwierdzone; nadal brak porównywalnych progów pasmowych |
| P03 | T/S, Xmax, korelacje, identyfikowalność | Częściowo |26produktów/27konfiguracji/11producentów, w tym4STX i3SB; raport038:oryginały2nowychSB,5832punkty i audytT/S; wcześniej dowód nieidentyfikowalności i identyfikacja z2Vb, dane2próbekScan32; nieustalone tolerancje populacji |
| P04 | Formalne równania i granice | Częściowo | Model bazowy i N7; bilans/pasywność/stabilność, odrębne granice geometrii |
| P05 | Niezależna replikacja | Częściowo | N7: odrębny układ4równań, przestrzeń stanu i ODE; P07:algebra i odrębne oceny numeryczne; brak pełnej walidacji pomiarowej |
| P06 | Niepewność globalna i odporność wyboru | Wykonane dla liniowych rodzin D/L; integracja otwarta | 24 modele, 13 czynników, 6 pasm20–80Hz, lokalna/globalna czułość, Sobol N4096/16384, MC/QMC, 1728 obwiedni, 6624 relacje i jawne kontrprzykłady przy wspólnym napędzie; raport 015. Zakresy nie są tolerancją produkcji. Rozszerzenie na modele nieliniowe/termikę/konstrukcję pozostaje P29 |
| P07 | Ciągła objętość | Częściowo |20–150l co1l oraz analityczne granice po wszystkichVb>0 dla pojedynczych sinusów, kontrolowane288przypadkami; optymalizacja całego pasma/DSP otwarta |
| P08 | N7 — przecieki i straty | Częściowo wykonane | ModelCab||Ra,1728rekordów; granice, sumowanie fazorowe,72progi pomocnicze; brak identyfikacji fizycznegoRa |
| P09 | Wypełnienie, lepkość i straty cieplne gazu | Wykonane rodziny kontrolne i P09C; identyfikacja materiału otwarta | Raport016:24bazy,12096wierszytermiki,17280modeliwypełnienia,radialnaFV. Raport039:18geometrii,55warstw,17820punktównapędu27konfiguracji,80niezależnychsieciFV; masa/gaz/podatność oddzielnie. Produkt i sprzężenie3D otwarte |
| P10 | Adiabatyczne/izotermiczne powietrze | Wykonane rodziny gazu; integracja w rodzinach P13 wykonana | 56 rodzin bezwymiarowych, 15 552 wiersze dla przetworników i temperatur, 1440 offsetów, 384 modeli wyrównania DC, 42 bilanse nieliniowe. P13 dodaje sprzężony ruch, prąd i temperaturę; nadal model gazu idealnego, nie THD egzemplarzy |
| P11 | Obciążenie promieniowaniem i granice przestrzeni | Wykonane rodziny kontrolne; geometria docelowa otwarta | Tłok/Rayleigh, czasza/sfera/komora, kalibracja Mmd/Mms, wzajemne promieniowanie, obrazy i sprzężony pokój; 4 154 112 realizacji częstotliwościowych, replikacja Bellows2024, bilans energii i odrębna zbieżność. Raport 017. Brak niezależnej identyfikacji Mmd/strat wszystkich egzemplarzy i rozpraszania na finalnej skrzyni |
| P12 | BL(x),Cms(x),Le(x,i),Rms(v) | Wykonane rodziny warunkowe i pamięć; identyfikacja fizyczna otwarta | Raport020:12 096przypadków. Raport021/P12C: moduł/fazaLgen, dodatnia pamięć i prawidłowa siłaL2R2,30odczytów, dokładne wykluczenie jednej gałęzi dla zapisanych przedziałów i niejednoznaczność dopasowańN3. To nie identyfikacja24produktów ani dowód niemożliwościN2 |
| P13 | Sprzężony ruch nieliniowy i gaz | Wykonane dla hermetycznego gazu i wybranych rodzin | Raport020:12 096punktów i72kompensacje. P12C dodaje1728ODE z pamięcią;17flag rozstrzygniętoRadau. Brak czasowej reakcji frontu, nieliniowego przecieku, wszystkich gałęzi i fizycznej identyfikacji; raport021 |
| P14 | THD i IMD | Wykonane rodziny P14B; identyfikacja fizyczna otwarta | Raport026:3312przypadków,23flagi rozstrzygnięteDOP853,4odrębneRadau,16560projekcji,39744fazory, faza/mały sygnał/preload. Zamknięty zadany zbiór modeli,nie THD produktów ani pełna emisja rzeczywistego tłoka |
| P15 | N8 — model cieplny w czasie | Wykonane rodziny P15A/P15B; parametry produktów otwarte | Raport025:4225sieciCauer/Foster i granice. Raport027:2304przebiegiRe(T),ruchu,strat i przyjętej konwekcji,4pełneODEaudio,1152porównania obwiedni. Brak identyfikacjiR/C, lokalnych gradientów i powietrza skrzyni |
| P16 | Sprzężenia cieplne i elektromechaniczne | Częściowo — Re(T),ruch i chłodzenie | P15B sprzęga prąd,Re(T),ruch i straty; twierdzenie napięciowe dla stałego biernego tła. Nie wykonano fizycznej identyfikacjiBL(T),pełnych dużych sygnałów, gradientów i wszystkich sprzężeń termicznych |
| P17 | Łączne granice użytecznego zakresu | Częściowo — wspólneV/I/X/chłodzenie | Raport028:5184zestawy,31104punkty,analityczne przedziałyVb>0,26246niezależnych brzegów i3tożsamościSymPy. Stały poziom wyjściowy i warunkoweRth. Nie zintegrowano jeszcze rzeczywistegoTHD,ciągłego pasma,muzyki,konstrukcji i pokoju |
| P18 | Płyty MDF: drgania, naprężenia, promieniowanie | Częściowo — P18A–E w modelach kontrolnych | Raport029:płyty. Raport033:front. Raport035:pełna rama6brył/12spoin,siatki do36771DOF,168punktówharmonicznych,ściągi i podparcie. U-021:frontstały;geometria finalna,frez,promieniowanie i porównanieMDF/sklejka zR3 otwarte; P18E/raport059: 27 modeli podatnych wręg, do 5070 DOF i zbieżność; nie pełny MES całej skrzyni |
| P19 | Usztywnienia, połączenia i klej | Częściowo — wykonane rodziny P19A–P19G | Raporty030–040:spoiny,styk,pełna rama,listwa. Raport041:24podmodele/144okna/do102033DOF,przekazanie stóp i dwa kierunki siatki. Wpływ pola N14/N18 większy niż ostatnie lokalne zagęszczenia;nośność,Gc,SN/J(t) i identyfikacjaMDF otwarte |
| P20 | Regulacja objętości | Częściowo — P20A–D w modelach konstrukcji | Raport042:108układów/78modułów. Raport043:56modeli przegrody. Raport044:18brył zklejem,1944porty gazu,11664punkty napędu27konfiguracji,24pełne MES+gaz,ciągłe wymaganieE,8flag siatki rozstrzygnięte n16/do40248DOF. Pole3D gazu,rzeczywisty mechanizm i mocowania otwarte; P20D/raport057: geometra 1000×440×500 mm, tory wkładów, obrys i ograniczenia maskownicy, bez gotowych rysunków |
| P21 | Wewnętrzne pole i sprzężenie paneli | Częściowo — P21B/C/D/E/F/G, nowy port z podatnymi ścianami | P21D/060: sztywne wręgi/wkłady P20D i materiał modelowy. P21E/064: jednorodny gaz + jeden mod sprężysty. P21F/065: 52 272 punktów modalnej pustej komory. **P21G/066**: przestrzenne FV z bryłami P20D, powierzchniowymi portami dwóch podatnych ścian; 29 faktoryzacji gazu, 348 odpowiedzi trzech głośników, 3 kroki siatki, wzajemność i bilans mocy. Nadal wyłącznie uproszczone ugięcie paneli, zastępcza bryła kosza oraz fenomenologiczny model wypełnienia. Pełny MES konstrukcji, lokalne naprężenia i promieniowanie paneli, rzeczywisty materiał i integracja DSP pozostają otwarte. |
| P22 | Napęd, impedancja wyjściowa i clipping | Częściowo — P22A/P22B + P22C: 99 900 obliczeń DSP/amp/Z(f) | P22C: 5 przetworników, 5 Vb, 4 moduły, Flex Eight RCA2V / Flex HTx RCA2V/TRS4V, 3 hipotetyczne budżety strat cewki, 111 częstotliwości; niezależna kontrola Python 99900, bilans energii rzędu 1e-15. Wykryto i skorygowano błąd RMS vs Xmax szczytowego w poprzednich 180 i 274725 wynikach. NC500MP 500W/4ohm jest czasowo ograniczone, producent podaje 100W mocy ciągłej przy 25°C; NCx252MP/NC252MP 50W/kanał. To nie certyfikat czystego SPL ani dynamiki SMPS, brak zidentyfikowanego clippingu, THD/IMD, pomiarów i cen BOM. Raport P22C 31.10.2026. |
| P23 | Cyfrowa korekcja, faza i opóźnienia | Częściowo — P23A i brief porównania dwóch centralnych DSP | Raport046: 27 konfiguracji, 972 projekty, 4860 kaskad, świadkowie wysokiej precyzji. Nowy brief: miniDSP Flex Eight RCA 2 Vrms, 96 kHz versus Flex HTx RCA 2 Vrms i symetryczne TRS 4 Vrms, 48 kHz; 8 kanałów na 6 monitorów i 2 niezależne subwoofery. Nie wykazano możliwości wgrania algorytmu P25E jako natywnego zabezpieczenia ani zgodności realnego gain/clip z modułami. |
| P24 | Dynamiczna ochrona | Częściowo — P24A; nowa granica 75–150 l i wymóg ochrony X/T | Raport049: świadkowie X/I/θ, ciągłe ODE, matematyczna klasa obszaru bezpieczeństwa. Nowy brief nie pozwala przenieść limitów z 120 l na 75–80 l i zakłada osobną ochronę ruchu X(t), termikę Re(T) z pojemnością cieplną, możliwość czujników U/I oraz bezpieczne pełne wejście ze streamera; brak rzeczywistych BL(x), Cms(x), Rth/Cth i finalnych progów. |
| P25 | Sygnały wielotonowe i realistyczne | Częściowo — P25C/D/E oraz nowy brief dwóch niezależnych subwooferów | P25C 216 przebiegów, P25D 144, P25E 288 trajektorii; dowód granicy ZOH dla przyjętych perturbacji, lecz żaden nie został zwalidowany na miniDSP Flex Eight/HTx i nowej obudowie 75–80 l. Wymagane sprawdzenie opóźnienia, dostępności wejścia U/I, natywnego kompresora i zabezpieczenia w najwyższym poziomie streamera. Nie uważać modelowego przekroczenia energii za dowód uszkodzenia. |
| P26 | Zespolony model pokoju ze stratami | Częściowo | Rodzina modalna, 4 ustawienia × 9 scenariuszy strat; Green 1D, pasywność i zbieżność, raport 013. P11 dodaje reakcję pola na napęd i gęstą siatkę, raport 017. Pozycje/straty i rozpraszanie na bryle rzeczywistej pozostają nieznane; P26D/raport061: osiem orientacji brył × dziewięć środowisk, bez rzeczywistego RT60 i rozpraszania brył |
| P27 | Jeden/dwa subwoofery i ustawienie | Częściowo | 4 scenariusze przy monitorach, 15 876 wierszy S0, 1512 diagnostycznych, 120 przypadków fazy i 48 koniecznych testów gabarytu. U-020 zmienia docelowo kanapę na prawą iRTV na lewą stronę rzutu; konfiguracjav2 i raport019. Wymiary U-019 aktualne; dawne S0 i pozycje nadal nie są pomiarem; P27D/raport061: wspólny budżet dwóch źródeł, nominalne gain/delay nie odporne na straty |
| P28 | Integracja monitorów i8wyjśćDSP | Częściowo — macierz 2→8 i idealne LR4 | Raport053: kontrola sumowania i stabilne filtry software; faza, opóźnienia i realne monitory nadal nieznane |
| P29 | Odporna optymalizacja wielokryterialna | Częściowo — 34 produkty / 35 konfiguracji, nowy przesiew po korekcie | C02 nadal tylko wstępny faworyt. 75/80/100/120/150l oraz zweryfikowany rejestr 9 marek: 274725 liniowych scenariuszy **przeliczono** z prawidłowym Xpk=√2 Xrms, 33 konfiguracje kompletne, 2 HOLD (EMS brak T/S, SUPRAVOX niespójność Mms). 180 oryginalnych świadków C02 również zastąpiono poprawnymi. P22C osobno 99900 przypadków 5 finalistów/4 wzmacniaczy/3 ścieżek DSP; wzmacniacze używają katalogowych referencji napięciowych, brak rzeczywistego czystego SPL, pełnych kosztów, THD/IMD, badań ciągłego grzania i pełnego wykonania P01–P30 na każdym nowym modelu. |
| P30 | Odtwarzalność i przyszły protokół | Częściowo — repo dokumentuje nowy audyt producentów, bez archiwum binarnego wszystkich PDF | Nine-brand frozen JSON pod dane/karty_producentow, oficjalne URL, warianty i definicje Xmax/mocy, skrypt pobrania i SHA-256, audyt Qts/Mms/BL/Vd; 180 punktów źródłowego scenariusza Dayton w CSV + JSON. Nie ma oryginalnych PDF w repo z powodu nierozstrzygniętych praw do redystrybucji ani pomiarów FRD/ZMA/large-signal. Należy utrwalić wersjonowane binaria wyłącznie z legalnym zezwoleniem, a potem zweryfikować całą pulę na jednolitych protokołach. |

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
(raport 013); nie zastępuje to pozostałych pakietów. P06 wykonano dla zadanych
liniowych rodzin (raport 015). P09/P10 mają wykonane rodziny z raportu 016.
P11 wykonano dla jawnych geometrii kontrolnych i sprzężonego pokoju
(raport 017). P12/P13 mają wykonane rodziny warunkowe (raport020).
P12C ma wykonane rodziny z raportu021. P14B wykonano w zadanej dziedzinie
(raport026), a P15A/P15B mają wykonane rodziny cieplne (raporty025/027).
P17ma wykonaną syntezęV/I/X/chłodzenia i objętości (raport028).
Wykonano podstawyP18A/P19A i odniesienieP21A (raporty029–031).
P18B/P19B dodają front z otworem,koszem i jednostronny styk (raport033).
P19Crozstrzyga konkretny zmiennystyk80Hz wjawnejrodzinie (raport034),
ze zbieżnościąredukcji i odrębną propagacjąpełnegoMES2959DOF.
P18C/P19Dmają wykonaną referencyjną pełnąramę i screeningubytku spoiny
(raporty035/036). U-021ustala front stały pod jeden docelowy przetwornik.
P19Ewyznacza wymaganiamodułu spoinw12scenariuszach (raport037).
P19Fzbadał listwę20/30/40mm,masę,prawidłowyportciśnienia i dwie nowe spoiny
(raport040). Lokalnenaprężenia sąniezbieżne mimo stabilniejszej korzyściC.
P19Gwykonał podmodel zezgodnymi siatkami i obciążeniami rzeczywistych
wycinków,24realizacje i kontroletransferu(raport041). Lokalna rozdzielczość
nie zastępuje niepewnego pola globalnego lub danych materiałowych.
P20Awykonał badania sztywnych/pustychwkładów,dostępu,netto,podatności,
szczelności i mocowań (raport042). Tory translacji są zweryfikowane w swej
klasie, a część formalnych modów0Dwychodzi poza referencję przestrzenną.
P20Bporównał przegrodę zmodułami przy wspólnymgazie iβK, uwzględniając
dwa ciśnienia,masękrzyżową,podatne mocowania,przecieki i ekranydziedziny.
SRC54/55:9pierwotnychwariantów sklejki i porównaniepasa;pełny materiał
ortotropowy i klejenie do powierzchni pozostają otwarte.
P20Cwykonał pełnąbryłę ze spoinami3D i dwoma portami,6pierwiastków
ciągłego wymaganegoE oraz dodatkowe siatki po8flagach. Nośność/relaksacja
nie wynika ze sztywności; gaz0D pozostaje odrębnym przybliżeniem.
Najbliższykrok:P21B—przestrzenny gaz wewnątrz modułu i praca na wspólnej
granicy z bryłą,energia i granica0D. Następnie główna komora zregulacją
i porowatymwyklejeniem. Zachować kontrolnyport sztywno blokowanejprzegrody,
nie zamykać wyboru metody zgóry. Potem
czasoweDSP/napędP22–P25, pokójP26–P28 i integracjaP29/P30.
Poszukiwanie danych materiałowych i nieliniowych może toczyć się równolegle
z obliczeniami niewymagającymi tych danych. Nie wykonywać zakupów.

## Aktualizacja 2026-10-29 — następny krok po P21B/P21C0

Zamknięto zadaną rodzinę P21B, zachowując historyczną migawkę 17/18.
P21C0 bada puste sztywne komory o głębokości do 500 mm i skończone
źródło kwadratowe; nie zamyka całego P21C. Teraz: uzgodnić port
skończonej membrany i Mmd/Mms, następnie dodać przestrzenną regulację,
wypełnienie i podatność ścian. Nie przenosić małej korekty małego modułu
na port głównej komory. P29, końcowy wybór i PDF pozostają otwarte.


## Postęp 2026-10-30 — P21C1, wyłącznie badania lokalne

Użytkownik wstrzymał publikację i PR; nie ponawiać zapisu GitHub.
Raport 051: równoważny tłok kołowy z Sd 26 produktów, 27 geometrii,
1103 dopuszczone źródła, 301 odrzuconych, 6618 punktów i 451 par położeń.
To model pustej sztywnej komory, nie rzeczywisty stożek/kosz lub finalny Vb.
Rzędy 80/160/320; Parseval ogranicza ogon do 3.943e-5 R (ocena float).
Sześć niezależnych całek po dysku oraz trzy świadki obrotu, masy i rzędu 640.
Zmiana bezwładności po przesunięciu do 4.215 g; nie dodawać jej bez
uzgodnienia do Mms. Wykres 96 sprawdzony wizualnie; dane i hashe p21c1/manifest_P21C1.
Następny krok: kołowy port z przestrzennym wypełnieniem i regulacją,
następnie podatne ściany i bilans mas napędu. Wybór/PDF pozostają otwarte.


## Postęp 2026-10-30 — P21C2/C3, P18D i P29A/B/C

Nowsze polecenie użytkownika ponownie autoryzuje PR oraz kontynuowanie badań;
zastępuje wcześniejszy zakaz publikacji, ale nie zleca merge ani Release.
Raporty 052–055: przestrzenne warstwy i wkłady, zagęszczenie FV, front
z przesuniętym otworem, porównanie 27 konfiguracji i warunkowa rekomendacja
C02 RSS390HF-4, start około 120 l, regulacja 100/120/150 l.
Korpus 880×480×500 mm, front 44 mm; całkowity obrys z maskownicą nadal otwarty.
P29C koryguje regułę: próg 0,2 dB spełnia już 100 l (99 l na nowej siatce),
120 l to punkt eksperymentu, nie matematycznie minimalna objętość.
Przecięcie C02/C11 przy 86,813 W jest wynikiem scenariusza, nie pomiarem
chłodzenia. Przy 470 mm obecne wkłady kolidują z matą na 6 mm.
Hashe: wyniki/manifest_rekomendacji_P29.json. Brak pomiarów urządzenia,
realnego presetu ochrony X/T i pełnego sprzężenia; nie zamykać 30 pakietów.
Najbliższy krok: spójna geometria wręg/dostępu/obrysu, następnie ochrona
czasowa nowego układu. Zachować stare dane, nie dodawać masy powietrza dwa razy.


## Aktualizacja 2026-10-31 — badania Work 056–061

Najnowsza seria obejmuje: P20D (wspólna geometria, dostęp do wkładów i obrys),
P18E (podatne wręgi, modele zredukowane), P21D (przestrzenny port i napęd),
P25C (216 krótkich przebiegów ochrony), P26D/P27D (osiem geometrii
dwóch źródeł w dziewięciu założonych środowiskach) oraz audyt P30.
Wyniki są w raportach 056–061; wejścia, skrypty, surowe dane i wykresy
są w odpowiednich katalogach. Nie należy dodawać skutków podatnych
ścian do P21D bez bilansu energii, ani nazywać P25C gotową ochroną
sprzętu lub P26D pomiarami konkretnego pokoju.
Ceny nie zostały jeszcze włączone; obowiązuje kryterium wyboru
najtańszego przetwornika spełniającego łącznie wymagania.
