"""P21H: exact face-integrated pressure coupling to Navier Kirchhoff plate modes.

Run: OPENBLAS_NUM_THREADS=1 python skrypty/p21h_rozlozone_mody_paneli_fv.py
Requires skrypty/p21g_fv_podatne_panele.py (P21G) and its input JSON files.
Two independent simply-supported 22 mm MDF plates, 1..9 modes per plate.
NOT full P18E bonded-brace FEM; assumed supports, damping and modulus.
"""
import csv,hashlib,json,platform
from pathlib import Path
import numpy as np, scipy
from scipy.sparse import coo_matrix,diags
from scipy.sparse.linalg import splu
from p21g_fv_podatne_panele import grid,source,driver_ts

ROOT=Path(__file__).resolve().parents[1]
C=ROOT/'dane/konfiguracje/p21h_modalne_plyty_fv.json'
P=ROOT/'dane/przetworniki/pula_rozszerzona.json'
O=ROOT/'wyniki';O.mkdir(exist_ok=True)

def integrals_sine(a,b,m,L):
    return L/(m*np.pi)*(np.cos(m*np.pi*a/L)-np.cos(m*np.pi*b/L))

def modes(g,c,limit):
    # Integral phi_mn dA on each FLUID-EXPOSED boundary face, not a
    # normalized patch average. Same integral governs pressure force and
    # wall-induced flow, providing reciprocal coupling at the FV interface.
    xe,ye,ids=g['xe'],g['ye'],g['ids'];W=xe[-1];D=ye[-1]
    ret=[];desc=[]
    for side in (0,1):
        k=0 if side==0 else -1
        for m in range(1,limit+1):
            ix=integrals_sine(xe[:-1],xe[1:],m,W)
            for n in range(1,limit+1):
                iy=integrals_sine(ye[:-1],ye[1:],n,D)
                s=np.zeros(g['n'])
                for i in range(len(ix)):
                    for j in range(len(iy)):
                        idx=ids[i,j,k]
                        if idx>=0:s[idx]=ix[i]*iy[j]
                ret.append(s);desc.append((side,m,n))
    return np.column_stack(ret),desc

def structure(c,desc,E,zeta):
    W=.956;D=.374;h=c['panel_t_m'];rho=c['panel_density_kg_m3'];nu=c['panel_nu']
    bending=E*h**3/(12*(1-nu**2));mass=rho*h*W*D/4
    omegas=np.array([np.pi**2*np.sqrt(bending/(rho*h))*((m/W)**2+(n/D)**2)
                     for _,m,n in desc])
    return mass,omegas,2*zeta*mass*omegas

def port(g,c,f,src,ms):
    w=2*np.pi*f;rho=c['rho_kg_m3'];c0=c['sound_m_s']
    bulk=np.full(g['n'],rho*c0*c0+0j)
    bulk[g['fill']]*=(1+1j*c['fill_bulk_loss_tangent'])
    a,b=g['a'],g['b'];cond=g['face']/(rho*(g['da']+g['db']))
    mat=coo_matrix((np.r_[cond,cond,-cond,-cond],
        (np.r_[a,b,a,b],np.r_[a,b,b,a])),shape=(g['n'],g['n'])).tocsc()
    mat-=diags(w*w*g['vol']/bulk,format='csc')
    S=np.column_stack([src,ms]);rhs=1j*w*S
    X=splu(mat).solve(rhs.astype(complex));Z=S.T@X
    res=np.linalg.norm(mat@X-rhs)/np.linalg.norm(rhs)
    rec=np.max(abs(Z-Z.T))/max(np.max(abs(Z)),1e-12)
    assert res<1e-8 and rec<1e-9,(res,rec)
    return Z,float(res),float(rec)

def coupled(Z,d,c,desc,limit,f,E,zeta):
    sd,cms,mechm,rm,bl,re,le=driver_ts(d,c)
    s=2j*np.pi*f;w=2*np.pi*f;ze=re+s*le
    Zm=rm+s*mechm+1/(s*cms)
    indices=[0]+[3+j for j,(_,m,n) in enumerate(desc) if m<=limit and n<=limit]
    z=Z[np.ix_(indices,indices)];nm=len(indices)-1
    zrig=Zm+sd*sd*z[0,0];Irig=1/(ze+bl*bl/zrig);vrig=bl*Irig/zrig
    mass,omega,rw=structure(c,[x for x in desc if x[1]<=limit and x[2]<=limit],E,zeta)
    A=np.zeros((nm+2,nm+2),complex);rhs=np.zeros(nm+2,complex);rhs[-1]=1
    A[0,0]=zrig;A[0,1:nm+1]=-sd*z[0,1:];A[0,-1]=-bl
    A[1:nm+1,0]=-sd*z[1:,0]
    A[1:nm+1,1:nm+1]=z[1:,1:]+np.diag(rw+s*mass+mass*omega**2/s)
    A[-1,0]=bl;A[-1,-1]=ze
    q=np.linalg.solve(A,rhs);v=q[0];u=q[1:-1];current=q[-1]
    flows=np.r_[sd*v,-u];press=z@flows
    Pgas=float(np.real(np.vdot(flows,press)))
    Pwall=float(np.sum(rw*abs(u)**2));Pin=float(np.real(current))
    power_rel=abs(Pin-re*abs(current)**2-rm*abs(v)**2-Pwall-Pgas)/max(Pin,1e-12)
    if power_rel>1e-9 or Pgas<-1e-8:
        raise AssertionError(('energy',power_rel,Pgas,limit,f,E,zeta))
    defmax=float(np.sum(abs(u)/w))  # triangle upper bound, m/V
    return dict(gain_db=float(20*np.log10(abs(v/vrig))),
       velocity_m_s_per_V=float(abs(v)),
       rigid_velocity_m_s_per_V=float(abs(vrig)),
       power_error_rel=float(power_rel),
       acoustic_dissipation_W_per_V2=Pgas,
       panel_dissipation_W_per_V2=Pwall,
       panel_deflection_upper_bound_mm_per_V=float(defmax*1000),
       input_power_W_per_V2=Pin)

