# Import Work z 31.10.2026 — status częściowy

Źródło: `SUB_prototyp_badania_postep_20261031.zip` wygenerowane przez ChatGPT Work.
Baza archiwum: `4d79871616ca1fd37a4b12c07de2c3febdb8e054` (przed PR #4).

## Co opublikowano w tej gałęzi

Z oryginalnego archiwum przesłano **34 nowe pliki** z zachowaniem
identycznych bajtów obiektów Git blob: źródła, części danych, raporty 056–060
i wykresy 100/101, P18E.

Dokument `README.md` zmieniono **osobno**, przez włączenie najważniejszych
wniosków i wykresów do odpowiednich rozdziałów przewodnika, bez changelogu
na początku.

## Czego tu jeszcze nie ma

Archiwum obejmuje 60 plików w katalogu `pliki/`, jednak 23 nowe
obiekty nie były dostępne w magazynie GitHuba podczas tego importu.
Nie zostały podmienione plikami zastępczymi ani pozorowanymi wynikami.

- `dane/konfiguracje/p26d_bryly_scenariusze.json`
- `raporty/061_bryly_offset_i_dwa_subwoofery.md`
- `skrypty/pokoj_bryly_P26D.py`
- `skrypty/raportuj_bryly_P26D.py`
- `wyniki/p21d_dogeszczenie.json`
- `wyniki/p21d_naped.csv`
- `wyniki/p21d_podsumowanie.json`
- `wyniki/p21d_port.csv`
- `wyniki/p21d_wyniki.json`
- `wyniki/p25c_kampania.csv`
- `wyniki/p25c_manifest.json`
- `wyniki/p25c_ograniczenia.png`
- `wyniki/p25c_podsumowanie.json`
- `wyniki/p25c_przebiegi.png`
- `wyniki/p25c_termiczne_porownanie.json`
- `wyniki/p25c_weryfikacja_przejsciowa.json`
- `wyniki/p26d_bryly_i_odpowiedz.png`
- `wyniki/p26d_manifest.json`
- `wyniki/p26d_odpowiedzi_nominalne.json`
- `wyniki/p26d_podsumowanie.json`
- `wyniki/p26d_porownanie.csv`
- `wyniki/p30_audyt_manifestow.json`
- `wyniki/p30_audyt_referencje.json`

Trzy pozostałe pliki w archiwum (`AGENTS.md`,
`PROGRAM_30_BADAN.md`, `README.md`) zawierają starszy punkt
odniesienia po PR #3 i wymagają selektywnego połączenia z nowszym
`main`; nie należy ich bezpośrednio nadpisywać. Istotne informacje
o stanie publikacji znajdują się także w `WZNOWIENIE.md` archiwum.

**Uwaga:** P25C/P21D/P26D mają częściowo brakujące tabele lub wykresy,
więc powiązanych raportów nie traktować jako w pełni opublikowanych
pakietów odtwarzalnych. Ten PR powinien pozostać szkicem do uzupełnienia,
a nie zostać scalony przed weryfikacją kompletności.

## Kryteria dokończenia importu

1. Porównać dokładne hashe Git blob każdego pliku z lokalnym archiwum.
2. Dosłać brakujące 23 pliki (w szczególności wyniki i rysunki P25C/P26D).
3. Scalić jedynie niesprzeczne zmiany `AGENTS.md` i
   `PROGRAM_30_BADAN.md`, bez cofania zasad przewodnika po PR #4.
4. Sprawdzić, że wszystkie linki i wymagane dane dla raportów 056–061
   istnieją na gałęzi.
5. Zaktualizować `raporty/README.md` jako **indeks tematyczny**,
   nie dziennik zmian, oraz sprawdzić reprodukowalność.

Archiwum zweryfikowano lokalnie: 60/60 wpisów zgodnych z sumami SHA-256
i rozmiarami z `MANIFEST_SHA256.json`. Nie oznacza to pełnego audytu
fizycznego ani niezależnego przeliczenia wszystkich symulacji.
