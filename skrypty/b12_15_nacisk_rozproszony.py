#!/usr/bin/env python3
"""B12-15: multi-patch unilateral annular contact under hypothetical preload relaxation.
NOT continuous FEM; NOT a measurement; NOT CNC. Python 3 standard library.
"""
import json, math, itertools, hashlib
from pathlib import Path

RB=184.0
RI,RO=177.9,194.2
RC=(RI+RO)/2
A=math.pi*(RO**2-RI**2)
MASS=30*0.45359237
G=9.80665
KB=200.0       # N/mm bolt spring, hypothesis
KC=500.0       # N/mm contact of 1/8 ring, hypothesis
NN=(8,16,32)
KAPPAS=(0.,3.,12.) # preload localization on ring, arbitrary angular profile
CONTACT_MULT=(.5,1.,2.)
PRELOAD=(100.,300.,600.)
RETENTION=(1.,.75,.5) # residual, not a time-dependent viscoelastic model
ACCELS=(1.,5.,10.)
ARMS=(80.,120.)
DIRECTIONS=('x','z')

def gauss(a,b):
    v=[list(map(float,a[i]))+[float(b[i])] for i in range(3)]
    for i in range(3):
        pivot=max(range(i,3),key=lambda j:abs(v[j][i]))
        v[i],v[pivot]=v[pivot],v[i]
        if abs(v[i][i])<1e-11:raise ArithmeticError('singular tangent')
        den=v[i][i]
        v[i]=[z/den for z in v[i]]
        for j in range(3):
            if j==i:continue
            factor=v[j][i]
            v[j]=[v[j][k]-factor*v[i][k] for k in range(4)]
    return [v[i][3] for i in range(3)]

def geometry(n,kappa,contact_mult,preload_residual):
    bolts=[(1.,math.cos(2*math.pi*i/8),math.sin(2*math.pi*i/8)) for i in range(8)]
    contact=[(1.,RC/RB*math.cos(2*math.pi*j/n),RC/RB*math.sin(2*math.pi*j/n)) for j in range(n)]
    w=[]
    for j in range(n):
        phi=2*math.pi*j/n
        weight=sum(math.exp(kappa*(math.cos(phi-2*math.pi*i/8)-1)) for i in range(8))
        w.append(weight)
    total=sum(w)
    c0=[8*preload_residual*x/total for x in w]
    # Ring-sector stiffness is area-normalized: refinement must not
    # spuriously increase the integrated normal stiffness.
    kj=[KC*8/n*contact_mult]*n
    return bolts,contact,c0,kj

def simulate(n,kappa,contact_mult,P,retention,accel,arm,direction):
    effective=P*retention
    bolts,cpts,c0,kc=geometry(n,kappa,contact_mult,effective)
    rhs=[0.,0.,0.]
    moment=MASS*G*accel*arm/RB
    rhs[1 if direction=='x' else 2]=moment
    def evaluate(z,tangent=False):
        res=[-q for q in rhs]
        mat=[[0.]*3 for i in range(3)]
        B=[];C=[]
        def add(q,val,deriv):
            for i in range(3):
                res[i]+=val*q[i]
                if tangent:
                    for j in range(3):mat[i][j]+=deriv*q[i]*q[j]
        for q in bolts:
            d=sum(q[j]*z[j] for j in range(3))
            raw=effective+KB*d
            b=max(0.,raw)
            B.append(b)
            add(q,b,KB if raw>0 else 0.)
        for i,q in enumerate(cpts):
            d=sum(q[j]*z[j] for j in range(3))
            raw=c0[i]-kc[i]*d
            c=max(0.,raw)
            C.append(c)
            add(q,-c,kc[i] if raw>0 else 0.)
        return res,mat,B,C
    z=[0.,0.,0.]
    for iteration in range(80):
        r,J,B,C=evaluate(z,True)
        err=max(abs(v) for v in r)
        if err<1e-7:break
        step=gauss(J,r)
        lam=1.
        for k in range(40):
            zp=[z[i]-lam*step[i] for i in range(3)]
            next_r,*_=evaluate(zp)
            if max(map(abs,next_r))<err-1.e-11:
                z=zp
                break
            lam/=2
        else:raise ArithmeticError('line search failed')
    else:raise ArithmeticError('Newton did not converge')
    res,_,B,C=evaluate(z)
    assert max(map(abs,res))<1e-6
    assert abs(sum(B)-sum(C))<1e-6
    assert min(B+C)>=0
    pmax=max(C)/(A/n) # Pressure proxy ONLY: actual gasket contact area unknown
    totalC=sum(C)
    return {'ring_nodes':n,'concentration_kappa':kappa,'contact_stiffness_multiplier':contact_mult,
       'initial_preload_per_bolt_N':P,'residual_fraction':retention,
       'remaining_preload_per_bolt_N':effective,'accel_g':accel,'moment_arm_mm':arm,
       'force_direction':direction,'external_shear_N':MASS*G*accel,
       'open_contact_patches':sum(v<1e-8 for v in C),
       'open_ring_fraction_model':sum(v<1e-8 for v in C)/n,
       'sum_contact_N':totalC,'max_bolt_tension_N':max(B),
       'max_contact_force_N':max(C),'max_pressure_proxy_N_per_mm2':pmax,
       'pressure_concentration_ratio':n*max(C)/totalC if totalC else 0.,
       'mu_required_global':MASS*G*accel/totalC if totalC else None,
       'bolt_forces_N':B,'contact_forces_N':C,
       'max_balance_error_N':max(map(abs,res)),'iterations':iteration,
       'displacements_a_b_c_mm':z}

