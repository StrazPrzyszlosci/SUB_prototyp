"""P21D: same research geometry as P20D; rigid frames/insert envelopes.
Two equal-volume surrogate motors, NOT measured basket geometry. SI FV.
"""
from pathlib import Path
import json,csv,platform
import numpy as np
import scipy
from scipy.integrate import quad
from scipy.sparse import coo_matrix,diags
from scipy.sparse.linalg import spsolve
from model_wypelnienia import CircularPores
from komora_warstwowa_P21C2 import MED,port
from analiza_rozszerzenia_SB import candidates
from geometria_zintegrowana_P20D import geometry
ROOT=Path(__file__).resolve().parents[1];O=ROOT/'wyniki'
W,H,D=.956,.456,.374
PHI=1-20/1380
CID='C02'; CURRENT=[]
def boxes(count):return CURRENT

def set_obstacles(large,small,proxy):
 global CURRENT
 L,br,mods,mat=geometry(1000,440)
 selected=mods[:small]+mods[4:4+large]
 if proxy=='A':selected.append(np.array([[84,40,128],[334,140,328]]))
 if proxy=='B':selected.append(np.array([[109,20,128],[309,145,328]]))
 CURRENT=[tuple(v for j in range(3) for v in [b[0,j]/1000,b[1,j]/1000]) for b in br+selected]
def axis(L,edges,step):
 knots=sorted(set([0.,L]+[round(e,9) for e in edges if 0<e<L]));a=[]
 for x,y in zip(knots,knots[1:]):a.extend(np.linspace(x,y,int(np.ceil((y-x)/step))+1)[:-1])
 return np.array(a+[L])
def build(count,step,fill):
 bb=boxes(count);xe=axis(W,[v for b in bb for v in b[:2]],step);ye=axis(D,[v for b in bb for v in b[2:4]]+([D-.05] if fill else []),step);ze=axis(H,[v for b in bb for v in b[4:]],step)
 dx,dy,dz=map(np.diff,(xe,ye,ze));xc=(xe[:-1]+xe[1:])/2;yc=(ye[:-1]+ye[1:])/2;zc=(ze[:-1]+ze[1:])/2
 X,Y,Z=np.meshgrid(xc,yc,zc,indexing='ij');solid=np.zeros(X.shape,bool)
 for b in bb:solid|=(X>b[0])&(X<b[1])&(Y>b[2])&(Y<b[3])&(Z>b[4])&(Z<b[5])
 ids=np.full(X.shape,-1);ids[~solid]=np.arange((~solid).sum());vol=(dx[:,None,None]*dy[None,:,None]*dz[None,None,:])[~solid]
 flags=(Y>D-.05)[~solid] if fill else np.zeros(len(vol),bool)
 A=[];B=[];area=[];da=[];db=[]
 lengths=[dx,dy,dz]
 for axisidx in range(3):
  sl=[slice(None)]*3;sr=sl.copy();sl[axisidx]=slice(None,-1);sr[axisidx]=slice(1,None);sl=tuple(sl);sr=tuple(sr)
  ia,ib=ids[sl],ids[sr];ok=(ia>=0)&(ib>=0)
  dd=np.broadcast_to(lengths[axisidx].reshape([len(lengths[axisidx]) if j==axisidx else 1 for j in range(3)]),ids.shape)
  fullvol=dx[:,None,None]*dy[None,:,None]*dz[None,None,:];face=fullvol/dd
  A.extend(ia[ok]);B.extend(ib[ok]);area.extend(face[sl][ok]);da.extend(dd[sl][ok]/2);db.extend(dd[sr][ok]/2)
 A=np.array(A);B=np.array(B);area=np.array(area);da=np.array(da);db=np.array(db)
 d={cid:d for cid,pid,d,c in candidates()}[CID];rad=np.sqrt(d.sd/np.pi);cx=209/1000;cz=H/2;source=np.zeros(len(vol));correction=0
 for i in range(len(dx)):
  for k in range(len(dz)):
   l=max(xe[i]-cx,-rad);r=min(xe[i+1]-cx,rad)
   if l>=r:continue
   def chord(x):
    half=np.sqrt(max(0,rad*rad-x*x));return max(0,min(ze[k+1]-cz,half)-max(ze[k]-cz,-half))
   ar=quad(chord,l,r,epsabs=1e-12,points=[0] if l<0<r else None,limit=150)[0]
   if ar>0:
    ix=ids[i,0,k];assert ix>=0;source[ix]=ar/d.sd
    correction+=(ar/d.sd)**2*dy[0]/(2*dx[i]*dz[k])
 assert abs(sum(source)-1)<1e-7
 expected=W*H*D-sum(np.prod(np.array(b)[[1,3,5]]-np.array(b)[[0,2,4]]) for b in bb)
 assert abs(sum(vol)-expected)<1e-10
 return dict(A=A,B=B,area=area,da=da,db=db,vol=vol,flags=flags,source=source,correction=correction,source_area_error=float(abs(sum(source)-1)),n=len(vol))
