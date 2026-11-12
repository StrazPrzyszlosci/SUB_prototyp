# S14. Weryfikacja katalogowa toru miniDSP Flex Eight -> ICEpower 300AS1 (tylko kandydat)

Bramki E1/E2 z S09. S01 rozpatruje obwiednie napedu do 40 Vrms/12 Arms. ICEpower 300AS1 ma w karcie TYPowe Vpeak 50 V i Ipeak 20 A, a nie stale 40 Vrms czystego sinusa. Dla idealnego sinusa 50/sqrt(2)=35,36 Vrms, wiec przypadkow z 40 Vrms z modelu nie wolno przenosic na te koncowke bez przeliczenia.

Zrodla: https://www.minidsp.com/products/minidsp-in-a-box/minidsp-flex-eight oraz https://shop.icepoweraudio.com/wp-content/uploads/2023/02/ICEpower300AS1_Datasheet_2_2.pdf .

Flex Eight w wariancie 8 RCA ma 8 niesymetrycznych wyjsc analogowych, maksymalnie 2 Vrms, a AS1 zbalansowane wejscie audio i gain katalogowy 28,0-28,3 dB. Przy gornym gain 28,3 dB (= ok. 26,00 x) 2 Vrms na wejsciu teoretycznie zadaloby 52,0 Vrms na wyjsciu, poza jego TYPowym 50 Vpeak. Przy zalozeniu idealnego sinusa dopasowanie do 50 Vpeak daje maksymalnie ok. 1,360 Vrms na wejściu (= -3,35 dB wzgledem 2 Vrms). To nie jest nastawa docelowa ani prog ochrony.

Przy hipotetycznym tlumieniu -6,0 dB poziomu full-scale Flex Eight otrzymalibysmy idealnie 26,06 Vrms (36,86 Vpeak) na obciazeniu i 2,65 dB marginesu do typowej granicy 50 Vpeak. Obwiednia nie obejmuje korekcji EQ +9 dB, sumowania dwoch kanalow wewnatrz DSP, chwilowego clippingu, zmiennej impedancji, zjawisk termicznych, dokladnosci i poziomow adaptera RCA -> wejscie roznicowe. Nie wpisywac tej wartosci jako globalny limiter.

Uwagi wykonawcze i bezpieczenstwa:
- Wyjscie AS1 to para OUT+ i OUT- o duzej skladowej wspolnej; nie laczyc OUT- z masa sygnalowa ani obudowa. Pomiar oscyloskopem wymaga procedury zgodnej z dokumentacja urzadzenia i sondy roznicowej o odpowiednich parametrach.
- speakON to sygnal glosnikowy, NIE gniazdo zasilania sieciowego. Neutrik ostrzega przed rozlaczaniem pod obciazeniem.
- MiniDSP Flex Eight i Flex/Balanced lub HTx to ROZNE modele; nie wpisywac do Flex Eight 4 V na wyjsciu TRS.
- Dwa suby potrzebuja dwoch niezaleznych torow mocy, kazdy z ograniczeniem Xpeak/U/I/T; dwie trojdrozne kolumny wymagaja lacznie jeszcze 6 torow. Razem 8 kanalow DSP.
- Przed wyborem koncowki: dopasowac topologie unbalanced RCA do zbalansowanego inputu wedlug dokumentacji producenta, osobno sprawdzic Z(f) rzeczywistego drivera, pomiary zasilania, rozruch i zabezpieczenia. Wysokonapieciowy montaz modulow AC pozostaje poza zakresem samodzielnych prob bez uprawnionego wykonawcy.

Wniosek: ICEpower 300AS1 jest sprawdzalnym kontrkandydatem, ale nie uzasadnia modelowych limitow 40 Vrms i nie zostal zatwierdzony do docelowego zestawu. Nie ma potwierdzonej ochrony membrany ani termiki; CNC/elektronika HOLD.
