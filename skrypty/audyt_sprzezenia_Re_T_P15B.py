"""Odrębne twierdzenia, kontrole sieci oraz czasowy wzorzec audio P15B."""
import json
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp,trapezoid
import sympy as sp
from analiza_sprzezenia_Re_T_P15B import make_coupled
from model_gazu import Medium

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def exact_identities():
    R,R0,a,b,V,A,B=sp.symbols('R R0 a b V A B',positive=True)
    den=(R+a)**2+b*b;pcu=V*V*R/den
    target=V*V*(a*a+b*b-R*R)/den**2
    # H/temperature jest malejące przy R=R0(1+alpha*temperature).
    ratio=(A*R+B)/((R-R0)*den)
    derivative=sp.diff(ratio,R)
    negative_form=-(A*R0+B)/((R-R0)**2*den)-(A*R+B)*2*(R+a)/((R-R0)*den**2)
    identities=dict(Pcu_derivative=sp.factor(sp.diff(pcu,R)-target),
                    heat_over_temperature_derivative=sp.factor(derivative-negative_form))
    assert all(x==0 for x in identities.values())
    return dict(identities={k:str(v) for k,v in identities.items()},negative_derivative=str(negative_form),
                domain='R>R0>0,a>=0,b dowolne rzeczywiste,A>0,B>=0. Stałe chłodzenie. Tożsamość znaku nie jest twierdzeniem o pełnym nieliniowym DUT.')


def full_audio_reference(model,seconds,phase=0.):
    """Jawny x,v,i,gaz,j i dwa węzły T; konwekcja kv=0 dla zgodności modeli."""
    if model.forced_g_per_velocity!=0:raise ValueError('Ten wzorzec sprawdza wyłącznie kv=0')
    if model.instant_h<=0:raise ValueError('Jawny stan prądu wymaga Linstant>0')
    p=model.plant;m=Medium();f=model.frequencies;w=2*np.pi*f;count=len(model.branches)
    # Przygotowany zimny stan okresowy oddziela audyt uśredniania od rozruchu.
    amps=model.response(0.);zgas=-(m.gamma-1)*p.sd/(model.volume_l*.001)*amps['velocity']/(1/model.tau_gas_s+1j*w)
    start=np.zeros(6+count)
    start[0]=np.sqrt(2)*sum((amps['velocity']/(1j*w)*np.exp(1j*phase)).real)
    start[1]=np.sqrt(2)*sum((amps['velocity']*np.exp(1j*phase)).real)
    start[2]=np.sqrt(2)*sum((amps['current']*np.exp(1j*phase)).real)
    start[3]=np.sqrt(2)*sum((zgas*np.exp(1j*phase)).real)
    for k,branch in enumerate(model.branches):
        start[4+k]=np.sqrt(2)*sum((amps['current']/(1+1j*w*branch.tau_s)*np.exp(1j*phase)).real)
    def rhs(t,y):
        x,v,i,z=y[:4];j=y[4:4+count];tv,tm=y[-2:]
        jd=np.array([(i-j[k])/branch.tau_s for k,branch in enumerate(model.branches)])
        voltage=np.sqrt(2)*sum(model.voltage_rms*np.cos(w*t+phase))
        re=p.re*(1+model.alpha_per_k*tv)
        idot=(voltage-re*i-p.bl0*v-sum(branch.inductance_h*jd[k] for k,branch in enumerate(model.branches)))/model.instant_h
        acceleration=(p.bl0*i-p.resistance*v-x/p.cms+p.sd*m.p0_pa*(z-p.sd*x/(model.volume_l*.001)))/p.mass
        zdot=-(m.gamma-1)*p.sd/(model.volume_l*.001)*v-z/model.tau_gas_s
        eddy=sum(branch.inductance_h/branch.tau_s*(i-j[k])**2 for k,branch in enumerate(model.branches))
        heat=np.array([re*i*i+model.eta_eddy_to_coil*eddy,(1-model.eta_eddy_to_coil)*eddy])
        td=(heat-model.thermal.conductance@np.array([tv,tm]))/model.thermal.capacities
        return np.r_[v,acceleration,idot,zdot,jd,td]
    atol=np.r_[1e-12,1e-10,1e-10,1e-12,np.full(count,1e-10),1e-10,1e-10]
    fast=solve_ivp(rhs,[0,seconds],start,method='LSODA',rtol=2e-10,atol=atol,dense_output=True,max_step=1/(32*max(f)))
    slow=solve_ivp(lambda t,y:model.rhs(t,y,True),[0,seconds],np.zeros(4),method='DOP853',rtol=2e-11,atol=1e-11,dense_output=True,max_step=.05)
    assert fast.success and slow.success
    base=float(np.gcd.reduce(f.astype(int)));period=1/base
    samples=np.linspace(seconds-period,seconds,4097)
    actual=fast.sol(samples)[-2:]
    averaged=slow.sol(samples)[:2]
    # Średnia obu przebiegów na TYM SAMYM oknie. Różnica punktowa zawiera pulsację2f.
    mean_fast=trapezoid(actual,samples,axis=1)/period;mean_slow=trapezoid(averaged,samples,axis=1)/period
    return dict(full_audio_nfev=fast.nfev,seconds=seconds,phase_rad=phase,
        mean_coil_rise_full_k=float(mean_fast[0]),mean_coil_rise_slow_k=float(mean_slow[0]),
        mean_coil_absolute_error_k=float(abs(mean_fast[0]-mean_slow[0])),
        mean_coil_relative_error=float(abs(mean_fast[0]-mean_slow[0])/max(abs(mean_fast[0]),1e-20)),
        full_coil_ripple_in_last_period_k=float(np.ptp(actual[0]-averaged[0])),
        scope='Liniowy ruch/gaz i pamięć; Re(T) i I²Re dynamiczne. Przygotowany zimny stan audio, kv=0. Nie identyfikuje parametrów produktu ani całej dziedziny uśredniania.')


