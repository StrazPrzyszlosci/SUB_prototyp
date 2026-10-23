# Analiza obrazów wątku DIY — bass-reflex RSS315HF-4

Data oględzin: 2026-10-23. Źródło: [Help finalising enclosure design](https://www.diyaudio.com/community/threads/help-finalising-enclosure-design-dayton-rss315hf-4.360765/),
otakar, wrzesień 2020; komentarze m.in. Pharos, Brian Steele i chris 661.
Odczyt i pobranie przez browser-harness; obejrzano **wszystkie dziewięć załączników**.
Oryginały oraz ich bezpośrednie adresy: [indeks](../dane/zrodla/obrazy_diyaudio_360765/indeks.json).

## Odczyt treści graficznej

| Plik | Treść i widoczne warunki | Ograniczenie |
|---|---|---|
| [01](../dane/zrodla/obrazy_diyaudio_360765/zalacznik_01.png) | WinISD 0.7.0.950, względna charakterystyka; F3 wizualnie ok. 21–23 Hz | Brak bezwzględnego SPL |
| [02](../dane/zrodla/obrazy_diyaudio_360765/zalacznik_02.png) | Prędkość portu; maksimum ok. 18 przy 22–23 Hz | Nie widać ustawień jednostek ani poziomu zasilania |
| [03](../dane/zrodla/obrazy_diyaudio_360765/zalacznik_03.png) | Wychylenie; minimum przy strojeniu, przekroczenie czerwonej granicy ok. 14,3 mm poniżej 20–22 Hz | Nie znamy napięcia/mocy wejściowej |
| [04](../dane/zrodla/obrazy_diyaudio_360765/zalacznik_04.png) | Typ vented, Vb=3,700 ft³, Fb= 24 Hz | Symulacja innej topologii niż prototyp sealed |
| [05](../dane/zrodla/obrazy_diyaudio_360765/zalacznik_05.png) | Jeden port prostokątny 2 × 15,75″, długość 35,03″, pole 203,2 cm²; rezonans portu 193,12 Hz | Geometria i filtry wymagają pełnych danych |
| [06](../dane/zrodla/obrazy_diyaudio_360765/zalacznik_06.jpg) | Rysunek skrzyni, portu i centralnej wręgi; bilans brutto/netto | Szkic, nie dokumentacja wykonawcza |
| [07](../dane/zrodla/obrazy_diyaudio_360765/zalacznik_07.jpg), [08](../dane/zrodla/obrazy_diyaudio_360765/zalacznik_08.jpg) | Przykład innej kolumny ze wzmocnieniami prętowymi i wyłożeniem ścian | Nie są zdjęciami ukończonego projektu otakara |
| [09](../dane/zrodla/obrazy_diyaudio_360765/zalacznik_09.jpg) | Zmieniony szkic rozmieszczenia wzmocnień | Brak porównawczego pomiaru drgań |

Odczyty z krzywych są przybliżone. Pola liczbowe są czytelniejsze niż same
przecięcia krzywych. Pasek kursora w prawym górnym rogu nie zastępuje informacji
o aktualnym punkcie każdej krzywej. Załączniki 01/04/05 powtarzają tę samą
odpowiedź z różnymi zakładkami; nie są trzema niezależnymi eksperymentami.

## Własne przeliczenia

[Skrypt audytu](../skrypty/audyt_wykresow.py) przelicza jednostki z jawnych
odczytów i zapisuje [JSON](../wyniki/audyt_wykresow_diyaudio.json):

- 3,7 ft³ = **104,77 l netto**.
- Kanał 2 × 15,75 × 35,03″ obejmuje około **18,08 l powietrza**. To przestrzeń
  kanału, a nie sam materiał ścianek; w bilansie trzeba je rozróżniać.
- Szkic odejmuje 0,638 ft³ kanału, zgodne z powyższym przeliczeniem.
- Z zapisanych na szkicu 4,45 − 0,0581 − 0,638 − 0,05 otrzymujemy
  3,7039 ft³, czyli około 104,88 l. Różnica względem 3,7 wynika z zaokrągleń.

Nie odtworzono pełnej symulacji WinISD: brakuje wejścia Signal, filtrów,
pełnego zestawu T/S i strat. Nie wyznaczono z tych obrazów THD ani mocy bezpiecznej.

## Wpływ na nasz projekt

Wykresy są spójne jakościowo z odciążeniem membrany w pobliżu strojenia BR
i wzrostem ruchu poniżej. Nie dowodzą, że nasza obudowa zamknięta osiągnie
podobne pasmo, wychylenie lub wydajność. Nasz model pozostaje liczony osobno.

Do dokumentacji prototypu przenosimy metodę bilansu objętości, potrzebę
kontroli Xpeak i usztywniania przeciwległych paneli. Skuteczność wręg oceniamy
z geometrii i późniejszych badań; odsłuch opukiwania panelu jest diagnostyką,
nie ilościowym dowodem redukcji promieniowania ścian.

Nie uznajemy ok.18 na wykresie prędkości za potwierdzenie bezszumowej pracy
portu: znaczenie mają jednostki, poziom sygnału, profil krawędzi i przepływ.
W obecnym prototypie sealed zagadnienie kanału jest wyłącznie porównawcze.
