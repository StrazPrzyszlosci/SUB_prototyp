# P40 — projekt testów mocowania Dayton: badania konieczne przed decyzją CNC

**1 listopada 2026 — lista eksperymentów i danych do pozyskania.** Ten plik **nie zawiera wyników pomiarów**.

## Krytyczne ryzyko ujawnione w P40A/B

Przy hipotetycznym 15kg×5g, e=120mm, osiem równomiernie działających połączeń ma w modelu rozkładu grupy śrub do **151 N** reakcji wypadkowej na punkt. Nie wyznacza to nośności ani bezpieczeństwa śruby; przy rzeczywistym kontakcie, tarciu, wstępnym ścisku i odrywaniach siły mogą być inne.

Pierścień współosiowy wokół wycięcia Ø355,8 z otworami na BCD Ø368 przy otworze Ø6,5 dzieli **tylko 2,85mm** na luz do wycięcia i pas metalu. Scenariusz badawczy wymagający jednocześnie ≥1mm luzu i ≥2mm metalu jest **niemożliwy w tej geometrii**, niezależnie od OD i grubości zwykłego annular backera.

## Alternatywy do badania, NIE zatwierdzone rozwiązania

| Koncepcja R&D | Idea ścieżki sił | Co może rozwiązywać | Nowe ryzyko |
|---|---|---|---|
| A. Szeroki sztywny *carrier* poza otworem kosza | 8 połączeń do nowego elementu ramowego, następnie dodatkowe mocowania rozłożone na większej powierzchni MDF lub bezpośrednio do wręg | Ograniczenie punktowego obciążenia w wąskim pasie 2,85mm | Kolizje z koszem, złączami i wręgami; dostęp dla narzędzi; odwrócenie obciążeń; szczelność |
| B. Dwie / cztery *belki przenoszące* zamiast cienkiej obręczy | Rozprowadzenie sił do stref MDF odległych od krawędzi wycięcia i do struktury obudowy | Potencjalnie usuwa wymaganie ciągłego pasma metalu przy wszystkich 8 otworach | Znaczne miejscowe ugięcia, masa, nieznane punkty zaczepienia, asymetryczne naprężenia |
| C. Zmieniony układ frontu i mocowania | Modyfikacja frontu, osadzenia albo dobór głośnika o korzystniejszym interfejsie mechanicznym | Ograniczenie kompromisu kołnierz–otwór–śruby | Wymaga nowego bilansu objętości, stanu DSP, masy i kosztów |

**Nie wybierać spośród A/B/C bez realnych wymiarów kosza/śrub i badania sztywności złączy.** Sam pierścień blachy nie jest automatcznie wzmocnieniem naciąganej części MDF.

## Protokół próbek (minimum)

1. Rzeczywisty kosz lub dokładny szablon producenta: odnotować współrzędne i kierunek wszystkich 8 otworów, rozmiar nakrętek i główek, miejsce gniazd przewodów, maksymalny promień kosza na 0–178 mm od płaszczyzny frontu.
2. Trzy lub więcej reprezentatywnych próbek każdego *rzeczywiście wybranego typu złącza*, wykonanych z docelowego MDF44mm, z identycznym klejem, wkładką, otworem i warunkami utwardzania.
3. Wykonać co najmniej dwa **niezależne rodzaje próby**: **siła poprzeczna–przemieszczenie** oraz **siła odrywająca–przemieszczenie** przy znanej geometrii i kontrolowanej prędkości. Rejestrować trwałe odkształcenie, obszar zniszczenia, lokalne pęknięcia MDF, wpływ cyklu montaż/demontaż.
4. Oddzielna próba skręcenia/obrotu połączenia z rzeczywistą parą moment–kąt. Siła z P40A nie może być bezpośrednio użyta jako dopuszczalna siła śruby.
5. Rozważyć próbę zmęczeniową, zmianę wilgotności i temperatury, pełzanie i szczelność złącza. Liczbę cykli i poziom obciążeń ustalić na podstawie założeń użytkowych, nie z modelu 5g jako „wymagania”.
6. Dopiero wtedy zaimportować pomiary do kontaktowego MES **z rzeczywistą bryłą kosza i jego kołnierza**; odtworzyć rozkład na 8 złączy i naprężenia w MDF, zbieżność siatki oraz warianty transportu/pion-poziom. Porównać z pomiarem jednej próbnej sztuki.

## Minimalne pola danych do zapisania

ID próbki; data; partia MDF i wilgotność; grubość/długość/szerokość; rodzaj śruby/tulei/nakrętki; średnice zewnętrzne i wewnętrzne; faza/wysokość kołnierza; grubość blachy/pierścienia; położenie i tolerancje; moment montażu; siła N; przemieszczenie mm; moment Nm; obrót rad; zniszczenie i miejsce pęknięcia; zdjęcia; liczba cykli.

**Brak rzeczywistych prób oznacza, że nie można wyznaczyć sensownych współczynników bezpieczeństwa dla MDF, metalu ani śrub.** CAD i wyniki P40 służą do przygotowania tych prób, nie do ich zastąpienia.

## Status i następne wyjście

Zaakceptowane: analityczne P40A/B jako **modele wstępne do porównania scenariuszy**.

NIEzaakceptowane: nośność przy 5g/10g, dobór konkretnej śruby, gabaryt główki i tolerancje producenta, bezpieczeństwo transportu, szczelność oraz frezowanie finalnego MDF. Najbliższy krok to **precyzyjny pomiar rzeczywistego interfejsu kosza i przygotowanie 2 niezależnych wariantów kontaktowego CAD**, bez nowych nieuzasadnionych założeń materiałowych.
