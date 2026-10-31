# Rejestr dokumentacji dziewięciu marek — stan 31.10.2026

**Odtwarzalne wartości producentów są zapisane bezpośrednio w repozytorium**, w [wersjonowanym pliku JSON](2026-10-31_9_marek_weryfikacja.json). Dla każdej z dziewięciu marek plik podaje model, oficjalny adres producenta, dokładny URL oryginalnej karty (jeśli jest), parametry T/S, moc i jej protokół, wymiary kosza/otworu, rodzaj wychylenia i źródłowe zastrzeżenia. Pola `null` oznaczają brak zweryfikowanych danych.

Rejestr obejmuje: Great Plains Audio 416-8B, VOLT RV3863, SUPRAVOX 400-2000 EXC (elektromagnes 12 V), EMS B15EX, PURIFI PTT10.0X04-NAB-01, Kartesian Wom265_vKi-6, PHL 6301MNd, ETON Symphony II 12-212/C8/62 HEX i Davis 39 GPA 15.

**Kontrola źródeł:** [obliczony audyt T/S i odstępstw](../../wyniki/brief20261031_audyt_t_s_9_marek.json). W szczególności w danych GPA 416-8B katalogowe Vd=314 cm³ różni się od Sd×Xmax=329,48 cm³. SUPRAVOX ma rozbieżność opublikowanej Mms=66 g wobec 78,74 g z Fs/Vas/Sd przy zadanym modelu powietrza. EMS nie ma pełnego zestawu producentowych T/S. Nie podstawiono wartości z forum ani niezależnych katalogów.

**Oryginalne karty:** [skrypt pobrania PDF/HTML i utworzenia manifestu SHA-256](../../skrypty/odtworz_dokumentacje_producentow.py) odtwarza lokalne kopie źródeł z dokładnych URL zapisanych w JSON. Komenda z katalogu repo:

```bash
python skrypty/odtworz_dokumentacje_producentow.py --out /tmp/sub_producers
```

Bez potwierdzonych praw redystrybucji nie opublikowano oryginalnych binarnych kart PDF w Git. To oznacza, że z samego repo można odtworzyć **utrwalone parametry liczbowe i ich pochodzenie**, ale nie całe oryginalne wykresy ani przyszłą dostępność zewnętrznych serwerów. Stan ten pozostaje jawnie niezamkniętym wymaganiem archiwalnym, a nie pełną kopią kart producentów.

**Zakres badań:** [brief i metodologia](../../raporty/BRIEF_2026-10-31_wzmacniacz_DSP_i_9_marek.md) oraz [274 725 obliczeń przesiewowych](../../wyniki/brief20261031_pelna_pula_35_wstepna_analiza.json). Pierwotna pula: 24 produkty + 2 SB (3 warianty elektryczne); nowych unikatowych produktów jest 8, bo PURIFI już występował. Łącznie 34 produkty, 35 konfiguracji elektrycznych, 33 przeanalizowane w przesiewie i 2 wstrzymane. Nie jest to jeszcze powtórzenie pełnych eksperymentów P01–P30 dla nowych modeli.
