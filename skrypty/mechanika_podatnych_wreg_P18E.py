"""P18E reduced panel pair, finite perimeter springs and actual brace strips.
No full-cabinet claim. SI, linear small-strain plate+beam+axial rod energy.
"""
from pathlib import Path
import json,csv,hashlib,platform
import numpy as np
import scipy
from scipy import sparse
from scipy.sparse.linalg import spsolve,eigsh
from model_plyty_MITC_P18 import RectangularPlate,PlateMaterial,navier_reference

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];O=ROOT/'wyniki'
CFG=ROOT/'dane/konfiguracje/p18e_podatne_wregi.json';C=json.loads(CFG.read_text())
GEOM=ROOT/'dane/konfiguracje/p18e_geometria_zamrozona.json';G=json.loads(GEOM.read_text())

def eb(L,EI,rhoA):
    k=EI/L**3*np.array([[12,6*L,-12,6*L],[6*L,4*L*L,-6*L,2*L*L],[-12,-6*L,12,-6*L],[6*L,2*L*L,-6*L,4*L*L]])
    m=rhoA*L/420*np.array([[156,22*L,54,-13*L],[22*L,4*L*L,13*L,-3*L*L],[54,13*L,156,-22*L],[-13*L,-3*L*L,-22*L,4*L*L]])
    return k,m

def point(p,x,y,field):
    i=min(p.nx-1,max(0,int(x/p.dx)));j=min(p.ny-1,max(0,int(y/p.dy)))
    u=(x-i*p.dx)/p.dx;v=(y-j*p.dy)/p.dy
    ids=p.elements[j*p.nx+i]*3+field
    return sparse.csr_matrix(([(1-u)*(1-v),u*(1-v),u*v,(1-u)*v],([0]*4,ids)),shape=(1,len(p.full_F)))

def perimeter(p,kt,kr):
    k=sparse.lil_matrix(p.full_K.shape)
    edges=[]
    for j in range(p.ny):
        for i in [0,p.nx]:edges.append(([j*(p.nx+1)+i,(j+1)*(p.nx+1)+i],p.dy,1))
    for i in range(p.nx):
        for j in [0,p.ny]:edges.append(([j*(p.nx+1)+i,j*(p.nx+1)+i+1],p.dx,2))
    for nodes,L,rot in edges:
        for f,stiff in [(0,kt),(rot,kr)]:
            ids=3*np.array(nodes)+f;block=stiff*L*np.array([[2,1],[1,2]])/6
            for a in range(2):
                for b in range(2):k[ids[a],ids[b]]+=block[a,b]
    return k.tocsr()

def model(n,E=2.1e9,Eg=1e8,kt=1e7,kr=1000,front=.010,parity='breathing',braced=True):
    W,D,H=np.array(G['inside_mm'])*.001
    mat=PlateMaterial(E,.3,730,.022)
    p=RectangularPlate(W,D,n,max(4,round(n*D/W)),mat,'FREE')
    kp=perimeter(p,kt,kr);K=p.full_K+kp;M=p.full_M.copy();nd=K.shape[0];legs=[];beams=[]
    if braced:
        for x,start in np.array(G['top_beam_axis_x_start_y_mm'])*.001:
            ends=np.unique(np.r_[start,np.arange(p.ny+1)*p.dy,D]);ends=ends[(ends>=start-1e-10)&(ends<=D+1e-10)]
            for a,b in zip(ends,ends[1:]):
                T=sparse.vstack([point(p,x,a,0),point(p,x,a,2),point(p,x,b,0),point(p,x,b,2)]).tocsr()
                kb,mb=eb(b-a,E*.022*.022**3/12,730*.022*.022)
                K+=T.T@sparse.csr_matrix(kb)@T;M+=T.T@sparse.csr_matrix(mb)@T
                beams.append((T,kb,b-a))
            for y,width in ([(front/2,front),(D-.011,.022)] if start==0 else [(D-.011,.022)]):
                area=.022*width;ell=H-.044
                kleg=1/(ell/(E*area)+2*C['glue_t_m']/(Eg*area))
                # Distributed contact averages ensure no mesh-dependent point singularity for legs.
                v=sparse.csr_matrix(p.patch_average((x,y),(.022,width))[None,:])
                factor=2 if parity=='breathing' else 0
                K+=factor*kleg*(v.T@v)
                meff=730*area*ell/(6 if parity=='breathing' else 2)
                M+=meff*(v.T@v)
                legs.append(dict(v=v,k=kleg,factor=factor,area=area,x=x,y=y,width=width))
    return p,K.tocsr(),M.tocsr(),kp,legs,beams

