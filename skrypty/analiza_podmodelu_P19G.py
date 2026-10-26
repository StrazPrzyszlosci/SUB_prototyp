"""P19G: lokalna siatka MDF/listwy, trzy odległości granicy i dwa pola rodzica."""
from pathlib import Path
import csv,gc,hashlib,json,platform,resource
import numpy as np
import scipy
from model_podmodelu_P19G import ParentField,LocalJoint
from analiza_listwy_stalego_frontu_P19F import solve_refined

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki';CFG=ROOT/'dane/konfiguracje/p19g_podmodel_lokalny.json'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def source_fields(cfg):
    meta=json.loads((OUT/'p19g_pola_globalne.json').read_text())
    original=json.loads((OUT/'p19f_pole_referencyjne.json').read_text())
    path=ROOT/cfg['parent_reference_npz'];assert sha(path)==original['output_sha256'][cfg['parent_reference_npz']]
    paths={(14,.03):path}
    for r in meta['parents']:
        path=ROOT/r['path'];assert sha(path)==r['sha256'];paths[(r['mesh_n'],r['section_m'])]=path
    return paths


def solve_case(cfg,parent,case,save_field=False):
    available=int(next(s.split()[1] for s in Path('/proc/meminfo').read_text().splitlines() if s.startswith('MemAvailable:')))*1024
    assert available>1_500_000_000,('MEMORY_GUARD',available)
    domain=next(d for d in cfg['domains'] if d['id']==case['domain'])
    b=LocalJoint(cfg,domain,case['section_m'],case['yz_step_m'],case['nx'])
    F,fixed,prescribed,foot,feet=b.loads_and_boundary(parent)
    free=np.setdiff1d(np.arange(b.ndof),fixed);q=np.zeros(b.ndof);q[fixed]=prescribed
    force_reduced=F[free]-b.K[free][:,fixed]@prescribed
    value,res=solve_refined(b.K[free][:,free],force_reduced[:,None]);q[free]=value[:,0]
    r=b.K@q-F;reaction=np.zeros(b.ndof);reaction[fixed]=r[fixed]
    net=b.R.T@(F+reaction)
    balance=float(np.linalg.norm(net)/max(np.linalg.norm(F),1.))
    assert balance<1e-7,balance
    energy=float(.5*q@(b.K@q));assert energy>0
    work=float(q@(F+reaction));work_error=abs(work-2*energy)/max(2*energy,1e-30)
    assert work_error<1e-7
    row=dict(**case,dof=b.ndof,fixed_dof=len(fixed),free_linear_residual=max(res),
        force_moment_balance_normalized=balance,energy_work_relative_error=work_error,
        strain_energy_j=energy,local_foot_vertical_force_n=float(foot[2]),
        geometric_rigid_K_error=b.rigid_error,
        peak_process_RSS_MiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024)
    observations=[dict(case_id=case['case_id'],**r) for r in b.observations(q)]
    if save_field:
        np.savez_compressed(OUT/'p19g_pole_lokalne_B30_middle.npz',xyz_m=b.xyz,q_m=q,
            panel_names=np.array([p.name for p in b.panels]),panel_offsets=np.array([p.offset for p in b.panels]),
            panel_node_counts=np.array([len(p.xyz) for p in b.panels]),fixed_dof=fixed,
            prescribed_m=prescribed,parent_rigid_shift=parent.shift)
    del b;gc.collect()
    return dict(case=row,observations=observations)


def table(name,rows):
    with (OUT/name).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def main():
    cfg=json.loads(CFG.read_text());sources=source_fields(cfg)
    inputs=[CFG,Path(__file__),ROOT/'skrypty/model_podmodelu_P19G.py',ROOT/'skrypty/element_brylowy_P18C.py',
        ROOT/'skrypty/model_ramy_3D_P18C.py',ROOT/'skrypty/analiza_listwy_stalego_frontu_P19F.py',
        OUT/'p19g_pola_globalne.json',OUT/'p19f_pole_referencyjne.json',ROOT/'brief_system_audio_DIY_v0.6.md',*sources.values()]
    hashes={str(p.relative_to(ROOT)):sha(p) for p in inputs}
    run=hashlib.sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest()
    cache=Path('/tmp')/('sub-p19g-'+run[:16]);cache.mkdir(exist_ok=True)
    cases=[]
    for s in cfg['sections_m']:
        for domain in cfg['domains']:
            for h in cfg['yz_target_step_m']:
                cases.append(dict(case_id=f'B{int(s*1000)}_{domain["id"]}_H{h:g}_P14_X8',
                    section_m=s,domain=domain['id'],yz_step_m=h,parent_n=14,nx=8))
    for h in [.005,.0025]:cases.append(dict(case_id=f'B30_middle_H{h:g}_P18_X8',section_m=.03,domain='middle',yz_step_m=h,parent_n=18,nx=8))
    for nx in cfg['span_refinements_x']:cases.append(dict(case_id=f'B30_middle_H0.0025_P14_X{nx}',section_m=.03,domain='middle',yz_step_m=.0025,parent_n=14,nx=nx))
    parents={key:ParentField(path,*key) for key,path in sources.items()}
    results=[];new_count=0
    for case in cases:
        path=cache/(case['case_id']+'.json')
        field=case['case_id']=='B30_middle_H0.0025_P14_X8'
        if path.exists() and (not field or (OUT/'p19g_pole_lokalne_B30_middle.npz').exists()):
            archived=json.loads(path.read_text());assert archived['run_sha256']==run
            raw=json.dumps(archived['result'],sort_keys=True,allow_nan=False).encode();assert hashlib.sha256(raw).hexdigest()==archived['result_sha256']
            result=archived['result'];print('P19G cache:',case['case_id'],flush=True)
        else:
            result=solve_case(cfg,parents[(case['parent_n'],case['section_m'])],case,field)
            digest=hashlib.sha256(json.dumps(result,sort_keys=True,allow_nan=False).encode()).hexdigest()
            tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(dict(run_sha256=run,result=result,result_sha256=digest),allow_nan=False));tmp.replace(path)
            new_count+=1;print('P19G calculated:',case['case_id'],'dof',result['case']['dof'],flush=True)
        results.append(result)
    assert len(results)==22
    table('p19g_przypadki_i_bilans.csv',[r['case'] for r in results])
    table('p19g_lokalne_pola_spoin.csv',[o for r in results for o in r['observations']])
    result=dict(status='ONE_WAY_CONFORMING_LOCAL_JOINT_STUDY_NOT_STRENGTH_QUALIFICATION',date='2026-10-26',
        run_sha256=run,cases=len(results),observation_rows=sum(len(r['observations']) for r in results),
        new_cases_this_invocation=new_count,cache_note='Wznowienie zgodnego cache nie jest świeżą niezależną replikacją.',
        libraries=dict(Python=platform.python_version(),NumPy=np.__version__,SciPy=scipy.__version__),
        input_sha256=hashes,limitations=cfg['gates'])
    (OUT/'p19g_podsumowanie.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print('P19G COMPLETE:',len(results),'cases;',new_count,'new.',flush=True)


if __name__=='__main__':main()
