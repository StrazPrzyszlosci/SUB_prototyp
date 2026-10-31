from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];O=R/'wyniki';rows=json.loads((O/'p18e_przypadki.json').read_text());ctrl=json.loads((O/'p18e_kontrole.json').read_text())
base=dict(E=2.1e9,Eg=1e8,kt=1e7,kr=1000,parity='breathing')
nom=[r for r in rows if all(r[k]==v for k,v in base.items())]
def get(n,front=.01,braced=True):return next(r for r in nom if r['nx']==n and r['front']==front and r['braced']==braced)
nmax=max(r['nx'] for r in nom);a=get(nmax);b=get(nmax,.022);un=get(nmax,braced=False);previous=get(48)
parts=['''# Raport 059 — P18E: skończona sztywność wręg i podparcia paneli

Data obliczenia: 2026-10-31. **Wykonany model zredukowany podzespołu, nie pełny MES skrzyni i nie pomiar.** Geometria pochodzi z wariantu P20D 1000×440×500 mm. Przednia pionowa listwa wręgi ma głębokość **10 mm**, zgodnie z korytarzem dostępu. Wariant 22 mm jest kontrfaktycznym porównaniem mechanicznym; nie przenosimy na niego zaliczonego dostępu wkładów.

## Pytanie, hipoteza i wpływ na decyzję

Czy realne wąskie elementy wręgi można utożsamić z idealnymi liniami podparcia dzielącymi panele na małe pola? Hipoteza robocza: po uwzględnieniu ugięcia belek, skończonej sztywności pionowych listew i otaczających ścian częstotliwości mogą pozostać znacznie niższe od wyniku idealnie podpartego małego pola. Osobno sprawdzamy cenę zwężenia przedniej listwy z22 do10 mm, które umożliwia dostęp.

**Wynik:** w badanej rodzinie podpory są dalekie od idealnej blokady. Nie ma podstaw do przypisania tej geometrii wcześniejszego wskaźnika około395 Hz z pola280×300 mm. Nie wyznaczono jednak rzeczywistych modów całej obudowy: wynik zależy od reprezentacji reszty skrzyni sprężynami.

## Dziedzina, geometria i pochodzenie

Płyta górna/dolna: wewnętrzny prostokąt956×374 mm, MDF22 mm. Dwa pełne obwody wręg mają środki x437 i702 mm. Każdy łączy górną i dolną płytę belką22×22 mm biegnącą przez głębokość374 mm, przednią listwą22×10 mm i tylną22×22 mm. Dodatkowa tylna konstrukcja U ma x209 mm, belkę od y220 do374 mm i tylko tylną pionową listwę. Długość osiowa pionowych listew:412 mm. Współrzędne zamrożono w `p18e_geometria_zamrozona.json`. Po refaktoryzacji generatora P20D sprawdzono dokładną równość wszystkich11 prostokątów wręg oraz wymiarów wnętrza względem jawnej poprzedniej listy. Moduły nie są wejściem P18E. Obliczenia nie importują zmiennego generatora; wejściowy hash migawki jest w manifeście.

Dwie przeciwległe płyty są zredukowane przez symetrię. Badamy: (a) oddychanie, obie na zewnątrz; (b) wspólny ruch w tym samym fizycznym kierunku, z przeciwnymi znakami lokalnych normalnych. W drugim przypadku listwy nie rozciągają się osiowo, lecz nadal wnoszą masę. Nie dokładamy masy i sztywności drugiej płyty do modelu jednej współrzędnej przez pomyłkę.

MDF E=1,5/2,1/3 GPa, nu=0,3, rho=730 kg/m³; E kleju1/10/100/1718 MPa i grubość każdej z dwóch spoin0,25 mm to **scenariusze**, nie pomiary ani karta wybranego wyrobu. Otoczenie reprezentują sprężyny rozłożone po obwodzie: k_t=10⁶/10⁷/10⁸ N/m² i k_r=0/1000 N. Zakresy są badaniem wrażliwości, nie udowodnionymi granicami rzeczywistej ramy. Sprężyny kończą się na układzie odniesienia; nie obliczono przemieszczeń frontu, boków, tyłu ani stóp.

Płyta: istniejący Reissner–Mindlin/MITC4 z P18A. Belki: nowe dwuwęzłowe elementy Eulera–Bernoulliego z zgodną masą, bez dokładania sztywności kompozytowej z osi równoległych. Belka i płyta mają wspólne przemieszczenie/obrót poprzez interpolację. Pominięto rzeczywisty mimośród, membranowe przenoszenie sił i podatny styk belka–panel. To redukcja, nie pełny model sklejonego przekroju; nie wolno deklarować, że daje gwarantowaną dolną granicę sztywności urządzenia. Osiowe spoiny na końcach pionowych listew uwzględniono osobno.

## Równania i jednostki

Dla pionowej listwy o polu A, długości L, module E i dwóch spoinach t_g,E_g:

`k_leg = 1 / [L/(E A) + 2 t_g/(E_g A)]` [N/m].

Jej lokalny port jest średnim przemieszczeniem płaty styku bᵀq, nie pojedynczym węzłem. W oddychaniu wkład do macierzy jednej z dwóch jednakowych płyt wynosi `2 k_leg b bᵀ`; przy wspólnym ruchu wynosi zero. Zgodna masa osiowa na jedną płytę wynosi odpowiednio `m_leg/6` i `m_leg/2`, mnożone przez b bᵀ. To wynika z całki energii pręta o liniowym polu prędkości pomiędzy dwoma końcami.

`K = K_MITC + K_obwód + Σ Tᵀ K_beam T + Σ 2 k_leg b bᵀ`,
`M = M_MITC + Σ Tᵀ M_beam T + Σ m_eff b bᵀ`.

Energia sprężyn obwodu to `½ ∮ (k_t w² + k_r theta_n²) ds`. Dlatego k_t ma jednostkę N/m², a k_r N. Płyta nie ma tu narzuconego zerowego w na krawędziach. Małe drgania: `K phi = omega² M phi`. Statyka: `K q=F p`. Harmoniczne: `(K−omega² M+j omega C)q=F p`, gdzie `C=alpha M+beta K`, zeta=0,03 przy f1 i5f1. Ten damping nie jest zidentyfikowanym tłumieniem MDF i nie opisuje strat sprzężonego gazu.

Przy amplitudach peak moc średnia ma czynnik1/2: `P_in=−omega Im(Fᵀq)/2`, `P_loss=omega² q* C q/2`. W kodzie reszta względna porównuje oba wyrażenia bez wspólnego czynnika1/2. Nie raportujemy ich jako bezwzględnej mocy urządzenia. Nacisk jednorodny1 Pa jest portem kontrolnym, a nie polem gazu z P21. Podatność FᵀK⁻¹F [m³/Pa] dotyczy jednej płyty, nie całej komory.

## Wykonane obliczenia

''']
parts.append(f"Przeliczono **{len(rows)} modeli**, po sześć postaci oraz statykę i cztery częstotliwości20/40/80/160 Hz. Najgęstsza siatka ma {a['nx']}×{a['ny']} elementów i{a['dof']} stopni swobody. Siatki12/20/32/48/64 są nowym badaniem zbieżności tej redukcji, nie powtórzeniem dawnych kampanii.\n\n")
parts.append('| Wariant przy E=2,1 GPa, E_g=100 MPa, k_t=10⁷ N/m², k_r=1000 N | f1 [Hz] | maks. ugięcie statyczne [µm/Pa] | podatność jednej płyty [m³/Pa] |\n|---|---:|---:|---:|\n')
for label,r in [('Bez wręg, to samo otoczenie',un),('Wręgi, przednia listwa10 mm',a),('Wręgi, przednia listwa22 mm; dostęp niezaliczony',b)]:parts.append(f"| {label} | {r['f1_Hz']:.3f} | {r['wmax_m_Pa']*1e6:.6f} | {r['compliance_m3_Pa']:.8g} |\n")
parts.append(f"\nZmniejszenie listwy22→10 mm obniża f1 o{100*(1-a['f1_Hz']/b['f1_Hz']):.2f}% i zwiększa maksymalne statyczne ugięcie o{100*(a['wmax_m_Pa']/b['wmax_m_Pa']-1):.2f}%. Dodanie aktualnych wręg redukuje ugięcie o{100*(1-a['wmax_m_Pa']/un['wmax_m_Pa']):.2f}% względem braku wręg. To korzyść w tej redukcji, nie gwarancja rzeczywistej obudowy.\n\n")
parts.append('''Przy n20 zmiana samego k_t od10⁶ do10⁸ N/m² daje f1 około123,00–152,44 Hz. Zmiana E MDF1,5→3 GPa daje125,98–171,34 Hz. Zmiana E_g1→1718 MPa daje140,43–146,31 Hz. Są to oddzielne przekroje parametrów, nie wspólne globalne minimum/maksimum. W tym zakresie niepewność otoczenia i MDF jest większa niż efekt wyboru10/22 mm.

| f [Hz] | ruch [µm/Pa peak] | diagnostyczne naprężenie powierzchni płyty [Pa/Pa peak] | średnie osiowe naprężenie listwy/spoiny [Pa/Pa peak] |
|---:|---:|---:|---:|
''')
for h in a['harmonics']:parts.append(f"| {h['f_Hz']} | {h['w_peak_per_Papeak_m']*1e6:.6f} | {h['max_surface_stress_per_Papeak']:.3f} | {h['leg_mean_axial_stress_per_Papeak']:.3f} |\n")
parts.append('''
Wartości przy160 Hz znajdują się blisko postaci własnych i są bardziej czułe na siatkę/damping. Cztery częstotliwości nie wyznaczają maksimum ciągłego pasma. Sama większa sztywność może przybliżyć rezonans do konkretnej częstotliwości i zwiększyć odpowiedź: porównanie22 mm ma przy160 Hz większy ruch niż10 mm. To nie dowodzi przewagi10 mm dla wszystkich sygnałów.

## Weryfikacja, zbieżność i granice

| Siatka nx | f1 listwy10 mm [Hz] | podatność [m³/Pa] | ruch przy160 Hz [µm/Pa] |
|---:|---:|---:|---:|
''')
for n in [12,20,32,48,64]:
 r=get(n);parts.append(f"| {n} | {r['f1_Hz']:.5f} | {r['compliance_m3_Pa']:.8g} | {r['harmonics'][-1]['w_peak_per_Papeak_m']*1e6:.6f} |\n")
