"""P21G: FV spatial cavity with P20D rigid AABB obstacles + compliant wall ports.

Run at repo root:
  OPENBLAS_NUM_THREADS=1 python skrypty/p21g_fv_podatne_panele.py
Small-signal conditional research; not an integrated structural FEM nor actual product data.
Uses frozen geometric boxes and published driver T/S; 1 V RMS harmonic drive.
"""
import csv, hashlib, json, platform
from pathlib import Path
import numpy as np
import scipy
from scipy.integrate import quad
from scipy.sparse import coo_matrix, diags
from scipy.sparse.linalg import splu

ROOT=Path(__file__).resolve().parents[1]
CFG=ROOT/'dane/konfiguracje/p21g_fv_panele.json'
GEOM=ROOT/'dane/konfiguracje/p18e_geometria_zamrozona.json'
P20=ROOT/'dane/konfiguracje/p20d_geometria.json'
POOL=ROOT/'dane/przetworniki/pula_rozszerzona.json'
OUT=ROOT/'wyniki'

def axis(length, cuts, step):
    knots=sorted(set([0.,float(length)]+[round(float(e),9) for e in cuts if 0<e<length]))
    a=[]
    for x,y in zip(knots,knots[1:]):
        a.extend(np.linspace(x,y,int(np.ceil((y-x)/step))+1)[:-1])
    return np.asarray(a+[length])

def obstacles(large,small,proxy,geo,p20):
    L=np.asarray(geo['inside_mm'])/1000
    braces=[np.asarray(x,dtype=float)/1000 for x in geo['braces_mm']]
    # Original P20D modules: 4 small pieces then 16 large ones,
    # geometry from frozen box and module centre arrays.
    smallboxes=[]
    for x,z in p20['module_small_centres_xz_mm']:
        w,h=p20['module_small_mm'][0]/2,p20['module_small_mm'][2]/2
        y0,y1=p20['module_small_y_interval_mm']
        smallboxes.append(np.array([[x-w,y0,z-h],[x+w,y1,z+h]])/1000)
    xfirst=p20['ring_x_start_mm']+p20['ring_thickness_mm']
    split=(xfirst+L[0]*1000)/2-p20['ring_thickness_mm']/2
    xs=[(xfirst+split)/2,(split+p20['ring_thickness_mm']+L[0]*1000)/2]
    centers=[(x,y,z) for x in xs[::-1]
             for y in p20['module_centres_y_mm']
             for z in p20['module_centres_z_mm']]
    size=np.asarray(p20['module_mm'],float)
    bigboxes=[np.array([np.asarray(k)-size/2,np.asarray(k)+size/2])/1000 for k in centers]
    if proxy=='A': motor=np.array([[84,40,128],[334,140,328]],float)/1000
    elif proxy=='B':motor=np.array([[109,20,128],[309,145,328]],float)/1000
    else:raise ValueError(proxy)
    boxes=braces+smallboxes[:small]+bigboxes[:large]+[motor]
    return L,boxes

def grid(c,large,small,step,proxy='A'):
    geo=json.loads(GEOM.read_text());p20=json.loads(P20.read_text())
    L,bb=obstacles(large,small,proxy,geo,p20);W,D,H=L
    xe=axis(W,[v for b in bb for v in b[:,0]],step)
    ye=axis(D,[v for b in bb for v in b[:,1]]+[D-c['fill_depth_m']],step)
    ze=axis(H,[v for b in bb for v in b[:,2]],step)
    dx,dy,dz=map(np.diff,(xe,ye,ze))
    xc,yc,zc=[(edges[:-1]+edges[1:])/2 for edges in (xe,ye,ze)]
    X,Y,Z=np.meshgrid(xc,yc,zc,indexing='ij');solid=np.zeros(X.shape,bool)
    for box in bb:
        solid|=((X>box[0,0])&(X<box[1,0])&
                (Y>box[0,1])&(Y<box[1,1])&
                (Z>box[0,2])&(Z<box[1,2]))
    ids=np.full(X.shape,-1,int);ids[~solid]=np.arange((~solid).sum())
    volfull=dx[:,None,None]*dy[None,:,None]*dz[None,None,:]
    vol=volfull[~solid]
    fill=(Y>D-c['fill_depth_m'])[~solid]
    assert min(vol)>0
    aa=[];bb2=[];face=[];dleft=[];dright=[]
    for direction,width in enumerate((dx,dy,dz)):
        index=[slice(None)]*3; index[direction]=slice(None,-1)
        nxt=list(index);nxt[direction]=slice(1,None)
        il,ir=ids[tuple(index)],ids[tuple(nxt)]
        valid=(il>=0)&(ir>=0)
        d=np.broadcast_to(width.reshape([len(width) if i==direction else 1 for i in range(3)]),ids.shape)
        faces=volfull/d
        aa.extend(il[valid]);bb2.extend(ir[valid])
        face.extend(faces[tuple(index)][valid])
        dleft.extend(d[tuple(index)][valid]/2)
        dright.extend(d[tuple(nxt)][valid]/2)
    n=int((~solid).sum())
    sf=np.zeros((n,2))
    # Effective uniform outward wall motion per fluid-exposed top/bottom face.
    for j,k in enumerate((0,-1)):
        for ix in range(len(dx)):
            for iy in range(len(dy)):
                idx=ids[ix,iy,k]
                if idx>=0:sf[idx,j]=dx[ix]*dy[iy]
    area=sf.sum(axis=0);assert all(area>0)
    sf/=area[None,:]
    return dict(n=n,xe=xe,ye=ye,ze=ze,ids=ids,vol=vol,fill=fill,
                a=np.asarray(aa,int),b=np.asarray(bb2,int),face=np.asarray(face),
                da=np.asarray(dleft),db=np.asarray(dright),wall=sf,
                wall_area=area.tolist(),lengths=L.tolist(),air_l=vol.sum()*1000,
                count_solid=int(solid.sum()),step=step)

