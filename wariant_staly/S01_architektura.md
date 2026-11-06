# S01. Dwa jednakowe moduły zamknięte do systemu 2.2

Status: rekomendacja do projektu szczegółowego, CNC HOLD. Praca na osobnej gałęzi. Dokumentacja K30-K46 stanowi punkt porównawczy dla wariantu regulowanego. Ten raport dotyczy jednej sztuki, chyba że wskazano parę.

## Wymagania i decyzja

Dwa aktywne moduły samonośne, każdy z jedną komorą i z serwisem od przodu. Elektronika klasy D i zasilacz w oddzielnej wentylowanej przestrzeni. Preferowana pełna głębokość 450 mm, granica warunkowa 500 mm. Wybór do dalszego opracowania: RSS390HF-4, 102 l netto, geometria A. Priorytetem projektu pary jest pasmo 20 do 40 Hz i główny punkt odsłuchowy znany z P26. Wykonanie obejmie dwa wykończenia na tym samym froncie. Wskaźniki obejmują zapas napędu, reakcję pokoju, drgania, dostęp serwisowy oraz zużycie materiału.

## Porównanie napędów i stałego litrażu

Wspólna podstawa to [P29C](../raporty/055_wrazliwosc_wyboru_i_margines_glebokosci.md), jego zapisane 512 scenariuszy oraz [model liniowy](../skrypty/model_subwoofera.py). Do czterech finalistów włączono oba Daytony prowadzące w różnych warunkach cieplnych, model HO oraz pojedynczy STX. Wcześniejsze porównanie dwóch STX ma inną liczbę membran na moduł. Dla każdego finalisty przeliczono P29C przy nowej objętości. Wynik jest dolną obwiednią siatki scenariuszy i częstotliwości 20 do 80 Hz dla pojedynczej sztuki przy 1 m, w półprzestrzeni, 40 V RMS i 12 A RMS.

| Napęd | Minimum dB przy 25 / 50 / 100 W strat Cu | Zapas po DSP w 20 do 40 Hz przy 50 W, dB |
|---|---:|---:|
| RSS390HF-4 | 92,84 / 95,80 / 95,80 | 5,74 |
| RSS390HE-22, cewki szeregowo | 89,75 / 92,76 / 95,77 | 3,13 |
| STX W.32.800.8.FCX | 91,84 / 91,84 / 91,84 | 5,43 |
| RSS390HO-4 | 94,08 / 94,46 / 94,46 | 7,13 |

Ostatnia kolumna dotyczy osobnego testu nominalnego. Korekcja Linkwitza do górnoprzepustowego 20 Hz, Q=0,707, następnie dolnoprzepustowy LR4 przy 80 Hz. Ustalono 95 dB przy 40 Hz na moduł. Jest to punkt porównawczy, a nie specyfikacja poziomu w fotelu. Uwzględniono indukcyjność w odpowiedzi głośnika. Dla każdego tonu ograniczono napięcie, prąd, wychylenie szczytowe oraz moc w rezystancji cewki. RSS390HF-4 potrzebuje do 9,81 V RMS, 2,11 A RMS, 4,74 mm wychylenia i 13,35 W strat w badanym paśmie przy tym poziomie. Maksima mogą wypadać przy różnych częstotliwościach. Dla HE z tym samym filtrem docelowym potrzeba do 15,49 V. Zaletą HF jest najlepszy wynik odporności przy bazowym założeniu 50 W. HO wygrywa test nominalnego zapasu oraz przesiew stresowy przy 25 W. Przy 100 W różnica między HF i HE wynosi tylko 0,024 dB. Te dane nie rozstrzygają, który egzemplarz będzie miał najniższe THD/IMD.

