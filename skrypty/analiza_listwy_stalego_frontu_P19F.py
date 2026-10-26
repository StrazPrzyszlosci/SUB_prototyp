"""P19F: skończona droga siły przez listwę MDF, dwie spoiny i pełną ramę.

Statyka, nie kryterium zniszczenia. Cache /tmp zawiera wyłącznie zgodne
wyniki z hashem, nie jest nową niezależną replikacją po wznowieniu.
"""
from pathlib import Path
import csv
import gc
import hashlib
import json
import os
import platform
import resource
import numpy as np
import scipy
from scipy import sparse
from scipy.sparse.linalg import splu
from element_brylowy_P18C import quad_quadrature
from model_ramy_3D_P18C import clip_rectangle, polygon_quadrature, inverse_quad
from model_listwy_naroznej_P19F import model

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'wyniki'
CFG=ROOT/'dane/konfiguracje/p19f_listwa_stalego_frontu.json'
INPUTS=[CFG,Path(__file__),ROOT/'skrypty/model_listwy_naroznej_P19F.py',
        ROOT/'skrypty/model_ramy_3D_P18C.py',ROOT/'skrypty/element_brylowy_P18C.py',
        ROOT/'skrypty/model_frontu_z_otworem_P18B.py',ROOT/'skrypty/model_plyty_MITC_P18.py',
        ROOT/'dane/konfiguracje/p18c_rama_3D.json',ROOT/'brief_system_audio_DIY_v0.6.md']


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def solve_refined(K,F):
    """Równoważenie diagonalne, jedna LU i poprawianie reszty longdouble."""
    scale=1/np.sqrt(K.diagonal())
    S=sparse.diags(scale)
    lu=splu((S@K@S).tocsc())
    q=scale[:,None]*lu.solve(scale[:,None]*F)
    Kl=K.astype(np.longdouble);Fl=F.astype(np.longdouble)
    for step in range(5):
        residual=Fl-Kl@q.astype(np.longdouble)
        relative=np.linalg.norm(np.asarray(residual,float),axis=0)/np.linalg.norm(F,axis=0)
        if max(relative)<2e-9:break
        q+=scale[:,None]*lu.solve(scale[:,None]*np.asarray(residual,float))
    assert max(relative)<2e-8,relative
    return q,relative.tolist()


def joint_fields(b,q):
    """Jawne skoki w dodatniej kwadraturze, rozciąganie osobno od ściskania."""
    result={}
    for piece in b.bonds:
        axis=piece.normal_axis;other=[a for a in range(3) if a!=axis]
        first=b.xyz[piece.nodes[:4]][:,other];second=b.xyz[piece.nodes[4:]][:,other]
        poly=clip_rectangle(first,second.min(axis=0),second.max(axis=0))
        u=q[(3*piece.nodes[:,None]+np.arange(3)).ravel()].reshape(8,3)
        sign=-1 if piece.name.startswith(('front_','bottom_')) else 1
        item=result.setdefault(piece.name,dict(area=0.,tension2=0.,compression2=0.,shear2=0.,peak=0.,energy=0.))
        stiffness=np.array([piece.kn if a==axis else piece.ks for a in range(3)])
        for point,w in polygon_quadrature(poly,4):
            d=np.r_[inverse_quad(first,point),-inverse_quad(second,point)]
            jump=d@u;traction=stiffness*jump;normal=sign*traction[axis]
            item['area']+=w
            item['tension2']+=w*max(normal,0)**2
            item['compression2']+=w*min(normal,0)**2
            item['shear2']+=w*sum(traction[a]**2 for a in other)
            item['peak']=max(item['peak'],normal)
            item['energy']+=.5*w*np.sum(stiffness*jump**2)
    return [dict(joint=name,area_m2=r['area'],tensile_spatial_rms_pa=np.sqrt(r['tension2']/r['area']),
                 compressive_spatial_rms_pa=np.sqrt(r['compression2']/r['area']),
                 shear_spatial_rms_pa=np.sqrt(r['shear2']/r['area']),
                 sampled_maximum_tensile_pa=r['peak'],spring_energy_j=r['energy']) for name,r in result.items()]