def solve(g,f):
 om=2*np.pi*f;rho=np.full(g['n'],MED.rho,complex);bulk=np.full(g['n'],MED.gamma*MED.p0_pa,complex)
 rp,kp=CircularPores(.0002,PHI,'rigid',20).equivalent_properties(np.array([f]),MED);rho[g['flags']]=rp[0];bulk[g['flags']]=kp[0]
 a,b=g['A'],g['B'];conduct=g['area']/(rho[a]*g['da']+rho[b]*g['db'])
 K=coo_matrix((np.r_[conduct,conduct,-conduct,-conduct],(np.r_[a,b,a,b],np.r_[a,b,b,a])),shape=(g['n'],g['n'])).tocsc()-diags(om*om*g['vol']/bulk)
 rhs=1j*om*g['source'];p=spsolve(K,rhs)
 residual=np.linalg.norm(K@p-rhs)/np.linalg.norm(rhs)
 # All source faces are pure air; face correction uses source cell mean velocity.
 zp=g['source']@p+1j*om*MED.rho*g['correction']
 assert residual<1e-7 and zp.real>-1e-6
 return complex(zp),float(residual)

def main():
 global CID,CURRENT
 pool={cid:d for cid,pid,d,c in candidates()}; rows=[]; coupled=[];controls=[]
 for name,n,k in [('150',2,0),('120',11,1),('100',16,3)]:
  for proxy,step in [('A',.05),('A',.035),('B',.035)]:
   for cid in (['C02','C11','C06'] if (proxy,step)==('A',.035) else ['C02']):
    CID=cid;set_obstacles(n,k,proxy);g=build(0,step,True)
    for f in [20.,40.,80.]:
     z,res=solve(g,f);d=pool[cid];om=2*np.pi*f
     air=sum(g['vol'])*1000; solid_fill=sum(g['vol'][g['flags']])*(1-PHI)*1000
     r=dict(configuration=name,large=n,small=k,proxy=proxy,step_m=step,candidate=cid,
            f_hz=f,dof=g['n'],envelope_air_l=air,porous_solid_l=solid_fill,
            Z_real=z.real,Z_imag=z.imag,residual=res)
     rows.append(r)
     if proxy=='A' and step==.035:
      # Same effective Mms convention as 052; finite rear air is not silently added twice.
      for mass_side in [0,1]:
       radius=np.sqrt(d.sd/np.pi);refmass=8*MED.rho*radius**3/3
       zm=d.rms+1j*om*(d.mms-mass_side*refmass)+1/(1j*om*d.cms)+d.sd*d.sd*z
       ze=d.re_ohm+1j*om*d.le_mh*.001;iv=1/(ze+d.bl*d.bl/zm);vv=d.bl*iv/zm
       z0=-1j*MED.gamma*MED.p0_pa/(om*(air/1000))
       zm0=d.rms+1j*om*d.mms+1/(1j*om*d.cms)+d.sd*d.sd*z0
       i0=1/(ze+d.bl*d.bl/zm0);v0=d.bl*i0/zm0
       loss=d.re_ohm*abs(iv)**2+zm.real*abs(vv)**2
       # Real input complex power at 1 Vrms: mechanical damping includes rear load.
       assert abs(iv.real-loss)<1e-9 and z.real>=-1e-6
       coupled.append(dict(configuration=name,candidate=cid,f_hz=f,mass_convention=mass_side,
            I_per_Vrms=abs(iv),X_mm_per_Vrms=abs(vv)/om*1000,
            acceleration_vs_0D_dB=20*np.log10(abs(vv/v0)),
            rear_mass_reference_g=refmass*1000,input_power_balance_relative=abs(iv.real-loss)/max(loss,1e-12)))
    print(name,proxy,step,cid,g['n'],flush=True)
    (O/'p21d_checkpoint.json').write_text(json.dumps(dict(rows=rows,coupled=coupled),indent=2))
 # Independent separated modal solution, no frames, same source centre and rear fill.
 CURRENT=[];CID='C02';driver=pool[CID]
 for step in [.05,.035]:
  g=build(0,step,True)
  for f in [20.,80.]:
   z,res=solve(g,f);exact=port(W,H,[(D-.05,None),(.05,CircularPores(.0002,PHI,'rigid',20))],(.209,H/2),driver.sd,[f],200)[0]
   controls.append(dict(test='empty_modal_reference',step_m=step,f_hz=f,dof=g['n'],relative_error=abs(z/exact-1)))
 # Low frequency conservation, pure air. One witness each real regulation geometry.
 for name,n,k in [('150',2,0),('120',11,1),('100',16,3)]:
  set_obstacles(n,k,'A');g=build(0,.035,False);f=.2;z,res=solve(g,f)
  expected=-1j*MED.gamma*MED.p0_pa/(2*np.pi*f*sum(g['vol']))
  controls.append(dict(test='uniform_compliance_limit',configuration=name,f_hz=f,relative_error=abs(z/expected-1)))
 convergence=[];shape=[]
 for r in rows:
  if r['candidate']=='C02' and r['proxy']=='A' and r['step_m']==.035:
   z=complex(r['Z_real'],r['Z_imag'])
   coarse=next(q for q in rows if q['configuration']==r['configuration'] and q['candidate']=='C02' and q['proxy']=='A' and q['step_m']==.05 and q['f_hz']==r['f_hz'])
   zb=next(q for q in rows if q['configuration']==r['configuration'] and q['candidate']=='C02' and q['proxy']=='B' and q['f_hz']==r['f_hz'])
   convergence.append(dict(configuration=r['configuration'],f_hz=r['f_hz'],relative_change=abs(complex(coarse['Z_real'],coarse['Z_imag'])/z-1)))
   shape.append(dict(configuration=r['configuration'],f_hz=r['f_hz'],relative_change=abs(complex(zb['Z_real'],zb['Z_imag'])/z-1)))
 result=dict(scope='Rigid research cabinet 1000x440x500; same brace/insert geometry P20D. Surrogate motor5l, porous scenario, no elastic coupling or measured basket.',
   rows=rows,coupled=coupled,controls=controls,convergence=convergence,motor_shape_sensitivity=shape,
   software=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__))
 (O/'p21d_wyniki.json').write_text(json.dumps(result,indent=2))
 for filename,records in [('p21d_port.csv',rows),('p21d_naped.csv',coupled)]:
  with (O/filename).open('w') as fh:
   w=csv.DictWriter(fh,fieldnames=records[0]);w.writeheader();w.writerows(records)
 print('DONE',len(rows),len(coupled),max(c['relative_change'] for c in convergence),flush=True)
if __name__=='__main__':main()
