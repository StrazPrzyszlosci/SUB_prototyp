"""Odtwarzalne obliczenia etapu przed budową. Uruchom z dowolnego katalogu."""
import csv
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

os.environ.setdefault('MPLCONFIGDIR', '/tmp/sub-krystian-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import scipy
import sympy
import mpmath
from model_subwoofera import Driver, alignment, response, linear_envelope, dsp_shape, sealed_shape, room_modes

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'wyniki'


def table(name, rows):
    rows = list(rows)
    with (OUT / name).open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def savefig(name):
    plt.tight_layout()
    plt.savefig(OUT / (name + '.png'), dpi=160)
    plt.savefig(OUT / (name + '.svg'))
    plt.close()


def main():
    OUT.mkdir(exist_ok=True)
    data_path = ROOT / 'dane/przetworniki/kandydaci.json'
    cfg_path = ROOT / 'dane/konfiguracje/badania_wstepne.json'
    data = json.loads(data_path.read_text())
    cfg = json.loads(cfg_path.read_text())
    room_path = ROOT / 'dane/konfiguracje/pokoj_odsluchowy.json'
    if room_path.exists():
        room = json.loads(room_path.read_text())
        expected = [room['length_y_m'], room['width_x_m'], room['height_z_m']]
        if not np.allclose(cfg['room_dimensions_m'], expected, rtol=0, atol=1e-12):
            raise ValueError('Niespójne wymiary pokoju lub zamieniona kolejność osi')
    drivers = [Driver(**row['model']) for row in data['drivers']]
    f = np.geomspace(10, 200, 1400)
    probe = np.array([20., 25., 31.5, 40., 63., 80.])
    summaries, band_rows, consistency, sensitivity = [], [], [], []
    fig, axes = plt.subplots(len(drivers), 2, figsize=(12, 3.7 * len(drivers)), squeeze=False)
    for k, (d, raw) in enumerate(zip(drivers, data['drivers'])):
        published = raw['catalog_extra']
        for key, calc in [('qts', d.qts), ('mms_g', d.mms * 1000), ('bl_tm', d.bl), ('cms_mm_n', d.cms * 1000)]:
            if published.get(key) is not None:
                cat = published[key]
                consistency.append({'driver': d.name, 'parameter': key, 'catalog': cat,
                                    'derived': calc, 'relative_difference_percent': 100 * (calc / cat - 1)})
        for vb in cfg['volumes_l']:
            fc, qtc, f3 = alignment(d, vb)
            h = sealed_shape(f, fc, qtc)
            dsp = dsp_shape(f, fc, qtc, **cfg['dsp_example'])
            base = response(d, vb, probe, cfg['reference_vrms'])
            env = linear_envelope(d, vb, probe, cfg['amp_vrms'], cfg['amp_irms'])
            eq_probe = np.abs(dsp_shape(probe, fc, qtc, **cfg['dsp_example']))
            eq_response = response(d, vb, probe, cfg['reference_vrms'] * eq_probe)
            summary = {'driver': d.name, 'vb_net_l': vb, 'fc_hz': fc, 'qtc': qtc, 'f3_hz': f3,
                       'dsp_max_gain_10_200_db': 20 * np.log10(np.max(abs(dsp))),
                       'xmax_volume_displacement_l': d.sd * d.xmax_mm}
            summaries.append(summary)
            for i, freq in enumerate(probe):
                row = {'driver': d.name, 'vb_net_l': vb, 'f_hz': freq,
                       'spl_2pi_1m_rms_at_ref_v_db': base['spl_rms_db'][i],
                       'x_peak_at_ref_v_mm': base['x_peak_m'][i] * 1000,
                       'eq_spl_2pi_1m_rms_at_ref_input_db': eq_response['spl_rms_db'][i],
                       'eq_x_peak_at_ref_input_mm': eq_response['x_peak_m'][i] * 1000,
                       'eq_output_vrms': cfg['reference_vrms'] * eq_probe[i],
                       'model_linear_envelope_2pi_1m_rms_db': env['spl_rms_db'][i],
                       'limit': ['xmax', 'amp_voltage', 'amp_current', 'catalog_voltage_proxy'][env['limit'][i]],
                       'envelope_voltage_rms': env['v_rms'][i],
                       'envelope_current_rms': env['i_rms'][i],
                       'envelope_electrical_real_w': env['p_real_w'][i],
                       'envelope_copper_loss_w': env['p_copper_w'][i]}
                for dist in cfg['distance_m']:
                    row[f'free_field_2pi_{dist}m_rms_db'] = env['spl_rms_db'][i] - 20 * np.log10(dist)
                # Wyłącznie scenariusze czułości; nie model zidentyfikowanego pokoju.
                for gain in cfg['room_gain_20hz_db']:
                    g = gain * np.clip(np.log2(80 / freq) / 2, 0, 1)
                    row[f'scenario_3m_gain20_{gain}db_rms_db'] = env['spl_rms_db'][i] - 20 * np.log10(3) + g
                band_rows.append(row)
            axes[k, 0].semilogx(f, 20 * np.log10(abs(h)), label=f'{vb} l')
            e = linear_envelope(d, vb, f, cfg['amp_vrms'], cfg['amp_irms'])
            axes[k, 1].semilogx(f, e['spl_rms_db'], label=f'{vb} l')
        for param, fraction in [('fs_hz', .05), ('qes', .1), ('vas_l', .1)]:
            for sign in [-1, 1]:
                changed = replace(d, **{param: getattr(d, param) * (1 + sign * fraction)})
                fc, qtc, f3 = alignment(changed, cfg['comparison_volume_l'])
                sensitivity.append({'driver': d.name, 'changed': param, 'delta_percent': sign * fraction * 100,
                                    'vb_net_l': cfg['comparison_volume_l'], 'fc_hz': fc, 'qtc': qtc, 'f3_hz': f3})
        axes[k, 0].set(title=d.name + ' — model 2. rzędu bez EQ', ylabel='dB względem asymptoty', ylim=(-35, 5))
        axes[k, 1].set(title=d.name + ' — granica liniowego modelu', ylabel='SPL RMS [dB], 2π, 1 m')
        for ax in axes[k]:
            ax.set(xlabel='Częstotliwość [Hz]', xlim=(10, 200))
            ax.grid(True, which='both', alpha=.3)
            ax.legend(fontsize=8, ncol=2)
    savefig('01_objetosc_i_granice_modelu')
    table('porownanie_obudow.csv', summaries)
    table('pasma_i_limity.csv', band_rows)
    table('spojnosc_ts.csv', consistency)
    table('wrazliwosc_ts.csv', sensitivity)
    modes = room_modes(cfg['room_dimensions_m'])
    table('mody_pokoju.csv', modes)
    plt.figure(figsize=(10, 3.7))
    for row in modes:
        if row['typ'] == 'osiowy':
            plt.axvline(row['f_hz'], alpha=.45)
            plt.text(row['f_hz'], .5, f"{row['nx']}{row['ny']}{row['nz']}", rotation=90)
    plt.xlim(15, 200)
    plt.yticks([])
    plt.xlabel('Częstotliwość [Hz]')
    plt.title('Mody osiowe: pokój idealny; amplitudy i zaniki nieznane')
    savefig('02_mody_osiowe')
    fig, ax = plt.subplots(2, 1, figsize=(10, 8))
    for d in drivers:
        fc, qtc, _ = alignment(d, cfg['comparison_volume_l'])
        h = sealed_shape(f, fc, qtc)
        dsp = dsp_shape(f, fc, qtc, **cfg['dsp_example'])
        ax[0].semilogx(f, 20 * np.log10(abs(h)), '--', alpha=.5)
        ax[0].semilogx(f, 20 * np.log10(abs(h * dsp)), label=d.name)
        ax[1].semilogx(f, 20 * np.log10(abs(dsp)), label=d.name)
    ax[0].set(ylabel='Odpowiedź znormalizowana [dB]', title='Przykład EQ, 60 l netto; linia przerywana bez EQ')
    ax[1].set(ylabel='Wzmocnienie filtrów [dB]', xlabel='Częstotliwość [Hz]', title='LT + HP + LP; wzorzec analogowy, bez limitera')
    for a in ax:
        a.grid(True, which='both', alpha=.3)
        a.legend()
    savefig('03_przyklad_dsp')
    geometry = []
    for g in cfg['cabinet_geometry_examples']:
        w, h, dep = g['inside_mm']
        t, front = g['wall_mm'], g['front_mm']
        gross = w * h * dep / 1e6
        geometry.append({'name': g['name'], 'inside_w_mm': w, 'inside_h_mm': h, 'inside_d_mm': dep,
                         'outside_w_mm': w + 2 * t, 'outside_h_mm': h + 2 * t, 'outside_d_mm': dep + t + front,
                         'gross_internal_l': gross, 'assumed_driver_l': g['assumed_driver_l'],
                         'assumed_braces_l': g['assumed_braces_l'],
                         'net_before_modules_l': gross - g['assumed_driver_l'] - g['assumed_braces_l'],
                         'status': 'geometria_pogladowa_nie_projekt_CNC'})
    table('geometria_wstepna.csv', geometry)
    # Manifest obejmuje kod i wyniki, nie tylko nazwy bibliotek.
    files = [ROOT / 'brief_system_audio_DIY_v0.6.md', ROOT / 'DECYZJE_I_PYTANIA.md',
             ROOT / 'requirements.txt',
             *([ROOT/'requirements_zrodla.txt'] if (ROOT/'requirements_zrodla.txt').exists() else []),
             ROOT / 'PLAN_BADAN_NAUKOWYCH.md', ROOT / 'PROGRAM_30_BADAN.md', data_path, cfg_path,
             *sorted((ROOT / 'dane/przetworniki').glob('*.json')),
             *sorted((ROOT / 'dane/konfiguracje').glob('*.json')),
             *sorted(p for p in (ROOT/'dane/materialy').glob('*.json') if p.is_file()),
             *sorted((ROOT / 'skrypty').glob('*.py')),
             *sorted(p for p in (ROOT / 'dane/zrodla').rglob('*') if p.is_file())]
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    output_hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in sorted(OUT.iterdir()) if p.is_file() and p.name != 'manifest.json'}
    documents = [*sorted(ROOT.glob('*.md')),
                 *sorted((ROOT / 'baza_wiedzy').glob('*.md')),
                 *sorted((ROOT / 'raporty').glob('*.md'))]
    documentation_hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in documents}
    manifest = {'generated_at': datetime.now(ZoneInfo('Europe/Warsaw')).isoformat(),
                'status': 'BADANIA_MODELOWE_PRZED_BUDOWA_NIE_WALIDACJA_URZADZENIA', 'python': sys.version,
                'libraries': {'numpy': np.__version__, 'scipy': scipy.__version__, 'matplotlib': matplotlib.__version__,
                              'sympy': sympy.__version__, 'mpmath': mpmath.__version__},
                'input_sha256': hashes, 'output_sha256': output_hashes,
                'documentation_sha256': documentation_hashes,
                'configuration': cfg, 'limitations': [
                    'Nie jest pomiarem ani gwarancją maksymalnego użytecznego SPL.',
                    'Modele T/S nie wyznaczają THD, temperatury, kompresji ani BL(x), Cms(x), Le(x).',
                    'Pierwotne P26/P27 zakładają zadaną U; P11 dodaje reakcję modalnego pola na napęd. Pozycje i straty pozostają niezidentyfikowane.',
                    'P11: geometrie kontrolne i port Gaussa nie rozwiązują rozpraszania na docelowej skrzyni; kalibracja w Fs nie jest pomiarem Mmd.',
                    'Granice dotyczą osobnych sinusów; nie wolno sumować ich jako dostępnego SPL muzyki.',
                    'Pe*Znom to orientacyjny limit napięcia, nie wyznaczona granica termiczna.',
                    'T/S producentów wymagają późniejszej walidacji egzemplarzy.']}
    (OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    print(f'Historyczna baza porównawcza: {len(drivers)} przetworniki, {len(summaries)} obudów, {len(band_rows)} rekordów pasmowych; rozszerzenia w osobnych tabelach')
    for d in drivers:
        print(f'{d.name}: Qts={d.qts:.4f}, BL wyprowadzone={d.bl:.2f} Tm, Mms={d.mms*1000:.1f} g')


if __name__ == '__main__':
    main()
