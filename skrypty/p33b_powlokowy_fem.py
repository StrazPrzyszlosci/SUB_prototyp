#!/usr/bin/env python3
"""P33B provisional global 6DOF/node Q4 Mindlin shell FEM; NOT qualified CNC.
Membrane/bending 2x2 Gauss; transverse shear 1 point.
Assumed cut-cell opening, joint springs, ring beams and lumped speaker mass.
"""
import numpy as np, math, json, argparse, time
from scipy.sparse import coo_matrix,diags
from scipy.sparse.linalg import spsolve,eigsh
W,D,H=1.020,.425,.5
E=2.1e9;nu=.3;rho=730.;R=.3558/2;cx=.231;cz=.25
def sections(breaks,h):
 a=[breaks[0]]
 for x,y in zip(breaks[:-1],breaks[1:]):
  a.extend(np.linspace(x,y,math.ceil((y-x)/h)+1)[1:])
 return np.asarray(a)
def shell_element(Lx,Ly,t,cut=1):
 K=np.zeros((20,20));corners=np.array([[-1,-1],[1,-1],[1,1],[-1,1]])
 Dm=E*t/(1-nu**2)*np.array([[1,nu,0],[nu,1,0],[0,0,(1-nu)/2]])
 Db=Dm*t*t/12;G=E/(2*(1+nu));Ds=(5/6)*G*t*np.eye(2)
 def ops(xi,eta):
  N=.25*(1+corners[:,0]*xi)*(1+corners[:,1]*eta)
  dx=corners[:,0]*(1+corners[:,1]*eta)/(2*Lx)
  dy=corners[:,1]*(1+corners[:,0]*xi)/(2*Ly)
  bm=np.zeros((3,20));bb=np.zeros((3,20));bs=np.zeros((2,20))
  for i in range(4):
   j=5*i
   bm[0,j]=dx[i];bm[1,j+1]=dy[i];bm[2,j]=dy[i];bm[2,j+1]=dx[i]
   bb[0,j+3]=dx[i];bb[1,j+4]=dy[i];bb[2,j+3]=dy[i];bb[2,j+4]=dx[i]
   bs[0,j+2]=dx[i];bs[0,j+3]=-N[i];bs[1,j+2]=dy[i];bs[1,j+4]=-N[i]
  return bm,bb,bs
 for xi in (-1/math.sqrt(3),1/math.sqrt(3)):
  for eta in (-1/math.sqrt(3),1/math.sqrt(3)):
   a,b,_=ops(xi,eta);K+=(a.T@Dm@a+b.T@Db@b)*Lx*Ly/4
 _,_,bs=ops(0,0);K+=(bs.T@Ds@bs)*Lx*Ly
 return K*cut
