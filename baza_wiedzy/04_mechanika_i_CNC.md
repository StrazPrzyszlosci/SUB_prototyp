# 04. Mechanika obudowy badawczej i przygotowanie konstrukcji do CNC

## Status, źródła i zakres

- **[Wymaganie — brief]** Podstawą jest [brief v0.6](../brief_system_audio_DIY_v0.6.md): prototyp zamknięty, regulowana objętość, wymienność przetworników oraz zewnętrzna elektronika.
- **[Ustalenie — użytkownik]** Aktualnie prowadzimy prace badawcze do budowy; nie wykonujemy obudowy, nie kontaktujemy wykonawcy i nie zamawiamy CNC.
- **[Ustalenie — użytkownik]** Posiadane narzędzia to multimetr, oscyloskop i lutownica; dobór oraz zakupy toru pomiarowego nastąpią po budowie, a późniejsze pomiary wyłącznie w pokoju.
- **[Model/metoda]** Tym oznaczeniem objęto wiedzę inżynierską, wzory i procedury; nie są to wyniki pomiarów, wykonanej symulacji ani potwierdzenie osiągów konstrukcji.
- **[Deklaracja oferty]** Dane diyKraft, oferta Allegro nr 17586111495, pochodzą z informacji przekazanych przez użytkownika; nie sprawdzano strony, parku maszynowego ani wykonanych elementów.
- **[Rekomendacja]** Rozdział czytać wraz z [planem B+R](../PLAN_B_R.md), gdy powstanie; szczegóły oferty mają trafić do osobnego [WYKONAWCA_CNC.md](../WYKONAWCA_CNC.md).

## Objętości: trzy różne wielkości

- **[Model/metoda]** Gabaryt zewnętrzny opisuje zajęte miejsce; dla prostopadłościanu jego objętość wynosi `V_zew = W_zew H_zew D_zew` i nie jest objętością powietrza.
- **[Model/metoda]** Geometryczna objętość wewnętrzna brutto `V_brutto` to przestrzeń ograniczona wewnętrznymi powierzchniami obudowy przed odjęciem elementów zajmujących tę przestrzeń.
- **[Model/metoda]** Dla prostych ścian `W_wew = W_zew − t_lewa − t_prawa`; analogiczne zależności dla wysokości i głębokości wymagają uwzględnienia rzeczywistego sposobu łączenia płyt.
- **[Model/metoda]** Objętość netto powietrza zapisać jako `V_air = V_brutto − V_przetwornika − V_wzmocnień − V_bloków − V_innych_elementów`, bez podwójnego odejmowania części wspólnych.
- **[Model/metoda]** Dla przegrody `V_brutto` wyznaczać od razu dla czynnej komory albo jawnie odjąć wyłączoną przestrzeń i przegrodę; nie mieszać obu konwencji.
- **[Model/metoda]** Objętość przetwornika oznacza wypartą przestrzeń za przyjętą płaszczyzną frontu; otwarte okna kosza zawierają powietrze, więc obrys walcowy nie jest dokładnym wyporem.
- **[Model/metoda]** Otwory w ażurowym wzmocnieniu pozostają częścią `V_air`, jeśli łączą się z komorą; odjąć materiał wzmocnienia, a nie jego pełną bryłę obwiedniową.
- **[Model/metoda]** Uszczelki, uchwyty bloków, terminal, osłony wewnętrzne i zmiana grubości frontu również zmieniają bilans; przypisać każdej pozycji identyfikator i metodę wyznaczenia objętości.
- **[Model/metoda]** We wzorach używać metrów i metrów sześciennych; litry oraz milimetry mogą występować w tabelach użytkowych po jawnym przeliczeniu jednostek.
- **[Model/metoda]** Dla małych zmian wymiarów prostopadłościanu `δV ≈ HD δW + WD δH + WH δD`; to przybliżenie pierwszego rzędu, nie gwarancja tolerancji gotowej skrzyni.
- **[Rekomendacja]** Dla każdego ustawienia przygotować tabelę: wariant frontu, przetwornik, pozycja przegrody lub zestaw bloków, `V_brutto`, odjęte składniki, `V_air` i niepewności.

