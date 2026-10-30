"""Cell-centered FV heterogeneous Helmholtz, conforming rectangular obstacles.
Rigid sealed module envelopes, no internal gas counted; no driver basket.
Pressure / volume-flow port. Source pressure reconstructed to boundary.
"""
from pathlib import Path
import json
import numpy as np
from scipy.integrate import quad
from scipy.sparse import coo_matrix,diags
from scipy.sparse.linalg import spsolve
from model_wypelnienia import CircularPores
from komora_warstwowa_P21C2 import MED,port
from analiza_rozszerzenia_SB import candidates
ROOT=Path(__file__).resolve().parents[1];O=ROOT/'wyniki'
W,H,D=.836,.456,.414

def boxes(count):
 # Pack deep layer first, then near layer; 2 columns, 4 rows per layer.
 out=[]
 for yc in [.275,.095]:
  for zc in [.068,.178,.288,.398]:
   for xc in [.53,.72]:out.append((xc-.09,xc+.09,yc-.085,yc+.085,zc-.05,zc+.05))
 return out[:count]
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
 d={cid:d for cid,pid,d,c in candidates()}['C02'];rad=np.sqrt(d.sd/np.pi);cx=W/4;cz=H/2;source=np.zeros(len(vol));correction=0
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
 expected=W*H*D-count*.18*.17*.1
 assert abs(sum(vol)-expected)<1e-10
 return dict(A=A,B=B,area=area,da=da,db=db,vol=vol,flags=flags,source=source,correction=correction,source_area_error=float(abs(sum(source)-1)),n=len(vol))
def solve(g,f):
 om=2*np.pi*f;rho=np.full(g['n'],MED.rho,complex);bulk=np.full(g['n'],MED.gamma*MED.p0_pa,complex)
 rp,kp=CircularPores(.0002,.98,'rigid',20).equivalent_properties(np.array([f]),MED);rho[g['flags']]=rp[0];bulk[g['flags']]=kp[0]
 a,b=g['A'],g['B'];conduct=g['area']/(rho[a]*g['da']+rho[b]*g['db'])
 K=coo_matrix((np.r_[conduct,conduct,-conduct,-conduct],(np.r_[a,b,a,b],np.r_[a,b,b,a])),shape=(g['n'],g['n'])).tocsc()-diags(om*om*g['vol']/bulk)
 rhs=1j*om*g['source'];p=spsolve(K,rhs)
 residual=np.linalg.norm(K@p-rhs)/np.linalg.norm(rhs)
 # All source faces are pure air; face correction uses source cell mean velocity.
 zp=g['source']@p+1j*om*MED.rho*g['correction']
 assert residual<1e-7 and zp.real>-1e-6
 return complex(zp),float(residual)
def main():
 rows=[]
 for count in [0,10,16]:
  for fill in [False,True]:
   for step in [.04,.025]:
    g=build(count,step,fill)
    for f in [20.,40.,80.]:
     z,res=solve(g,f);r=dict(count=count,fill=fill,step=step,f=f,dof=g['n'],gas_l=sum(g['vol'])*1000,Z_real=z.real,Z_imag=z.imag,residual=res,source_area_error=g['source_area_error']);rows.append(r)
    print(count,fill,step,g['n'],flush=True)
    (O/'p21c3_checkpoint.json').write_text(json.dumps(rows,indent=2))
 # exact matching no-obstacle model, same depth and source.
 d={cid:d for cid,pid,d,c in candidates()}['C02']
 for r in rows:
  if r['count']==0:
   layers=[(D-.05,None),(.05,CircularPores(.0002,.98,'rigid',20))] if r['fill'] else [(D,None)]
   z=port(W,H,layers,(W/4,H/2),d.sd,[r['f']],200)[0];r['empty_modal_relative_error']=float(abs(complex(r['Z_real'],r['Z_imag'])/z-1))
 (O/'p21c3_wyniki.json').write_text(json.dumps(rows,indent=2))
 print('DONE',len(rows),flush=True)
if __name__=='__main__':main()
