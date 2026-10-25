"""P12C: dokładne wykluczenie jednego bieguna i dopasowania|Lgen|.

Twierdzenie dotyczy zapisanych przedziałów digitalizacji; nie tolerancji
pomiarowej ani producenta. Dopasowania wielostartowe nie są globalnymi ekstremami.
"""
import csv
from decimal import Decimal,ROUND_FLOOR,ROUND_CEILING
from fractions import Fraction
from itertools import combinations
import json
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from model_cewki_z_pamiecia import FluxBranch,generalized_inductance,blocked_impedance

ROOT=Path(__file__).resolve().parents[1]


def rational_bound(text,lower):
    # Zewnętrzne zaokrąglenie zapisanej liczby dziesiętnej do1e-12H.
    value=Decimal(text).quantize(Decimal('1e-12'),rounding=ROUND_FLOOR if lower else ROUND_CEILING)
    return Fraction(value)


def exact_one_pole_exclusion(rows):
    limits=[]
    for i,j,k in combinations(range(len(rows)),3):
        a,b,c=[Fraction(rows[n]['f_hz'])**2 for n in [i,j,k]]
        yl=[rational_bound(rows[n]['digitization_lower_h'],True)**2 for n in [i,j,k]]
        yu=[rational_bound(rows[n]['digitization_upper_h'],False)**2 for n in [i,j,k]]
        assert yl[0]>yu[1] and yl[1]>yu[2]
        rlo=(yl[0]-yu[1])/(yu[1]-yl[2]);rhi=(yu[0]-yl[1])/(yl[1]-yu[2])
        aa=(b-a)/(c-b);rzero=aa*c/a
        if rlo>=rzero or rhi<=aa:
            return dict(excluded=True,direct_triple=[i,j,k],reason='Ratio poza całym zakresemf_c²>=0')
        tl=Fraction(0) if rhi>=rzero else (aa*c-rhi*a)/(rhi-aa)
        th=None if rlo<=aa else (aa*c-rlo*a)/(rlo-aa)
        limits.append(dict(triple_indices=[i,j,k],lower=tl,upper=th))
    if not limits:return dict(excluded=False,reason='Brak użytecznych trójek; to nie dowód istnienia dopasowania')
    lower=max(limits,key=lambda x:x['lower'])
    finite=[x for x in limits if x['upper'] is not None]
    if not finite:return dict(excluded=False,required_fc2_lower_rational=str(lower['lower']),
                              reason='Warunki konieczne nie ograniczają fc² z góry; to nie dowód istnienia dopasowania')
    upper=min(finite,key=lambda x:x['upper'])
    excluded=lower['lower']>upper['upper']
    return dict(excluded=excluded,required_fc2_lower_rational=str(lower['lower']),
                required_fc2_upper_rational=str(upper['upper']),required_fc2_lower_hz2=float(lower['lower']),
                required_fc2_upper_hz2=float(upper['upper']),lower_triple=lower['triple_indices'],upper_triple=upper['triple_indices'],
                exact_positive_gap_rational=str(lower['lower']-upper['upper']),
                formula='|L|²=a+b/(1+(f/fc)²); ratio_differences=A*(fc²+fk²)/(fc²+fi²)',
                scope='Wszystkie dodatniefc,Linstant,L1 tej rodziny dla zewnętrznie zaokrąglonych zapisanych przedziałów. Nie jest stwierdzeniem o nieznanej niepewności producenta.')


