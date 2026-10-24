"""Niezależna termodynamika, radialna dyfuzja FV, granice i energia P09/P10."""
import csv
from dataclasses import replace
import json
from pathlib import Path
import numpy as np
from scipy.linalg import solve_banded
from scipy.integrate import solve_ivp
from model_subwoofera import Driver, response
from model_nieszczelnosci import leakage_response
from model_gazu import Medium, ThermalSpectrum, gas_response, gas_state, conductance_from_reference
from model_wypelnienia import CircularPores, layer_impedance, response_with_acoustic_impedance, two_temperature_modulus
from termodynamika_nieliniowa import periodic_gas, periodic_gas_ode, cycle_energy, static_offset

ROOT=Path(__file__).resolve().parents[1]


def independent_thermodynamic(d, vb_l, f, tau, leak_ref, medium):
    """Nie używa K(s). Niewiadome: i,x,p,delta_rho/rho,delta_T/T0."""
    s=2j*np.pi*f;volume=vb_l*1e-3
    g=conductance_from_reference(leak_ref,medium)
    matrix=np.zeros((5,5),complex)
    matrix[0,:3]=[d.re_ohm+s*d.le_mh*1e-3,d.bl*s,0]
    matrix[1,:3]=[-d.bl,d.mms*s*s+d.rms*s+1/d.cms,-d.sd]
    matrix[2,1:4]=[d.sd*s/volume,g/volume,s]
    matrix[3,2:]=[1.,-medium.p0_pa,-medium.p0_pa]
    if tau == 0:matrix[4,4]=1.
    else:
        matrix[4,1]=(medium.gamma-1)*d.sd*s/volume
        matrix[4,2]=(medium.gamma-1)*g/volume
        matrix[4,4]=s+(0. if np.isposinf(tau) else 1/tau)
    return np.linalg.solve(matrix,np.array([1.,0.,0.,0.,0.]))


def radial_fv(f_hz,radius_m,cells,medium):
    """Niezależne zachowawcze FV równania dyfuzji w przekroju poru."""
    dr=radius_m/cells
    faces=np.arange(cells+1)*dr
    volume=(faces[1:]**2-faces[:-1]**2)/2
    lower=faces[:-1]/(dr*volume)
    upper=faces[1:]/(dr*volume)
    upper[-1]*=2  # Ściana Dirichleta leży pół kroku od środka komórki.
    diag=lower+upper
    s=2j*np.pi*f_hz
    def solve(coefficient,inertial,rhs):
        ab=np.zeros((3,cells),complex)
        ab[1]=coefficient*diag+inertial
        ab[0,1:]=-coefficient*upper[:-1]
        ab[2,:-1]=-coefficient*lower[1:]
        value=solve_banded((1,1),ab,np.full(cells,rhs,dtype=complex))
        return np.sum(value*volume)/np.sum(volume)
    velocity=solve(medium.viscosity_pa_s,s*medium.rho,1.)
    alpha=medium.thermal_conductivity_w_m_k/(medium.rho*medium.cp)
    temperature=solve(alpha,s,s)
    return 1/(s*velocity), medium.gamma*medium.p0_pa/(medium.gamma-(medium.gamma-1)*temperature)


