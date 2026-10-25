"""Wykonaj162rodziny płyt i par ścian; statyka,mody,dynamika i siły w ściągu."""
from concurrent.futures import ProcessPoolExecutor,as_completed
import csv
import fcntl
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from model_plyty_MITC_P18 import PlateMaterial,RectangularPlate

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def reference_E(thickness_mm,data):
    match=[r for r in data['MDF_reference']['thickness_classes'] if r['minimum_exclusive_mm']<thickness_mm<=r['maximum_inclusive_mm']]
    if len(match)!=1:raise ValueError('Grubość poza referencjąMDF')
    return match[0]


def build_case(case,cfg,data):
    geom=case['geometry'];profile=case['material'];t=case['thickness_mm'];prop=reference_E(t,data)
    material=PlateMaterial(prop['bending_modulus_pa']*profile['E_factor'],profile['nu'],profile['density_kg_m3'],t*.001)
    nx=cfg['mesh_short_n'];ny=2*math.ceil(nx*geom['b_m']/geom['a_m']/2)
    beta=case.get('edge_beta',None)
    boundary=case['boundary'];rot=0. if beta is None else beta*material.rigidity_nm/min(geom['a_m'],geom['b_m'])
    p=RectangularPlate(geom['a_m'],geom['b_m'],nx,ny,material,boundary,rot)
    K=p.K.copy();M=p.M.copy();ties=[]
    rod_t=cfg['tie_thickness_m'];rod_b=cfg['tie_width_m'];length=geom['tie_length_m']
    rod_E=reference_E(rod_t*1000,data)['bending_modulus_pa']*profile['E_factor']
    axial=rod_E*rod_t*rod_b/length
    factor=case.get('joint_factor',np.inf);stiffness=axial if np.isposinf(factor) else axial/(1+2/factor)
    mass=profile['density_kg_m3']*rod_t*rod_b*length
    pad_mass=profile['density_kg_m3']*cfg['pad_size_m']**2*cfg['pad_thickness_m']
    for k in range(case['tie_count']):
        y=geom['b_m']/2 if case['tie_count']==1 else geom['b_m']*(k+1)/3
        patch=p.patch_average((geom['a_m']/2,y),(cfg['pad_size_m'],cfg['pad_size_m']))
        Ks,Ms=p.tied_pair(patch,stiffness,mass,case.get('parity','symmetric'),pad_mass)
        K+=Ks-p.K;M+=Ms-p.M
        ties.append(dict(patch=patch,stiffness_n_m=stiffness,rod_mass_kg=mass,pad_mass_each_kg=pad_mass,
                         axial_rod_only_n_m=axial,position_y_m=y))
    return p,K,M,ties,prop


