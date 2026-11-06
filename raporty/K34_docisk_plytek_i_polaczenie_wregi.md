# K34 — docisk płytek i przeniesienie obciążenia wręgi

5 listopada 2026. **Obliczenia przybliżone, CNC HOLD.** Nie zmieniono DXF.
Analiza K33 wykazała zwiększenie reakcji podpór do około108 N na śrubę
w scenariuszu5g. K34 sprawdza, co ta siła oznacza dla MDF i połączeń wręgi.

## Najważniejsza korekta: napięcie wstępne nie jest siłą zewnętrzną

W uproszczonym połączeniu śrubowym, przed rozwarciem:

- siła śruby `Fb = Fi + C·P`;
- pozostający docisk części `Fc = Fi − (1−C)·P`;
- siła netto przekazywana na wręgę `Fb − Fc = P`.

`Fi` to napięcie wstępne, `C` przyjęty udział sztywności, `P` zewnętrzne
obciążenie rozciągające połączenie. Po rozwarciu model przyjmuje `Fc=0`
i `Fb=P`. Nie dodajemy wszystkich napięć wstępnych do globalnej siły,
którą ma przenieść klej wręgi. Lokalny nacisk pod płytką zależy jednak od
**pełnej siły śruby**, nie tylko od108 N obciążenia wkładu.

Przeliczono12 scenariuszy Fi50/100/300/600 N i C0,1/0,3/0,5.
To umowne wartości do analizy, **nie instrukcja dokręcania**. Dla Fi50 N
wszystkie trzy scenariusze rozwarły się; Fi100 N zachowało dodatni docisk
w przyjętych przypadkach. Nie wynika z tego zalecenie100 N: osiadanie MDF,
pełzanie, rzeczywiste C, tolerancje i utrata napięcia nie zostały rozpoznane.
Przykład Fi300/C0,3/P108,015: śruba332,405 N, pozostający docisk224,389 N,
siła netto108,015 N. M3 retencji tworzą własne lokalne pętle docisku.

## Pole płytki nie rozkłada nacisku równomiernie

Model pomocniczy: belka metalowa18×80×4 na jednostronnym podłożu sprężystym
Winklera o grubości22 mm. Sprężyny przenoszą wyłącznie ściskanie.
Przyjęto siłę główną600 N i po30 N od każdej śruby retencyjnej M3.
To oddzielny scenariusz obciążenia płytki, nie wynik przeliczenia momentu
ani bezpośrednio jeden z12 stanów połączenia.

**Model ma pełny przekrój brutto bez otworów.** Nie odtwarza koncentracji
wokół Ø6/Ø4, wyrywania gwintu, odłupania wąskiego pasa MDF ani ortotropii.
Moduł normalny MDF50/150/500 MPa oraz metalu70000/200000 MPa są umowną
analizą wrażliwości, nie danymi wybranego materiału.

| Wynik | Wartość |
|---|---:|
| Średni nacisk po pełnym polu1440 mm² | 0,458 MPa |
| Maksimum w sześciu modelach belka–podłoże | 0,548–1,100 MPa |
| Przypadek Ez150/Ep200000, 81 węzłów | 0,669708 MPa |
| Ten sam przypadek, 161 węzłów | 0,669692 MPa |
| Ten sam przypadek, 321 węzłów | 0,669688 MPa |

Zbieżność siatki potwierdza rozwiązanie tego modelu, **nie jego zgodność
z rzeczywistym MDF**. Nie przypisujemy maksymalnej wartości1,100 MPa
statusu górnego ograniczenia rzeczywistych naprężeń. W szczególności
otwory i krawędzie mogą zwiększyć koncentrację. Sama większa płytka K32
nie uzasadnia nośności przez podzielenie siły przez całe pole.

## Wręga musi rzeczywiście łączyć się z korpusem

Geometria K30/K32 ma wręgę X448–470, Y44–410, Z22–478.
Jej nominalne powierzchnie kontaktu z frontem i tyłem wynoszą po10032 mm²,
a z dnem i górą po8052 mm². Istnienie styku w CAD **nie jest dowodem
wykonanej spoiny klejowej**.

