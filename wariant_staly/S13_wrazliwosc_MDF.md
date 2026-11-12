# S13. Kontrola wplywu konkretnego MDF na modele drgan

Nie ma fizycznego MES zwalidowanego pomiarami. Ta notatka pokazuje tylko policzalną wrazliwosc izolowanej tylnej plyty, zachowujac zalozenia brzegowe S03 i umowna gestosc 800 kg/m3.

S03 przy E=2000 MPa i grubosci22 mm: tył wariantu A przy 1 kPa, utwierdzenie daje 0,043 mm odksztalcenia. Oddzielny model plyty przegubowo podpartej daje f1 ok. 117 Hz. Z karty referencyjnego EGGER (>19-30mm) uzyskujemy E srednie 2100 MPa, tolerancje nominalnej grubosci 22±0,3 mm. Skalowanie Kirchhoffa dla tej samej rozpiętości i podpór:
- ugiecie ~ 1/(E*t^3), przy zachowanym obciazeniu;
- czestotliwosc wlasna ~ t*sqrt(E/rho), przy stalym rho i wspolczynniku Poissona.

Przy E=2100 MPa i t=21,7..22,3 mm, nominalna prognoza ugiecia utwierdzonej plyty to 0,04267..0,03932 mm. Skladowa f1 w osobnym przypadku przegubowym wynosi 118,25..121,52 Hz. To dwie rozne konfiguracje warunkow brzegowych, nie jeden wspolny model! Nie wolno zestawiac ich z mierzonymi rezonansami gotowej skrzyni.

Brak charakterystycznego dolnego E, rozrzutu gestosci, zespolonej sztywnosci spoin, rzeczywistych warunkow podpór i podatnosci zabudowy. E=2100 MPa jest srednia z karty konkretnego gatunku, a nie gwarantowana najgorsza wartoscia. Sama siatka S02 zmieniala podatnosc A o okolo 18% pomiedzy 45 i 30 mm; jej niezalezne zageszczenie i porownanie z powłoką plytową pozostaje wazniejsze niz poprawa jednej liczby E. Żadnego wynikowego statusu CNC nie zmieniono.

Zadanie mechaniczne M5: ponownie policzyc pelny korpus z polaczeniami i rzeczywistym MDF, po otwarciu danych pomiarowych, i sprawdzic dwie orientacje stóp oraz mody w zabudowie meblowej.
