"""P18B: porównanie frontów z rzeczywistymi średnicami i jawnymi hipotezami."""
import csv
import hashlib
import itertools
import json
from pathlib import Path
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve
from model_frontu_z_otworem_P18B import PlateMaterial,FrontWithHole,MountedFront

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def table(name,rows):
    keys=list(dict.fromkeys(k for r in rows for k in r))
    with (OUT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,keys);w.writeheader();w.writerows(rows)


def resized(base,mass,k,rg=.1,zcg=.08):
    p=base.plate
    K=sparse.block_diag([p.K,sparse.csr_matrix((3,3))],format='csr')+k*(base.D.T@base.D)
    J=mass*(rg*rg+zcg*zcg)
    M=sparse.block_diag([p.M,sparse.diags([mass,J,J])],format='csr')
    return MountedFront(p,K,M,base.B,base.G,base.D,k,mass,base.positions)


def main():
    cfg=json.loads((ROOT/'dane/konfiguracje/p18b_front_z_otworem.json').read_text())
    inputs=['brief_system_audio_DIY_v0.6.md','dane/konfiguracje/p18b_front_z_otworem.json',
            'dane/zrodla/P18B_geometria_i_ograniczenia.json','dane/materialy/mdf_i_kleje_P18_P19.json',
            'skrypty/model_frontu_z_otworem_P18B.py','skrypty/model_plyty_MITC_P18.py',
            'skrypty/analiza_frontu_z_otworem_P18B.py','wyniki/p11_kalibracje_masy.csv']
    hashes={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in inputs}
    allrows=[];coupled=[];controls=[];modes=[];worst_independent=0.;worst_power=0.

    def record(system,cid,span,h,bc,group):
        nonlocal worst_independent
        p=system.plate;H=system.load(pressure_pa=1,pressure_cap=True)
        freqs,vec=system.modes(8)
        cp=float(H@system.static(H));participation=(vec.T@H)**2/(2*np.pi*freqs)**2/cp
        dominant=int(np.argmax(participation))
        row=dict(candidate_id=cid,group=group,span_a_m=span[0],span_b_m=span[1],thickness_m=h,boundary=bc,
                 payload_mass_kg=system.mass,spring_each_n_m=system.k,first_mode_hz=float(freqs[0]),
                 pressure_strongest_of_8_hz=float(freqs[dominant]),first_mode_static_pressure_fraction=float(participation[0]),
                 strongest_of_8_pressure_fraction=float(participation[dominant]),first_8_static_pressure_fraction=float(sum(participation)),
                 front_mdf_mass_kg=p.actual_solid_area_m2*p.material.thickness_m*p.material.density_kg_m3,
                 minimum_clear_span_margin_m=min(span)/2-p.r,
                 mass_evidence='CATALOGUE_NET_C04' if cid=='C04' and system.mass==7.68 else 'ASSUMED_COMMON_OR_STRESS_PAYLOAD')
        loads=[('pressure',system.load(pressure_pa=cfg['pressure_control_pa'],pressure_cap=True)),
               ('force',system.load(basket_force_n=cfg['force_control_n'])),
               ('moment',system.load(moment_x_nm=cfg['moment_control_nm']))]
        for label,F in loads:
            q=system.static(F);obs=system.observe(q)
            row[label+'_max_plate_w_m']=obs['maximum_plate_w_m']
            row[label+'_basket_w_m']=float(q[-3]);row[label+'_basket_tilt_rad']=float(np.linalg.norm(q[-2:]))
            row[label+'_max_joint_force_n']=float(max(abs(obs['joint_forces_n'])))
            row[label+'_max_gauss_bending_principal_pa']=p.bending_stress_bound(q[:-3])
            row[label+'_generalized_compliance_work_j']=float(F@q)
        if group!='COMMON_PAYLOAD' or (h==.022 and span==[.46,.46] and system.k==1e6):
            F=loads[0][1]+loads[1][1]+loads[2][1]
            q=system.static(F);qr,forces=system.independent_static(F)
            err=float(np.max(abs(q-qr))/np.max(abs(q)));worst_independent=max(worst_independent,err);assert err<1e-8
        for i in range(8):modes.append(dict(case_id=len(allrows),candidate_id=cid,mode=i+1,f_hz=float(freqs[i]),static_pressure_compliance_fraction=float(participation[i])))
        allrows.append(row)
        return row

    for span,h,bc in itertools.product(cfg['front_spans_m'],cfg['thickness_m'],cfg['boundaries']):
        E=2.2e9 if h<=.019 else 2.1e9
        for d in cfg['drivers']:
            p=FrontWithHole(*span,d['hole_radius_m'],PlateMaterial(E,.3,730,h),
                            cfg['mesh_angular_per_side'],cfg['mesh_radial_layers'],bc)
            base=p.mounted(d['bolt_circle_radius_m'],d['bolt_count'],10,.164,1e6,cfg['patch_radius_m'])
            for k in cfg['spring_each_n_m']:
                system=resized(base,10,k);record(system,d['candidate_id'],span,h,bc,'COMMON_PAYLOAD')
            if span==[.46,.46] and h==.022:
                for mass in [5.,7.68,15.]:record(resized(base,mass,1e6),d['candidate_id'],span,h,bc,'PAYLOAD_SENSITIVITY')
                if d['candidate_id']=='C04':
                    for phase,patch,k,label in [(np.pi/8,.004,1e6,'BOLT_PHASE_PI8'),(0,.002,1e6,'PATCH_2MM'),
                                              (0,.006,1e6,'PATCH_6MM'),(0,.004,1e3,'SOFT_JOINT'),(0,.004,1e9,'STIFF_JOINT')]:
                        test=p.mounted(d['bolt_circle_radius_m'],8,7.68,7.68*.0164,k,patch,phase)
                        record(test,'C04',span,h,bc,label)
                    with (OUT/'p11_kalibracje_masy.csv').open() as f:
                        cal=[r for r in csv.DictReader(f) if r['candidate_id']=='C04' and r['reference']=='PISTON']
                    for k in cfg['spring_each_n_m']:
                        system=resized(base,7.68,k)
                        for calibration,f in itertools.product(cal,[20.,40.,80.,150.,300.]):
                            m=float(calibration['effective_remaining_mass_kg'])
                            q,row=system.prescribed_cone(f,.001,m,.0458)
                            obs=system.observe(q);worst_power=max(worst_power,row['relative_power_residual'])
                            assert row['relative_power_residual']<1e-8
                            row.update(candidate_id='C04',boundary=bc,spring_each_n_m=k,payload_mass_kg=7.68,
                                       reference_faces=float(calibration['faces']),frequency_scope='LOW_BAND_REFERENCE' if f<=80 else 'CAVITY_0D_EXTRAPOLATION',
                                       basket_motion_rms_m=float(abs(q[-3])),maximum_plate_peak_m=np.sqrt(2)*obs['maximum_plate_w_m'],
                                       maximum_joint_peak_n=float(np.sqrt(2)*max(abs(obs['joint_forces_n']))),
                                       maximum_gauss_bending_principal_peak_bound_pa=np.sqrt(2)*p.bending_stress_bound(q[:-3]))
                            coupled.append(row)
                    Kc,Mc,Fc,Tc=p.continuous_inner(7.68,7.68*.0164);Fc[-3]+=p.hole_polygon_area_m2
                    qc=spsolve(Kc,Fc)
                    controls.append(dict(candidate_id='C04',boundary=bc,scope='CONTINUOUS_INNER_RIGID_CLAMP_NOT_BOLTED_ASSEMBLY',
                                         pressure_pa=1,cap_displacement_m=float(qc[-3]),compliance_m3_pa=float(Fc@qc)))
            print('P18B:',span,h,bc,d['candidate_id'],'zapisanych przypadków',len(allrows),flush=True)
    table('p18b_fronty_i_mocowania.csv',allrows);table('p18b_mody_i_udzialy.csv',modes)
    table('p18b_ruch_zadany_i_komora.csv',coupled);table('p18b_ciagly_sztywny_brzeg.csv',controls)
    summary=dict(status='P18B_EXECUTED_SCOPED_FRONT_MODELS_NOT_FINAL_CABINET',cases=len(allrows),modal_rows=len(modes),
                 coupled_rows=len(coupled),continuous_inner_controls=len(controls),input_sha256=hashes,
                 worst_independent_static_relative_error=worst_independent,maximum_coupled_power_residual=worst_power,
                 scope=cfg['gates'],next='Rzeczywiste połączenie front-rama,preload/uszczelka i integracja pełnej skrzyni P19-P21.')
    (OUT/'p18b_podsumowanie.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False,allow_nan=False))
    print('P18B zakończone:',len(allrows),len(coupled),'bilans',worst_power)


if __name__=='__main__':main()