def main():
    source=ROOT/'dane/zrodla/digitalizacja/Purifi_NAB01_Lgen_fig4.csv'
    with source.open() as handle:all_rows=list(csv.DictReader(handle))
    data=sorted([r for r in all_rows if float(r['position_mm'])==0],key=lambda r:float(r['f_hz']))
    exclusion=exact_one_pole_exclusion(data)
    assert exclusion['excluded']
    f=np.array([float(r['f_hz']) for r in data]);low=np.array([float(r['digitization_lower_h']) for r in data])
    high=np.array([float(r['digitization_upper_h']) for r in data]);target=np.sqrt(low*high)
    sigma=(np.log(high)-np.log(low))/2
    random=np.random.default_rng(20261024);rows=[];networks=[]
    for count,starts in [(1,16),(2,24),(3,36)]:
        for seed in range(starts):
            initial=np.r_[np.log(random.uniform(.03,.25)*1e-3),
                          np.log(random.uniform(.1,3.,count)*1e-3),
                          np.log(1/(2*np.pi*np.geomspace(40.,6000.,count))*np.exp(random.normal(0,.7,count)))]
            bounds=(np.r_[np.full(count+1,-20.),np.full(count,-16.)],
                    np.r_[np.full(count+1,-1.),np.full(count,0.)])
            def unpack(x):
                values=np.exp(x);return values[0],[FluxBranch(float(lj),float(tau)) for lj,tau in zip(values[1:count+1],values[count+1:])]
            def residual(x):
                instant,bs=unpack(x)
                return (np.log(abs(generalized_inductance(f,instant,bs)))-np.log(target))/sigma
            fit=least_squares(residual,initial,bounds=bounds,max_nfev=1600,xtol=2e-11,ftol=2e-11,gtol=2e-11)
            instant,bs=unpack(fit.x);pred=abs(generalized_inductance(f,instant,bs))
            inside=bool(np.all(pred>=low)&np.all(pred<=high))
            z=blocked_impedance(np.array([20.,100.,156.,1000.]),3.9,instant,bs)
            lg=generalized_inductance(np.array([20.,100.,156.,1000.]),instant,bs)
            gate=bool(z[2].real<=4.7)
            row=dict(network_id=f'N{count}_{seed}',branches=count,seed=seed,inside_digitization_box=inside,
                     nominal_ReZ156_gate=gate,cost=float(np.dot(fit.fun,fit.fun)),max_scaled_residual=float(max(abs(fit.fun))),
                     real_Z20_ohm=float(z[0].real),real_Z156_ohm=float(z[2].real),
                     Lgen_phase20_deg=float(np.angle(lg[0],deg=True)),Lgen_phase100_deg=float(np.angle(lg[1],deg=True)),
                     Lgen_phase1000_deg=float(np.angle(lg[3],deg=True)),nfev=fit.nfev,
                     local_jacobian_rank=int(np.linalg.matrix_rank(fit.jac,tol=1e-7)),parameters=2*count+1)
            rows.append(row)
            if inside:networks.append(dict(**row,instant_h=instant,branch_parameters=[dict(inductance_h=b.inductance_h,tau_s=b.tau_s) for b in bs]))
        print('P12C dopasowania:',count,'biegunów',flush=True)
    with (ROOT/'wyniki/p12c_dopasowania_Lgen.csv').open('w',newline='') as handle:
        w=csv.DictWriter(handle,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    accepted=[n for n in networks if n['nominal_ReZ156_gate']]
    # Znalezione świadki, nie globalne obwiednie parametrów/phase.
    witnesses=[]
    if accepted:
        for key in ['Lgen_phase20_deg','real_Z156_ohm']:
            for selector in [min,max]:
                item=selector(accepted,key=lambda n:n[key])
                if item['network_id'] not in [w['network_id'] for w in witnesses]:witnesses.append(item)
    # Dokładna konstrukcja: stały moduł jednego skalaru nie daje zerowej pochodnej zespolonej.
    q=np.linspace(-1.,1.,101);beta=.1;phi=-np.pi/6+beta*q;mag=.001;fp=100.;fx=100.
    instant=mag*(np.cos(phi)+np.sin(phi));lbranch=-2*mag*np.sin(phi)
    assert np.all(instant>0)&np.all(lbranch>0)
    value=instant+lbranch/(1+1j*fx/fp)
    flat_error=float(max(abs(abs(value)/mag-1)))
    force_kernel_magnitude=mag*beta/.01/2
    result=dict(status='DIGITALIZACJA_I_WARUNKOWE_DOPASOWANIA_NIE_IDENTYFIKACJA_PRODUKTU',
                source_points=len(data),one_pole_exact_exclusion=exclusion,
                fits=len(rows),within_digitization_box=len(networks),within_box_and_nominal_gate=len(accepted),
                fits_by_order={str(n):dict(attempts=sum(r['branches']==n for r in rows),
                                           accepted=sum(r['branches']==n and r['inside_digitization_box'] for r in rows)) for n in [1,2,3]},
                witnesses=witnesses,constant_magnitude_counterexample=dict(max_relative_magnitude_error=flat_error,
                    phase_range_deg=[float(min(phi)*180/np.pi),float(max(phi)*180/np.pi)],
                    force_kernel_abs_N_A2=force_kernel_magnitude,
                    scope='Jawna dodatnia rodzina Linstant,L1,tauconst. Stały|Lgen| przy100Hz, niezerowa pochodna fazy. To nie jest krzywa Purifi.'),
                fit_domain='L w exp([-20,-1])H,tau w exp([-16,0])s; wyłącznie wielostartowy search, nie certyfikat globalnych ekstremów',
                warning='Przedziały opisują digitalizację wykresu, nie pełną niepewność źródła. Kalibracja x=0 nie identyfikuje pochodnej zespolonej po x.')
    (ROOT/'wyniki/p12c_ident_Le.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print(json.dumps({k:v for k,v in result.items() if k!='witnesses'},ensure_ascii=False,indent=2));return result


if __name__=='__main__':main()
