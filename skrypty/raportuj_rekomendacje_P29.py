from pathlib import Path
import json,csv,hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];O=ROOT/'wyniki'
def main():
 a=list(csv.DictReader((O/'p29a_screening.csv').open()));b=list(csv.DictReader((O/'p29b_warstwa_naped.csv').open()));fv=json.loads((O/'p21c3_wyniki.json').read_text());fine=json.loads((O/'p21c3_dogeszczenie.json').read_text());front=json.loads((O/'p18d_front.json').read_text());g=json.loads((ROOT/'dane/konfiguracje/rekomendacja_prototypu_P29.json').read_text())
 def rank(v,p):return sorted([r for r in a if int(r['volume_l'])==v and int(r['pcu_budget_w'])==p and int(r['vmax'])==40],key=lambda r:float(r['stress_minband_db']),reverse=True)
 # Explicit post-analysis selection policy: conservative prototype at 50W stress budget.
 ranked=rank(120,50);assert ranked[0]['configuration']=='C02'
 chosen=['C02','C11','C20','C21','C04','C06','C15','C25','C26S'];table=[]
 for cid in chosen:
  r=next(x for x in ranked if x['configuration']==cid);s=next(x for x in rank(120,200) if x['configuration']==cid)
  table.append(f"| {cid}: {r['model']} | {float(r['nominal_minband_db']):.2f} | {float(r['stress_minband_db']):.2f} | {float(s['stress_minband_db']):.2f} |")
 fig,ax=plt.subplots(1,2,figsize=(11,4.6))
 for cid,col in [('C02','#137c87'),('C11','#aa6331'),('C20','#7551a6'),('C06','#666666')]:
  for pc,style in [(50,'-'),(200,'--')]:
   q=[r for r in a if r['configuration']==cid and int(r['pcu_budget_w'])==pc and int(r['vmax'])==40]
   ax[0].plot([float(r['volume_l']) for r in q],[float(r['stress_minband_db']) for r in q],style,color=col,label=f'{cid}; {pc} W strat')
 ax[0].set(xlabel='Vb [l]',ylabel='Minimum w próbie stresowej [dB]',title='Osobne sinusy 20–80 Hz, 2π/1 m/RMS');ax[0].legend(fontsize=7,ncol=2);ax[0].grid(alpha=.2)
 for frac,style in [(.5,'-'),(.25,'--')]:
  q=[r for r in front if r['n']==36 and r['mass_assumed_kg']==15 and r['x_fraction']==frac]
  ax[1].plot([r['t_m']*1000 for r in q],[r['first_mode_hz'] for r in q],style,marker='o',label=f'x/W wewn.={frac}')
 ax[1].axhline(80,color='gray',ls=':');ax[1].set(xlabel='Grubość frontu [mm]',ylabel='Pierwsza postać modelowa [Hz]',title='Front utwierdzony; kosz sztywny 15 kg');ax[1].legend(fontsize=8);ax[1].grid(alpha=.2)
 fig.suptitle('Wyniki modeli; nie pomiar SPL, temperatury ani nośności połączeń',fontsize=11);fig.tight_layout();fig.savefig(O/'97_P29_wybor_i_front.png',dpi=170);plt.close(fig)
 # finite-volume plot with explicit same-volume 3D comparison
 from komora_warstwowa_P21C2 import port
 from model_wypelnienia import CircularPores
 from analiza_rozszerzenia_SB import candidates
 d={i:d for i,p,d,c in candidates()}['C02'];effects=[]
 for r in fine:
  dep=r['gas_l']*.001/(.836*.456);layers=[(dep-.05,None),(.05,CircularPores(.0002,.98,'rigid',20))] if r['fill'] else [(dep,None)]
  z=port(.836,.456,layers,(.209,.228),d.sd,[80.],200)[0];zz=complex(r['Z_real'],r['Z_imag']);coarse=next(q for q in fv if q['count']==r['count'] and q['fill']==r['fill'] and q['step']==.025 and q['f']==80)
  effects.append(dict(count=r['count'],fill=r['fill'],relative_port_difference=float(abs(zz/z-1)),last_grid_change=float(abs(zz-complex(coarse['Z_real'],coarse['Z_imag']))/abs(zz))))
 (O/'p29_interpretacja.json').write_text(json.dumps(dict(selected='C02',selection_policy='Post-analysis conservative experimental prototype; maximize observed worst sampled band output at 50W copper and 40Vrms/12Arms, 100L is the smallest original grid volume within 0.2dB of sampled plateau; 120L is an engineering starting point within an adjustable 100/120/150L prototype, not the mathematical minimum. Not pre-registered or global optimum.',fv_effects=effects,screen_rows=len(a),screen_frequency_evaluations=len(a)*513*121,integrated_rows=len(b),front_models=len(front),recommended_volume_nominal_l=120),indent=2))
 report52='''# Raport 052 — P21C2/P21C3/P18D: warstwa, wkłady i nowy front

Data: 2026-10-30. Wyniki obliczeń; brak pomiarów urządzenia.

## Komora z kołowym źródłem i porowatą warstwą

Zastosowano rozdzielenie modów poprzecznych w prostokątnej komorze.
Dla każdego modu kappa i warstwy: q²=omega²*rho/K−kappa²,
Zc=omega*rho/q, Ztył=−j Zc cot(qd). Kolejne warstwy składa rekurencja
Zin=(Zload+j Zc tan(qd))/(1+j Zload tan(qd)/Zc).
Port tłoka to suma epsilon_n epsilon_l b_nl² Zin/(W H),
gdzie b jest transformatą kołowego tłoka z raportu 051.

To model 3D ze zmianami ośrodka po głębokości; warstwa zajmuje cały
przekrój. Nie utożsamiać jej z matą na pięciu ścianach. ZK z nieruchomym
szkieletem, porowatość 0,98, promienie porów 0,05/0,2/1 mm są scenariuszami,
nie identyfikacją produktu. Warstwa tylna 0/25/50/100 mm; 9 finalistów,
100/120/140 l, 7 częstotliwości 20–80 Hz, zimne/gorące Re, dwie
konwencje tylnej masy powietrza i diagnostyczna podatność ścian:
**15120 punktów napędu**. Te prostokąty odpowiadają objętości netto,
ale nie odwzorowują rozpraszania przez kosz lub usztywnienia.

Mms jest efektywne. Zamiast dopisać bez kontroli cały port gazu, odjęto
0 lub 1 razy jedną stronę niskoczęstotliwościowej masy tłoka w odgrodzie
8 rho a³/3. To dwie jawne konwencje zastępcze, nie wyznaczenie Mmd.
Nie dodano ponownie frontowego promieniowania. Prawdziwy brak Mmd
pozostaje otwarty. Minimalne Re(Z) jest nieujemne w badanym zakresie.

Kontrole: redukcja do pustego portu P21C1 z błędem 7,8e−16; redukcja
jednorodnego modu do warstw 1D. Odrębna drabinka FV dla 12 kombinacji
mod/f (20/80/160 Hz, mody 00/10/12/33) i siatek 64/128/256/512:
największa końcowa różnica około 2,71e−5 względnie. Trzy świadki
ucięcia poprzecznego 100→200 zmieniają port do 3,53e−5 względnie.
To nie certyfikat całej ciągłej dziedziny materiału.

## Wkłady: rzeczywiste przeszkody przestrzenne

Zbudowano niezależny, trójwymiarowy model objętości skończonych
Helmholtza na siatce dopasowanej do prostokątnych granic wkładów.
Komora 836×414×456 mm, źródło C02 w (209,228) mm na froncie.
0/10/16 sztywnych zamkniętych modułów 180×170×100 mm, ułożonych
w prawej połowie. Ich gaz wewnętrzny nie został ponownie doliczony.
Tylna warstwa 50 mm albo brak warstwy. Model nie zawiera jeszcze
kosza, wszystkich wręg, okuć i podatności samych modułów.

Równanie FV: (K−omega² C)p=j omega Q. K zawiera harmoniczne
przejścia 1/rho przez granice ośrodków, C=V/Kbulk. Źródło całkowano
po przecięciu dysku z komórkami. Do ciśnienia środka komórki dodano
rekonstrukcję na powierzchnię z warunku Neumanna. Bez niej porównanie
z analitycznym naciskiem na tłok jest błędne.

36 rozwiązań: 3 liczby modułów × 2 wypełnienia × 2 siatki × 3 f.
Dodatkowe 4 rozwiązania przy 80 Hz: do 44990 niewiadomych.
Błąd portu pustej komory z warstwą względem niezależnego szeregu
spadł z 0,651% przy kroku 25 mm do 0,209% przy 16 mm.
Dla 16 wkładów i maty zmiana 40→25 mm wynosiła 1,08%; po dogęszczeniu
25→16 mm nadal 0,840%. Nie nazwano tego certyfikatem dokładności <1%.

'''
 report52+='| Wkłady | Mata | Różnica portu względem prostokąta o tej samej objętości, 80 Hz | Zmiana ostatniej siatki |\n|---:|---|---:|---:|\n'
 for e in effects:report52+=f"| {e['count']} | {e['fill']} | {100*e['relative_port_difference']:.3f}% | {100*e['last_grid_change']:.3f}% |\n"
 report52+='''
Różnica dotyczy zespolonego p/Q, nie zewnętrznego SPL. Wniosek:
regulacja wkładami jest wykonalnym eksperymentem, ale nie jest dokładnie
równoważna pustej skrzyni o mniejszej głębokości.

## Nowy front z przesuniętym otworem

MITC4 z otworem wielokątnym zbieżnym do koła Ø355,8 mm, front 880×500 mm.
Warianty 22/33/44 mm, otwór centralny lub x=231 mm od lewej krawędzi,
12/24/36 podziałów na bok, kosz sztywny 10/15 kg. Łącznie 36 modeli,
do 7347 współrzędnych po redukcji. Masa kosza jest scenariuszem, nie
potwierdzonym Mnet RSS390HF-4. Brzeg zewnętrzny utwierdzony, kosz ciągle
sztywno związany z otworem: nie odwzorowuje ośmiu realnych śrub/uszczelki.

Przy przesuniętym otworze i 15 kg pierwsza postać wynosi około
180,5 / 289,6 / 388,0 Hz dla 22/33/44 mm. Statyczna podatność całego
portu frontu spada z 5,02e−9 do 0,813e−9 m³/Pa. Nowa siatka centralna
odtwarza macierz wcześniejszego kodu dokładnie; każda zachowuje pole
prostokąta po dodaniu otworu. Nie przenosimy tych liczb na pełną ramę,
luźny styk, naprężenia śrub, klej lub zmęczenie.

Diagnostyka innych ścian: nieusztywniony panel 836×456×22 mm przy
E=2 GPa, rho=800 kg/m³ ma pierwszą postać SSSS około 103 Hz.
Dlatego rekomendacja wymaga usztywnień. Umowne podparte pola około
280×300 mm dają około 395 Hz. Podparcia SSSS nie są dowodem, że konkretna
wręga zapewni takie zamocowanie; jej połączenie musi zachować tę drogę siły.

## Odtworzenie

`komora_warstwowa_P21C2.py`, `integracja_P29B.py`,
`wklady_przestrzenne_P21C3.py`, `dogesc_P21C3.py`,
`front_przesuniety_P18D.py`, `weryfikacja_i_geometria_P29.py`.
Uruchamiać kolejno z OPENBLAS_NUM_THREADS=1. Wyniki: p29b_*, p21c3_*, p18d_*.
'''
 (ROOT/'raporty/052_komora_warstwy_wklady_i_front.md').write_text(report52)
 report53='''# Raport 053 — P29A/B: porównanie, niepewność i sygnały

Data: 2026-10-30. **Rekomendacja eksperymentu, nie ranking zmierzonej jakości.**

## Kryterium i zakres

Przeliczono wszystkie 27 konfiguracji elektrycznych / 26 produktów.
5 objętości 60/80/100/120/150 l, 2 budżety 40 V/12 A i 60 V/20 A RMS,
3 hipotetyczne pułapy strat miedzi 50/100/200 W. W każdej konfiguracji
121 częstotliwości w 20–80 Hz i 512 punktów Sobola plus nominalny.
810 wierszy syntezy, 50279730 ocen częstotliwościowych (część wspólnego
modelu ponownie oceniana przy różnych limitach; nie tyle niezależnych modeli).

Metryka: minimum obwiedni dla **oddzielnych sinusów**, monopól 2π/1 m,
ciśnienie RMS; katalogowy skok peak. Nie jest to muzyka, SPL w pokoju,
czas dopuszczalnej pracy albo wynik przy normowym THD.

Zakresy stresowe: Mms ±10%, Cms ±15%, BL ±10%, Rms ±30%, Re ±5%,
Le ±20%, Sd ±2%, V ±3%; moduł gazu 0,714–1 adiabatycznego,
dodatkowy Rms 0–1 bazowego, Xref 0,5–0,8 katalogowego, wzrost T 0–80 K.
Re(T) ma założone alpha=0,004/K. To niezależnie zaburzane parametry
fizyczne, nie rozkład produkcji ani pewność, że obejmują rzeczywiste egzemplarze.
Wspólne współrzędne Sobola porównują warianty, nie dowodzą dominacji
przy wszystkich niezależnych parach. Nominalny Xref=0,7 Xmax nie gwarantuje THD.

Pułap Pcu nie jest katalogowym Pe. Wybrano trzy scenariusze właśnie
po to, aby nie przypisać nieznanego chłodzenia na podstawie mocy nadrukowanej.
50 W stałego grzania wymaga Rth ≤0,8 K/W dla przyrostu ≤40 K w prostym
stanie ustalonym; dla 80 K: ≤1,6 K/W. Te progi nie są pomiarami produktu.
Nie uwzględniają innych źródeł ciepła i dopuszczalnych temperatur materiału.

## Wynik porównania przy 120 l i 40 V/12 A

| Konfiguracja | Nominalnie, Pcu≤50 W [dB] | Minimum próby stresowej, 50 W [dB] | Minimum próby stresowej, 200 W [dB] |
|---|---:|---:|---:|
'''+ '\n'.join(table)+'''

**Przyjęta po analizie reguła wyboru prototypu:** preferuj wariant z
najwyższym zaobserwowanym minimum przy konserwatywnym scenariuszu 50 W
Próg do 0,2 dB od plateau spełnia już **100 l**, a nie dopiero 120 l.
Korekta P29C (raport 055) rozdziela wybór głośnika od wyboru punktu
eksperymentu: **C02 RSS390HF-4, start około 120 l**, z regulacją 100/120/150 l.
120 l jest decyzją inżynierską, nie najmniejszą objętością wynikającą z tego
progu ani globalnym optimum. Reguła nie była prerejestrowana przez użytkownika.
Badanie wszystkich pułapów pokazuje też argument przeciw wyborowi:
przy większym dozwolonym grzaniu wygrywa RSS390HE-22.

Nie odrzucono STX z powodu marki. C06 ma wartościowy model 12″,
ale mniejsze Sd·X ogranicza dół pasma w przyjętym kryterium. SB również
pozostaje sensowną alternatywą dla mniejszego zapotrzebowania na 20 Hz.
Nie wykazano, że C02 ma niższe rzeczywiste THD niż STX, SB lub Ultimax.

![Kryterium wyboru i front](../wyniki/97_P29_wybor_i_front.png)

## Kontrole i integracja

324 świadki sprawdzono odrębnym układem równań I/v/x i bilansem energii;
reszty około 2,2e−15. To kontrola algebraiczna, nie walidacja fizyczna.
Raport 052 dodaje przestrzenną warstwę, dwie konwencje tylnej masy gazu,
Re po ogrzaniu i diagnostyczną podatność ścian dla dziewięciu finalistów.
W tej rodzinie przy 120 l i pułapie 50 W minimum C02 to około 98,38 dB,
C11 około 95,09 dB, C06 około 94,83 dB. Nie łączyć tych minimów z minimami
Sobola jako jednego wspólnego certyfikatu: kampanie mają różne osie.

9 wielotonów: C02, 100/120/140 l, 10 jednoczesnych tonów 20–80 Hz,
3 układy faz. Wyrównanie poziomów tonów jest skończoną inversją
częstotliwościową przed filtrami HP BW2 20 Hz / LP BW4 80 Hz.
To nie realizowalny preset miniDSP, nagranie muzyki ani rzeczywisty limiter.
Pułapy: 56,57 Vpeak, 16,97 Apeak, 9,8 mmpeak i 50 W średniego Pcu.
W każdym przypadku wiąże ruch. Dla 120 l średnie Pcu wynosi około
7,50–13,33 W, a crest factor ruchu około 2,52–3,36, zależnie od faz.

Próbki 12 kHz uzupełniono granicą międzypróbkową: max_próbki +
(suma omega_k |amplituda_k|)/(2 Fs). Poziom przeskalowano tą granicą,
nie samym maksimum dyskretnym. Dotyczy tylko tych skończonych sinusów,
bez rozruchu, sygnału arbitralnego i zmian temperatury w czasie.
Nie przenosić starego certyfikatu P24A na nową komorę bez ponownej identyfikacji.

## Architektura dwóch subwooferów i monitorów

Sprawdzono macierz 2→8: kanały 1–3 lewy monitor, 4–6 prawy,
7–8 niezależne subwoofery, każdy z sumą 0,5 L + 0,5 R.
Norma każdego wiersza wynosi 1: sama macierz nie podwaja amplitudy
przy wspólnofazowym sygnale stereo. To nie ogranicza wzmocnienia EQ.

Idealne akustyczne LP LR4 + HP LR4 przy 80 Hz sumują się do modułu 1;
sprawdzono 1000 częstotliwości. Realne monitory są nieznane: filtry,
opóźnienia i fazę trzeba dobrać do pomiarów, nie do samej algebraicznej tożsamości.
Wariant startowy software ma HP BW2 20 Hz + LP LR4 80 Hz, bez dodatniego
EQ, zapis SOS dla 96 kHz. Wszystkie bieguny wewnątrz koła jednostkowego.
To inny LP niż w opisanym eksperymencie wielotonowym; nie utożsamiono ich.

## Wrażliwość rekomendacji

Wybór może zmienić się przy: (1) większym dopuszczalnym grzaniu lub
lepszym zmierzonym chłodzeniu konkurenta, (2) mniejszym rzeczywistym
użytecznym skoku C02, (3) braku miejsca na dwie szerokie skrzynie.
Nie zidentyfikowano danych, które pozwoliłyby ogłosić przewagę jakościową
nad ADAM Sub12/Sub15 lub końcowy poziom w sweet spocie.

Odtwarzanie: `synteza_P29A.py`, `integracja_P29B.py`,
`weryfikacja_i_geometria_P29.py`. Wejścia stresu i wszystkie wyniki
są zapisane; brak kosztorysu jest zgodny z odłożeniem części handlowej.
'''
 # Correct count from actual rows, avoid hand-counting duplicated evaluations.
 report53=report53.replace('50279730',str(len(a)*513*121))
 (ROOT/'raporty/053_porownanie_i_odpornosc_rekomendacji.md').write_text(report53)
 report54='''# Raport 054 — rekomendowana konfiguracja pierwszego prototypu

Data: 2026-10-30. **Wybrano konfigurację do dalszego opracowania prototypu.**
To rekomendacja inżynierska na podstawie modeli, nie ukończona dokumentacja
wykonawcza ani potwierdzenie osiągów gotowego urządzenia. Publikacja wyników w PR została ponownie zlecona przez użytkownika.

## Jeden rekomendowany wariant

| Element | Rekomendacja | Status / uzasadnienie |
|---|---|---|
| Głośnik | **Dayton Audio RSS390HF-4, 15″, 4 Ω** | Dane producenta + porównanie wszystkich 27 konfiguracji; najlepsze minimum badanego konserwatywnego scenariusza |
| Topologia | Zamknięta; jeden stały front pod C02 | Wymaganie użytkownika |
| Punkt startowy | **Około 120 l netto powietrza** | 10 nominalnych wkładów daje 118,84 l przy rezerwie 8 l; dokładność zależy od rzeczywistej wyporności |
| Regulacja | Około **100 / 120 / 150 l** | 16 / 10 / 0 mocowanych, szczelnych wkładów; krok nominalnie 3,06 l |
| Gabaryt korpusu W×D×H | **880×480×500 mm** | Obliczona geometria; pionowo 500×480×880 mm |
| Limit głębokości | Nie przekroczyć 500 mm po dodaniu wystających elementów | Korpus zostawia 20 mm; maskownica, wychylenie i terminal muszą się w tym zmieścić albo trzeba zmniejszyć głębokość korpusu i przeliczyć litraż. Nie zatwierdzono jeszcze maskownicy |
| Materiał | MDF 22 mm, front 44 mm (dwie klejone warstwy) | Model izotropowy + porównanie frontów; rzeczywista jakość laminowania i spoin wymaga kontroli |
| Pozycja | Oś około 231 mm od lewej i 250 mm od dołu frontu | Blisko środka lewej połowy; niewielkie odsunięcie od skrajnej krawędzi. Można odbić lustrzanie |
| Usztywnienia | Dzielić duże panele na pola rzędu ≤280×300 mm, z zachowaniem torów wkładów | Docelowa funkcja konstrukcyjna z modelu płyt; rozmieszczenie i sztywność realnych wręg nie są jeszcze zatwierdzonym rysunkiem |
| Wypełnienie startowe | Zdejmowana tylna warstwa poliestrowa 50 mm | Pole około 0,381 m², objętość obwiedni 19,06 l. Przy założeniu 20 kg/m³: **około 0,38 kg**; nie odejmować 19 l jako litego materiału |
| Wkłady | Nominalnie 180×170×100 mm zewnętrznie, szczelne, ścianki MDF około 8 mm, podparte wewnętrznie | Wzorzec P20/P21; końcowy obrys wraz ze spoinami/okuciami wymaga kontroli. Mocowanie dodatnie we wszystkich orientacjach, nie luźny stos |
| Klejenie | PVAc D3 do prób, np. Kleiberit 303.0; stałe szerokie połączenia i listwy | Kandydat procesu. Brak Gc/S-N/J(t) MDF nie pozwala zatwierdzić trwałości samą klasą D3 |
| Napęd | Zewnętrzna klasa D; projektowy budżet **40 V RMS / 12 A RMS** dla osobnych sinusów | 40 V na czystych 4 Ω odpowiada 400 W, ale głośnik nie jest stałym rezystorem. To wymaganie portu, nie nastawa bezpiecznej mocy |
| DSP | **miniDSP Flex Eight w wersji z 8 wyjściami analogowymi**, bez Dirac w modelu 96 kHz | Dwa suby + dwa monitory trójdrożne; producent potwierdza macierz i wyjścia |
| Filtry początkowe | HP BW2 20 Hz, LP LR4 80 Hz, bez dodatniego EQ do pierwszych pomiarów | Odtwarzalne współczynniki software, nie gotowa ochrona X/T ani wyrównanie do 20 Hz |

Rekomendowana skrzynia ma być platformą prób. Nie należy zamawiać CNC
wyłącznie z tej tabeli: grubość frontu, otwór, wręgi, mocowania wkładów
oraz całkowity obrys muszą tworzyć jeden zweryfikowany rysunek wykonawczy.
Konstrukcja i regulacja zostały wybrane warunkowo; detale wykonawcze pozostają otwarte.
Raport 055 pokazuje, że skrócenie korpusu do 470 mm wymaga też zmiany
układu wkładów: obecny układ kolidowałby z tylną matą na 6 mm.

## Rzeczywisty bilans litrów

Puste wnętrze: 836×414×456 mm = **157,823 l brutto**.
W modelu startowym rezerwa na głośnik, usztywnienia i osprzęt wynosi 8 l;
nie jest to zmierzona wyporność RSS390HF-4. Zakres stresowy 4–11 l daje:

| Wkłady | Nominalne netto [l] | Zakres przy rezerwie 4–11 l [l] |
|---:|---:|---:|
'''
 for rr in g['configurations']:report54+=f"| {rr['modules']} | {rr['nominal_net_air_l']:.2f} | {rr['net_air_range_l'][0]:.2f}–{rr['net_air_range_l'][1]:.2f} |\n"
 report54+='''
Odjęto także 0,381 l ciała stałego maty przy założonej porowatości 0,98.
Efektywna podatność z matą nie jest tym samym co netto powietrza.
Zmienna masa/gęstość i rzeczywisty opór przepływu materiału mogą wymagać
zmiany grubości; 0,38 kg to punkt eksperymentu, nie udowodnione optimum włókniny.

Sprawdzono 48 odcinków translacyjnych montażu 16 wkładów w pustym
korpusie, przez otwór po wyjętym głośniku. Należy zachować te korytarze
po dodaniu wręg i zamków. Test nie obejmuje narzędzia, dłoni, przewodów,
łączników ani tarcia. Moduły nie są konstrukcyjnym podparciem ścian.

## Dlaczego ten wariant, a nie sam największy skok

RSS390HF-4 daje w przyjętym badaniu dobry dół pasma bez uzależniania
wyboru od pułapu 200 W ciągłych strat miedzi. Około 120 l osiąga plateau
wybranego konserwatywnego kryterium; większy litraż pozostawiono jako
wartościową możliwość eksperymentu, zamiast na stałe budować mniejsze wnętrze.
Front 44 mm ogranicza podatność w przeprowadzonym porównaniu przesuniętego otworu.
Regulacja wkładami zachowuje stały front i nie wymaga uszczelnienia całej
ruchomej przegrody. Jej koszt to masa oraz zmiana przestrzennego portu.

**Najsilniejszy argument przeciw rekomendacji:** duża i ciężka skrzynia
z głośnikiem o mniejszym skoku od RSS390HE-22. Sam model masy korpusu
MDF daje około 36 kg, bez głośnika, wkładów i pełnego osprzętu.
Przy lepszym chłodzeniu i mocniejszym wykorzystaniu napędu HE może być
lepszym wyborem dla maksymalnego SPL. Nie wykazano wyższej jakości THD C02.

Alternatywa 12″: STX W.32.800.8.FCX (C06), jeśli priorytet przesunie się
na mniejszy gabaryt, lub SB34SWPL76-4 (C04) jako inny dobrze opisany kandydat.
Nie nazywamy żadnego najtańszym: zgodnie z zakresem nie badano bieżących cen.
Wariant o większym potencjale przy większym grzaniu: RSS390HE-22 (C11).

## Co może zmienić wybór i jak to rozstrzygnąć

1. Rzeczywiste użyteczne wychylenie/THD C02 okaże się znacznie gorsze niż
   przyjęty margines 0,5–0,8 Xmax. Rozstrzyga stopniowany test ruchu,
   zniekształceń i kompresji, z kontrolą napięcia i temperatury po budowie.
2. Chłodzenie lub BL(T) sprawi, że konserwatywna przewaga C02 zniknie.
   Potrzebne Re po ogrzaniu, kompresja i powtarzalne sygnały z określonym czasem.
3. Dwie skrzynie nie zmieszczą się w realnych miejscach. Suma szerokości
   poziomych to 1,76 m, pionowych 1,00 m; nie dowodzi to miejsca przy monitorach,
   meblach i przejściu. Pozycje użytkownika nadal nie są ustalone.

**Najkrótszy eksperyment rozróżniający litraż i wypełnienie:** w tym samym
prototypie porównać małosygnałową impedancję oraz bliskie pole przy 0/10/16
wkładach, najpierw bez maty, potem z tą samą zważoną matą. Zachować pozycję,
napięcie, temperaturę i pliki surowe. To identyfikuje obciążenie oraz
wykrywa przeciek; sam pomiar impedancji nie rozdziela wszystkich strat.
Pomiary w pokoju nie stają się pomiarem wolnego pola przez przeliczenie odległości.

## Ochrona i gotowość

Compressor miniDSP nie jest zidentyfikowanym obserwatorem wychylenia
ani temperatury. 40 V/12 A to możliwości modelowego napędu, a nie zgoda
na pełny sygnał. Nowego presetu ochronnego nie zatwierdzono: współczynniki
HP/LP nie zastępują limitu ruchu, pamięci cieplnej i kalibracji toru DAC–wzmacniacz.
Wyniki P24A są punktem odniesienia, nie certyfikatem nowej geometrii.

Wyłoniono **jedną rekomendację prototypu**, ale nie ogłoszono zamknięcia
wszystkich 30 pakietów, dokumentacji wykonawczej ani końcowego PDF.
Otwarte są pełne sprzężenie ścian/spoin/wkładów, rzeczywista identyfikacja
materiału i napędu, parametry ochrony, dokładny obrys maskownicy oraz pomiary.

## Źródła i odtworzenie

Podstawą są raporty 028, 038–051 oraz nowe 052–053. Dane katalogowe
pozostały niezmienione. Ponowny odczyt źródeł z 2026-10-30 zapisano w
`dane/zrodla/P29_weryfikacja_zrodel_20261030.json`.

- [RSS390HF-4 — producent](https://daytonaudio.com/product/126/rss390hf-4-15-reference-hf-subwoofer-4-ohm)
- [Karta producenta RSS390HE-22](https://www.parts-express.com/pedocs/specs/295-292--dayton-audio-rss390he-22-spec-sheet.pdf)
- [Karta producenta UMII15-22](https://www.parts-express.com/pedocs/specs/295-714--dayton-audio-UMII15-22-spec-sheet.pdf)
- [Flex Eight — producent](https://www.minidsp.com/products/minidsp-in-a-box/minidsp-flex-eight)
- [Routing i przetwarzanie](https://docs.minidsp.com/product-manuals/flex-eight/signal-flow/index.html)
- [Kleiberit 303.0 — TDS](https://www.kleiberit.com/fileadmin/Content_new/Produktinformationen/303.0/dbe3030_KSE.pdf)

Nowe pliki i hashe: `wyniki/manifest_rekomendacji_P29.json`.
'''
 (ROOT/'raporty/054_rekomendowana_konfiguracja_prototypu.md').write_text(report54)
 print('Reports 052–054 generated; recommendation C02, ~120 l, 880×480×500 mm')
if __name__=='__main__':main()
