"""P26D: cabinet bounds and offset sources in existing phenomenological ModalRoom.
Fixed total |volume-velocity| budget. No scattering, measured room, monitors or SPL claims.
"""
from pathlib import Path
import json,csv,hashlib,platform
import numpy as np
import scipy
from model_pokoju import ModalRoom
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
ROOT=Path(__file__).resolve().parents[1];O=ROOT/'wyniki';D=ROOT/'dane/konfiguracje'

def configurations():
    old=json.loads((D/'p26_scenariusze.json').read_text())
    rec=np.array(old['assumed_listener_xyz_m'])+np.array(old['diagnostic_neighbor_offsets_xyz_m'])
    layouts=[]
    for placement,fronts in [('A',[.65,.65]),('B',[.55,.8])]:
        for orient in ['H_in','H_out','V_low','V_high']:
            sources=[];bounds=[]
            for side,(cx,fronty) in enumerate(zip([.7,3.0],fronts)):
                if orient.startswith('H'):
                    width,height=1.,.5
                    toward=(orient=='H_in')==(side==0)
                    localx=.769 if toward else .231;localz=.25
                else:
                    width,height=.5,1.
                    localx=.25;localz=.231 if orient=='V_low' else .769
                # Scenario feet 20 mm, source front rest offset 16 mm, enclosing C02 depth 496 mm.
                bounds.append([[cx-width/2,fronty-.440-.008,.020],[cx+width/2,fronty+.048,.020+height]])
                sources.append([cx-width/2+localx,fronty+.016,.020+localz])
            b=np.array(bounds);assert np.all(b[:,0]>=0) and np.all(b[:,1]<=[3.7,4.6,2.5])
            assert not np.all(np.minimum(b[0,1],b[1,1])>np.maximum(b[0,0],b[1,0]))
            layouts.append(dict(id=placement+'_'+orient,placement=placement,orientation=orient,sources_xyz_m=sources,complete_envelopes_minmax_xyz_m=bounds,
                 front_planes_y_m=fronts,geometric_fit=True,
                 min_wall_clearance_m=float(np.minimum(b[:,0],np.array([3.7,4.6,2.5])-b[:,1]).min())))
    cfg=dict(scope='Scenarios, not measured room or actual placement. New complete cabinet bound 1000x440x500 mm plus stated protrusions and feet; only C02 excursion bound here. V orientation is rotation about depth axis. No obstacle scattering. Unknown monitor responses.',
        dimensions_xyz_m=[3.7,4.6,2.5],cabinet_body_W_D_H_m=[1,.440,.5],driver_source_from_front_left_bottom_m=[.231,.250],
        geometry_inputs_note='Source rest projection16mm, full front extension48mm, rear8mm, feet20mm are explicit scenarios. C02 geometry only; C11 larger excursion requires rechecking grille bound.',
        receiver_positions_xyz_m=rec.tolist(),receiver_source_file='dane/konfiguracje/p26_scenariusze.json',
        layouts=layouts,modal_t60_s=[.2,.4,.8],zero_relaxation_s=[.02,.2,2],frequencies_Hz=np.arange(20,80.01,.5).tolist(),
        kmax=40,convergence_kmax=60,source_sigma_m=.12,receiver_sigma_m=.03,
        alpha_left_grid=[.25,.5,.75],relative_delay_right_ms=list(range(-8,9,2)),total_source_absolute_U=1,
        nominal_environment=dict(T60_s=.4,tau0_s=.2),budget_note='U_left=alpha, U_right=(1-alpha) exp(-j omega delay), sum abs=1; single-source controls U=1. Not equal electrical power or max SPL.')
    return cfg

def summary(H,f,alpha=.5,delay=0):
    weights=np.array([alpha,1-alpha])[None,:]*np.column_stack([np.ones(len(f)),np.exp(-2j*np.pi*f*delay)])
    response=np.einsum('frs,fs->fr',H,weights)
    db=20*np.log10(np.maximum(abs(response),1e-100));center=db[:,0]
    incoherent=np.sum(abs(H[:,0,:])*abs(weights),axis=1)
    cancellation=20*np.log10(np.maximum(abs(response[:,0])/np.maximum(incoherent,1e-100),1e-100))
    phase=np.angle(H[:,0,0]*np.conj(H[:,0,1]*np.exp(-2j*np.pi*f*delay)))
    return dict(center_ripple_dB=float(np.ptp(center)),center_mean_transfer_dB=float(center.mean()),
       worst_neighbor_center_difference_dB=float(np.max(abs(db[:,1:]-center[:,None]))),
       worst_spatial_spread_dB=float(np.max(np.ptp(db,axis=1))),
       worst_cancellation_dB=float(cancellation.min()),relative_phase_rms_deg=float(np.sqrt(np.mean(phase**2))*180/np.pi),
       minimum_frequency_Hz=float(f[np.argmin(center)])),response

