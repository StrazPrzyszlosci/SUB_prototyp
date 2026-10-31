# Raport 019 — docelowa zamiana kanapy i ściany RTV

Stan: 2026-10-24. **Dane użytkownika U-020:** użytkownik zamieni kanapę i RTV
miejscami. Docelowo **kanapa po prawej, RTV po lewej stronie rzutu**.
Wymiary około 4,6 × 3,7 × 2,5 m potwierdzone w U-019 pozostają bez zmian.

To aktualizacja docelowego układu. Oryginalny obraz i konfiguracja v1
zachowują poprzedni układ; nie zmieniono bajtów materiału źródłowego.
Raport018 opisuje wcześniejsze przypisanie orientacji i nadal poprawne,
warunkowe zależności odległości, a nie obowiązujące pozycje urządzeń.

## Konwencja osi do dalszych badań

- y=0: lewa strona obrazu, nowa ściana RTV; +y w prawo, ku kanapie.
- x=0: dolna strona obrazu, lewa strona osoby patrzącej na nowe RTV;
  +x ku górze obrazu.
- z: wysokość nad podłogą.

**Dokładna tożsamość geometryczna:** dla tego samego fizycznego punktu
przejście ze starej konwencji do nowej ma postać:

```text
x_new = 3.7 - x_old
y_new = 4.6 - y_old
z_new = z_old
```

Transformacja zachowuje odległości. Nie wyznacza nowych pozycji uszu,
monitorów ani subwooferów, ponieważ użytkownik przestawia meble, a nie obraca
całego wnętrza wraz z otworami i jego warunkami brzegowymi.

## Konsekwencje akustyczne i konstrukcyjne

Okna/stolarka z dolnej części rzutu stają się lewą stroną osoby patrzącej
na nowe RTV. Górne przejście jest po jej prawej stronie. Stół i pozostałe
stałe ograniczenia zachowują położenie na oryginalnym obrazie, o ile nie
otrzymamy odrębnej informacji o ich przestawieniu.

**Obliczenie modelowe:** częstotliwości własne idealnego, sztywnego
prostopadłościanu zależą od wymiarów, więc sama zmiana konwencji osi ich
nie zmienia. Amplitudy, fazy i zapotrzebowanie na korekcję zależą od nowych
pozycji źródeł/głowy oraz od otwarć, stolarki i strat. Nie wolno przypisać
wynikom dawnego scenariusza fizycznej trafności dla nowego ustawienia.

Odsłuch 2,5–3 m i miejsca na dwie skrzynie należy oceniać względem nowego
frontu. Dokładne współrzędne i prześwity nadal nie są znane. Nie powtarzamy
obecnie pytania o położenie głowy. Badania P12/P13 napędu i gazu mogą być
kontynuowane niezależnie od ustawienia pokoju; integracja pola pozostaje
osobnym zadaniem P26–P29.

Źródło: objaśnienie użytkownika w rozmowie, U-020, oraz niezmieniony
[oryginalny rzut](../dane/zrodla/materialy_uzytkownika/rzut_pokoju_sSKtLurb.jpeg).
Aktualny kontekst: [konfiguracja v2](../dane/konfiguracje/pokoj_rzut_scenariusze_v2.json).
Poprzedni kontekst: [konfiguracja v1](../dane/konfiguracje/pokoj_rzut_scenariusze_v1.json).
