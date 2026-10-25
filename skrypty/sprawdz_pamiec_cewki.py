"""P12C: energia dwóch realizacji, macierz stanu i granice pamięci."""
from dataclasses import replace
import json
from pathlib import Path
import numpy as np
import sympy as sy
from scipy.integrate import solve_ivp
from model_subwoofera import Driver
from model_nieliniowy import Plant,Shape,NonlinearModel,simulate_sine
from model_cewki_z_pamiecia import (FluxBranch,MemoryModel,blocked_impedance,
    generalized_inductance,linear_memory_response,simulate_memory_sine)

ROOT=Path(__file__).resolve().parents[1]


def main():
    # Stan j jest współrzędną pamięci strumienia, nie fizycznym prądem w metalu.
    i,j,a,ax,v,l,tau=sy.symbols('i j a ax v L tau',real=True,nonzero=True)
    jd=(a*i-j)/tau;voltage=l*(a*jd+ax*j*v);force=l*ax*i*j
    energy_rate=l*j*jd;loss=l*(a*i-j)**2/tau
    assert sy.expand(i*voltage-force*v-energy_rate-loss)==0
    # KontrolaNAIVE jest też pasywna; to NIE potwierdza właściwego wzoru siły.
    jd2=(i-j)/tau-2*ax/a*j*v
    voltage2=l*a*a/tau*(i-j);force2=l*a*ax*j*j
    energy_rate2=l*a*ax*j*j*v+l*a*a*j*jd2
    loss2=l*a*a/tau*(i-j)**2
    assert sy.expand(i*voltage2-force2*v-energy_rate2-loss2)==0
    raw=json.loads((ROOT/'dane/przetworniki/pula_rozszerzona.json').read_text())['drivers']
    d=Driver(**next(x for x in raw if x['candidate_id']=='C02')['model']);p=Plant.from_driver(d)
    branches=[FluxBranch(.002,.001,.5),FluxBranch(.0007,.0001,-.3)]
    shape=Shape(bl_asym=.1,bl_decay=.3,k_asym=.2,k_quad=.4,l_asym=.2,saturation_a=8.)
    max_gradient=0.;max_acc=0.;points=0
    for realization in ['FLUX','NAIVE']:
        for instant in [0.,.0004]:
            model=MemoryModel(p,100.,instant,branches,shape,realization=realization)
            for q,vn,current in [(-.6,.4,4.),(.3,-.7,-3.)]:
                state=np.zeros(model.size);state[:2]=[q,vn]
                if model.has_current:state[2]=current
                if model.has_temperature:state[model.it]=.2
                state[model.base_size:]=[2.,-1.]
                phase=.7;omega=2*np.pi*40;peak=20.
                dy=model.scalar_rhs(phase,state,omega,peak)
                obs=model.observables(np.array([phase]),state[:,None],omega,peak)
                max_acc=max(max_acc,abs(dy[1]*omega**2*p.xref-float(obs['acc'][0])))
                grad=[]
                for k in range(model.size):
                    delta=2e-5;yp=state.copy();ym=state.copy();yp[k]+=delta;ym[k]-=delta
                    ep=model.observables(np.array([phase]),yp[:,None],omega,peak)['energy'][0]
                    em=model.observables(np.array([phase]),ym[:,None],omega,peak)['energy'][0]
                    grad.append((ep-em)/(2*delta))
                net=float(obs['input_power'][0]-obs['copper_power'][0]-obs['mechanical_loss'][0]-obs['thermal_exergy_loss'][0])
                max_gradient=max(max_gradient,abs(np.dot(grad,dy)*omega-net)/max(abs(net),1.));points+=1
    assert max_gradient<2e-7 and max_acc<1e-8,(max_gradient,max_acc)
    # Niezależny układ macierzowy stanu, nie przepisywanie Z(s).
    frequency=np.array([10.,20.,100.,1000.,5000.]);transfer_error=0.;eigen_max=-np.inf;cases=0
    for cid in ['C02','C06','C10','C18']:
        plant=Plant.from_driver(Driver(**next(x for x in raw if x['candidate_id']==cid)['model']))
        for volume in [30.,100.]:
            for instant,bs in [(plant.le0,[]),(.0003,[FluxBranch(.001,.001)]),
                               (.0003,[FluxBranch(.001,.001),FluxBranch(.0004,.0001)]),
                               (0.,[FluxBranch(.001,.001)])]:
                model=MemoryModel(plant,volume,instant,bs,gas_nonlinear=False)
                zero=np.zeros(model.size)
                matrix=np.column_stack([model.scalar_rhs(0.,u,1.,0.) for u in np.eye(model.size)])
                drive=model.scalar_rhs(np.pi/2,zero,1.,1.)
                eigen_max=max(eigen_max,float(np.max(np.linalg.eigvals(matrix).real)))
                reference=linear_memory_response(plant,volume,frequency,instant,bs)
                for k,f in enumerate(frequency):
                    z=np.linalg.solve(2j*np.pi*f*np.eye(model.size)-matrix,drive)
                    x=plant.xref*z[0]
                    v=plant.xref*z[1]
                    current=z[2] if model.has_current else (1-plant.bl0*v+sum(b.inductance_h*z[model.base_size+j]/b.tau_s for j,b in enumerate(bs)))/(plant.re+sum(b.inductance_h/b.tau_s for b in bs))
                    transfer_error=max(transfer_error,abs(x/(reference['velocity'][k]/(2j*np.pi*f))-1),abs(current/reference['current'][k]-1));cases+=1
    assert transfer_error<1e-10 and eigen_max<0,(transfer_error,eigen_max)
    # Odrębna realizacja sprzężonych induktorów o dodatniej macierzy energii.
    mutual_energy_error=mutual_force_error=0.
    for q in [-1.,-.2,.7]:
        for current,mem in [(3.,np.array([1.,-2.])),(-4.,np.array([2.,.5]))]:
            lj=np.array([b.inductance_h*np.exp(b.slope*q+b.curvature*q*q) for b in branches])
            derivative=np.array([b.slope+2*b.curvature*q for b in branches])/p.xref
            g=np.sqrt(lj);r=np.sqrt([b.inductance_h for b in branches])*mem
            secondary=r-g*current  # Umowna jednostkowa indukcyjność wtórna.
            lprimary=.0004+sum(lj)
            energy=.5*lprimary*current**2+sum(g*current*secondary+.5*secondary**2)
            canonical=.5*.0004*current**2+.5*sum(r*r)
            force=.5*sum(lj*derivative)*current**2+sum(.5*g*derivative*current*secondary)
            reference_force=sum(.5*g*derivative*current*r)
            mutual_energy_error=max(mutual_energy_error,abs(energy-canonical))
            mutual_force_error=max(mutual_force_error,abs(force-reference_force))
    assert mutual_energy_error<1e-12 and mutual_force_error<1e-12
    # Redukcja N=0 do wcześniejszego modelu, bez zmiany starego kodu/wejść.
    old=simulate_sine(NonlinearModel(p,100.,shape,tau_s=.005),20.,10.)
    new=simulate_memory_sine(MemoryModel(p,100.,p.le0,[],shape),20.,10.)
    reduction=abs(new['x_fundamental_peak_m']/old['x_fundamental_peak_m']-1)
    assert reduction<1e-10
    f=np.geomspace(.01,1e6,400);z=blocked_impedance(f,p.re,.0003,branches)
    assert np.min(z.real)>=p.re
    frozen=generalized_inductance([1.,100.],.0003,[FluxBranch(.002,np.inf)])
    assert np.max(abs(frozen-.0003))==0
    tiny=generalized_inductance([1.,1000.],.0003,[FluxBranch(.002,1e-12)])
    tiny_error=float(max(abs(tiny/.0023-1)))
    assert tiny_error<1e-8
    high=generalized_inductance([1e12],.0003,branches)
    high_error=float(abs(high[0]/.0003-1));assert high_error<1e-7
    dc=generalized_inductance([0.],.0003,branches)[0]
    assert abs(dc-(.0003+sum(b.inductance_h for b in branches)))<1e-15
    lossless=MemoryModel(replace(p,re=0.,resistance=0.),100.,.0003,
                         [FluxBranch(.002,np.inf,.4)],Shape(k_quad=.4),tau_s=np.inf)
    init=np.array([.2,0.,1.,2.]);times=np.linspace(0,20*np.pi,2049);omega=2*np.pi*20
    sol=solve_ivp(lambda t,y:lossless.scalar_rhs(t,y,omega,0.),[0,times[-1]],init,
                  t_eval=times,method='DOP853',rtol=3e-11,atol=3e-13,max_step=2*np.pi/128)
    assert sol.success
    energy=lossless.observables(times,sol.y,omega,0.)['energy']
    frozen_energy_drift=float(max(abs(energy/energy[0]-1)));assert frozen_energy_drift<1e-7
    assert max(abs(sol.y[-1]-init[-1]))==0
    result=dict(status='PASS_ENERGII_STANU_I_GRANIC_NIE_WALIDACJA_PRODUKTU',
                symbolic_identities=['FLUX: moc/energia i dodatnia strata','NAIVE: pasywność mimo innej siły'],
                gradient_points=points,max_energy_gradient_relative_error=max_gradient,
                max_scalar_vector_acceleration_error=max_acc,state_frequency_cases=cases,
                max_state_vs_frequency_relative_error=float(transfer_error),max_linear_eigenvalue_real=eigen_max,
                mutual_energy_absolute_error=mutual_energy_error,mutual_force_absolute_error=mutual_force_error,
                no_memory_reduction_relative_error=reduction,
                tau_to_zero_frequency_error=tiny_error,formal_high_frequency_error=high_error,
                nonzero_frozen_memory_lossless_energy_drift=frozen_energy_drift,
                limits=['N=0','Linstant=0 z redukcją algebraiczną','tau->0','f=0,finfinity formalnie',
                        'tau->inf z zerową i niezerową pamięcią wejściową','Re(Zblocked)>=Re'],
                scope='Współrzędne pamięci są pomocnicze. Pasywność nie identyfikuje fizycznej siły ani dowolnej realizacji głośnika.')
    (ROOT/'wyniki/p12c_weryfikacja.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print(json.dumps(result,ensure_ascii=False,indent=2));return result


if __name__=='__main__':main()
