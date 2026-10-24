"""Kontrole rodziny P06: odrębny model N7, energia, Sobol i obwiednie IV."""
import json
from pathlib import Path
import numpy as np
from scipy.stats import sobol_indices, uniform
from model_subwoofera import Driver, RHO, C, P_REF
from model_nieszczelnosci import leakage_response
from model_niepewnosci import CFG, FACTORS, evaluate, physical, derived_ts, correlated_design
from przedzialy_niepewnosci import pressure_bounds, refine_enclosure

ROOT = Path(__file__).resolve().parents[1]


def main():
    data = json.loads((ROOT / 'dane/przetworniki/pula_rozszerzona.json').read_text())['drivers']
    rng = np.random.default_rng(602624)
    max_diff, max_energy, comparisons, enclosure_points = 0., 0., 0, 0
    frequencies = [20., 40.]
    for raw in data:
        d = Driver(**raw['model'])
        u = rng.random((512, len(FACTORS)))
        for family in ['D', 'L']:
            out = evaluate(d, u, family=family)
            p = out['physical']
            assert np.all(out['voltage'] <= p['vmax'][:, None]*(1+2e-14))
            assert np.all(out['current'] <= p['imax'][:, None]*(1+2e-14))
            assert np.all(out['x_peak_m'] <= p['xmax_m'][:, None]*(1+2e-14))
            for j in range(3):
                pars = {k: v[j:j+1] for k, v in p.items()}
                ts = derived_ts(pars)
                qms_total = float(2*np.pi*ts['fs'][0]*p['mms'][j] /
                                  (p['rms'][j]*(1+p['extra_r_fraction'][j])))
                other = Driver(name='independent_N7', fs_hz=float(ts['fs'][0]),
                               qes=float(ts['qes'][0]), qms=qms_total, vas_l=float(ts['vas_l'][0]),
                               sd_cm2=p['sd'][j]*1e4, re_ohm=p['re'][j], le_mh=p['le'][j]*1e3,
                               xmax_mm=p['xmax_m'][j]*1000, nominal_ohm=d.nominal_ohm, rated_w=d.rated_w)
                independent = leakage_response(other, p['vb_l'][j], frequencies,
                                               p['leak_hz'][j], out['voltage'][j])
                for a, b in [(out['x_peak_m'][j], independent['x_peak_m']),
                             (out['current'][j], independent['i_rms_a']),
                             (out['velocity_complex_m_s'][j], independent['v_complex_m_s'])]:
                    max_diff = max(max_diff, float(np.max(abs(a-b)/np.maximum(abs(b), 1e-30))))
                # Wspólne drogi: czysta zmiana normalizacji 4pi -> 2pi, nie model rzeczywistej odgrody.
                max_diff = max(max_diff, float(np.max(abs(out['spl_db'][j] -
                                             independent['spl_4pi_db'] - 20*np.log10(2)))))
                residual = abs(independent['energy_residual_w']) / np.maximum(independent['p_input_w'], 1e-30)
                max_energy = max(max_energy, float(np.max(residual)))
                comparisons += 1
            box = np.tile([0., 1.], (len(FACTORS), 1))
            for fi, freq in enumerate(frequencies):
                low, high = pressure_bounds(d, box, 100., 40., 12., family, freq)
                values = P_REF*10**(out['spl_db'][:, fi]/20)
                assert min(values) >= low*(1-1e-12)
                assert max(values) <= high*(1+1e-12)
                enclosure_points += len(values)
    assert max_diff < 2e-12 and max_energy < 3e-14
    # Odrębny wzorzec indeksów: model addytywny ma Si=STi=ai²/sum(aj²).
    coefficients = np.array([1., 2., 4.])
    indices = sobol_indices(func=lambda x: coefficients @ x, n=8192,
                           dists=[uniform()]*3, rng=np.random.default_rng(417))
    exact = coefficients**2/np.sum(coefficients**2)
    sobol_error = float(max(np.max(abs(indices.first_order-exact)), np.max(abs(indices.total_order-exact))))
    assert sobol_error < 0.006
    d = Driver(**data[1]['model'])
    refined = refine_enclosure(d, 100., 40., 12., 'L', 20., leaves=24, include_cells=True)
    assert refined['partition_volume'] == 1.
    cells = [np.array(x) for x in refined['cells']]
    for i, a in enumerate(cells):
        for b in cells[i+1:]:
            assert np.any(np.minimum(a[:, 1], b[:, 1]) <= np.maximum(a[:, 0], b[:, 0]))
    assert refined['lower_pa'] >= refined['root_lower_pa']*(1-1e-14)
    assert refined['upper_pa'] <= refined['root_upper_pa']*(1+1e-14)
    # Specjalny koniec Le=0 oraz brak wycieku/ruch niepewny wyłączony.
    from dataclasses import replace
    no_le = replace(d, le_mh=0.)
    out = evaluate(no_le, rng.random((64, len(FACTORS))), family='D')
    assert np.all(np.isfinite(out['spl_db']))
    # Monotoniczność wspólnego progu X: powiększenie dopuszczalnego ruchu nie szkodzi.
    u = rng.random((128, len(FACTORS))); lo=u.copy(); hi=u.copy()
    lo[:, -1] = 0.; hi[:, -1] = 1.
    assert np.all(evaluate(d, hi)['spl_db'] >= evaluate(d, lo)['spl_db']-1e-12)
    result = dict(status='PASS_MODELE_I_OBWIEDNIE_NIE_WALIDACJA_PRODUKCJI',
                  independent_N7_comparisons=comparisons,
                  max_independent_relative_or_db_difference=max_diff,
                  max_relative_energy_residual=max_energy,
                  tested_points_inside_root_enclosures=enclosure_points,
                  additive_sobol_max_error=sobol_error,
                  partition_leaf_count=refined['leaves'], partition_volume=refined['partition_volume'],
                  scope='Przedziały wynikają z działań IV, próbki są kontrolą implementacji. Dokładność fizyczna parametrów nie jest certyfikowana.')
    (ROOT / 'wyniki/p06_weryfikacja.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


if __name__ == '__main__':
    main()
