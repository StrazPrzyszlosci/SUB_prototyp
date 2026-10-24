# Decyzje, pytania i zmiany zakresu

Stan: 2026-10-23. Ten rejestr uzupełnia brief, bez zmieniania jego treści.

| ID | Ustalenie | Źródło | Wpływ |
|---|---|---|---|
| U-001 | Użytkownik ma multimetr, oscyloskop i lutownicę | Odpowiedź w rozmowie 2026-10-23 | Nie zakładać, że ma mikrofon, interfejs czy DSP |
| U-002 | Dobór i zakupy toru pomiarowego po zakończeniu budowy prototypu | Odpowiedź w rozmowie 2026-10-23 | Bieżący etap opierać na źródłach, modelach i tolerancjach; nie blokować go pomiarem T/S |
| U-003 | Możliwe pomiary tylko w pokoju odsłuchowym | Odpowiedź w rozmowie 2026-10-23 | Osiągi in-room; ograniczona identyfikacja urządzenia w oderwaniu od pokoju |
| U-004 | Teraz praca badawcza do budowy prototypu | Doprecyzowanie w rozmowie 2026-10-23 | Budowa i pomiary jako dalsze etapy, obecnie research i dokumentacja |
| U-005 | Uwzględnić opinie użytkowników i osób znających aktualne przetworniki | Doprecyzowanie w rozmowie 2026-10-23 | Osobny rejestr doświadczeń z modelami i warunkami, bez mieszania z pomiarami |
| U-006 | Internet przez browser-harness; później dopuszczony także Firecrawl do wiedzy badawczej, obliczeń i symulacji | Polecenia użytkownika | Firecrawl do ekstrakcji, przeglądarka do interakcji i obrazów |
| U-007 | Obejrzeć również wykresy w znalezionym wątku | Doprecyzowanie w rozmowie 2026-10-23 | Pobrano i obejrzano 9 załączników wątku 360765; osobny raport analizy |
| U-008 | Obecnie nie zajmować się narzędziami CAD | Doprecyzowanie w rozmowie 2026-10-23 | Ocena/instalacja integracji CAD i ich MCP odłożona; geometria i wymagania mechaniczne pozostają w planie |
| U-009 | Na razie zatwierdzone wyłącznie ADAM Sub12 i Sub15 jako referencje | Odpowiedź użytkownika 2026-10-23 | Referencje subwooferów ustalone; A8H/S3V tylko materiał rozpoznawczy na później; progi liczbowe nadal otwarte |
| U-010 | Teraz zajmować się wyłącznie naukowymi tematami budowy prototypu | Doprecyzowanie użytkownika 2026-10-23 | Aktywne: fizyka, źródła techniczne, obliczenia i symulacje. Dobór handlowy, wyceny, zakupy i narzędzia CAD odłożone; dotychczasowa dokumentacja pozostaje jako kontekst |
| U-011 | Wykonać program30pakietów badań bez sprzętu; końcowyPDF dopiero po wyczerpaniu tego zakresu | Przekazane materiały i polecenia użytkownika | PROGRAM_30_BADAN.md jest macierzą pokrycia; nie kończyć zadania raportem wstępnym |
| U-012 | Rodzaj kleju też ma wynikać z obliczeń | Polecenie użytkownika | P19 obejmuje nośność spoiny/MDF, geometrię, odrywanie, pełzanie, szczelność i warunki wykonania |
| U-013 | Na końcu zarekomendować jeden głośnik i jedną konstrukcję obudowy | Polecenie użytkownika | Ostateczny wynik nie może być samą krótką listą lub frontemPareto; uzasadnić pojedynczy wybór |
| U-014 | Szeroko rozszerzyć pulę, także STX i innych producentów; dane producentów, opinie i obliczenia dla każdego | Polecenia użytkownika | P03/P29 wymagają przekrojowej kwalifikacji, a nie uznania pierwszych4modeli za najlepsze |
| U-015 | Profesjonalny dobór pod brief | Polecenie użytkownika | Każdy kandydat ma ślad wymagań20–40Hz, liniowości, ochrony, napędu i architektury; braki wyraźnie oznaczone |
| U-016 | Pamiętać o wymiarach pokoju | Przypomnienie użytkownika2026-10-24 |4.6×3.7×2.5m,17.02m²,42.55m³z przybliżonych wymiarów; sweetspot2.5–3m. Sprawdzić miejsce dla dwóchsubów przy monitorach; bez założenia dowolnej lokalizacji przód/tył |
| U-017 | Dokładne pozycje głowy i monitorów nie są obecnie znane | Odpowiedź użytkownika 2026-10-24 | Kontynuować oznaczone scenariusze; nie ponawiać teraz tego pytania ani nie traktować współrzędnych P26 jako pomiaru |

## Decyzje, których nie podejmowano

Nie zatwierdzono przetwornika, wielkości skrzyni, modelu napędu ani DSP.
Nie ustalono liczbowych progów użytecznego SPL, THD, kompresji i szumu.
Zatwierdzono Sub12/Sub15; nie zatwierdzono referencji monitorów.
Obecne modele przetworników i geometrie prototypu są robocze.

## Pytania do właściwego etapu

| Pytanie | Kiedy potrzebne | Jak pracować do odpowiedzi |
|---|---|---|
| Jakie porównywalne progi wynikają z Sub12/Sub15? | Zamknięcie liczbowych wymagań R0 | Modele zatwierdzone w U-009; badać ich pełne dane i warunki |
| Jaki kompromis 20 Hz kontra 25–40 Hz i wysoki SPL? | Po pokazaniu R2 | Porównać cele i koszt headroomu; nie wymyślać zatwierdzonego progu |
| Dokładna pozycja głowy i dostępne miejsca skrzyni? | Przed finalną geometrią R3 | Scenariusze dla pokoju 4,6 × 3,7 × 2,5 m, 2,5–3 m odsłuchu |
| Jakie formaty i tolerancje przyjmuje wykonawca CNC? | R5 | Projekt parametryczny; nie zatwierdzać rozkroju |
| Modele multimetru/oscyloskopu i sond? | Kontrole elektroniki i etap po budowie | Nie zakładać możliwości bezpiecznego pomiaru wyjść mostkowych |

Brak odpowiedzi na pytania późniejszych etapów nie wstrzymuje badań źródłowych.