def calculate(cfg,case):
    available=int(next(s.split()[1] for s in Path('/proc/meminfo').read_text().splitlines() if s.startswith('MemAvailable:')))*1024
    assert available>1_300_000_000,('MEMORY_GUARD',available)
    n,size,nc,E=case['mesh_n'],case['section_m'],case['cross_intervals'],case['new_glue_E_pa']
    t=cfg['glue_thickness_m'];nu=cfg['glue_nu_assumed']
    b=model(n=n,section=size,cross_intervals=nc,kn=E/t,ks=E/(2*(1+nu)*t),end_gap=cfg['cleat_end_clearance_m'])
    b.set_floor(cfg['floor_normal_each_n_m'],cfg['floor_tangent_each_n_m'])
    gravity=-9.80665*(b.M@b.R[:,2])
    frozen=getattr(b,'frozen_original_pressure',b.pressure)
    F=np.column_stack([gravity,cfg['static_internal_pressure_pa']*b.pressure,frozen])
    q,res=solve_refined(b.K+b.floor_K,F)
    stats=dict(**case,dof=b.ndof,body_mass_kg=float(b.R[:,2]@(b.M@b.R[:,2])),
               supported_C_actual_pressure_m3_pa=float(b.pressure@q[:,1]/cfg['static_internal_pressure_pa']),
               supported_C_frozen_original_H_m3_pa=float(frozen@q[:,2]),
               normalized_linear_residual=max(res),peak_process_RSS_MiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,
               attachment_checks=b.cleat['checks'] if size else None)
    loads=[];fields=[]
    for name,qq,ff in [('GRAVITY',q[:,0],gravity),
                      ('GRAVITY_PLUS_STATIC_1KPA',q[:,0]+q[:,1],F[:,0]+F[:,1])]:
        reactions=[float(-f['k'][2]*(f['P']@qq)[2]) for f in b.feet]
        load=dict(case_id=case['case_id'],load=name,minimum_floor_normal_reaction_n=min(reactions),
                  valid_normal_contact=min(reactions)>0,
                  elastic_work_half_j=float(.5*ff@qq))
        assert load['valid_normal_contact'],load
        loads.append(load)
        fields += [dict(case_id=case['case_id'],load=name,**x) for x in joint_fields(b,qq)]
    del b;gc.collect()
    return dict(case=stats,loads=loads,joints=fields)


def write(name,rows):
    with (OUT/name).open('w',newline='',encoding='utf-8') as h:
        w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def main():
    cfg=json.loads(CFG.read_text())
    hashes={str(p.relative_to(ROOT)):sha(p) for p in INPUTS}
    run=hashlib.sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest()
    cache=Path('/tmp')/('sub-p19f-'+run[:16]);cache.mkdir(exist_ok=True)
    cases=[];E=cfg['glue_reference_effective_E_pa']
    for n in cfg['global_mesh_n']:
        for s in [0.]+cfg['cleat_sections_m']:
            cases.append(dict(case_id=f'N{n}_B{int(s*1000)}_REF',mesh_n=n,section_m=s,cross_intervals=4,new_glue_E_pa=E))
    for s in cfg['cleat_sections_m']:
        for e in cfg['new_joint_E_stress_pa']:
            cases.append(dict(case_id=f'N14_B{int(s*1000)}_E{e:g}',mesh_n=14,section_m=s,cross_intervals=4,new_glue_E_pa=e))
    for nc in [2,8]:
        cases.append(dict(case_id=f'N14_B30_CROSS{nc}',mesh_n=14,section_m=.03,cross_intervals=nc,new_glue_E_pa=E))
    results=[];new_count=0
    for case in cases:
        p=cache/(case['case_id']+'.json')
        if p.exists():
            r=json.loads(p.read_text());assert r['run_sha256']==run
            r=r['result']
            print('P19F cache:',case['case_id'],flush=True)
        else:
            r=calculate(cfg,case)
            tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(dict(run_sha256=run,result=r),ensure_ascii=False,allow_nan=False));tmp.replace(p)
            new_count+=1
            print('P19F calculated:',case['case_id'],'dof',r['case']['dof'],'C',r['case']['supported_C_frozen_original_H_m3_pa'],flush=True)
        results.append(r)
    # Tę samą listwę oceniamy wobec tej samej siatki i obciążenia H.
    for r in results:
        n=r['case']['mesh_n']
        ref=next(x['case'] for x in results if x['case']['mesh_n']==n and x['case']['section_m']==0)
        ratio=r['case']['supported_C_frozen_original_H_m3_pa']/ref['supported_C_frozen_original_H_m3_pa']
        assert ratio<=1+1e-7,(r['case']['case_id'],ratio)
        r['case']['C_frozen_to_same_mesh_no_cleat_ratio']=ratio
    flat=[]
    for r in results:
        c={k:v for k,v in r['case'].items() if k!='attachment_checks'}
        if r['case']['attachment_checks']:
            a=r['case']['attachment_checks'];c.update(added_mass_kg=a['added_mass_kg'],occupied_volume_l=a['occupied_volume_m3']*1000)
        else:c.update(added_mass_kg=0.,occupied_volume_l=0.)
        flat.append(c)
    write('p19f_geometrie_i_podatnosc.csv',flat)
    write('p19f_obciazenia_i_podpory.csv',[x for r in results for x in r['loads']])
    write('p19f_spoiny_i_przeniesienie_obciazen.csv',[x for r in results for x in r['joints']])
    result=dict(status='FINITE_CLEAT_GEOMETRY_AND_JOINT_LOAD_SCREENING_NOT_FRACTURE_QUALIFICATION',date='2026-10-26',
        run_sha256=run,cases=len(results),load_cases=sum(len(r['loads']) for r in results),
        new_cases_this_invocation=new_count,cache_note='Zgodny cache nie jest świeżą niezależną replikacją.',
        libraries=dict(Python=platform.python_version(),NumPy=np.__version__,SciPy=scipy.__version__),
        input_sha256=hashes,attachment_checks=[r['case']['attachment_checks'] for r in results if r['case']['attachment_checks']],
        limitations=cfg['gates'],next='Wybrać geometrię do lokalnego uzupełnienia siatki/MDF i warunkowej trwałości; następnie P20/P21.')
    (OUT/'p19f_podsumowanie.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print('P19F COMPLETE:',len(results),'cases;',new_count,'new.',flush=True)


if __name__=='__main__':main()