def main():
    drivers=[Driver(**r['model']) for r in json.loads((ROOT/'dane/przetworniki/pula_rozszerzona.json').read_text())['drivers']]
    physical_medium=Medium();legacy=Medium.legacy()
    frequencies=np.array([20.,25.,31.5,40.,63.,80.])
    specs=[ThermalSpectrum((x,),(1.,)) for x in [0.,0.0005,0.005,0.05,0.5,np.inf]]
    specs.append(ThermalSpectrum((.0005,.005,.05),(.25,.5,.25)))
    max_power=max_state=max_direct=max_legacy=0.
    stable=0
    for d in drivers:
        for vb in [30.,100.,150.]:
            for spec in specs:
                for leak in [0.,1.,3.,np.inf]:
                    out=gas_response(d,vb,frequencies,spec,physical_medium,leak)
                    max_power=max(max_power,float(np.max(abs(out['energy_residual_w'])/out['p_input_w'])))
                    assert np.all(out['p_thermal_w']>=0) and np.all(out['p_leak_w']>=0)
                    a,b,idx,w=gas_state(d,vb,spec,physical_medium,leak)
                    assert max(np.linalg.eigvals(a).real)<0
                    stable+=1
                    chol=np.linalg.cholesky(w)
                    transformed=chol.T@a@np.linalg.inv(chol.T)
                    dissip=-(transformed+transformed.T)/2
                    assert min(np.linalg.eigvalsh(dissip))>=-1e-10*max(1,np.linalg.norm(transformed))
                    # Wybór kilku częstotliwości kontroluje całą realizację stanu.
                    for fi in [0,3,5]:
                        z=np.linalg.solve(2j*np.pi*frequencies[fi]*np.eye(len(a))-a,b)
                        err=abs(z[idx['x']]-out['x_complex_m'][fi])/abs(out['x_complex_m'][fi])
                        max_state=max(max_state,float(err))
                    if len(spec.times_s)==1 and np.isfinite(leak):
                        for fi in [0,5]:
                            independent=independent_thermodynamic(d,vb,frequencies[fi],spec.times_s[0],leak,physical_medium)
                            max_direct=max(max_direct,float(abs(independent[1]/out['x_complex_m'][fi]-1)))
            spec=ThermalSpectrum((np.inf,),(1.,))
            for leak in [0.,1.,3.,np.inf]:
                new=gas_response(d,vb,frequencies,spec,legacy,leak)
                old=leakage_response(d,vb,frequencies,leak*100/vb)
                max_legacy=max(max_legacy,float(np.max(abs(new['x_complex_m']/old['x_complex_m']-1))))
    assert max_power<2e-13 and max_state<2e-11 and max_direct<2e-11 and max_legacy<2e-12
    # DC i formalne końce: Le=0, gamma=1, brak ciśnienia przy Ra=0.
    d=drivers[1]
    dc=gas_response(d,100,[0.],ThermalSpectrum(),physical_medium,0.)
    expected=d.bl/(d.re_ohm*(1/d.cms+physical_medium.p0_pa*d.sd**2/.1))
    assert abs(dc['x_complex_m'][0]/expected-1)<1e-13
    for leak in [0.,3.,np.inf]:
        no_le=replace(d,le_mh=0.)
        a,b,idx,w=gas_state(no_le,100,ThermalSpectrum(),physical_medium,leak)
        assert max(np.linalg.eigvals(a).real)<0
    gamma1=replace(physical_medium,gamma=1.)
    assert np.all(ThermalSpectrum().bulk_modulus(frequencies,gamma1)==gamma1.p0_pa)
    open_dc=gas_response(d,100,[0.],ThermalSpectrum(),physical_medium,3.)
    assert abs(open_dc['x_complex_m'][0]/(d.bl*d.cms/d.re_ohm)-1)<1e-13
    # Niezależna przestrzenna dyfuzja, nie drugi zapis tych samych funkcji Bessela.
    fv_rows=[]
    for radius in [.00005,.0002,.001]:
        pores=CircularPores(radius,1.)
        for f in [20.,80.,400.]:
            exact_rho,exact_k=pores.equivalent_properties([f],physical_medium)
            for cells in [64,128,256,512]:
                rho,k=radial_fv(f,radius,cells,physical_medium)
                fv_rows.append(dict(radius_m=radius,f_hz=f,cells=cells,
                                    relative_density_error=float(abs(rho/exact_rho[0]-1)),
                                    relative_modulus_error=float(abs(k/exact_k[0]-1))))
    with (ROOT/'wyniki/p09_dyfuzja_FV_zbieznosc.csv').open('w',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=list(fv_rows[0]));writer.writeheader();writer.writerows(fv_rows)
    assert max(max(r['relative_density_error'],r['relative_modulus_error']) for r in fv_rows if r['cells']==512)<2e-4
    # Granica Poiseuille'a, izotermiczna/adiabatyczna, nieruchomy/wiotki szkielet.
    material=CircularPores()
    rho_low,k_low=material.equivalent_properties([1e-6],physical_medium)
    assert abs((2j*np.pi*1e-6*rho_low[0])/material.flow_resistivity(physical_medium)-1)<1e-5
    assert abs(k_low[0]/(physical_medium.p0_pa/material.porosity)-1)<1e-7
    _,k_high=material.equivalent_properties([1e10],physical_medium)
    assert abs(k_high[0]/(physical_medium.gamma*physical_medium.p0_pa/material.porosity)-1)<1e-3
    full_f=np.geomspace(.0001,1e5,800)
    for frame in ['rigid','limp']:
        mat=replace(material,frame=frame)
        one=layer_impedance(full_f,.2,[(.5,mat)],physical_medium)
        two=layer_impedance(full_f,.2,[(.25,mat),(.25,mat)],physical_medium)
        assert np.max(abs((two-one)/one))<1e-11
        assert np.min(one.real)>-1e-9
        out=response_with_acoustic_impedance(d,full_f,one,medium=physical_medium,leak_hz_ref=1.)
        assert np.max(abs(out['energy_residual_w'])/out['p_input_w'])<2e-12
    # Dwa Cp: granica izolowanego materiału i strata zgodna z Im(K).
    for ratio in [1.,10.,100.]:
        two=two_temperature_modulus([1e-6,20.,80.],100,ratio,medium=physical_medium)
        low_expected=physical_medium.p0_pa*(1+(physical_medium.gamma-1)/(1+ratio))
        assert abs(two['bulk_modulus_pa'][0]/low_expected-1)<1e-6
        power=2*np.pi*np.array([1e-6,20.,80.])*.1*two['bulk_modulus_pa'].imag
        assert np.max(abs(power-two['thermal_dissipation_per_rms_strain_w'])/np.maximum(power,1e-12))<1e-6
    # FFT okresowa i niezależne strzelanie ODE.
    max_ode=max_period=max_fft=0.
    for eps in [.001,.05,.2]:
        for a in [.01,.1,1.,10.,100.]:
            fft=periodic_gas(eps,a,1024,physical_medium)
            p,t,residual=periodic_gas_ode(eps,a,1024,physical_medium)
            max_ode=max(max_ode,float(np.max(abs(p-fft['pressure_pa']))/physical_medium.p0_pa))
            max_period=max(max_period,residual)
            refined=periodic_gas(eps,a,2048,physical_medium)
            max_fft=max(max_fft,abs(fft['h2_to_h1_pct']-refined['h2_to_h1_pct']),abs(fft['h3_to_h1_pct']-refined['h3_to_h1_pct']))
    assert max_ode<1e-8 and max_period<1e-8 and max_fft<1e-8
    energy=cycle_energy(.05,20.,100.,.005,physical_medium)
    assert abs(energy['energy_residual_w'])<1e-8 and abs(energy['exergy_residual_w'])<1e-8
    # Granica małego ruchu zgodna z liniowym modułem, bez dopasowywania THD.
    eps=1e-4;a=1.
    small=periodic_gas(eps,a,4096,physical_medium)
    k=ThermalSpectrum((a/(2*np.pi*20),),(1.,)).bulk_modulus([20.],physical_medium)[0]
    assert abs(small['fundamental_peak_pa']/(eps*abs(k))-1)<1e-7
    # Nieskładanie się granic H->0 i t->inf przy zadanej objętości.
    initial=periodic_gas(.2,np.inf,4096,physical_medium,'initial_entropy')
    periodic=periodic_gas(.2,np.inf,4096,physical_medium,'periodic_limit')
    assert abs(initial['pressure_dc_relative_pa']-periodic['pressure_dc_relative_pa'])>1.
    for dt in [-10.,0.,10.]:
        case=static_offset(d,100,physical_medium.temperature_k+dt,physical_medium.p0_pa,physical_medium)
        assert case['volume_ratio']>0
        force_gas=d.sd*(case['inside_pressure_pa']-physical_medium.p0_pa)
        assert abs(force_gas-case['x_bias_m']/d.cms)<1e-8
    result=dict(status='PASS_WERYFIKACJA_MODELI_NIE_POMIAR_MATERIALU',stable_state_models=stable,
                max_relative_power_residual=max_power,max_relative_state_frequency_error=max_state,
                max_relative_primitive_thermodynamics_error=max_direct,max_relative_legacy_N7_error=max_legacy,
                finite_volume_cases=len(fv_rows),max_fv_error_at512=max(max(r['relative_density_error'],r['relative_modulus_error']) for r in fv_rows if r['cells']==512),
                nonlinear_ode_max_pressure_error_over_p0=max_ode,nonlinear_ode_periodic_residual=max_period,
                nonlinear_fft_harmonics_difference_pct=max_fft,nonlinear_cycle_energy=energy,
                scope='Dodatnie modele i jawne założenia; brak danych rzeczywistego wypełnienia i pełnych nieliniowości głośnika.')
    (ROOT/'wyniki/p09_p10_weryfikacja.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return result


if __name__=='__main__':main()
