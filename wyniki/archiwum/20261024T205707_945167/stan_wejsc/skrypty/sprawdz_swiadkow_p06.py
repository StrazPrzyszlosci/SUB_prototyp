"""Niezależny układ 3 równań i ponowna ocena świadków P06."""
import json
from pathlib import Path
import numpy as np
from model_subwoofera import Driver, RHO, C, P_REF
from model_niepewnosci import evaluate
from przedzialy_niepewnosci import pressure_bounds

ROOT = Path(__file__).resolve().parents[1]


def main():
    catalog = json.loads((ROOT / 'dane/przetworniki/pula_rozszerzona.json').read_text())['drivers']
    drivers = {r['candidate_id']:Driver(**r['model']) for r in catalog}
    cases = json.loads((ROOT / 'wyniki/p06_swiadkowie_niezaleznych_zaburzen.json').read_text())
    max_error = 0.
    records = []
    for row in cases:
        if 'candidate_id' not in row:
            continue
        u = np.array(row['unit_coordinates'])
        assert np.all((u >= 0) & (u <= 1)) and np.all(u[8:10] == 1.)
        out = evaluate(drivers[row['candidate_id']], [u], family=row['family'])
        p = {k:v[0] for k, v in out['physical'].items()}
        for fi, f in enumerate([20., 40.]):
            s = 2j*np.pi*f
            cab = p['vb_l']*1e-3/(RHO*C*C)
            g = 2*np.pi*p['leak_hz']*cab
            matrix = np.array([[p['re']+s*p['le'], p['bl']*s, 0.],
                               [-p['bl'], p['mms']*s*s+p['rms']*(1+p['extra_r_fraction'])*s+1/p['cms'], -p['sd']],
                               [0., p['sd']*s, cab*s+g]], dtype=complex)
            current, x, pi = np.linalg.solve(matrix, np.array([out['voltage'][0, fi], 0., 0.]))
            total_flow = p['sd']*s*x+g*pi
            pressure = abs(RHO*s*total_flow/(2*np.pi))
            spl = 20*np.log10(pressure/P_REF)
            error = abs(spl-out['spl_db'][0, fi])
            max_error = max(max_error, float(error))
            assert abs(current) <= 12*(1+1e-12)
            assert np.sqrt(2)*abs(x) <= p['xmax_m']*(1+1e-12)
            expected = row['spl20_db'] if fi == 0 else row['spl40_db']
            assert abs(spl-expected) < 2e-11
        records.append(dict(candidate_id=row['candidate_id'], family=row['family'], target=row['target'],
                            independent_spl20_db=float(out['spl_db'][0, 0])))
    separated = []
    for row in cases:
        if row.get('kind') == 'INDEPENDENT_ADMISSIBLE_PAIR':
            a = evaluate(drivers[row['a']], [row['unit_a']], family=row['family'])['spl_db'][0, 0]
            b = evaluate(drivers[row['b']], [row['unit_b']], family=row['family'])['spl_db'][0, 0]
            assert a < b and abs((a-b)-row['margin_a_minus_b_db']) < 1e-10
            ua, ub = np.array(row['unit_a']), np.array(row['unit_b'])
            bounds_a = pressure_bounds(drivers[row['a']], np.column_stack([ua, ua]), 100., 40., 12., row['family'], 20.)
            bounds_b = pressure_bounds(drivers[row['b']], np.column_stack([ub, ub]), 100., 40., 12., row['family'], 20.)
            assert bounds_a[1] < bounds_b[0]
            separated.append(dict(family=row['family'], a=row['a'], b=row['b'],
                                  upper_pressure_a_pa=bounds_a[1], lower_pressure_b_pa=bounds_b[0],
                                  strict_iv_pressure_separation=True))
    result = dict(status='PASS_KONTRPRZYKLADY_W_ZADANYM_MODELU', independent_three_equation_max_error_db=max_error,
                  shared_amp_vrms=40., shared_amp_irms=12., individual_cases=len(records),
                  valid_pair_refutations=sum(r.get('kind')=='INDEPENDENT_ADMISSIBLE_PAIR' for r in cases),
                  pair_point_enclosures=separated,
                  limitation='Świadek falsyfikuje uniwersalną dominację w zadanej rodzinie, nie wybiera lepszego produktu fizycznego.')
    (ROOT / 'wyniki/p06_swiadkowie_weryfikacja.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


if __name__ == '__main__':
    main()
