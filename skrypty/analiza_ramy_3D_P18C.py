"""Pelna3Drama:6paneli,12spoin,otwor,kosz,sciagi i podparcie;SI."""
import csv,gc,hashlib,json,resource
from pathlib import Path
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import eigsh,spsolve
from model_ramy_3D_P18C import Cabinet3D

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def table(name,rows):
    keys=list(dict.fromkeys(k for r in rows for k in r))
    with (OUT/name).open('w',newline='') as f:
        writer=csv.DictWriter(f,keys);writer.writeheader();writer.writerows(rows)


def main():
    cfg=json.loads((ROOT/'dane/konfiguracje/p18c_rama_3D.json').read_text())
    kn=cfg['glue_E_proxy_pa']/cfg['glue_thickness_m'];ks=kn/(2*(1+cfg['glue_nu_assumed']))
    sources=['brief_system_audio_DIY_v0.6.md','dane/konfiguracje/p18c_rama_3D.json','dane/zrodla/P18B_geometria_i_ograniczenia.json',
             'dane/materialy/mdf_i_kleje_P18_P19.json','dane/materialy/kleje_P19_mechanika_v1.json',
             'skrypty/element_brylowy_P18C.py','skrypty/model_ramy_3D_P18C.py','skrypty/analiza_ramy_3D_P18C.py',
             'skrypty/model_frontu_z_otworem_P18B.py','skrypty/model_plyty_MITC_P18.py']
    hashes={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in sources}
    summary=[];modes=[];harmonics=[];joints=[];support_rows=[];unexecuted=[]

    def record(b,label,do_dynamic=False):
        q,F,acc=b.balanced_static(b.pressure);work=float(b.pressure@q)
        val,vec=b.free_modes(12);frequencies=np.sqrt(np.maximum(val[6:],0))/(2*np.pi)
        assert max(abs(val[:6]))<.01,'Brak szesciu numerycznych modow sztywnych'
        assert min(val[6:])>1
        participation=(vec[:,6:].T@b.pressure)**2/val[6:]/work;dominant=int(np.argmax(participation))
        static_res=float(np.linalg.norm(b.K@q-F)/np.linalg.norm(F));assert static_res<1e-7
        mass=float(b.mass_rigid[0,0]);volume=sum(p.volume for p in b.panels)
        row=dict(case_id=label,mesh_n=b.n,dof=b.ndof,element_form='EAS9' if b.enhanced else 'H8_FULL',
                 MDF_volume_m3=volume,total_mass_kg=mass,wall_volume_compliance_m3_pa=work,
                 first_elastic_hz=float(frequencies[0]),strongest_pressure_of12_hz=float(frequencies[dominant]),
                 captured_static_pressure_fraction=float(sum(participation)),static_relative_residual=static_res,
                 basket_y_com_relative_m_pa=float(q[-5]),peak_process_RSS_MiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024)
        summary.append(row)
        for index,frequency in enumerate(frequencies):modes.append(dict(case_id=label,index=index+1,f_hz=float(frequency),pressure_static_compliance_fraction=float(participation[index])))
        for item in b.joint_summary(q):joints.append(dict(case_id=label,load='PRESSURE_STATIC_1PA',**item))
        Fbody=np.zeros(b.ndof);Fbody[-5]=1.;qa,balanced,ar=b.balanced_static(Fbody)
        row['body_inertial_relief_compliance_m_n']=float(balanced@qa)
        row['reciprocity_absolute_error']=float(abs(b.pressure@qa-balanced@q))
        if do_dynamic:
            for support in [0.,*cfg['floor_normal_each_n_m']]:
                if support:b.set_floor(support,support*cfg['floor_tangential_to_normal'])
                else:b.floor_K=sparse.csr_matrix(b.K.shape)
                if support:
                    gravity=-9.80665*(b.M@b.R[:,2]);qg=spsolve(b.K+b.floor_K,gravity)
                    reactions=np.array([-foot['k'][2]*(foot['P']@qg)[2] for foot in b.feet])
                    assert min(reactions)>0
                    fullfreq=eigsh(b.K+b.floor_K,k=12,M=b.M,sigma=0,which='LM',v0=np.sin(np.arange(b.ndof)+1))[0]
                    support_rows.append(dict(case_id=label,normal_each_n_m=support,gravity_min_reaction_n=float(min(reactions)),
                                             gravity_max_reaction_n=float(max(reactions)),gravity_max_node_displacement_m=float(max(abs(qg))),
                                             first_supported_hz=float(np.sqrt(min(fullfreq))/(2*np.pi)),
                                             gravity_generalized_force_residual=float(np.linalg.norm(b.R.T@(gravity-b.floor_K@qg))/np.linalg.norm(b.R.T@gravity))))
                    for item in b.joint_summary(qg):joints.append(dict(case_id=label,load='GRAVITY_FLOOR_'+str(support),**item))
                for signal,Fharm in [('PRESSURE_1PA_RMS',b.pressure),('BASKET_Y_1N_RMS',Fbody)]:
                    for frequency in cfg['harmonic_f_hz']:
                        w=2*np.pi*frequency;eta=cfg['structural_loss_factor_assumed'];etaf=cfg['floor_loss_factor_assumed']
                        Z=(1+1j*eta)*b.K+(1+1j*etaf)*b.floor_K-w*w*b.M
                        u=spsolve(Z,Fharm.astype(complex));pin=float((-1j*w*np.vdot(u,Fharm)).real)
                        loss=float(w*(eta*np.vdot(u,b.K@u).real+etaf*np.vdot(u,b.floor_K@u).real))
                        power_res=abs(pin-loss)/max(abs(pin),abs(loss),1e-30);assert power_res<1e-6
                        rigid=b.R@np.linalg.solve(b.mass_rigid,b.R.T@(b.M@u));relative=u-rigid
                        item=dict(case_id=label,normal_each_n_m=support,signal=signal,f_hz=frequency,
                                  basket_y_rms_m=float(abs(u[-5])),basket_y_internal_rms_m=float(abs(relative[-5])),
                                  wall_volume_response_rms_m3=float(abs(b.pressure@u)),input_power_w=pin,dissipated_power_w=loss,
                                  relative_power_residual=power_res)
                        if support:
                            margin=[];friction=[]
                            for foot,normal in zip(b.feet,reactions):
                                force=-(1+1j*etaf)*foot['k']*(foot['P']@u)
                                low=normal-np.sqrt(2)*abs(force[2]);margin.append(low)
                                friction.append(float(np.sqrt(2)*np.linalg.norm(force[:2])/low) if low>0 else None)
                            item['minimum_normal_contact_margin_n']=float(min(margin))
                            item['required_friction_coefficient_bound']=max(x for x in friction if x is not None) if all(x is not None for x in friction) else None
                            item['normal_support_gate']='PRESERVED_AT_SAMPLED_FREQUENCY' if min(margin)>0 else 'UNLOADING_POSSIBLE'
                        harmonics.append(item)
                print('P18C harmonic',label,'support',support,flush=True)
        print('P18C case',label,'dof',b.ndof,'C',work,'f1',frequencies[0],'RSS',row['peak_process_RSS_MiB'],flush=True)
        # Kazdy skonczony blok ma jawny zapis;nie udajemy calosci po przerwaniu.
        table('p18c_rama.csv',summary);table('p18c_mody.csv',modes);table('p18c_harmoniczne.csv',harmonics)
        table('p18c_spoiny.csv',joints);table('p18c_podparcie.csv',support_rows)
        return row

    for n in cfg['mesh_interior_intervals']:
        available=int(next(line.split()[1] for line in Path('/proc/meminfo').read_text().splitlines() if line.startswith('MemAvailable:')))*1024
        if n>=14 and available<1_500_000_000:
            unexecuted.append(dict(mesh_n=n,reason='AVAILABLE_MEMORY_GUARD',available_bytes=available));continue
        b=Cabinet3D(n=n,nt=cfg['thickness_layers'],bond_kn=kn,bond_ks=ks)
        record(b,'MESH_'+str(n));del b;gc.collect()
    # Wspolny modelN10:dobor usztywnien,jakoscspoiny/materialu i podparcie.
    for factor in cfg['bond_stiffness_stress_factors']:
        b=Cabinet3D(n=10,bond_kn=kn*factor,bond_ks=ks*factor)
        record(b,'BOND_'+str(factor),factor==1)
        if factor==1:
            K0=b.K.copy();M0=b.M.copy()
            for count in [1,2]:
                b.K=K0.copy();b.M=M0.copy();b.add_ties(count)
                record(b,'TIES_'+str(count),True)
        del b;gc.collect()
    for case in cfg['material_stresses']:
        params={k:v for k,v in case.items() if k!='id'}
        b=Cabinet3D(n=10,bond_kn=kn,bond_ks=ks,**params);record(b,case['id']);del b;gc.collect()
    b=Cabinet3D(n=6,bond_kn=kn,bond_ks=ks,enhanced=False);record(b,'H8_FULL_CONTROL');del b;gc.collect()
    result=dict(status='SCOPED_FULL_FRAME_STUDY_NOT_FINAL_CABINET',case_count=len(summary),modal_rows=len(modes),harmonic_rows=len(harmonics),
                joint_rows=len(joints),support_rows=len(support_rows),unexecuted=unexecuted,input_sha256=hashes,
                maximum_power_residual=max(r['relative_power_residual'] for r in harmonics),scope=cfg['gates'])
    (OUT/'p18c_podsumowanie.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print('P18C complete',len(summary),len(harmonics),'unexecuted',unexecuted,flush=True)


if __name__=='__main__':main()
