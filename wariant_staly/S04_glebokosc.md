# S04. Jak zmieścić kompletny moduł A w głębokości 450 mm

Wybrać do przymiarki wyjście przewodu przez prawy bok patrząc od przodu. Korpus zachowuje nominalne 816,8 × 473,3 × 394 mm z dokładniejszych danych S01. Po obrocie do pozycji wysokiej bok ze złączem ma znaleźć się na górze. Przy ustawieniu niskim dostęp do tego boku musi zapewniać sąsiednia komora serwisowa. Oba identyczne moduły wymagają takiego dostępu. Układ korpusu i wręgi ma nadal bilans nominalny 102 l z dotychczasowym szacunkowym odjęciem 0,175 l na terminal.

## Przewód i gniazdo

Do makiety przyjęto gniazdo Neutrik NL4MPRXX, wtyk NL4FXX-W-S i przewód Sommer Meridian Mobile SP225 425-0051, Ø7,8 mm, 2 × 2,5 mm². Przewód mieści się w zakresie uchwytu 6 do 12 mm. Z rysunków przyjęto kołnierz gniazda Ø50,8 mm i maksymalną długość całego wtyku 82,5 mm. Rozpatrywane połączenie dotyczy wyjścia wzmacniacza do głośnika. Źródła producentów sprawdzone 6 listopada 2026: [gniazdo i rysunek](https://www.neutrik.com/en/product/nl4mprxx), [wtyk](https://www.neutrik.com/en/product/nl4fxx-w-s), [rysunek wtyku](https://www.neutrik.com/media/19738/download/Drawing%20NL4FXX-W-S-50%20%28PDF%29.pdf?v=1), [karta przewodu](https://www.sommercable.com/media/14/62/df/1708085783/Datasheet_425-0051_pm_4791.pdf).

Oś gniazda roboczo 295 mm od zewnętrznej płaszczyzny frontu konstrukcyjnego, w połowie wysokości prawego boku. Kołnierz zajmuje na osi głębokości od 269,6 do 320,4 mm. Wręga S02 kończy się na 219 mm, tył zaczyna się na 372 mm. Oddzielnie sprawdzić dostęp do zacisków w płycie 22 mm. Do prób przewidzieć odkręcaną, uszczelnioną płytkę montażową, o grubości dopasowanej do rysunku gniazda i mocowania. Po wyborze płytki policzyć objętość powietrza w ewentualnym zagłębieniu, wyporność osprzętu i osłabienie boku wokół wycięcia. Oś robocza nie stanowi zgody na wiercenie.

Rezerwa na bok wynosi 186,4 mm: przyjęte 10 mm na występ gniazda i płytki, 82,5 mm na cały wtyk, 10 mm odcinka prostego za odgiętką, łuk 90° w stronę frontu o promieniu osi 80 mm oraz 3,9 mm do płaszcza przewodu. W praktyce część wtyku chowa się w gnieździe. Promień 80 mm jest założeniem trasy do sprawdzenia z przewodem. Dalszy odcinek i pętlę serwisową poprowadzić w dostępnej komorze z boku lub nad modułem, bez przechodzenia za tył i przed maskownicę. Weryfikacja wymaga też wsunięcia ręki, odblokowania, obrócenia i wyjęcia wtyku. Dla poziomego A potrzeba nominalnie co najmniej 1003,2 mm szerokości korpusu z tym łukiem; dla pionowego A około 1023,2 mm wysokości z łukiem i stopami 20 mm. Dostęp dłoni, luz na pozostałych bokach i swobodne wyjęcie modułu wymagają osobnego miejsca w rzeczywistym meblu.

## Bilans najgorszego przypadku

Kaseta tkaninowa i kaseta z kratką mają wspólną maksymalną nominalną głębokość 38 mm. Przyjęto dodatnią odchyłkę gotowego korpusu 1 mm oraz kasety 1 mm, włącznie z okleiną i mocowaniami. W S01 wyjście tylne dawało 394 + 38 + 18 = 450 mm już nominalnie. Po dodaniu tych samych odchyłek potrzeba 452 mm jeszcze przed uwzględnieniem pochylenia i szczeliny za urządzeniem.

| Orientacja ze złączem bocznym | Pochylenie | Głębokość konserwatywnej obwiedni | Razem ze szczeliną 5 mm | Zapas do 450 mm |
|---|---:|---:|---:|---:|
| Pozioma lub pionowa | 0° | 434,0 mm | 439,0 mm | 11,0 mm |
| Pozioma | 0,5° | 438,3 mm | 443,3 mm | 6,7 mm |
| Pionowa | 0,5° | 442,9 mm | 447,9 mm | 2,1 mm |
| Pionowa | 1° | 451,8 mm | 456,8 mm | przekroczenie 6,8 mm |

Rzut prostokątnej obwiedni w kierunku głębokości wynosi D cos θ + H sin |θ|. Do H wliczono stopy, 1 mm rezerwy i w ustawieniu pionowym cały boczny budżet przewodu. Taka obwiednia obejmuje też puste narożniki; przekroczenie w tym teście oznacza potrzebę dokładniejszej przymiarki. Model obejmuje pochylenie przód-tył. Wnękę mierzyć w najwęższym miejscu i sprawdzić równoległość frontu do zabudowy, gdyż skręcenie względem ściany również zwiększa potrzebną głębokość. Przyjąć poziomowanie pod obciążeniem i kontrolę po osiadaniu stóp. 5 mm za obudową jest rezerwą montażową do próby drgań.

## Prześwit maskownicy i czynności odbiorowe

Wstępny warunek dla obu kaset: przy głębokości co najmniej 37 mm, przeszkodzie grubości do 4 mm w świetle membrany, ugięciu do wewnątrz do 3 mm, roboczym skoku do przodu 14 mm i rezerwie 2 mm najwyższy ruchomy punkt w spoczynku może wystawać maksymalnie 14 mm ponad front konstrukcyjny. Uwzględnić kopułkę, zawieszenie i grubość uszczelki pod koszem. Liczby 3 i 14 mm są założeniami próby. Zmierzyć osobno naciągniętą tkaninę i kratkę oraz szczytowy ruch w zakresie dopuszczonym przez DSP. Po zmianie skoku albo ugięcia zaktualizować bilans. Przy przekroczeniu progu zmienić kasetę i przeliczyć głębokość całego zestawu.

Najbliższa weryfikacja: na makiecie prawego boku z rzeczywistym złączem oraz przewodem zmierzyć zajętość i dostęp po obrocie. Na rzeczywistym froncie sprawdzić ruchomą obwiednię przetwornika względem obu kaset. Zestawić wyniki z wymiarami dwóch wnęk. Do tego czasu architektura 450 mm jest warunkowo wykonalna; finalne otwory boku i obrys mebla pozostają do ustalenia. [Model i kontrole](s04.py) · [wyniki wszystkich przypadków](s04_wyniki.json) · [próba połączenia frontu S03](S03_karta_proby_frontu.md).
