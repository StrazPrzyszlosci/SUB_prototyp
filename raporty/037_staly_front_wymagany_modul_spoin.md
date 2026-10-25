# Raport 037 — P19E: wymagany moduł spoin stałego frontu

Stan: 2026-10-25. **U-021: front stały, niedemontowalny, pod jeden
docelowo wybrany przetwornik.** Wykonano 12 obliczeniowych progów
sztywności. C04 pozostaje referencją geometrii; nie jest końcowym
wyborem głośnika. Regulacja objętości i porównanie kandydatów pozostają
częścią projektu.

## Co policzono i co z tego wynika

**Wynik modelu:** dla scenariusza wzrostu podatności całej ramy o 10%,
na siatce N=14, efektywny moduł warstwy 0,2 mm wynosi około **9,09 MPa**,
jeśli zmieniamy tylko cztery połączenia front–korpus. Gdy jednocześnie
zmieniamy wszystkie dwanaście spoin, próg wynosi około **72,14 MPa**.

**Rekomendacja badawcza:** dane o sztywności kleju porównywać z wymaganiem
odpowiedniej grupy połączeń, grubością warstwy i stanem utwardzenia.
Próg modułu nie jest wymaganiem wytrzymałościowym, dopuszczalnym naprężeniem
lub potwierdzeniem trwałości. D3/D4, moduł folii i nośność spoiny MDF
pozostają różnymi wielkościami.

## Dziedzina i kryteria

Użyto ramy z [P18C](035_pelna_rama_3D_spoiny_i_podparcie.md), N=10/14,
stałej geometrii i ciśnieniowego portu H. Nie zmieniano masy, materiału
płyt i ośmiu pozostałych spoin przy badaniu samego frontu.

Model warstwy ma kn=Eeff/t i ks=Eeff/[2(1+nu)t], nu=0,35 jako założenie.
Referencją jest efektywne odwzorowanie Eref=1718 MPa, t=0,2 mm.
Nie utożsamiamy go z pomiarem spoiny MDF.

Scenariusze +5/+10/+20% C są **osiami badania**, a nie zaakceptowanymi
progami briefu, zmianą SPL lub kryterium odsłuchowym. Cref jest podatnością
ramy z tą skończoną referencją spoin, nie z idealnym złączem nieskończenie
sztywnym. Wszystkie wyniki mają charakter symulacji.

## Metoda i kontrola monotoniczności

Dla wybranej grupy połączeń:

    K(beta) = Kfixed + beta*Kvariable
    Eeff = beta*Eref
    C(beta) = H^T K(beta)^+ H
    dC/dbeta = -q^T Kvariable q <= 0

H jest zrównoważone, a ruch sztywny oddzielono zgodnie z P18C.
Kvariable ma dodatnią energię skoku przemieszczeń. Dla beta>0 i stałej
geometrii otrzymujemy monotoniczny problem skalarny. Szukano w log(beta)
metodą Brenta, zamiast wybierać najbliższy punkt rzadkiej siatki modułów.

Analityczną pochodną sprawdzono odrębną różnicą skończoną przy każdym
progu; względne różnice są poniżej 9e−7. Sprawdza to rachunek w tej
rodzinie, nie identyfikuje fizycznego kleju.

## Progi efektywnego E dla warstwy 0,2 mm

| Zmieniane spoiny | Siatka | +5% C [MPa] | +10% C [MPa] | +20% C [MPa] |
|---|---:|---:|---:|---:|
|Tylko front–korpus|N=10|19,42|7,83|2,91|
|Tylko front–korpus|N=14|25,95|9,09|3,17|
|Wszystkie spoiny|N=10|160,80|67,72|27,83|
|Wszystkie spoiny|N=14|178,40|72,14|28,66|

Porównanie siatek zmienia niektóre progi nawet o około 34%. Nie są to
zatem dokładne charakterystyki materiałowe lub ścisłe minimum dla
continuum. Różnica nie jest tolerancją produkcji ani przedziałem ufności.

Referencyjny moduł folii EA9466 leży powyżej tych obliczonych wartości,
lecz **nie dowodzi to**, że rzeczywista spoina na konkretnym MDF zachowa
wymaganą sztywność, adhezję, szczelność i nośność po starzeniu.
Nie przypisano brakującego modułu PVAc z samej klasy D3/D4.

## Grubość warstwy i ograniczenia przeliczenia

Przy zachowaniu tego samego kn/ks moduł wymagany skaluje się liniowo z t.
Dla samego frontu, N=14 i scenariusza +10% C:

| Warstwa | Próg Eeff |
|---:|---:|
|50 µm|2,27 MPa|
|200 µm|9,09 MPa|
|500 µm|22,71 MPa|

To przeliczenie cienkiego interfejsu o tej samej lokalizacji i prawie
liniowym. Nie jest prawem utwardzania konkretnego produktu, instrukcją
wykonawczą lub dowodem dopuszczalnej szczeliny. Wpływ warstwy na masę,
geometrię lokalną i strefę procesu pękania jest odrębnym zagadnieniem.

![Wymagany moduł spoin stałego frontu](../wyniki/60_P19E_staly_front_i_wymagany_modul.png)

## Powiązanie z nośnością i następny krok

Zapotrzebowanie na moduł należy połączyć z obciążeniami z
[P19D](036_spoiny_3D_i_wirtualne_odspojenie.md). Duży moduł nie usuwa
koncentracji naprężeń ani nie zastępuje Gc, SN, J(t) i danych spoiny MDF.
Niezbieżnego screeningu odspojenia nie zamieniamy w potwierdzenie nośności.

**Najbliższy krok:** lokalna geometria i rozprowadzenie sił w stałym
połączeniu front–korpus, z lokalnym zagęszczeniem zamiast samego globalnego
zwiększania siatki. Wyboru jednego głośnika i finalnej obudowy nadal
wymaga synteza programu; fizyczny prototyp otrzyma jeden stały front.

[Dane 12 progów](../wyniki/p19e_wymagane_moduly_stalego_frontu.csv)
· [założenia i pochodzenie](../wyniki/p19e_wymagane_moduly_podsumowanie.json).
