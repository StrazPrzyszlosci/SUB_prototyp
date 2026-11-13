# S18. Projekt kasety speakON z dławnicą poza MDF 22 mm

Status: cyfrowe rysunki DXF zaprojektowane; dalej wymagane cyfrowe opracowanie detali połączeń i izolacji. Bez badań fizycznych, bez CAM.

## Naprawiony błąd z S17

LAPP ST-M16x1,5 ma długość gwintu tylko 8 mm według karty producenta. Przenosimy jego mocowanie z grubej ścianki MDF na aluminium o grubości 3 mm. Dotychczasowy otwór Ø16,5 w MDF i pogłębienie Ø36×17 zostają WYCOFANE z aktualnych plików.

Nowa kaseta jako odrębna, zdejmowana osłona elektryczna (wyłącznie sygnał głośnikowy) ma obwiednię 70x80x72 mm. Złącze jest przykręcone do frontu, który jest prostopadły do osi głębokości obudowy. Oś wtykania wzdłuż boku według S05. Prawy bok otrzymuje tylko otwór przejścia przewodu Ø30, 4 ślepe gniazda pod RAMPA M6x18. Podstawa aluminiowa 80x72x3 ma osobny otwór Ø16,5 dla dławnicy. Uszczelniona płaszczyzna podstawy odcina otwór Ø30 od otoczenia, a dławnica uszczelnia przewód w podstawie.

Źródła:
- Neutrik NL4MPRXX rysunek: https://www.neutrik.com/media/14274/download/st-nl4mprxx.PDF?v=1
- LAPP SKINTOP ST-M16 w czarnym wykonaniu 53111210: https://www.lapp.com/en_US/us/skintop-st-m/skintop-str-m/p/53111210
- RAMPA SKD330 M6x18 do MDF22 art420618001: https://www.rampa.com/media/e2/ed/d4/1699524202/RAMPA_Produktdatenblatt_MDF-EN.pdf

Płyty osłony:
| Pozycja | Format mm | Grubość | Na moduł |
|---|---:|---:|---:|
| Baza na MDF | 80×72 | AL3 | 1 |
| Front z Neutrik | 64×66 | AL3 | 1 |
| Tył | 64×66 | AL3 | 1 |
| Zewnętrzny bok | 80×72 | AL3 | 1 |
| Góra i dół | 64×74 | AL3 | 2 |

Cztery bloki serwisowe z M3 na narożach frontu są częścią następnego cyfrowego etapu. Osłona musi mieć również izolację styków, uszczelnienie ciągłe pomiędzy bazą i MDF, udokumentowane połączenie blach, przewód wewnętrzny oraz nośne zamocowanie w MDF. Dławnica ST-M16 nie ma fabrycznego O-ringu w zestawieniu LAPP dla tego rozmiaru - nie wolno uznać samego gniazda za hermetyczne. Szczegóły uszczelki zostaną określone w CAD.

Weryfikacja: python wariant_staly/cnc_stala_revA/sprawdz_s17.py, z kontrolą nowego rysunku BOK_R, podstawy, frontu i liczby formatek osłony.

Zachowano 102 l netto jako cel i dwa identyczne moduły. Brak zmian głównego README. Nie przewiduje się badań fizycznych przed skompletowaniem cyfrowego projektu CNC.