def main():
    cfg=json.loads((ROOT/'dane/konfiguracje/p15b_sprzezenie_Re_T.json').read_text());memory=json.loads((ROOT/'dane/konfiguracje/p12c_pamiec_cewki.json').read_text())
    pool=json.loads((ROOT/'dane/przetworniki/pula_rozszerzona.json').read_text())['drivers'];entry=next(r for r in pool if r['candidate_id']=='C02')
    identities=exact_identities();checks=[]
    for frequencies in ([20],[40],[80],[20,85]):
        model=make_coupled(entry,frequencies,1.,0.,0.,cfg,memory)
        for rise in (0.,20.,100.):
            r=model.response(rise);h=1e-3
            numerical=(model.response(rise+h)['pcu_w']-model.response(rise-h)['pcu_w'])/(2*h)
            error=abs(numerical-r['pcu_slope_w_k']);assert error<1e-8
            checks.append(dict(frequencies_hz=frequencies,rise_k=rise,Pcu_slope_absolute_error=error))
    full=[]
    for frequencies in ([40],[20,85]):
        for phase in (0.,np.pi/2):
            model=make_coupled(entry,frequencies,1.,0.,0.,cfg,memory)
            result=full_audio_reference(model,5.,phase);result['frequencies_hz']=frequencies
            if result['mean_coil_relative_error']>.02:raise AssertionError('Sprawdzony świadek przekracza2% zakresu kontroli uśredniania')
            full.append(result);print('Pełne audio:',result,flush=True)
    result=dict(status='SYMBOLIC_AND_SELECTED_FULL_AUDIO_CONTROLS',identities=identities,derivative_controls=checks,full_audio=full,
                scope='12kontroli pochodnej i4wybrane pełne czasoweODE,40Hz/20+85Hz,dwie fazy. To kontrola zakresu przybliżenia, nie certyfikat wszystkich2304przebiegów.')
    (OUT/'p15b_audyt_sprzezenia.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print(json.dumps(result,ensure_ascii=False,indent=2));return result


if __name__=='__main__':main()
