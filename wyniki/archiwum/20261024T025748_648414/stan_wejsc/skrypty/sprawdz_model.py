"""Kontrole istotnych zależności fizycznych; nie pomiar zgodności z rzeczywistością."""
import json
from pathlib import Path
import numpy as np
from scipy.constants import pi
import sympy as sp
from model_subwoofera import Driver, alignment, response, sealed_shape, linear_envelope, room_modes


def main():
    root = Path(__file__).resolve().parents[1]
    rows = json.loads((root / 'dane/przetworniki/kandydaci.json').read_text())['drivers']
    f = np.geomspace(10, 200, 1000)
    count = 0
    for row in rows:
        d = Driver(**row['model'])
        a = response(d, 60, f)
        b = response(d, 60, f, vrms=2)
        np.testing.assert_allclose(b['spl_rms_db'] - a['spl_rms_db'], 20 * np.log10(2))
        np.testing.assert_allclose(b['x_peak_m'], 2 * a['x_peak_m'])
        np.testing.assert_allclose(b['p_real_w'], 4 * a['p_real_w'])
        distant = response(d, 60, f, distance_m=2)
        np.testing.assert_allclose(a['spl_rms_db'] - distant['spl_rms_db'], 20 * np.log10(2))
        full = response(d, 60, f, solid_angle=4 * pi)
        np.testing.assert_allclose(a['spl_rms_db'] - full['spl_rms_db'], 20 * np.log10(2))
        assert np.all(np.real(a['z']) >= d.re_ohm)
        np.testing.assert_allclose(a['p_real_w'] - a['p_copper_w'],
                                   d.rms * (a['x_peak_m'] * (2*pi*f) / np.sqrt(2))**2,
                                   rtol=1e-10, atol=1e-12)
        fc, qtc, f3 = alignment(d, 60)
        np.testing.assert_allclose(abs(sealed_shape(np.array([f3]), fc, qtc)[0])**2, .5)
        far_fc, far_q, _ = alignment(d, 1e12)
        np.testing.assert_allclose([far_fc, far_q], [d.fs_hz, d.qts], rtol=1e-8)
        # Redukcja elektromechaniki do analitycznego modelu, Le=0.
        from dataclasses import replace
        no_le = replace(d, le_mh=1e-12)
        physical = response(no_le, 60, f)
        p_asymptote = 1.2041 * d.sd * d.bl / (2*pi*d.re_ohm*d.mms)
        analytic = 20*np.log10(p_asymptote / 20e-6 * abs(sealed_shape(f, fc, qtc)))
        np.testing.assert_allclose(physical['spl_rms_db'], analytic, atol=1e-8)
        env = linear_envelope(d, 60, f, 40, 12)
        assert np.all(env['x_peak_m'] <= d.xmax_mm * 1e-3 * (1+1e-12))
        assert np.all(env['i_rms'] <= 12*(1+1e-12))
        assert np.all(env['v_rms'] <= 40*(1+1e-12))
        count += 13
    modes = room_modes([4.6, 3.7, 2.5])
    np.testing.assert_allclose(modes[0]['f_hz'], 343 / (2*4.6))
    # Symboliczna kontrola wzajemnej zgodności podatności, Vas i Fs.
    rho, c, sd, vas, fs = sp.symbols('rho c sd vas fs', positive=True)
    cms = vas / (rho*c**2*sd**2)
    mms = 1 / ((2*sp.pi*fs)**2 * cms)
    assert sp.simplify(1/(2*sp.pi*sp.sqrt(mms*cms)) - fs) == 0
    print(f'PASS: {count + 2} kontroli skalowania, energii, modelu analitycznego i granic; nie walidacja urządzenia.')


if __name__ == '__main__':
    main()
