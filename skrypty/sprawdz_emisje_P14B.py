"""Wzorce analityczne widma, mieszania oraz źródła w czasie opóźnionym."""
import json
from pathlib import Path
import numpy as np
from model_gazu import Medium
from model_wymuszen_P14B import rms_spectrum
from model_emisji_P14B import moving_monopole,retarded_time,mixing_products,pressure_metrics

ROOT=Path(__file__).resolve().parents[1]


def main():
    cfg=json.loads((ROOT/'dane/konfiguracje/p14b_emisja.json').read_text())
    dynamic=json.loads((ROOT/'dane/konfiguracje/p14b_IMD.json').read_text())
    m=Medium();checks={}
    # Parseval obejmuje DC i Nyquista; niezależny rachunek bez FFT.
    n=16384;t=np.arange(n)/n
    samples=.3+np.sqrt(2)*2*np.cos(2*np.pi*13*t+.7)+.4*(-1.)**np.arange(n)
    spectrum=rms_spectrum(samples)
    checks['Parseval_DC_Nyquist_error']=float(abs(np.linalg.norm(spectrum)**2-(.3**2+2**2+.4**2)))
    assert checks['Parseval_DC_Nyquist_error']<1e-12
    # Zwykła nieliniowość wielomianowa: znane współczynniki i fazy IM2/IM3.
    errors=[]
    for low,high in ((20,85),(25,95),(45,95),(85,20)):
        a,b=.7,1.3;pa,pb=.43,-.61
        x=np.sqrt(2)*a*np.cos(2*np.pi*low*t+pa)+np.sqrt(2)*b*np.cos(2*np.pi*high*t+pb)
        sp2=rms_spectrum(x*x);sp3=rms_spectrum(x*x*x)
        for name,freq,k,l in mixing_products((low,high)):
            if name.startswith('IM2'):
                expected=np.sqrt(2)*a*b*np.exp(1j*(k*pa+l*pb));actual=sp2[int(freq)]
            else:
                expected=1.5*a**abs(k)*b**abs(l)*np.exp(1j*(k*pa+l*pb));actual=sp3[int(freq)]
            errors.append(abs(actual-expected)/abs(expected))
    checks['polynomial_complex_mixing_error']=float(max(errors));assert max(errors)<1e-12
    # Ruch prostoliniowy ma jawny czas opóźniony, dopóki źródło przed obserwatorem.
    r=1.;v=12.;times=np.linspace(0,.01,101)
    state=lambda tau:(v*tau,np.full_like(tau,v))
    tau,d,mr,diag=retarded_time(times,state,r,1.,m.c)
    exact=(times-r/m.c)/(1-v/m.c)
    checks['uniform_motion_retarded_time_error_s']=float(max(abs(tau-exact)))
    assert checks['uniform_motion_retarded_time_error_s']<2e-13
    assert max(abs(mr-v/m.c))<1e-14
    # Zablokowane położenie: dokładny stacjonarny monopol, Q wciąż oscyluje.
    f=np.arange(801)*1.25;omega=2*np.pi*f;sd=.05
    xr=np.zeros(801,complex);xr[16]=.003*np.exp(.7j);xr[68]=.001*np.exp(-.4j)
    stationary=m.rho*(1j*omega)**2*sd*xr*np.exp(-1j*omega/m.c)/(4*np.pi)
    p0,diag=moving_monopole(xr,f,sd,cfg,position_factor=0.)
    checks['fixed_source_pressure_relative_error']=float(np.linalg.norm(p0-stationary)/np.linalg.norm(stationary))
    assert checks['fixed_source_pressure_relative_error']<5e-8
    # Niezależne rozwinięcie do drugiego rzędu przy x=Acos(wt):
    # p2_peak=C*(-A²w²/r -2j*A²w³/c)*exp(-2j*w*r/c).
    # Wynika z d/dt[v+xv/r+(v²+xa)/c], nie z kodu czasu opóźnionego.
    small=[];convergence=[]
    for amplitude in (1e-4,5e-5,1e-5):
        xr=np.zeros(801,complex);xr[16]=amplitude/np.sqrt(2);w=2*np.pi*20
        p,diag=moving_monopole(xr,f,sd,cfg)
        expected=m.rho*sd/(4*np.pi)*(-amplitude**2*w*w-2j*amplitude**2*w**3/m.c)*np.exp(-2j*w/m.c)/np.sqrt(2)
        error=float(abs(p[32]-expected)/abs(expected));small.append(dict(A_peak_m=amplitude,H2_complex_relative_error=error))
        p4,_=moving_monopole(xr,f,sd,cfg,oversampling=4)
        convergence.append(float(np.linalg.norm(p4-p)/np.linalg.norm(p4)))
        assert error<2e-6
    checks['moving_source_second_order_oracle']=small
    checks['moving_source_oversampling_relative_error']=max(convergence);assert max(convergence)<5e-9
    # Formalne granice: zero i jawnie wyłączona dziedzina dużej prędkości.
    zero,_=moving_monopole(np.zeros(801,complex),f,sd,cfg);assert np.all(zero==0.)
    try:retarded_time(times,lambda tau:(0*tau,np.full_like(tau,m.c*.3)),1.,1.,m.c)
    except ValueError:checks['Mach_domain_rejected']=True
    else:raise AssertionError('Brak kontroli dziedziny Mach')
    # Czysty AM i mały PM: sprawdzenie zespolonych par bocznych.
    case=dict(frequencies_hz=[20,85],phase2_rad=0.)
    p=np.zeros(801,complex);p[16]=.1;p[68]=1.;p[52]=.025;p[84]=.025
    metrics,_=pressure_metrics(p,f,case,dynamic)
    assert abs(metrics['first_sideband_AM_depth']-.05)<1e-14
    assert metrics['first_sideband_PM_index_rad']<1e-14
    p[52]=-.025;p[84]=.025
    metrics,_=pressure_metrics(p,f,case,dynamic)
    assert abs(metrics['first_sideband_PM_index_rad']-.05)<1e-14
    assert metrics['first_sideband_AM_depth']<1e-14
    checks['AM_PM_complex_sidebands']=True
    result=dict(status='ANALYTICAL_ORACLES_PASS_NOT_DEVICE_VALIDATION',checks=checks,
                scope='Wzorce analityczne, mała amplituda, zbieżność dyskretyzacji. Nie potwierdzają realnego THD ani całego ruchomego tłoka.')
    (ROOT/'wyniki/p14b_kontrole_emisji.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False))
    print(json.dumps(result,indent=2,ensure_ascii=False));return result


if __name__=='__main__':main()
