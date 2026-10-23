# Narzędzia obliczeń, symulacji i rola MCP

Stan 2026-10-23. Użytkownik odłożył zajmowanie się narzędziamiCAD.
Nie instalujemy ani nie konfigurujemyCAD lub jegoMCP. Plan dokumentacji
mechanicznej pozostaje w projekcie, lecz wybór narzędzia jest późniejszą decyzją.

## Co jest potrzebne teraz

| Zadanie badawcze | Obecne narzędzie | Potrzeba dodatkowegoMCP |
|---|---|---|
| T/S i kontrola spójności | Python, NumPy, SymPy | Brak: równania i wejścia są w repo |
| Sealed, impedancja, Xpeak, napięcie/prąd | Python, NumPy/SciPy | Brak: model wykonuje obliczenia bez zewnętrznej aplikacji |
| EQ i czułość parametrów | SciPy i jawne skrypty | Brak: potrzebna kontrola modelu i warunków |
| Wykresy i eksport tabel | Matplotlib, CSV/JSON | Brak |
| Gromadzenie źródeł | browser-harness; dopuszczonyFirecrawl | To dostęp do informacji, nie solver fizyczny |
| Odczyt wykresów z forum/PDF | Przeglądarka, lokalne obrazy i skrypty przeliczeń | Brak: potrzebna kontrola osi, sygnału i topologii |

MCP to protokół dostępu do funkcji programu lub danych. Nie poprawia
automatycznie jakości fizyki, danych materiałowych ani warunków brzegowych.
Dla obecnej analizy elektroakustycznej dodatkowy serwer nie jest konieczny.

## Kiedy rozważyć integrację solvera

Gdy pojawi się konkretne pytanie o drgania paneli, sprzężenie konstrukcji
z powietrzem lub promieniowanie wymagające metodyMES/BEM, przydatna integracja
powinna umożliwiać: parametry wejściowe, jednostki, generowanie zadania,
kontrolę siatki i warunków, uruchomienie solvera, odczyt logów i eksport
wyników do niezależnej analizy. To wymagania funkcjonalne przyszłego narzędzia,
a nie deklaracja, że wybranyMCP już je realizuje.

Warunkiem sensownej symulacji mechanicznej są rzeczywiste dane materiału,
geometria połączeń i model tłumienia. Warunkiem modelu pokoju są geometria,
warunki brzegowe i późniejsza identyfikacja. Bardziej złożony solver z
arbitralnymi parametrami może dać bardziej szczegółowy, lecz nadal niepewny wynik.

Najpierw rozwiązać jawny prosty przypadek kontrolny, następnie sprawdzić
zbieżność i porównać z analizą prostszą lub eksperymentem. Sam komunikat
„solver zakończył” nie jest dowodem poprawności wyniku.

## Aktualny rezultat oceny

Przegląd katalogu integracji nie dostarczył w tej sesji potwierdzonego,
pasującegoMCP do obudów/solvera. To nie jest twierdzenie, że takich projektów
nie ma. Nie zakończono audytu konkretnych repozytoriów, bo użytkownik
odłożył tematCAD. Żadnej integracji nie uznano za sprawdzoną ani nie uruchomiono.

Rekomendacja: kontynuować modelPython, kontrolę źródeł i analizę wariantów.
Powrócić do dodatkowego solvera dopiero przy pytaniu, którego obecny model
nie rozstrzyga. Ograniczenia już wskazane: THD, termika, drgania paneli,
nieszczelności i rzeczywiste pole pokoju.
