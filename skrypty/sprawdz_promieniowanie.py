"""P11: niezależne całki, strumień energii, sfera pełna i granice ka."""
from dataclasses import replace
import json
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import quad
from model_subwoofera import Driver
from model_gazu import Medium
from model_promieniowania import (piston_impedance,piston_rayleigh_impedance,piston_added_mass_static,
    piston_on_axis_pressure,mutual_piston_impedance,spherical_cap_impedance,spherical_cap_field,
    spherical_cap_added_mass_static,spherical_cavity_impedance,gaussian_free_impedance)
from odgroda_i_obrazy import image_radiation_matrix,image_angular_resistance,image_pressure_operator
from naped_z_promieniowaniem import reference_calibration,solve_motor_ports

ROOT=Path(__file__).resolve().parents[1]


def main():
    medium=Medium();area=.0841;a=np.sqrt(area/np.pi)
    ka=np.geomspace(1e-7,100.,80);f=ka*medium.c/(2*np.pi*a)
    analytic=piston_impedance(f,area,medium)
    rayleigh=piston_rayleigh_impedance(f,area,512,medium)
    ray_error=float(max(abs(analytic-rayleigh)/np.maximum(abs(analytic),1e-300)))
    assert ray_error<2e-7
    # Moc ze wzoru kierunkowego daje niezależnie część rzeczywistą impedancji.
    angular=image_angular_resistance(f[:65],[area],[[.65,.3]],(),medium,128)[:,0,0].real
    angular_error=float(max(abs(angular-analytic[:65].real)/np.maximum(analytic[:65].real,1e-300)))
    assert angular_error<1e-8
    assert np.all(analytic.real>=0)
    zero=piston_impedance([0.],area,medium)[0];assert zero==0
    low_f=1e-4
    measured_mass=piston_impedance([low_f],area,medium)[0].imag/(2*np.pi*low_f)
    assert abs(measured_mass/piston_added_mass_static(area,medium)-1)<1e-10
    # Dokładne pole na osi vs osobna całka powierzchni Rayleigha.
    faxis=np.array([20.,80.,1000.])
    on_axis=piston_on_axis_pressure(faxis,area,1.,medium)
    integ=image_pressure_operator(faxis,[area],[[0.,0.]],[[0.,1.,0.]],(),medium,24,96)[:,0,0]
    axis_error=float(max(abs(integ/on_axis-1)));assert axis_error<1e-11
    # Sfera pobudzana na całej powierzchni ma prostą dokładną impedancję.
    b=.3;whole=4*np.pi*b*b
    fsphere=np.geomspace(.001,10000,100);x=2*np.pi*fsphere*b/medium.c
    closed=medium.rho*medium.c*whole*1j*x/(1+1j*x)
    sphere=spherical_cap_impedance(fsphere,whole,b,512,medium)
    sphere_error=float(max(abs(sphere/closed-1)));assert sphere_error<1e-12
    # Ciśnienie i prędkość w polu bliskim: używamy Re(p*v_r*), nie |p|²/(rho*c).
    frequencies=np.array([20.,40.,80.,300.])
    cap=spherical_cap_impedance(frequencies,area,b,1024,medium)
    mu,w=leggauss(192)
    flux_errors=[]
    for radius in [.4,1.,10.]:
        p,v=spherical_cap_field(frequencies,area,b,radius,mu,768,medium)
        flux=2*np.pi*radius*radius*np.sum(np.real(p*np.conj(v))*w,axis=1)
        flux_errors.append(float(max(abs(flux/cap.real-1))))
    assert max(flux_errors)<2e-6
    # Zbieżność czaszy i całki pola; skok prędkości na brzegu nie ma zbieżności jednostajnej.
    z256=spherical_cap_impedance(frequencies,area,b,256,medium)
    z512=spherical_cap_impedance(frequencies,area,b,512,medium)
    z1024=cap
    cap_convergence=dict(relative_256_1024=float(max(abs((z256-z1024)/z1024))),
                         relative_512_1024=float(max(abs((z512-z1024)/z1024))))
    assert cap_convergence['relative_512_1024']<2e-5
    mass0=spherical_cap_added_mass_static(area,b,2048,medium)
    mass_small=spherical_cap_impedance([1e-4],area,b,2048,medium)[0].imag/(2*np.pi*1e-4)
    assert abs(mass_small/mass0-1)<1e-10
    # Granica lokalnie płaskiej odgrody, kontrola monotonicznego dojścia masy.
    flat_ratios=[spherical_cap_added_mass_static(area,r*a,8192,medium)/piston_added_mass_static(area,medium) for r in [2.,4.,8.,16.,32.]]
    assert np.all(np.diff(flat_ratios)>0) and .95<flat_ratios[-1]<1.
    # Rigid cavity: biegun jednorodnego sprężania i dodatnia masa rozłożonego powietrza.
    volume=.1;stiffness=medium.gamma*medium.p0_pa*area*area/volume
    cavity=spherical_cavity_impedance([.001,.1,20.],area,volume,1024,medium)
    assert abs(cavity[0]*(2j*np.pi*.001)/stiffness-1)<1e-8
    assert np.all(cavity.real==0)
    # Wzajemne promieniowanie i podłoga/ściana: energia na rzeczywistej domenie kątowej.
    max_image_error=0.
    positions=[[.65,.3],[3.05,.3]]
    for walls in [(),('FLOOR',),('LEFT',),('FLOOR','LEFT')]:
        z=image_radiation_matrix(frequencies[:3],[area,area],positions,walls,medium)
        power=image_angular_resistance(frequencies[:3],[area,area],positions,walls,medium,96)
        max_image_error=max(max_image_error,float(max(abs((z.real-power).ravel()))))
        assert np.max(abs(z-z.transpose(0,2,1)))<1e-12
        assert np.linalg.eigvalsh((z+z.conj().transpose(0,2,1))/2).min()>-1e-12
    assert max_image_error<1e-10
    # Odrębna kwadratura3D radialnego rozkładu par Gaussa.
    sigma=.12;fg=np.array([1e-3,20.,80.,1000.]);zg=gaussian_free_impedance(fg,area,sigma,medium)
    gaussian_errors=[]
    for j,frequency in enumerate(fg):
        k=2*np.pi*frequency/medium.c
        re=quad(lambda r:r*np.exp(-r*r/(4*sigma*sigma))*np.cos(k*r),0.,12*sigma,epsabs=1e-13)[0]
        im=quad(lambda r:r*np.exp(-r*r/(4*sigma*sigma))*np.sin(k*r),0.,12*sigma,epsabs=1e-13)[0]
        expected=medium.rho*2j*np.pi*frequency*area**2/(8*np.pi**1.5*sigma**3)*(re-1j*im)
        gaussian_errors.append(float(abs(expected/zg[j]-1)))
    assert max(gaussian_errors)<1e-10 and np.min(zg.real)>=0
    # Kalibracja i napęd wszystkich24przetworników.
    data=json.loads((ROOT/'dane/przetworniki/pula_rozszerzona.json').read_text())['drivers']
    max_reference=max_energy=0.
    cases=0
    for row in data:
        d=Driver(**row['model'])
        for faces in [1.,2.]:
            motor,_=reference_calibration(d,faces,medium=medium)
            s=2j*np.pi*d.fs_hz;rad=faces*piston_impedance([d.fs_hz],d.sd,medium)[0]
            z=motor.resistance_n_s_m+s*motor.mass_kg+1/(s*motor.compliance_m_n)+rad
            max_reference=max(max_reference,float(abs(z-d.rms)/d.rms))
            rear=spherical_cavity_impedance(frequencies[:3],d.sd,.1,512,medium)[:,None]
            front=spherical_cap_impedance(frequencies[:3],d.sd,.31,512,medium)[:,None,None]
            out=solve_motor_ports(frequencies[:3],[motor],rear,front,[1.])
            max_energy=max(max_energy,float(max(abs(out['energy_residual_w'])/out['input_w'])))
            assert np.all(out['radiation_w']>=0);cases+=1
    assert max_reference<1e-12 and max_energy<1e-12
    # Kalibracja nie może tworzyć ujemnej mechanicznej dyssypacji.
    d=Driver(**data[0]['model']);invalid=replace(d,qms=1e9)
    try:reference_calibration(invalid,2.,medium=medium)
    except ValueError:pass
    else:raise AssertionError('Brak odrzucenia ujemnego R pozostałego')
    result=dict(status='PASS_WZORCOWE_GEOMETRIE_NIE_WALIDACJA_SKRZYNI',
                rayleigh_vs_struve_max_relative_error=ray_error,angular_power_max_relative_error=angular_error,
                axis_pressure_integral_max_relative_error=axis_error,full_sphere_max_relative_error=sphere_error,
                cap_flux_max_relative_error=max(flux_errors),cap_convergence=cap_convergence,
                cap_flat_static_mass_ratios=flat_ratios,image_power_max_absolute_error=max_image_error,
                gaussian_integral_max_relative_error=max(gaussian_errors),reference_point_max_relative_error=max_reference,
                motor_cases=cases,max_motor_relative_energy_residual=max_energy,
                limits=['ka->0','ka duże','f=0','pełna sfera','czasza->płaska odgroda','biegunK/s komory','ujemnyR kalibracji'],
                caveat='Wzorcowe geometrie, konwencja referencyjnego powietrza i dane T/S pozostają jawnymi założeniami.')
    (ROOT/'wyniki/p11_weryfikacja.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return result


if __name__=='__main__':main()
