# S08. Niezależna bramka stałych 102 l: objętość i pasowanie wręgi

Stan 12.11.2026: obliczeniowe sprawdzenie wariantu A z S01-S07. NIE CNC. Nie zmienia historycznego projektu regulowanego ani głównego README.

## Decyzja i ograniczenie modelu
Dalej projektujemy jedną, stałą pojemność 102 l netto na sztukę. Nie jest to regulator 100/120/150 l. Uzasadnienie wyboru 102 l i tolerancji +/-3 l pochodzi z S01 (kryterium wrażliwości P29C), a nie z pomiaru przetwornika. Również RSS390HF-4 jest wybrany do prototypowania, ale czyste THD/IMD i parametry termiczne wymagają pomiarów.

S06: obudowa A 816,8 x 473,3 x 394,0 mm; front FR1+FR2, boki, tył, góra i dół MDF22; jedna wręga z otworem. Objętość geometryczna komory nominalnie 108,818277 l. Wręga nominalnie zajmuje 1,507214 l. Inne oszacowane wyporności: kosz 5,000 l, terminal 0,175 l, przewody i klej 0,150 l. Wychodzi 101,986063 l netto, czyli około 102 l.

## Nowe badanie niezależnych krańców

Narzędzie s08.py oblicza objętość z wymiarów ZMONTOWANEGO korpusu i rzeczywistych grubości każdej kategorii płyt osobno; osobno oblicza objętość wręgi okiennej i wyporności osprzętu. Wersja podstawowa nie używa S06 do rachunku, a test porównuje wynik z zapisanym S06. Dla wszystkich wejść pozwala wprowadzić niepewność +/-; przedział jest arytmetyczną obwiednią najgorszego przypadku, a nie rozkładem prawdopodobieństwa.

Poniższe zakresy są ZALOZENIAMI DO BADANIA, nie zmierzonymi tolerancjami CNC ani kartą producenta. W przykladowej karcie:
- obrys zewnętrzny i każda wielkość wręgi +/-0,2 mm;
- każda grubość MDF i wręgi +/-0,3 mm, promień naroża wręgi +/-1 mm;
- wyporność kosza 5,0 +/-1,0 l, terminala 0,175 +/-0,15 l, przewodów/kleju 0,150 +/-0,15 l.

| Wynik w przykładowym modelu | Wartość |
|---|---:|
| Netto nominalne | 101,9861 l |
| Netto przy niezależnych skrajnościach | 99,9761 do 103,9983 l |
| Modelowy warunek S01 102 +/-3 l | Spełniony przy założeniach |
| Nominalny łączny luz wręgi na szerokości i wysokości | 0,2 / 0,2 mm |
| Najgorszy łączny luz wręgi z niezależnych odchyłek | -0,8 / -0,8 mm |
| Zdolność montażu wręgi dla całego przedziału | NIE |

Główny rezultat: nawet gdy modelowa objętość mieści się w tolerancji, wręga wymiarowana bez pomiaru konkretnej partii MDF może wymagać fizycznego wcisku 0,8 mm na wymiar. To blokuje uznanie nominalnej listy formatek S06 za projekt produkcyjny. Rozwiązaniem jest wspólna baza, pomiar realnych grubości i wymiarowanie wręgi do złożonej skrzyni, z uwzględnieniem wymaganego i przebadanego zakresu spoiny. Nie wolno po prostu zwiększyć luzu i założyć równoważnej sztywności połączenia.

## Warunki przejścia
1. Pobrać pomiary z realnego kompletu płyt i wręgi w karcie s08_karta.json, wraz z niepewnościami przyrządów. Nie wpisywać do niej liczb z przykładu.
2. Przed sklejaniem sprawdzić pełny styk wręgi w kilku przekrojach, wielkość i nośność spoiny oraz prostopadłość w przyrządzie. Skorygować formatki względem zmierzonych baz.
3. Zważyć i zmierzyć wyporność rzeczywistego głośnika i osprzętu; uwzględnić wszystkie łączniki, przewody, uszczelnienie, wsporniki i ewentualne dodatkowe wzmocnienia. Osobno ocenić wpływ porowatego wypełnienia na podatność akustyczną.
4. Powtórzyć S07 dla rzeczywistego frontu i przejścia kosza oraz S03 dla docisku i uszczelnienia pierścienia. Potwierdzić terminal S05, kasetę S04 i zabudowę w obu orientacjach.
5. Dopiero po akceptacji nośności połączeń, szczelności i tolerancji opracować finalne CAD, dokumentację CAM i zakres kontroli odbiorczej. Żaden wynik tego skryptu samodzielnie nie zmienia CNC HOLD.

Odtwarzanie:
- python wariant_staly/s08.py --karta wariant_staly/s08_scenariusz.json
- python wariant_staly/s08.py --karta wariant_staly/s08_karta.json
- python wariant_staly/sprawdz_s08.py

Wszystkie dane i skrypt wyłącznie w katalogu wariant_staly.
