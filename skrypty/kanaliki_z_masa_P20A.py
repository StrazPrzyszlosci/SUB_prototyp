"""Masa przecieku jako kontrprzykład modelu czysto rezystancyjnego wkładu."""
from pathlib import Path
from itertools import product
import hashlib,json
import numpy as np
import sympy as sp
from model_gazu import Medium
from model_wypelnienia import CircularPores
from model_wkladu_P20A import HollowModule
from analiza_wkladow_P20A import table

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def main():
    p=ROOT/'dane/konfiguracje/p20a_kanaliki_kontrolne.json';cfg=json.loads(p.read_text())
    basepath=ROOT/'dane/konfiguracje/p20a_regulacja_objetosci.json';base=json.loads(basepath.read_text());medium=Medium()
    m=HollowModule(base['selected_comparison_outer_width_length_height_m'],.008,'CCCC',base,braced=True)
    lo,hi,n=cfg['frequency_hz_grid'];f=np.geomspace(lo,hi,int(n));s=2j*np.pi*f
    chi=m.wall_compliance(f);Ci=m.inner_volume/(medium.gamma*medium.p0_pa)
    rows=[];screens=[];peaks=[];max_power=0.
    for radius,extension in product(cfg['radius_m'],cfg['end_inertance_lengths_in_radii_assumed']):
        area=np.pi*radius**2;L=m.wall
        density,_=CircularPores(radius,1.,'rigid',20.).equivalent_properties(f,medium)
        Z=s*density*L/area+s*medium.rho*extension*radius/area;G=1/Z
        pi=(G+s*chi)/(G+s*(chi+Ci));difference=1-pi;Qleak=G*difference;Y=s*Ci*pi
        wall_loss=abs(difference)**2*np.real(s*chi);neck_loss=abs(Qleak)**2*Z.real
        err=abs(Y.real-wall_loss-neck_loss)/np.maximum(abs(Y),1e-30);max_power=max(max_power,float(err.max()))
        assert np.min(Y.real)>=-1e-15 and np.min(Z.real)>0
        velocity_per_pa=abs(Qleak)/area;peak_index=int(np.argmax(Y.real))
        Rdc=8*medium.viscosity_pa_s*L/(np.pi*radius**4)
        Mlow=medium.rho*((4/3)*L+extension*radius)/area
        proxy=1/(2*np.pi*np.sqrt(Mlow*(Ci+m.chi_static)))
        vpk=np.sqrt(2)*velocity_per_pa
        plimit=np.minimum(cfg['displacement_to_radius_screen_limit_assumed']*(2*np.pi*f)*radius/np.maximum(vpk,1e-300),
                         cfg['peak_mach_screen_limit_assumed']*medium.c/np.maximum(vpk,1e-300))
        peaks.append(dict(radius_mm=radius*1000,end_length_in_r=extension,
            low_frequency_R_pa_s_m3=Rdc,low_frequency_inertance_pa_s2_m3=Mlow,
            low_frequency_Helmholtz_proxy_hz=proxy,sampled_max_ReY_frequency_hz=float(f[peak_index]),
            small_amplitude_screen_pressure_at_peak_pa_rms=float(plimit[peak_index]),
            length_to_radius=L/radius))
        for j,freq in enumerate(f):
            rows.append(dict(radius_mm=radius*1000,end_length_in_r=extension,f_hz=float(freq),
                neck_resistance_pa_s_m3=float(Z[j].real),neck_reactance_pa_s_m3=float(Z[j].imag),
                module_admittance_real=float(Y[j].real),module_admittance_imag=float(Y[j].imag),
                velocity_rms_m_s_per_outer_pa=float(velocity_per_pa[j]),screen_outer_pa_rms=float(plimit[j])))
        for pressure in cfg['outer_pressure_rms_pa_cases']:
            Re=medium.rho*(vpk*pressure)*(2*radius)/medium.viscosity_pa_s
            Ma=vpk*pressure/medium.c;excursion=vpk*pressure/(2*np.pi*f*radius)
            failed=(Ma>cfg['peak_mach_screen_limit_assumed'])|(excursion>cfg['displacement_to_radius_screen_limit_assumed'])
            screens.append(dict(radius_mm=radius*1000,end_length_in_r=extension,outer_pressure_pa_rms=pressure,
                max_peak_Reynolds=float(Re.max()),max_peak_Mach=float(Ma.max()),max_particle_displacement_to_radius=float(excursion.max()),
                failed_frequency_points=int(failed.sum()),total_frequency_points=len(f),
                scope='Screen only, not validated flow, turbulence threshold, noise or real-hole performance.'))
    assert max_power<1e-10
    x=sp.symbols('x');cv=x/8-x*x/48+11*x**3/3072-19*x**4/30720
    inertance=sp.limit((x/cv-8)/x,x,0);assert inertance==sp.Rational(4,3)
    table('p20a_kanaliki_porty.csv',rows);table('p20a_kanaliki_piki_i_dziedzina.csv',peaks);table('p20a_kanaliki_amplituda.csv',screens)
    inputs=[p,basepath,Path(__file__),ROOT/'skrypty/model_wkladu_P20A.py',ROOT/'skrypty/model_wypelnienia.py',ROOT/'skrypty/model_gazu.py',ROOT/'skrypty/model_plyty_MITC_P18.py']
    result=dict(status='LINEAR_INERTIAL_NECK_COUNTEREXAMPLES_WITH_EXPLICIT_AMPLITUDE_SCREENS',cases=len(peaks),frequency_rows=len(rows),amplitude_screens=len(screens),
        max_normalized_power_residual=max_power,low_frequency_inertance_to_slug=str(inertance),
        input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},limitations=cfg['notes'])
    (OUT/'p20a_kanaliki_podsumowanie.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print('P20A neck:',result['cases'],'cases,',result['frequency_rows'],'rows;',max_power,flush=True)


if __name__=='__main__':main()