def experiment():
    c=json.loads(C.read_text());data=json.loads(P.read_text())['drivers']
    dc={z['model']['name']:z['model'] for z in data}
    drivers=[dc[z] for z in c['drivers']]
    rows=[];ctrl=[]
    for setting in c['grid_settings']:
        g=grid(c,setting['large'],setting['small'],setting['step_m'])
        nm_max=max(c['panel_mode_cutoffs']);S,desc=modes(g,c,nm_max)
        src=np.column_stack([source(g,d['sd_cm2']*1e-4,c['source_x_m'],c['source_z_m'])
                             for d in drivers])
        assert all(abs(src.sum(axis=0)-1)<1e-7)
        for f in setting['frequency_hz']:
            Z,res,rec=port(g,c,f,src,S)
            ctrl.append(dict(setting=setting['name'],f_hz=f,n=int(g['n']),
                air_l=float(g['vol'].sum()*1000),reciprocity_rel=rec,
                FV_residual_rel=res))
            for j,driver in enumerate(drivers):
                # The first three port columns correspond to three source
                # footprints; choose the proper one for each driver.
                col=[j]+list(range(3, Z.shape[0]))
                Zj=Z[np.ix_(col,col)]
                for E,zeta in [(2.1e9,.03),(1.5e9,.03),(3e9,.03),
                                (2.1e9,.01),(2.1e9,.06)]:
                    for limit in c['panel_mode_cutoffs']:
                        rr=coupled(Zj,driver,c,desc,limit,f,E,zeta)
                        rows.append(dict(setting=setting['name'],f_hz=f,
                            candidate=driver['name'],E_pa=E,zeta=zeta,
                            modes_per_plate=limit**2,**rr))
            print(setting['name'],f,'n',g['n'],'FV residual',round(res,13),flush=True)
    assert len(rows)==sum(len(x['frequency_hz']) for x in c['grid_settings'])*len(drivers)*5*len(c['panel_mode_cutoffs'])
    with (O/'p21h_kampania.csv').open('w',newline='') as h:
        wr=csv.DictWriter(h,fieldnames=rows[0]);wr.writeheader();wr.writerows(rows)
    (O/'p21h_kontrole.json').write_text(json.dumps(ctrl,indent=2)+'\n')
    groups=[]
    for state in (x['name'] for x in c['grid_settings']):
        for d in drivers:
            for E,zeta in [(2.1e9,.03),(1.5e9,.03),(3e9,.03),
                           (2.1e9,.01),(2.1e9,.06)]:
                subset=[r for r in rows if r['setting']==state and
                    r['candidate']==d['name'] and r['E_pa']==E and
                    r['zeta']==zeta and r['modes_per_plate']==9]
                groups.append(dict(setting=state,candidate=d['name'],
                    E_pa=E,zeta=zeta,
                    min_gain_db=float(min(r['gain_db'] for r in subset)),
                    max_gain_db=float(max(r['gain_db'] for r in subset)),
                    max_deflection_bound_mm_per_V=float(max(r['panel_deflection_upper_bound_mm_per_V'] for r in subset))))
    limits=[]
    for r in rows:
        if (r['E_pa']==2.1e9 and r['zeta']==.03 and r['setting']=='120_refined'
             and r['candidate']==drivers[0]['name']):
            peer=next(q for q in rows if q['E_pa']==2.1e9 and
                q['zeta']==.03 and q['setting']==r['setting'] and
                q['candidate']==r['candidate'] and q['f_hz']==r['f_hz']
                and q['modes_per_plate']==9)
            limits.append(dict(f_hz=r['f_hz'],modes_per_plate=r['modes_per_plate'],
                vs_3x3_db=float(r['gain_db']-peer['gain_db'])))
    summary=dict(n_rows=len(rows),n_factorizations=len(ctrl),
        max_FV_residual=max(r['FV_residual_rel'] for r in ctrl),
        max_reciprocity_residual=max(r['reciprocity_rel'] for r in ctrl),
        max_power_error=max(r['power_error_rel'] for r in rows),
        neg_acoustic_power=sum(r['acoustic_dissipation_W_per_V2']<-1e-8 for r in rows),
        groups=groups,limits=limits,geometric_scope=c['scope'],caveats=c['caveats'])
    (O/'p21h_podsumowanie.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
    (O/'p21h_manifest.json').write_text(json.dumps({
        'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,
        'sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in [C,P,Path(__file__),O/'p21h_kampania.csv',
                      O/'p21h_kontrole.json',O/'p21h_podsumowanie.json']}},indent=2)+'\n')
    print('SUMMARY',json.dumps({k:v for k,v in summary.items() if k not in ['groups','limits']},indent=2),flush=True)

if __name__=='__main__':experiment()
