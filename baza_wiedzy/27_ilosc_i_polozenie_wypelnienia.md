# 27 — Ilość i położenie wypełnienia

**Własny model/obliczenie.** Dane i ograniczenia:
[raport 039](../raporty/039_wypelnienie_ilosc_polozenie_i_straty.md).

Materiał porowaty opisują co najmniej: obszar i grubość, masa sucha,
porowatość otwarta, właściwości przepływowe/cieplne oraz mocowanie szkieletu.
Sztywne wkłady do regulacji objętości to osobny element konstrukcji.

## Trzy objętości i masa

Vporous jest obrysem materiału wraz z porami. Przy otwartych porach
dostępnych dla ciśnienia komory:

    Vsolid = (1-phi)*Vporous
    Vgas = Vfree + phi*Vporous
    mdry = rho_bulk_dry*Vporous

Odejmowanie całego obrysu maty od objętości gazu dawałoby inny model,
jak dla szczelnego wkładu. Z kolei dodanie bonusu Veq do Vgas i ponowne
odjęcie tych samych włókien liczyłoby ich wpływ dwukrotnie.

Masa/gęstość nie identyfikuje porów. Gęstość zwiększona przez zagęszczanie
konkretnego materiału może zmienić phi, oporność przepływu i szkielet;
nie jest tym samym co niezależna zmiana jednego parametru w stresie.

## Podatność jest funkcją częstotliwości

Gdy ciśnienie jest wspólne, podatności regionów sumują się:

    C(f) = Vfree/Kfree(f) + Vporous/Kporous(f)
    Veq(f) = gamma*p0*C(f)

Tylko po zadaniu warunków cieplnych poszczególnych regionów można podać
granicę. Adiabatyczny rdzeń z izotermicznymi porami daje inny koniec niż
izotermiczna cała masa gazu. Skończone Cs i nieznane Hgs nie ustalają
od razu wartości C przy 20 Hz. Sorpcja pozostaje osobnym mechanizmem.

## Ułożenie wpływa na straty

Przy propagacji 1D:

    dp/dx = -s*rho_eq*Q/A
    dQ/dx = -s*A*p/K_eq

Strata zależy od lokalnego przepływu i ciśnienia, więc równa masa w trzech
położeniach nie musi dawać równego Zin. Porównanie 039 sprawdza tę
zależność również niezależną siecią FV. Model warstwy przez cały przekrój
nie jest równoważny z wyklejeniem tylko boków. Powiązanie prawdziwego
układu mat z przestrzennym polem wymaga P21.

Większe Re(Zin) lub mniejszy pik rezonansu nie rozstrzyga całej jakości.
Należy równocześnie policzyć ruch membrany, napięcie, prąd, straty cewki,
ochronę, pasmo i wpływ na regulację Vb. Przy aktywnym limicie Sd·Xmax
materiał nie tworzy dodatkowego skoku objętościowego.