def global_mesh(mesh=.1,kTrans=3e7,kRot=1e3,driverMass=15,insertMass=8,brace=True):
 xs=sections([0,.426,.701,W],mesh);ys=sections([0,D],mesh);zs=sections([0,H],mesh)
 faces=[('top',xs,ys,(1,0,0),(0,1,0),H,.022,'xy'),
 ('bottom',xs,ys,(1,0,0),(0,1,0),0,.022,'xy'),
 ('front',xs,zs,(1,0,0),(0,0,1),0,.044,'xz'),
 ('back',xs,zs,(1,0,0),(0,0,1),D,.022,'xz'),
 ('left',ys,zs,(0,1,0),(0,0,1),0,.022,'yz'),
 ('right',ys,zs,(0,1,0),(0,0,1),W,.022,'yz')]
 pts=[];mass=[];rotmass=[];tab={}
 for name,u,v,e1,e2,c,t,typ in faces:
  ids={}
  for i,a in enumerate(u):
   for j,b in enumerate(v):
    p=(a,b,c) if typ=='xy' else ((a,c,b) if typ=='xz' else (c,a,b))
    ix=len(pts);pts.append(p);mass.append(0);rotmass.append(0);ids[i,j]=ix
  tab[name]=dict(node=ids,u=u,v=v,typ=typ)
 n=len(pts);pts=np.asarray(pts);F=np.zeros(6*n);rows=[];cols=[];values=[]
 def add(K,ids):
  for i,ii in enumerate(ids):
   for j,jj in enumerate(ids):
    if K[i,j]:rows.append(ii);cols.append(jj);values.append(K[i,j])
 def link(a,b,k,kr):
  for d in range(6):
   t=k if d<3 else kr
   add(np.array([[t,-t],[-t,t]]),[6*a+d,6*b+d])
 hole=0.
 for name,u,v,e1,e2,c,t,typ in faces:
  e1=np.asarray(e1);e2=np.asarray(e2);nvec=np.cross(e1,e2)
  T=np.zeros((20,24))
  for a in range(4):
   for d in range(3):
    T[5*a,6*a+d]=e1[d];T[5*a+1,6*a+d]=e2[d];T[5*a+2,6*a+d]=nvec[d]
    T[5*a+3,6*a+3+d]=e2[d];T[5*a+4,6*a+3+d]=-e1[d]
  nodes=tab[name]['node']
  for i in range(len(u)-1):
   for j in range(len(v)-1):
    dx=u[i+1]-u[i];dy=v[j+1]-v[j]
    q=[nodes[i,j],nodes[i+1,j],nodes[i+1,j+1],nodes[i,j+1]]
    if name=='front':
     frac=np.mean([((u[i]+(a+.5)*dx/10-cx)**2+(v[j]+(b+.5)*dy/10-cz)**2)>=R**2
                   for a in range(10) for b in range(10)])
     hole+=dx*dy*(1-frac)
    else:frac=1.
    if frac<1e-7:continue
    g=[6*k+d for k in q for d in range(6)]
    add(T.T@shell_element(dx,dy,t,frac)@T,g)
    for k in q:
     mass[k]+=rho*t*dx*dy*frac/4;rotmass[k]+=rho*t**3*dx*dy*frac/48
     ax={'top':2,'bottom':2,'front':1,'back':1,'left':0,'right':0}[name]
     sign={'top':1,'bottom':-1,'front':-1,'back':1,'left':-1,'right':1}[name]
     F[6*k+ax]+=1000*dx*dy*frac*sign/4
  # Weak non-physical drilling regularization.
  for k in nodes.values():
   ids=[6*k+3+d for d in range(3)]
   add(1e-2*E*t**3*np.outer(nvec,nvec),ids)
 from collections import defaultdict
 groups=defaultdict(list)
 for k,p in enumerate(pts):
  iscorner=sum(abs(p[z])<1e-8 or abs(p[z]-[W,D,H][z])<1e-8 for z in range(3))
  if iscorner>=2:groups[tuple(np.round(p,7))].append(k)
 ties=0
 for g in groups.values():
  for q in g[1:]:link(g[0],q,kTrans*mesh,kRot*mesh);ties+=1
 bars=0
 if brace:
  for x in [.426,.701]:
   for face,axisid in [('top',1),('bottom',1),('front',2),('back',2)]:
    candidates=sorted([q for q in tab[face]['node'].values() if abs(pts[q,0]-x)<1e-9],key=lambda k:pts[k,axisid])
    A=.022*(.010 if face=='front' else .022);I=A*.022**2/12
    for a,b in zip(candidates[:-1],candidates[1:]):
     L=np.linalg.norm(pts[b]-pts[a]);axis=(pts[b]-pts[a])/L
     v=np.zeros(12)
     for d in range(3):v[d]=-axis[d];v[6+d]=axis[d]
     ids=[6*a+d for d in range(6)]+[6*b+d for d in range(6)]
     add(E*A/L*np.outer(v,v),ids)
     for ix in range(3):
      dir=np.eye(3)[ix]
      if abs(np.dot(dir,axis))>.99:continue
      rot=np.cross(axis,dir);vv=np.zeros(12)
      for d in range(3):
       vv[d]=-dir[d]/L;vv[6+d]=dir[d]/L
       vv[3+d]=-rot[d]/2;vv[9+d]=-rot[d]/2
      add(12*E*I/L*np.outer(vv,vv),ids)
     mass[a]+=rho*A*L/2;mass[b]+=rho*A*L/2;bars+=1
 rim=[q for q in tab['front']['node'].values()
      if abs(np.linalg.norm(pts[q][[0,2]]-np.array([cx,cz]))-R)<mesh*.85]
 if len(rim)<6:raise RuntimeError('rim nodes too sparse')
 for q in rim:mass[q]+=driverMass/len(rim);F[6*q+1]-=1000*math.pi*R**2/len(rim)
 back=[q for q in tab['back']['node'].values() if pts[q,0]>.45*W]
 for q in back:mass[q]+=insertMass/len(back)
 foot=[q for q in tab['bottom']['node'].values()
       if (abs(pts[q,0])<1e-8 or abs(pts[q,0]-W)<1e-8)
       and (abs(pts[q,1])<1e-8 or abs(pts[q,1]-D)<1e-8)]
 for q in foot:
  for d in range(3):add(np.array([[1.5e6]]),[6*q+d])
 active=np.flatnonzero(np.asarray(mass)>0)
 dofs=np.concatenate([6*active+d for d in range(6)]).reshape(6,-1).T.ravel()
 K=coo_matrix((values,(rows,cols)),shape=(6*n,6*n)).tocsr()[dofs,:][:,dofs].tocsc()
 M=np.zeros(6*len(active))
 for i,q in enumerate(active):
  M[6*i:6*i+3]=mass[q];M[6*i+3:6*i+6]=max(1e-10,rotmass[q])
 load=F[dofs];q=spsolve(K,load);e=float(q@(K@q))
 if not np.isfinite(e) or abs(e-q@load)/max(1,e)>1e-8:raise RuntimeError('energy residual')
 lam=eigsh(K,k=min(18,len(M)-2),M=diags(M),sigma=0,which='LM',tol=1e-5,return_eigenvectors=False)
 f=np.sort(np.sqrt(np.maximum(0,lam))/(2*math.pi))
 maxU=float(np.max(np.linalg.norm(q.reshape(-1,6)[:,:3],axis=1))*1e6)
 return {'mesh':mesh,'joint_trans_N_m2':kTrans,'joint_rot_N':kRot,
  'driverMass':driverMass,'insertMass':insertMass,'braces':brace,
  'node_count':len(active),'ndof':len(M),'joint_ties':ties,'bar_count':bars,
  'hole_area':hole,'expected_hole_area':math.pi*R**2,
  'total_mass_kg':float(sum(mass)),
  'first_freq_Hz':[float(x) for x in f[:12]],
  'max_static_disp_um':maxU,'energy_J':e}
