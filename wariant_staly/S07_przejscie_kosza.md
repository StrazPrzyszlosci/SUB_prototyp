# S07. Przejście Daytona przez front i odstęp od wręgi

Rekomendacja dla stałej skrzyni A: zachować wręgę w przedziale Y = 197 do 219 mm. Przy prostym wsuwaniu głośnika od przodu najgłębsze położenie osiąga się przy jego osadzeniu. Nawet licząc pełne katalogowe 178 mm w głąb od zewnętrznej powierzchni FR1, kosz kończy się 19 mm przed pierwszą płaszczyzną wręgi. Wniosek dotyczy geometrii osiowej, płaskiego montażu bez zagłębienia i samego przetwornika. Zaciski z przewodem trzeba sprawdzić w wybranym położeniu kątowym.

## Wymiary i bazy

Rysunek dla RSS390HF-4, nr 295-468, podaje kołnierz Ø388,4 mm, wymiar montażowy Ø355,8 mm, osiem otworów Ø6,5 mm na okręgu Ø368 mm, 10,5 mm dla kołnierza i 178 mm głębokości. Dane sprawdzono 6 listopada 2026 w indeksowanej karcie i jej kopii dystrybutora. Bezpośrednie wyświetlenie pliku na serwerze Dayton było w tej sesji blokowane. [Karta Dayton Audio](https://www.daytonaudio.com/images/resources/295-468-dayton-audio-rss390hf-4-specifications-46176.pdf) · [kopia tej samej karty](https://www.parts-express.com/pedocs/specs/295-468-dayton-audio-rss390hf-4-specifications-46176.pdf) · [wcześniejsza analiza rysunku](../raporty/096_P38A_front_Dayton_otwory_i_mocowania.md).

| Kontrola w nominalnym korpusie S06 | Wynik |
|---|---:|
| Środek głośnika, X/Z od lewego dolnego narożnika frontu | 408,40 / 236,65 mm |
| Od kołnierza do najbliższej krawędzi frontu | 42,45 mm |
| Od końca obwiedni 178 mm do pierwszej płaszczyzny wręgi | 19,0 mm |
| Od tej samej obwiedni do wewnętrznej strony tyłu | 194,0 mm |
| Od końca obwiedni do wręgi przy odliczeniu kołnierza 10,5 mm jak w P38A | 29,5 mm |
| Promieniowa różnica między otworem pierścienia Ø358 a otworem płyt Ø355,8 | 1,10 mm |
| Promieniowa nadwyżka krótszego wymiaru okna wręgi 369,1 mm względem Ø355,8 przy współosiowości | 6,65 mm |

Wartości 19 i 29,5 mm pokazują dwa sposoby odniesienia wymiaru do płaszczyzny frontu. Rezerwy 19 mm użyto do decyzji o położeniu wręgi. W razie późniejszego wpuszczenia kosza każde 1 mm zagłębienia zużywa 1 mm tej rezerwy. Środek wręgi jest otwarty. Odstęp osiowy od jej płaszczyzny sam w sobie nie określa wentylacji magnesu. Kontrolę otworu i uszczelki trzeba wykonać niezależnie od tego bilansu.

## Co faktycznie przejdzie przez front 44 mm

Otwór projektowy Ø355,8 w obu płytach odpowiada wymiarowi katalogowemu. Odejmowanie od niego tej samej liczby jako rzekomo zmierzonej średnicy kosza nie wyznacza fizycznego luzu. Podczas wsuwania i wyjmowania kolejne przekroje żeber, zacisków i przewodów przechodzą przez dwa otwory oraz strefę pierścienia. Uwzględnić także ślad przewodu podczas odpinania po wysunięciu.

[Karta wejściowa](s07_karta.json) służy jednemu egzemplarzowi i jednemu złożonemu frontowi. Do kopii wpisać identyfikator zestawu. Wszystkie wartości są w mm. Dla każdej warstwy podać dolne ograniczenie średnicy koła wpisanego w rzeczywisty otwór na całej jego głębokości oraz górne ograniczenie odsunięcia środka tego koła od wspólnej osi. Promień obwiedni głośnika to największa odległość od osi do części, która musi przejść przez front, razem z podłączonym przewodem w przewidzianym ułożeniu. Kołnierz opiera się na FR1 i pozostaje na zewnątrz. Pomiar samej średnicy magnesu lub rozstawu żeber w jednym przekroju nie wystarcza. Wymiary graniczne muszą już uwzględniać niepewność pomiaru.

Dla każdej warstwy kalkulator od promienia koła wpisanego odejmuje błąd osi, promień obwiedni, maksymalny błąd prowadzenia i wymagany dodatni luz roboczy. Błąd prowadzenia musi obejmować dodatkowy promieniowy zasięg od odchylenia kosza na całym torze. Wynik nieujemny we wszystkich warstwach spełnia wystarczający warunek promieniowy. Ujemny kieruje do dokładniejszej próby ustawienia lub korekty. Nie rozstrzyga o kolizji nieregularnych kształtów przy konkretnym kącie obrotu.

Odtworzenie ze wzorem karty: `python wariant_staly/s07.py`. Po wpisaniu pomiarów: `python wariant_staly/s07.py --karta karta_egzemplarza.json`. Puste pola dają status braku pomiarów. Regresja obejmuje pustą kartę, dokładnie wyczerpany wymagany zapas i niezależny błąd osi FR2 dający niedobór 0,01 mm. Liczby testowe są syntetyczne.

## Decyzja przed CNC

Pozostawić nominalną średnicę Ø355,8 do próby oraz zachować środek i pozycję wręgi S06. Na zestawie FR1/FR2 z pierścieniem sprawdzić wsunięcie i wyjęcie przetwornika przy docelowej fazie otworów, z podpartym koszem i podłączonym przewodem. Przy lokalnej kolizji oznaczyć konkretną warstwę i pozycję kątową przed zmianą obrysu. Każde powiększenie średnicy o 1 mm zmniejsza nominalny mostek MDF między otworem kosza a otworem śruby o 0,5 mm. O kwalifikacji frontu decydują łącznie przejście kosza, rejestracja ośmiu śrub, nośność i szczelność. [S03, próba frontu](S03_karta_proby_frontu.md) · [S06, geometria korpusu](S06_plyty.md).
