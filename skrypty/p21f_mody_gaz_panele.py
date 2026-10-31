"""P21F: 3D acoustic Neumann modes + reciprocal compliant wall pistons.
Run at repository root:
    OPENBLAS_NUM_THREADS=1 python skrypty/p21f_mody_gaz_panele.py
Research-only modal surrogate; NOT P21D obstacle-resolved FEM/FV or measured THD.
"""
import csv, itertools, json, math, hashlib, platform
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy.special import j1
import scipy

ROOT=Path(__file__).resolve().parents[1]
CFG=ROOT/'dane/konfiguracje/p21f_mody_gaz_panele.json'
POOL=ROOT/'dane/przetworniki/pula_rozszerzona.json'
OUT=ROOT/'wyniki'
CACHE={}

def ts(d,c):
    rho,sound=c['rho_kg_m3'],c['speed_of_sound_m_s']
    sd=d['sd_cm2']*1e-4
    cms=d['vas_l']*1e-3/(rho*sound**2*sd**2)
    om=2*np.pi*d['fs_hz']
    m=1/(cms*om*om)
    return sd,cms,m,om*m/d['qms'],np.sqrt(om*m*d['re_ohm']/d['qes']),d['re_ohm'],d['le_mh']*.001

def patch(n,L,fraction):
    if n==0:return 1.
    width=fraction*L; angle=n*np.pi/2
    return float(np.sinc(n*width/(2*L))*np.cos(angle))

def acoustic_modes(c,xc,sd,nmax):
    key=(xc,sd,nmax)
    if key in CACHE:return CACHE[key]
    Lx,Ly,Lz=c['interior_rect_m']; rad=np.sqrt(sd/np.pi)
    assert rad<min(xc,Lx-xc,Lz/2), 'driver disk outside front face'
    omg=[];B=[]
    for nx,ny,nz in itertools.product(range(nmax+1),repeat=3):
        if (nx,ny,nz)==(0,0,0):continue
        k=np.pi*np.array([nx/Lx,ny/Ly,nz/Lz])
        norm=np.prod([np.sqrt(2.) if n else 1. for n in (nx,ny,nz)])
        kr=rad*np.hypot(k[0],k[2])
        disk=2*j1(kr)/kr if kr else 1.
        driver=norm*np.cos(k[0]*xc)*np.cos(k[2]*Lz/2)*disk
        side=norm*patch(ny,Ly,c['wall_patch_fraction_of_span'])*patch(nz,Lz,c['wall_patch_fraction_of_span'])
        top=norm*patch(nx,Lx,c['wall_patch_fraction_of_span'])*patch(ny,Ly,c['wall_patch_fraction_of_span'])*((-1)**nz)
        B.append([driver,side,side*((-1)**nx),top])
        omg.append(c['speed_of_sound_m_s']*np.linalg.norm(k))
    CACHE[key]=(np.array(omg),np.array(B).reshape((-1,4)))
    return CACHE[key]

def acoustic_matrix(w,c,vb,om,B):
    K=c['rho_kg_m3']*c['speed_of_sound_m_s']**2/(vb*.001)
    a=K*np.ones((4,4),complex)  # common, lossless compression mode
    if len(om):
        zeta=c['acoustic_damping_ratio']
        h=-w*w/(om*om-w*w+2j*zeta*om*w)
        a+=K*np.einsum('n,ni,nj->ij',h,B,B)
    return a

def walls(c,kind):
    cw=2*c['single_panel_compliance_m3_Pa']
    if kind=='rigid':return [],[]
    if kind=='uniform_one':return [cw],[c['panel_frequency_hz'][0]]
    scale=2 if kind=='three_patches_2x' else 1
    return [cw*scale*p for p in c['three_panel_compliance_weights']],c['panel_frequency_hz']

