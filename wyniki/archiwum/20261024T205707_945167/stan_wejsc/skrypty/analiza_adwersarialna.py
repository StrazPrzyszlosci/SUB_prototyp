"""P06: jawne świadki odwrócenia kolejności dla niezależnych zaburzeń modeli.

Optymalizacja heurystyczna daje dopuszczalny świadek, nie dowód globalnego
ekstremum. Dla falsyfikacji uniwersalnej dominacji wystarczy jeden świadek.
"""
import json
from pathlib import Path
import numpy as np
from scipy.optimize import differential_evolution
from model_subwoofera import Driver
from model_niepewnosci import FACTORS, evaluate

ROOT = Path(__file__).resolve().parents[1]


def main():
    raw = json.loads((ROOT / 'dane/przetworniki/pula_rozszerzona.json').read_text())['drivers']
    ds = {r['candidate_id']:Driver(**r['model']) for r in raw}
    records = []
    for family in ['D', 'L']:
        active = np.arange(8) if family == 'D' else np.array([*range(8), 10, 11, 12])
        def expand(x):
            a = np.asarray(x)
            compact = a[None, :] if a.ndim == 1 else a.T
            points = np.full((len(compact), len(FACTORS)), 0.5)
            points[:, active] = compact
            points[:, 8:10] = 1.  # Wspólny napęd40V/12A dla obu modeli.
            return points
        extremes = {}
        for key in ['C02', 'C11']:
            for sign in [1., -1.]:
                def objective(x):
                    a = np.asarray(x)
                    points = expand(a)
                    values = sign*evaluate(ds[key], points, family=family)['spl_db'][:, 0]
                    return float(values[0]) if a.ndim == 1 else values
                result = differential_evolution(objective, [(0., 1.)]*len(active), maxiter=140,
                                                popsize=10, vectorized=True, updating='deferred',
                                                rng=np.random.default_rng(602617), tol=1e-9, polish=True)
                point = expand(result.x)
                value = evaluate(ds[key], point, family=family)
                record = dict(family=family, candidate_id=key, target='min' if sign == 1 else 'max',
                              unit_coordinates=point[0].tolist(),
                              shared_amp_vrms=40., shared_amp_irms=12.,
                              spl20_db=float(value['spl_db'][0, 0]), spl40_db=float(value['spl_db'][0, 1]),
                              voltage20_rms=float(value['voltage'][0, 0]),
                              current20_rms=float(value['current'][0, 0]),
                              x20_peak_mm=float(value['x_peak_m'][0, 0]*1000),
                              optimizer_success=bool(result.success), iterations=int(result.nit),
                              scope='DOPUSZCZALNY_SWIADEK_NIE_CERTYFIKAT_GLOBALNEGO_EKSTREMUM')
                records.append(record)
                extremes[(key, record['target'])] = record
        for ca, cb in [('C02', 'C11'), ('C11', 'C02')]:
            a, b = extremes[(ca, 'min')], extremes[(cb, 'max')]
            records.append(dict(family=family, kind='INDEPENDENT_ADMISSIBLE_PAIR',
                                a=ca, b=cb, unit_a=a['unit_coordinates'], unit_b=b['unit_coordinates'],
                                spl20_a_db=a['spl20_db'], spl20_b_db=b['spl20_db'],
                                margin_a_minus_b_db=a['spl20_db']-b['spl20_db'],
                                a_ge_b_refuted_at20hz=bool(a['spl20_db'] < b['spl20_db'])))
    (ROOT / 'wyniki/p06_swiadkowie_niezaleznych_zaburzen.json').write_text(json.dumps(records, ensure_ascii=False, indent=2))
    print('P06: zapisano dopuszczalne świadki dla niezależnych zaburzeń C02/C11')
    return records


if __name__ == '__main__':
    main()
