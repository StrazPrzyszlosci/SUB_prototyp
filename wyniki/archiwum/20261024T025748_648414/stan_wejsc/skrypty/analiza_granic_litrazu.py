"""P07: granice bez narzuconych20–150l; kontrola gęstą siatką i inną oceną."""
from dataclasses import replace
import csv,json
from pathlib import Path
import numpy as np
import sympy as sp
from scipy.optimize import minimize_scalar
from model_subwoofera import Driver,response
from granice_litrazu import global_bound

ROOT=Path(__file__).resolve().parents[1]


def main():
    re,le,omega,rms,bl=sp.symbols('Re Le omega Rms BL',positive=True)
    kappa=sp.symbols('kappa',real=True)
    polynomial=(re*kappa-omega**2*le*rms)**2+(omega*le*kappa+omega*(re*rms+bl**2))**2
    expanded=(re**2+(omega*le)**2)*kappa**2+2*omega**2*le*bl**2*kappa+omega**4*le**2*rms**2+omega**2*(re*rms+bl**2)**2
    assert sp.simplify(polynomial-expanded)==0
    stationary=-omega**2*le*bl**2/(re**2+(omega*le)**2)
    assert sp.simplify(sp.diff(polynomial,kappa).subs(kappa,stationary))==0
    raw=json.loads((ROOT/'dane/przetworniki/pula_rozszerzona.json').read_text())
    rows=[];max_grid_excess=0.;max_boundary_error=0.
    for r in raw['drivers']:
        d=Driver(**r['model'])
        for f in (20.,25.,31.5,40.,63.,80.):
            for v,i in ((40.,12.),(60.,20.)):
                bound=global_bound(d,f,v,i)
                # Odrębna ocena w podstawowym modelu po obu stronach przestrzeniVb.
                grid=np.geomspace(.01,1e7,1200)
                def achieved(vb):
                    one=response(d,vb,np.array([f]))
                    drive=min(v,i/one['i_rms'][0],d.xmax_mm*.001/one['x_peak_m'][0])
                    return float(one['spl_rms_db'][0]+20*np.log10(drive))
                numeric=np.array([achieved(vb) for vb in grid])
                peak=int(np.argmax(numeric))
                optimized=minimize_scalar(lambda logv:-achieved(np.exp(logv)),
                    bounds=(np.log(grid[max(0,peak-1)]),np.log(grid[min(len(grid)-1,peak+1)])),method='bounded')
                excess=max(numeric.max(),-optimized.fun)-bound['single_frequency_spl_2pi_1m_db']
                max_grid_excess=max(max_grid_excess,float(excess))
                assert excess<2e-8
                for key in ('vb_min_within_tolerance_l','vb_max_within_tolerance_l'):
                    if bound[key] is not None:
                        err=abs(achieved(bound[key])-(bound['single_frequency_spl_2pi_1m_db']-.5))
                        max_boundary_error=max(max_boundary_error,err)
                        assert err<1e-6
                rows.append({'candidate_id':r['candidate_id'],'driver':d.name,'f_hz':f,'amp_vrms':v,'amp_irms':i,**bound})
    # Le=0 i dobórV/I z Re: przypadki degeneracji wielomianu przecięcia.
    d=replace(Driver(**raw['drivers'][0]['model']),le_mh=0.)
    for f in (20.,80.):
        x=global_bound(d,f,d.re_ohm*12.,12.)
        assert np.isfinite(x['single_frequency_spl_2pi_1m_db'])
    with (ROOT/'wyniki/pula_granice_globalne_Vb.csv').open('w',newline='',encoding='utf-8') as h:
        w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    summary={'status':'EKSTREMA_MODELU_SINUSOIDALNEGO_NIE_FINALNY_LITRAZ','cases':len(rows),
             'symbolic_checks':['Rozwinięcie modułu mianownika','Stacjonarność granicy napięciowej'],
             'numeric_grid_volume_l':[.01,1e7],'grid_points':1200,
             'max_numeric_excess_over_analytic_bound_db':max_grid_excess,
             'max_near_optimal_boundary_error_db':max_boundary_error,
             'selected_20hz':[r for r in rows if r['f_hz']==20 and r['candidate_id'] in ('C02','C06','C11','C20','C21')],
             'limitations':'Brak sprzężonej optymalizacji pasma/DSP/termiki/konstrukcji. None dlaVbmax oznacza nieograniczony górny zakres, a nie brak danych.'}
    (ROOT/'wyniki/pula_granice_globalne_Vb.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
    print('P07:',len(rows),'przypadki; przewyższenie granicy=',max_grid_excess,'dB; błąd brzegów=',max_boundary_error,'dB')


if __name__=='__main__':main()