## Wytłumienie i efektywna podatność akustyczna

- **[Model/metoda]** W uproszczonym modelu skupionym pustej szczelnej komory podatność akustyczna wynosi `C_ab = V_air/(ρ₀ c²)`, przy zadanych gęstości powietrza `ρ₀` i prędkości dźwięku `c`.
- **[Model/metoda]** Jednostki tego zapisu: `ρ₀` w kg/m³, `c` w m/s, `C_ab` w m³/Pa; zakłada on w przybliżeniu jednorodne ciśnienie i sztywne granice komory.
- **[Model/metoda]** Wytłumienie może zmienić wymianę ciepła, straty oraz impedancję akustyczną; równoważna podatność może zależeć od częstotliwości i sposobu identyfikacji modelu.
- **[Model/metoda]** Objętość efektywna opisuje parametr modelu sprężystości powietrza; nie jest dodatkową geometryczną przestrzenią i nie zastępuje bilansu `V_air`.
- **[Rekomendacja]** Nie przyjmować stałego procentowego bonusu za włókninę; zapisać materiał, masę, rozmieszczenie, stopień upakowania i wolne przestrzenie przy przetworniku.
- **[Model/metoda]** Pory materiału porowatego mogą zawierać powietrze uczestniczące w procesie; odjęcie całej zewnętrznej objętości włókniny jako litej bryły daje inny model niż opis jej strat.
- **[Rekomendacja]** Zmianę objętości badać najpierw przy stałym opisie wytłumienia; potem rozdzielić serię zmiany wytłumienia, aby nie przypisać dwóch efektów jednemu parametrowi.
- **[Model/metoda]** Późniejsza identyfikacja podatności i strat wymaga danych urządzenia; sam rozmiar skrzyni lub wykres odpowiedzi w pokoju nie wyznacza ich jednoznacznie.

## Dane wejściowe przed wyborem wymiarów

- **[Wymaganie — brief]** Porównanie obejmuje co najmniej trzy przetworniki, w tym 12″ i 15″; nie ma narzuconego limitu gabarytów obudowy ani zatwierdzonego litrażu.
- **[Model/metoda]** Nominalna średnica w calach nie określa średnicy otworu, kołnierza, rozstawu śrub ani głębokości kosza; potrzebne są rysunki konkretnych kandydatów.
- **[Rekomendacja]** Zebrać głębokość montażową, obrys magnesu i kosza, miejsce terminali, wymagane prześwity wentylacyjne oraz zakres ruchu elementów przed i za frontem.
- **[Model/metoda]** Zakres objętości wynika z modeli elektroakustycznych oraz ograniczeń wychylenia i napięcia; jedna wartość `Qtc` nie ustala automatycznie najlepszego eksperymentu.
- **[Rekomendacja]** Największą czynną objętość wybrać po porównaniu kandydatów; możliwość jej zmniejszania nie naprawi skrzyni za małej dla potrzebnego wariantu.
- **[Model/metoda]** Fronty, wzmocnienia i przegroda muszą mieścić pełne obrysy kandydatów; ta sama skrzynia z różnymi frontami nie musi mieć identycznej objętości netto.
- **[Rekomendacja]** Zestawić warianty gabarytów, masy, dostępności serwisowej i ustawienia w pokoju; ograniczenia technologiczne pojedynczej płyty rozwiązywać także podziałem konstrukcji.

## Regulacja objętości: bloki lub przegroda

| Wariant | Status i zasada | Główne niewiadome do sprawdzenia |
|---|---|---|
| Pełne sztywne bloki | **[Model/metoda]** Wypierają własną objętość materiału | Masa, mocowanie, tolerancja objętości, brak grzechotania |
| Sztywne szczelne bloki puste | **[Model/metoda]** Wyłączają zamknięte wnętrze z czynnej komory, jeśli ich ścianki są dostatecznie sztywne | Szczelność, ugięcie ścianek, rezonanse, trwałość połączeń |
| Szczelna przegroda | **[Model/metoda]** Oddziela czynną komorę od niewykorzystanej przestrzeni | Uszczelnienie obwodu, sztywność, powtarzalne pozycjonowanie |

