"""P13: niezależny solver dla słabego H2 i opublikowanego przykładu kampanii."""
import csv
import json
from pathlib import Path
import numpy as np
from model_subwoofera import Driver
from model_nieliniowy import Plant,Shape,NonlinearModel,simulate_sine

ROOT=Path(__file__).resolve().parents[1]


def main():
    with (ROOT/'wyniki/p13_kompensacja_gazu.csv').open() as handle:rows=list(csv.DictReader(handle))
    raw=json.loads((ROOT/'dane/przetworniki/pula_rozszerzona.json').read_text())['drivers']
    drivers={r['candidate_id']:Driver(**r['model']) for r in raw}
    compensated=[r for r in rows if float(r['cancellation_multiplier'])==1]
    selected=[min(compensated,key=lambda r:float(r['h2_pressure_pct'])),
              next(r for r in compensated if r['candidate_id']=='C02' and float(r['volume_l'])==30
                   and float(r['f_hz'])==20 and float(r['target_linear_x_fraction'])==.6)]
    checks=[]
    for row in selected:
        model=NonlinearModel(Plant.from_driver(drivers[row['candidate_id']]),float(row['volume_l']),
                             Shape(k_asym=float(row['k_asym']),k_quad=float(row['k_quad'])),np.inf,True)
        r=simulate_sine(model,float(row['f_hz']),float(row['voltage_rms_v']),method='DOP853',
                         cycles=32,max_cycles=128,rtol=3e-12,atol=3e-14,samples_per_cycle=1024,closure_tolerance=1e-10)
        assert r['status']=='PERIODIC_WITHIN_MODEL_TOLERANCE',r
        error=abs(r['h2_pressure_pct']-float(row['h2_pressure_pct']))
        checks.append(dict(candidate_id=row['candidate_id'],volume_l=float(row['volume_l']),f_hz=float(row['f_hz']),
                           target_linear_x_fraction=float(row['target_linear_x_fraction']),
                           original_h2_pct=float(row['h2_pressure_pct']),refined_h2_pct=r['h2_pressure_pct'],
                           absolute_h2_percentage_point_difference=error,
                           diagnostic_h2_over_solver_difference=r['h2_pressure_pct']/max(error,1e-300),
                           relative_fundamental_difference=abs(r['x_fundamental_peak_m']/float(row['x_fundamental_peak_m'])-1),
                           refined_energy_relative_residual=r['energy_relative_residual']))
    result=dict(status='SPRAWDZENIE_WYBRANYCH_SLADÓW_KOMPENSACJI',checks=checks,
                scope='Różnica solverów nie jest certyfikowaną granicą błędu. Bardzo małego H2 nie interpretować poniżej numerycznej rozdzielczości; nie waliduje krzywych produktu.')
    (ROOT/'wyniki/p13_kompensacja_weryfikacja.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print(json.dumps(result,ensure_ascii=False,indent=2));return result


if __name__=='__main__':main()