def calculate():
    cases=[]
    for args in itertools.product(NN,KAPPAS,CONTACT_MULT,PRELOAD,RETENTION,ACCELS,ARMS,DIRECTIONS):
        cases.append(simulate(*args))
    assert len(cases)==3*3*3*3*3*3*2*2==2916
    assert all(x['max_balance_error_N']<1e-6 for x in cases)
    # Closed-contact analytical reference independent of ring subdivision.
    for n in NN:
        x=simulate(n,0.,1.,300.,1.,5.,120.,'x')
        assert x['open_contact_patches']==0
        assert abs(x['sum_contact_N']-2400.)<1e-6
        moment=MASS*G*5*120/RB
        delta=KB*moment/(4*KB+4*KC*(RC/RB)**2)
        assert abs(x['max_bolt_tension_N']-(300+delta))<1.e-6
        assert abs(x['pressure_concentration_ratio']-1.)>0.
    samples=[]
    for n in NN:
        for kappa in KAPPAS:
            for retention in RETENTION:
                x=simulate(n,kappa,1.,300.,retention,5.,120.,'x')
                samples.append({k:round(x[k],6) if isinstance(x[k],float) else x[k]
                    for k in ['ring_nodes','concentration_kappa','residual_fraction','open_contact_patches',
                              'sum_contact_N','max_bolt_tension_N','max_pressure_proxy_N_per_mm2',
                              'pressure_concentration_ratio','mu_required_global']})
    summary={'cases':len(cases),'ring_discretizations':NN,'preload_distribution_kappa':KAPPAS,
         'contact_stiffness_factors':CONTACT_MULT,'assumed_preload_N':PRELOAD,
         'residual_fractions':RETENTION,'gravity_levels':ACCELS,
         'arms_mm':ARMS,'directions':DIRECTIONS,
         'contact_open_cases':sum(x['open_contact_patches']>0 for x in cases),
         'examples':samples,
         'mass_catalog_kg':MASS,'annular_area_geometric_proxy_mm2':A,
         'all_equilibria_checked':True}
    out=Path('wyniki');out.mkdir(exist_ok=True)
    data={'study':'B12-15','evidence':'hypothetical numerical study ONLY','summary':summary,
          'limitations':['annular continuous contact approximated by 8/16/32 uncoupled patches',
          'ideal full annular area used as nominal pressure divisor; real seal area unknown',
          'relaxation is prescribed residual PRELOAD, not time-dependent viscoelastic model',
          'friction evaluated as necessary global threshold, not local slip',
          'no measured gasket or MDF stiffness/contact/fastener capacity, no CNC approval'],
          'scenarios':cases}
    dest=out/'b12_15_pelne_rozklady.json'
    dest.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    digest=hashlib.sha256(dest.read_bytes()).hexdigest()
    (out/'b12_15_generated_manifest.json').write_text(
       json.dumps({'sha256':digest,'summary':summary},ensure_ascii=False,indent=2)+'\n',
       encoding='utf8')
    print(json.dumps({'cases':len(cases),'open':summary['contact_open_cases'],
                      'selected':samples[:14], 'hash':digest},ensure_ascii=False,indent=2))
    return summary

if __name__=='__main__':calculate()
