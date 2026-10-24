"""P06: globalna wrażliwość, obwiednie i falsyfikacja odporności rankingu.

QMC/MC całkują jawną umowną miarę projektu. Nie tworzą rozkładu produktów.
Przedziały ciśnienia obejmują całą zadaną dziedzinę, nie tylko próbki.
"""
import csv
from dataclasses import replace
from itertools import product
import json
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR', '/tmp/sub-krystian-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import brentq
from scipy.stats import qmc, sobol_indices, uniform
from model_subwoofera import Driver, alignment, P_REF
from model_niepewnosci import CFG, FACTORS, evaluate, physical, derived_ts, correlated_design
from przedzialy_niepewnosci import refine_enclosure

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'wyniki'


def table(name, rows):
    with (OUT / name).open('w', newline='', encoding='utf-8') as handle:
        w = csv.DictWriter(handle, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)


def nominal_unit_point():
    target = dict.fromkeys(FACTORS, 1.)
    target.update(leak_ref_hz=0., extra_r_over_rms=0.)
    return np.array([(target[key]-CFG['ranges'][key][0]) /
                     (CFG['ranges'][key][1]-CFG['ranges'][key][0]) for key in FACTORS])


def main():
    raw = json.loads((ROOT / 'dane/przetworniki/pula_rozszerzona.json').read_text())['drivers']
    drivers = [Driver(**r['model']) for r in raw]
    positions = {r['candidate_id']:i for i, r in enumerate(raw)}
    hf, he, um, scan = [positions[key] for key in ['C02', 'C11', 'C21', 'C10']]
    probes = CFG['frequencies_hz']
    assert probes == [20., 40.] and CFG['ranges']['x_fraction'] == [0.5, 1.]
    nominal = nominal_unit_point()
    # Ścisły kontrprzykład dla odporności nominalnego porównania na wspólne kryterium X.
    def margin(x_fraction):
        u = nominal.copy(); u[-1] = (x_fraction-0.5)/0.5
        return float(evaluate(drivers[hf], [u])['spl_db'][0, 0] -
                     evaluate(drivers[he], [u])['spl_db'][0, 0])
    crossover = brentq(margin, 0.5, 1., xtol=1e-13)
    witnesses = []
    for fraction in [0.7, crossover, 1.]:
        u = nominal.copy(); u[-1] = (fraction-0.5)/0.5
        row = dict(kind='WSPOLNY_PROG_RUCHU_NIE_THD', x_fraction=float(fraction), unit_coordinates=u.tolist(), models=[])
        for index in [hf, he]:
            out = evaluate(drivers[index], [u])
            row['models'].append(dict(candidate_id=raw[index]['candidate_id'], driver=drivers[index].name,
                                      equivalent_spl_2pi_1m_rms_20hz_db=float(out['spl_db'][0, 0]),
                                      voltage_rms=float(out['voltage'][0, 0]),
                                      current_rms=float(out['current'][0, 0]),
                                      x_peak_mm=float(out['x_peak_m'][0, 0]*1000)))
        witnesses.append(row)
    # Lokalne pochodne w środku umownej dziedziny L, z kontrolą kroku.
    local = []
    for index, d in enumerate(drivers):
        for j, key in enumerate(FACTORS):
            derivatives = []
            for step in [1e-4, 1e-5]:
                lo = np.full((1, len(FACTORS)), 0.5); hi = lo.copy()
                lo[0, j] -= step; hi[0, j] += step
                derivatives.append((evaluate(d, hi)['spl_db'][0]-evaluate(d, lo)['spl_db'][0])/(2*step))
            for fi, f in enumerate(probes):
                local.append(dict(candidate_id=raw[index]['candidate_id'], f_hz=f, factor=key,
                                  d_spl_db_per_unit_coordinate=float(derivatives[-1][fi]),
                                  difference_between_steps=float(abs(derivatives[-1][fi]-derivatives[0][fi])),
                                  status='LOKALNY_SRODEK_RODZINY_L_NIE_NOMINALNY_PRODUKT'))
    table('p06_czulosc_lokalna.csv', local)
    # Funkcja wielowyjściowa: kolejno dwa pasma każdego modelu.
    sobol_rows = []
    sobol_runs = {}
    for family in ['D', 'L']:
        def model_for_sobol(x):
            return np.concatenate([evaluate(d, x.T, family=family)['spl_db'].T for d in drivers])
        for power in CFG['sobol_powers']:
            for seed in CFG['sobol_seeds']:
                print('P06 Sobol:', family, 'N=', 2**power, 'seed=', seed, flush=True)
                result = sobol_indices(func=model_for_sobol, n=2**power,
                                       dists=[uniform() for _ in FACTORS], rng=np.random.default_rng(seed))
                first = np.asarray(result.first_order).reshape(len(drivers), len(probes), len(FACTORS))
                total = np.asarray(result.total_order).reshape(first.shape)
                sobol_runs[(family, power, seed)] = (first, total)
                for di, r in enumerate(raw):
                    for fi, f in enumerate(probes):
                        for j, key in enumerate(FACTORS):
                            sobol_rows.append(dict(candidate_id=r['candidate_id'], family=family, f_hz=f,
                                                   n_base=2**power, seed=seed, factor=key,
                                                   first_order=float(first[di, fi, j]), total_order=float(total[di, fi, j]),
                                                   measure='UNIFORM_DESIGN_NOT_PRODUCT_PROBABILITY'))
    table('p06_indeksy_sobola.csv', sobol_rows)
    convergence = []
    low_power, high_power = min(CFG['sobol_powers']), max(CFG['sobol_powers'])
    for family in ['D', 'L']:
        for seed in CFG['sobol_seeds']:
            small = sobol_runs[(family, low_power, seed)]
            large = sobol_runs[(family, high_power, seed)]
            convergence.append(dict(family=family, comparison=f'N{2**low_power}_N{2**high_power}_seed{seed}',
                                    max_first_order_difference=float(np.max(abs(small[0]-large[0]))),
                                    max_total_order_difference=float(np.max(abs(small[1]-large[1])))))
        a, b = [sobol_runs[(family, high_power, seed)] for seed in CFG['sobol_seeds']]
        convergence.append(dict(family=family, comparison=f'scrambles_N{2**high_power}',
                                max_first_order_difference=float(np.max(abs(a[0]-b[0]))),
                                max_total_order_difference=float(np.max(abs(a[1]-b[1])))))
    table('p06_sobol_zbieznosc.csv', convergence)
    # Nie ukrywamy nieosiągnięcia progu przeglądu numerycznego.
    convergence_ok = max(max(r['max_first_order_difference'], r['max_total_order_difference'])
                         for r in convergence) <= CFG['sobol_max_difference_review_threshold']
    # Wspólne scenariusze względnych zaburzeń dla wszystkich porównywanych modeli.
    base_u = qmc.Sobol(len(FACTORS), scramble=True, rng=np.random.default_rng(20260624)).random_base2(CFG['ranking_sample_power'])
    rank_rows, mc_rows, corr_rows = [], [], []
    qmc_outputs = {}
    for rho in CFG['correlation_profiles_mms_cms_gaussian']:
        u = correlated_design(base_u, rho)
        p = physical(drivers[hf], u, 100., 40., 12.)
        ts = derived_ts(p)
        keys = ['mms', 'cms', 'fs', 'qes', 'qms', 'vas_l']
        matrix = np.stack([p[k] if k in p else ts[k] for k in keys])
        corr = np.corrcoef(matrix)
        for i, ka in enumerate(keys):
            for j, kb in enumerate(keys):
                corr_rows.append(dict(profile_gaussian_rho=rho, parameter_a=ka, parameter_b=kb,
                                      design_pearson_correlation=float(corr[i, j]),
                                      status='KORELACJA_UMOWNEJ_MIARY_NIE_DANE_EGZEMPLARZY'))
        for family in ['D', 'L']:
            for vb in CFG['volumes_nominal_l']:
                for vmax, imax in CFG['amplifier_scenarios']:
                    outputs = np.stack([evaluate(d, u, vb, vmax, imax, family)['spl_db'] for d in drivers])
                    best = outputs.argmax(axis=0)
                    for di, r in enumerate(raw):
                        for fi, f in enumerate(probes):
                            vals = outputs[di, :, fi]
                            rank_rows.append(dict(candidate_id=r['candidate_id'], family=family, vb_l=vb,
                                                  vmax=vmax, imax=imax, gaussian_rho=rho, f_hz=f,
                                                  design_min_db=float(min(vals)), design_max_db=float(max(vals)),
                                                  design_mean_db=float(np.mean(vals)),
                                                  design_best_count=int(np.sum(best[:, fi] == di)),
                                                  n_design=len(u), status='WSPOLNE_SCENARIUSZE_NIE_PRAWDOPODOBIENSTWO_WYBORU'))
                    if rho == 0 and vb == 100 and vmax == 40:
                        qmc_outputs[family] = outputs
                        margin_values = outputs[hf, :, 0]-outputs[he, :, 0]
                        for which, j in [('C02_MINUS_C11_MIN', int(np.argmin(margin_values))),
                                         ('C02_MINUS_C11_MAX', int(np.argmax(margin_values)))]:
                            witnesses.append(dict(kind=which, family=family, vb_l=vb, vmax=vmax, imax=imax,
                                                  unit_coordinates=u[j].tolist(),
                                                  margin_db=float(margin_values[j]),
                                                  c02_db=float(outputs[hf, j, 0]), c11_db=float(outputs[he, j, 0])))
    table('p06_ranking_scenariuszy.csv', rank_rows)
    table('p06_korelacje_miary.csv', corr_rows)
    # Zwykłe MC jako niezależny sposób całkowania tej samej umownej miary.
    mc_u = np.random.default_rng(CFG['ranking_mc_seed']).random(base_u.shape)
    for family in ['D', 'L']:
        for di, d in enumerate(drivers):
            vals = evaluate(d, mc_u, family=family)['spl_db']
            for fi, f in enumerate(probes):
                mc_rows.append(dict(candidate_id=raw[di]['candidate_id'], family=family, f_hz=f,
                                    n_points=len(mc_u), mc_design_mean_db=float(np.mean(vals[:, fi])),
                                    qmc_design_mean_db=float(np.mean(qmc_outputs[family][di, :, fi])),
                                    difference_of_means_db=float(np.mean(vals[:, fi])-np.mean(qmc_outputs[family][di, :, fi])),
                                    status='BLAD_CALKOWANIA_MIARY_NIE_NIEPEWNOSC_POPULACJI'))
    table('p06_mc_i_qmc.csv', mc_rows)
    # Globalne obwiednie: wszystkie dodatnie parametry w zadanych przedziałach.
    intervals = []
    for di, d in enumerate(drivers):
        print('P06 obwiednie:', raw[di]['candidate_id'], d.name, flush=True)
        for family in ['D', 'L']:
            for vb in CFG['volumes_nominal_l']:
                for vmax, imax in CFG['amplifier_scenarios']:
                    for f in probes:
                        bound = refine_enclosure(d, vb, vmax, imax, family, f, leaves=CFG['interval_leaf_budget'])
                        intervals.append(dict(candidate_id=raw[di]['candidate_id'], family=family,
                                              vb_l=vb, vmax=vmax, imax=imax, f_hz=f, **bound))
    table('p06_obwiednie_przedzialowe.csv', intervals)
    robust = []
    for family, vb, amp in product(['D', 'L'], CFG['volumes_nominal_l'], CFG['amplifier_scenarios']):
        subset = [r for r in intervals if r['family']==family and r['vb_l']==vb and r['vmax']==amp[0]]
        lookup = {(r['candidate_id'], r['f_hz']): r for r in subset}
        for ra, rb in product(raw, repeat=2):
            if ra['candidate_id'] == rb['candidate_id']:
                continue
            margins = [lookup[(ra['candidate_id'], f)]['lower_db'] - lookup[(rb['candidate_id'], f)]['upper_db'] for f in probes]
            dominates = all(lookup[(ra['candidate_id'], f)]['lower_pa'] > lookup[(rb['candidate_id'], f)]['upper_pa'] for f in probes)
            robust.append(dict(family=family, vb_l=vb, vmax=amp[0], imax=amp[1],
                               candidate_a=ra['candidate_id'], candidate_b=rb['candidate_id'],
                               a_dominates_b_both_frequencies=dominates,
                               lower_a_minus_upper_b_20hz_db=margins[0], lower_a_minus_upper_b_40hz_db=margins[1],
                               scope='TYLKO_DWA_KRYTERIA_P06_NIE_PELNY_BRIEF'))
    table('p06_dominacja_odporna.csv', robust)
    (OUT / 'p06_kontrprzyklady.json').write_text(json.dumps(witnesses, ensure_ascii=False, indent=2))
    # Zestawy TSL zachowane wspólnie kontra sztuczne mieszanie ich składowych.
    published = json.loads((ROOT / 'dane/zrodla/pomiary_opublikowane/scan32_voicecoil_2013.json').read_text())
    sets = [r for r in published['parameter_sets'] if r['label'] in ['TSL_S1', 'TSL_S2']]
    fields = ['fs_hz', 'qes', 'qms', 'vas_l', 'sd_cm2', 're_ohm']
    mixed_models = [replace(drivers[scan], **dict(zip(fields, vals)), le_mh=0.) for vals in product(
        *[sorted({r[k] for r in sets}) for k in fields])]
    joint_models = [replace(drivers[scan], **{k:r[k] for k in fields}, le_mh=0.) for r in sets]
    joint_rows = []
    for vb in [50., 60., 100., 150.]:
        joint_f3 = [alignment(d, vb)[2] for d in joint_models]
        mixed_f3 = [alignment(d, vb)[2] for d in mixed_models]
        joint_rows.append(dict(vb_l=vb, joint_tsl_f3_min_hz=min(joint_f3), joint_tsl_f3_max_hz=max(joint_f3),
                               artificial_coordinate_box_f3_min_hz=min(mixed_f3), artificial_coordinate_box_f3_max_hz=max(mixed_f3),
                               unique_artificial_corner_models=len(mixed_models),
                               scope='DWA_WSPOLNE_ZESTAWY_NIE_ROZKLAD_POPULACJI; Le=0 WSPOLNY_MODEL_PROJEKCJI'))
    table('p06_scan32_zestawy_i_mieszanie.csv', joint_rows)
    # Wykres obwiedni jest przykładem100l/40V; nie finalną kolejnością jakości.
    fig, ax = plt.subplots(1, 2, figsize=(15, 8))
    y = np.arange(len(raw))
    for family, color, offset in [('D', '#2266aa', -0.13), ('L', '#cc7722', 0.13)]:
        sub = [r for r in intervals if r['family']==family and r['vb_l']==100 and r['vmax']==40 and r['f_hz']==20]
        low = np.array([r['lower_db'] for r in sub]); high = np.array([r['upper_db'] for r in sub])
        ax[0].errorbar((low+high)/2, y+offset, xerr=(high-low)/2, fmt='.', color=color, label=f'Rodzina {family}')
    ax[0].set_yticks(y, [r['candidate_id']+' '+d.name for r, d in zip(raw, drivers)], fontsize=7)
    ax[0].set(xlabel='Równoważny limit modelu 20 Hz [dB], 2π / 1 m RMS',
              title='Obwiednie zadanych dziedzin, 100 l / 40 Vrms / 12 Arms')
    ax[0].legend(); ax[0].grid(alpha=0.25)
    xs = np.linspace(.5, 1, 201)
    ys = []
    for index in [hf, he, um]:
        u = np.repeat(nominal[None, :], len(xs), axis=0); u[:, -1]=(xs-.5)/.5
        vals = evaluate(drivers[index], u)['spl_db'][:, 0]
        ax[1].plot(xs, vals, label=raw[index]['candidate_id']+' '+drivers[index].name)
    ax[1].axvline(crossover, linestyle='--', color='grey', label=f'C02/C11: {crossover:.3f} X')
    ax[1].set(xlabel='Wspólny ułamek katalogowej amplitudy X (nie kryterium THD)',
              ylabel='Limit równoważny 20 Hz [dB], 2π / 1 m RMS',
              title='Zmiana kolejności bez zmiany pozostałych parametrów')
    ax[1].legend(fontsize=8); ax[1].grid(alpha=.25)
    fig.tight_layout()
    for ext in ['png', 'svg']:
        fig.savefig(OUT / f'11_niepewnosc_i_kolejnosc.{ext}', dpi=170)
    plt.close(fig)
    result = dict(status='P06_RODZINY_WARUNKOWE_NIE_FINALNY_WYBOR',
                  drivers=len(drivers), factors=len(FACTORS), interval_rows=len(intervals),
                  sobol_rows=len(sobol_rows), rank_rows=len(rank_rows), local_rows=len(local),
                  mc_rows=len(mc_rows), dominance_rows=len(robust),
                  sobol_vector_input_evaluations=sum(2**power for power in CFG['sobol_powers'])*len(CFG['sobol_seeds'])*2*(len(FACTORS)+2),
                  proven_two_criterion_dominance_pairs=sum(r['a_dominates_b_both_frequencies'] for r in robust),
                  x_fraction_c02_c11_crossover_at100l_40v=crossover,
                  sobol_convergence_review_pass=convergence_ok,
                  sobol_convergence=convergence,
                  max_mc_qmc_design_mean_difference_db=max(abs(r['difference_of_means_db']) for r in mc_rows),
                  limitations=['Zakresy i miara wejściowa są umowne, nie populacyjne.',
                               'L: wspólnofazowy przepływ sumaryczny, geometria przecieku pozostaje nieznana.',
                               'Brak rzeczywistego THD, termiki i sprzężenia z pokojem.',
                               'Brak globalnego zwycięzcy całego briefu; obwiednie dotyczą zadanego modelu.',
                               'Brak separacji przedziałów nie dowodzi braku dominacji; obwiednia może być szeroka.'])
    (OUT / 'p06_podsumowanie.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


if __name__ == '__main__':
    main()
