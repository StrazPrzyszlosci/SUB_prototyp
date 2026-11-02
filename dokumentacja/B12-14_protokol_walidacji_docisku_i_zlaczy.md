# B12-14 — protokół walidacji docisku, śrub, MDF i tarcia kołnierza RSS390HF-4

**2 listopada 2026. Dokument planistyczny; NIE raport przeprowadzonych prób. Brak zamówień i zatwierdzenia CNC.**

## Warunek rozpoczęcia

Przed testami trzeba zweryfikować typ i rewizję RSS390HF-4, rzeczywisty obrys kosza i terminali za MDF 44 mm, osiem punktów mocujących, rodzaj śruby i wkładki, sposób klejenia oraz projekt dwóch ścieżek sił:
- **A:** osiem lokalnych klocków i wkładek za frontem, ze szczególnym sprawdzeniem rozwarcia po utracie jednego połączenia;
- **B:** rama rozprowadzająca obciążenie, z pełnymi złączami kołnierz–rama–wręgi–front; nie może być idealnie sztywnym niezmierzonym odniesieniem.

Dokumentacja producenta nie daje sztywności ani nośności tych połączeń. Grupy muszą być porównywane dla tych samych obciążeń, warunków MDF i procesu montażu.

## Macierz prób i wielkości pomiarowe

| Próba | Mierzone wielkości | Wymagany zapis |
|---|---|---|
| Geometria i montaż | 8 osi, faza 4 żeber, obwiednia terminali, tor narzędzia, grubości, wymiary wkładek | plik/rysunek, jednostki, niepewności pomiaru, rewizja kosza |
| Kontrola wstępnego docisku | rzeczywiste napięcie w śrubie, powtarzalność montażu; pomiar po 1 h i 24 h | metoda pomiaru; nie utożsamiać samego momentu z siłą |
| Sztywność lokalna | krzywa siła–ugięcie, histereza, rozwarcie i powrót styku | kompletne przebiegi, zero i kalibracja czujników |
| Tarcie połączenia | siła poprzeczna przy pierwszym mikropoślizgu i po makropoślizgu | lokalny rozkład nacisku, wybrana uszczelka, powierzchnie |
| Wyrywanie / docisk MDF | zniszczenie gwintu lub wkładki, uszkodzenia MDF | siła szczytowa, przemieszczenie, zdjęcia przełomów |
| Spoina klejona | odrywanie krawędzi, ścinanie, pełzanie, odwilgocenie | krzywa siła–przemieszczenie, temperatura/wilgotność/czas |
| Serwisowanie | powtarzane wyjęcie i założenie śruby, obrót wkładki | moment, zużycie, utrata szczelności i sprawności |
| Niezawodność pojedynczego punktu | kontrolowana utrata jednego łącznika, ponowne rozłożenie sił | mapa wszystkich punktów, otwarcie i przemieszczenia |
| Warunki obudowy | masa i drgania, szczelność, wentylacja, pełna głębokość z osprzętem ≤500 mm | wymiary całego zespołu oraz zdjęcia geometrii |

**Liczebność:** pilotaż minimum trzech próbek na wariant i warunek ma wykazać rozrzut metody i obszary awarii. Trzy próbki nie pozwalają zadeklarować normowej niezawodności ani ustalić materiałowych współczynników bezpieczeństwa; liczebność końcową określa się z rzeczywistego rozrzutu i wymaganego poziomu ufności.

## Walidacja modelu B12-14

Zmierzony docisk P_i oraz charakterystyki siła–ugięcie są wejściami do nowego modelu. Dla każdego scenariusza:
1. porównać przewidywane i zmierzone siły w śrubach oraz maksymalne przemieszczenia;
2. zweryfikować, że model kontaktu daje C=0 tam, gdzie szczelina faktycznie się otwiera, a nie odwrotnie;
3. porównać lokalną inicjację poślizgu z modelem tarcia; globalny limit µΣC jest jedynie nierównością konieczną, nie modelem lokalnym;
4. wykonać siatkową analizę zbieżności MES kontaktu o **rzeczywistym rozkładzie powierzchni nacisku**;
5. porównać warianty A/B dopiero po określeniu rzeczywistego kosztu mechanicznego: liczby połączeń, łatwości serwisu, trwałości, miejsca na wentylację i spójnego warunku obciążenia.

## Status metodologiczny

- **WYKONANE:** warunkowe obliczenia B12-14 (1152 układów kontaktu, 4608 nierówności tarcia; kod i regresja GitHub).
- **NIE WYKONANO:** doświadczeń na MDF, kleju i połączeniach; fizycznego pomiaru docisku, prześwitu i temperatury; zwalidowanego MES 3D; prototypu.
- **NIE DOPUSZCZONO:** frezowania CNC, doboru momentu dokręcenia i zakupów.

Źródła metodologiczne: [B12-13](../raporty/B12-13_sztywnosc_4plus4_i_awaria_mocowan_RSS390HF4.md), [P44B](../raporty/113_P44B_tarcie_i_wrazliwosc_16200.md), [Sandia National Laboratories – Guideline for Bolted Joint Design and Analysis](https://www.sandia.gov/research/publications/details/guideline-for-bolted-joint-design-and-analysis-version-1-0-2008-01-01/).
