# Raport 014 — weryfikacja etapu badawczego 2026-10-24

Wykonano pełny przebieg `python3 skrypty/odtworz_wszystko.py` z zachowaniem
poprzedniego stanu. Dalsza korekta opisów i metadanych nie zmieniła równań
ani wejść badawczych. Poniższe kontrole dotyczą odtwarzalności i matematyki
modeli, a nie osiągów fizycznego prototypu.

| Obszar | Wynik |
|---|---|
| Brief v0.6 | Zachowany SHA-256 `3bd9f8d43a92b96256073e66cd0f4f105336e969a37c29fc42f17cda9d66736f` |
| Dawny model bazowy | 54 kontrole przechodzą; osobne wyniki historycznej puli czterech modeli zachowane |
| Pula rozszerzona | 24 modele / 11 producentów; 12 576 scenariuszy, jawne różnice definicji X i braki danych |
| N7 dla pełnej puli | 720 stabilnych modeli stanowych; względny bilans mocy < 1e-15, zgodność odrębnego rozwiązania ruchu < 3,1e-15 |
| Granice po Vb | 288 przypadków; niezależna siatka i lokalna optymalizacja nie przewyższają wyniku analitycznego o więcej niż 2,85e-14 dB |
| Identyfikowalność | Symboliczna swoboda skalowania; 24 syntetyczne identyfikacje z dwóch Vb, błąd masy < 4,8e-15; nie są pomiarami |
| P26 | Niezależny Green 1D, kwadratura normalizacji, wzajemność, pasywność, symetria i granice relaksacji przechodzą |
| P26/P27 | 15 876 wierszy S0, 1512 diagnostycznych, 120 przypadków fazy, 48 testów koniecznych gabarytów, 72 przypadki regularizacji |
| Zbieżność modalna | 48 420 względem 124 132 modów: maksymalna różnica pary około 0,0000265 dB na sprawdzonej siatce; nie jest to błąd fizycznego pokoju |
| Kod i dane | Składnia wszystkich skryptów oraz JSON poprawna; względne odnośniki dokumentacji wskazują istniejące pliki |
| Źródła obrazowe | Obejrzano wykresy 09 i 10; oryginalny skan Scan32 oceniono wzrokowo; odrzucono automatyczne tablice odczytów wykresów |

Względem migawki `wyniki/archiwum/20261024T025748_648414` **25 wspólnych tabel
CSV odtworzyło się bajt w bajt**. Jedna tabela `p26_zbieznosc.csv` celowo się
zmieniła: rozszerzono kontrolę z kroku 1 Hz do 0,25 Hz i dopisano błąd dla pary.
Tabela regularizacji jest nowym wynikiem. Nie deklarujemy identyczności bajtów
generowanych SVG, które zawierają metadane generowania.

[Manifest](../wyniki/manifest.json) obejmuje SHA-256 wejść, kodu, wyników
oraz osobno dokumentacji. Wszystkie ścieżki i hashe należy sprawdzić po
zakończeniu zapisu raportów. Archiwa zachowują poprzednie wersje; oznaczenie
stanu roboczego nie udaje odtworzenia wejść nieistniejącego dawnego przebiegu.

Raporty [009](009_N7_straty_nieszczelnosci.md),
[010](010_szeroka_pula_i_kwalifikacja.md),
[011](011_granice_globalne_litrazu.md),
[012](012_identyfikowalnosc_i_dane_publikowane.md),
[013](013_pokoj_i_realne_gabaryty.md) wyznaczają dziedzinę tych wniosków.
Nie wykonano końcowego PDF ani wyboru zwycięzcy przed integracją nieliniowości,
termiki, konstrukcji, kleju i ochrony z pozostałą częścią programu.

Następny krok: P06 — globalna niepewność i odporność porównania pod brief.
