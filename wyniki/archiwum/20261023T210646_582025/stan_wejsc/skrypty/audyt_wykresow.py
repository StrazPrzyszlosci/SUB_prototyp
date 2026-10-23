"""Przeliczenia odczytów z obrazów WinISD, bez udawania pomiaru czy digitalizacji."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    ft3_l = 28.316846592
    inch_mm = 25.4
    # Odczyt widocznych pól z załączników04/05 i odręcznego bilansu06.
    box_ft3, fb_hz = 3.7, 24.0
    width_in, height_in, length_in = 15.75, 2.0, 35.03
    area_cm2 = (width_in * inch_mm / 10) * (height_in * inch_mm / 10)
    port_l = area_cm2 * (length_in * inch_mm / 10) / 1000
    result = {
        'status': 'ODCZYT_OBRAZU_I_PRZELICZENIE_NIE_POMIAR',
        'source_url': 'https://www.diyaudio.com/community/threads/help-finalising-enclosure-design-dayton-rss315hf-4.360765/',
        'source_date': '2020-09-27', 'access_date': '2026-10-23',
        'box_ft3_read': box_ft3, 'box_net_l_calculated': box_ft3 * ft3_l,
        'fb_hz_read': fb_hz,
        'port_dimensions_in_read': [width_in, height_in, length_in],
        'port_area_cm2_calculated': area_cm2,
        'port_air_volume_l_calculated': port_l,
        'port_air_volume_l_handwritten': .638 * ft3_l,
        'handwritten_net_ft3_calculated': 4.45 - .0581 - .638 - .05,
        'handwritten_net_l_calculated': (4.45 - .0581 - .638 - .05) * ft3_l,
        'f3_visual_estimate_hz': [21, 23],
        'excursion_xmax_crossing_visual_estimate_hz': [20, 22],
        'xmax_reference_line_visual_mm': 14.3,
        'missing': ['Napięcie/moc wejściowa (zakładka Signal niewidoczna)',
                    'Pełny zestaw T/S z użytej bazy', 'Aktywne filtry i straty',
                    'Definicja jednostek velocity/excursion w tej konfiguracji WinISD'],
        'images_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in sorted((ROOT/'dane/zrodla/obrazy_diyaudio_360765').glob('*')) if p.suffix in ('.png','.jpg')}
    }
    (ROOT/'wyniki/audyt_wykresow_diyaudio.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(f'WinISD: Vb={result["box_net_l_calculated"]:.2f} l; port={port_l:.2f} l; pole={area_cm2:.2f} cm²')


if __name__ == '__main__':
    main()