def main():
    cfg=configurations();(D/'p26d_bryly_scenariusze.json').write_text(json.dumps(cfg,indent=2))
    room=ModalRoom();f=np.array(cfg['frequencies_Hz']);rec=np.array(cfg['receiver_positions_xyz_m']);sources=np.array([s for l in cfg['layouts'] for s in l['sources_xyz_m']])
    transfer={};rows=[];best=[];traces={};nomH=None
    for T60 in cfg['modal_t60_s']:
        for tau in cfg['zero_relaxation_s']:
            H=room.transfer(f,sources,rec,T60,tau,kmax_m_inv=40)
            transfer[T60,tau]=H
            if T60==.4 and tau==.2:nomH=H
            print('environment',T60,tau,flush=True)
    for j,l in enumerate(cfg['layouts']):
        H=nomH[:,:,2*j:2*j+2];tested=[]
        for alpha in cfg['alpha_left_grid']:
            for delayms in cfg['relative_delay_right_ms']:
                s,_=summary(H,f,alpha,delayms*.001);tested.append((s['center_ripple_dB'],alpha,delayms))
        minimum=min(t[0] for t in tested)
        # Resolve numerical ties by keeping equal gain/no delay, rather than arbitrary .25/.75.
        tied=[t for t in tested if t[0]<=minimum+1e-9]
        _,alpha,delayms=min(tied,key=lambda t:(abs(t[2]),abs(t[1]-.5),t[1]))
        best.append(dict(layout=l['id'],alpha_left=alpha,relative_delay_right_ms=delayms,search_candidates=len(tested),selection='minimum central ripple in nominal environment only; frozen for all other environments'))
        for (T60,tau),allH in transfer.items():
            H=allH[:,:,2*j:2*j+2]
            baseline,base=summary(H,f)
            for strategy,a,delay in [('equal',.5,0),('nominal_fit',alpha,delayms*.001),('left_only',1,0),('right_only',0,0)]:
                s,response=summary(H,f,a,delay);rows.append(dict(layout=l['id'],T60_s=T60,tau0_s=tau,strategy=strategy,alpha_left=a,delay_right_ms=1000*delay,
                      mean_level_change_vs_equal_dB=s['center_mean_transfer_dB']-baseline['center_mean_transfer_dB'],**s))
                if T60==.4 and tau==.2 and strategy in ['equal','nominal_fit']:traces[l['id']+'_'+strategy]=(20*np.log10(abs(response[:,0]))).tolist()
    assert all(len(v)==len(f) for v in traces.values())
    checks=[]
    # Symmetric cabinets and central/symmetric receiver positions must give mirror equality.
    for j,l in enumerate(cfg['layouts']):
        if l['placement']!='A':continue
        for (T60,tau),allH in transfer.items():
            _,h=summary(allH[:,:,2*j:2*j+2],f)
            err=float(np.max(abs(h[:,1]-h[:,2]))/np.max(abs(h)))
            assert err<1e-11
            checks.append(dict(test='x_reflection_equal_sources',layout=l['id'],T60_s=T60,tau0_s=tau,relative_error=err))
    # Cutoff witnesses at broad band endpoints plus the actual sampled minimum.
    for name in ['A_H_in','B_V_high']:
        j=next(j for j,l in enumerate(cfg['layouts']) if l['id']==name)
        h40=nomH[:,:,2*j:2*j+2];s,_=summary(h40,f)
        ff=np.unique([20.,40.,60.,80.,s['minimum_frequency_Hz']]);ii=np.array([np.argmin(abs(f-f0)) for f0 in ff])
        h60=room.transfer(ff,sources[2*j:2*j+2],rec,.4,.2,kmax_m_inv=60)
        a=h40[ii];diff=h60-a
        relmax=float(np.max(abs(diff)/np.maximum(abs(h60),1e-100)))
        ampdb=float(np.max(abs(20*np.log10(abs(h60)/abs(a)))))
        checks.append(dict(test='cutoff40_60',layout=name,frequencies_Hz=ff.tolist(),relative_L2=float(np.linalg.norm(diff)/np.linalg.norm(h60)),max_pointwise_relative=relmax,max_magnitude_change_dB=ampdb,
             note='Source and receiver smoothing fixed .12/.03m. No certificate for point-source limit or all environments.'))
    for name in ['A_V_high','B_H_out']:
        j=next(j for j,l in enumerate(cfg['layouts']) if l['id']==name)
        worst=max([r for r in rows if r['layout']==name and r['strategy']=='equal'],key=lambda r:r['center_ripple_dB'])
        for step in [.25,.125]:
            ff=np.arange(20,80.001,step)
            hh=room.transfer(ff,sources[2*j:2*j+2],rec,worst['T60_s'],worst['tau0_s'],kmax_m_inv=40)
            ss,_=summary(hh,ff)
            checks.append(dict(test='frequency_mesh_worst_equal_case',layout=name,T60_s=worst['T60_s'],tau0_s=worst['tau0_s'],step_Hz=step,
              ripple_dB=ss['center_ripple_dB'],minimum_frequency_Hz=ss['minimum_frequency_Hz'],ripple_change_vs_halfHz_dB=ss['center_ripple_dB']-worst['center_ripple_dB'],
              note='Deep cancellations are sensitive to frequency sampling; no continuum maximum claim.'))
    assert len(rows)==8*9*4
    # Analytic rigid-box axial frequencies are descriptive, not measured room resonances.
    modes=[dict(axis=ax,length_m=L,first_axial_Hz=343/(2*L)) for ax,L in zip('xyz',[3.7,4.6,2.5])]
    out=dict(scope=cfg['scope'],cases=len(rows),model_layout_environments=72,optimization=best,checks=checks,axial_modes=modes,
       software=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__),
       limitations=['No obstacle scattering or cabinet recoil','No electrical or excursion limits in imposed-U transfer','Phenomenological rigid-mode diagonal damping, not physical impedance boundary','No measured room or monitors','Frequency grid .5Hz, no continuum optimum or guaranteed EQ'])
    (O/'p26d_podsumowanie.json').write_text(json.dumps(out,indent=2))
    with (O/'p26d_porownanie.csv').open('w') as fh:
        w=csv.DictWriter(fh,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (O/'p26d_odpowiedzi_nominalne.json').write_text(json.dumps(dict(frequencies_Hz=f.tolist(),transfer_dB_re_1_Pa_s_m3=traces),indent=2))
    fig,axs=plt.subplots(1,3,figsize=(15,4.5))
    for l in cfg['layouts']:
        if l['id'] in ['A_H_in','B_V_high']:
            for lo,hi in np.array(l['complete_envelopes_minmax_xyz_m']):axs[0].add_patch(Rectangle(lo[:2],hi[0]-lo[0],hi[1]-lo[1],fill=False,label=l['id']))
            ss=np.array(l['sources_xyz_m']);axs[0].scatter(ss[:,0],ss[:,1],s=20)
    axs[0].scatter(rec[:,0],rec[:,1],c='k',s=12);axs[0].set(xlim=(0,3.7),ylim=(0,4.6),aspect='equal',xlabel='x [m]',ylabel='y [m]',title='Bryły i źródła: dwa świadki')
    for name in ['A_H_in','A_H_out','A_V_low','A_V_high']:
        axs[1].plot(f,traces[name+'_equal'],label=name)
    axs[1].set(xlabel='f [Hz]',ylabel='Transfer [dB re 1 Pa s/m³]',title='Jednakowy łączny budżet |U|; środowisko nominalne');axs[1].legend(fontsize=8)
    ids=[l['id'] for l in cfg['layouts']]
    for offset,strategy in [(-.15,'equal'),(.15,'nominal_fit')]:
        vals=[[r['center_ripple_dB'] for r in rows if r['layout']==name and r['strategy']==strategy] for name in ids]
        axs[2].bar(np.arange(8)+offset,[max(v) for v in vals],.3,label=strategy)
    axs[2].set(xticks=np.arange(8),xticklabels=ids,ylabel='Najgorsza nierównomierność [dB]',title='9 środowisk; nominalny wybór gain/delay');axs[2].tick_params(axis='x',rotation=65);axs[2].legend(fontsize=8)
    fig.tight_layout();fig.savefig(O/'p26d_bryly_i_odpowiedz.png',dpi=160);plt.close(fig)
    files=[Path(__file__),ROOT/'skrypty/model_pokoju.py',D/'p26_scenariusze.json',D/'pokoj_odsluchowy.json',D/'pokoj_rzut_scenariusze_v2.json',D/'p26d_bryly_scenariusze.json',ROOT/'brief_system_audio_DIY_v0.6.md',O/'p26d_podsumowanie.json',O/'p26d_porownanie.csv',O/'p26d_odpowiedzi_nominalne.json',O/'p26d_bryly_i_odpowiedz.png']
    (O/'p26d_manifest.json').write_text(json.dumps({str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},indent=2))
    print('DONE',len(rows),flush=True)
if __name__=='__main__':main()
