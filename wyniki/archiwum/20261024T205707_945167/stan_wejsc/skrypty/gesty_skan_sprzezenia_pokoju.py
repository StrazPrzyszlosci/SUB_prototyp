"""P11: gęsty skan reakcji wszystkich24modeli przy modach pokoju."""
import json
from pathlib import Path
import numpy as np
from model_subwoofera import Driver
from model_gazu import Medium
from model_pokoju import ModalRoom
from analiza_scian_i_sprzezen import room_case,pressure_db
from analiza_promieniowania import table,save
from naped_z_promieniowaniem import common_drive_envelope
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def case_metrics(f,motor,out,oneway,p,p0,bounds):
    eps=np.array([x[0] for x in bounds])
    velocity=np.linalg.norm(out['velocity']-oneway['velocity'],axis=1)/np.linalg.norm(oneway['velocity'],axis=1)
    bound=np.array([x[1] if x[1] is not None else np.inf for x in bounds])
    assert np.all(velocity<=bound*(1+1e-10))
    delta=20*np.log10(abs(p[:,0]/p0[:,0]))
    ie=int(np.argmax(eps));iv=int(np.argmax(velocity));ip=int(np.argmax(abs(delta)))
    scale,_=common_drive_envelope(out,[motor]*out['velocity'].shape[1],40.,12.,1.)
    scale0,_=common_drive_envelope(oneway,[motor]*out['velocity'].shape[1],40.,12.,1.)
    capacity=20*np.log10(abs(p[:,0]*scale/(p0[:,0]*scale0)))
    minimum_pressure=np.min(abs(p0[:,0]))/np.max(abs(p0[:,0]))
    return dict(max_perturbation_norm=float(eps[ie]),f_max_perturbation_hz=float(f[ie]),
                max_relative_velocity_change=float(velocity[iv]),f_max_velocity_change_hz=float(f[iv]),
                max_abs_pressure_feedback_db=float(abs(delta[ip])),f_max_pressure_feedback_hz=float(f[ip]),
                min_pressure_feedback_db=float(min(delta)),max_pressure_feedback_db=float(max(delta)),
                max_abs_available40v12a1X_change_db=float(max(abs(capacity))),
                reference_pressure_min_over_max=float(minimum_pressure),
                all_sampled_neumann_bounds_available=bool(np.all(eps<1)),
                max_relative_energy_residual=float(max(abs(out['energy_residual_w'])/np.maximum(out['input_w'],1e-300))))