- **[Model/metoda]** Porowata pianka lub luźno ułożona włóknina nie jest równoważna sztywnemu szczelnemu blokowi zmniejszającemu objętość.
- **[Rekomendacja]** Bloki oznaczyć indywidualnymi identyfikatorami; mocować odwracalnie, bez zasłaniania wentylacji kosza i bez możliwości przemieszczenia przy drganiach lub transporcie.
- **[Model/metoda]** Ściśliwa obudowa pustego bloku może wnosić dodatkową podatność, a nieszczelność może dołączyć jego wnętrze do komory; sama zewnętrzna geometria wtedy nie wystarcza.
- **[Rekomendacja]** Dla przegrody rozważyć kilka indeksowanych pozycji montażowych; ciągły przesuw zwiększa wymagania dotyczące docisku, prowadzenia i szczelności.
- **[Model/metoda]** Przegroda musi przenosić zmienne ciśnienie, a nie tylko własny ciężar; nieszczelna lub podatna może utworzyć dodatkowy układ sprzężonych komór.
- **[Rekomendacja]** Zdefiniować stan przestrzeni za przegrodą: zamknięta lub odpowietrzana według projektu; w obu przypadkach czynna komora ma pozostawać szczelnie oddzielona.
- **[Model/metoda]** Zmiana warunków za przegrodą wpływa na jej obciążenie i drgania; trzeba uwzględnić to w analizie, zamiast traktować ją jako idealnie nieruchomą granicę.
- **[Rekomendacja]** Dla kolejnych konfiguracji zmieniać jeden czynnik, zapisywać kolejność montażu i zachować możliwość powrotu do tej samej geometrii.
- **[Rekomendacja]** Wybór bloków lub przegrody oprzeć na potrzebnym zakresie regulacji, przyroście masy, koszcie wykonania oraz liczbie potencjalnych nieszczelności; decyzja pozostaje otwarta.

## Wymienny front 12″/15″ i dostęp serwisowy

- **[Rekomendacja]** Rozważyć pełne wymienne fronty ze wspólnym obrysem i interfejsem mocowania; każdy front otrzymuje własny otwór i rozstaw śrub odpowiedni dla przetwornika.
- **[Model/metoda]** Wspólny interfejs ma być poza obrysem większego kołnierza i strefą uszczelnienia; nie wolno wyznaczać go wyłącznie z nominalnego rozmiaru 15″.
- **[Model/metoda]** Pierścień redukcyjny we froncie większego głośnika jest osobnym wariantem: dodaje połączenie, uszczelkę, zmienia lokalną sztywność i wymaga własnego bilansu objętości.
- **[Rekomendacja]** Sprawdzić prześwit kosza w otworze, głębokość podfrezowania, nośność strefy śrub, dostęp do nakrętek i trasę przewodów dla obu rozmiarów.
- **[Model/metoda]** Wewnętrzna krawędź otworu może ograniczyć przepływ przy oknach kosza; ewentualne fazowanie nie może osłabić podparcia śrub ani powierzchni uszczelnienia.
- **[Rekomendacja]** Dla wielokrotnego demontażu przewidzieć wymienne uszczelki i połączenia gwintowane o sprawdzonej nośności; nie zakładać trwałości wielokrotnie wkręcanych wkrętów w MDF.
- **[Model/metoda]** Docisk uszczelki zależy od jej charakterystyki, płaskości, rozstawu mocowań i pełzania podłoża; większa siła dokręcania nie gwarantuje lepszego uszczelnienia.
- **[Rekomendacja]** Front, przegrodę i bloki zaprojektować tak, aby można było wyjąć je bez uszkodzenia skrzyni; określić dostęp narzędzi i sposób podparcia ciężkiego przetwornika.
- **[Rekomendacja]** Osłona przed dziećmi ma pozostać odsunięta od ruchomych części i pewnie zamocowana; jej wpływ na akustykę pozostaje do późniejszej oceny.