def p21e_0d(f,c,d,vb):
    sd,cms,m,rm,bl,re,le=ts(d,c);s=2j*np.pi*f
    Cg=vb*.001/(c['rho_kg_m3']*c['speed_of_sound_m_s']**2)
    Cw=2*c['single_panel_compliance_m3_Pa']
    fn=c['panel_frequency_hz'][0]
    Ceff=Cw/(1-(f/fn)**2+2j*c['panel_damping_ratio']*f/fn)
    zm=rm+m*s+1/(cms*s)+sd**2/(s*(Cg+Ceff))
    I=1/(re+le*s+bl*bl/zm)
    return float(abs(bl*I/zm))

def evaluate(f,c,d,vb,xc,kind,nmax):
    sd,cms,m,rm,bl,re,le=ts(d,c)
    om,B=acoustic_modes(c,xc,sd,nmax)
    if kind=='uniform_one':
        # symmetric displacements on two opposite walls, one generalized y
        one=(B[:,1]+B[:,2])*.5
        B=np.column_stack([B[:,0],one,np.zeros(len(B)),np.zeros(len(B))])
    A=acoustic_matrix(2*np.pi*f,c,vb,om,B)
    comp,fn=walls(c,kind)
    s=2j*np.pi*f;w=2*np.pi*f
    ze=re+s*le;N=len(comp)+1
    Z=np.zeros((N,N),complex);rhs=np.zeros(N,complex)
    Z[0,0]=rm*s+m*s*s+1/cms+bl*bl*s/ze+sd*sd*A[0,0]
    rhs[0]=bl/ze
    damps=[]
    for j,(cj,fj) in enumerate(zip(comp,fn),start=1):
        kw=1/cj; mw=kw/(2*np.pi*fj)**2
        rw=2*c['panel_damping_ratio']*np.sqrt(kw*mw)
        damps.append(rw)
        Z[j,j]=kw+mw*s*s+rw*s+A[j,j]
        Z[0,j]=-sd*A[0,j];Z[j,0]=-sd*A[j,0]
        for k in range(1,j):
            Z[j,k]=A[j,k];Z[k,j]=A[k,j]
    y=np.linalg.solve(Z,rhs);x=y[0];v=s*x
    current=(1-bl*v)/ze
    q=np.zeros(4,complex);q[0]=sd*v;q[1:N]=-s*y[1:]
    p=A@q/s
    air=float(np.real(np.vdot(q,p)))
    wall=float(sum(rw*abs(s*z)**2 for rw,z in zip(damps,y[1:])))
    K=c['rho_kg_m3']*c['speed_of_sound_m_s']**2/(vb*.001)
    if len(om):
        H=s/(om**2-w*w+2j*c['acoustic_damping_ratio']*om*w)
        expected=float(K*np.sum(np.real(H)*abs(B@q)**2))
    else:expected=0.
    input_w=float(np.real(current))
    balance=abs(input_w-(re*abs(current)**2+rm*abs(v)**2+wall+air))/max(abs(input_w),1e-15)
    modal_error=abs(air-expected)/max(abs(input_w),1e-15)
    if air<-1e-9 or balance>2e-10 or modal_error>2e-10:
        raise AssertionError((air,balance,modal_error,kind,nmax,f))
    return dict(velocity_m_s_per_V=float(abs(v)),current_A_per_V=float(abs(current)),
                acoustic_dissipation_W_per_V2=air,wall_dissipation_W_per_V2=wall,
                input_power_W_per_V2=input_w,power_balance_rel=balance,
                acoustic_modal_power_rel=modal_error,acoustic_modes=len(om))

