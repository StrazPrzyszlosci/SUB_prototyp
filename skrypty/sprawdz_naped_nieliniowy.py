"""P12/P13: formalna energia, redukcja liniowa, metody niezależne i granice."""
from dataclasses import replace
import json
from pathlib import Path
import numpy as np
import sympy as sy
from scipy.integrate import solve_ivp
from model_subwoofera import Driver
from model_gazu import Medium,ThermalSpectrum,gas_response
from model_nieliniowy import Plant,Shape,NonlinearModel,simulate_sine

ROOT=Path(__file__).resolve().parents[1]


def formal_identities():
    i,v,di,li,lx,wx,bl,re,rm,fs,fg=sy.symbols('i v di Li Lx Wx BL Re Rm Fs Fg',real=True)
    voltage=re*i+li*di+(bl+lx)*v
    balance=(bl*i+wx-fs-rm*v+fg)*v+fs*v+i*li*di+(i*lx-wx)*v-fg*v
    assert sy.expand(balance-(voltage*i-re*i*i-rm*v*v))==0
    # Utrata członu Wx daje błąd -Wx*v w bilansie, nie dodatkową fizyczną stratę.
    assert sy.expand(balance-wx*v-(voltage*i-re*i*i-rm*v*v))==-wx*v
    t,t0,p0,v0,vg,tau,gamma,sd=sy.symbols('T T0 p0 V0 V tau gamma Sd',positive=True)
    cvt0=p0*v0/(gamma-1)
    a=cvt0*(t/t0-1-sy.log(t/t0))+p0*v0*(vg/v0-1-sy.log(vg/v0))
    tdot=-(gamma-1)*t*sd*v/vg-(t-t0)/tau
    derivative=sy.diff(a,t)*tdot+sy.diff(a,vg)*sd*v
    pressure=p0*v0*t/(t0*vg)
    dissipation=cvt0/tau*(t/t0-1)**2/(t/t0)
    assert sy.simplify(derivative+(pressure-p0)*sd*v+dissipation)==0
    q,k0,x0,k1,k2,k4=sy.symbols('q K0 X0 k1 k2 k4',real=True)
    potential=k0*x0*x0*(q*q/2+k1*q**3/3+k2*q**4/4+k4*q**6/6)
    force=k0*x0*q*(1+k1*q+k2*q*q+k4*q**4)
    assert sy.expand(sy.diff(potential,q)/x0-force)==0
    return ['Współenergia: energia motoru z oboma członami sprzężenia',
            'Pominięcie siły reluktancyjnej: dokładny defekt -Frel*v',
            'Dostępność szczelnego gazu: praca i dodatnia strata cieplna',
            'Kms sieczne: całka siły jest energią zawieszenia']