## Materiały, sztywność i masa

| Materiał lub układ | Status i kryterium porównania | Czego nie zakładać |
|---|---|---|
| MDF | **[Model/metoda]** Porównać gęstość, moduł, tłumienie, płaskość i wytrzymałość mocowań | Jednej wartości parametrów dla wszystkich płyt i warunków wilgotności |
| Sklejka | **[Model/metoda]** Uwzględnić kierunki warstw, jakość klejenia i pustki | Izotropii ani jednakowej sztywności w obu kierunkach |
| Warstwy klejone | **[Model/metoda]** Uwzględnić przenoszenie ścinania przez spoinę i jej ciągłość | Że luźno skręcone płyty pracują jak jedna lita płyta |
| Układ z warstwą stratną | **[Model/metoda]** Znać charakterystykę lepkosprężystą i temperaturę | Że każda miękka przekładka automatycznie poprawia konstrukcję |

- **[Model/metoda]** Masa elementu wynosi `m = ρ V_mat`; bez gęstości konkretnego materiału można porównywać tylko scenariusze, a nie potwierdzić masę paczki.
- **[Model/metoda]** Dla cienkiej jednorodnej płyty izotropowej sztywność giętna `D_p = E t³/[12(1−ν²)]`; warunki modelu nie obejmują dowolnie grubej płyty ani sklejki bez adaptacji.
- **[Model/metoda]** We wzorach płytowych `E` oznacza moduł Younga w Pa, `ν` bezwymiarowy współczynnik Poissona, `t` grubość w m, `ρ` gęstość w kg/m³, a `a` charakterystyczną rozpiętość w m.
- **[Model/metoda]** Dla podobnych płyt częstotliwości giętne skalują się w przybliżeniu z `t/a² · √(E/ρ)`, przy stałych proporcjach i zamocowaniu; to trend, nie prognoza rezonansu skrzyni.
- **[Model/metoda]** Zwiększenie masy samo nie określa amplitudy drgań; potrzebne są sztywność, tłumienie, wymuszenie i sposób podparcia.
- **[Rekomendacja]** Wzmocnienia skracać mają podatne rozpiętości paneli i łączyć przeciwległe ściany; sprawdzić ich połączenia, wypieraną objętość i dostęp do elementów regulacyjnych.
- **[Model/metoda]** Nie wystarczy przesunąć jednego rezonansu ponad pasmo subwoofera: trzeba rozpatrzyć pozostałe mody, harmoniczne wymuszenia i skuteczność promieniowania paneli.
- **[Rekomendacja]** MDF jest roboczym wariantem zgodnym z przekazaną ofertą; wybór materiału i grubości wymaga porównania, nie wynika z samej dostępności usługi.

## FEA: informacje potrzebne do sensownego modelu

