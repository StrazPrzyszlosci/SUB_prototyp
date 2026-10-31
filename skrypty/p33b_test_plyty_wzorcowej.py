#!/usr/bin/env python3
"""Independent simply-supported rectangle benchmark for P33B Q4 Mindlin shell."""
import numpy as np, math
from scipy.sparse import coo_matrix,diags
from scipy.sparse.linalg import eigsh
from p33b_powlokowy_fem import shell_element,E,nu,rho
L=.976;B=.359;t=.022
D=E*t**3/(12*(1-nu**2))
analytic=math.pi/2*math.sqrt(D/(rho*t))*(1/L**2+1/B**2)
for nx,ny in [(8,4),(16,8),(32,12)]:
 rows=[];cols=[];vals=[];mass=np.zeros(5*(nx+1)*(ny+1))
 def node(i,j):return i*(ny+1)+j
 for i in range(nx):
  for j in range(ny):
   K=shell_element(L/nx,B/ny,t)
   nodes=[node(i,j),node(i+1,j),node(i+1,j+1),node(i,j+1)]
   ids=[5*n+d for n in nodes for d in range(5)]
   area=L*B/(nx*ny)
   for a,I in enumerate(ids):
    d=a%5
    mass[I]+=(rho*t*area/4 if d<=2 else rho*t**3*area/48)
    for b,J in enumerate(ids):
     if K[a,b]:rows.append(I);cols.append(J);vals.append(K[a,b])
 free=[]
 for i in range(nx+1):
  for j in range(ny+1):
   q=node(i,j)
   free.extend([5*q+3,5*q+4])
   if 0<i<nx and 0<j<ny:free.append(5*q+2)
 K=coo_matrix((vals,(rows,cols)),shape=(len(mass),len(mass))).tocsr()[free,:][:,free]
 eigen=eigsh(K,k=4,M=diags(mass[free]),sigma=0,which='LM',
             tol=1e-6,return_eigenvectors=False)
 f=float(np.sqrt(max(0,min(eigen)))/(2*math.pi))
 print(nx,ny,'Mindlin Hz',round(f,6),'Kirchhoff Hz',round(analytic,6),
       'relative error %',round(100*(f-analytic)/analytic,4))
 if abs(f-analytic)/analytic>.04:raise RuntimeError('Benchmark Q4 outside 4 percent')