def solve_case(n,**params):
    p,K,M,kp,legs,beams=model(n,**params);F=p.full_F
    vals,vec=eigsh(K,k=6,M=M,sigma=0,which='LM',v0=np.sin(np.arange(K.shape[0])+1));ii=np.argsort(vals);vals=vals[ii];vec=vec[:,ii]
    vec*=np.sign(vec[np.argmax(abs(vec),axis=0),np.arange(vec.shape[1])])[None,:]
    freq=np.sqrt(vals)/(2*np.pi);q=spsolve(K,F);w=q[0::3]
    ones=np.zeros(len(q));ones[0::3]=1
    maxres=np.linalg.norm(K@q-F)/np.linalg.norm(F)
    legforces=np.array([d['factor']*d['k']*float((d['v']@q)[0]) for d in legs])
    balance=abs(ones@(kp@q)+sum(legforces)-sum(F))/sum(F)
    energy=abs(float(q@(K@q)-q@F))/float(q@F)
    f1=freq[0];a=2*.03*(2*np.pi*f1)*(2*np.pi*5*f1)/(2*np.pi*6*f1);b=2*.03/(2*np.pi*6*f1);damp=a*M+b*K
    harmonics=[]
    for f in C['frequency_Hz']:
        om=2*np.pi*f;u=spsolve(K-om**2*M+1j*om*damp,F)
        power=-om*np.imag(F@u);loss=om**2*np.real(np.vdot(u,damp@u));res=abs(power-loss)/max(abs(power),1e-30)
        legstress=max([abs(d['factor']*d['k']*(d['v']@u)[0])/d['area'] for d in legs],default=0)
        beamstress=max([max(abs((kb@(T@u))[[1,3]]))*.011/(.022*.022**3/12) for T,kb,ell in beams],default=0)
        harmonics.append(dict(f_Hz=f,leg_mean_axial_stress_per_Papeak=float(legstress),beam_centroid_bending_stress_per_Papeak=float(beamstress),w_peak_per_Papeak_m=float(max(abs(u[0::3]))),max_surface_stress_per_Papeak=float(p.peak_principal_bound(u)),power_residual=float(res)))
    # Uniform normal acceleration is common physical motion; only physically interpret in common parity.
    gforce=M@ones*9.80665;g=spsolve(K,gforce)
    row=dict(**params,nx=n,ny=p.ny,dof=K.shape[0],f1_Hz=float(freq[0]),f2_Hz=float(freq[1]),
      compliance_m3_Pa=float(F@q),wmax_m_Pa=float(max(abs(w))),surface_stress_bound_Pa_Pa=p.peak_principal_bound(q),
      max_leg_force_N_Pa=float(max(abs(legforces))) if len(legs) else 0,
      max_leg_axial_stress_Pa_Pa=float(max([abs(force)/d['area'] for force,d in zip(legforces,legs)],default=0)),
      reaction_balance_relative=float(balance),static_energy_relative=float(energy),linear_residual=float(maxres),
      gravity_common_normal_deflection_m=float(max(abs(g[0::3]))) if params['parity']=='common' else None,
      gravity_scope='horizontal: top/bottom normal load; vertical: normal component zero, in-plane load NOT modelled',
      harmonics=harmonics)
    assert maxres<1e-7 and balance<1e-7 and energy<1e-7
    assert all(h['power_residual']<1e-7 for h in harmonics)
    return row,(p,q,freq,vec)

def controls():
    result=[dict(test='series_glue_leg_compliance_algebra',E_MDF_Pa=2.1e9,leg_length_m=.412,glue_each_m=.00025,glue_compliance_fraction_of_leg_max=.05,required_Eglue_Pa=2*.00025*2.1e9/(.05*.412),meaning='joint elastic compliance <=5% of axial leg compliance, not strength or whole-cabinet criterion')]
    # Independent closed-form simply-supported Mindlin plate reference (no braces/springs).
    mat=PlateMaterial(2.1e9,.3,730,.022)
    for n in [12,20,32,48,64]:
        p=RectangularPlate(.956,.374,n,max(4,round(n*.374/.956)),mat,'SSSS');q=p.static();f=p.modes(1)[0][0];ref=navier_reference(.956,.374,mat,201)
        result.append(dict(test='independent_Navier_Mindlin',nx=n,relative_compliance=float((p.F@q)/ref['volume_compliance_m3_pa']-1),relative_f1=float(f/ref['first_mode_hz']-1)))
    # Independently derived Euler beam: simply supported elastic end translations under uniform load.
    # Exact midspan w=5 q L^4/(384 EI)+q L/(2k). No plate code in this check.
    for n in [4,8,16]:
        L=.374;EI=2.1e9*.022*.022**3/12;k=1e5;d=L/n
        K=np.zeros((2*n+2,2*n+2));F=np.zeros(2*n+2)
        for i in range(n):
            ids=np.arange(2*i,2*i+4);ke,_=eb(d,EI,0);K[np.ix_(ids,ids)]+=ke;F[ids]+=np.array([d/2,d*d/12,d/2,-d*d/12])
        K[0,0]+=k;K[-2,-2]+=k;u=np.linalg.solve(K,F);ref=5*L**4/(384*EI)+L/(2*k)
        err=abs(u[n]/ref-1);assert err<1e-9
        result.append(dict(test='independent_elastic_end_beam_formula',elements=n,relative_midspan=float(err)))
    return result

