"""P15A: równoważność portu, rozróżnienie stanów i granice sprzężenia I²Re."""
import csv
import hashlib
import json
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/sub-krystian-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp
from model_termiczny_P15 import ThermalCauer,indistinguishable_cooling_family

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def main():
    path=ROOT/'dane/konfiguracje/p15a_topologia_termiczna.json';cfg=json.loads(path.read_text())
    example=ThermalCauer(**cfg['control']);foster=example.foster_port()
    times=np.linspace(0,15,301);physical=example.step(times,[cfg['control_heat_w'],0.]);fit=foster.step(times,cfg['control_heat_w'])
    ode=solve_ivp(lambda t,y:example.state_matrix@y+np.array([1.,0.])/example.capacities,[0,15],[0.,0.],t_eval=times,method='DOP853',rtol=2e-13,atol=1e-14,max_step=.2)
    assert ode.success
    control_error=float(np.max(abs(physical[:,0]-fit)));ode_error=float(np.max(abs(physical-ode.y.T)))
    assert control_error<2e-13 and ode_error<2e-11
    fgrid=np.r_[0.,np.logspace(-4,4,81)];s=2j*np.pi*fgrid
    rr=np.logspace(*cfg['resistance_ratio_log10_range'],cfg['grid_size']);cr=np.logspace(*cfg['capacity_ratio_log10_range'],cfg['grid_size'])
    rows=[];max_frequency_error=0.;max_steady_error=0.
    for r in rr:
        for c in cr:
            model=ThermalCauer(1.,float(c),1.,float(r));port=model.foster_port()
            exact=model.impedance(s);other=port.impedance(s)
            error=float(max(abs(exact-other)/np.maximum(abs(exact),1e-30)));max_frequency_error=max(max_frequency_error,error)
            steady=model.steady([1.,0.]);max_steady_error=max(max_steady_error,abs(steady[0]-(1+r))/max(1+r,1.))
            taus=np.array(port.time_constants_s);naive=np.sort([1.,r*c]);actual=np.sort(taus)
            rows.append(dict(Rma_to_Rvm=float(r),Cm_to_Cv=float(c),port_relative_error=error,
                tau_fast_over_RvmCv=float(actual[0]),tau_slow_over_RvmCv=float(actual[1]),
                max_relative_error_if_individual_R_C_assigned_to_Cauer_poles=float(max(abs(naive-actual)/actual)),
                pole_sum_identity_error=float(abs(sum(taus)-(c*r+1+r))/max(c*r+1+r,1.)),
                pole_product_identity_error=float(abs(np.prod(taus)-c*r)/max(c*r,1e-30))))
    # Tożsamości biernego portu; szeroki stres uwarunkowania, nie tolerancje produktów.
    assert max_frequency_error<2e-7
    assert max_steady_error<1e-9
    assert max(r['pole_sum_identity_error'] for r in rows)<2e-7
    assert max(r['pole_product_identity_error'] for r in rows)<2e-7
    # Sieć izolowana: brak stanu ustalonego, ale suma C*T rośnie dokładnie Pt.
    insulated=ThermalCauer(2.,3.,np.inf,np.inf,np.inf);ins=insulated.step([0.,1.,10.],[4.,2.])
    assert max(abs(ins@insulated.capacities-np.array([0.,1.,10.])*6))<1e-12
    # Idealnie trzymany prąd: próg k=P0*alpha=1/Rth, sprawdzenie spektrum.
    feedback=[];rth=example.steady([1.,0.])[0]
    for normalized in (.0,.1,.9,.999,1.,1.001,1.1,2.):
        result=example.current_heating_stability(float(normalized/rth),1.)
        result['normalized_feedback']=normalized;feedback.append(result)
        decay=result['smallest_decay_per_s']
        if normalized<1:assert decay>0
        elif normalized>1:assert decay<0
        else:assert abs(decay)<1e-14
    # Bezpośrednia konwekcja: osobne dodatnie sieci, nie parametr dopasowany.
    direct=[]
    for value in cfg['direct_cooling_ratio_controls']:
        model=ThermalCauer(1.,1.,1.,1.,value);port=model.foster_port()
        error=float(max(abs(model.impedance(s)-port.impedance(s))/abs(model.impedance(s))))
        assert error<1e-12
        assert abs(model.steady([1.,0.])[0]-1/(1/value+.5))<1e-12
        direct.append(dict(Rva_k_w=value,Rth_port_k_w=float(model.steady([1.,0.])[0]),port_relative_error=error))
    # Przy dodatkowej ścieżce chłodzenia nawet wybrana klasa Cauer ma swobodę.
    # To jawne świadki ciągłej rodziny wyprowadzonej algebraicznie, nie sam fit.
    ambiguous=[];reference=ThermalCauer(1.,1.,1.,1.,1.).impedance(s)
    for b in (.6,.75,1.,1.5,1.9):
        model=indistinguishable_cooling_family(1.,2.,2.,1.,b)
        error=float(max(abs(model.impedance(s)-reference)/abs(reference)));assert error<1e-12
        equilibrium=model.steady([1.,0.]);magnet_heat=model.steady([0.,1.])
        ambiguous.append(dict(gvm_w_k=b,Cm_j_k=model.magnet_capacity_j_k,Rvm_k_w=model.coil_to_magnet_k_w,
            Rma_k_w=model.magnet_to_air_k_w,Rva_k_w=model.coil_to_air_k_w,port_relative_error=error,
            steady_coil_k=equilibrium[0],steady_magnet_k=equilibrium[1],coil_rise_for_1w_at_magnet_k=magnet_heat[0]))
    with (OUT/'p15a_sieci_termiczne.csv').open('w',newline='') as handle:
        w=csv.DictWriter(handle,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    # Wymagania chłodzenia wynikające z P14 przy zamrożonej mocy, nie prognoza T.
    witness=np.load(OUT/'p14b_swiadkowie_emisji.npz',allow_pickle=False);requirements=[]
    for text in witness['row_json']:
        row=json.loads(str(text));power=row['mean_copper_w']
        for rise in cfg['allowed_temperature_rise_scenarios_k']:
            requirements.append(dict(case_id=row['case_id'],candidate_id=row['candidate_id'],profile=row['profile'],
                frozen_copper_w=power,allowed_rise_scenario_k=rise,maximum_steady_coil_port_Rth_k_w=rise/power,
                scope='STALE_PCU_BEZ_SPRZEZENIA_Re_T_I_BEZ_PRZYPISANIA_EDDY_DO_WEZLOW_NIE_TEMPERATURA_PRODUKTU'))
    with (OUT/'p15a_wymagania_Rth.csv').open('w',newline='') as handle:
        w=csv.DictWriter(handle,fieldnames=list(requirements[0]));w.writeheader();w.writerows(requirements)
    fig,axes=plt.subplots(1,2,figsize=(12,4.8))
    axes[0].plot(times,physical[:,0],label='Cauer: cewka');axes[0].plot(times,fit,'--',label='Foster: ten sam port')
    axes[0].set(xlabel='Czas [s]',ylabel='Przyrost temperatury [K]',title='Umowna sieć: P = 1 W; R: 1 K/W; C: 1 J/K')
    axes[1].plot(times,physical[:,1],label='Cauer: węzeł magnesu')
    axes[1].plot(times,foster.step_states(times,1.)[:,0],'--',label='Foster: wolny stan zastępczy')
    axes[1].set(xlabel='Czas [s]',ylabel='Stan termiczny [K]',title='Zgodny port nie oznacza zgodnych wnętrz')
    for ax in axes:ax.grid(alpha=.25);ax.legend(fontsize=8)
    fig.tight_layout()
    for ext in ('png','svg'):fig.savefig(OUT/f'34_P15A_Cauer_Foster.{ext}',dpi=170)
    plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(12,4.8))
    matrix=np.array([r['max_relative_error_if_individual_R_C_assigned_to_Cauer_poles'] for r in rows]).reshape(len(rr),len(cr))
    image=axes[0].pcolormesh(np.log10(cr),np.log10(rr),np.log10(np.maximum(matrix,1e-8)),shading='auto');fig.colorbar(image,ax=axes[0],label='log10(względnego błędu stałej czasowej)')
    axes[0].set(xlabel='log10(Cm/Cv)',ylabel='log10(Rma/Rvm)',title='Przeniesienie wzorów Foster do Cauer bez transformacji')
    axes[1].plot([r['normalized_feedback'] for r in feedback],[r['smallest_decay_per_s'] for r in feedback],'o-')
    axes[1].axhline(0,color='k',lw=.8);axes[1].axvline(1,color='r',ls='--');axes[1].grid(alpha=.25)
    axes[1].set(xlabel='P0 * alpha * Rth [bezwymiarowe]',ylabel='Najmniejsze tempo zaniku [1/s]',title='Idealne źródło prądu: warunkowy próg stabilności')
    fig.tight_layout()
    for ext in ('png','svg'):fig.savefig(OUT/f'35_P15A_topologia_i_sprzezenie.{ext}',dpi=170)
    plt.close(fig)
    result=dict(status='P15A_KONTROLE_TOPOLOGII_NIE_ZAMKNIETY_MODEL_CIEPLNY',network_cases=len(rows),
        max_complex_port_relative_error=max_frequency_error,max_steady_relative_error=max_steady_error,
        max_step_port_error_k=control_error,independent_ODE_max_error_k=ode_error,
        control_Cauer_steady_k=example.steady([1.,0.]).tolist(),Foster_R_k_w=list(foster.resistances_k_w),
        Foster_tau_s=list(foster.time_constants_s),Foster_equivalent_C_j_k=foster.equivalent_capacities_j_k.tolist(),
        Foster_steady_internal_k=foster.step_states([1e6],1.)[0].tolist(),current_feedback=feedback,direct_cooling=direct,
        indistinguishable_Cauer_with_direct_cooling=ambiguous,
        conditional_Rth_requirements=len(requirements),
        input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,Path(__file__),ROOT/'skrypty/model_termiczny_P15.py',OUT/'p14b_swiadkowie_emisji.npz']},
        scope='Dodatnie sieci kontrolne, nie zidentyfikowane C/R24produktów. Progi Rth wynikają z narzuconych przyrostów i zamrożonego Pcu. Próg prądowy nie dotyczy automatycznie rzeczywistego wzmacniacza.')
    (OUT/'p15a_topologia_podsumowanie.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False))
    print(json.dumps(result,indent=2,ensure_ascii=False));return result


if __name__=='__main__':main()
