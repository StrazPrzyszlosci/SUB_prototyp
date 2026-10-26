# 26 — Dwie cewki: połączenie, ograniczenia i porównywanie SB

**Model liniowy i wyprowadzenie**, nie identyfikacja konkretnego motoru.
Przykład i źródła: [raport 038](../raporty/038_SB_Acoustics_rozszerzenie_i_porownanie.md).

## Ten sam produkt może wymagać dwóch porównań napędu

Przy identycznych cewkach zasilanych zgodnie w fazie, w liniowym modelu
tej samej gałęzi ruchowej, port szeregowy ma względem równoległego:

    Re_series = 4*Re_parallel
    Le_series = 4*Le_parallel
    BL_series = 2*BL_parallel
    Qes_series = Qes_parallel

Współzależność magnetyczna nie znosi współczynnika 4 dla idealnie
symetrycznej macierzy indukcyjności w tych dwóch połączeniach. Przy tym
samym ruchu U_series=2*U_parallel, I_series=I_parallel/2 i moc obu cewek
łącznie jest taka sama. Nie dotyczy to połączenia przeciwfazowego,
uszkodzenia jednej cewki, dowolnej asymetrii lub niezgodnych wzmacniaczy.

**Dane producenta C26** podają Le 1,4/6,1 mH, co nie spełnia dokładnie
tej transformacji. Zachowujemy oba wpisy; nie wyprowadzamy z nich jednej
dokładnej macierzy cewek. Hipotezy o warunkach pomiaru/zaokrągleniach
wymagałyby danych, których nie ma. Katalogowe BL 9,7/19,5 Tm jest odrębnym
zaokrąglonym wpisem; model używa BL wyprowadzonego ze spójnego zestawu T/S.

## Wspólne U i I mogą zmienić kolejność

Przy stałym limicie napięcia połączenie szeregowe może ograniczyć ruch
wcześniej. Przy stałym limicie prądu ograniczenie może wcześniej pojawić
się w równoległym. Impedancja zależy od częstotliwości i obudowy, więc
nie zastępujemy jej samą impedancją nominalną. Dopuszczalny wzmacniacz do
1,5 Ω nie wynika ze stwierdzenia „moduł klasy D”.

Przy granicy samego ruchu:

    p_RMS = rho*omega²*Sd*Xpeak/(solid_angle*r*sqrt(2))

Ten pułap nie wzrasta od przełączenia cewek lub dalszego zwiększania Vb.
Wymagane U/I mogą się zmienić. Wspólne Sd·Xmax nie dowodzi jednak takiego
samego THD, chłodzenia, obciążenia membrany lub niezawodności.

## Dane, których nie wolno dopisać

Moc oznaczona w PDF jako „ser.” nie staje się automatycznie potwierdzonym
limitem parallel. Ogólna klasa IEC bez protokołu i identyfikacji chłodzenia
nie określa temperatury w danym sygnale. W obliczeniach 038 nie użyto Pe
jako limitu; model nie potwierdza żadnego dopuszczalnego czasu pracy.

Rozbieżność C25 między 22 a 22,5 mm p-p zachowujemy jako konflikt źródeł,
a nie tolerancję populacji. Geometryczny skok peak powstaje przez podzielenie
p-p przez 2; nie przez sqrt(2). RMS dotyczy dalej konkretnego sinusa.

Historyczny zbiór 24 modeli oraz nowe dwa produkty są różnymi wejściami.
Wynik nieliniowy starej bazy C04 nie przechodzi na C25/C26. Tak samo relacja
właściciela o bass-reflexie nie identyfikuje jakości obudowy zamkniętej.
