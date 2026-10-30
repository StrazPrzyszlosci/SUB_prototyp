from pathlib import Path
import json,csv,hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pilot_P21C_geometria import transverse_tail_bound
ROOT=Path(__file__).resolve().parents[1];O=ROOT/'wyniki'
def main():
 s=json.loads((O/'p21c1_podsumowanie.json').read_text());rows=list(csv.DictReader((O/'p21c1_membrana.csv').open()));pairs=list(csv.DictReader((O/'p21c1_przesuniecie.csv').open()))
 for r in rows:
  for k in ['volume_l','depth_ext_m','aspect','width_ext_m','height_ext_m','sd_m2','x_fraction','f_hz','R','tail_bound','square_R','circle_minus_square']:r[k]=float(r[k])
  r['square_tail_bound']=transverse_tail_bound((r['width_ext_m']-.044,r['depth_ext_m']-.044,r['height_ext_m']-.044),(np.sqrt(r['sd_m2']),)*2,r['f_hz'],320,343.)
 # Difference R_disk-R_square lies in [computed-B_disk,computed+B_square].
 shape=max(rows,key=lambda r:abs(r['circle_minus_square']));mass=s['max_offset_mass']
 fig,ax=plt.subplots(1,2,figsize=(11,4.5))
 for cid,color in [('C02','#127d89'),('C04','#b86a20'),('C25','#7953a5')]:
  for frac,style in [(.5,'-'),(.25,'--')]:
   q=[r for r in rows if r['product']==cid and r['volume_l']==150 and r['depth_ext_m']==.5 and r['aspect']==1.5 and r['x_fraction']==frac]
   ax[0].plot([r['f_hz'] for r in q],[r['R'] for r in q],style,color=color,label=f'{cid}, x/W={frac}')
 ax[0].set(xlabel='Częstotliwość [Hz]',ylabel='R: nacisk względem gazu 0D',title='150 l brutto; D=500 mm; W/H=1,5');ax[0].legend(fontsize=8);ax[0].grid(alpha=.2)
 for depth,col in [(.35,'#127d89'),(.425,'#b86a20'),(.5,'#7953a5')]:
  q=[p for p in pairs if float(p['depth_ext_m'])==depth]
  ax[1].scatter([float(p['volume_l']) for p in q],[1000*float(p['delta_mass_kg']) for p in q],s=12,alpha=.35,label=f'D={depth*1000:g} mm',color=col)
 ax[1].set(xlabel='Puste wnętrze brutto [l]',ylabel='Zmiana modelowej masy powietrza [g]',title='Przesunięcie x/W: 0,5 → 0,25');ax[1].legend(fontsize=8);ax[1].grid(alpha=.2)
 fig.suptitle('Jednorodny tłok kołowy; sztywna pusta komora — bez prognozy SPL i THD',fontsize=11);fig.tight_layout();fig.savefig(O/'96_P21C1_membrana_i_przesuniecie.png',dpi=170);plt.close(fig)
 ex=[]
 for cid in ['C02','C04','C25']:
  q=[r for r in rows if r['product']==cid and r['volume_l']==150 and r['depth_ext_m']==.5 and r['aspect']==1.5 and r['f_hz']==80]
  p=next(p for p in pairs if p['product']==cid and float(p['volume_l'])==150 and float(p['depth_ext_m'])==.5 and float(p['aspect'])==1.5)
  ex.append(f"| {cid}: {q[0]['model']} | {q[0]['sd_m2']*1e4:.1f} | {next(r['R'] for r in q if r['x_fraction']==.5):.6f} | {next(r['R'] for r in q if r['x_fraction']==.25):.6f} | {float(p['delta_mass_kg'])*1000:.3f} |")
 report=r'''# Raport 051 — P21C1: kołowa membrana i bezwładność powietrza

Data: 2026-10-30. **Obliczenia modelowe; brak pomiarów. Wyłącznie praca lokalna, bez publikacji i PR.**

## Pytanie i zakres

Czy wnioski P21C0 pozostają po zastąpieniu kwadratu kołem o powierzchni
katalogowego Sd? Zbadano 26 produktów z zamrożonej puli repozytorium.
C26P/C26S mają tę samą powierzchnię: policzono jeden port akustyczny,
bez tworzenia dwóch pozornie niezależnych geometrii. Nie aktualizowano kart producentów.
Koło o promieniu sqrt(Sd/pi) jest **założonym tłokiem równoważnym**, nie
odwzorowaniem stożka, zawieszenia, kosza lub otworu montażowego.

27 wnętrz: 60/100/150 l, głębokość zewnętrzna 350/425/500 mm,
W/H=1/1,5/2. Ściany geometryczne 22 mm, akustycznie sztywne;
c=343 m/s i rho=1,2 kg/m³ to założenia. Źródło na froncie,
z=H/2 i x=W/2 albo W/4; osobne częstotliwości 20/25/31,5/40/63/80 Hz.
Brak regulatora, wypełnienia, strat, ścian podatnych, kosza i napędu.
Objętości są brutto pustego wnętrza; nie finalnym Vb netto.

## Wyprowadzenie

Uśrednienie modu cosinusowego po dysku daje

\[
b_{nl}=\cos(n\pi x_c/W)\cos(l\pi z_c/H)
\frac{2J_1(a\kappa_{nl})}{a\kappa_{nl}},\qquad
\kappa_{nl}^2=(n\pi/W)^2+(l\pi/H)^2.
\]

W zerze iloraz ma granicę 1. Wzór wynika z całki Fouriera jednorodnego
koła; osobno sprawdzono go całkowaniem po cięciwach. Kwadraty b razy
wagi epsilon (1 dla zera, 2 dla dodatniego indeksu) wchodzą do tej samej
sumy głębokości D cot(qD)/q co w raporcie 050. R oznacza nacisk
zwrotny na tłok przy zadanym ruchu, podzielony przez nacisk gazu 0D.
Nie oznacza stosunku SPL na zewnątrz.

**Granica ogona:** Parseval daje sumę wszystkich wag b² = WH/(pi a²).
Po odjęciu policzonego prostokąta indeksów zostaje dodatnia reszta E_N.
Poza nim kappa >= pi(N+1)/max(W,H). Poniżej pierwszego modu
pominięte składniki są ujemne, a ich moduł maleje z kappa. Zatem

\[
R_N-B_N\le R\le R_N,\qquad
B_N=E_N k^2D\frac{\coth(D\alpha_{min})}{\alpha_{min}},
\quad \alpha_{min}=\sqrt{[\pi(N+1)/\max(W,H)]^2-k^2}.
\]

To analityczne ograniczenie ucięcia ocenione w float, nie certyfikat
przedziałowy obejmujący zaokrąglenia ani niepewność danych producenta.
Policzono rzędy 80/160/320. Dla kwadratu o identycznej powierzchni
użyto osobnej granicy ogona z P21C0; oba źródła mieszczą się na froncie.

W granicy małej częstotliwości K_g R = K_g - omega² M_air + O(omega⁴),
gdzie K_g=rho c² Sd²/V, a

\[
M_{air}=\frac{\rho S_d^2}{V}\left[\frac{D^2}{3}+
\sum_{(n,l)\ne(0,0)}\epsilon_n\epsilon_l b_{nl}^2
\frac{D\coth(\kappa_{nl}D)}{\kappa_{nl}}\right].
\]

To bezwładność wewnętrznego gazu w zadanej geometrii, nie Mms ani Mmd.
Różnica dwóch pozycji tego samego tłoka usuwa wspólną nieznaną bazową
masę przetwornika. Nie usuwa zmian promieniowania zewnętrznego przy
przesunięciu na skończonym froncie; ich tutaj nie policzono.

## Wyniki

'''
 report+=f"Dopuszczono {s['accepted_sources']} źródeł, odrzucono geometrycznie {s['rejected_sources']}; wykonano **{s['frequency_points']} punktów** i {s['paired_positions']} par położeń. Odrzucenie dotyczy tylko wystawania równoważnego dysku poza front, nie kwalifikacji całego głośnika.\n\n"
 report+='Przykłady: 150 l brutto, D zewnętrzne 500 mm, W/H=1,5, 80 Hz. Ostatnia kolumna to granica niskoczęstotliwościowa, nie masa dopasowana przy 80 Hz.\n\n| Model | Sd [cm²] | R centralnie | R przesunięty | Delta M_air [g] |\n|---|---:|---:|---:|---:|\n'+'\n'.join(ex)+'\n\n'
 report+=f"Największa znaleziona różnica koło–kwadrat przy równym Sd wynosi {shape['circle_minus_square']:.6f} jednostki R: {shape['case']}, {shape['f_hz']:g} Hz. Jej przedział ucięcia wynosi [{shape['circle_minus_square']-shape['tail_bound']:.6f}; {shape['circle_minus_square']+shape['square_tail_bound']:.6f}]. To różnica kształtu kontrolnego źródła, nie poprawa jakości produktu.\n\n"
 report+=f"Największa zmiana M_air po przesunięciu: {1000*mass['delta_mass_kg']:.3f} g dla {mass['product']}, {mass['volume_l']} l, D={mass['depth_ext_m']*1000:g} mm, W/H={mass['aspect']}; przedział ucięcia [{1000*mass['delta_mass_lower_kg']:.3f}; {1000*mass['delta_mass_upper_kg']:.3f}] g. To maksimum znalezione w skończonej siatce.\n\n"
 report+='![Membrana i położenie](../wyniki/96_P21C1_membrana_i_przesuniecie.png)\n\n'
 report+=f"## Kontrole i ograniczenia\n\nNajwiększa zmiana 160→320: {s['max_last_change']:.8g} R; największa granica ogona: {s['max_tail_bound']:.8g} R. Sześć odrębnych całek po dysku sprawdza sprzężenie źródła. Trzy świadki sprawdzają obrót, granicę masową przy 0,1 Hz i dalsze zagęszczenie do 640. Każdy przebieg kampanii sprawdza znak zmiany i zgodność z granicą poprzedniego rzędu. To kontrola matematyczna własnego modelu, nie niezależna recenzja lub nowa walidacja FV wszystkich punktów.\n\n"
 report+=r'''## Znaczenie dla decyzji

| Kryterium | Wynik modelowy | Co pozostaje nieznane | Warunek dalszego użycia / następny krok |
|---|---|---|---|
| Powierzchnia źródła | Koło z Sd i porównanie równej powierzchni | Kształt stożka i ruch zawieszenia | Zachować port skończony; nie zastępować go monopolem |
| Pozycja | R i zmiana wewnętrznej bezwładności dla dwóch pozycji | Front zewnętrzny, kosz i wzmocnienia | Porównać pełny bilans mas bez podwójnego Mms |
| Głębokość | Wszystkie warianty ≤500 mm | Wyporność kosza, prześwity i osprzęt | Sprawdzić rysunek montażowy i bilans netto |
| Regulacja i wypełnienie | Tutaj nie są modelowane | Przestrzenne straty i objętość zajęta | Następne obliczenie: port kołowy z warstwą porowatą i przegrodą |
| Ostateczny wybór | Brak rankingu produktów | Sprzężony napęd, ciepło, DSP, pokój | Zintegrować przed wyborem; prototyp zweryfikować pomiarowo |

Przesunięcie nadal zmienia nacisk po zastąpieniu kwadratu kołem.
Nie wynika stąd automatycznie, że centralne położenie daje lepszy bas.
Zamknięto wyłącznie krok P21C1; pełne P21C i wybór prototypu pozostają otwarte.

## Odtworzenie

```bash
OPENBLAS_NUM_THREADS=1 python3 skrypty/membrana_kolowa_P21C1.py
OPENBLAS_NUM_THREADS=1 python3 skrypty/raportuj_P21C1.py
```

Wejścia i wersje bibliotek zapisano w `wyniki/p21c1_podsumowanie.json`.
Pliki wynikowe: `p21c1_membrana.csv`, `p21c1_odrzucenia.csv`,
`p21c1_przesuniecie.csv`. Manifest zawiera kod, wejścia, brief i wyniki.
Nie pozyskano nowych danych producentów i nie wykonano pomiarów.
'''
 (ROOT/'raporty/051_P21C1_membrana_kolowa_i_bezwladnosc.md').write_text(report)
 paths=[ROOT/p for p in s['input_sha256']]+[Path(__file__),ROOT/'raporty/051_P21C1_membrana_kolowa_i_bezwladnosc.md',O/'96_P21C1_membrana_i_przesuniecie.png']+list(O.glob('p21c1_*.csv'))+[O/'p21c1_podsumowanie.json']
 (O/'manifest_P21C1.json').write_text(json.dumps({str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},indent=2))
 print(json.dumps({k:s[k] for k in ['accepted_sources','rejected_sources','frequency_points','max_tail_bound','max_last_change','max_offset_mass']},indent=2))
if __name__=='__main__':main()
