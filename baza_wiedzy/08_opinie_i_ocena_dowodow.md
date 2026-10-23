# Opinie właścicieli i konstruktorów — jak je wykorzystujemy

Stan: 2026-10-23. Włączono do researchu na wyraźne życzenie użytkownika.
Poniższy rejestr jest początkiem zbioru, a nie reprezentatywną ankietą rynku.

## Cztery różne rodzaje świadectwa

| Typ | Wartość dla projektu | Ograniczenie |
|---|---|---|
| Własna konstrukcja + zdjęcia + nastawy + pomiary | Można sprawdzić warunki i porównać z modelem | Wynik nadal dotyczy konkretnej sztuki i pokoju |
| Właściciel opisuje dłuższe użytkowanie | Hałas mechaniczny, trwałość, praktyka montażu, serwis | Zwykle brak wspólnego protokołu i liczby wszystkich sprzedanych sztuk |
| Doświadczony konstruktor radzi w wątku | Hipotezy i rozpoznanie błędów projektowych | Sam staż ani liczba postów nie dowodzą prawdziwości każdej tezy |
| Plany, symulacje, pytanie o zakup | Dobre źródło problemów i danych do sprawdzenia | Nie jest opinią z eksploatacji gotowego urządzenia |

Nie oznaczamy autora jako eksperta wyłącznie na podstawie nicku lub popularności.
Zapisujemy weryfikowalny kontekst: własny projekt, pomiar, analizę, zmianę zdania.

## Pierwsze zebrane przypadki

### OP-01 — RSS315HF-4, projekt bass-reflex, 2020

Źródło: [otakar i dyskusja o finalizacji skrzyni](https://www.diyaudio.com/community/threads/help-finalising-enclosure-design-dayton-rss315hf-4.360765/),
dostęp 2026-10-23 przez browser-harness. Typ: plan i symulacja, porady konstruktorów.
Autor pokazał projekt BR i zrzuty WinISD. Brian Steele zwrócił uwagę na
łączenie przeciwległych paneli; Pharos pokazał przykłady prętowych wzmocnień.
chris 661 wskazał SpeakON w rozmowie o terminalu. Nie ma tu udokumentowanego
porównania THD ani potwierdzonego rezultatu ukończonego subwoofera autora.

Wpływ na projekt: do sprawdzenia układ wręg, front–tył i szczelny terminal.
Nie przenosimy portu ani jego strojenia do sealed. Obrazy zostały pobrane
i obejrzane osobno: [raport analizy](../raporty/005_analiza_obrazow_diyaudio.md).

### OP-02 — RSS315HF-4 i alternatywny projekt, 2006

Źródło: [DIY Sub with DAYTON RSS315HF-4 in progress](https://www.diyaudio.com/community/threads/diy-sub-with-dayton-rss315hf-4-in-progress-can-someone-check-my-math.72895/),
dostęp 2026-10-23 przez browser-harness. Typ: mieszany, historyczny.
`pjpoes` opisuje własny projekt i subiektywnie preferuje sealed po wcześniejszym
wariancie portowanym; wskazuje też rolę EQ i pokoju. Nie podaje porównywalnych
poziomów, pełnego protokołu ani THD. Nie uznajemy tego za dowód przewagi sealed.

`lousymusician` opisuje własny Quattro, a później koryguje wcześniejszą ocenę
HF po wykryciu błędnego Vas w WinISD. To istotny przykład potrzeby czytania
całego wątku, wraz z korektami. Quattro nie jest obecnym finalistą projektu.

Wątek jest stary, a cytowane w nim parametry RSS315HF-4 różnią się od obecnej
karty. Nie używamy jego T/S do dzisiejszego modelu ani jako statystyki trwałości
obecnej produkcji. Nie kopiujemy opinii o filtrach jako reguły ochrony napędu.

## Czego nadal brakuje

Uzupełnienie przez Firecrawl: [wątek386102](https://www.diyaudio.com/community/threads/sealed-ported-convertible-subwoofer.386102/page-2)
zawiera własną relację `cspieker` o zamykanych portach i uszczelnieniu, ale
nie porównywalny test naszych czterech modeli. Wzmianki o pomiarach JohnMarsh/HobbyHiFi
to tropy do oryginałów; nie uznano ich za odczytane wyniki. Linkowany tam
SB34SWPL76-3DVC jest innym modelem niż SB34SWPL76-4.

[Dyskusja ASR28117](https://www.audiosciencereview.com/forum/index.php?threads/help-with-my-faulty-12-subwoofer-design.28117/page-3)
dotyczy również SB34SWPL76-4 i interpretacji THD. Odczytano stronę3, bez pełnej
historii i danych surowych; nie przyjęto porad litrażowych jako dowodu optimum.
Notatki: [SRC13/14](../dane/zrodla/SRC13_14_notatki_firecrawl.json).
Zgodnie zU-010 dalsza praca koncentruje się teraz na danych i pytaniach fizycznych.

- Aktualnych, niezależnych relacji właścicieli dla RSS390HF-4, RSS315HFA-8
  i SB34SWPL76-4 z rozpoznaną rewizją i warunkami eksploatacji.
- Dane o hałasach mechanicznych i wadach egzemplarzy z opisem diagnozy,
  a nie samym nagraniem przesterowanego telefonu.
- Długotrwałego użytkowania i serwisu; brak doniesień nie dowodzi bezawaryjności.
- Niezależnych krzywych THD/kompresji przy znanym poziomie i napięciu.
- Sprawdzenia, czy relacje na różnych stronach nie pochodzą od tej samej osoby.

Wynik negatywny researchu też zapisujemy: „nie znaleziono wiarygodnej relacji
w przeszukanych źródłach”, z zakresem i datą. Nie zamieniamy tego w „problem nie istnieje”.

## Karta przyszłej opinii

| Pole | Wymagany zapis |
|---|---|
| Identyfikacja | Model, wersja/impedancja, data wpisu i dostępu, URL/permalink |
| Autor i niezależność | Właściciel/konstruktor/sprzedawca; powiązanie handlowe jeśli znane |
| Konfiguracja | Sealed/BR, netto, wypełnienie, napęd, DSP, poziom, pokój |
| Twierdzenie | Parafraza oddzielona od własnej interpretacji; krótki cytat tylko jeśli potrzebny |
| Dokumentacja | Zdjęcie, plik projektu, wykres, dane surowe, warunki pomiaru |
| Problem i korekta | Co nie działało, jak wykluczono elektronikę/skrzynię, czy autor zmienił zdanie |
| Znaczenie | Parametr do sprawdzenia, możliwy test lub konsekwencja dla wyboru |
| Pewność | Wysoka/średnia/niska z przyczyną; bez pozornej punktowej precyzji |

## Jak czytać wykresy z forum

Najpierw obejrzeć oryginał, nie sam podpis. Zidentyfikować narzędzie, osie,
jednostki, skalę, legendę, warunki i sygnał. Oddzielić symulację od pomiaru,
transfer znormalizowany od SPL bezwzględnego i impedancję od odpowiedzi akustycznej.
Sprawdzić, czy zdjęcie dotyczy konstrukcji autora czy jest tylko przykładem.

Brak zakładki Signal w WinISD uniemożliwia porównanie ilościowego wychylenia
przy znanej mocy. Nieznane filtry, straty i parametry T/S uniemożliwiają
dokładny replay. Odczyt z krzywej zapisywać jako zakres lub przybliżenie;
wartości z czytelnych pól wejściowych mają inny status niż digitalizacja wykresu.
