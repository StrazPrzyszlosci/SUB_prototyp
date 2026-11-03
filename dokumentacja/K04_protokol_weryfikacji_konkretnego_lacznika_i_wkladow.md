# K04 — karta rzeczywistego testu łącznika i przejścia modułów

**Stan: przygotowano protokół, NIE WYKONANO pomiarów ani prób, nie wybrano części do zamówienia. Celem jest rozstrzygnąć pierwszy prawdziwy węzeł mocowania RSS390HF-4.**

## Test próbny — nie pomijać części zespołu

Dla tych samych śrub na PCD Ø368 mm porównać:
- **N1: śruba przelotowa, nakrętka zabezpieczona przed obrotem + element rozkładający siły**. Szczegółowy gabaryt nominalnej M5 i M6 sprawdzono w K04, ale żadne z nich nie jest jeszcze doborem produkcyjnym. Wzmocnienie drewniane K02 (20 mm) i płytka metalowa mogą kolidować z koszem i drogami wkładów.
- **S1: odpowiedni wkręt do MDF wzmocnionego lokalnym klockiem**. Wymaga prób wyrywania blisko krawędzi otworu, rozwarstwiania i demontażu.
- **R: lokalny metalowy mostek / pełniejsza rama** tylko jeśli N1/S1 nie spełnią wymaganych parametrów. Również musi mieć cały tor siły i własne badania.
- Dodatkowo **N2: nakrętka lub płytka w kontrolowanym wgłębieniu w klocku** — *wyłącznie opcja do przebadania*, bo wybranie kieszeni usuwa drewno i może obniżyć nośność. Nie wycinać kieszeni bez wymiarów rzeczywistego osprzętu i zwalidowanej analizy.

## Dokumentacja rzeczywistego osprzętu — puste pola, niczego nie zakładać

| Parametr konieczny do zamknięcia konstrukcji | Wartość |
|---|---|
| Dokładna rewizja głośnika / identyfikator zdjęć kosza z podziałką | NIE ZMIERZONO |
| R_basket(Y,θ) dla 8 punktów, Y=44–74 mm | NIE ZMIERZONO |
| Fabryczna faza żeber względem osi śrub i gabaryt zacisków | NIE ZMIERZONO |
| Średnica faktycznego otworu w MDF i ograniczenia jego tolerancji | NIE USTALONO |
| Pełne wymiary realnej nakrętki/wkładki/płytki wraz z tolerancjami | NIE USTALONO |
| Typ i sposób mechanicznego zabezpieczenia nakrętki przed obrotem i wysunięciem | NIE USTALONO |
| Dostęp do główki śruby od przodu po finalnym montażu osłony | NIE ZWERYFIKOWANO |
| Dostęp do ewentualnej nakrętki podczas wymiany przetwornika | NIE ZWERYFIKOWANO |
| Obrys narzędzia i dłoni przy każdej z 8 osi | NIE ZWERYFIKOWANO |
| Sprężystość MDF44, spoiny, siły wyrywania, lokalny nacisk | NIE ZMIERZONO |
| Wilgotność, temperatura i partia płyt / metoda klejenia | NIE OKREŚLONO |
| Pełny gabaryt urządzenia z osłoną, terminalem i przewodem ≤500 mm | NIE ZWERYFIKOWANO |

## Test 1 — geometria i serwis

Zanim zbierze się siły na próbkach, przyrząd pomocniczy musi odwzorować prawdziwe odlewane żebra kosza i terminale. Od strony frontowej sprawdzić ręczne założenie, demontaż i cofnięcie każdej śruby; **gdy tylna nakrętka obraca się bez możliwości unieruchomienia, wariant należy odrzucić lub przeprojektować**.

Potwierdzić rzeczywisty metalowy nośnik przy promieniach R178,0–202 mm z jego podparciem i wymaganym obszarem pracy narzędzia. 0,1 mm nominalnej odległości do wycięcia w modelu K04 **nie jest tolerancją montażową**. Jeżeli prawdziwy kosz, pierścień albo przewód przecina jego obrys, przerywamy wybór N1, zamiast dopasowywać kosz siłą.

## Test 2 — regulacja objętości

Po docelowym montażu wszystkich 8 łączników w osadzonej wersji testowej:
1. Wyjąć przetwornik, pozostawiając złącza w stanie wymaganym przy normalnym serwisie.
2. Wprowadzić rzeczywiste **20 wkładów z uchwytami, zamkami i narzędziami** zgodnie z sekwencją P30E/K02 dla stanu 100 l; wykonać pełny demontaż.
3. Powtórzyć stan 120 l (12 sztuk) i 150 l (1 sztuka), nie uszkadzając przy tym mocowań i uszczelek.
4. Rejestrować minimalne odległości do żeber, nakrętek, terminali, przewodów, wręg i tylnej maty; po kolizji przerwać próbę i poprawić geometrię.
5. W obu docelowych orientacjach potwierdzić możliwość zatrzymania i zabezpieczenia wszystkich wkładów.

Nie wolno oznaczać tych weryfikacji jako wykonanych na podstawie sukcesu plannerów translacyjnych K02/K04.

## Test 3 — fizyczna trwałość węzła

Z tej samej partii MDF i kleju wykonać **co najmniej trzy pilotażowe próbki dla każdej konfiguracji** (minimalna liczba porównawcza, nie normowa ocena niezawodności). Dla N1 i S1 oddzielnie dokumentować:
- siła/przemieszczenie wyrywania, ścinania, odrywania spoiny i uszkodzenia cienkiego pasa MDF;
- utrata docisku (zdefiniowany czas, temperatura i wilgotność), zmiany osadzenia przy ponownym montażu;
- obrót, wypadanie i zakleszczenie wkładki/nakrętki;
- zdjęcia uszkodzeń oraz siły graniczne i ich rozrzut.

**Nie wyliczać „bezpiecznego momentu” dokręcenia z hipotetycznych sprężyn B12.** Limit konstrukcyjny trzeba wyznaczyć dla rzeczywistych elementów, z uwzględnieniem dokumentacji producenta łącznika.

## Warunki zamknięcia bramki

Dopuścić konkretną konfigurację dopiero, gdy jednocześnie są potwierdzone: geometria i pełen tor siły na każdej z ośmiu osi, montaż i serwis, nośność próbek, dostęp do 20 wkładów w obydwu orientacjach, objętość 100/120/150 l po policzeniu rzeczywistych wyporności i całościowy obrys ≤500 mm. W razie porażki wrócić do alternatywnego nośnika lub kolejności wkładów, a nie zaliczać jej na podstawie kolejnych hipotetycznych modeli.

Powiązania: [K04](../raporty/K04_pelne_gabaryty_nakretki_podkladki_i_montaz_20_modulow.md) · [K02 – wcześniejsze próby tras](K02_protokol_pomiarow_kosza_i_probek_zlacz.md) · [K03 – wymagany pas MDF](../raporty/K03_wezel_mocowania_waski_pas_MDF_i_sciezka_sily.md).

**CNC HOLD — brak realnych pomiarów kosza i próbek.**
