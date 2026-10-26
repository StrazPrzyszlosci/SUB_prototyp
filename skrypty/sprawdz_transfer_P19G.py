"""Niezależne całki obciążeń, interpolacja afiniczna i niezmienniczość na ruch sztywny."""
from pathlib import Path
import csv,hashlib,json
import numpy as np
from model_podmodelu_P19G import ParentField,LocalJoint
from analiza_podmodelu_P19G import source_fields
from analiza_listwy_stalego_frontu_P19F import solve_refined

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def solve(b,parent):
    F,fixed,prescribed,foot,feet=b.loads_and_boundary(parent)
    free=np.setdiff1d(np.arange(b.ndof),fixed);q=np.zeros(b.ndof);q[fixed]=prescribed
    u,res=solve_refined(b.K[free][:,free],(F[free]-b.K[free][:,fixed]@prescribed)[:,None]);q[free]=u[:,0]
    return q


def main():
    cfgpath=ROOT/'dane/konfiguracje/p19g_podmodel_lokalny.json';cfg=json.loads(cfgpath.read_text());paths=source_fields(cfg)
    global_cases={r['case_id']:r for r in csv.DictReader((OUT/'p19f_geometrie_i_podatnosc.csv').open())}
    source_checks=[];affine_max=0.
    A=np.array([[.013,-.004,.007],[.005,.011,-.006],[-.008,.009,.017]]);shift=np.array([.12,-.13,.09])
    sample={'front':np.array([[.1,.004,.075],[.085,.012,.065],[.12,.018,.04]]),
            'bottom':np.array([[.1,.08,.003],[.1,.12,.015],[.09,.15,.02]]),
            'cleat':np.array([[.08,.025,.026],[.1,.03,.028],[.12,.037,.037]])}
    for (n,s),path in paths.items():
        p=ParentField(path,n,s);feet=p.foot_tractions(cfg['floor_k_xyz_n_m'],cfg['floor_patch_size_m'])
        mass=float(global_cases[f'N{n}_B{int(s*1000)}_REF']['body_mass_kg'])
        force=sum((f['force'] for f in feet),np.zeros(3));expected=np.array([0.,0.,mass*9.80665])
        error=float(np.linalg.norm(force-expected)/np.linalg.norm(expected));assert error<1e-8
        source_checks.append(dict(parent_n=n,section_m=s,total_foot_force_n=force.tolist(),weight_n=expected[2],relative_error=error))
        p.synthetic_affine(A,shift)
        for name,points in sample.items():
            values=p.evaluate(name,points);err=float(np.max(abs(values-(points@A.T+shift))));affine_max=max(affine_max,err)
    assert affine_max<1e-11
    parent=ParentField(paths[(14,.03)],14,.03);load_checks=[]
    rho,g=cfg['rho_mdf_kg_m3'],9.80665;h=cfg['wall_thickness_m'];s=.03
    for domain in cfg['domains']:
        b=LocalJoint(cfg,domain,s,.01)
        F,fixed,prescribed,foot,feet=b.loads_and_boundary(parent)
        width=b.x1-b.x0;y,z=b.ycut,b.zcut;x=(b.x0+b.x1)/2
        force=np.zeros(3);moment=np.zeros(3)
        def add(center,load):
            nonlocal force,moment
            force+=load;moment+=np.cross(center,load)
        for V,c in [(width*h*z,[x,h/2,z/2]),(width*(y-h)*h,[x,(y+h)/2,h/2]),(width*s*s,[x,h+s/2,h+s/2])]:
            add(c,np.array([0.,0.,-rho*g*V]))
        pressure=cfg['static_pressure_pa']
        for area,c,axis in [(width*(z-h-s),[x,h,(z+h+s)/2],1),
                            (width*(y-h-s),[x,(y+h+s)/2,h],2),
                            (width*s,[x,h+s,h+s/2],1),(width*s,[x,h+s/2,h+s],2)]:
            add(c,-pressure*area*np.eye(3)[axis])
        expected_foot=np.zeros(3)
        for f in feet:
            lo=np.maximum(f['lo'],[b.x0,h]);hi=np.minimum(f['hi'],[b.x1,y])
            if np.any(hi<=lo):continue
            ff=f['traction']*np.prod(hi-lo);add(np.r_[(lo+hi)/2,0.],ff);expected_foot+=ff
        actual_F=b.R[:,:3].T@F;actual_M=b.R[:,3:].T@F
        ferr=float(np.linalg.norm(actual_F-force)/max(np.linalg.norm(force),1.))
        merr=float(np.linalg.norm(actual_M-moment)/max(np.linalg.norm(moment),1.))
        footerr=float(np.linalg.norm(foot-expected_foot)/max(np.linalg.norm(expected_foot),1.))
        assert max(ferr,merr,footerr)<1e-10
        load_checks.append(dict(domain=domain['id'],force_relative_error=ferr,moment_relative_error=merr,
                               clipped_foot_relative_error=footerr,local_vertical_foot_force_n=float(foot[2])))
    b=LocalJoint(cfg,cfg['domains'][1],.03,.01)
    pshift=ParentField(paths[(14,.03)],14,.03);praw=ParentField(paths[(14,.03)],14,.03,remove_rigid=False)
    q1,q2=solve(b,pshift),solve(b,praw)
    expected_shift=b.R@pshift.shift
    rigid_error=float(np.linalg.norm((q2-q1)-expected_shift)/np.linalg.norm(q2))
    a=b.observations(q1);c=b.observations(q2)
    observation_error=max(abs(x[k]-y[k])/max(abs(x[k]),1.) for x,y in zip(a,c)
                          for k in ['tension_rms_pa','compression_rms_pa','shear_rms_pa'])
    assert rigid_error<1e-6 and observation_error<1e-4
    inputs=[cfgpath,Path(__file__),ROOT/'skrypty/model_podmodelu_P19G.py',ROOT/'skrypty/analiza_podmodelu_P19G.py',
            ROOT/'skrypty/analiza_listwy_stalego_frontu_P19F.py',ROOT/'skrypty/model_ramy_3D_P18C.py',
            ROOT/'skrypty/element_brylowy_P18C.py',OUT/'p19f_geometrie_i_podatnosc.csv',*paths.values()]
    result=dict(status='AFFINE_TRANSFER_LOAD_INTEGRALS_AND_RIGID_FRAME_CONTROLS_NOT_DEVICE_VALIDATION',
        source_foot_weight_checks=source_checks,affine_interpolation_max_abs_m=affine_max,
        independent_load_integrals=load_checks,rigid_frame_displacement_relative_error=rigid_error,
        rigid_frame_stress_observation_relative_error=observation_error,
        input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs})
    (OUT/'p19g_transfer_i_obciazenia_kontrola.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps({k:v for k,v in result.items() if k!='input_sha256'},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