def worker(job):
    case,cfg,data=job;p,K,M,ties,prop=build_case(case,cfg,data)
    static=p.static(K);freq,modes,_=p.modes(8,K,M)
    pressure=cfg['static_pressure_peak_pa'];h=p.material.thickness_m
    row={k:v for k,v in case.items() if k not in ['geometry','material']}
    row.update(geometry_id=case['geometry']['id'],material_id=case['material']['id'],a_m=p.a,b_m=p.b,
        E_pa=p.material.E_pa,rho_kg_m3=p.material.density_kg_m3,nu=p.material.nu,mesh_nx=p.nx,mesh_ny=p.ny,
        panel_mass_kg=p.material.density_kg_m3*h*p.a*p.b,first_mode_hz=float(freq[0]),modes_hz=freq.tolist(),
        compliance_static_m3_pa=float(p.F@static),static_max_w_m=float(max(abs(p.transverse_displacements(static)))*pressure),
        static_peak_principal_bound_pa=p.peak_principal_bound(static)*pressure,
        static_max_edge_moment_per_length_n=p.edge_moment_peak(static)*pressure,
        static_nominal_MOR_utilization=p.peak_principal_bound(static)*pressure/prop['bending_strength_pa'],
        static_max_w_over_thickness=float(max(abs(p.transverse_displacements(static)))*pressure/h),
        pair_rod_and_pad_added_mass_kg=float(sum(r['rod_mass_kg']+2*r['pad_mass_each_kg'] for r in ties)),
        net_rod_and_pad_solid_volume_l=float(sum((r['rod_mass_kg']+2*r['pad_mass_each_kg'])/p.material.density_kg_m3*1000 for r in ties)),
        static_max_tie_axial_force_n=float(max([abs(2*r['stiffness_n_m']*(r['patch']@static))*pressure for r in ties] or [0.])),
        physical_scope='PANEL_RELATIVE_TO_PRESCRIBED_EDGE_NOT_FULL_CABINET;TIE_SYMMETRIC_PRESSURE_CHANNEL')
    participation=(p.F@modes)**2/(2*np.pi*freq)**2/(p.F@static)
    assert sum(participation)<1+1e-8
    row['modal_uniform_pressure_static_compliance_fractions']=participation.tolist()
    dynamic=[];save=None
    if case.get('dynamic',False):
        base=np.geomspace(*cfg['frequency_base_hz'],cfg['frequency_grid_points']);resonances=freq[(freq>base[0])&(freq<base[-1])]
        fgrid=np.unique(np.r_[base,resonances,resonances*.97,resonances*1.03,20.,40.,80.,100.]);fgrid=fgrid[(fgrid>0)&(fgrid<=1000)]
        values,states,rayleigh=p.frequency_response(fgrid,case['zeta'],K,M)
        amp=cfg['dynamic_pressure_rms_pa']
        for r,q in zip(values,states.T):
            r.update(case_id=case['case_id'],geometry_id=case['geometry']['id'],material_id=case['material']['id'],boundary=case['boundary'],
                tie_count=case['tie_count'],zeta=case['zeta'],thickness_mm=case['thickness_mm'],
                peak_w_at_given_pressure_m=r['maximum_node_peak_per_PaRMS_m']*amp,
                peak_stress_bound_at_given_pressure_pa=r['principal_stress_peak_bound_per_PaRMS']*amp,
                peak_edge_moment_at_given_pressure_n=r['edge_moment_peak_per_PaRMS_n']*amp,
                max_w_over_thickness=r['maximum_node_peak_per_PaRMS_m']*amp/h,
                maximum_tie_force_peak_n=float(max([np.sqrt(2)*abs(2*x['stiffness_n_m']*(x['patch']@q))*amp for x in ties] or [0.])))
            dynamic.append(r)
        row.update(max_dynamic_peak_w_m=max(r['peak_w_at_given_pressure_m'] for r in values),
            max_dynamic_stress_bound_pa=max(r['peak_stress_bound_at_given_pressure_pa'] for r in values),
            max_dynamic_tie_force_n=max(r['maximum_tie_force_peak_n'] for r in values),
            max_dynamic_edge_moment_per_length_n=max(r['peak_edge_moment_at_given_pressure_n'] for r in values),
            max_dynamic_power_residual=max(r['relative_power_residual'] for r in values),
            rayleigh=rayleigh,
            linear_deflection_reference_exceeded=any(r['max_w_over_thickness']>cfg['linear_deflection_to_thickness_reference'] for r in values))
        if case['material']['id']=='REFERENCE' and case['zeta']==.03:
            # Mały zestaw pól do niezależnej projekcji Rayleigha i obrazów.
            peak_index=int(np.argmax([r['peak_w_at_given_pressure_m'] for r in values]))
            chosen=np.unique([int(np.argmin(abs(fgrid-f))) for f in [20.,80.,freq[0],fgrid[peak_index],500.]])
            save=dict(static=static,modes=modes[:,:4],frequency_hz=fgrid[chosen],dynamic=states[:,chosen],xy=p.xy,free=p.free)
    return row,dynamic,save


def jobs(cfg):
    cases=[]
    for geom in cfg['geometries']:
        for t in cfg['thickness_mm']:
            for material in cfg['materials']:
                for boundary in cfg['boundaries']:
                    for tie_count in cfg['tie_counts']:
                        dynamic=(geom['id']==cfg['dynamic_geometry'] and t==cfg['dynamic_thickness_mm'])
                        cases.append(dict(case_id=f'{len(cases):04d}',geometry=geom,thickness_mm=t,material=material,boundary=boundary,tie_count=tie_count,
                                          dynamic=dynamic,zeta=.03))
    base=next(r for r in cases if r['geometry']['id']==cfg['dynamic_geometry'] and r['thickness_mm']==22 and r['material']['id']=='REFERENCE' and r['boundary']=='SSSS' and r['tie_count']==1)
    for zeta in cfg['dynamic_zeta']:
        if zeta==.03:continue
        cases.append(dict(base,case_id=f'{len(cases):04d}',zeta=zeta))
    for beta in cfg['rotational_edge_beta_controls']:
        cases.append(dict(base,case_id=f'{len(cases):04d}',boundary='ELASTIC',edge_beta=beta,dynamic=False))
    for factor in cfg['joint_stiffness_factors_to_rod']:
        cases.append(dict(base,case_id=f'{len(cases):04d}',joint_factor=factor))
    return cases


