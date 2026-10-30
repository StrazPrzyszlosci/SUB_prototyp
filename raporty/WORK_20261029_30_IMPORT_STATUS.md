# Publikacja wyników badań Work — inwentaryzacja 29–30.10.2026

**Status: IMPORT CZĘŚCIOWY.** Dokument podaje stan faktyczny, aby nie pomylić opublikowanych raportów z pełnym zbiorem danych, niezbędnym do reprodukcji badań.

## Pakiety źródłowe (archiwa przygotowane w trybie Work)

| Archiwum | Rozmiar | SHA-256 |
|---|---:|---|
| `SUB_prototyp_badania_20261029.zip` | 34 183 508 B | `dc924c28457a0ac06d8c7ffe31da06bbaaceb5146333597ef98da687ef9a4dc2` |
| `SUB_prototyp_P21C1_20261030.zip` | 634 267 B | `cc94596be15fb26af4e39a2d3f9217994e58c817d72c1be16f0e6b5fb69274e1` |
| `SUB_prototyp_rekomendacja_PR_20261030.zip` | 20 416 511 B | `3765ed4bfa2852c9fa17024384fb4d6b8ae8d5ce1174790ab18748df2dbf62ab` |

Są to **archiwa przekazania**, nie trzy niezależne zbiory wyników: między nimi występują duplikaty, a nowsze wersje niektórych plików zastępują starsze. Po połączeniu ścieżek, z priorytetem najnowszego pakietu, inwentaryzacja wykazała 417 unikalnych plików. W chwili porównania 92 miały treść inną niż głowica gałęzi roboczej; obejmowały około 23,1 MB danych. Ta liczba nie oznacza 92 nowych raportów.

## Publikacja

- PR #1 został scalony z `main` (raporty 054 i 055). Jego scalenia nie wykonał mechanizm tego importu.
- PR #2 (draft) obejmuje część pozostałych raportów i skryptów: raporty 050–053, dane wejściowe P21C1/P29A, skrypty P21C1/P21C2/P21C3/P29A/P29C i przykładowe JSON.
- **Nie uznawać PR #2 za pełny import.** Pełne źródła, skrypty pomocnicze, wykresy i wyniki CSV/NPZ, zwłaszcza punkty kontrolne P21B i obszerne tabele P21C/P29, wymagają osobnego przeniesienia i weryfikacji SHA.

Zachować oryginalne archiwa do momentu pełnego porównania hashy w repozytorium. W paczce najnowszej znajduje się `zmiany.bundle` z lokalnym grafem commitów i instrukcją `PR.md`; nie jest to to samo co dokonany już import GitHub API.

## Status naukowy

Wybór **RSS390HF-4 / ok. 120 l netto** jest warunkową rekomendacją symulacyjną. Zakres regulacji około 100/120/150 l, korpus 880×480×500 mm, front 44 mm i ograniczenie całkowitej głębokości 500 mm wymagają dalszej weryfikacji wykonawczej. Raport 055 koryguje próg objętości: 99 l jest pierwszym punktem na siatce co 1 l mieszczącym się 0,2 dB od modelowego plateau; 120 l to punkt startu prób, a nie matematyczne optimum.

Nie ma pomiarów zbudowanego prototypu, potwierdzonego THD, danych rzeczywistego chłodzenia lub finalnej ochrony czasowej DSP.

## Warunek zakończenia importu

1. Dla każdej zmienionej lub nowej ścieżki porównać SHA pliku z archiwum i GitHub.
2. Dołączyć brakujące dane binarne/numeryczne, wykresy, komplet skryptów i zmodyfikowane indeksy.
3. Sprawdzić zależności skryptów i odtwarzalność raportów w środowisku z bibliotekami wymienionymi w manifestach Work.
4. Dopiero wtedy oznaczyć import jako kompletny. Nie scalać automatycznie PR #2.
