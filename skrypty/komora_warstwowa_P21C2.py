"""Separable 3D modal port: circular piston, full cross-section porous layers.
Rigid rectangular cavity; exact depth transfer for each transverse mode.
No claim that full cross-section layer equals lining five walls.
"""
import numpy as np
from scipy.linalg import solve_banded
from membrana_kolowa_P21C1 import disk_coeff
from model_wypelnienia import CircularPores
from model_gazu import Medium
MED=Medium.legacy()
def modal_impedances(w,h,layers,f,N):
 nx,nz=np.meshgrid(np.arange(N+1),np.arange(N+1),indexing='ij');kt2=(np.pi*nx/w)**2+(np.pi*nz/h)**2
 omega=2*np.pi*f;load=None
 for length,material in reversed(layers):
  if length<=0:continue
  rho,bulk=(MED.rho,MED.gamma*MED.p0_pa) if material is None else [v[0] for v in material.equivalent_properties(np.array([f]),MED)]
  q=np.sqrt(omega**2*rho/bulk-kt2+0j);zc=omega*rho/q;t=np.tan(q*length)
  load=-1j*zc/t if load is None else (load+1j*zc*t)/(1+1j*load*t/zc)
 return nx,nz,load

def port(w,h,layers,center,area,freq,N=100):
 a=np.sqrt(area/np.pi);result=[]
 for f in freq:
  nx,nz,z=modal_impedances(w,h,layers,f,N)
  weights=2.**((nx>0).astype(int)+(nz>0).astype(int))*disk_coeff(nx,nz,w,h,*center,a)**2
  result.append(np.sum(weights*z)/(w*h))
 return np.array(result)

def independent_mode_ladder(w,h,layers,f,n,l,resolution):
 # 1D finite-volume p/v network for ONE transverse cosine mode, not full 3D mesh.
 om=2*np.pi*f;kt2=(np.pi*n/w)**2+(np.pi*l/h)**2;length=sum(a for a,b in layers);zs=[];ys=[]
 for d,mat in layers:
  if d<=0:continue
  cells=max(1,int(np.ceil(resolution*d/length)));dy=d/cells
  rho,bulk=(MED.rho,MED.gamma*MED.p0_pa) if mat is None else [v[0] for v in mat.equivalent_properties(np.array([f]),MED)]
  zs.extend([1j*om*rho*dy]*cells);ys.extend([1j*(om/bulk-kt2/(om*rho))*dy]*cells)
 z=np.array(zs);y=np.array(ys);diag=np.zeros(len(z)+1,complex);diag[:-1]+=y/2;diag[1:]+=y/2
 diag[:-1]+=1/z;diag[1:]+=1/z;ab=np.zeros((3,len(diag)),complex);ab[1]=diag;ab[0,1:]=-1/z;ab[2,:-1]=-1/z
 rhs=np.zeros(len(diag),complex);rhs[0]=1
 return solve_banded((1,1),ab,rhs)[0]