"""Addytywne porównanie 26 produktów / 27 połączeń, bez modelu cieplnego.

SI wewnętrznie; sinus ustalony, U/I RMS, x peak, idealny monopol 2pi/1 m.
Nie przewiduje THD, pomieszczenia ani dopuszczalnego czasu pracy.
"""
from dataclasses import dataclass, fields, replace
from pathlib import Path
import csv
import hashlib
import json
import os
import platform
os.environ.setdefault('MPLCONFIGDIR', '/tmp/sub-krystian-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import scipy
from model_subwoofera import Driver, response, alignment, sealed_shape, RHO, C, P_REF

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'wyniki'
EXT = ROOT / 'dane/przetworniki/rozszerzenie_SB_20261025.json'
BASE = ROOT / 'dane/przetworniki/pula_rozszerzona.json'
VOLUMES = [20., 30., 45., 60., 80., 100., 120., 150., 200.]
FREQ = np.array([20., 25., 31.5, 40., 63., 80.])


@dataclass(frozen=True)
class SmallSignal:
    """Port T/S bez pola mocy katalogowej; nie dopisujemy nieznanego Pe."""
    name: str
    fs_hz: float
    qes: float
    qms: float
    vas_l: float
    sd_cm2: float
    re_ohm: float
    le_mh: float
    xmax_mm: float
    sd = Driver.sd
    cms = Driver.cms
    mms = Driver.mms
    bl = Driver.bl
    rms = Driver.rms
    qts = Driver.qts


def make(spec):
    return SmallSignal(**{f.name: spec[f.name] for f in fields(SmallSignal)})


def candidates():
    ext = json.loads(EXT.read_text())
    assert hashlib.sha256(BASE.read_bytes()).hexdigest() == ext['base_pool_sha256']
    result = [(r['candidate_id'], r['candidate_id'], make(r['model']), r['catalog_extra'])
              for r in json.loads(BASE.read_text())['drivers']]
    for p in ext['products']:
        if 'model' in p:
            result.append((p['candidate_id'], p['candidate_id'], make(p['model']), p['catalog_extra']))
        else:
            for conf in p['configurations']:
                cat = dict(p['catalog_extra'], bl_tm=conf['catalog_bl_tm'])
                result.append((conf['configuration_id'], p['candidate_id'],
                               make(dict(p['common_model'], **conf)), cat))
    return result


def limited(d, volume, freq, vmax, imax, fraction=1.):
    one = response(d, volume, freq)
    limits = np.array([fraction*d.xmax_mm*1e-3/one['x_peak_m'],
                       np.full_like(np.asarray(freq), vmax), imax/one['i_rms']])
    voltage = np.min(limits, axis=0)
    return voltage, np.argmin(limits, axis=0), response(d, volume, freq, voltage)


def table(name, rows):
    with (OUT/name).open('w', newline='', encoding='utf-8') as h:
        writer = csv.DictWriter(h, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    pool = candidates()
    rows, audit, summary = [], [], []
    matrix_error = energy_error = shape_error = 0.
    for cid, pid, d, cat in pool:
        for vb in VOLUMES:
            fc, qtc, f3 = alignment(d, vb)
            one = response(d, vb, FREQ)
            # Odrębny układ I/v/x, bez eliminacji impedancji ruchowej.
            for k, f in enumerate(FREQ):
                w = 2*np.pi*f
                stiffness = 1/d.cms + RHO*C*C*d.sd*d.sd/(vb*.001)
                matrix = np.array([[d.re_ohm+1j*w*d.le_mh*.001, d.bl, 0],
                                   [-d.bl, d.rms+1j*w*d.mms, stiffness],
                                   [0, 1, -1j*w]], complex)
                i, v, x = np.linalg.solve(matrix, [1, 0, 0])
                values = [abs(abs(i)/one['i_rms'][k]-1),
                          abs(np.sqrt(2)*abs(x)/one['x_peak_m'][k]-1),
                          abs((1/i)/one['z'][k]-1)]
                matrix_error = max(matrix_error, *values)
                pin = i.real
                energy_error = max(energy_error,
                                   abs(pin-(d.re_ohm*abs(i)**2+d.rms*abs(v)**2))/pin)
            # Le=0: niezależny wzorzec odpowiedzi drugiego rzędu.
            no_le = response(replace(d, le_mh=0.), vb, FREQ)
            asymptote = RHO*d.sd*d.bl/(2*np.pi*d.re_ohm*d.mms)
            expected = asymptote*abs(sealed_shape(FREQ, fc, qtc))
            actual = P_REF*10**(no_le['spl_rms_db']/20)
            shape_error = max(shape_error, float(np.max(abs(actual/expected-1))))
            for vmax, imax in [(40., 12.), (60., 20.)]:
                for fraction in [.7, 1.]:
                    voltage, active, out = limited(d, vb, FREQ, vmax, imax, fraction)
                    assert np.all(out['x_peak_m'] <= fraction*d.xmax_mm*.001*(1+1e-12))
                    assert np.all(out['i_rms'] <= imax*(1+1e-12))
                    for k, f in enumerate(FREQ):
                        rows.append(dict(configuration_id=cid, product_id=pid, vb_air_net_l=vb,
                                         f_hz=float(f), amp_v_rms=vmax, amp_i_rms=imax,
                                         fraction_catalog_xmax=fraction, fc_hz=fc, qtc=qtc,
                                         f3_Le0_reference_hz=f3, u_rms_v=float(voltage[k]),
                                         i_rms_a=float(out['i_rms'][k]), x_peak_mm=float(out['x_peak_m'][k]*1000),
                                         spl_rms_2pi_1m_db=float(out['spl_rms_db'][k]),
                                         copper_loss_w=float(out['p_copper_w'][k]),
                                         active_limit=['catalog_x', 'voltage', 'current'][active[k]]))
        for key, value in [('qts', d.qts), ('mms_g', 1000*d.mms),
                           ('cms_mm_n', 1000*d.cms), ('bl_tm', d.bl), ('rms_kg_s', d.rms)]:
            if key in cat:
                audit.append(dict(configuration_id=cid, parameter=key, catalog=cat[key],
                                  derived=value, relative_difference_pct=100*(value/cat[key]-1)))
        picked = [r for r in rows if r['configuration_id']==cid and r['vb_air_net_l']==100
                  and r['amp_v_rms']==40 and r['fraction_catalog_xmax']==1]
        summary.append(dict(configuration_id=cid, product_id=pid, name=d.name,
                            vd_catalog_l=d.sd*d.xmax_mm, qts_derived=d.qts,
                            fc_100l_hz=alignment(d, 100)[0], qtc_100l=alignment(d, 100)[1],
                            f3_Le0_100l_hz=alignment(d, 100)[2],
                            **{f'spl_{r["f_hz"]:g}hz_db':r['spl_rms_2pi_1m_db'] for r in picked},
                            **{f'limit_{r["f_hz"]:g}hz':r['active_limit'] for r in picked}))
    assert len(pool)==27 and len({r[1] for r in pool})==26 and len(rows)==5832
    assert max(matrix_error, energy_error, shape_error)<1e-11
    # Równoważność idealnego przełączenia obu cewek, nie korekta danych producenta.
    lookup = {r[0]:r[2] for r in pool}
    par, ser = lookup['C26P'], lookup['C26S']
    ideal_ser = replace(ser, le_mh=4*par.le_mh)
    fcheck = np.geomspace(.01, 20000., 2000)
    ap, ass = response(par, 100, fcheck), response(ideal_ser, 100, fcheck, 2.)
    transform_error = float(np.max(abs(ass['x_peak_m']/ap['x_peak_m']-1)))
    assert transform_error<1e-11
    # Sprawdzenie historycznych 24 na wspólnych punktach, bez zmiany starych plików.
    old = {r['candidate_id']:r for r in csv.DictReader((OUT/'pula_podsumowanie.csv').open())}
    historical_error = max(abs(r[f'spl_{f}hz_db']-float(old[r['configuration_id']][f'at100l_{f}hz_40v12a_db']))
                           for r in summary if r['configuration_id'] in old for f in [20, 40])
    assert historical_error<1e-10
    table('sb_rozszerzenie_scenariusze.csv', rows)
    table('sb_rozszerzenie_spojnosc_TS.csv', audit)
    table('sb_rozszerzenie_podsumowanie.csv', summary)
    # Tylko sześć czytelnych linii; pełna pula zachowana w tabelach.
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    colors = ['#7a7a7a', '#222222', '#127b8e', '#c06b00', '#b83b75', '#4659aa']
    probes = np.geomspace(10, 120, 450)
    for color, cid in zip(colors, ['C01','C02','C04','C25','C26P','C26S']):
        d = lookup[cid]
        _, _, out = limited(d, 100, probes, 40., 12.)
        axes[0].semilogx(probes, out['spl_rms_db'], label=cid, color=color,
                         linestyle='--' if cid=='C26S' else '-')
    axes[0].set(xlabel='Częstotliwość [Hz]', ylabel='SPL RMS [dB], 2π / 1 m',
                title='100 l netto, 40 V RMS / 12 A RMS; limit X/V/I')
    axes[0].legend(ncol=3)
    axes[0].grid(True, which='both', alpha=.25)
    indexes=['C04','C25','C26P','C26S']
    for cid, color in zip(indexes, colors[2:]+[colors[-1]]):
        selection=[r for r in rows if r['configuration_id']==cid and r['f_hz']==20
                   and r['amp_v_rms']==40 and r['fraction_catalog_xmax']==1]
        axes[1].semilogx([r['vb_air_net_l'] for r in selection],
                         [r['spl_rms_2pi_1m_db'] for r in selection], marker='o', label=cid,
                         color=color, linestyle='--' if cid=='C26S' else '-')
    axes[1].set(xlabel='Vb netto powietrza [l]', ylabel='SPL RMS 20 Hz [dB], 2π / 1 m',
                title='SB: zmiana litrażu przy tych samych limitach')
    axes[1].legend()
    axes[1].grid(True, which='both', alpha=.25)
    fig.suptitle('Model liniowy: osobne sinusy ustalone, bez termiki, THD i pokoju', fontsize=11)
    fig.tight_layout()
    for ext in ['png', 'svg']:
        fig.savefig(OUT/f'61_SB_porownanie_i_objetosc.{ext}', dpi=170)
    plt.close(fig)
    inputs=[BASE, EXT, ROOT/'skrypty/model_subwoofera.py', Path(__file__),
            OUT/'pula_podsumowanie.csv', ROOT/'brief_system_audio_DIY_v0.6.md']
    checks=dict(independent_3equation_points=len(pool)*len(VOLUMES)*len(FREQ),
                max_relative_matrix_error=matrix_error, max_relative_energy_error=energy_error,
                max_Le0_shape_error=shape_error, ideal_dual_coil_transform_error=transform_error,
                historical_24_max_spl_difference_db=historical_error,
                web_vs_pdf_motion_ceiling_difference_db=20*np.log10(11.25/11.))
    result=dict(status='ADDITIVE_LINEAR_SCREENING_NOT_FINAL_SELECTION', date='2026-10-26',
                physical_products=26, electrical_configurations=27, SB_products=3,
                manufacturer_count=11, point_cases=len(rows), volumes_air_net_l=VOLUMES,
                frequencies_hz=FREQ.tolist(), checks=checks,
                libraries=dict(Python=platform.python_version(), NumPy=np.__version__,
                               SciPy=scipy.__version__, Matplotlib=matplotlib.__version__),
                input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
                scope=['Osobne ustalone sinusy; brak ograniczenia czasu/cieplnego i THD.',
                       '2pi/1m nie jest SPL w pokoju lub całym systemie.',
                       '9 punktów Vb nie dowodzi optimum w ciągłym litrażu.',
                       'Stare kampanie nieliniowe/termiczne obejmują 24 bazy; nie rozszerzono ich automatycznie.',
                       'Stałe Le z tabeli nie identyfikuje cewki ani obu połączeń jedną macierzą.',
                       'Qtc/F3 są wzorcem Le=0, nie parametrami całej odpowiedzi z Le.'])
    (OUT/'sb_rozszerzenie_weryfikacja.json').write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    print(json.dumps(dict(cases=len(rows), checks=checks), ensure_ascii=False))


if __name__=='__main__':
    main()
