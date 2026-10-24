"""Rzut od użytkownika: orientacja i warunkowa zgodność odległości odsłuchu."""
import csv
import hashlib
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def main():
    cfg = json.loads((ROOT/'dane/konfiguracje/pokoj_rzut_scenariusze_v1.json').read_text())
    source = ROOT/cfg['source_image']
    assert hashlib.sha256(source.read_bytes()).hexdigest() == cfg['source_image_sha256']
    width, length, height = cfg['room_dimensions_xyz_m_assumed']
    rows = []
    for clearance in cfg['listener_back_wall_clearance_scenarios_m']:
        listener_y = length-clearance
        for lateral in cfg['monitor_lateral_offset_from_listener_m']:
            for distance in cfg['listening_distance_scenarios_m']:
                # Równe, założone wysokości. To twierdzenie Pitagorasa, nie fit pikseli.
                longitudinal = float(np.sqrt(distance**2-lateral**2))
                monitor_y = listener_y-longitudinal
                reconstructed = float(np.linalg.norm([lateral, listener_y-monitor_y, 0.]))
                assert abs(reconstructed-distance) < 1e-12
                legacy_distance = float(np.hypot(lateral, listener_y-cfg['legacy_hypothetical_monitor_front_distance_m']))
                rows.append(dict(listener_back_clearance_m=clearance,
                                 listener_y_m=listener_y, lateral_offset_m=lateral,
                                 stereo_spacing_m=2*lateral, target_distance_m=distance,
                                 required_monitor_front_distance_m=monitor_y,
                                 within_room_point_only=bool(0<monitor_y<length and lateral<width/2),
                                 distance_if_legacy_front_0_65_m=legacy_distance,
                                 reconstructed_distance_m=reconstructed,
                                 scope='GEOMETRIA_SCENARIUSZA_NIE_POZYCJA_ZMIERZONA'))
    with (ROOT/'wyniki/p26_rzut_geometria_odsluchu.csv').open('w', newline='') as handle:
        writer=csv.DictWriter(handle, fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    example=[r for r in rows if r['listener_back_clearance_m']==.7 and r['lateral_offset_m']==1.2]
    minimum=min(r['required_monitor_front_distance_m'] for r in example)
    maximum=max(r['required_monitor_front_distance_m'] for r in example)
    text=f'''# Raport 018 — rzut pokoju i geometria odsłuchu

**Aktualizacja U-020:** opis orientacji poniżej dotyczy wcześniejszego
układu z oryginalnego rzutu. Docelowo RTV będzie po lewej, kanapa po prawej;
obowiązuje [raport019](019_zamiana_kanapy_i_RTV.md) i konfiguracja v2.
Rachunki odległości pozostają warunkową geometrią, nie pozycjami klienta.

Stan: 2026-10-24. **Dane użytkownika:** osoba siedzi na kanapie po lewej
stronie przesłanego rzutu; ściana RTV jest po prawej.

## Co zmienia nowy materiał

Przednia ściana akustyczna y=0 leży po prawej stronie obrazu. Dodatnia oś y
biegnie w lewo ku kanapie. Oś x biegnie od góry obrazu ku dołowi, czyli
od lewej do prawej strony osoby patrzącej na RTV. Oś z pozostaje pionowa.
To przypisanie orientacji nie zamienia symbolu człowieka w pomiar uszu.

Dotychczasowe współrzędne S0=(1,85; 3,10; 1,10) m i monitorów y=0,65 m
były **założeniami**, nie danymi klienta. Nie uznajemy ich za potwierdzone
samym otrzymaniem rzutu. Raporty 013 i 017 zachowują dziedzinę swoich
scenariuszy; ich wykresy nie stają się przez to odpowiedzią tego wnętrza.

**U-019:** użytkownik potwierdził aktualny układ rzutu oraz przybliżone
wymiary z briefu: 3,7 × 4,6 × 2,5 m w kolejności x/y/z.
Nie zmieniono briefu ani nie dopasowano skali rastra do tych liczb.
Potwierdzenie układu nie identyfikuje impedancji otwarć, stanu drzwi,
tolerancji wymiarów ani dokładnego położenia uszu i głośników.
Nie przyjęto pola powierzchni z obróconego, niewyraźnego opisu jako nowego
wejścia liczbowego sprzecznego z potwierdzonymi wymiarami briefu.

## Obliczenie warunkowe: kanapa z tyłu a odsłuch 2,5–3 m

Przeprowadzono {len(rows)} rachunków odległości dla jawnych scenariuszy:
uszy 0,4/0,7/1,0 m od tylnej ściany, środek szerokości pokoju,
równe wysokości uszu i głośnika wysokotonowego 1,1 m oraz boczna odległość
każdego monitora od osi słuchacza 0,8/1,0/1,2 m. **Wartości te nie są
odczytem ze zdjęcia.** Równanie dla monitorów przed słuchaczem:

```text
y_monitor = y_head - sqrt(r² - (x_monitor-x_head)² - (z_monitor-z_head)²)
```

Przykład: uszy 0,7 m od tylnej ściany, y_head=3,9 m, rozstaw monitorów
2,4 m. Gdy zachowamy dawne założenie y_monitor=0,65 m, odległość od każdego
monitora do głowy wynosi **{example[0]['distance_if_legacy_front_0_65_m']:.3f} m**.
To więcej niż orientacyjne 2,5–3 m z briefu.

| Odległość odsłuchu [m] | Wymagana odległość frontu monitora od ściany RTV [m] |
|---:|---:|
'''
    for row in example:
        text+=f"| {row['target_distance_m']:.2f} | {row['required_monitor_front_distance_m']:.3f} |\n"
    text+=f'''
W tym konkretnym scenariuszu odległość 2,5–3 m wymaga frontów monitorów
około **{minimum:.2f}–{maximum:.2f} m od ściany RTV**. To warunek geometryczny,
nie rekomendacja wysunięcia kolumn w przejście. Punkt wewnątrz pokoju nie
potwierdza zmieszczenia skrzyni, podstawy, przewodów i prześwitu za koszem.
Brak wysokości uszu i monitorów nadal uniemożliwia przyjęcie dokładnych r.
Głośniki subwoofera mają osobną wysokość i odległość; nie utożsamiamy ich
z osiami głośników wysokotonowych.

Wniosek projektowy: **położenie kanapy, pozycje monitorów i odległość
odsłuchu muszą być sprawdzane razem**. Nie należy równocześnie zamrażać
dawnych hipotetycznych monitorów, umieszczać głowy bliżej tylnej ściany
i deklarować spełnienia 2,5–3 m bez przeliczenia odległości.

## Warunki brzegowe i wykonalność

Na rzucie widać nieciągłość/przejście w górnej lewej części oraz stolarkę
okienną/drzwiową na dole. To obserwacja obrazu, bez identyfikacji impedancji
otwarć, szkła i połączenia z sąsiednią przestrzenią. Stan drzwi i zakres
akustycznego otwarcia pozostają nieznane. Nie wolno przyjąć na tej podstawie
idealnie sztywnej, szczelnej granicy całego rzeczywistego wnętrza.
Dotychczasowy prostokątny model modalny i tau0 są rodziną kontrolną.
Tau0 nie identyfikuje całej częstotliwościowej impedancji przejścia do korytarza.

Stół, kanapa, szafka RTV oraz otwieranie stolarki ograniczają miejsca dwóch
skrzyń i monitorów. Nie wyznaczono wolnych obszarów z dokładnością CNC
ani nie przyjęto rozmieszczenia przód/tył. Linie i oznaczenia instalacji
elektrycznej na rzucie nie są naszym projektem akustycznym.

## Dowód i granica wyniku

Równanie odległości sprawdzono niezależnym odtworzeniem normy 3D dla
wszystkich {len(rows)} punktów. To dokładna geometria przy założonych
współrzędnych, **bez symulacji SPL i bez pomiaru pokoju**.
Do czasu uzyskania dokładnych pozycji rozwijamy scenariusze w potwierdzonym
układzie i przybliżonych wymiarach pokoju.
Badania napędu, termiki i mechaniki przetworników mogą być kontynuowane
niezależnie od tej odpowiedzi. Nie wybieramy teraz końcowego ustawienia.

Źródło: [niezmieniona kopia rzutu](../{cfg['source_image']}).
SHA-256: `{cfg['source_image_sha256']}`.
Wejścia: [konfiguracja i status obserwacji](../dane/konfiguracje/pokoj_rzut_scenariusze_v1.json).
Kod: [analiza geometrii](../skrypty/analiza_geometrii_odsluchu.py).
Wyniki: [27 scenariuszy CSV](../wyniki/p26_rzut_geometria_odsluchu.csv).
'''
    (ROOT/'raporty/018_rzut_pokoju_i_odleglosc_odsluchu.md').write_text(text)
    print('Rzut: orientacja zapisana;',len(rows),'warunkowych rachunków odległości')
    return rows


if __name__=='__main__':main()
