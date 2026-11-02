#!/usr/bin/env python3
"""B12-14: unilateral contact, bolt springs and global Coulomb bound.
Research screen ONLY. No measured preload, MDF compliance, friction
coefficient, contact geometry, fastening strength, 3D CAD or CNC approval.
Run: python3 skrypty/b12_14_kontakt_docisk_tarcie.py
"""
import hashlib
import itertools
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'wyniki'
OUT.mkdir(parents=True,exist_ok=True)
R=184.0
MASS=30*0.45359237
GRAV=9.80665
KB=200.0  # N/mm: HYPOTHETICAL axial stiffness per inter-rib bolt
KC=500.0  # N/mm: HYPOTHETICAL compression-contact patch stiffness
PRELOADS=(0.0,100.0,300.0,600.0)
RATIOS=(0.5,1.0,2.0,4.0)
GS=(1,3,5,10)
ARMS=(80.0,120.0,160.0)
DIRECTIONS=('x','z')
LOST=(None,0,1)  # two representative bolt-loss locations, not all eight
MUS=(0.15,0.30,0.50,0.70)
Q=[(1.0,math.cos(math.pi*i/4),math.sin(math.pi*i/4)) for i in range(8)]

def lin3(A,b):
    """Three by three Gaussian elimination with partial pivoting."""
    a=[list(map(float,A[i]))+[float(b[i])] for i in range(3)]
    for k in range(3):
        j=max(range(k,3),key=lambda j:abs(a[j][k]))
        a[j],a[k]=a[k],a[j]
        p=a[k][k]
        if abs(p)<1.e-10:raise ArithmeticError('singular contact tangent')
        for l in range(k,4):a[k][l]/=p
        for j in range(3):
            if j==k:continue
            w=a[j][k]
            for l in range(k,4):a[j][l]-=w*a[k][l]
    return [a[i][3] for i in range(3)]

def forces(u,p,kb,kc):
    """B=max(0,p+kb*u), C=max(0,p-kc*u); at u=0 both equal p."""
    B=max(0.0,p+kb*u) if kb else 0.0
    C=max(0.0,p-kc*u)
    if p+kb*u>1.e-9 and p-kc*u>1.e-9:slope=kb+kc
    elif p+kb*u>1.e-9:slope=kb
    elif p-kc*u>1.e-9:slope=kc
    elif kb and abs(p+kb*u)<1.e-9:slope=kb
    elif abs(p-kc*u)<1.e-9:slope=kc
    else:slope=0.0
    return B,C,slope

def solve_contact(preload,ratio,accel,arm,direction,lost):
    F=MASS*GRAV*accel
    moment=F*arm/R
    rhs=(0.0,moment if direction=='x' else 0.0,
         moment if direction=='z' else 0.0)
    ps=[preload if i!=lost else 0.0 for i in range(8)]
    kbs=[KB*(ratio if i%2==0 else 1) if i!=lost else 0.0
         for i in range(8)]
    def residual(z,with_tangent=False):
        B=[];C=[];J=[[0.0]*3 for _ in range(3)];rr=[0.0]*3
        for i,q in enumerate(Q):
            u=sum(z[j]*q[j] for j in range(3))
            b,c,slope=forces(u,ps[i],kbs[i],KC)
            B.append(b);C.append(c)
            for a in range(3):
                rr[a]+=(b-c)*q[a]
                if with_tangent:
                    for t in range(3):J[a][t]+=slope*q[a]*q[t]
        return [rr[k]-rhs[k] for k in range(3)],J,B,C
    z=[0.0,0.0,0.0]
    steps=0
    for it in range(55):
        res,J,B,C=residual(z,True)
        err=max(abs(x) for x in res)
        if err<1.e-7:break
        step=lin3(J,res)
        alpha=1.0
        for trial in range(36):
            zz=[z[k]-alpha*step[k] for k in range(3)]
            nr,*_=residual(zz)
            if max(abs(x) for x in nr)<err-1.e-11:
                z=zz
                break
            alpha*=0.5
        else:raise ArithmeticError('contact solver no descent')
        steps+=1
    else:raise ArithmeticError('contact solver no convergence')
    res,_,B,C=residual(z)
    if max(abs(x) for x in res)>1.e-6:raise AssertionError('normal equilibrium')
    if any(v<0 for v in B+C):raise AssertionError('unilateral constraint')
    if abs(sum(B)-sum(C))>1.e-6:raise AssertionError('axial force balance')
    if lost is not None:assert B[lost]==0
    return {'preload_N_per_intact_bolt':preload,'stiffness_ratio':ratio,
            'accel_g':accel,'moment_arm_mm':arm,'load_direction':direction,
            'lost_bolt':lost,'transverse_force_N':F,'moment_Nmm':F*arm,
            'contact_sum_N':sum(C),'bolt_tension_sum_N':sum(B),
            'contact_open_points':sum(c<=1.e-8 for c in C),
            'bolt_slack_points':sum(b<=1.e-8 for b in B),
            'max_bolt_total_tension_N':max(B),
            'max_bolt_increment_over_initial_N':max(B[i]-ps[i] for i in range(8)),
            'max_contact_patch_compression_N':max(C),
            'max_equilibrium_residual_N':max(abs(x) for x in res),
            'rigid_plate_displacements_mm':z,'solver_iterations':steps,
            'bolt_tensions_N':B,'contact_compressions_N':C}