def main():
    cfg=json.loads((ROOT/'dane/konfiguracje/p11_promieniowanie.json').read_text())
    p26=json.loads((ROOT/'dane/konfiguracje/p26_scenariusze.json').read_text())
    geo=json.loads((ROOT/'dane/konfiguracje/pokoj_odsluchowy.json').read_text())
    raw=json.loads((ROOT/'dane/przetworniki/pula_rozszerzona.json').read_text())['drivers']
    drivers={r['candidate_id']:Driver(**r['model']) for r in raw}
    medium=Medium();room=ModalRoom((geo['width_x_m'],geo['length_y_m'],geo['height_z_m']),medium.c,medium.rho)
    lower,upper,step=cfg['room_dense_grid_hz'];f=np.arange(lower,upper+step/2,step)
    sigma=cfg['room_source_sigma_m'];receiver=np.array(p26['assumed_listener_xyz_m'])
    prefactor=medium.rho*medium.c**2/room.volume_m3;s=2j*np.pi*f
    rows=[];curves=[]
    for setup in p26['source_sets']:
        pos=setup['positions_xyz_m']
        for t60 in p26['modal_t60_s']:
            print('P11 gęsta siatka:',setup['id'],'modalneT60=',t60,flush=True)
            port_base=room.transfer(f,pos,pos,t60,.2,sigma,sigma,cfg['room_kmax_m_inv'])
            obs_base=room.transfer(f,pos,[receiver],t60,.2,sigma,cfg['room_receiver_sigma_m'],cfg['room_kmax_m_inv'])
            for tau0 in p26['zero_relaxation_s']:
                correction=prefactor*(1/(s+1/tau0)-1/(s+5))
                port=port_base+correction[:,None,None];observer=obs_base+correction[:,None,None]
                for cid,d in drivers.items():
                    for vb in cfg['volumes_l']:
                        for n in [1,2]:
                            motor,out,ow,p,p0,bounds=room_case(d,vb,f,port[:,:n,:n],observer[:,:,:n],sigma,medium)
                            metrics=case_metrics(f,motor,out,ow,p,p0,bounds)
                            rows.append(dict(candidate_id=cid,volume_l=vb,source_set=setup['id'],
                                             modal_t60_s=t60,zero_tau_s=tau0,source_count=n,frequency_step_hz=step,**metrics))
                            if (cid in ['C02','C06','C11'] and vb==100 and setup['id'] in ['A','D']
                                    and t60==.4 and tau0==.2 and n==2):
                                velocity=np.linalg.norm(out['velocity']-ow['velocity'],axis=1)/np.linalg.norm(ow['velocity'],axis=1)
                                for j,frequency in enumerate(f):
                                    curves.append(dict(candidate_id=cid,source_set=setup['id'],f_hz=float(frequency),
                                                       pressure_feedback_db=float(20*np.log10(abs(p[j,0]/p0[j,0]))),
                                                       relative_velocity_change=float(velocity[j]),
                                                       coupled_SPL_1v_per_amp_db=float(pressure_db(p[j,0])),
                                                       one_way_SPL_1v_per_amp_db=float(pressure_db(p0[j,0]))))
    table('p11_pokoj_geste_podsumowania.csv',rows)
    table('p11_pokoj_geste_przyklady.csv',curves)
    # Najgorsze znalezione przypadki mają odrębne zagęszczenie siatki.
    keys=['max_perturbation_norm','max_relative_velocity_change','max_abs_pressure_feedback_db']
    refined=[]
    for metric in keys:
        coarse=max(rows,key=lambda r:r[metric]);setup=next(x for x in p26['source_sets'] if x['id']==coarse['source_set'])
        finer=cfg['room_refinement_step_hz'];grid=np.arange(lower,upper+finer/2,finer)
        pos=setup['positions_xyz_m'];n=coarse['source_count']
        port=room.transfer(grid,pos[:n],pos[:n],coarse['modal_t60_s'],coarse['zero_tau_s'],sigma,sigma,cfg['room_kmax_m_inv'])
        observer=room.transfer(grid,pos[:n],[receiver],coarse['modal_t60_s'],coarse['zero_tau_s'],sigma,cfg['room_receiver_sigma_m'],cfg['room_kmax_m_inv'])
        motor,out,ow,p,p0,bounds=room_case(drivers[coarse['candidate_id']],coarse['volume_l'],grid,port,observer,sigma,medium)
        values=case_metrics(grid,motor,out,ow,p,p0,bounds)
        refined.append(dict(metric=metric,candidate_id=coarse['candidate_id'],source_set=coarse['source_set'],
                            volume_l=coarse['volume_l'],modal_t60_s=coarse['modal_t60_s'],zero_tau_s=coarse['zero_tau_s'],
                            source_count=n,coarse_value=coarse[metric],refined_value=values[metric],
                            step_refined_hz=finer,absolute_difference=abs(coarse[metric]-values[metric])))
    table('p11_pokoj_gesty_zbieznosc.csv',refined)
    fig,axes=plt.subplots(1,2,figsize=(12,5))
    for cid in ['C02','C06','C11']:
        selected=[r for r in curves if r['candidate_id']==cid and r['source_set']=='A']
        axes[0].plot([r['f_hz'] for r in selected],[r['pressure_feedback_db'] for r in selected],label=cid)
        axes[1].plot([r['f_hz'] for r in selected],[r['relative_velocity_change']*100 for r in selected],label=cid)
    axes[0].set(xlabel='Hz',ylabel='Zmiana ciśnienia S0 przez reakcję pokoju [dB]',title='Scenariusz A, 100 l, modalne T60=0,4 s / tau0=0,2 s')
    axes[1].set(xlabel='Hz',ylabel='Względna zmiana wektora prędkości [%]',title='Dwa źródła, 1 Vrms na wzmacniacz')
    for ax in axes:ax.grid(alpha=.25);ax.legend()
    save(fig,'21_gesty_skan_reakcji_pokoju')
    result=dict(status='GESTY_SKAN_MODELOWY_NIE_CERTYFIKAT_CIAGLEGO_PASMA',cases=len(rows),frequency_points=len(f),
                total_frequency_realizations=len(rows)*len(f),example_curve_rows=len(curves),refinements=refined,
                maxima={key:max(r[key] for r in rows) for key in keys},
                all_sampled_neumann_bounds_available=all(r['all_sampled_neumann_bounds_available'] for r in rows),
                max_relative_energy_residual=max(r['max_relative_energy_residual'] for r in rows),
                scope='Wszystkie24modele i36rodzin pokoju,4Vb,jeden/dwa źródła. Geometria i straty nie są pomiaremU-017.')
    (OUT/'p11_pokoj_gesty_skan.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps(result,ensure_ascii=False,indent=2));return result


if __name__=='__main__':main()