def experiment():
    cfg=json.loads(CFG.read_text())
    pool={v['model']['name']:v['model'] for v in json.loads(POOL.read_text())['drivers']}
    allrows=[];refchecks=[]
    freqs=np.arange(cfg['frequency_hz']['start'],cfg['frequency_hz']['stop']+1e-8,cfg['frequency_hz']['step'])
    for name in cfg['candidate_model_names']:
      for volume in cfg['volume_l']:
       for x0 in cfg['driver_centres_xz_m']:
        for kind in cfg['panel_scenarios']:
         for nmax in cfg['acoustic_cutoff_max_index']:
          for f in freqs:
           res=evaluate(float(f),cfg,pool[name],volume,x0,kind,nmax)
           if kind=='uniform_one' and nmax==0:
               exact=p21e_0d(float(f),cfg,pool[name],volume)
               refchecks.append(abs(res['velocity_m_s_per_V']-exact)/exact)
           allrows.append(dict(candidate=name,volume_l=volume,source_x_m=x0,
                         scenario=kind,nmax=nmax,f_hz=float(f),**res))
    assert max(refchecks)<1e-12
    OUT.mkdir(exist_ok=True)
    with (OUT/'p21f_kampania.csv').open('w',newline='') as h:
        wr=csv.DictWriter(h,fieldnames=allrows[0]);wr.writeheader();wr.writerows(allrows)
    by={(r['candidate'],r['volume_l'],r['source_x_m'],r['scenario'],r['nmax'],r['f_hz']):r for r in allrows}
    out=[];groups=defaultdict(list)
    for name in cfg['candidate_model_names']:
     for volume in cfg['volume_l']:
      for x0 in cfg['driver_centres_xz_m']:
       for kind in cfg['panel_scenarios']:
        for f in freqs:
         f=float(f);prefix=(name,volume,x0,kind)
         v0=by[(*prefix,0,f)]['velocity_m_s_per_V']
         v4=by[(*prefix,4,f)]['velocity_m_s_per_V']
         v5=by[(*prefix,5,f)]['velocity_m_s_per_V']
         stiff=by[(name,volume,x0,'rigid',0,f)]['velocity_m_s_per_V']
         value=dict(candidate=name,volume_l=volume,source_x_m=x0,scenario=kind,
           f_hz=f,gain_vs_rigid0_db=float(20*np.log10(v5/stiff)),
           spatial_vs_uniform_db=float(20*np.log10(v5/v0)),
           n4_n5_db=float(20*np.log10(v5/v4)))
         out.append(value);groups[prefix].append(value)
    with (OUT/'p21f_porownanie.csv').open('w',newline='') as h:
        wr=csv.DictWriter(h,fieldnames=out[0]);wr.writeheader();wr.writerows(out)
    groupstats=[]
    for key,vals in groups.items():
        groupstats.append(dict(candidate=key[0],volume_l=key[1],source_x_m=key[2],
            scenario=key[3],minimum_gain_db=min(x['gain_vs_rigid0_db'] for x in vals),
            maximum_gain_db=max(x['gain_vs_rigid0_db'] for x in vals),
            maximum_spatial_abs_db=max(abs(x['spatial_vs_uniform_db']) for x in vals),
            maximum_n4_n5_abs_db=max(abs(x['n4_n5_db']) for x in vals)))
    totals={}
    for kind in cfg['panel_scenarios']:
        g=[x for x in groupstats if x['scenario']==kind]
        totals[kind]=dict(minimum_gain_db=min(x['minimum_gain_db'] for x in g),
            maximum_gain_db=max(x['maximum_gain_db'] for x in g),
            maximum_spatial_abs_db=max(x['maximum_spatial_abs_db'] for x in g),
            maximum_n4_n5_abs_db=max(x['maximum_n4_n5_abs_db'] for x in g))
    summary=dict(n=len(allrows),reference_checks=len(refchecks),
        reference_error_rel=max(refchecks),power_balance_rel_max=max(x['power_balance_rel'] for x in allrows),
        acoustic_modal_power_rel_max=max(x['acoustic_modal_power_rel'] for x in allrows),
        negative_acoustic_dissipation_count=sum(x['acoustic_dissipation_W_per_V2']<-1e-12 for x in allrows),
        n4_n5_abs_db_max=max(abs(x['n4_n5_db']) for x in out),
        scenarios=totals,groups=groupstats,limitations=cfg['scope'])
    summaryfile=OUT/'p21f_podsumowanie.json'
    summaryfile.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    manifestfiles=[CFG,POOL,Path(__file__),OUT/'p21f_kampania.csv',OUT/'p21f_porownanie.csv',summaryfile]
    (OUT/'p21f_manifest.json').write_text(json.dumps({
      'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,
      'sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in manifestfiles}
    },indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='groups'},indent=2,ensure_ascii=False))

if __name__=='__main__':experiment()
