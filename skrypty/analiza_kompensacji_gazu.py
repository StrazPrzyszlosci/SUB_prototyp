"""P13: czy kwadratowy człon gazu może kompensować asymetrię zawieszenia?

Dokładna algebra Taylora przy x=0, potem pełne nieliniowe ODE; bez
przypisywania takiej kompensacji konkretnemu wyprodukowanemu głośnikowi.
"""
import csv
import json
from pathlib import Path
import numpy as np
import sympy as s
from model_subwoofera import Driver
from model_gazu import Medium,ThermalSpectrum,gas_response
from model_nieliniowy import Plant,Shape,NonlinearModel,simulate_sine

ROOT=Path(__file__).resolve().parents[1]


def main():
    x,p0,sd,vb,gamma,cms,x0,k1=s.symbols('x p0 Sd V gamma Cms X0 k1',positive=True)
    gas_force=p0*sd*((1+sd*x/vb)**(-gamma)-1)
    coefficient=s.simplify(s.diff(gas_force,x,2).subs(x,0)/2)
    cancellation=s.simplify(coefficient*cms*x0)
    assert s.simplify(cancellation-gamma*(gamma+1)*p0*sd**3*cms*x0/(2*vb**2))==0
    raw=json.loads((ROOT/'dane/przetworniki/pula_rozszerzona.json').read_text())['drivers']
    m=Medium();rows=[]
    for cid in ['C02','C06']:
        d=Driver(**next(r for r in raw if r['candidate_id']==cid)['model']);plant=Plant.from_driver(d)
        for volume in [30.,100.]:
            star=m.gamma*(m.gamma+1)/2*m.p0_pa*plant.sd**3*plant.cms*plant.xref/(volume*.001)**2
            k2=max(.4,star*star)
            for f in [20.,40.]:
                linear=gas_response(d,volume,[f],ThermalSpectrum((np.inf,),(1.,)),vrms=1.)
                for target in [.2,.6,.9]:
                    voltage=min(target*plant.xref/linear['x_peak_m'][0],40.,12./linear['i_rms_a'][0])
                    for multiplier in [-1.,0.,1.]:
                        shape=Shape(k_asym=multiplier*star,k_quad=k2)
                        model=NonlinearModel(plant,volume,shape,np.inf,True)
                        result=simulate_sine(model,f,voltage,method='Radau',rtol=1e-11,atol=1e-13,
                                             samples_per_cycle=512,closure_tolerance=1e-8)
                        rows.append(dict(candidate_id=cid,volume_l=volume,f_hz=f,target_linear_x_fraction=target,
                                         voltage_rms_v=float(voltage),cancellation_multiplier=multiplier,
                                         k_asym=float(multiplier*star),k_quad=k2,**result))
            print('P13 kompensacja:',cid,volume,flush=True)
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with (ROOT/'wyniki/p13_kompensacja_gazu.csv').open('w',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=fields);writer.writeheader();writer.writerows(rows)
    ratios=[]
    for r in rows:
        if r['cancellation_multiplier']!=1 or r['status']!='PERIODIC_WITHIN_MODEL_TOLERANCE':continue
        base=next(t for t in rows if t['candidate_id']==r['candidate_id'] and t['volume_l']==r['volume_l']
                  and t['f_hz']==r['f_hz'] and t['target_linear_x_fraction']==r['target_linear_x_fraction']
                  and t['cancellation_multiplier']==0)
        ratios.append(r['h2_pressure_pct']/base['h2_pressure_pct'])
    result=dict(status='WARUNKOWA_KOMPENSACJA_CZLONU_KWADRATOWEGO_NIE_KONSTRUKCJA_ZIDENTYFIKOWANA',
                quadratic_gas_force_coefficient=str(coefficient),k_asym_cancel_formula=str(cancellation),
                rows=len(rows),min_H2_ratio_to_zero_asymmetry=min(ratios),max_H2_ratio_to_zero_asymmetry=max(ratios),
                scope='Stałe napięcie w porównaniu, gaz adiabatyczny z entropią początkową, BL/Le liniowe. Skasowanie kwadratu siły nie usuwa wyższych rzędów, H3, pamięci cieplnej ani zależności częstotliwościowej.',
                shape_status='Tylko hipotetyczna asymetria, nie krzywa zawieszenia C02/C06.')
    (ROOT/'wyniki/p13_kompensacja_gazu.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print(json.dumps(result,ensure_ascii=False,indent=2));return result


if __name__=='__main__':main()