def source(g,area,cx,cz):
    xe,ze,ids=g['xe'],g['ze'],g['ids']
    R=np.sqrt(area/np.pi)
    assert cx-R>0 and cx+R<xe[-1] and cz-R>0 and cz+R<ze[-1]
    out=np.zeros(g['n'])
    for j in range(len(xe)-1):
        lo=max(xe[j]-cx,-R);hi=min(xe[j+1]-cx,R)
        if lo>=hi:continue
        for k in range(len(ze)-1):
            def chord(x):
                dy=np.sqrt(max(0.,R*R-x*x))
                return max(0.,min(ze[k+1]-cz,dy)-max(ze[k]-cz,-dy))
            a=quad(chord,lo,hi,epsabs=1e-12,limit=80)[0]
            if a>0:
                idx=ids[j,0,k]
                assert idx>=0, 'source intersects solid'
                out[idx]=a/area
    assert abs(out.sum()-1)<1e-8
    return out

def driver_ts(d,c):
    rho,sound=c['rho_kg_m3'],c['sound_m_s']
    sd=d['sd_cm2']*1e-4
    cms=d['vas_l']*.001/(rho*sound**2*sd**2)
    w0=2*np.pi*d['fs_hz'];m=1/(cms*w0*w0)
    return (sd,cms,m,w0*m/d['qms'],np.sqrt(w0*m*d['re_ohm']/d['qes']),
            d['re_ohm'],d['le_mh']*.001)

def fv_port(g,c,f,drivers):
    omega=2*np.pi*f
    rho=c['rho_kg_m3'];K0=rho*c['sound_m_s']**2
    bulk=np.full(g['n'],K0,complex)
    bulk[g['fill']]=K0*(1+1j*c['fill_bulk_loss_tangent'])
    conduct=g['face']/(rho*(g['da']+g['db']))
    a,b=g['a'],g['b']
    mat=coo_matrix((np.r_[conduct,conduct,-conduct,-conduct],
         (np.r_[a,b,a,b],np.r_[a,b,b,a])),shape=(g['n'],g['n'])).tocsc()
    mat=mat-diags(omega**2*g['vol']/bulk,format='csc')
    S=np.column_stack([source(g,d['sd_cm2']*1e-4,c['source_x_m'],c['source_z_m'])
                       for d in drivers]+[g['wall'][:,0],g['wall'][:,1]])
    lu=splu(mat);P=lu.solve((1j*omega*S).astype(complex))
    residual=np.linalg.norm(mat@P-1j*omega*S)/np.linalg.norm(1j*omega*S)
    Z=S.T@P
    reciprocity=np.max(abs(Z-Z.T))/max(np.max(abs(Z)),1e-40)
    assert residual<1e-8 and reciprocity<2e-10,(residual,reciprocity)
    return Z,residual,reciprocity

