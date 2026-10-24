"""P11/P26: ściany wzorcowe i zwrotne obciążenie przez modalny pokój.

Geometrie odgrody i pełny model pokoju są osobnymi eksperymentami; ich
odpowiedzi nie są dodawane jako dwa niezależne zyski room gain.
"""
import json
from pathlib import Path
import numpy as np
from model_subwoofera import Driver,P_REF
from model_gazu import Medium,ThermalSpectrum
from model_pokoju import ModalRoom
from model_promieniowania import gaussian_free_impedance
from odgroda_i_obrazy import image_radiation_matrix,image_pressure_operator
from naped_z_promieniowaniem import reference_calibration,solve_motor_ports,common_drive_envelope
from analiza_promieniowania import table,save
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def pressure_db(value):return 20*np.log10(np.maximum(abs(value),1e-300)/P_REF)


def room_case(d,vb,f,port_h,observer_h,sigma,medium):
    motor,_=reference_calibration(d,1.,'GAUSSIAN',sigma,medium)
    n=port_h.shape[1];s=2j*np.pi*f
    rear=d.sd*d.sd*ThermalSpectrum((.005,),(1.,)).bulk_modulus(f,medium)/(s*vb*.001)
    free=gaussian_free_impedance(f,d.sd,sigma,medium)
    zfree=free[:,None,None]*np.eye(n)[None,:,:]
    zroom=port_h*d.sd*d.sd
    out=solve_motor_ports(f,[motor]*n,rear[:,None],zroom,np.ones(n))
    one_way=solve_motor_ports(f,[motor]*n,rear[:,None],zfree,np.ones(n))
    operator=observer_h*d.sd
    pressure=np.einsum('frj,fj->fr',operator,out['velocity'])
    p0=np.einsum('frj,fj->fr',operator,one_way['velocity'])
    ze=motor.re_ohm+s*motor.le_h
    diagonal=motor.resistance_n_s_m+s*motor.mass_kg+1/(s*motor.compliance_m_n)+rear+free+motor.bl_tm**2/ze
    eps=np.linalg.norm((zroom-zfree)/diagonal[:,None,None],ord=2,axis=(1,2))
    bounds=[(float(value),float(value/(1-value)) if value<1 else None) for value in eps]
    return motor,out,one_way,pressure,p0,bounds