parts.append(f"\nOstatnia zmiana48→64: f1 {abs(a['f1_Hz']/previous['f1_Hz']-1)*100:.3f}%, podatność {abs(a['compliance_m3_Pa']/previous['compliance_m3_Pa']-1)*100:.3f}%, ruch160 Hz {abs(a['harmonics'][-1]['w_peak_per_Papeak_m']/previous['harmonics'][-1]['w_peak_per_Papeak_m']-1)*100:.3f}%. To obserwacja dwóch dyskretyzacji, nie ścisły certyfikat błędu kontinuum. Naprężenia z naroży elementów nie rozwiązują lokalnych koncentracji na krawędzi spoiny.\n\n")
nav=ctrl['controls'][-4] if False else [c for c in ctrl['controls'] if c['test']=='independent_Navier_Mindlin'][-1]
parts.append(f"Odrębny analityczny szereg Naviera–Mindlina dla płyty bez wręg/sprężyn, z podparciem SSSS: na n64 różnica podatności {abs(nav['relative_compliance'])*100:.3f}%, f1 {abs(nav['relative_f1'])*100:.3f}%. Jest to kontrola składnika płytowego w innej, rozwiązywalnej granicy, nie niezależne rozwiązanie całego nowego podzespołu.\n\n")
parts.append('''Drugą kontrolą jest odrębny wzór belki z dwiema sprężystymi podporami i jednorodnym obciążeniem q: `w_mid=5 q L⁴/(384 EI)+q L/(2k)`. Siatki4/8/16 elementów odtwarzają wartość z błędem względnym do1,63e−12. To niezależny wzorzec matematyczny, bez wywoływania kodu płyty.

Każdy przypadek sprawdza równowagę sił z sumą reakcji sprężyn i listew, energię statyczną qᵀKq=qᵀF oraz harmoniczny bilans strat. Progi reszt ustalono w kodzie na1e−7; wyniki są rzędu1e−12 lub mniejsze dla energii i równowagi. Reszta rozwiązania liniowego jest osobną diagnostyką. Składowe macierzy mają nieujemną energię: dodatnie materiały, zgodna masa, dodatnie sprężyny. Wyłączenie wręg daje zachowaną rodzinę porównawczą. W granicy wspólnej translacji pręty nie mogą dostarczać osiowej siły przywracającej: kod ustawia jej współczynnik na0 zamiast błędnie zostawiać2k.

![Pola podzespołu](../wyniki/p18e_pola.png)
![Zbieżność i odpowiedź harmoniczna](../wyniki/p18e_wrazliwosc.png)

## Grawitacja, orientacje i wymagania materiałowe

Dla ustawienia poziomego policzono normalny ciężar paneli, belek i przypisanej części masy listew jako `f_g=M r g` w rodzinie wspólnego ruchu. Nie obejmuje to ciężaru głośnika, wkładów ani całości korpusu: ich mocowania wymagają odrębnego modelu. Dla obrotu skrzyni o90° wokół osi głębokości grawitacja leży w płaszczyźnie tych dwóch paneli, więc normalna składowa tej konkretnej analizy wynosi0; obciążenie w płaszczyźnie, ścinanie spoin, ugięcie innych paneli i stopnie swobody całego zespołu **nie zostały rozstrzygnięte**. Nie jest to zaliczenie bezpieczeństwa pion/poziom.

''')
g=[r for r in rows if r['parity']=='common' and r['front']==.01];g.sort(key=lambda r:r['nx']);parts.append('| nx | normalne ugięcie od własnego ciężaru podzespołu [µm] |\n|---:|---:|\n')
for r in g:parts.append(f"| {r['nx']} | {r['gravity_common_normal_deflection_m']*1e6:.4f} |\n")
parts.append('''
Dla kryterium pomocniczego „podatność obu spoin najwyżej5% osiowej podatności listwy” otrzymujemy z samej algebry `E_g ≥ 2 t_g E/(0,05 L)`; przy E=2,1 GPa i L=412 mm jest to **50,97 MPa**. Jest to warunek sztywności w przyjętej geometrii. Nie oznacza nośności, adhezji, odporności na odrywanie, pełzania lub zmęczenia. E_g musi być modułem efektywnym właściwym dla temperatury/czasu/wilgotności; nominalne E w krótkiej próbie może nie spełniać warunku w eksploatacji.

Dla dowolnej założonej amplitudy ciśnienia peak p* wymagane przeniesienie średniego naprężenia osiowego wynika z tabeli jako `sigma_req=p* sigma_per_Pa`. W paśmie20–80 Hz i przy p*=2500 Pa daje ono około0,37 MPa dla nominalnej listwy10 mm; naprężenie powierzchni płyty około0,66 MPa. Największa obliczona siła osiowa listwy przy statycznym jednorodnym1000 Pa wynosi37,37 N; przy2500 Pa:93,42 N. Wymagania dotyczą obu identycznie obciążonych spoin końcowych listwy, nie sumy dwóch sił na jednej spoinie. Pod obrotem całego zespołu kierunek tych sił względem listwy nie zmienia się, ale dochodzi inne obciążenie grawitacyjne, którego pełnej kombinacji tutaj nie policzono. To obciążenia modelowe, **bez współczynnika bezpieczeństwa i bez zatwierdzonej nośności**. p*=250/1000/2500 Pa są ekranami skalowania, nie zmierzonym ciśnieniem z głośnika. Rzeczywiste pole przestrzenne należy przenieść przez wspólny port P21.

Wymagania przed kwalifikacją: rzeczywista nośność MDF i spoin w rozciąganiu/ścinaniu/odrywaniu, efektywne E(t,T,RH), Gc, S–N i jakość laminacji; siły od kosza i modułów; miejscowe naciski i karby; mimośród belek oraz transfer do stóp. Bez tych danych nie wyznaczono trwałości, liczby cykli, maksymalnej bezpiecznej amplitudy ani dopuszczalnego obciążenia całej skrzyni.

## Decyzja i następny krok

Zachować10 mm jako **wariant badawczy umożliwiający dostęp**, a nie jako zatwierdzoną konstrukcję. Jego mechaniczny koszt wobec22 mm jest umiarkowany w policzonym przekroju parametrów, lecz otaczająca rama i podatność połączeń mają większy wpływ. Nie wracać automatycznie do22 mm, bo naruszyłoby to tor wkładów. Jeśli pełna rama ujawni zbyt duży ruch, szukać wzmocnienia zachowującego korytarz: zmiana przekroju/położenia poza nim wymaga nowego bilansu i kontroli kolizji.

P18/P19 są nadal częściowe: ukończono rodzinę zredukowanych podpór, ale nie model frontu z otworem, pełną bryłę, naprężenia lokalne i grawitację wszystkich elementów. Następny krok to pełna rama P18C/P19D z tą geometrią i portami z P21, albo ilościowo uzasadniona redukcja z kalibracją na wybranych pełnych rozwiązaniach. Ten raport nie zmienia samodzielnie rankingu C02/C11/C06 i nie stanowi zgody na CNC.

Odtwarzanie:

```bash
OPENBLAS_NUM_THREADS=1 python skrypty/mechanika_podatnych_wreg_P18E.py
python skrypty/raportuj_podatne_wregi_P18E.py
```

Wejścia: `dane/konfiguracje/p18e_podatne_wregi.json` i geometria P20D. Wyniki: `p18e_przypadki.json`, `p18e_kontrole.json`, dwa wykresy i `p18e_manifest.json`. Podstawy i wcześniejsze kontrole: raport029/P18A oraz raporty035–041/P18C–P19G. Nie pozyskano nowych danych materiałowych producenta; wszystkie dodatkowe moduły i sprężyny mają status scenariuszy.
''')
p=R/'raporty/059_podatne_wregi_i_panele.md';p.write_text(''.join(parts))
manifest=json.loads((O/'p18e_manifest.json').read_text())
for f in [p,Path(__file__)]:manifest[str(f.relative_to(R))]=hashlib.sha256(f.read_bytes()).hexdigest()
(O/'p18e_manifest.json').write_text(json.dumps(manifest,indent=2))
print(p)
