"""Mapa indeksów całkowitych w całym zestawie pasm P06."""
import csv
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR', '/tmp/sub-krystian-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from model_niepewnosci import CFG, FACTORS

ROOT = Path(__file__).resolve().parents[1]


def main():
    rows = list(csv.DictReader((ROOT / 'wyniki/p06_indeksy_sobola.csv').open()))
    n = 2**max(CFG['sobol_powers'])
    fig, axes = plt.subplots(2, 2, figsize=(14, 7), constrained_layout=True)
    frequencies = CFG['frequencies_hz']
    labels = ['Mms', 'Cms', 'BL', 'Rms', 'Re', 'Le', 'Sd', 'Vb', 'Vmax', 'Imax', 'przeciek', 'R+dodatk.', 'próg X']
    for i, cid in enumerate(['C02', 'C11']):
        for j, family in enumerate(['D', 'L']):
            matrix = np.array([[np.mean([float(r['total_order']) for r in rows
                                       if r['candidate_id']==cid and r['family']==family and int(r['n_base'])==n
                                       and float(r['f_hz'])==f and r['factor']==key])
                                for key in FACTORS] for f in frequencies])
            im = axes[i, j].imshow(matrix, vmin=0., vmax=1.05, cmap='viridis', aspect='auto')
            axes[i, j].set(title=f'{cid}, rodzina {family}, N={n}; średnia dwóch scrambli',
                            xticks=np.arange(len(FACTORS)), yticks=np.arange(len(frequencies)),
                            xticklabels=labels, yticklabels=[f'{f:g}' for f in frequencies], ylabel='Hz')
            axes[i, j].tick_params(axis='x', labelrotation=45, labelsize=8)
    fig.colorbar(im, ax=axes.ravel().tolist(), label='Całkowity indeks Sobola S_T (zależny od umownej miary)')
    fig.suptitle('P06: wpływ parametrów zależy od pasma — brak interpretacji jako rozrzut produktów')
    for ext in ['png', 'svg']:
        fig.savefig(ROOT / f'wyniki/12_sobol_pasmo.{ext}', dpi=170)
    plt.close(fig)


if __name__ == '__main__':
    main()
