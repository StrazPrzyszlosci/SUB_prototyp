# Raport 011 — globalne granice po objętości bez sztucznego limitu

Stan:2026-10-24. Zakres: model liniowy, jeden sinus, stałe limityV/I/X,
idealne 2π/1 m. Nie jest to optymalizacja całego pasma, muzyki, termiki i konstrukcji.

## Wyprowadzenie

Niech `B=BL`, `Ks=1/Cms`, `Kb=rho*c²*Sd²/Vb`, `kappa=Ks+Kb−Mms*omega²`.
Zmienna `kappa` jest ograniczona od dołu przez `kappa0=Ks−Mms*omega²`.
Przy fazorach RMS i stałej indukcyjności Le:

```text
A = Re²+(omega*Le)²
B2 = 2*omega²*Le*B²
C0 = omega⁴*Le²*Rms²+omega²*(Re*Rms+B²)²
den² = A*kappa²+B2*kappa+C0
vV = Vmax*B*omega/sqrt(den²)
vI = Imax*B*omega/sqrt(kappa²+(omega*Rms)²)
vX = omega*Xpeak/sqrt(2)
v_available = min(vV,vI,vX)
```

Kandydaci maksimum: dolna granica `kappa0`, stacjonarne punkty `vV` i `vI`,
przecięcia ich krzywych. Przy `kappa→∞` oba ograniczenia elektryczne dążą
do zera. Ograniczenie X może tworzyć plateau; nie zmienia kompletności
zbioru kandydatów na maksymalną wartość. Objętość wynika z
`Vb=rho*c²*Sd²/(kappa-kappa0)`. Granica `kappa=kappa0` odpowiada `Vb→∞`.

Wyznaczono też przedziałVb osiągający wynik niegorszy niż 0.5 dB poniżej
granicy: nierówności `vV>=vcel` i `vI>=vcel` są kwadratowymi nierównościami
przedziałowymi w zmiennej `kappa`. To próg scenariusza, nie zatwierdzona specyfikacja.

## Kontrole i dziedzina wniosku

Sprawdzono symbolicznie rozwinięcie mianownika i punkt stacjonarny.
Policzono 288 przypadki: wszystkie modele puli,6 pasm i 2 napędy.
Odrębna ocena w modelu bazowym:1200 objętości 0.01–10^7 l oraz lokalna
optymalizacja numeryczna. Maksymalne przewyższenie granicyanalitycznej
przez wynik numeryczny: 2.84e-14dB.
Sprawdzono takżeLe=0 i zdegenerowane przecięcie dlaVmax=Re*Imax.

To kontrola algebry i obliczeń zmiennoprzecinkowych, nie końcowe obudowy
ani przedziałowa certyfikacja wszystkich błędów zaokrągleń.

## Przykład 20 Hz: nie więcej niż 0.5 dB poniżej granicy

| Model |Vmax [Vrms]|GranicaSPL RMS [dB]|MinimalneVb w tym scenariuszu [l]|
|---|---:|---:|---:|
| Dayton RSS390HF-4 |40|101.89|53.5|
| Dayton RSS390HF-4 |60|101.89|32.5|
| STX W.32.800.8.FCX |40|97.93|39.7|
| STX W.32.800.8.FCX |60|97.93|21.7|
| Dayton RSS390HE-22 seria |40|102.76|379.1|
| Dayton RSS390HE-22 seria |60|106.28|379.1|
| Dayton UMII12-22 seria |40|101.50|352.5|
| Dayton UMII12-22 seria |60|101.89|53.3|
| Dayton UMII15-22 seria |40|104.11|753.2|
| Dayton UMII15-22 seria |60|106.15|204.7|

Nie jest to „minimalna bezpieczna skrzynia”. Inne częstotliwości,EQ,THD,
termika, masa i panele mogą wymagać innego wyboru. Duże wartości pokazują
koszt dążenia do granicy jednego punktu 20 Hz, a nie obowiązek budowy ogromnej
skrzyni.100/150 l nie przyjęto jako odgórnego limitu briefu.

Analogicznie minimum F3 samo w sobie nie wybiera prototypu. Dla modelu 2.rzędu
minimalizacja poVb, gdyQts<1/sqrt(2), dajeQtc=1/sqrt(2). Dla UMII15-22
takie kryterium prowadzi do około 5 m³ z powoduQts bliskiego 0.707; nie jest
to rekomendacja konstrukcyjna. Wybór wymaga połączenia całego briefu.

Kod:[granice_litrazu.py](../skrypty/granice_litrazu.py),
[eksperyment](../skrypty/analiza_granic_litrazu.py).
Wyniki:[CSV](../wyniki/pula_granice_globalne_Vb.csv),
[JSON](../wyniki/pula_granice_globalne_Vb.json).
