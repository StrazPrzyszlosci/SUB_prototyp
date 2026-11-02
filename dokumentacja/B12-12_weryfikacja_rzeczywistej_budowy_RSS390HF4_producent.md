# B12-12W — weryfikacja rzeczywistej budowy RSS390HF-4 na źródłach Dayton Audio

**Data kontroli: 02.11.2026. Rodzaj dowodu: oględziny oryginalnego rysunku wymiarowego producenta i fotografia; brak pomiaru fizycznego kosza. Dotyczy wyłącznie RSS390HF-4, nie RSS390HE ani RSS390HO.**

## Pierwotne źródła

1. **Aktualny arkusz producenta:** [Dayton Audio 295-468, RSS390HF-4, karta techniczna PDF](https://www.daytonaudio.com/images/resources/295-468-dayton-audio-rss390hf-4-specifications-46176.pdf). Odczytano **rysunek z boku i rzut od tyłu**, w tym widoczne połączenia żeber z kołnierzem oraz asymetryczne terminale. Użyte wymiary są opisane na rysunku; nie skalowano zdjęcia w celu pozyskania dodatkowych liczb.
2. **Strona producenta:** [RSS390HF-4, Dayton Audio](https://daytonaudio.com/product/126/rss390hf-4-15-reference-hf-subwoofer-4-ohm). Zawiera opis materiałów i wentylacji.
3. **Archiwalny arkusz producenta (inna rewizja parametrów T/S):** [Dayton Audio RSS390HF-4 specification sheet, archiwalny PDF](https://loudmagnet.com/html/pdf/dayton/RSS390HF-4_specsheet.pdf). Rysunek kosza jest zgodny co do schematu czterech głównych żeber i ośmiu otworów, ale dane T/S **różnią się** od nowej karty. Dla bieżących obliczeń elektroakustycznych nie mieszać Fs=18,0 Hz/Vas=281,8 l ze współczesnym Fs=19,5 Hz/Vas=212 l bez odrębnego uzasadnienia rewizji.

Żadne zdjęcia producenta nie zostały skopiowane do repozytorium. Własny szkic: [obraz prawdziwego wzajemnego rozstawu osi widocznego na rysunku producenta — NIE CNC](../wyniki/b12_12_faza_zeber_producent_NIE_CNC.svg).

## Co da się stwierdzić z rysunku (nie tylko z symulacji)

| Element | Pewność | Wniosek |
|---|---|---|
| Kołnierz Ø388,4 mm | **Zwymiarowane przez producenta** | Promień zewnętrzny 194,2 mm |
| Wycięcie Ø355,8 mm | **Zwymiarowane** | Promień wycięcia 177,9 mm |
| Okrąg montażowy Ø368 mm | **Zwymiarowane** | Osiem otworów o wspólnym nominalnym promieniu 184 mm |
| Otwory kołnierza Ø6,5 mm | **Zwymiarowane** | Nie są średnicą wymaganego wiercenia w MDF ani zewnętrzną średnicą wkładki |
| Grubość kołnierza 10,5 mm i całościowa głębokość 178 mm | **Zwymiarowane** | Nie zastępują skanu promienia żebra w funkcji głębokości |
| Silnik / magnes Ø190 mm | **Zwymiarowane** | Promień dolnego zespołu około 95 mm, ale nie promień całego kosza powyżej magnesu |
| Cztery główne promieniowe żebra odlewanego kosza | **Obserwacja wizualna rysunku** | Żebra ułożone w rzucie zbliżonym do osi 0/90/180/270° względem jednego z otworów |
| Cztery otwory na osiach żeber + cztery między żebrami | **Obserwacja wizualna rysunku** | Wzajemna faza żeber i śrub wygląda na ok. **0°**, a nie 22,5°. Nie przypisuje się pomierzonej tolerancji kątowej |
| Dwa terminale połączeniowe poza osią głównych żeber | **Obserwacja wizualna** | Dodatkowa lokalna przeszkoda i trasa przewodu; konkretnego kąta i obwiedni nie da się wiarygodnie odczytać liczbowo |
| Zwężające się ku silnikowi żebra | **Obserwacja przekroju bocznego** | Przy Y=44–74 mm (za frontem MDF44) mogą być bliżej osi niż przy kołnierzu; **brak zwymiarowanej funkcji R_b(Y,θ)** |

**UWAGA:** cztery otwory geometrycznie „pod żebrami” w rzucie od tyłu NIE oznaczają automatycznie, że śruba od przodu wejdzie w żebro lub że lokalny klocek za MDF będzie kolidował. Żebro jest odlewem po wewnętrznej stronie kosza, zwęża się ku silnikowi, a o kolizji decyduje wspólny zakres (X,Y,Z). Śruba prowadzona od przodu przechodzi otworem kołnierza; klocek/wkładka za MDF pracuje w innym przedziale głębokości.

## Konsekwencja dla wcześniejszego B12-12 (korekta interpretacji)

Analityczna granica **22,5°** z badania kątowego jest poprawnym wynikiem matematycznym **dla swobodnie wybieranej fazy czterech żeber względem ośmiu śrub**. W rzeczywistym koszu faza jest związana konstrukcyjnie, a na źródłowym rysunku wygląda na **0°**: cztery otwory leżą na osiach żeber, cztery pomiędzy nimi. Nie wolno traktować 22,5° jako ustawienia dostępnego przez obrót głośnika w obudowie.

Jeżeli hipotetyczne żebra **sięgają promieniowo aż do obszaru klocka i nakładają się z nim w głębokości**, wtedy model φ=0° przewiduje *sektorowe* nakładanie z czterema osiami śrub. **Nie jest to jeszcze wynik testu kolizji przestrzennej**. Jeżeli natomiast żebra odsuwają się radialnie do środka zanim osiągną tylną płaszczyznę MDF i klocek, kolizja może nie nastąpić nawet przy współosiowości w rzucie.

Konsekwencją jest projekt **co najmniej dwóch geometrycznych klas mocowania**: cztery punkty przy osiach żeber i cztery w oknach pomiędzy nimi, z osobnym sprawdzeniem lokalizacji terminali. Nie narzuca to stosowania dwóch różnych typów śrub ani czterech klocków zamiast ośmiu; to podział na strefy wymagające osobnych weryfikacji.

## Czego NIE rozstrzyga karta producenta

- Zmienna powierzchnia R_b(Y,θ) żeber, wyprowadzeń i obudowy zacisków przy Y=44–74 mm, szerokość żeber w 3D, ich grubość oraz tolerancje odlewu.
- Wymiary dla rzeczywistej długości śruby po uwzględnieniu konkretnej uszczelki, podkładki, formy łba i gwintu.
- Moment dokręcenia, nośność MDF, wyrywanie/obracanie wkładki, wymagane luzy i prześwity narzędziowe.
- Efekt wentylacji układu napędowego po umieszczeniu ośmiu klocków i wypełnienia.
- Ostateczna objętość netto, głębokość całego urządzenia (musi być ≤500 mm), dostęp do wkładów 100/120/150 l, uszczelnienie i naprawa po sklejeniu obudowy.

**Decyzja konstrukcyjna:** nie wybierać ani nie odrzucać miejscowego mocowania na podstawie samego rzutu; przejść do pomiaru/STEP zmiennego obrysu i testów próbek. **CNC: HOLD.**

## Procedura najbliższej weryfikacji

1. Potwierdzić u producenta **plik STEP rzeczywiście dla RSS390HF-4** lub uzyskać profil kosza i terminali z udokumentowanego pomiaru.
2. Ustalić układ kątowy względem jednego ze środkowych otworów leżących na osi żebra, a potem opracować rozdzielnie cztery strefy żebrowe i cztery międzyżebrowe. Mierzyć R_b(Y,θ) za frontem MDF44.
3. Zdefiniować rzeczywistą śrubę i geometrię wkładki, zaś próby nośności prowadzić z MDF docelowej partii. Bez pomiaru nie nadawać normatywnych wartości siły/przemieszczenia lub momentu dokręcania.
4. Przeliczyć B12-09–11 dla stwierdzonego kosza; nie interpretować poprzednich ułamków scenariuszy jako prawdopodobieństw.

Powyższy dokument **weryfikuje budowę ze źródeł pierwotnych**, nie jest raportem z badania fizycznie posiadanego głośnika.
