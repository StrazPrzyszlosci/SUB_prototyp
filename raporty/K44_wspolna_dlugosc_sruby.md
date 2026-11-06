# K44. Jedna długość śruby dla ośmiu osi

[Kalkulator](../skrypty/k43_front_pomiar.py) oblicza dopuszczalny zakres rzeczywistej długości pod łbem z [karty próby K43](../dane/k43_karta_frontu.json). Wynik dotyczy wyłącznie podanej średnicy śruby, długości części gwintowanej, faz i zmierzonego stosu z uszczelką pod dociskiem. Po zmianie typu śruby trzeba wpisać jej własne wymiary. Zakres służy do porównania z pełną tolerancją partii.

Niech a i b oznaczają gwarantowane granice pełnego gwintu w stali, T odległość od końcówki śruby do granicy pełnego gwintu przy łbie, t długość niepełnej końcówki, E wymagane efektywne zazębienie, D głębokość dna, C wymagany luz. Dla długości L część wspólna przedziałów [a,b] oraz [L−T,L−t] musi mieć długość co najmniej E. Stąd wynikają warunki:

- b−a ≥ E oraz T−t ≥ E.
- L ≥ a+E+t i L ≤ b+T−E.
- L ≤ D−C oraz L ≥ T przy zastosowanej definicji wymiaru T.
- Każdy z trzech kontrolowanych otworów musi mieć dodatni luz promieniowy względem osi gwintu.

Kalkulator przecina osiem przedziałów. Puste pole wyniku oznacza brak wspólnego rozwiązania. Może wystąpić nawet wtedy, gdy dla każdego otworu z osobna istnieje dopuszczalna długość. Pole osie_bez_rozwiazania wylicza tylko osie, które odpadają już indywidualnie.

## Przykład do sprawdzenia arytmetyki

Dla przykładowego E=4 mm, C=1 mm, T=20 mm i t=1 mm oś 2 zaczynająca pełny gwint na głębokości 34,50 mm daje dolną granicę 39,50 mm. Na osi 7 dno na głębokości 42,75 mm ogranicza długość do 41,75 mm. Pozostałe dane przykładu znajdują się w [teście](../skrypty/sprawdz_k43.py). Wspólny zakres wynosi od 39,50 do 41,75 mm. Przy założonej symetrycznej tolerancji długości ±0,20 mm przedział nominalny wynosi od 39,70 do 41,55 mm. Sprawdzono 601 długości za pomocą niezależnego porównania z bezpośrednim obliczeniem pokrycia gwintów. Wszystkie liczby w przykładzie są syntetyczne.

Próba warsztatowa wymaga jednego złożenia ośmiu osi, pomiaru przed i po sklejeniu oraz osobno uzasadnionego wymagania nośności. Podstawienie przykładowego E zamiast wyniku próby obciążeniowej nie kwalifikuje złącza. CNC HOLD.