Przy obciążeniu wszystkich czterech rzędów jak duże wkłady K33, umowne
rozdzielenie na przednią i tylną krawędź daje432,06 i427,19 N.
Średnie wskaźniki ścinania na pełnej przedniej/tylnej spoinie to
0,0431/0,0426 MPa. Nie są naprężeniami maksymalnymi ani obliczeniem nośności
kleju. Nie uwzględniają odrywania, niepełnego zwilżenia, niedoklejenia,
podatności korpusu i lokalnego nacisku. Czwarty rząd jest mniejszy, dlatego
przypisanie mu masy dużego rzędu stanowi wspólny scenariusz obciążeniowy,
nie dokładny rozkład mas nastawy100.

Jako test zależności od podparcia usunięto w modelu przednią spoinę oraz
połączenie wąskiego przedniego pasa z żebrami/tyłem, pozostawiając podporę
tylko na końcach Z22/478. Liniowa belka20×22, E2000, z czterema siłami108 N
daje około15,48 mm ugięcia. **To celowo uproszczony kontrprzypadek podparcia,
nie prognoza ugięcia rzeczywistej wręgi.** Pokazuje, dlaczego nie wolno
zakwalifikować jej na podstawie samych małych średnich naprężeń spoiny.
Pełny układ okien, żeber i korpusu wymaga osobnego modelu.

## Nowy problem pasowania: wręga też wymaga pomiaru

Przy zachowaniu dokładnie zewnętrznych D432/H500 mm, nominalnych frontach
2×22, tyle22, górze/dnie22 i wrędze366×456:

| Kierunek | Rozrzut grubości płyt ±0,5 i cięcia wręgi ±0,1 | Skutek |
|---|---|---|
| Głębokość, trzy płyty | łączna szczelina −1,6…+1,6 mm | możliwy wcisk lub otwarta spoina |
| Wysokość, dwie płyty | łączna szczelina −1,1…+1,1 mm | możliwy wcisk lub otwarta spoina |

Warunek utrzymania gabarytu zewnętrznego jest tu jawny. Jeśli wykonanie
utrzyma zamiast niego długość boków, zmieni się gabaryt; tych dwóch strategii
nie należy mieszać. Nie jest to pełna tolerancja zmontowanej skrzyni.

Reguła do przyszłego generatora: `wymiar wręgi = zmierzony wymiar komory −2g`.
Dla próbnego g0,2 mm, błędu pomiaru komory ±0,05 i cięcia±0,1, łączna
szczelina wynosi0,25–0,55 mm. **g nie zostało zakwalifikowane dla kleju**;
centrowanie obu szczelin, dokładność pomiaru i wilgotność pozostają wymaganiami
do sprawdzenia. Przesunięcie lub zmiana wymiaru wręgi wymaga też ponownego
przeliczenia globalnych osi śrub i okien, a nie tylko skrócenia jej obrysu.
Dlatego K34 nie wydaje nowego DXF z pozornie dokładnym wymiarem.

## Walidacja i kolejny krok

Sprawdzono równowagę12 stanów połączenia, nieujemność nacisku i symetrię,
równowagę9 rozwiązań kontaktowych, zbieżność siatki, skalowanie obciążenia,
granicę bardzo sztywnej płytki, reakcje modelu pasa i24 kombinacje skrajne
pasowania wręgi. Tolerancja reszty sił kontaktu1e−3 N przy660 N wynika z
uwarunkowania macierzy na drobnej siatce; nie jest tolerancją wykonania.

[Kod](../skrypty/k34_docisk_i_wrega.py) · [kontrola](../skrypty/sprawdz_k34.py)
· [wyniki i rozkłady](../wyniki/k34_docisk_i_wrega.json)
· [manifest](../wyniki/k34_manifest.json).
Odtwarzanie: `OPENBLAS_NUM_THREADS=1 python skrypty/k34_docisk_i_wrega.py`,
następnie `OPENBLAS_NUM_THREADS=1 python skrypty/sprawdz_k34.py`.

**Następny krok: opracować wspólny, pomiarowy model pasowania korpusu i wręgi,
z zachowaniem globalnych osi mocowań, oraz specyfikację połączenia wręgi
z frontem/tyłem.** Potem model kontaktowy ze zmierzonymi właściwościami
lub próba węzła ma rozstrzygnąć dopuszczalny docisk i trwałość. Bez tego,
bez kwalifikacji metalu/spoin K33 oraz mocowania głośnika i terminala
całość pozostaje CNC HOLD.
