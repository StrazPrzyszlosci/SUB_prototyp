# B12-12 — protokół danych rzeczywistych kosza i badań połączeń (RSS390HF-4)

**02.11.2026 · protokół przygotowawczy, NIE zapis wykonanych pomiarów · bez zakupów i CNC.**

## 1. Rejestr danych źródłowych

| Parametr | Status dowodu | Wartość |
|---|---|---|
| Model | Karta Daytona 295-468 | RSS390HF-4 (15", 4 Ω) |
| Wymiar zewnętrzny kołnierza | Producent | Ø388,4 mm |
| Wycięcie montażowe | Producent | Ø355,8 mm |
| BCD ośmiu otworów | Producent | Ø368 mm |
| Średnica w kołnierzu | Producent | Ø6,5 mm |
| Grubość kołnierza | Producent | 10,5 mm |
| Głębokość całkowita | Producent | 178 mm |
| Liczba głównych żeber | Oględziny rysunku producenta | 4 |
| Relacja osi żebro–śruba | Oględziny rysunku producenta | 4 osie otworów ok. na osi żeber, 4 między żebrami |
| Dokładna faza φ i jej tolerancja | **Niezwymiarowane** | NIE ZMIERZONO |
| R_b(Y,θ) i zasięg żeber na Y=44–74 mm | **Niezwymiarowane** | NIE ZMIERZONO |
| Obwiednia terminali i przewodów | **Niezwymiarowane** | NIE ZMIERZONO |
| Dostęp klucza, wkrętaka, ręki | **Niezwymiarowane** | NIE ZMIERZONO |
| Nośność MDF, spoin i wkładek | **Brak testów** | NIE ZMIERZONO |

Źródło pierwotne: https://www.daytonaudio.com/images/resources/295-468-dayton-audio-rss390hf-4-specifications-46176.pdf (kontrola 02.11.2026). Sekcję z danymi producenta należy oddzielać od własnych pomiarów; archiwalna karta ma inne wartości parametrów T/S.

## 2. Co zebrać od producenta lub z rzeczywistego egzemplarza

Własny układ współrzędnych kosza: oś = (0,0), pozytywny Y do wnętrza od przedniej płaszczyzny MDF, kąt θ=0 na jednej z czterech osi otworów wizualnie związanych z żebrami. Dokumentować **rzeczywistą** fazę po ustaleniu jednoznacznej definicji, a nie domyślać się z poglądowego szkicu.

- Fotografia/rzut od tyłu z nieodkształconą perspektywą, skala i referencja Ø368; oznaczenia kolejnych ośmiu otworów 0–7 oraz czterech żeber.
- Promień skrajnej powierzchni kosza i żeber, jako funkcja **kąta θ i głębokości Y**, z naciskiem na pozycje, w których mają znaleźć się klocki za frontem MDF44 (Y=44–54, 44–64, 44–74).
- Cztery strefy *pod żebrami* oraz cztery strefy *pomiędzy żebrami* oddzielnie, w tym minimum kątowe i radialne prześwity wokół osi śrub.
- Otwór i rowek terminali, wyprowadzenia kabli, promień dojścia i wydmuchu dla otworów wentylacyjnych.
- Typ konkretnego łba, podkładki, uszczelki, wkładki (średnica **zewnętrzna** i długość) oraz minimalne wymagane zazębienie określone dokumentacją wybranego połączenia; nie zakładać, że Ø6,5 w koszu = Ø6,5 otworu MDF.
- Przejście narzędzia od frontu, ewentualny dostęp do tylnej nakrętki po sklejeniu obudowy, uszkodzenie wkładki przy serwisie, ponowne uszczelnienie.

**Nie podpisywać pomiarów jako gotowych przed ich fizycznym uzyskaniem.** Fotografii właścicieli z forów nie zastępować pomiarami Fundacji; przypisywać autorstwo i linkować oryginały.

## 3. Protokół mechaniczny dwóch kandydatów (jeszcze bez pomiarów)

Porównać **A: osiem lokalnych klocków/wkładek** i **B: rama rozprowadzająca siły do MDF/wręg**. Dla każdego wykonać na rzeczywistej partii MDF44: udokumentowaną procedurę łączenia; co najmniej trzy powtarzalne próbki tego samego detalu (liczba jest minimalną propozycją badań porównawczych, nie normą); próby wyrywania, poprzecznego ścinania, odrywania i obrotu wkładki; pomiar przemieszczeń, momentu i rodzaju uszkodzenia. Oddzielnie badać cykle montażowe, obciążenie długotrwałe, wilgotność i zmęczenie. Stan powierzchni, klej, grubość i czas utwardzania rejestrować.

Protokół nie przypisuje **żadnego bezpiecznego momentu dokręcania**, dopuszczalnej siły, klasy śruby ani wytrzymałości kleju bez pomiarów. Wariant B musi mieć własny wykaz rzeczywistych złączy od ośmiu otworów kołnierza do wręg — nie porównywać samego pola spoiny A z idealnie sztywną ramą B.

## 4. Bramki akceptacyjne

- G1: zweryfikowany model kosza i terminali zgodny z konkretną rewizją RSS390HF-4.
- G2: test pełnego prześwitu **3D**, odróżniający punkty żebrowe i międzyżebrowe, z prawdziwym narzędziem i kablem.
- G3: rzeczywiste próbki MDF/spoiny/łącznika i powtarzalne próby statyczne, odrywające i serwisowe.
- G4: ocena wentylacji i szczelności oraz kompletny obrys całego urządzenia **≤500 mm**.
- G5: zintegrowany i zwalidowany model kontaktu oraz ścieżki sił (nie tylko geometria) przed CNC.

**G1–G5 są otwarte. Brak pełnego modelu kosza i próbek uniemożliwia wydanie zgody CNC.**
