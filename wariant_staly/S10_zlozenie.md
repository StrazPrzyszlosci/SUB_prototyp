# S10. Jeden model złożeniowy CAD stałej skrzyni A 102 l

Wynik: pierwsza wspólna parametryczna reprezentacja korpusu A, obejmująca FR1/FR2, tył, boki, dno, górę, wręgę, otwór przetwornika i próbny stalowy pierścień. Model w OpenSCAD: [S10_korpus_A_102L_NIE_CNC.scad](S10_korpus_A_102L_NIE_CNC.scad). Jest to REPREZENTACJA KONCEPCYJNA, nie dokumentacja do cięcia lub frezowania.

Pochodzenie wymiarów: S06 (816,8 x 473,3 x 394 mm, front 2x22 mm, światło komory 772,8 x 429,3 x 328 mm, wręga 772,6 x 429,1 mm i okno 712,6 x 369,1 mm R3); S07 (oś X408,4/Z236,65; otwór Ø355,8; od końca pełnej obwiedni osiowej 178 mm do wręgi 19 mm); K42 (pierścień Ø400/358 x 6 mm i próbna kieszeń Ø400,4 x 6,2 mm).

Model jest wykonany w jednym współrzędnym układzie X - prawo, Y - głąb, Z - góra. Opcja show_pair pokazuje dwa identyczne moduły bez odbijania konstrukcji. Opcja show_driver_envelope wyświetla zastępczą niebieską bryłę Ø355,8 x 178 mm. To świadomie uproszczona obwiednia, NIE rzeczywista geometria żeber i zacisków kosza. Nie wolno z jej widoku wnioskować o możliwości wsunięcia głośnika. S07 nadal wymaga pomiaru promienia przejścia przez trzy warstwy.

Opcjonalna pomarańczowa obwiednia złącza jest makietą S05 70 x 80 x 72 mm umieszczoną na prawym boku; nie zawiera prawdziwego otworu w MDF, przepustu szczelnego ani łączników. Model nie wyznacza śrub pierścienia, baz wiercenia, faz, pełnej powierzchni kleju, okleiny, stop, kasety maskownicy, wentylacji, toru przewodu ani fizycznych tolerancji. Elementy te są bramkami M1-M5 z S09.

Kontrola automatyczna: python wariant_staly/sprawdz_s10.py. Weryfikuje wszystkie kluczowe stałe CAD względem S06 i osiową odległość od wręgi według S07. Nie zastępuje walidacji bryłowej w rzeczywistym narzędziu, kontroli ruchu ani CAM.

Dalsze zadanie: po zwymiarowaniu osprzętu i doborze rzeczywistego pasowania wręgi zastąpić makiety sprawdzonymi komponentami, przeprowadzić niezależny test kolizji narzędzia/kosza/terminala i dopiero po zaliczeniu bramek zlecić próbne elementy. Obowiązuje CNC HOLD.
