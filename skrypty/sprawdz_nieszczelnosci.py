"""N7: niezależny układ równań, bilans, stany, asymptoty i błędne wejścia."""
from dataclasses import replace
import json
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import roots_legendre
from model_subwoofera import C, RHO, Driver, alignment, response, linear_envelope, room_modes
from model_nieszczelnosci import leakage_response, state_matrices

ROOT = Path(__file__).resolve().parents[1]


def independent(d, vb, f, leak_hz, voltage):
    """Bez wywołania analitycznego rdzenia: I,x,p,U z czterech praw pierwotnych."""
    s = 2j*np.pi*f
    cab = vb*1e-3/(RHO*C*C)
    g = 2*np.pi*leak_hz*cab if np.isfinite(leak_hz) else 0.
    mat = np.array([[d.re_ohm+s*d.le_mh*1e-3, d.bl*s, 0, 0],
                    [-d.bl, d.mms*s*s+d.rms*s+1/d.cms, -d.sd, 0],
                    [0, d.sd*s, s*cab, 1],
                    [0, 0, -g, 1]], dtype=complex)
    if np.isposinf(leak_hz):
        mat[3] = [0, 0, 1, 0]
    return np.linalg.solve(mat, [voltage, 0, 0, 0])


def main(catalog_path=None):
    catalog = Path(catalog_path) if catalog_path is not None else ROOT/'dane/przetworniki/kandydaci.json'
    drivers = [Driver(**r['model']) for r in json.loads(catalog.read_text())['drivers']]
    f = np.geomspace(.1, 200, 91)
    max_energy, max_independent, max_regression = 0., 0., 0.
    scenario_count = state_count = 0
    controls = []
    for d in drivers:
        for vb in (30, 45, 60, 80, 100, 120):
            for leak_hz in (0., 1., 3., 10., np.inf):
                out = leakage_response(d, vb, f, leak_hz, vrms=2.83)
                scale = np.maximum(out['p_input_w'], 1e-24)
                err = np.max(abs(out['energy_residual_w'])/scale)
                max_energy = max(max_energy, float(err))
                assert err < 2e-13
                assert np.all(out['p_leak_loss_w'] >= 0)
                assert np.all(out['radiation_diagnostic_w'] >= 0)
                for freq in (.001, 1., 20., 37., 80., 200.):
                    a = leakage_response(d, vb, freq, leak_hz, vrms=2.83)
                    b = independent(d, vb, freq, leak_hz, 2.83)
                    for actual, expected in [(a['i_complex_a'],b[0]), (a['x_complex_m'],b[1]),
                                              (a['p_inside_pa'],b[2]), (a['u_leak_m3_s'],b[3])]:
                        np.testing.assert_allclose(actual, expected, rtol=3e-9, atol=1e-13)
                    max_independent = max(max_independent, float(abs(a['x_complex_m']/b[1]-1)))
                mat, bv, xi = state_matrices(d, vb, leak_hz)
                poles = np.linalg.eigvals(mat)
                assert np.max(poles.real) < 0
                # Inny zapis rachunku: odpowiedź realizacji stanu.
                for freq in (1., 20., 80.):
                    states = np.linalg.solve(2j*np.pi*freq*np.eye(len(mat))-mat, bv*2.83)
                    np.testing.assert_allclose(states[xi], leakage_response(d,vb,freq,leak_hz,2.83)['x_complex_m'],rtol=1e-10,atol=1e-14)
                state_count += 1
                if leak_hz == 0:
                    base = response(d, vb, f, 2.83, solid_angle=4*np.pi)
                    re = np.max(abs(out['x_peak_m']/base['x_peak_m']-1))
                    max_regression = max(max_regression,float(re))
                    np.testing.assert_allclose(out['spl_4pi_db'],base['spl_rms_db'],atol=2e-12)
                scenario_count += 1
        controls.append(d.name+': bilans, równania pierwotne, stabilność i realizacja stanu')
    d = drivers[0]
    # DC i niezamienność granic: nawet wolny przeciek znosi statyczną sprężynę.
    for leak_hz in (0.,1.,10.,np.inf):
        dc = leakage_response(d,60,0.,leak_hz,1.)
        keff = 1/d.cms+(d.sd*d.sd/(.06/(RHO*C*C)) if leak_hz==0 else 0)
        np.testing.assert_allclose(dc['x_complex_m'],d.bl/(d.re_ohm*keff),rtol=1e-13)
        assert np.isneginf(dc['spl_4pi_db']) and dc['p_total_pa']==0
    controls.append('DC zredukowane; przypadki szczelny/otwarty; brak sztucznego floor dla zera')
    # Asymptota ciśnienia: dla równych dróg omega³, dla nierównych ogólnie omega².
    low = np.array([1e-6,2e-6])
    equal = leakage_response(d,60,low,3.)
    axial = leakage_response(d,60,low,3.,leak=(0,0,-.35))
    np.testing.assert_allclose(abs(equal['p_total_pa'][1]/equal['p_total_pa'][0]),8.,rtol=1e-8)
    np.testing.assert_allclose(abs(axial['p_total_pa'][1]/axial['p_total_pa'][0]),4.,rtol=1e-8)
    open_equal = leakage_response(d,60,f,np.inf)
    assert np.all(open_equal['p_total_pa']==0) and np.all(open_equal['radiation_diagnostic_w']==0)
    open_axial = leakage_response(d,60,f,np.inf,leak=(0,0,-.35))
    assert np.all(abs(open_axial['p_total_pa'])>0)
    controls.append('Asymptoty omega³/omega² i otwarty dipol z rozdzielonymi źródłami')
    # Całka kątowa mocy dalekiego pola niezależna od formy analitycznej sinc.
    mu, weights = roots_legendre(128)
    for freq in (.01,20.,80.,200.):
        out = leakage_response(d,60,freq,10.,leak=(0,0,-.35))
        z = 2*np.pi*freq*.35/C
        field = out['u_membrane_m3_s']+out['u_leak_m3_s']*np.exp(-1j*z*mu)
        integral = RHO*(2*np.pi*freq)**2/(8*np.pi*C)*np.sum(weights*abs(field)**2)
        np.testing.assert_allclose(out['radiation_diagnostic_w'],integral,rtol=2e-10,atol=1e-25)
    controls.append('Moc diagnostyczna: niezależna kwadratura Gaussa i człon interferencyjny')
    # Granice Le=0 i algebraicznie wysokiej częstotliwości.
    no_le = replace(d,le_mh=0.)
    for leak_hz in (0.,3.,np.inf):
        aa,bb,xi = state_matrices(no_le,60,leak_hz)
        assert np.max(np.linalg.eigvals(aa).real)<0
        st = np.linalg.solve(2j*np.pi*20*np.eye(len(aa))-aa,bb)
        np.testing.assert_allclose(st[xi],leakage_response(no_le,60,20,leak_hz)['x_complex_m'],rtol=1e-12)
    high = np.array([1e7,2e7])
    h1 = leakage_response(d,60,high,3.)
    h0 = leakage_response(no_le,60,high,3.)
    np.testing.assert_allclose(abs(h1['v_complex_m_s'][1]/h1['v_complex_m_s'][0]),.25,rtol=1e-5)
    np.testing.assert_allclose(abs(h0['v_complex_m_s'][1]/h0['v_complex_m_s'][0]),.5,rtol=1e-5)
    controls.append('Le=0: redukcja stanu, stabilność; formalne granice wysokoczęstotliwościowe')
    # Niezależna integracja czasowa pełnego układu stanu dla sinusoidalnego napięcia.
    mat,bv,xi = state_matrices(d,60,3.)
    pole_slow = abs(np.max(np.linalg.eigvals(mat).real))
    end = max(1.,12/pole_slow)
    t = np.linspace(end-.2,end,401)
    sol = solve_ivp(lambda tt,y:mat@y+bv*np.cos(2*np.pi*20*tt),(0,end),np.zeros(len(mat)),
                    method='Radau',rtol=1e-9,atol=1e-12,t_eval=t,max_step=.002)
    assert sol.success
    exact = np.real(leakage_response(d,60,20.,3.)['x_complex_m']*np.exp(2j*np.pi*20*t))
    np.testing.assert_allclose(sol.y[xi],exact,atol=2e-9,rtol=2e-4)
    controls.append('Rozwiązanie ODE Radau kontra ustalona odpowiedź fazorowa')
    # Skrajne dodatnie Q: F3 bez arbitralnego bracketu pierwiastka.
    for q in (1e-6,.01,.1,.7071067811865475,10.,1e6):
        dd = replace(d,qes=2*q,qms=2*q)
        fc,qt,f3 = alignment(dd,1e12)
        r=f3/fc
        power=r**4/((1-r*r)**2+r*r/(qt*qt))
        np.testing.assert_allclose(power,.5,rtol=1e-12)
    controls.append('F3 dla Q od1e-6 do1e6; eliminacja ograniczenia bracketu')
    rejects = [lambda:leakage_response(d,0,[20]),lambda:leakage_response(d,60,[np.nan]),
               lambda:leakage_response(d,60,[-1]),lambda:leakage_response(d,60,[20],-1),
               lambda:leakage_response(d,60,[20],np.nan),lambda:leakage_response(d,60,[20],vrms=np.inf),
               lambda:leakage_response(d,60,[20],observer=(0,0,0)),lambda:leakage_response(d,60,[],0),
               lambda:response(d,60,[np.nan]),lambda:linear_envelope(d,60,[20],-1,12),
               lambda:room_modes([4.6,np.inf,2.5]),lambda:room_modes([4.6,3.7,2.5],c=0),
               lambda:replace(d,re_ohm=0),lambda:replace(d,le_mh=-1)]
    for fn in rejects:
        try: fn()
        except ValueError: pass
        else: raise AssertionError('Nie odrzucono błędnego wejścia')
    controls.append(f'Odrzucanie {len(rejects)} błędnych wejść; NaN, inf, ujemne i zerowe wielkości')
    result={'status':'WERYFIKACJA_NUMERYCZNA_NIE_POMIAR','scenarios':scenario_count,
            'stable_state_models':state_count,'max_relative_energy_residual':max_energy,
            'max_relative_independent_displacement_error':max_independent,
            'max_relative_sealed_regression_error':max_regression,'controls':controls,
            'missing':'Nie zidentyfikowano rzeczywistego Ra ani reakcji promieniowania powierzchni skończonych.'}
    filename = 'n7_weryfikacja_pula.json' if catalog_path is not None else 'n7_weryfikacja.json'
    (ROOT/'wyniki'/filename).write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
