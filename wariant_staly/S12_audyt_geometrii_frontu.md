# S12. Audyt wspolnej geometrii frontu i przylacza na danych katalogowych

Do policzenia: python wariant_staly/s11_s14.py. Wyniki sa wyliczane ze zrodel S11, nominalnych formatow S06 i wariantu probnego pierścienia K42; NIE sa to rysunki CNC.

Wspolny front 816,8 x 473,3 mm; otwor głośnika Ø355,8 mm, pokrycie kosza Ø388,4 mm. Najmniejszy nominalny margines zewnetrzny kołnierza to 42,45 mm, a kieszeni stalowego pierścienia Ø400,4 mm - 36,45 mm od krawedzi frontu. Przy PCD Ø368 mm i wstepnym otworze FR1 Ø5,6 mm pozostaje JEDYNIE 3,30 mm mostka MDF miedzy wycieciem Ø355,8 a krawedzia otworu. To jest geometria, nie udowodniona nośność. Stalowy pierścień pozostaje bramka M3.

Kieszen Ø400,4 i glebokosc 6,2 mm, przy 6 mm pierścieniu, zostawia nominalnie 0,2 mm osiowej roznicy. Dla EGGER 22±0,3 minimalna grubosc FR2 pod kieszenia (bez uwzglednienia tolerancji samego frezowania) wynosi 15,5 mm. Dodatkowe modelowe pogłebienie 4 mm pod trzpien daje 11,5 mm. Obie liczby musza byc przeliczone z rzeczywistymi pomiarami oraz naddatkami CNC.

Nominalna powierzchnia FR1/FR2 jest 0,386591 m², a poza kieszenia Ø400,4 wynosi ok. 0,260676 m². KLEIBERIT 303.0 100-130 g/m² dla klejenia powierzchniowego daje 26,1-33,9 g produktu na jedna parę FR1/FR2 i 52,1-67,8 g dla dwoch frontow. To WYŁĄCZNIE szacunek zuzycia na MDF-MDF poza kieszenia, NIE instrukcja ani certyfikat spoiny, bez kleju do kontaktu stalowego i bez strat technologicznych. Orientacyjny docisk dla lameli 0,7-1 N/mm² nie jest automatycznie wymaganiem dla tego laminatu.

Przymiarka wspornika S05 70 x 72 mm: nominalnie 9,6 mm od kolnierza Ø50,8 do krawedzi poziomej wspornika i 10,6 mm pionowo. Dla czterech otworow ≥Ø3,2 mm w kwadracie 29,2 mm minimalny nominalny mostek z otworu do krawedzi wspornika wynosi 18,8 mm poziomo i 19,8 mm pionowo. Wyciecie minimum Ø24 jest otworem SAMEGO wspornika pod gniazdo; nie wolno przenosic go automatycznie na boczny MDF 22. S05 przewiduje ODDZIELNY szczelny przepust do komory. Wspornik, położenie otworu MDF, przepust, uszczelka, sztywność mocowań i wygoda operowania wtykiem nie sa jeszcze zwymiarowane.

Wniosek: dopasowanie plaskiego kolnierza i ramki jest NOMINALNIE mozliwe, ale ostroznosc wymaga krytycznych testów 3D, zwłaszcza mostka frontu, wchodzenia kosza, docisku i szczelnosci. Nie ma tu uzasadnienia do automatycznego wydania DXF.
