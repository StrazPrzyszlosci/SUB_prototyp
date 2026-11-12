# S16. Niezależne sprawdzenie układu zamkniętego 102 l i znaczenia tolerancji T/S

Data: 12.11.2026. To nie jest powrót do regulacji pojemności. Analizowana konstrukcja ma JEDNO docelowe 102 l netto; 99 i 105 l są odchyleniami tolerancji, nie mechanicznymi nastawami.

Źródła: producent RSS390HF-4 https://daytonaudio.com/product/126/rss390hf-4-15-reference-hf-subwoofer-4-ohm oraz S01 (metoda wybrania 102 l), S06 (101,9861 l nominalne). Katalogowe Fs=19,5 Hz, Qts=0,43, Vas=212 l.

## Weryfikacja wzorami zamkniętej obudowy
Dla liniowego układu o parametrach skupionych, bez przecieków, wytłumienia, dodatkowej objętości akustycznej, indukcyjności, DSP i zniekształceń:
- alpha = Vas / Vb;
- Fc = Fs × sqrt(1 + alpha);
- Qtc = Qts × sqrt(1 + alpha);
- F3 z dokładnego modułu znormalizowanego filtru górnoprzepustowego drugiego rzędu, a nie z reguły Fc=F3.

Dla 102 l otrzymujemy Fc około 34,214 Hz, Qtc około 0,7545 i F3 około 32,201 Hz. S01 raportował Fc=34,21 Hz, Qtc=0,75 i F3 około 32,27 Hz w swoim szerszym modelu, więc zgadzają się co do skali; różnica F3 to konsekwencja odmiennych założeń modelowych / zaokrągleń i wymaga porównania definicji, a nie ukrytego wyrównania danych.

## Czego NIE wiemy z karty
Katalogowe T/S nie podaje rozkładu między rzeczywistymi egzemplarzami, zmian po wygrzewaniu, przesunięć termicznych, Bl(x), Cms(x) czy zmian efektywnej objętości po wypełnieniu. Brak podstaw do przyjęcia stałego, gwarantowanego Qtc i SPL po produkcji.

Skrypt wykonuje dwa jawnie oddzielone przesiewy:
1. 99, 102, 105 l przy niezmiennych katalogowych T/S, jako model tolerancji litrażu;
2. HIPOTETYCZNY obszar Fs ±5%, Vas ±10%, Qts ±0,05 oraz Vb 99-105 l. To NIE są tolerancje podane przez Dayton, tylko test wpływu brakującej wiedzy. Nie służy do przedłużania niepewności ani wyboru nowego regulowanego litrażu.

Decyzja: pozostawić 102 l jako cel do pomiaru, ale nie zatwierdzać DSP ani mechaniki na podstawie jednej dokładnej liczby Qtc. Przed zamknięciem BOM zmierzyć T/S każdego z dwóch egzemplarzy, porównać je na wspólnej skali, po zmontowaniu powtórzyć impedancję, ocenić szczelność, efektywnie odczuwane Vb i stratność. Po wypełnieniu włókniną ponownie zmierzyć, a nie dopisywać arbitralny procent zwiększenia litrażu.

Odtworzenie: python wariant_staly/s16_odpowiedz.py oraz python wariant_staly/sprawdz_s15_s16.py. Wnioski ograniczone do układu małosygnałowego przed DSP i pokojem; CNC HOLD.