- **[Model/metoda]** Najpierw zdefiniować pytanie: ugięcie pod obciążeniem, częstotliwości własne, odpowiedź harmoniczna czy sprzężenie drgań obudowy z powietrzem.
- **[Model/metoda]** Geometria wejściowa obejmuje front, otwory, wzmocnienia, przegrodę, miejsca śrub oraz model masy i zamocowania przetwornika; uproszczenia trzeba wypisać.
- **[Model/metoda]** Potrzebne są gęstość, moduły sprężyste, współczynniki Poissona i tłumienie; dla materiałów kierunkowych także moduły ścinania i orientacja osi.
- **[Model/metoda]** Warunki brzegowe obejmują klejenia, styki śrubowe, podatność uszczelek, nóżki i podłoże; idealne utwierdzenie całych krawędzi jest osobnym założeniem.
- **[Model/metoda]** Wymuszenia obejmują ciśnienie w komorze i reakcję napędu przetwornika; nie utożsamiać ciśnienia wewnątrz z SPL przy miejscu odsłuchowym.
- **[Model/metoda]** Analiza modalna bez wymuszenia i tłumienia nie daje amplitudy drgań ani poziomu emitowanego dźwięku; odpowiedź harmoniczna wymaga dodatkowych danych.
- **[Model/metoda]** Sprawdzić zbieżność siatki, dobór elementów powłokowych lub bryłowych, bilans masy i wrażliwość na zamocowanie, moduł materiału oraz tłumienie.
- **[Rekomendacja]** Zacząć od porównania wariantów z jawnymi przedziałami wejść; nie interpretować kolorowej mapy przemieszczeń bez skali i normalizacji.
- **[Model/metoda]** Sprzężona analiza akustyczna wymaga modelu komory, strat i warunków promieniowania; strukturalne FEA nie potwierdza szczelności, THD ani braku słyszalnych podbarwień.
- **[Ustalenie — zakres]** W tym rozdziale nie uruchomiono FEA i nie podano wyników; późniejsza ocena fizyczna będzie ograniczona do dostępnych warunków w pokoju.

## diyKraft: przekazane ograniczenia wykonawcze

- **[Deklaracja oferty]** Dostępne grubości MDF: 8, 10, 12, 18, 22 i 25 mm; nie jest to potwierdzenie bieżącego stanu materiałów ani ich właściwości mechanicznych.
- **[Model/metoda]** Front nominalnie 36 mm można analizować jako `2 × 18 mm`; grubość po klejeniu, obróbce i wykończeniu zależy od płyt, spoiny i procesu.
- **[Rekomendacja]** Dla frontu warstwowego zaprojektować bazowanie warstw, ciągłość sklejenia i dostęp do mocowań; podfrezowanie może wymagać osobnego rysunku każdej warstwy.
- **[Deklaracja oferty]** Przekazywane formaty: DXF, DWG, SVG, PDF, ZIP lub szkic; akceptowany format nie oznacza zatwierdzonej geometrii ani kompletnego programu maszynowego.
- **[Deklaracja oferty]** Tolerancje szerokości i długości: ±0,1 mm; głębokości: ±0,5 mm. Są to deklaracje oferty, nie potwierdzona zdolność procesu ani tolerancja całego montażu.
- **[Model/metoda]** Przy pasowaniach, wpustach i gniazdach uszczelek trzeba zsumować odchyłki obu elementów, grubości płyt i powłok; tolerancja głębokości jest odrębnym składnikiem.
- **[Deklaracja oferty]** Wewnętrzne narożniki mają R4, czyli promień 4 mm, przy frezie o średnicy 8 mm; nie zakładać ostrego narożnika wklęsłego bez zmiany geometrii.
- **[Rekomendacja]** Zaprojektować współpracujące promienie albo jawnie oznaczone podcięcia; podcięcie nie może nieświadomie przerwać obwodu uszczelnienia lub osłabić strefy śruby.
- **[Deklaracja oferty]** Brak wykonywania otworów w bocznych krawędziach płyt; konstrukcja wymagająca takich otworów wymaga przeprojektowania lub jawnego osobnego etapu poza tą usługą.
- **[Rekomendacja]** Rozważyć mocowania dostępne od powierzchni płyt, kieszenie i warstwy frontu; nie wpisywać bocznego wiercenia jako wykonanej operacji CNC.
- **[Deklaracja oferty]** Standardowo obrabiana jest jedna strona; operacje obustronne trzeba jednoznacznie oznaczyć wraz z orientacją i wspólnymi bazami.
- **[Deklaracja oferty]** Maksymalny bok elementu: 1400 mm; maksymalna suma długości i szerokości: 2700 mm; limit masy pojedynczego elementu: 30 kg.
- **[Model/metoda]** Ograniczenia te dotyczą elementów usługi, nie narzuconego gabarytu subwoofera; ewentualny podział panelu dodaje połączenia wymagające analizy szczelności i sztywności.
- **[Deklaracja oferty]** Wykonawca nie projektuje i nie sprawdza kompletności; dostarcza surowe elementy do samodzielnego montażu, bez potwierdzenia gotowości konstrukcji do pracy.
- **[Rekomendacja]** Przygotowanie konstrukcji, zgodności części, instrukcji montażu i kontroli wejść pozostaje po stronie projektu; szczegóły i braki opisać w [dokumencie wykonawcy](../WYKONAWCA_CNC.md).

