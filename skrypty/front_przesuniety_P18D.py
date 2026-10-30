"""Offset-hole MITC front, rigid continuous basket attachment, clamped perimeter.
Conditional panel study; no full-frame/splice/contact validation.
"""
import json
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import eigsh,spsolve
from scipy.spatial import cKDTree
from model_frontu_z_otworem_P18B import FrontWithHole,element
from model_plyty_MITC_P18 import PlateMaterial
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Offset(FrontWithHole):
 def __init__(self,W,H,cx,cz,r,t,n,E=2.1e9):
  self.a=W;self.b=H;self.r=r;self.material=PlateMaterial(E,.3,730,t);self.nr=n//2;self.nt=4*n;self.boundary='CCCC';self.outer_circle=False
  corners=np.array([[W-cx,-cz],[W-cx,H-cz],[-cx,H-cz],[-cx,-cz]])
  cuts=np.unwrap(np.arctan2(corners[:,1],corners[:,0]));cuts=np.r_[cuts,cuts[0]+2*np.pi]
  th=np.concatenate([np.linspace(cuts[i],cuts[i+1],n,endpoint=False) for i in range(4)]);c=np.cos(th);s=np.sin(th)
  ro=np.minimum(np.where(c>0,(W-cx)/np.maximum(c,1e-16),cx/np.maximum(-c,1e-16)),np.where(s>0,(H-cz)/np.maximum(s,1e-16),cz/np.maximum(-s,1e-16)))
  radius=r+(ro-r)*np.linspace(0,1,self.nr+1)[:,None];self.xy=np.stack([radius*c,radius*s],axis=-1).reshape(-1,2)
  self.elements=np.array([[i*self.nt+j,(i+1)*self.nt+j,(i+1)*self.nt+(j+1)%self.nt,i*self.nt+(j+1)%self.nt] for i in range(self.nr) for j in range(self.nt)])
  self.dofs=(3*self.elements[:,:,None]+np.arange(3)[None,None,:]).reshape(-1,12);nd=3*len(self.xy);ke=[];me=[];F=np.zeros(nd)
  for nodes,ids in zip(self.elements,self.dofs):
   k,m,f=element(self.xy[nodes],self.material);ke.append(k.ravel());me.append(m.ravel());np.add.at(F,ids,f)
  rows=np.repeat(self.dofs,12,axis=1).ravel();cols=np.tile(self.dofs,(1,12)).ravel()
  self.full_K=sparse.coo_matrix((np.ravel(ke),(rows,cols)),shape=(nd,nd)).tocsr();self.full_M=sparse.coo_matrix((np.ravel(me),(rows,cols)),shape=(nd,nd)).tocsr();self.full_F=F
  self.fixed=np.arange(3*self.nr*self.nt,nd);self.free=np.setdiff1d(np.arange(nd),self.fixed);self.K=self.full_K[self.free][:,self.free];self.M=self.full_M[self.free][:,self.free];self.F=F[self.free]
  self.tree=cKDTree(self.xy[self.elements].mean(axis=1));self.hole_polygon_area_m2=.5*abs(np.sum(self.xy[:self.nt,0]*np.roll(self.xy[:self.nt,1],-1)-self.xy[:self.nt,1]*np.roll(self.xy[:self.nt,0],-1)))
  assert abs(F.sum()+self.hole_polygon_area_m2-W*H)<1e-10

def main():
 rows=[]
 for t in [.022,.033,.044]:
  for frac in [.5,.25]:
   cx=.022+.836*frac
   for n in [12,24,36]:
    p=Offset(.88,.5,cx,.25,.1779,t,n)
    for mass in [10.,15.]:
     K,M,F,T=p.continuous_inner(mass,mass*.1**2);val=eigsh(K,k=3,M=M,sigma=0,which='LM',return_eigenvectors=False)
     # pressure acts on solid front plus cap reaction transmitted through rigid basket
     F[-3]+=p.hole_polygon_area_m2
     u=spsolve(K,F);rows.append(dict(t_m=t,x_fraction=frac,n=n,mass_assumed_kg=mass,first_mode_hz=float(np.sqrt(min(val))/(2*np.pi)),compliance_m3_Pa=float(F@u),basket_displacement_per_Pa_m=float(u[-3]),dof=len(u)))
    print(t,frac,n,flush=True)
    (ROOT/'wyniki/p18d_front.json').write_text(json.dumps(rows,indent=2))
if __name__=='__main__':main()