def table(path,rows):
    fields=list(dict.fromkeys(k for row in rows for k in row))
    with path.open('w',newline='') as h:w=csv.DictWriter(h,fieldnames=fields);w.writeheader();w.writerows(rows)


def main():
    cfgp=ROOT/'dane/konfiguracje/p18a_plyty_i_sciagi.json';dp=ROOT/'dane/materialy/mdf_i_kleje_P18_P19.json'
    cfg=json.loads(cfgp.read_text());data=json.loads(dp.read_text());cases=jobs(cfg)
    sources=[cfgp,dp,Path(__file__),ROOT/'skrypty/model_plyty_MITC_P18.py',ROOT/'brief_system_audio_DIY_v0.6.md',ROOT/'dane/konfiguracje/badania_wstepne.json']
    hashes={str(p.relative_to(ROOT)):__import__('hashlib').sha256(p.read_bytes()).hexdigest() for p in sources}
    digest=hashlib.sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest()
    lockdir=ROOT/'.p18_locks';lockdir.mkdir(exist_ok=True);guard=(lockdir/(digest+'.lock')).open('a')
    try:fcntl.flock(guard,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError:guard.close();raise RuntimeError('Ten przebiegP18nadal działa')
    cache=OUT/'p18a_checkpoint'/digest[:16];cache.mkdir(parents=True,exist_ok=True)
    snapshot=OUT/'archiwum'/('P18A_start_'+digest[:16])/'stan_wejsc'
    for p in sources:
        dest=snapshot/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True)
        if not dest.exists():dest.write_bytes(p.read_bytes())
        assert dest.read_bytes()==p.read_bytes()
    completed={}
    for case in cases:
        p=cache/(case['case_id']+'.json')
        if p.exists():completed[case['case_id']]=json.loads(p.read_text())
    print('P18A:',len(cases),'przypadków;',len(completed),'checkpointów',flush=True)
    with ProcessPoolExecutor(max_workers=cfg['workers']) as ex:
        futures={ex.submit(worker,(case,cfg,data)):case for case in cases if case['case_id'] not in completed}
        for future in as_completed(futures):
            row,dynamic,arrays=future.result();case_id=row['case_id'];record=dict(row=row,dynamic=dynamic)
            if arrays is not None:np.savez_compressed(cache/(case_id+'.npz'),**arrays)
            temp=cache/(case_id+'.tmp');temp.write_text(json.dumps(record,ensure_ascii=False,allow_nan=False));temp.replace(cache/(case_id+'.json'));completed[case_id]=record
            if len(completed)%10==0:print('P18A:',len(completed),'/',len(cases),case_id,flush=True)
    for p in sources:assert hashlib.sha256(p.read_bytes()).hexdigest()==hashes[str(p.relative_to(ROOT))]
    rows=[completed[c['case_id']]['row'] for c in cases];dynamic=[r for c in cases for r in completed[c['case_id']]['dynamic']]
    table(OUT/'p18a_plyty_i_sciagi.csv',rows);table(OUT/'p18a_dynamika.csv',dynamic)
    result=dict(status='P18A_PLYTY_I_SCIAGI_NIE_PELNA_SKRZYNIA',run_sha256=digest,input_sha256=hashes,cases=len(rows),dynamic_rows=len(dynamic),
        checkpoint_folder=str(cache.relative_to(ROOT)),
        max_dynamic_power_residual=max(r.get('max_dynamic_power_residual',0) for r in rows),
        dynamic_cases_outside_declared_small_deflection_reference=sum(r.get('linear_deflection_reference_exceeded',False) for r in rows),
        scope=cfg['scope'],gates=cfg['gates'])
    (OUT/'p18a_podsumowanie.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False));guard.close();print(json.dumps(result,ensure_ascii=False,indent=2));return result


if __name__=='__main__':main()