def main():
    rows=[];states={}
    base=dict(E=2.1e9,Eg=1e8,kt=1e7,kr=1000,front=.010,parity='breathing',braced=True)
    cases=[]
    for n in C['mesh_nx']:
        for front in [.010,.022]:cases.append((n,dict(base,front=front)))
        cases.append((n,dict(base,braced=False)))
    for key,values in [('E',C['mdf_E_Pa']),('Eg',C['glue_E_Pa']),('kt',C['perimeter_translation_N_m2']),('kr',C['perimeter_rotation_N'])]:
        for v in values:cases.append((20,dict(base,**{key:v})))
    for parity in ['common','breathing']:
        for front in [.010,.022]:cases.append((32,dict(base,parity=parity,front=front)))
    for n in [48,64]:cases.append((n,dict(base,parity='common',front=.010)))
    seen=set()
    for n,p in cases:
        key=(n,tuple(p.items()))
        if key in seen:continue
        seen.add(key);row,state=solve_case(n,**p);rows.append(row)
        if n==64 and p['front']==.010 and p['parity']=='breathing' and p['braced']:states['nominal']=state
        print('case',len(rows),'n',n,'f1',row['f1_Hz'],flush=True)
        (O/'p18e_przypadki.json').write_text(json.dumps(rows,indent=2))
    ctrl=controls()
    out=dict(scope=C['scope'],cases=len(rows),controls=ctrl,software=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__),
             acceptance='Equilibrium/energy residual <1e-7. Mesh changes reported, not assumed <5%. No material strength threshold supplied.')
    (O/'p18e_kontrole.json').write_text(json.dumps(out,indent=2))
    p,q,freq,vec=states['nominal'];fig,axs=plt.subplots(1,3,figsize=(14,4))
    for i,v in enumerate([q,vec[:,0],vec[:,1]]):
        field=v[0::3].reshape(p.ny+1,p.nx+1);im=axs[i].imshow(field,origin='lower',extent=[0,p.a,0,p.b],aspect='equal',cmap='coolwarm');fig.colorbar(im,ax=axs[i],shrink=.55)
        axs[i].set(xlabel='x [m]',ylabel='głębokość y [m]',title='Ugięcie [m/Pa]' if i==0 else f'Mod {i}: {freq[i-1]:.1f} Hz, norma M')
    fig.suptitle('P18E: podzespół paneli, sprężyste otoczenie; nie pełna skrzynia');fig.tight_layout();fig.savefig(O/'p18e_pola.png',dpi=150);plt.close(fig)
    fig,axs=plt.subplots(1,2,figsize=(11,4))
    for front,label in [(.010,'noga przednia 10 mm'),(.022,'22 mm: kontrfaktyczny dostęp')]:
        a=[r for r in rows if all(r[k]==v for k,v in base.items() if k!='front') and r['front']==front]
        a=sorted(a,key=lambda r:r['nx']);axs[0].plot([r['nx'] for r in a],[r['f1_Hz'] for r in a],'o-',label=label)
        r=a[-1];axs[1].plot([h['f_Hz'] for h in r['harmonics']],[h['w_peak_per_Papeak_m']*1e6 for h in r['harmonics']],'o-',label=label)
    axs[0].set(xlabel='Podziały w x',ylabel='Pierwszy mod [Hz]',title='Zbieżność podzespołu');axs[1].set(xlabel='f [Hz]',ylabel='Maks. ruch [µm/Pa peak]',title='Odpowiedź harmoniczna; zeta=0,03')
    for ax in axs:ax.legend(fontsize=8);ax.grid(alpha=.3)
    fig.tight_layout();fig.savefig(O/'p18e_wrazliwosc.png',dpi=150);plt.close(fig)
    files=[CFG,Path(__file__),ROOT/'skrypty/model_plyty_MITC_P18.py',GEOM,ROOT/'brief_system_audio_DIY_v0.6.md',O/'p18e_przypadki.json',O/'p18e_kontrole.json',O/'p18e_pola.png',O/'p18e_wrazliwosc.png']
    (O/'p18e_manifest.json').write_text(json.dumps({str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files},indent=2))
if __name__=='__main__':main()