def run(output):
 rows=[]
 for h in (.15,.11,.085):
  for kt,kr in ((3e6,3e2),(3e7,3e3),(3e8,3e4)):
   t=time.monotonic();z=global_mesh(h,kt,kr);rows.append(z)
   print(h,kt,kr,'ndof',z['ndof'],'f1',z['first_freq_Hz'][0],'um',z['max_static_disp_um'],flush=True)
 for m in (0,12,18):
  z=global_mesh(.11,3e7,3e3,driverMass=m,insertMass=8);z['case']='driver_mass';rows.append(z)
 for m in (0,14):
  z=global_mesh(.11,3e7,3e3,driverMass=15,insertMass=m);z['case']='insert_mass';rows.append(z)
 z=global_mesh(.11,3e7,3e3,brace=False);z['case']='without_braces';rows.append(z)
 result={'study':'P33B','date':'2026-10-31','status':'PROVISIONAL Q4 Reissner-Mindlin shell FEM, NOT CNC release','cases':len(rows),'rows':rows,
 'limitations':['1-point transverse shear and weak drilling stiffness require patch/hourglass tests.',
 'Front cut-cells scale square element matrices, not conforming curved mesh.',
 'Elastic translational/rotational glue springs have no peel, strength, time or failure model.',
 'Braces are simplified beam contributions, not solid rings or 3D adhesive geometry.',
 'Speaker, insert mass and 1000 Pa load are hypothetical; actual dynamic gas coupling missing.',
 'Feet modeled with arbitrary 1.5 MN/m translational stiffness.']}
 with open(output,'w') as f:json.dump(result,f,ensure_ascii=False,indent=2)
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',default='wyniki/p33b_shell_15_przypadkow.json')
 args=p.parse_args();run(args.out)