## Pakiet projektu do przyszłej obróbki

- **[Rekomendacja]** Najpierw zamknąć listę wariantów objętości i frontów, potem przygotować parametryczny model CAD; żadnego pliku w tym rozdziale nie uznawać za gotowy do produkcji.
- **[Model/metoda]** Zdefiniować osie, początek układu, jednostki, numer rewizji, stronę widoczną, kierunek warstw i powierzchnie bazowe każdej części.
- **[Rekomendacja]** Rysunek części ma zawierać identyfikator, ilość, materiał, grubość nominalną, kontur, otwory, kieszenie, głębokości i wymagania stron A/B.
- **[Model/metoda]** Oddzielić kontury przelotowe od gniazd i operacji o zadanej głębokości; zamknięte kontury, skala oraz brak zdublowanych linii wymagają sprawdzenia po eksporcie.
- **[Rekomendacja]** Dołączyć rysunek złożeniowy, przekroje połączeń, bilans objętości oraz zestawienie elementów, uszczelek, łączników i części nieobjętych ofertą CNC.
- **[Model/metoda]** Model CAD opisuje geometrię; CAM dodatkowo określa narzędzia, mocowanie i kolejność obróbki. Sam DXF nie potwierdza wykonalności ani bezpieczeństwa procesu.
- **[Rekomendacja]** Przed przyszłym zleceniem przeprowadzić przegląd kolizji, dostępu do śrub, promieni R4, tolerancji głębokości, oznaczeń obustronnych i limitów pojedynczych elementów.
- **[Rekomendacja]** Instrukcja montażu ma uwzględniać kolejność klejenia, bazowanie, docisk, wymienność modułów oraz ochronę powierzchni uszczelniających; wartości procesu wymagają danych materiałów.
- **[Model/metoda]** Masa i położenie środka ciężkości służą ocenie przenoszenia i przewrócenia; sama duża masa nie potwierdza stabilności przy nacisku na osłonę lub obudowę.
- **[Ustalenie — zakres]** Nie powstały tu pliki CAD/CAM, rozkrój, lista zakupowa ani zamówienie; gotowość do CNC pozostaje przyszłą bramką projektu.

## Ścieżka dalszych prac i otwarte decyzje

- **[Rekomendacja]** Najbliższy krok: zebrać rysunki i zweryfikowane wejścia kandydatów 12″/15″, aby ustalić wspólny interfejs frontów oraz potrzebny zakres objętości.
- **[Rekomendacja]** Obliczenia prowadzić skryptami Pythona, zapisując jednostki SI, wersje bibliotek, wejścia, ich hashe i ograniczenia; w tej notatce podano wyłącznie metody.
- **[Rekomendacja]** Przyszłe modele powiązać z planowanym [rozdziałem elektroakustycznym](02_modelowanie_elektroakustyczne.md) i [raportem obliczeń](../raporty/002_obliczenia_wstepne.md); linki nie dowodzą istnienia wyników.
- **[Ustalenie — otwarte]** Nie wybrano przetwornika, materiału, grubości, litrażu, sposobu regulacji ani progów odbiorowych; wymagania referencyjne i progi wymagają osobnego zatwierdzenia.
- **[Model/metoda]** Późniejsze badania w pokoju mogą ujawnić nieszczelności i drgania, lecz odpowiedź w sweet spocie obejmuje też pomieszczenie; nie zastępuje kontrolowanego pomiaru własności urządzenia.
- **[Ustalenie — zakres]** Rozdział dokumentuje badania przed budową; nie potwierdza szczelności, wytrzymałości, promieniowania paneli ani osiągów nieistniejącego prototypu.
