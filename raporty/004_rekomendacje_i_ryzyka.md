# Raport 004 — rekomendacje i otwarte ryzyka

Aktualizacja U-010: części dotyczące rynku i doboru handlowego są odłożone.
Bieżący kierunek naukowy: [plan](../PLAN_BADAN_NAUKOWYCH.md) i
[raport 007](007_fizyka_nieliniowosci_i_DSP.md).

Data 2026-10-23. Status: rekomendacje do dalszych badań, nie decyzja zakupowa.

## Zalecana ścieżka

Kontynuować porównanie 12″/15″ z zewnętrzną elektroniką i regulacją netto.
Model wskazuje wyraźną korzyść większegoSd·Xmax przy 20 Hz; opłacalność oraz
niskieTHD pozostają do wykazania. Przed projektem wykonawczym potrzebne są
źródłowe ceny, opinie finalistów, definicjeXmax i pełniejsze referencje.

Do dalszej siatki objętości: RSS315HF-4 około 45–60 l, HFA8 około 45–80 l,
RSS390HF-4 około 80–120 l; SB porównać około 30–60 l i szerszą korekcję.
To zakresy **eksperymentów obliczeniowych**, bez zatwierdzonego litrażu.
Rozszerzyć je, jeśli analiza uzgodnionego celu pokaże korzyść.

Mechanika: maksymalna przestrzeń robocza z mocowanymi sztywnymi modułami
wypornościowymi jest sensowną koncepcją startową. Alternatywa to uszczelniana
przegroda. Ocenić koszt, dostęp, ugięcia i ryzyko nieszczelności przed wyborem.
WykonawcaMDF i jego ograniczenia są opisane w [karcie](../WYKONAWCA_CNC.md).

## Trzy założenia mogące zmienić wybór

1. **Docelowy poziom 20–40 Hz.** Jeśli oczekiwana jest duża wydajność także 20 Hz,
   pojedynczy 12″ może okazać się niewystarczający mimoEQ. Wtedy rośnie znaczenie
   większegoSd·Xmax lub dwóch źródeł.
2. **Porównywalność danych liniowości.** KatalogowyXmax może opisywać geometrię,
   a użyteczny ruch przy wymaganymTHD być mniejszy. To może zmienić ranking
   nawet przy poprawnej arytmetyceSd·Xmax.
3. **Dostępność i koszt całego napędu.** Wariant 8Ω potrzebuje innego napięcia
   do tego samego ruchu; dostępne moduły, zasilacz i chłodzenie mogą zmienić
   całkowity koszt względem tańszego samego głośnika.

## Najmocniejszy argument przeciw kierunkowi 15″

Większa skrzynia, masa i cena mogą nie być uzasadnione, jeżeli uzgodniony
poziom oraz rzeczywisty pokój pozwolą osiągnąć cel mniejszym przetwornikiem.
DużySd·Xmax nie rozstrzygaTHD, hałasu mechanicznego i jakości integracji.
Dlatego 15″ pozostaje ważnym wariantem, bez przedwczesnego zwycięzcy.

Najtańsza wiarygodna alternatywa: obecnie **nieustalona**, bo brakuje
porównywalnego kosztorysu i zatwierdzonych progów. Robocza alternatywa
badawcza to 12″ z łagodniejszym celem dolnego pasma; jej wystarczalność trzeba
wykazać. Nie zastępujemy braku cen zgadywaną kwotą.

## Najszybsze rozstrzygające działania

Przed budową: rozpoznać poziomy pasmowe referencji, sprawdzić karty i aktualne
oferty, następnie wykonać wspólną siatkę Vb/EQ/napęd. To ograniczy niepewność
wyboru bez zakupów aparatury. Po budowie: porównać te same sygnały, pozycję
i napięcie dla dwóch objętości, potem poziomy i kompresję. Tor pomiarowy
dobieramy dopiero wtedy zgodnie z decyzją użytkownika.

## Rejestr ryzyk

| Ryzyko | Skutek | Odpowiedź projektowa | Co pozostaje otwarte |
|---|---|---|---|
| NiespójneT/S | Błędny litraż i prognoza | Kontrola tożsamości, źródła, baza pierwotna | PDFBL dlaHF4, tolerancje sztuk |
| Za dużyEQ | Clipping/ruch/termika | HP, budżet poziomów i limity napięcia | Rzeczywiste możliwościDSP/napędu |
| Pe jako rzekomy limit termiczny | Fałszywy headroom ciągły | Traktować jako wskaźnik; później kompresja/temperatura | Model cieplny i protokół producenta |
| Rozrzut i definicjeXmax | Zmieniona liniowość | Rezerwa i jawna analiza czułości | NiezależneBL(x)/THD |
| Nieszczelne moduły/front | Zmieniona dobroć i odgłosy | Mocowanie, uszczelki, dostęp serwisowy | Sprawdzenie gotowej skrzyni |
| Drgania dużych paneli | Podbarwienie, straty | Wzmocnienia przeciwległych ścian i krótki rozstaw | Skuteczność po wykonaniu |
| Niepełne daneCNC | Niepasujące/niekompletne elementy | Checklista, rewizje, tolerancjeZ iR4 | Wycena i kontrola dostawy |
| Pokój maskuje odpowiedź źródła | Nieporównywalny maxSPL | Jasne oznaczeniein-room i ograniczeń metody | Brak pomiarów kontrolowanych poza pokojem |
| Opinie historyczne lub skopiowane | Błędna reputacja modelu | Data, rewizja, pierwsza ręka, korekty i niezależność | Aktualne relacje finalistów |
| Błędne wyjścia/gainDSP | Szum, zbyt mało torów, clipping | Schemat 8 torów i audyt konkretnej wersji | Pełna instrukcja i poziomy |
| Obudowa elektroniki/masa | Problemy uruchomienia i użytkowania | Zewnętrzny zamknięty napęd, ochrona membrany, stabilność | Projekt elektryczny i odbiór montażu |
| Przedwczesna komercjalizacja | Niewykazana powtarzalność | Osobny pilotaż egzemplarzy i pokojów | Późniejszy plan zgodności wyrobu |

## Granica obecnego rezultatu

Powstał plan i pierwsza obliczeniowa baza badawcza. Pełne przygotowanie
do budowy wymaga przejściaR1–R5. Nie ma jeszcze podstaw do zamówienia
konkretnego głośnika ani formatek na podstawie obecnego porównania.