Ceny poglądowe za sztukę podczas przeglądu 6 listopada 2026. [HF w LoudspeakerShop](https://loudspeakershop.eu/glosnik-dayton-audio-rss390hf-4-15-reference-sub-p-7660.html) 1613,33 PLN, deklarowany magazyn; [STX u producenta](https://stx.pl/manufacturer/stx/w-32-800-8-fcx.html) 990 PLN, dostępny; [HO w BlackDotAudio](https://blackdotaudio.eu/dayton-audio-reference-rss390ho-4-subwoofer%2C270%2C9951.html) 1676,08 PLN, chwilowo niedostępny; [HE w Audiophonics](https://www.audiophonics.fr/en/loudspeakers-subwoofers/dayton-audio-rss390he-22-speaker-driver-subwoofer-800w-22-89db-20hz-600hz-o381cm-p-17838.html) 449 EUR, strona jednocześnie wskazuje końcówkę zapasu i wycofanie produktu. Dostępność dwóch sztuk z jednej partii wymaga potwierdzenia. Koszt pary HF według pierwszej oferty to 3226,66 PLN przed pozostałym osprzętem.

Litraż badano od 70 do 160 l co 1 l. Reguła: wybrać najmniejszy nominalny litraż, który również po odchyleniu o ±3 l mieści się w 0,2 dB od najlepszego wyniku P29C dla HF przy 50 W. Budżet ±3 l to założenie projektowe obejmujące również niepewność wyporności części. Pierwszy wynik to 102 l, skrajna strata 0,189 dB. W 102 l Fc=34,21 Hz, Qtc=0,75 i F3=32,27 Hz przed korekcją. Opóźnienie grupowe po filtrach przy 20 Hz wynosi około 17,1 ms. Wyniki 91 objętości, charakterystyki i opóźnienia w sześciu punktach są w [danych obliczeń](s01_wyniki.json).

| Netto | Szczyt wzmocnienia elektrycznego filtra na badanej siatce | Zapas nominalny po DSP |
|---|---:|---:|
| 100 l | 9,11 dB | 5,56 dB |
| 102 l | 9,01 dB | 5,74 dB |
| 120 l | 8,16 dB | 7,16 dB |
| 150 l | 7,11 dB | 9,09 dB |

102 l to wybór przy priorytecie kompaktowego modułu i odporności na scenariusze P29C. Jeśli wymagany poziom przy docelowej krzywej przekroczy zapas tej konstrukcji, wrócić do 120 i 150 l. Przy tym samym poziomie większa komora wymaga mniejszej korekcji. Bez pomiaru kompresji, parametrów zależnych od wychylenia i odpowiedzi w pokoju maksymalny czysty SPL pozostaje otwarty.

## Geometria, bilans i mechanika

Każda geometria ma front 44 mm, tył i resztę ścian 22 mm. Komora ma 328 mm głębokości. Jedna poprzeczna wręga okienna z MDF 22 mm leży w połowie głębokości komory, z obrzeżem 30 mm. Środek przetwornika na środku frontu. Stalowy pierścień K42 wewnątrz laminatu frontu. Osobno liczone szacunki wyporności w każdej komorze: przetwornik 5,000 l, terminal 0,175 l, przewody i klej 0,150 l. Listwy i mechanizmy regulacji 0 l. Suma tych założeń i wręgi po odjęciu od brutto daje 102 l. Brak modelu rzeczywistego terminala i pomiaru wyporności przetwornika. Wypełnienie porowate osobno: sprawdzić zmianę podatności i strat pomiarem impedancji po dodaniu odważonej maty. Nie odjęto pełnej geometrycznej objętości maty.

| Wariant | Szer. × wys. × gł. korpusu, mm | Brutto / wręga, l | Masa płyt z wręgą, kg | Pierwszy mod tyłu, Hz | Ugięcie środka, mm/kPa | Przemieciona objętość tyłu, cm³/kPa |
|---|---|---:|---:|---:|---:|---:|
| A dolny | 816,8 × 473,4 × 394 | 108,83 / 1,51 | 32,51 | 117,4 | 0,16 | 23,16 |
| B uniwersalny | 619,8 × 619,8 × 394 | 108,77 / 1,44 | 31,74 | 99,7 | 0,23 | 31,83 |
| C boczny | 497,5 × 775,5 × 394 | 108,81 / 1,48 | 32,25 | 111,3 | 0,18 | 25,69 |

Masa przy 800 kg/m³ uwzględnia otwór frontowy. Do masy gotowej sztuki dodać przetwornik, okucia, maskownicę, podpory i różnicę masy stali względem MDF wybranego na kieszeń. Dwa razy masa płyt wariantu A to około 65 kg. Przy tym samym materiale różnica masy płyt A i B wynosi 0,77 kg na sztukę. Koszt obróbki, odpadu i oklein wymaga kalkulacji rozkroju i oferty frezarni.

Model porównawczy: płaska tylna płyta swobodnie podparta na czterech krawędziach, E=2 GPa, ν=0,3, 1 kPa równomiernego nacisku, szereg Naviera do 31 w obu kierunkach. Wręga stabilizuje ścianki boczne, nie podpiera środka tyłu. Nominalne naprężenie zginające w środku tyłu to około 0,22 / 0,20 / 0,22 MPa odpowiednio dla A/B/C. Wyniki dla pierwszych trzech postaci z parami indeksów znajdują się w JSON. Przemieciona objętość jest wskaźnikiem potencjalnego promieniowania niskoczęstotliwościowego. Nie ustalono poziomu dźwięku emitowanego przez ściany, naprężeń w spoinach ani modów całej skrzyni z otworem. Pierwsze osiowe mody gazu idealnego dla A/B/C wynoszą około 222/298/234 Hz. Wariant A ma najmniejsze ugięcie i najmniejszą przemieszczaną objętość tyłu oraz pasuje do niskiej zabudowy. B jest najlżejszy, C wygrywa szerokością. Dla dwóch identycznych modułów wybrano A z przewidzianym obrotem o 90° wokół osi promieniowania. Obrót zachowuje objętość i elementy nośne, zmienia rozstaw podparcia, stateczność, obciążenia grawitacyjne i pozycję źródła.

## Zabudowa, front i serwis

Budżet głębokości kompletnej: 394 mm korpusu + 38 mm kasety frontowej + 18 mm na wyjście przewodu = 450 mm nominalnie. Ostatnie 18 mm wymaga bocznego wyprowadzenia przewodu albo wpuszczonego złącza. Wartość graniczna pozostawia zerowy zapas na dodatnie tolerancje. Zmierzyć obwiednię z wybranym przewodem lub zmniejszyć głębokość korpusu i odpowiednio powiększyć pole frontu z ponownym bilansem. Dopiero udokumentowana kolizja uzasadnia rozważenie 500 mm. Wysokość z przykładowymi podporami 20 mm rośnie dla A do 493,4 mm lub 836,8 mm po obrocie. Zapewnić miejsce przed zabudową na wyjęcie całego modułu oraz osobno na wyjęcie głośnika.

Wspólny serwisowalny front FR1/FR2, pierścień i osiem gwintów M5 wg K42-K45, z nowymi współrzędnymi środka. Oba wykończenia na zdejmowanej ramce z mocowaniem poza obwodem uszczelnienia. Wewnętrzna strona tkaniny lub kratki powinna leżeć dalej niż najbardziej wysunięta ruchoma część kosza w spoczynku plus skok szczytowy, ugięcie ramki i tolerancja. Przykładowe 38 mm od płyty z ramką mającą 4 mm grubości pozostawia 34 mm do przeszkody, czyli 20 mm na pozycję spoczynkową, ugięcie i tolerancję po odjęciu 14 mm Xmax. Zmierzyć także zachowanie przy sygnale ograniczanym przez DSP. Sprawdzić świst, transmisję i brzęczenie obu kaset pomiarem A/B.

Oprzeć na niezależnym cokole przenoszącym obciążenie na podłogę, zostawić szczeliny od płyt meblowych i GK, przewód prowadzić luźną pętlą. Wstępne cztery podpory dla próbnej masy 50 kg i pionowej częstotliwości własnej 8 Hz: razem około 126 kN/m, około 31,6 kN/m i 123 N statycznie na podporę przy równym podziale. Ugięcie statyczne 3,88 mm. Dla liniowego oscylatora przy tłumieniu względnym 0,15 stosunek siły przeniesionej do wymuszającej wynosi około 0,24 przy 20 Hz i 0,075 przy 40 Hz. Wymuszenie przetwornika działa głównie poziomo. Osobno zmierzyć sztywność boczną, kołysanie i pełzanie pod rzeczywistym środkiem masy w obu orientacjach. Nie przypisywać liczb pionowych do GK. Do przenoszenia przewidzieć zdejmowaną podstawę transportową i uchwyty poza komorą. Udźwig, kotwienie zabezpieczenia przed przewróceniem, wymiary szczelin i nośność podłoża wymagają sprawdzenia dla zabudowy na miejscu.

## Pokój, monitory i zabezpieczenia

Zastosowano ten sam [pokój i punkty P26](../dane/konfiguracje/p26_scenariusze.json): X/Y/Z=3,7/4,6/2,5 m, słuchacz (1,85; 3,10; 1,10) m. Sprawdzono środek i sześć punktów przesuniętych o 15 cm poziomo lub 10 cm pionowo. Zsumowano zespolone ciśnienia dwóch źródeł skorygowanych DSP, przy stałej sumie modułów wag. Porównano cztery ustawienia, 15 kombinacji opóźnienia i wag na każde. Dla scenariusza nominalnego T60=0,4 s i relaksacja 0,2 s. W JSON podano współrzędne, dodatkowe scenariusze strat oraz kontrolę odcięcia bazy modalnej przy 60 zamiast 40 m⁻¹.

| Ustawienie | Rozstęp w centrum 20 do 40 Hz | Rozstęp w centrum 20 do 80 Hz | Największa zmiana po przesunięciu głowy, 20 do 80 Hz |
|---|---:|---:|---:|
| Dolny RTV | 5,64 dB | 51,46 dB | 22,49 dB |
| Boczne moduły | 5,62 dB | 42,32 dB | 14,78 dB |
| Ten sam A obrócony pionowo po bokach | 5,62 dB | 41,78 dB | 14,34 dB |
| Pozycja asymetryczna | 5,17 dB | 47,89 dB | 19,11 dB |

Tak duże rozstępy obejmują wąskie wygaszenia i filtr dolnoprzepustowy. Nie wolno na tej podstawie zamawiać mebli ani ustawiać dodatniej korekcji o kilkadziesiąt dB. Scenariusz boczny ma mniejszy najgorszy rozstęp w szerokim paśmie, asymetryczny nieco równiejsze 20 do 40 Hz. Modele ustawień jednocześnie zmieniają pozycję i wysokość. Wynik nie dowodzi przewagi samej proporcji C. Obrócony A w bocznych pozycjach uzyskał podobną odpowiedź jak C. Konieczny test rzeczywistych wnęk, tkaniny i monitorów. Model obejmuje ciśnienie modalne i uproszczone źródło, bez rozpraszania mebli oraz pomiarów pomieszczenia.

Dwa niezależne wyjścia DSP dla subów i po trzy dla każdego monitora, razem osiem. Utrzymać wcześniejsze punkty monitorów P26 jako założenie robocze i pozostawić strefy regulacji ich położenia. Start pomiarów: podział LR4 80 Hz, porównanie 60 i 70 Hz. Przy idealnie zgodnych centrach LR4 daje zgodne fazy i po −6 dB na gałąź przy podziale. Błąd drogi 0,34 m to około 0,99 ms lub 28,5° przy 80 Hz. Zmierzyć opóźnienie torów, fazę i polaryzację obu subów oraz monitorów oddzielnie. Wyrównać czas, potem skorygować szerokie maksima i sprawdzić sumowanie w siedmiu punktach. Modele nieznanych monitorów nie dają jeszcze rzeczywistej charakterystyki systemu 2.2.

Filtr transformujący wymaga około 9 dB elektrycznego wzmocnienia na badanej siatce. Ustalić rezerwę cyfrową, ograniczniki napięcia/prądu i ochronę wychylenia poniżej pasma. 40 V i 12 A RMS są oddzielnymi granicami modelu; wzmacniacz musi spełniać je na impedancji zespolonej, z rezerwą szczytową i wydajnością zasilacza obu kanałów. Wzmacniacz oraz zasilacz pozostają poza komorą, z dostępem do chłodzenia. Weryfikacja obejmie clipping, start filtrów, multiton 20 do 80 Hz, bursty muzyczne, pomiar Re(T), X oraz kompresji po nagrzaniu. Próba sinusoidalna wyznacza granicę modelową przy ustalonym sygnale. Nie dostarcza zmierzonego THD/IMD ani dopuszczalnego czasu pracy.

## Porównanie z regulowaną skrzynią i warunki przejścia do CNC

K30-K46 ma korpus 1080 × 500 × 432 mm w kolejności szerokość, wysokość, głębokość. Obsługuje trzy stany objętości i wymaga prowadnic, skrzynek oraz blokad. Stały A ma siedem płyt korpusu z podwójnym frontem oraz jedną wręgę. Zachowuje metodę pomiaru mocowania Daytona i umożliwia wymianę kasety frontowej. Dla tego samego przetwornika i tej samej rzeczywistej podatności liniowy model skupiony przewiduje tę samą odpowiedź niezależnie od sposobu uzyskania litrażu. Nowe proporcje wymagają osobnego sprawdzenia drgań płyt i wnęki. Nakład pracy i materiału można porównać po rozkroju i wycenie obu wariantów.

Przed zatwierdzeniem architektury wykonać model całej skrzyni z otworem, pierścieniem, połączeniami i podatną zabudową. Przeliczyć obie orientacje z rzeczywistą masą i wilgotnościowymi tolerancjami MDF, drogę przenoszenia oraz zabezpieczenia. Dobrać i zwymiarować konkretny terminal, przewód, geometrię ramki i kontrolowany prześwit. Ustalić docelowy SPL i kryteria kompresji oraz THD/IMD. Na prototypie zmierzyć rzeczywiste netto, impedancję, szczelność, drgania paneli i mebli, emisję maskownicy, obie pozycje pary oraz sumowanie z monitorami. Dopiero po akceptacji architektury przygotować rysunki wykonawcze i walidację CAM.
