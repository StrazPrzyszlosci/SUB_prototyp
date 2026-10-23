# Od zamysłu do sprawdzalnych wymagań

Status: wiedza modelowa i metoda projektowa. Wartości konkretnego modelu
muszą mieć źródło w [rejestrze](ZRODLA.md); wyniki własne w raportach.

## Co daje subwoofer w systemie aktywnym

Subwoofer przenosi najniższe pasmo i może odciążyć woofery monitorów, jeśli
te otrzymają odpowiedni filtr górnoprzepustowy. Samo dodanie subwoofera bez
odciążenia monitorów nie zapewnia im automatycznie większego headroomu.
Liczba obudów, liczba kanałów i liczba niezależnych filtrów to różne rzeczy.
Docelowy układ 2 × 3-drożny monitor + 2 subwoofery wymaga ośmiu niezależnych
torów wyjściowych i wzmacniających, choć wzmacniacze mogą dzielić obudowę.

## Parametry, które odpowiadają na różne pytania

| Parametr | Co opisuje | Czego sam nie dowodzi |
|---|---|---|
| Fs | Rezonans małosygnałowy przetwornika w określonych warunkach | Zejścia w obudowie ani maksymalnego SPL |
| Qes/Qms/Qts | Tłumienie w modelu małosygnałowym | Zniekształceń przy dużym wychyleniu |
| Vas | Objętość równoważna podatności zawieszenia | Objętości fizycznej kosza ani wymaganego litrażu |
| Sd | Efektywna powierzchnia promieniowania | Powierzchni koła o średnicy z nazwy 12″/15″ |
| Xmax | Deklarowany zakres ruchu według określonej definicji | Braku słyszalnych zniekształceń w całym zakresie |
| Xmech | Granica mechaniczna według producenta | Liniowej pracy ani bezpiecznej eksploatacji przy tej wartości |
| Pe | Obciążalność dla danego protokołu | Dostępnej mocy muzyki przy 20 Hz w każdej skrzyni |
| Re/Le/Z(f) | Obciążenie elektryczne i część dynamiki napędu | Stałej impedancji równej wartości nominalnej |
| BL | Sprzężenie siły/prądu i SEM/prędkości | Pełnej liniowości BL(x), temperatury i nasycenia |
| F3 | Punkt −3 dB względem określonego poziomu odniesienia | Użytecznego poziomu w tym paśmie ani jakości basu |

Rozróżniać 2,83 V/1 m i 1 W/1 m. Dla idealnych rezystancji 4 Ω napięcie
2,83 V odpowiada około 2 W, dla 8 Ω około 1 W; rzeczywisty Z(f) jest zespolony.
Przy porównywaniu skuteczności trzeba znać protokół i pasmo.

## Dlaczego 20 Hz jest wymagające

W przybliżeniu małego tłoka w ustalonej geometrii p ∝ f²·Sd·x. Dla takiego
samego ciśnienia obniżenie częstotliwości o oktawę wymaga czterokrotnie
większego wychylenia, dopóki model pozostaje właściwy. Podwojenie Sd·Xmax
daje idealnie 6,02 dB większą granicę ciśnienia ograniczoną ruchem; nie oznacza
to podobnego wzrostu przy ograniczeniu napięciem, termiką lub THD.

Większa skrzynia zmniejsza dodatkową sztywność powietrza i może zmniejszyć
wymagane napięcie przy danym ruchu. Nie zwiększa samego Sd·Xmax. Pozwala
łatwiej osiągnąć granicę ruchu, czasami przy mniejszej mocy, więc potrzebuje
dobranej ochrony. Przetwornik z bardzo niskim Fs nie musi mieć najlepszej
zdolności do głośnego odtwarzania muzyki w całym wymaganym paśmie.

## Dlaczego zaczynamy od sealed

Obudowa zamknięta jest założeniem eksperymentu z briefu: upraszcza porównanie
objętości, szczelności i filtrów, nie wprowadza strojenia portu oraz jego
hałasu. Jej niskoczęstotliwościowy spadek w idealnym modelu 2. rzędu wynosi
asymptotycznie 12 dB/oktawę. Korekcja tego spadku wymaga headroomu i ruchu.

Bass-reflex, membrana bierna i układy wieloprzetwornikowe są alternatywami,
gdy wyjdzie niedobór wydajności. Nie są obecnym wariantem wykonawczym.
Port może zwiększyć wydajność w okolicy strojenia, ale wymaga objętości,
przekroju, oceny turbulencji i ochrony poniżej strojenia. Zamknięta skrzynia
nie jest z definicji lepsza we wszystkich miarach.

## Jak rozumieć „szybki” i „kontrolowany” bas

Oceniamy łącznie pasmo, fazę, opóźnienie grupowe, rezonanse obudowy,
zniekształcenia i odpowiedź pomieszczenia. Porównanie impulsów o różnych
pasmach może być mylące. Niskie Qtc nie gwarantuje dobrego zaniku w pokoju,
a sam ciężar membrany nie jest wystarczającym wskaźnikiem jakości transjentów.

„Czarne tło” wymaga pomiaru szumu i brumu toru, sensownego gain staging
i oceny warunków odsłuchu. „Brak zadyszki” trzeba odnieść do kompresji,
clippingu, limiterów i THD. „Mastering” opisuje cel systemu, nie wynik jednego
wykresu małosygnałowego subwoofera.

## Ścieżka dowodowa

Potrzeba użytkowa → wymaganie z warunkami → dane kandydata → model → projekt
→ wykonanie → pomiar → porównanie prognozy z wynikiem → korekta projektu.
Każde przejście ma jawne wejścia. Opinie konstruktorów pomagają znaleźć
typowe pułapki i ważne pytania, ale nie zastępują brakujących danych ilościowych.