def main():
    identities=formal_identities()
    raw=json.loads((ROOT/'dane/przetworniki/pula_rozszerzona.json').read_text())['drivers']
    d=Driver(**next(x for x in raw if x['candidate_id']=='C02')['model']);plant=Plant.from_driver(d)
    full=Shape(bl_asym=.1,bl_decay=.3,k_asym=.2,k_quad=.4,l_asym=.3,l_quad=.1,saturation_a=8.)
    gradient_error=0.;scalar_vector_error=0.;points=0
    for nonlinear in [False,True]:
        for tau in [0.,.005,np.inf]:
            model=NonlinearModel(plant,100.,full,tau,nonlinear)
            for q,vn,current in [(-.6,.3,4.),(.4,-.7,-3.)]:
                phase=.71;w=2*np.pi*40;peak=20.
                state=np.array([q,vn,current]+([.2] if model.has_temperature else []))
                rhs=model.scalar_rhs(phase,state,w,peak)
                data=model.observables(np.array([phase]),state[:,None],w,peak)
                scalar_vector_error=max(scalar_vector_error,abs(rhs[1]*w*w*plant.xref-float(data['acc'][0])))
                grad=[]
                for j in range(model.size):
                    delta=2e-5;yp=state.copy();ym=state.copy();yp[j]+=delta;ym[j]-=delta
                    ep=model.observables(np.array([phase]),yp[:,None],w,peak)['energy'][0]
                    em=model.observables(np.array([phase]),ym[:,None],w,peak)['energy'][0]
                    grad.append((ep-em)/(2*delta))
                net=float(data['input_power'][0]-data['copper_power'][0]-data['mechanical_loss'][0]-data['thermal_exergy_loss'][0])
                gradient_error=max(gradient_error,abs(np.dot(grad,rhs)*w-net)/max(abs(net),1.))
                points+=1
    assert gradient_error<2e-7 and scalar_vector_error<1e-9,(gradient_error,scalar_vector_error)
    linear=[]
    for le in [0.,d.le_mh]:
        driver=replace(d,le_mh=le)
        for f in [20.,80.]:
            model=NonlinearModel(Plant.from_driver(driver),100.,tau_s=.005,gas_nonlinear=False)
            result=simulate_sine(model,f,2.,rtol=1e-10,atol=1e-12,closure_tolerance=1e-8)
            ref=gas_response(driver,100.,[f],ThermalSpectrum((.005,),(1.,)),vrms=2.,solid_angle=4*np.pi)
            error=abs(result['x_fundamental_peak_m']/ref['x_peak_m'][0]-1)
            assert error<2e-7,error
            linear.append(dict(le_mh=le,f_hz=f,relative_x_error=error,
                               numerical_pressure_thd_pct=result['thd_pressure_h2_h10_pct']))
    model=NonlinearModel(plant,100.,full,tau_s=.005)
    solver_results={method:simulate_sine(model,31.5,20.,method=method,rtol=3e-10,atol=3e-12,
                                       closure_tolerance=1e-8) for method in ['LSODA','Radau','DOP853']}
    base=solver_results['Radau'];differences={}
    for method,r in solver_results.items():
        differences[method]=dict(relative_fundamental_error=abs(r['x_fundamental_peak_m']/base['x_fundamental_peak_m']-1),
                                 absolute_h2_pct_error=abs(r['h2_pressure_pct']-base['h2_pressure_pct']),
                                 absolute_h3_pct_error=abs(r['h3_pressure_pct']-base['h3_pressure_pct']))
        assert differences[method]['relative_fundamental_error']<1e-6
        assert max(differences[method]['absolute_h2_pct_error'],differences[method]['absolute_h3_pct_error'])<2e-4
    high_sampling=simulate_sine(model,31.5,20.,method='Radau',rtol=3e-10,atol=3e-12,samples_per_cycle=1024,closure_tolerance=1e-8)
    sampling=abs(high_sampling['thd_pressure_h2_h10_pct']-base['thd_pressure_h2_h10_pct'])
    assert sampling<2e-4,sampling
    lossless=NonlinearModel(replace(plant,re=0.,resistance=0.),100.,full,tau_s=np.inf)
    init=np.array([.3,0.,1.]);phase=np.linspace(0,20*np.pi,2049);w=2*np.pi*20
    lossless_errors=[]
    for omit in [False,True]:
        sol=solve_ivp(lambda t,y:lossless.scalar_rhs(t,y,w,0.,omit_reluctance=omit),[0.,phase[-1]],init,
                      t_eval=phase,method='DOP853',rtol=3e-11,atol=3e-13,max_step=2*np.pi/128)
        assert sol.success
        energy=lossless.observables(phase,sol.y,w,0.)['energy']
        lossless_errors.append(float(max(abs(energy/energy[0]-1))))
    assert lossless_errors[0]<2e-7 and lossless_errors[1]>1e-4,lossless_errors
    rejected=False
    try:Shape(k_asym=1.,k_quad=.1)
    except ValueError:rejected=True
    assert rejected
    infinite=NonlinearModel(plant,np.inf)
    assert infinite.eta==0 and infinite.gas(np.array([.2]))[0][0]==0
    result=dict(status='PASS_MODELOWEJ_ENERGII_I_REDUKCJI_NIE_WALIDACJA_PRZETWORNIKA',symbolic_identities=identities,
                gradient_points=points,max_relative_energy_gradient_error=gradient_error,
                max_scalar_vector_acceleration_difference=scalar_vector_error,
                linear_reductions=linear,independent_solvers=differences,sampling_thd_absolute_pct_difference=sampling,
                lossless_max_relative_energy_drift=lossless_errors[0],
                omitted_reluctance_max_relative_energy_drift=lossless_errors[1],
                limits=['Le=0','Vb=inf','tau=0/inf','brak strat','odrzucona ujemna sztywność styczna'],
                scope='Kształty hipotetyczne, efektywne Mms/Rms, brak nowej reakcji frontu i bez termiki cewki.')
    (ROOT/'wyniki/p12_p13_weryfikacja.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print(json.dumps(result,ensure_ascii=False,indent=2));return result


if __name__=='__main__':main()
