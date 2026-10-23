# 07. Niepewność i organizacja badań

Stan: 2026-10-23. Podstawa: brief v0.6, `DECYZJE_I_PYTANIA.md` i [plan B+R](../PLAN_B_R.md).
Cel bieżącego etapu: odtwarzalna podstawa decyzji o budowie prototypu, z zachowaniem braków danych i ograniczeń modeli.
Dokument określa metodę; nie zawiera nowych ofert, cen, modeli urządzeń ani wyników pomiaru i nie wymaga teraz internetu.

## 1. Wspólny rejestr zakresu

| ID | Ustalenie z 2026-10-23 | Konsekwencja organizacyjna |
| --- | --- | --- |
| U-001 | Użytkownik ma multimetr, oscyloskop i lutownicę | To inwentarz, bez domniemania parametrów i wyposażenia sondowego. |
| U-002 | Dobór i zakupy toru pomiarowego po budowie | Nie uzależniać obecnej pracy od mikrofonu, interfejsu ani pomiaru free-air. |
| U-003 | Pomiary tylko w pokoju odsłuchowym | Osiągi in-room; brak automatycznego rozdzielenia urządzenia i pokoju. |
| U-004 | Teraz research do budowy prototypu | Budowa i pomiary są przyszłymi etapami, a nie wykonanymi elementami obecnego zadania. |
| U-005 | Uwzględniać opinie użytkowników i osób znających przetworniki | Oddzielny rejestr doświadczeń; opinia nie staje się pomiarem przez powtarzanie. |

Zmiana decyzji wymaga datowanego wpisu, źródła oraz wskazania dokumentów i obliczeń wymagających aktualizacji.
Nie renumerować identyfikatorów lokalnie; w razie sprzeczności zachować obie wersje i wskazać obowiązującą decyzję użytkownika.

## 2. Rodzaj twierdzenia i jakość dowodu

| Rodzaj | Co trzeba zachować | Czego sam nie dowodzi |
| --- | --- | --- |
| Wymaganie / decyzja | Autor, data, zakres i status zatwierdzenia | Wykonalności technicznej |
| Dane producenta | Dokładny dokument, rewizja, warunki, jednostki | Parametrów każdego egzemplarza |
| Pomiar niezależny | Autor, metoda, egzemplarz, warunki i dostępne dane | Identyczności warunków z naszym pokojem |
| Pomiar własny | Surowe pliki, konfiguracja, kalibracja i ograniczenia | Niezależnego potwierdzenia ani generalizacji na serię |
| Symulacja / obliczenie | Wejścia, kod, model, jednostki i granice stosowalności | THD, termiki i zachowania poza modelem |
| Założenie / rekomendacja | Uzasadnienie, alternatywa i warunek obalenia | Statusu potwierdzonego faktu |
| Opinia / relacja użytkownika | Pierwsza ręka, model/rewizja, warunki i pochodzenie | Skalibrowanego wyniku ani reprezentatywnego rozkładu awarii |

Ocena jakości zależy od tezy: karta producenta może być właściwa dla wymiarów, a nie wystarczać do oceny kompresji w pokoju.
Oddzielić wiarygodność źródła, kompletność metody, zgodność warunków i niezależność; nie zastępować ich jedną arbitralną oceną punktową.
Kilka publikacji kopiujących jedną tabelę stanowi jedną linię pochodzenia, nie kilka niezależnych potwierdzeń.
Sprzeczności źródeł zachować z możliwą przyczyną: rewizja, metoda, temperatura, orientacja, błąd jednostek lub nieznana różnica.

## 3. T/S nominalne i nieznane tolerancje

Katalogowe T/S są wejściem nominalnym do modelu; bez danych o rozrzucie nie są rozkładem parametrów przyszłego egzemplarza.
Przy każdym parametrze zapisać wartość, jednostkę, dokument, warunki oraz tolerancję podaną przez źródło albo `nieznana`.
Nie zastępować braku tolerancji zerem; nie traktować różnicy dwóch kart katalogowych jako zmierzonej tolerancji produkcji.
Weryfikować wersję produktu i spójność zestawu; nie składać najkorzystniejszych liczb z różnych rewizji w jeden przetwornik.
Rezystancja Re zależy od stanu cieplnego i nie jest impedancją nominalną; definicje Xmax i mocy wymagają osobnego opisu.
Oddzielić niepewność wejścia, uproszczenie modelu i nieznane procesy nieliniowe; większa liczba przebiegów nie usuwa tych braków.
Przed budową pracować na katalogu i jawnych scenariuszach; pomiar T/S egzemplarza nie jest bramką rozpoczęcia projektu.

## 4. Czułość: zmieniać współzależne parametry spójnie

