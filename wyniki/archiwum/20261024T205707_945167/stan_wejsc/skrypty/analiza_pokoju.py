"""P26/P27: pole zespolone i porównywalne scenariusze przy przedniej ścianie."""
import csv
import json
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR', '/tmp/sub-krystian-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from model_pokoju import ModalRoom

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'wyniki'


def table(name, rows):
    with (OUT / name).open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def db(x):
    # Wyłącznie zabezpieczenie logarytmu; nie przyjęty poziom szumu.
    return 20 * np.log10(np.maximum(np.abs(x), np.finfo(float).tiny))


def main():
    cfg = json.loads((ROOT / 'dane/konfiguracje/p26_scenariusze.json').read_text())
    geo = json.loads((ROOT / 'dane/konfiguracje/pokoj_odsluchowy.json').read_text())
    room = ModalRoom((geo['width_x_m'], geo['length_y_m'], geo['height_z_m']))
    lo, hi, df = cfg['frequency_grid_hz']
    f = np.arange(lo, hi + df / 2, df)
    s = 2j * np.pi * f
    fprobe = [20., 25., 31.5, 40., 63., 80.]
    probe_indices = [int(np.argmin(abs(f - a))) for a in fprobe]
    assert np.allclose(f[probe_indices], fprobe)
    listener = np.array(cfg['assumed_listener_xyz_m'])
    receivers = listener + np.array(cfg['diagnostic_neighbor_offsets_xyz_m'])
    sources = np.concatenate([np.array(a['positions_xyz_m']) for a in cfg['source_sets']])
    sigma_s = cfg['source_smoothing_sigma_m']
    sigma_r = cfg['receiver_smoothing_sigma_m']
    common = dict(source_sigma_m=sigma_s, receiver_sigma_m=sigma_r,
                  kmax_m_inv=cfg['kmax_m_inv'])
    pref = room.rho_kg_m3 * room.c_m_s ** 2 / room.volume_m3
    tau_base = 0.2
    curves, bands, stats, delays = [], [], [], []
    full = {}
    for t60 in cfg['modal_t60_s']:
        print('P26: pole przy modalnym T60 scenariusza', t60, flush=True)
        base = room.transfer(f, sources, receivers, t60, tau_base, **common)
        for tau in cfg['zero_relaxation_s']:
            # Zmieniamy dokładnie jeden mod; nie trzeba liczyć ponownie reszty.
            correction = pref * (1 / (s + 1 / tau) - 1 / (s + 1 / tau_base))
            h = base + correction[:, None, None]
            for index, source_set in enumerate(cfg['source_sets']):
                pair = h[:, :, 2 * index:2 * index + 2]
                left, right = pair[:, :, 0], pair[:, :, 1]
                summed = left + right
                full[(t60, tau, source_set['id'])] = pair
                rleft = np.linalg.norm(sources[2 * index] - listener)
                reference = room.rho_kg_m3 * s * np.exp(-s * rleft / room.c_m_s) / (2 * np.pi * rleft)
                for j, freq in enumerate(f):
                    curves.append(dict(set_id=source_set['id'], modal_t60_s=t60,
                                       zero_tau_s=tau, f_hz=float(freq),
                                       left_re_pa_s_m3=float(left[j, 0].real),
                                       left_im_pa_s_m3=float(left[j, 0].imag),
                                       right_re_pa_s_m3=float(right[j, 0].real),
                                       right_im_pa_s_m3=float(right[j, 0].imag),
                                       pair_per_source_u_to_left_db=float(db(summed[j, 0] / left[j, 0])),
                                       pair_fixed_total_u_to_left_db=float(db(summed[j, 0] / (2 * left[j, 0]))),
                                       left_to_2pi_same_u_distance_db=float(db(left[j, 0] / reference[j]))))
                for r in range(len(receivers)):
                    for j in probe_indices:
                        bands.append(dict(set_id=source_set['id'], modal_t60_s=t60,
                                          zero_tau_s=tau, receiver_id=r, f_hz=float(f[j]),
                                          pair_re_pa_s_m3=float(summed[j, r].real),
                                          pair_im_pa_s_m3=float(summed[j, r].imag),
                                          pair_vs_S0_db=float(db(summed[j, r] / summed[j, 0]))))
                band = (f >= 20) & (f <= 100)
                neighbor_change = db(summed[:, 1:] / summed[:, :1])
                stats.append(dict(set_id=source_set['id'], modal_t60_s=t60, zero_tau_s=tau,
                                  room_transfer_span_20_100_db=float(np.ptp(db(summed[band, 0]))),
                                  pair_to_left_min_20_100_db=float(np.min(db(summed[band, 0] / left[band, 0]))),
                                  pair_to_left_max_20_100_db=float(np.max(db(summed[band, 0] / left[band, 0]))),
                                  neighbor_max_abs_change_20_100_db=float(np.max(abs(neighbor_change[band])))))
                if tau == tau_base:
                    for delay in cfg['relative_delays_ms']:
                        for polarity in [1, -1]:
                            total = left[:, 0] + polarity * np.exp(-s * delay / 1000) * right[:, 0]
                            ratio = db(total / left[:, 0])
                            # Antyfaza symetrycznych źródeł w S0 jest analitycznie zerowa.
                            # Błąd zmiennoprzecinkowy nie wyznacza głębokości fizycznego dołka.
                            exact_zero = source_set['id'] in ['A', 'B', 'C'] and delay == 0 and polarity == -1
                            delays.append(dict(set_id=source_set['id'], modal_t60_s=t60,
                                               zero_tau_s=tau_base, delay_ms=delay, polarity=polarity,
                                               exact_symmetry_zero=exact_zero,
                                               min_ratio_20_100_db=None if exact_zero else float(min(ratio[band])),
                                               max_ratio_20_100_db=None if exact_zero else float(max(ratio[band]))))
    table('p26_transmitancje_S0.csv', curves)
    table('p26_punkty_diagnostyczne.csv', bands)
    table('p26_statystyki.csv', stats)
    table('p27_faza_i_opoznienie.csv', delays)
    # Zbieżność w całym paśmie dla czterech ustawień; zmiana modelu szerokości osobno.
    convergence = []
    fine = f.copy()
    for cutoff in [25., 40., 55.]:
        h = room.transfer(fine, sources, [listener], 0.4, 0.2,
                          source_sigma_m=sigma_s, receiver_sigma_m=sigma_r,
                          kmax_m_inv=cutoff)
        convergence.append((cutoff, h))
    reference = convergence[-1][1]
    reference_pairs = reference[..., 0::2] + reference[..., 1::2]
    convergence_rows = []
    for cutoff, h in convergence:
        pairs = h[..., 0::2] + h[..., 1::2]
        convergence_rows.append(dict(kmax_m_inv=cutoff,
                                     number_of_modes=len(room.modes(cutoff)[0]),
                                     max_complex_error_over_global_reference_max=float(np.max(abs(h-reference))/np.max(abs(reference))),
                                     max_level_difference_db=float(np.max(abs(db(h)-db(reference)))),
                                     max_pair_level_difference_db=float(np.max(abs(db(pairs)-db(reference_pairs))))))
    table('p26_zbieznosc.csv', convergence_rows)
    smoothing_rows = []
    smooth_reference = room.transfer(fprobe, sources, [listener], 0.4, 0.2,
                                     source_sigma_m=sigma_s, receiver_sigma_m=sigma_r,
                                     kmax_m_inv=55)
    for a in [0.1, 0.12, 0.18]:
        smoothed = room.transfer(fprobe, sources, [listener], 0.4, 0.2,
                                 source_sigma_m=a, receiver_sigma_m=sigma_r,
                                 kmax_m_inv=55)
        for j, freq in enumerate(fprobe):
            for index, source_set in enumerate(cfg['source_sets']):
                value = smoothed[j, 0, 2*index:2*index+2].sum()
                ref = smooth_reference[j, 0, 2*index:2*index+2].sum()
                smoothing_rows.append(dict(set_id=source_set['id'], f_hz=freq,
                                           source_sigma_m=a, change_to_sigma0_12_db=float(db(value/ref)),
                                           status='ZMIANA_MODELU_ZRODLA_NIE_TOLERANCJA_GLOSNIKA'))
    table('p26_regularizacja_zrodla.csv', smoothing_rows)
    # Wymiary są przybliżone. +/-5 cm jest zakresem projektu, nie tolerancją pomiaru.
    sensitivity = []
    for axis, L in zip(['x_width', 'y_length', 'z_height'], room.dimensions_xyz_m):
        for delta in [-0.05, 0., 0.05]:
            sensitivity.append(dict(axis=axis, length_m=L + delta,
                                    axial_f_hz=room.c_m_s / (2 * (L + delta)),
                                    status='ZAKRES_SCENARIUSZA_NIE_PRZEDZIAL_UFNOSCI'))
    table('p26_wymiary_i_mody.csv', sensitivity)
    # Konieczny test gabarytu: sześcienna komora, +10l hipotetycznej wyporności.
    # Nie jest to projekt konstrukcji, masa docelowa ani sprawdzenie otworu głośnika.
    geometry_rows = []
    for net_l in [20., 60., 100., 150., 379., 753.]:
        internal_side = ((net_l + 10) / 1000) ** (1/3)
        width = internal_side + 2 * 0.022
        depth = internal_side + 0.022 + 0.044
        height = width
        for source_set in cfg['source_sets']:
            for side, point in enumerate(source_set['positions_xyz_m']):
                x, y, _ = point
                back_clearance = y - depth
                lateral_clearance = min(x - width / 2, room.dimensions_xyz_m[0] - x - width / 2)
                geometry_rows.append(dict(set_id=source_set['id'], source_id=side,
                                          net_l=net_l, assumed_displacement_l=10.,
                                          outer_width_m=width, outer_depth_m=depth, outer_height_m=height,
                                          rear_to_front_wall_clearance_m=back_clearance,
                                          minimum_side_wall_clearance_m=lateral_clearance,
                                          necessary_cube_wall_clearance_0_1m=bool(back_clearance >= 0.1 and lateral_clearance >= 0.1),
                                          pair_floor_area_m2=2 * width * depth,
                                          status='GEOMETRIA_POGLADOWA_NIE_PELNA_KWALIFIKACJA'))
    table('p27_konieczne_gabaryty.csv', geometry_rows)
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    for t60 in cfg['modal_t60_s']:
        pair = full[(t60, 0.2, 'A')].sum(axis=2)
        axes[0, 0].plot(f, db(pair[:, 0]), label=f'T60 modów = {t60} s')
    axes[0, 0].set(ylabel='20 log10 |H|, odn. 1 Pa s/m³', title='A: dwa źródła, U = 1 m³/s na każde (normalizacja)')
    for tau in cfg['zero_relaxation_s']:
        pair = full[(0.4, tau, 'A')].sum(axis=2)
        axes[0, 1].plot(f, db(pair[:, 0]), label=f'τ0 = {tau} s')
    axes[0, 1].set(ylabel='20 log10 |H|, odn. 1 Pa s/m³', title='Wpływ relaksacji jednorodnego ciśnienia')
    for sid in ['A', 'D']:
        pair = full[(0.4, 0.2, sid)]
        ratio = pair[:, 0, :].sum(axis=1) / pair[:, 0, 0]
        axes[1, 0].plot(f, db(ratio), label=f'{sid}: ta sama U na źródło')
        axes[1, 0].plot(f, db(ratio / 2), '--', label=f'{sid}: ta sama suma U')
    axes[1, 0].axhline(20*np.log10(2), color='grey', lw=0.7)
    axes[1, 0].set(ylabel='Para / samo lewe, dB', title='Porównanie normalizacji; bez założenia równej mocy')
    pair = full[(0.4, 0.2, 'D')].sum(axis=2)
    variation = db(pair / pair[:, :1])
    axes[1, 1].fill_between(f, variation.min(axis=1), variation.max(axis=1), alpha=0.3)
    axes[1, 1].set(ylabel='Odchylenie od S0, dB', title='D: sąsiedztwo głowy ±15 cm, pion ±10 cm')
    for ax in axes.flat:
        ax.set(xlim=(10, 120), xlabel='Częstotliwość, Hz')
        ax.grid(alpha=0.25)
        if ax.lines and ax is not axes[1, 1]:
            ax.legend(fontsize=8)
    fig.suptitle('Pokój 3,7 (x) × 4,6 (y) × 2,5 (z) m — scenariusze P26/P27, nie pomiar SPL')
    fig.tight_layout()
    for ext in ['png', 'svg']:
        fig.savefig(OUT / f'10_pokoj_i_dwa_zrodla.{ext}', dpi=160)
    plt.close(fig)
    source_distance = np.linalg.norm(np.array(cfg['assumed_monitors_xyz_m']) - listener, axis=1)
    assert np.all((source_distance >= 2.5) & (source_distance <= 3.0))
    result = dict(status='SCENARIUSZE_P26_P27_NIE_ODPOWIEDZ_ZMIERZONEGO_POKOJU',
                  volume_m3=room.volume_m3, dimensions_xyz_m=list(room.dimensions_xyz_m),
                  assumed_monitor_listener_distances_m=source_distance.tolist(),
                  main_curve_rows=len(curves), diagnostic_rows=len(bands),
                  phase_cases=len(delays), geometry_rows=len(geometry_rows),
                  smoothing_sensitivity_rows=len(smoothing_rows),
                  convergence=convergence_rows,
                  uniform_room_to_100l_box_stiffness_ratio=0.1/room.volume_m3,
                  limitations=['Pozycje i straty nie są zidentyfikowane.',
                               'Brak nielokalnych impedancji ścian, drzwi, mebli i nieprostopadłościennej geometrii.',
                               'Zadana U, brak reakcji pokoju na membranę; nie używać jako przewidywany SPL przetwornika.',
                               'Źródła i odbiorniki rozłożone przez regularizację, nie rysunek membrany.',
                               'Gabaryty tylko konieczne dla jednej sześciennej rodziny, bez potwierdzenia miejsca monitorów/przejść.'])
    (OUT / 'p26_p27_podsumowanie.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(f'P26/P27: {len(curves)} wierszy głównych, {len(bands)} diagnostycznych, {len(delays)} przypadków fazy')
    return result


if __name__ == '__main__':
    main()
