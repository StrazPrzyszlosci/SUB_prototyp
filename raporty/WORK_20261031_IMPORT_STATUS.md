# Import Work 2026-10-31 — stan częściowy, do uzupełnienia

**Nie scalać bez uzupełnienia brakujących plików i ponownej kontroli.**
Archiwum źródłowe `SUB_prototyp_badania_postep_20261031.zip`
zawiera 60 plików badawczych o poprawnych SHA-256 względem
`MANIFEST_SHA256.json`. Work wygenerował je względem commitu
`4d79871616ca1fd37a4b12c07de2c3febdb8e054`.
Po scaleniu PR #4 bazą stał się commit `8078aa3c15ff0ed75fb2f085f1f051ecbda6e663`.

Niniejsza gałąź importuje **34 oryginalne pliki** z GitHub Git blobs
już przesłanych przez Work, a ponadto zmienia README tematycznie
(z zachowaniem przewodnika) i zapisuje niniejszy rejestr.

**Nie zastępować** `README.md` i `AGENTS.md` plikami z ZIP:
pochodzą ze starszej bazy i usunęłyby poprawki redakcyjne z PR #4.

## Brakujące 23 pliki w Git blob storage

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

Dopiero po wgraniu wszystkich brakujących plików należy:
1. Potwierdzić identyczność każdego z 60 plików z archiwum według SHA-256.
2. Zweryfikować odnośniki raportów i replikację skryptów.
3. Zaktualizować `PROGRAM_30_BADAN.md`, indeks raportów i `AGENTS.md` w oparciu o obecny `main`, bez usuwania zmian z PR #4.
4. Przenieść do rozdziałów README tylko wyniki i wykresy, które zostały rzeczywiście opublikowane i omówione.
5. Utrzymać status badania przed budową; nie ogłaszać walidacji urządzenia ani Release 1.