W małosygnałowym modelu skupionym obowiązują powiązania, m.in. `Fs = 1/(2π sqrt(Mms Cms))` oraz `1/Qts = 1/Qes + 1/Qms`.
Dalej `Qes = 2πFs Mms Re/(BL)²`, `Qms = 2πFs Mms/Rms` i `Vas = ρc²Sd²Cms`; Rms oznacza opór mechaniczny, a wejścia liczymy w SI.
To tożsamości modelu, nie dowód znajomości strat i nieliniowości rzeczywistego przetwornika.
Jeśli dane pozwalają, wybrać jawny zestaw parametrów pierwotnych, np. Mms, Cms, Rms, BL, Re i Sd, a zależne wyliczać ponownie.
Jeśli danych jest mniej, udokumentować alternatywną parametryzację oraz wielkości utrzymywane stałe; nie dopisywać braków bez źródła.
Zmiana Fs, Vas i Qts o niezależne procenty może naruszać przyjęte więzy lub ukrywać założenia o mechanice i napędzie.
Najpierw zmieniać jeden parametr pierwotny, następnie kilka jawnych scenariuszy spójnych; zachować wyniki również niekorzystne.
Czułość lokalną można przybliżyć różnicą `dY/dθ ≈ [Y(θ+h) − Y(θ−h)]/(2h)` po przeliczeniu parametrów zależnych.
Zapisać krok h, jednostki, punkt pracy i sprawdzenie stabilności wyniku przy zmianie kroku; pochodna jest zależna od parametryzacji.
Oceniać wpływ na odpowiedź, potrzebne EQ, napięcie, wychylenie i wybór objętości; nie utożsamiać czułości z prawdopodobieństwem awarii.
Zakres scenariusza bez danych o tolerancji jest założeniem projektowym, a nie przedziałem ufności lub gwarancją skrajnych egzemplarzy.

## 5. Monte Carlo i analiza bez rozkładów

Monte Carlo wymaga uzasadnienia rozkładów wejść, ich zależności oraz interpretacji losowania; samo wybranie ziarna tego nie zapewnia.
Bez tych danych nie podawać prawdopodobieństwa spełnienia wymagania, percentyli produkcji ani statystycznego zapasu bezpieczeństwa.
Losowanie jednostajne z arbitralnego zakresu bada ten wybrany rozkład, a nie populację przetworników; ewentualny eksperyment tak oznaczyć.
Preferować jawną siatkę i scenariusze w parametrach pierwotnych, z opisem wyboru zakresów i ograniczeniem liczby wariantów.
Scenariusze narożne nie gwarantują uchwycenia ekstremum nieliniowej funkcji; nie nazywać ich ścisłą obwiednią bez uzasadnienia.
Wynik nominalny i zakres zbadanych scenariuszy pokazywać oddzielnie; brak prób poza siatką pozostaje otwartą niewiadomą.
Kiedy różnice między kandydatami są mniejsze od nierozstrzygniętej niepewności, raportować nierozstrzygnięcie zamiast wymuszać ranking.

## 6. Koszt i Pareto bez arbitralnych wag

Ten rozdział nie wpisuje cen; przyszłe dane kosztowe wymagają źródła, daty sprawdzenia, waluty, VAT, dostawy i statusu dostępności.
Cena katalogowa nie potwierdza bieżącej oferty ani stanu magazynowego; stare dane zachować jako historyczne z datą, nie jako aktualną wycenę.
Porównywać kompletne konfiguracje: przetwornik, skrzynia i wykonanie, zewnętrzny napęd, DSP, połączenia oraz dostawa.
Tor pomiarowy pozostaje odłożoną pozycją poza bieżącym doborem zgodnie z U-002; nie dopisywać fikcyjnej kwoty dla kompletności sumy.
Przy brakujących składnikach oznaczyć koszt jako niepełny; nie porównywać samego głośnika z pełnym systemem konkurencyjnego wariantu.
Najpierw oddzielić jawne ograniczenia i zatwierdzone wymagania od miękkich preferencji; brak progu nie oznacza jego spełnienia.
Wariant dominuje drugi, gdy na wspólnie określonych kryteriach jest nie gorszy we wszystkich i lepszy w co najmniej jednym.
Ustalić kierunek każdego kryterium oraz identyczne warunki: np. koszt minimalizujemy, użyteczny poziom maksymalizujemy w danym paśmie.
Zbiór Pareto obejmuje warianty niezdominowane w zbadanym zbiorze; nie dowodzi globalnego optimum ani poprawności wejściowych prognoz.
Nie dodawać arbitralnych wag, skali „jakość 1–10” ani pojedynczego zwycięskiego wyniku ukrywającego kompromis 20 Hz kontra headroom.
Przy niepewnych kosztach i osiągach oznaczyć dominację jako warunkową lub nierozstrzygniętą; porównać stabilność wyboru w scenariuszach.
Wybór z Pareto wymaga ujawnionej preferencji użytkownika; „najtańszy spełniający” wolno wskazać dopiero po sprawdzeniu wymagań i kosztu.

