# Import badań ChatGPT Work — 29–30 października 2026

**Status: ZAKOŃCZONO PRZENIESIENIE PLIKÓW, 417/417 ZGODNYCH BAJTOWO NA GAŁĘZI.**
Porównanie wykonano na gałęzi `badania/rekomendacja-c02-p29-20261030` po zapisaniu plików. Import pozostaje do przeglądu w PR i nie został automatycznie scalony z `main`.

## Źródła

Zachowano wszystkie ścieżki wynikające z połączenia trzech archiwów
przy priorytecie nowszych wersji identycznej ścieżki:

| Archiwum Work | Rozmiar |
|---|---:|
| `SUB_prototyp_badania_20261029.zip` | 34 183 508 B |
| `SUB_prototyp_P21C1_20261030.zip` | 634 267 B |
| `SUB_prototyp_rekomendacja_PR_20261030.zip` | 20 416 511 B |

Po usunięciu duplikatów ścieżek powstało **417 plików źródłowych**.
Dla każdego obliczono obiektowy SHA Git: `sha1("blob "+len+NUL+oryginalne bajty)`.
Porównanie z `GET /git/trees/<branch>?recursive=1` dało **417 zgodnych SHA, 0 braków**.

Szczegółowy wykaz 417 pozycji, rozmiarów, SHA obiektów i archiwów:
[`wyniki/manifest_importu_work_20261030.json`](../wyniki/manifest_importu_work_20261030.json).

## Co przeniesiono

- Dokumentacja i raporty 045, 050–055; raporty 054–055 weszły do `main` przez wcześniejszy PR #1.
- Skrypty badań P21B, P21C0, P21C1, P21C2, P21C3, P18D i P29.
- Konfiguracje i dane wejściowe, wynikowe CSV i JSON (w tym ~1,9 MB `p21c1_membrana.csv` i ~2,1 MB `p29b_warstwa_naped.csv`).
- Oryginalne wykresy PNG/SVG oraz macierze, snapshoty numeryczne i checkpointy NPZ (w tym ~3,4 MB `p21b_pole_reference_9de2a58b864caa24.npz`).
- Indeksy projektowe i oryginalne manifesty badań.

85 oryginalnych obiektów Work (ponad 21 MB), które istniały już w magazynie obiektów GitHub, włączono do gałęzi bez ponownego przesyłania ich bajtów: `create_tree` + `create_commit` + `update_ref`.
Dla pozostałych sześciu brakujących obiektów utworzono nowe bloby przez API, zachowując oryginalne zakończenia wierszy CRLF w CSV.
Część raportów była dodana wcześniej tradycyjnym `create_file`.

## Stan publikacji

- PR #1 (**scalony przez innego aktora**) obejmuje rekomendację oraz raport 055.
- PR #2 (**scalony przez innego aktora**) obejmuje wstępną część skryptów i raportów.
- Dalsza publikacja wszystkich pozostałych plików jest na gałęzi `badania/rekomendacja-c02-p29-20261030` i wymaga odrębnego PR do `main`; nie należy uznawać jej za już scaloną.

## Ograniczenia naukowe

Zgodność plików **nie** oznacza niezależnego ponownego wykonania
wszystkich symulacji, recenzji metodyki ani pomiarowego potwierdzenia wyników.
Rekomendacja RSS390HF-4 i startowej komory około 120 l pozostaje
warunkowa i modelowa. Weryfikacja konstrukcji, wysunięć poza korpus,
limitu całkowitej głębokości 500 mm, ochrony DSP i pomiary prototypu
pozostają otwarte.

Pliki i wykresy są dostępne do recenzji. Nie łączyć PR automatycznie.
