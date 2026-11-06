# Front próbny pod Dayton RSS390HF-4

Zakres zlecenia próbnego: dwie płyty MDF i jeden stalowy pierścień dla jednego frontu. Wymiary w mm, DXF 1:1. Próba wymaga osobnych egzemplarzy głośnika, śrub, podkładek, uszczelki i kołków. CNC HOLD dla obudowy docelowej.

## Karta ustawienia CAM

| Detal | Półfabrykat nominalny | Operacje na wskazanej stronie |
|---|---|---|
| FR1 | MDF 22, format gotowy 1080 × 500 | Od frontu. Osiem przelotów Ø5,6, otwór kosza Ø355,8, obrys zewnętrzny. |
| FR2 | MDF 22, format gotowy 1080 × 500 | Od strony FR1. Kieszeń Ø400,4 na 6,20 od powierzchni. Na jej dnie osiem ulg Ø6,5 i dwa gniazda Ø4,2. Otwór kosza Ø355,8 przelotowo. |
| STAL_6 | Stal 6, pierścień Ø400/358 | Osiem gwintów przelotowych M5×0,8 na Ø368. Dwa otwory nominalne Ø4 na Ø388 pod kołki. Ustalić sposób osadzenia kołków przed wykonaniem tych dwóch otworów. |

Przy zerze Z na powierzchni FR2 końcowe rzędne wynoszą −6,20 dla dna kieszeni, −10,20 dla dna ulg śrub i −11,20 dla dna gniazd kołków. Wymiary odnoszą się do płaskiego dna. Jeśli warsztat używa wiertła ze stożkiem, trzeba osobno sprawdzić dostępną głębokość cylindryczną i najgłębszy punkt narzędzia. Nominalne Ø5 na warstwie GWINT_M5x0_8_NOM oznacza gwint. Średnicę otworu pod gwint dobrać do technologii gwintowania.

Widok obu płyt od strony zewnętrznej obudowy, środek X231/Z250 liczony od lewego dolnego narożnika płyty w tym widoku. Oś 1 leży w prawo od środka. Płyty i pierścień oznaczyć wspólnym kierunkiem przed montażem. W pliku DXF pierścienia środek również jest w punkcie 231/250. Po przesunięciu detalu w CAM wszystkie operacje muszą korzystać z tego samego przesunięcia.

## Kolejność próby

1. Przejrzeć CAM z wykonawcą, uzgodnić narzędzia, mocowanie półfabrykatów, pasowanie kołków i sposób pomiaru. Zapisać faktyczne grubości i wykonać detale próbne.
2. Ułożyć pierścień w kieszeni FR2, sprawdzić pełne oparcie i położenie kołków. Złożyć z FR1, koszem i uszczelką. Przed klejeniem sprawdzić ręczne wkręcenie ośmiu śrub w jednym ustawieniu.
3. Skopiować plik dane/k43_karta_frontu.json jako karta_proby.json. Wykonać pomiary według raportu K43. Do wpisania wymaganego zazębienia potrzebna jest podstawa nośności wybranego złącza. Pozostawić pole puste, jeżeli ta wartość oczekuje na próbę obciążeniową.
4. Z katalogu rozpakowanego archiwum uruchomić polecenie poniżej. Python 3 wystarcza. Wynik dotyczy geometrii. Po klejeniu powtórzyć pomiary i osobno sprawdzić utrzymanie docisku uszczelki, szczelność i stan MDF.

```
python3 skrypty/k43_front_pomiar.py karta_proby.json
```

W archiwum START.md leży w katalogu głównym. Katalog dokumentacja/cnc/K42_PROBA_HOLD zawiera trzy DXF. W katalogu raporty znajdują się obliczenia i procedura K42 do K44. Polecenie python3 skrypty/sprawdz_k43.py uruchamia sprawdzenie na danych syntetycznych.
