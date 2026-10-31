#!/usr/bin/env python3
"""P33C: Q4 Mindlin hourglass audit and analytic plate check.
This is a DIAGNOSTIC; it does not certify the entire P33B enclosure.
Usage: python skrypty/p33c_hourglass_audyt.py --out wyniki/p33c_hourglass_audyt.json
Requires numpy and scipy; loads the exact shell_element from P33B.
"""
import argparse, json, math
import numpy as np
from scipy.sparse import coo_matrix, diags
from scipy.sparse.linalg import eigsh
from p33b_powlokowy_fem import shell_element, E, nu, rho

CORNERS=np.array([[-1,-1],[1,-1],[1,1],[-1,1]])
def shear_matrix(lx,ly,t,xi,eta):
    N=.25*(1+CORNERS[:,0]*xi)*(1+CORNERS[:,1]*eta)
    dx=CORNERS[:,0]*(1+CORNERS[:,1]*eta)/(2*lx)
    dy=CORNERS[:,1]*(1+CORNERS[:,0]*xi)/(2*ly)
    B=np.zeros((2,20))
    for i in range(4):
        j=5*i
        B[0,j+2]=dx[i];B[0,j+3]=-N[i]
        B[1,j+2]=dy[i];B[1,j+4]=-N[i]
    return B.T@B*(5/6)*E/(2*(1+nu))*t

def element(lx,ly,t,gamma):
    red=shear_matrix(lx,ly,t,0,0)*lx*ly
    p=1/math.sqrt(3)
    full=sum((shear_matrix(lx,ly,t,x,y)*lx*ly/4 for x in (-p,p) for y in (-p,p)),np.zeros((20,20)))
    K=shell_element(lx,ly,t)+gamma*(full-red)
    return (K+K.T)/2

def rank_and_rigid(gamma):
    lx,ly,t=.2,.14,.022
    K=element(lx,ly,t,gamma)
    lam=np.linalg.eigvalsh(K)
    cutoff=lam[-1]*1e-9
    rank=int(np.sum(lam>cutoff))
    states=[
        lambda x,y:[1,0,0,0,0],lambda x,y:[0,1,0,0,0],
        lambda x,y:[0,0,1,0,0],lambda x,y:[-y,x,0,0,0],
        lambda x,y:[0,0,x,1,0],lambda x,y:[0,0,y,0,1]]
    errors=[]
    for state in states:
        v=np.array([state(x,y) for x,y in ((0,0),(lx,0),(lx,ly),(0,ly))]).ravel()
        errors.append(abs(float(v@K@v))/(lam[-1]*float(v@v)))
    if max(errors)>1e-10:raise AssertionError('Rigid body patch test')
    return dict(gamma=gamma,null_modes=20-rank,lambda7=float(lam[6]),
                lambda8=float(lam[7]),rigid_energy_rel_max=max(errors))

def plate(nx,ny,gamma):
    L,B,t=.976,.359,.022
    N=5*(nx+1)*(ny+1);mass=np.zeros(N);rr=[];cc=[];vv=[]
    Ke=element(L/nx,B/ny,t,gamma)
    def node(i,j):return i*(ny+1)+j
    area=L*B/(nx*ny)
    for i in range(nx):
        for j in range(ny):
            qq=[node(i,j),node(i+1,j),node(i+1,j+1),node(i,j+1)]
            ids=[5*n+d for n in qq for d in range(5)]
            for a,I in enumerate(ids):
                d=a%5
                mass[I]+=(rho*t*area/4 if d<=2 else rho*t**3*area/48)
                for b,J in enumerate(ids):
                    if Ke[a,b]:rr.append(I);cc.append(J);vv.append(Ke[a,b])
    free=[]
    for i in range(nx+1):
        for j in range(ny+1):
            node_id=node(i,j)
            free.extend([5*node_id+3,5*node_id+4])
            if 0<i<nx and 0<j<ny:free.append(5*node_id+2)
    K=coo_matrix((vv,(rr,cc)),shape=(N,N)).tocsr()[free,:][:,free]
    eigen=eigsh(K,k=4,M=diags(mass[free]),sigma=0,
                which='LM',tol=1e-6,return_eigenvectors=False)
    f=float(np.sqrt(max(0,min(eigen)))/(2*math.pi))
    D=E*t**3/(12*(1-nu**2))
    analytic=math.pi/2*math.sqrt(D/(rho*t))*(1/L**2+1/B**2)
    return dict(nx=nx,ny=ny,gamma=gamma,f1_Hz=f,
                analytical_Kirchhoff_f1_Hz=analytic,
                difference_percent=100*(f/analytic-1))

def run():
    gamma=[0,1e-5,1e-4,.001,.01,.03,.1,1.]
    ranks=[rank_and_rigid(g) for g in gamma]
    if ranks[0]['null_modes']!=8:raise AssertionError('P33B kernel changed; reassess')
    if any(x['null_modes']!=6 for x in ranks[1:]):raise AssertionError('Stabilized rank != 14')
    rows=[plate(nx,ny,g) for g in (0,.001,.01,.03,.1,1)
          for nx,ny in ((8,4),(16,8),(32,12))]
    if not any(x['gamma']==1 and x['nx']==8 and x['f1_Hz']>300 for x in rows):
        raise AssertionError('Shear-locking regression')
    return dict(study='P33C',date='2026-10-31',kind='ELEMENT TEST ONLY',
                element_tests=ranks,plate_tests=rows,
                warnings=['P33B element has 2 additional null modes (hourglass).',
                          'Gamma blend is numerical, not a calibrated material.',
                          'Full integration produces shear locking on coarse grids.',
                          'A successful separate-plate benchmark does NOT validate the full enclosure.',
                          'Previous P33B global displacement/modal estimates require a new, controlled assembly run.'])

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',default='wyniki/p33c_hourglass_audyt.json')
    args=p.parse_args()
    d=run()
    with open(args.out,'w',encoding='utf8') as f:json.dump(d,f,ensure_ascii=False,indent=2)
    print('Audit Q4:',len(d['element_tests']),'element tests,',len(d['plate_tests']),'plate cases')