def main():
    cfg=json.loads((ROOT/'dane/konfiguracje/p11_promieniowanie.json').read_text())
    positions_cfg=json.loads((ROOT/'dane/konfiguracje/p26_scenariusze.json').read_text())
    room_cfg=json.loads((ROOT/'dane/konfiguracje/pokoj_odsluchowy.json').read_text())
    raw=json.loads((ROOT/'dane/przetworniki/pula_rozszerzona.json').read_text())['drivers']
    f=np.array(cfg['frequencies_hz']);s=2j*np.pi*f;medium=Medium()
    wall_rows=[];max_energy=0.
    for entry in raw:
        d=Driver(**entry['model']);motor,_=reference_calibration(d,1.,medium=medium)
        positions=cfg['baffle_positions_xz_m'];observer=[cfg['baffle_observer_xyz_m']]
        print('P11 ściany i wzajemne promieniowanie:',entry['candidate_id'],flush=True)
        for walls in cfg['wall_cases']:
            rad=image_radiation_matrix(f,[d.sd,d.sd],positions,walls,medium)
            transfer=image_pressure_operator(f,[d.sd,d.sd],positions,observer,walls,medium)
            for vb in cfg['volumes_l']:
                for profile in cfg['profiles']:
                    spectrum=ThermalSpectrum((np.inf if profile=='ADIABATIC' else .005,),(1.,))
                    rear=d.sd**2*spectrum.bulk_modulus(f,medium)/(s*vb*.001)
                    for n in [1,2]:
                        out=solve_motor_ports(f,[motor]*n,rear[:,None],rad[:,:n,:n],np.ones(n))
                        isolated_rad=rad[:,:n,:n]*np.eye(n)[None,:,:]
                        isolated=solve_motor_ports(f,[motor]*n,rear[:,None],isolated_rad,np.ones(n))
                        p=np.einsum('frj,fj->fr',transfer[:,:,:n],out['velocity'])[:,0]
                        p0=np.einsum('frj,fj->fr',transfer[:,:,:n],isolated['velocity'])[:,0]
                        max_energy=max(max_energy,float(max(abs(out['energy_residual_w'])/out['input_w'])))
                        for j,frequency in enumerate(f):
                            row=dict(candidate_id=entry['candidate_id'],volume_l=vb,profile=profile,
                                     walls='+'.join(walls) or 'BAFFLE_ONLY',source_count=n,f_hz=frequency,
                                     spl_S0_1v_per_amp_rms_db=float(pressure_db(p[j])),
                                     delta_from_ignoring_mutual_db=float(20*np.log10(abs(p[j]/p0[j]))),
                                     radiated_power_1v_per_amp_w=float(out['radiation_w'][j]),
                                     input_power_1v_per_amp_w=float(out['input_w'][j]),
                                     max_current_per_amp_1v_rms_a=float(max(abs(out['current'][j]))),
                                     max_x_peak_1v_mm=float(max(out['x_peak_m'][j])*1000),
                                     min_input_power_per_amp_1v_w=float(min(out['input_per_port_w'][j])),
                                     radiation_min_hermitian_eigenvalue=float(np.linalg.eigvalsh((rad[j,:n,:n]+rad[j,:n,:n].conj().T)/2).min()),
                                     scope='ODGRODA_I_PROSTOPADLE_SCIANY_NIE_CALY_POKOJ')
                            for vmax,imax in cfg['amplifier_scenarios']:
                                for fraction in cfg['x_fractions']:
                                    scale,limit=common_drive_envelope(out,[motor]*n,vmax,imax,fraction)
                                    prefix=f'V{vmax:g}_X{fraction:g}'
                                    row[prefix+'_spl_S0_rms_db']=float(pressure_db(p[j]*scale[j]))
                                    row[prefix+'_voltage_per_amp_rms']=float(scale[j])
                                    row[prefix+'_limit']=['voltage','current','catalog_x'][int(limit[j])]
                            wall_rows.append(row)
    table('p11_sciany_i_wzajemne.csv',wall_rows)
    # Operator pokoju jest wspólny dla różnych głośników. Siły odbierają
    # tę samą aperturę co źródło, więc część hermitowska pozostaje >=0.
    room=ModalRoom((room_cfg['width_x_m'],room_cfg['length_y_m'],room_cfg['height_z_m']),medium.c,medium.rho)
    listener=np.array(positions_cfg['assumed_listener_xyz_m'])
    receivers=listener+np.array(positions_cfg['diagnostic_neighbor_offsets_xyz_m'])
    room_rows=[];max_eps=max_velocity_error=0.;max_pressure_delta=0.;all_bounds_valid=True
    sigma=cfg['room_source_sigma_m']
    sigma_records=[]
    for setup in positions_cfg['source_sets']:
        pos=setup['positions_xyz_m']
        for t60 in positions_cfg['modal_t60_s']:
            for tau0 in positions_cfg['zero_relaxation_s']:
                print('P11 zwrotne obciążenie pokoju:',setup['id'],t60,tau0,flush=True)
                port=room.transfer(f,pos,pos,t60,tau0,sigma,sigma,cfg['room_kmax_m_inv'])
                observer=room.transfer(f,pos,receivers,t60,tau0,sigma,cfg['room_receiver_sigma_m'],cfg['room_kmax_m_inv'])
                for entry in raw:
                    d=Driver(**entry['model'])
                    for vb in cfg['volumes_l']:
                        for n in [1,2]:
                            motor,out,oneway,p,p0,bounds=room_case(d,vb,f,port[:,:n,:n],observer[:,:,:n],sigma,medium)
                            energy=abs(out['energy_residual_w'])/np.maximum(out['input_w'],1e-300)
                            max_energy=max(max_energy,float(max(energy)))
                            velocity_error=np.linalg.norm(out['velocity']-oneway['velocity'],axis=1)/np.linalg.norm(oneway['velocity'],axis=1)
                            max_velocity_error=max(max_velocity_error,float(max(velocity_error)))
                            for j,frequency in enumerate(f):
                                epsilon,bound=bounds[j];max_eps=max(max_eps,epsilon)
                                if bound is None:all_bounds_valid=False
                                else:assert velocity_error[j]<=bound*(1+1e-10)
                                delta=float(20*np.log10(abs(p[j,0]/p0[j,0])))
                                max_pressure_delta=max(max_pressure_delta,abs(delta))
                                row=dict(candidate_id=entry['candidate_id'],volume_l=vb,source_set=setup['id'],
                                         modal_t60_s=t60,zero_tau_s=tau0,source_count=n,f_hz=frequency,
                                         sigma_m=sigma,spl_coupled_S0_1v_per_amp_db=float(pressure_db(p[j,0])),
                                         spl_oneway_S0_1v_per_amp_db=float(pressure_db(p0[j,0])),
                                         delta_pressure_from_oneway_db=delta,
                                         relative_velocity_2norm_change=float(velocity_error[j]),
                                         perturbation_norm=epsilon,neumann_velocity_relative_bound=bound,
                                         room_dissipation_1v_w=float(out['radiation_w'][j]),
                                         input_power_1v_w=float(out['input_w'][j]),
                                         max_current_per_amp_1v_rms_a=float(max(abs(out['current'][j]))),
                                         max_x_peak_1v_mm=float(max(out['x_peak_m'][j])*1000),
                                         min_input_power_per_amp_1v_w=float(min(out['input_per_port_w'][j])),
                                         max_neighbor_pressure_change_due_feedback_db=float(max(abs(20*np.log10(abs(p[j]/p0[j]))))),
                                         scope='FENOMENOLOGICZNY_PORT_GAUSSA_NIE_MMD_ANI_BRYLA_CNC')
                                for vmax,imax in cfg['amplifier_scenarios']:
                                    for fraction in cfg['x_fractions']:
                                        scale,limit=common_drive_envelope(out,[motor]*n,vmax,imax,fraction)
                                        prefix=f'V{vmax:g}_X{fraction:g}'
                                        row[prefix+'_spl_S0_rms_db']=float(pressure_db(p[j,0]*scale[j]))
                                        row[prefix+'_voltage_per_amp_rms']=float(scale[j])
                                        row[prefix+'_limit']=['voltage','current','catalog_x'][int(limit[j])]
                                room_rows.append(row)
    table('p11_pokoj_sprzezenie_zwrotne.csv',room_rows)
    setup=positions_cfg['source_sets'][0];pos=setup['positions_xyz_m']
    for a in cfg['room_feedback_sigma_sensitivity_m']:
        port=room.transfer(f,pos,pos,.4,.2,a,a,cfg['room_sigma_sensitivity_kmax_m_inv'])
        observer=room.transfer(f,pos,[listener],.4,.2,a,cfg['room_receiver_sigma_m'],cfg['room_sigma_sensitivity_kmax_m_inv'])
        for entry in raw:
            d=Driver(**entry['model']);_,out,ow,p,p0,_=room_case(d,100.,f,port,observer,a,medium)
            for j,frequency in enumerate(f):
                sigma_records.append(dict(candidate_id=entry['candidate_id'],sigma_m=a,f_hz=frequency,
                                          spl_S0_rms_1v_per_amp_db=float(pressure_db(p[j,0])),
                                          feedback_delta_db=float(20*np.log10(abs(p[j,0]/p0[j,0]))),
                                          scope='WRAZLIWOSC_NA_APERTURE_MODELOWA_NIE_TOLERANCJA_MEMBRANY'))
    table('p11_pokoj_apertura_wrazliwosc.csv',sigma_records)
    # Obserwowana zmiana ciśnienia i ograniczenie normowe nie są tym samym.
    fig,axes=plt.subplots(1,2,figsize=(12,5))
    for cid in ['C02','C06','C11']:
        sub=[r for r in room_rows if r['candidate_id']==cid and r['volume_l']==100 and r['source_set']=='A'
             and r['modal_t60_s']==.4 and r['zero_tau_s']==.2 and r['source_count']==2]
        axes[0].plot([r['f_hz'] for r in sub],[r['delta_pressure_from_oneway_db'] for r in sub],'o-',label=cid)
        axes[1].plot([r['f_hz'] for r in sub],[100*r['relative_velocity_2norm_change'] for r in sub],'o-',label=cid)
    axes[0].set(xlabel='Hz',ylabel='Zmiana SPL od reakcji pokoju [dB]',title='Scenariusz A: dwa źródła, 100 l, T60=0,4s/τ0=0,2s')
    axes[1].set(xlabel='Hz',ylabel='Zmiana normy prędkości [%]',title='Względem źródła bez reakcji pokoju')
    for ax in axes:ax.grid(alpha=.25);ax.legend()
    save(fig,'19_reakcja_pokoju_na_naped')
    fig,axes=plt.subplots(1,2,figsize=(12,5))
    for walls in ['BAFFLE_ONLY','FLOOR','FLOOR+LEFT']:
        for n in [1,2]:
            sub=[r for r in wall_rows if r['candidate_id']=='C02' and r['volume_l']==100 and r['profile']=='ADIABATIC' and r['walls']==walls and r['source_count']==n]
            axes[0].plot([r['f_hz'] for r in sub],[r['spl_S0_1v_per_amp_rms_db'] for r in sub],label=f'{walls}, liczba={n}')
    axes[0].set(xlabel='Hz',ylabel='Modelowe SPL S0 [dB], 1Vrms/amp',title='Idealna odgroda i ściany prostopadłe, C02')
    for cid in ['C02','C06','C11']:
        sub=[r for r in sigma_records if r['candidate_id']==cid and r['f_hz']==20]
        axes[1].plot([r['sigma_m'] for r in sub],[r['feedback_delta_db'] for r in sub],'o-',label=cid)
    axes[1].set(xlabel='sigma źródła i portu siłowego [m]',ylabel='Reakcja pokoju przy20Hz [dB]',title='Nieznana geometria apertury: osobna analiza modelu')
    for ax in axes:ax.grid(alpha=.25);ax.legend(fontsize=7)
    save(fig,'20_sciany_i_apertura')
    result=dict(status='ZWROTNE_SPRZEZENIE_MODELOWE_NIE_IDENTYFIKACJA_POKOJU',wall_rows=len(wall_rows),room_rows=len(room_rows),
                sigma_sensitivity_rows=len(sigma_records),max_relative_energy_residual=max_energy,
                max_perturbation_norm=max_eps,all_sampled_neumann_bounds_available=all_bounds_valid,
                max_relative_velocity_change=max_velocity_error,max_abs_S0_pressure_feedback_db=max_pressure_delta,
                room_dimensions_xyz_m=list(room.dimensions_xyz_m),room_volume_m3=room.volume_m3,
                caveats=['Pozycje i straty są scenariuszami U-017, nie pomiarem.',
                         'Porty Gaussa mają efektywne masy, nie niezależnie zmierzone Mmd.',
                         'Odgroda/obrazy i pełny model modalny są odrębnymi geometriami.',
                         'Ograniczenie Neumanna jest sprawdzone w punktach częstotliwości, nie certyfikatem całego ciągłego pasma.',
                         'Zmiana ciśnienia przy dołku może być większa niż zmiana prędkości; należy czytać obie wielkości.'])
    (OUT/'p11_sprzezenia_podsumowanie.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps(result,ensure_ascii=False,indent=2));return result


if __name__=='__main__':main()