## 7. Opinie jako źródło pytań badawczych

Dla U-005 zapisać autora/pochodzenie, datę, dokładny model i rewizję, liczbę egzemplarzy oraz informację, czy autor rzeczywiście ich używał.
Zebrać kontekst: obudowa, napęd, filtry, poziom, pokój, czas użytkowania i objaw; brak kontekstu jawnie obniża zakres wniosku.
Oddzielać opisy brzmienia, obserwacje mechaniczne, awarie i wyniki pomiarowe; twierdzenie o pomiarze wymaga dostępu do metody lub danych.
Szukać relacji przeciwnych i możliwych wspólnych źródeł; powielony wpis nie staje się niezależnym potwierdzeniem.
Z relacji wyprowadzić falsyfikowalne pytanie i metodę późniejszej kontroli, np. czy objaw powraca przy tej samej konfiguracji.
Brak opinii oznacza ograniczenie wiedzy, nie automatyczne odrzucenie kandydata; liczba wpisów nie wyznacza częstości awarii bez mianownika.

## 8. Odtwarzalność plików, wersji i raportów

Zgodnie z organizacją projektu wejścia zachować w `dane/`, kod w `skrypty/`, rezultaty w `wyniki/`, interpretację w `raporty/`.
W projekcie istnieją już takie artefakty. Pełny przebieg archiwizuje poprzedni stan i zapisuje manifest po wszystkich obliczeniach; data i konfiguracja wiążą wyniki z wejściami.
Manifest powinien wiązać dokładne pliki wejściowe, hash briefu i rejestru decyzji, wersję kodu, parametry uruchomienia i pliki wynikowe.
Stosować SHA-256 na dokładnych bajtach plików; przechować także oryginały, ponieważ sam hash nie pozwala odtworzyć treści.
Hash potwierdza tożsamość danych względem manifestu, a nie ich prawdziwość, poprawność modelu lub niezależność dowodu.
Zapisać wersję Pythona, bibliotek, modelu, schematu danych, generatora i ewentualne ziarno losowania; jawnie podać jednostki SI.
Nie nadpisywać wyników poprzedniego przebiegu; poprawkę wiązać z poprzednikiem i opisać jej wpływ na wnioski.
Raport oddziela wejścia, metodę, wyniki, ograniczenia, interpretację i decyzję; tabelę progów przechowywać niezależnie od danych wynikowych.
Puste wartości oznaczają brak z kodem przyczyny, nie zero; wyniki negatywne i odrzucone warianty również muszą mieć ślad.
Ręczną poprawkę tabeli traktować jak nową transformację; zachować formułę, źródło i autora zamiast ukrywać zmianę w wykresie.
Kontrola analitycznej granicy lub jednostek wspiera poprawność implementacji; ponowne uruchomienie tego samego kodu sprawdza odtwarzalność.
Żadna z tych kontroli nie zastępuje przyszłej walidacji gotowego prototypu w rzeczywistych warunkach pokoju.

## 9. Reguły stop i decyzja o gotowości do budowy

Przed pakietem pracy określić pytanie, dokładne wejścia, zależności, rezultat, limit poszukiwań oraz warunek rozstrzygnięcia i zakończenia.
Brak kluczowego wejścia zatrzymuje odpowiadające mu twierdzenie; równolegle można badać kandydatów i pytania bez tej zależności.
Brak rozkładu zatrzymuje interpretację probabilistyczną; brak ceny ocenę kosztu; brak progów odbiorowych deklarację spełnienia.
Wykryta niespójność T/S zatrzymuje wykorzystanie danego zestawu do rekomendacji do czasu wyjaśnienia lub jawnego scenariusza warunkowego.
Nie powtarzać analizy bez zmienionego wejścia, nowej metody lub pytania; powtórzenie kontrolne musi mieć określony cel.
Kończyć pakiet po otrzymaniu danych wystarczających do decyzji albo po opisaniu braku, który wyznacza konkretny następny krok.
Gotowość do budowy wymaga spójnego projektu, bilansu objętości, dopasowania napędu, odwracalnych decyzji i jawnych ryzyk do późniejszej walidacji.
Nie utożsamiać tej gotowości z dowodem maksymalnego SPL, niskiego THD, zgodnością normatywną lub zgodą na zakup i wykonanie.
Decyzję zapisać z uzasadnieniem, alternatywą, najsilniejszym kontrargumentem i warunkiem ponownego otwarcia; brak danych pozostawić widoczny.
Raport zamknąć jednym następnym działaniem, które zmniejsza najważniejszą niepewność; obecnie działanie musi mieścić się w researchu do budowy.