def main():
    cases=[];checks=[]
    for p,r,a,e,d,l in itertools.product(
         PRELOADS,RATIOS,GS,ARMS,DIRECTIONS,LOST):
        row=solve_contact(p,r,a,e,d,l)
        cases.append(row)
        for mu in MUS:
            cap=mu*row['contact_sum_N']
            F=row['transverse_force_N']
            checks.append({
              'normal_case_index':len(cases)-1,
              'mu_hypothesis':mu,
              'friction_capacity_upper_bound_N':cap,
              'force_N':F,
              'global_stick_capacity_pass':F<=cap+1.e-8,
              'minimum_untransmitted_shear_N':max(0.0,F-cap),
              'mu_required_for_global_capacity':
                  F/row['contact_sum_N'] if row['contact_sum_N'] else None})
    assert len(cases)==4*4*4*3*2*3==1152
    assert len(checks)==len(cases)*4==4608
    assert all(x['max_equilibrium_residual_N']<1.e-6 for x in cases)
    ref=solve_contact(300,1,5,120,'x',None)
    assert ref['contact_open_points']==0
    assert abs(ref['contact_sum_N']-2400)<1.e-7
    expected=(MASS*GRAV*5*120/(4*R))*(KB/(KB+KC))
    assert abs(ref['max_bolt_increment_over_initial_N']-expected)<1.e-7
    assert abs(ref['max_bolt_total_tension_N']-(300+expected))<1.e-7
    def compact(x):
        return {k:(round(x[k],4) if isinstance(x[k],float) else x[k])
                for k in ('contact_sum_N','contact_open_points',
                  'bolt_slack_points','max_bolt_total_tension_N',
                  'max_bolt_increment_over_initial_N',
                  'max_contact_patch_compression_N','solver_iterations')}
    selected={}
    for p in PRELOADS:
        row=solve_contact(p,1,5,120,'x',None)
        selected[str(int(p))]=dict(
            compact(row),transverse_force_N=round(row['transverse_force_N'],4),
            mu_required=round(row['transverse_force_N']/row['contact_sum_N'],4)
                 if row['contact_sum_N'] else None,
            friction_capacity_mu_0_3=round(.3*row['contact_sum_N'],4),
            friction_capacity_mu_0_5=round(.5*row['contact_sum_N'],4))
    summary={
        'normal_cases':len(cases),'friction_inequalities':len(checks),
        'all_normal_equilibrium_verified':True,
        'by_preload_at_5g_e120_rho1':selected,
        'stick_capacity_pass_by_mu':{
          str(mu):sum(z['global_stick_capacity_pass'] for z in checks
                  if z['mu_hypothesis']==mu) for mu in MUS},
        'contact_open_cases':sum(x['contact_open_points']>0 for x in cases),
        'slack_bolt_cases':sum(x['bolt_slack_points']>0 for x in cases),
        'max_iterations':max(x['solver_iterations'] for x in cases),
        'mass_catalog_kg':MASS,
        'global_friction_check':'necessary inequality only; not tangential stick-slip'}
    data={
        'study':'B12-14',
        'method':'8-node rigid flange with unilateral bolt tension/contact compression; semismooth Newton; global Coulomb necessary inequality',
        'source_repo_main':'69c64ab6617dda3ad2d94f4ec55cc027ca47c2dd',
        'known_inputs':{'bolt_circle_R_mm':184,'catalog_weight_lb':30},
        'assumed_inputs':{'bolt_k_N_per_mm':KB,'contact_k_N_per_mm':KC,
          'preloads_per_point_N':PRELOADS,
          'rib_interrib_bolt_stiffness_ratio':RATIOS,
          'accel_g':GS,'lever_mm':ARMS,'friction_mu':MUS,
          'lost_bolt_indices':LOST},
        'limitations':[
          'No measured preload torque, material compliance or friction',
          '8 discrete contact springs not continuous interface pressure',
          'No bolt hole bearing, actual MDF, adhesive or fatigue strength',
          'No physical 3D basket or terminal clearance',
          'Friction bound not a coupled tangential stick-slip solver',
          'No CNC or purchasing approval'],
        'summary':summary,'normal_scenarios':cases,'friction_checks':checks}
    dest=OUT/'b12_14_contact_full.json'
    dest.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    (OUT/'b12_14_manifest_odtworzony.json').write_text(
        json.dumps({'summary':summary,
            'generated_full_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),
            'generator':'skrypty/b12_14_kontakt_docisk_tarcie.py',
            'not_measured':True},
          indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    print(json.dumps(summary,indent=2,ensure_ascii=False))

if __name__=='__main__':main()
