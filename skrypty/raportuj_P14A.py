"""Raport częściowy P14A; pilot i wzorzec, bez zamykania całego P14/P25."""
import csv
import json
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/sub-krystian-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from model_subwoofera import Driver
from model_nieliniowy import Plant
from model_cewki_z_pamiecia import linear_memory_response
from analiza_cewki_z_pamiecia import dynamic_network

ROOT=Path(__file__).resolve().parents[1]


def load_rows(name):
    with (ROOT/'wyniki'/name).open() as handle:return list(csv.DictReader(handle))


def save(fig,name):
    fig.tight_layout()
    for ext in ['png','svg']:fig.savefig(ROOT/'wyniki'/f'{name}.{ext}',dpi=170)
    plt.close(fig)


def main():
    cfg=json.loads((ROOT/'dane/konfiguracje/p14a_sygnaly_i_pilot.json').read_text())
    memory=json.loads((ROOT/'dane/konfiguracje/p12c_pamiec_cewki.json').read_text())
    result=json.loads((ROOT/'wyniki/p14a_podsumowanie.json').read_text())
    checks=json.loads((ROOT/'wyniki/p14a_weryfikacja.json').read_text())
    reference=load_rows('p14a_wspolne_ograniczenia.csv');pilot=load_rows('p14a_pilot_IMD.csv')
    raw=json.loads((ROOT/'dane/przetworniki/pula_rozszerzona.json').read_text())['drivers']
    by_id={r['candidate_id']:r for r in raw};fundamental=[]
    for row in pilot:
        plant=Plant.from_driver(Driver(**by_id[row['candidate_id']]['model']))
        profile='FLUX_ONE' if row['profile']=='NL_FLUX_ONE' else 'SIMPLE'
        instant,branches,_=dynamic_network(plant,profile,memory)
        ref=linear_memory_response(plant,cfg['pilot_volume_l'],cfg['pilot_pair_hz'],instant,branches)
        for k,f in enumerate(cfg['pilot_pair_hz']):
            expected=abs(ref['pressure_equivalent_pa'][k])*float(row['voltage_scale'])*cfg['pilot_weights'][k]
            fundamental.append(dict(candidate_id=row['candidate_id'],profile=row['profile'],phase2_rad=float(row['phase2_rad']),
                                    f_hz=f,matched_linear_pressure_rms_pa=float(expected),
                                    actual_pressure_rms_pa=float(row[f'fundamental{k+1}_rms_pa']),
                                    delta_vs_matched_linear_db=float(20*np.log10(float(row[f'fundamental{k+1}_rms_pa'])/expected))))
    with (ROOT/'wyniki/p14a_skladowe_podstawowe.csv').open('w',newline='') as handle:
        w=csv.DictWriter(handle,fieldnames=list(fundamental[0]));w.writeheader();w.writerows(fundamental)
    fig,axes=plt.subplots(1,2,figsize=(12,5))
    for f1,f2 in cfg['tone_pairs_hz']:
        part=[r for r in reference if r['candidate_id']=='C02' and float(r['volume_l'])==100 and r['profile']=='SIMPLE'
              and float(r['weight1'])==1 and float(r['weight2'])==1 and int(r['f1_hz'])==f1 and int(r['f2_hz'])==f2]
        n1=f1/np.gcd(f1,f2)
        x=[float(r['phase2_rad'])/(2*np.pi/n1) for r in part]
        axes[0].plot(x,[float(r['change_from_separate_db']) for r in part],'o-',label=f'{f1}+{f2}Hz')
        axes[1].plot(x,[20*np.log10(float(r['scale_joint'])/float(r['scale_phase_independent'])) for r in part],'o-',label=f'{f1}+{f2}Hz')
    axes[0].set(xlabel='Faza drugiego tonu / okres klasy fazowej',ylabel='Wspólna skala względem osobnych limitów [dB]',title='C02/100l; dwa tony, liniowy wzorzec')
    axes[1].set(xlabel='Faza drugiego tonu / okres klasy fazowej',ylabel='Zapas względem osłony trójkątnej [dB]',title='Zależność szczytu od fazy, nie miara THD')
    for ax in axes:ax.grid(alpha=.25);ax.legend()
    save(fig,'29_wspolny_limit_dwoch_tonow')
    fig,axes=plt.subplots(1,2,figsize=(12,5));profiles=['LINEAR','NL_SIMPLE','NL_FLUX_ONE'];x=np.arange(3)
    for offset,cid in [(-.17,'C02'),(.17,'C06')]:
        part=[next(r for r in pilot if r['candidate_id']==cid and r['profile']==p and float(r['phase2_rad'])==0) for p in profiles]
        axes[0].bar(x+offset,[float(r['IM2_diagnostic_pct']) for r in part],width=.3,label=cid)
    axes[0].set(xticks=x,xticklabels=['Liniowy','NL bez pamięci','NL z FLUX'],ylabel='IM2 diagnostyczne [%]',title='20+85Hz; modele warunkowe, nie pomiar produktów')
    cases=[('C02','NL_SIMPLE'),('C02','NL_FLUX_ONE'),('C06','NL_SIMPLE'),('C06','NL_FLUX_ONE')]
    for offset,f in [(-.17,20),(.17,85)]:
        values=[next(r['delta_vs_matched_linear_db'] for r in fundamental if r['candidate_id']==cid and r['profile']==p
                     and r['phase2_rad']==0 and r['f_hz']==f) for cid,p in cases]
        axes[1].bar(np.arange(4)+offset,values,width=.3,label=f'{f}Hz')
    axes[1].set(xticks=np.arange(4),xticklabels=['C02 prosty','C02 FLUX','C06 prosty','C06 FLUX'],ylabel='Zmiana podstawowej względem własnego LTI [dB]',title='Harmoniczne nie opisują całej zmiany sygnału')
    for ax in axes:ax.grid(axis='y',alpha=.25);ax.legend(fontsize=8)
    save(fig,'30_pilot_dwutonowy_IMD_i_podstawowe')
    lines=[f'''# Raport 023 — P14A: wspólny limit sygnału i pilot dwutonowy

Stan:2026-10-25. **Częściowy etap P14**, nie zamknięcie badań IMD,
multitonów, sygnałów realistycznych ani całego programu. Wykonano
{result['reference_cases']}odniesień liniowych dla24baz i{result['pilot_cases']}pełnych przypadkówODE
dla C02/RSS390HF-4 i C06/STXW.32.800.8.FCX. Kształty nieliniowe są umowne,
nie charakterystykami tych produktów. Ocena postępu jest osobno w
[raporcie022](022_stan_badan_i_zakres_pozostaly.md).

## Wynik wpływający na projekt

**Osobnych limitów sinusoidalnych nie wolno sumować jako dostępnego
poziomu dla dwóch tonów.** W zadanych przypadkach wspólna skala napięcia
jest od{result['minimum_joint_vs_separate_db']:.3f}do{result['maximum_joint_vs_separate_db']:.3f}dB niższa od dopuszczonej
przez samą niezależną kontrolę składników. To porównanie obliczeniowych
budżetów, nie pomiar SPL urządzenia ani porównanie jednego/dwóch subwooferów.

Wspólna kontrola uwzględnia RMS całego napięcia i prądu, szczyt napięcia
i wychylenie sumy. Warunki:40Vrms/12Arms oraz jawny szczyt napięcia
sqrt(2)*40V wyprowadzony z budżetu sinusoidalnego. Nie jest specyfikacją
wybranego wzmacniacza. Rzeczywista ochrona i clipping pozostają P22/P24.

## Koherencja, fazy i kolizje widma

Wybrano20+85Hz i25+95Hz; podstawowa częstotliwość okresu wynosi5Hz.
Nie ma kolizji linii różnych kombinacji do3rzędu. Para20+80Hz jest
kontrolą przeciwną: linia60Hz może pochodzić z3f1 lubf2-f1, a40Hz
z2f1 lubf2-2f1. Nie należy dwukrotnie liczyć tej samej linii ani przypisywać
jej jednoznacznej przyczyny bez dodatkowej metody.

Fazy nie są wszystkie niezależnymi eksperymentami. Przy zablokowanej
fazie pierwszego tonu równoważność przesunięcia czasu daje okres fazy
drugiego tonu2pi/n1, gdzie n1=f1/gcd(f1,f2). Dla20+85Hz fazy0 i pi/2
są równoważne przesunięciu czasu. W pilocie użyto0 i pi/8, a nie dwóch
takich samych klas. Nie jest to twierdzenie o jednakowym rozruchu lub
braku wielu atraktorów dowolnego układu nieliniowego.

## Osłona błędu próbkowania szczytu

Dla ustalonych współczynników sygnału trygonometrycznego i Npróbek:

```text
M_sample <= M_true <= M_sample+0.5*sqrt(2)*sum(n²*|a_n|)*(pi/N)²
M_true <= sqrt(2)*sum(|a_n|)
```

W maksimum pochodna znika, więc rozwinięcie do drugiego rzędu ogranicza
błąd najbliższej próbki. Stosujemy minimum obu górnych osłon; przy fazach
wyrównanych sama próbka może już osiągać osłonę trójkątną. Obliczenia
wykorzystują4096próbek/okres. To matematyczna osłona próbkowania dla
ustalonych współczynnikówLTI, nie certyfikat pełnej niepewności modelu
fizycznego ani stałych zmiennoprzecinkowych. Osłona trójkątna daje również
osobny, niezależny od fazy wzorzec wspólnego ograniczenia.

## Pilot nieliniowy

W12przypadkach użyto20+85Hz, Vb100l, dwóch faz i trzech modeli: liniowy,
nieliniowy bez pamięci oraz nieliniowyFLUX. Napięcie w porównaniu profili
jest wspólne, ustalone na0,75konserwatywnego wzorca niezależnego od fazy.
Port napięciowy przyjmuje rzeczywistą w modelu sumę kosinusów; nie narzuca
się ruchu ani nie dodaje procentów zniekształceń z dwóch osobnych sinusów.

Gaz jest szczelny, tau5ms; termika cewki, clipping, rzeczywiste krzywe
przetworników i pełna emisja nie są zidentyfikowane. Pole diagnostyczne
to monopol4pi/1m/RMS z przyspieszenia. Nie jest to rzeczywisty THD produktów.
Diagnostyka ma mianownik RSS dwóch składowych podstawowych ciśnienia:

- IM2: RSS linii f2-f1 oraz f2+f1.
- IM3difference: RSS linii|2f1-f2| oraz|2f2-f1|.
- Pasmo5–1000Hz poza dwiema liniami wejściowymi: łącznie harmoniczne,
  intermodulacja i resztkowy błąd numeryczny; nie nazwano tego THD.

Nie deklarujemy zgodności tych definicji z konkretną normą. Zmianę samych
składowych podstawowych policzono oddzielnie względem dopasowanego
modelu liniowego każdej sieci, aby nie pomylić liniowych strat pamięci
z kompresją nieliniową. Faza sygnału wyjściowego i szersza analiza
amplitud pozostają dalszą pracą P14.

Wyniki dla fazy0, procenty diagnostyczne modeli:

| Baza | Model | IM2 [%] | IM3difference [%] |
|---|---|---:|---:|''']
    for r in pilot:
        if float(r['phase2_rad'])==0:lines.append(f"| {r['candidate_id']} | {r['profile']} | {float(r['IM2_diagnostic_pct']):.6g} | {float(r['IM3_difference_diagnostic_pct']):.6g} |")
    lines.append(f'''
W wybranym pilocie zmiana fazy nie dała istotnej zmiany amplitud niskich
produktów względem precyzji przebiegu. Nie dowodzi to braku wpływu fazy
w szerszych sygnałach, przy kolizjach, clippingu lub innych gałęziach.
Nie jest to ranking dwóch producentów: identycznie zadane współczynniki
względne nie są pomiarem właściwości każdego głośnika.

Wszystkie12przypadków spełniło zadane próbkowane kryterium cyklu.
Niezależny wzorzec odpowiedzi liniowej zgadza się względnie do
{checks['max_linear_oracle_relative_error']:.3g}; odrębnyRadau daje różnicę IM2/IM3 do
{checks['independent_Radau_IM_difference_pp']:.3g}punktu procentowego.
Poziom resztkowy liniowego modelu wynosi maksymalnie
{checks['linear_numerical_distortion_floor_pct']:.3g}% w paśmie diagnostyki.
Szczyty i okresowość nie są globalnym certyfikatem rozruchu/gałęzi.

**Następny krok P14B:** szersze obliczenia nieliniowe dla puli, poziomów
i sygnałów, pełne fazory/widma oraz operator promieniowania harmonicznych.
Następnie termika i konstrukcja obudowy. P14/P25 nie są zamknięte.

![Wspólny limit](../wyniki/29_wspolny_limit_dwoch_tonow.png)
![Pilot IMD](../wyniki/30_pilot_dwutonowy_IMD_i_podstawowe.png)

Wejścia:[konfiguracja](../dane/konfiguracje/p14a_sygnaly_i_pilot.json).
Kod:[sygnały](../skrypty/sygnaly_P14.py), [analiza](../skrypty/analiza_P14A_sygnaly.py),
[kontrole](../skrypty/sprawdz_P14A.py).
Wyniki:[9216odniesień](../wyniki/p14a_wspolne_ograniczenia.csv),
[12ODE](../wyniki/p14a_pilot_IMD.csv), [podstawowe](../wyniki/p14a_skladowe_podstawowe.csv),
[weryfikacja](../wyniki/p14a_weryfikacja.json).
''')
    (ROOT/'raporty/023_P14A_dwa_tony_i_wspolne_limity.md').write_text('\n'.join(lines))
    print('Zapisano raport023 i dwa wykresy')


if __name__=='__main__':main()