def coupled(Z,c,d,f,scale,driver_index):
    w=2*np.pi*f;s=1j*w
    sd,cms,m,rm,bl,re,le=driver_ts(d,c)
    # Ports in FV matrix: [C02,C11,C06,top,bottom]
    indices=[driver_index,3,4];zp=Z[np.ix_(indices,indices)]
    zmech=rm+s*m+1/(s*cms);ze=re+s*le
    A=np.zeros((4,4),complex);rhs=np.array([0,0,0,1],complex)
    A[0,0]=zmech+sd**2*zp[0,0];A[0,1:3]=-sd*zp[0,1:3];A[0,3]=-bl
    damp=[]
    for j in range(2):
        stiff=1/(scale*c['panel_compliance_single_m3_pa'])
        fw=c['panel_modes_hz'][j];mass=stiff/(2*np.pi*fw)**2
        rw=2*c['panel_damping_zeta']*np.sqrt(stiff*mass)
        damp.append(rw)
        A[j+1,0]=-sd*zp[j+1,0]
        A[j+1,1:3]=zp[j+1,1:3]
        A[j+1,j+1]+=stiff/s+rw+s*mass
    A[3,0]=bl;A[3,3]=ze
    v,q1,q2,i=np.linalg.solve(A,rhs)
    Q=np.array([sd*v,-q1,-q2])
    pa=zp@Q
    pg=float(np.real(np.vdot(Q,pa)))
    copper=float(re*abs(i)**2);mechanic=float(rm*abs(v)**2)
    pw=float(damp[0]*abs(q1)**2+damp[1]*abs(q2)**2)
    pin=float(np.real(i))
    energy_err=abs(pin-copper-mechanic-pw-pg)/max(abs(pin),1e-14)
    if energy_err>5e-9 or pg< -1e-8:
        raise AssertionError((energy_err,pg,f,scale,driver_index))
    return dict(velocity_m_s_per_V=float(abs(v)),current_A_per_V=float(abs(i)),
        acoustic_diss_W_per_V2=pg,panel_diss_W_per_V2=pw,
        input_power_W_per_V2=pin,power_error=energy_err,
        panel_flow_m3_s_per_V=float(np.hypot(abs(q1),abs(q2))))

def rigid(Z,c,d,f,index):
    sd,cms,m,rm,bl,re,le=driver_ts(d,c);w=2*np.pi*f;s=1j*w
    zm=rm+s*m+1/(s*cms)+sd**2*Z[index,index]
    ze=re+s*le
    i=1/(ze+bl*bl/zm)
    v=bl*i/zm
    return float(abs(v))

def main():
    c=json.loads(CFG.read_text());catalog=json.loads(POOL.read_text())['drivers']
    models={a['model']['name']:a['model'] for a in catalog}
    drivers=[models[name] for name in c['drivers']]
    allrows=[];checks=[];gen={}
    for setting in c['grid_settings']:
        g=grid(c,setting['large'],setting['small'],setting['step_m'])
        state=setting['name']
        for f in setting['frequency_hz']:
            Z,res,rec=fv_port(g,c,f,drivers)
            check={'configuration':state,'f_hz':f,'step_m':g['step'],
                 'air_l':float(g['air_l']),'dof':g['n'],
                 'source_residual':float(res),'reciprocity_residual':float(rec),
                 'wall_area_m2':g['wall_area']}
            checks.append(check)
            for j,name in enumerate(c['drivers']):
                baseline=rigid(Z,c,drivers[j],f,j)
                for scale in c['panel_compliance_scales']:
                    if scale==0:
                        result=dict(velocity_m_s_per_V=baseline,
                             current_A_per_V=0.,acoustic_diss_W_per_V2=0.,
                             panel_diss_W_per_V2=0.,input_power_W_per_V2=0.,
                             power_error=0.,panel_flow_m3_s_per_V=0.)
                    else: result=coupled(Z,c,drivers[j],f,scale,j)
                    allrows.append(dict(configuration=state,step_m=g['step'],dof=g['n'],
                        candidate=name,f_hz=f,scale=scale,
                        delta_vs_rigid_db=float(20*np.log10(result['velocity_m_s_per_V']/baseline)),
                        **result))
    OUT.mkdir(exist_ok=True)
    with (OUT/'p21g_porownania.csv').open('w',newline='') as h:
        writer=csv.DictWriter(h,fieldnames=allrows[0]);writer.writeheader();writer.writerows(allrows)
    (OUT/'p21g_kontrole.json').write_text(json.dumps(checks,indent=2)+'\n')
    report={'cases':len(allrows),'fluid_factorizations':len(checks),
      'max_reciprocity_residual':max(q['reciprocity_residual'] for q in checks),
      'max_FV_linear_residual':max(q['source_residual'] for q in checks),
      'max_coupled_power_error':max(q['power_error'] for q in allrows),
      'conditions':checks,
      'groups':[], 'scope':c['scope']}
    for state in sorted(set(z['configuration'] for z in allrows)):
      for name in c['drivers']:
        for scale in c['panel_compliance_scales'][1:]:
          subset=[z for z in allrows if z['configuration']==state and
                  z['candidate']==name and z['scale']==scale]
          report['groups'].append(dict(config=state,candidate=name,scale=scale,
             min_delta_db=min(z['delta_vs_rigid_db'] for z in subset),
             max_delta_db=max(z['delta_vs_rigid_db'] for z in subset),
             n=len(subset)))
    (OUT/'p21g_podsumowanie.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    files=[CFG,GEOM,P20,POOL,Path(__file__),OUT/'p21g_porownania.csv',OUT/'p21g_kontrole.json',OUT/'p21g_podsumowanie.json']
    (OUT/'p21g_manifest.json').write_text(json.dumps({
        'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,
        'sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}},indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='conditions'},indent=2))
if __name__=='__main__':main()
