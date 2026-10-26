# 29 — Podmodel i transfer obciążeń

**Własne wyprowadzenie i symulacje:** [raport 041](../raporty/041_lokalny_podmodel_i_granice_wiarygodnosci.md).

Podmodel nie otrzymuje automatycznie większej dokładności od samej liczby
węzłów. Jego pole zależy od danych na sztucznych cięciach oraz od poprawnego
przeniesienia rzeczywistych obciążeń wewnątrz wycinka.

## Zadane przemieszczenie i rzeczywista podpora

Przy podziale na współrzędne swobodne f i zadane b:

    Kff*qf = Ff - Kfb*qb
    reaction_b = (K*q-F)_b

Na fizycznych powierzchniach pozostają ciśnienie, ciężar i inne obciążenia.
Jeżeli wycinek przecina łaty stóp, trzeba przenieść odpowiedni fragment
siły. P19G używa znanych trakcji globalnych; nie dodaje ich drugi raz
jako nowych sprężyn. Pominięte sprzężenie zwrotne wymaga własnej oceny.

Siły stóp liczymy względem nieruchomego otoczenia **przed** usunięciem
wspólnego ruchu sztywnego. Do samego rozwiązania sprężystości można potem
usunąć ten ruch z warunków brzegowych, aby ograniczyć odejmowanie dużych liczb.
Naprężenia liniowe powinny pozostać niezmienne; to odrębna kontrola transferu.

## Co porównujemy

Miary lokalne wymagają stałego obszaru obserwacji. Zmiana całej powierzchni
podmodelu wraz z domeną zmieniałaby jednocześnie badane pole i definicję RMS.
P19G zachowuje okno x=92–108 mm, pełny pas i osobne odcięcie 5 mm.
To odcięcie jest diagnostyczne, nie materiałową długością krytyczną.

Trzeba oddzielić wpływ kroku y/z, podziału wzdłuż x, odległości cięcia
i rozdzielczości modelu źródłowego. Osobne dwa zagęszczenia nie dowodzą
całkowitego błędu wspólnej siatki. Pole globalne może ograniczać wynik
silniej niż ostatnie lokalne zagęszczenie.

## Brak dodatniej części nie dowodzi bezpieczeństwa

RMS dodatniej części rozciągania może przejść przez zero przy niewielkiej
zmianie siatki lub danych brzegowych. Wtedy względny błąd jest złą miarą:
zapisujemy także zmianę bezwzględną, ścinanie, ściskanie i definicję okna.
Nie przenosimy klasyfikacji z jednego okna na całą spoinę.

Dokładny bilans pracy i reszta liniowego solvera nie identyfikują Gc,
pełzania, zmęczenia lub adhezji. Zakończenie rodziny obliczeń i kwalifikacja
rzeczywistego połączenia są odrębnymi etapami projektu.
