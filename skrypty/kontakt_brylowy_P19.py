"""Wypukly styk3D:skalowanie,refinement kroku i precyzyjna reszta/energia."""
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import splu


def solve_hinges(K,D,stiffness,offset,F,tol=1e-9,max_iter=80):
    K=K.tocsr();D=D.tocsr()
    skew_relative=np.linalg.norm((K-K.T).data)/max(np.linalg.norm(K.data),1e-30)
    if skew_relative>1e-12:raise ValueError('Niesymetryczna energia liniowa')
    K=(K+K.T)*.5;Khi=K.astype(np.longdouble);Dhi=D.astype(np.longdouble)
    a=np.asarray(stiffness,np.longdouble);off=np.asarray(offset,np.longdouble);Fhi=np.asarray(F,np.longdouble)
    zero=np.maximum(off,0);q=np.zeros(K.shape[0])
    scale=max(np.linalg.norm(F),np.linalg.norm(np.asarray(D.T@(a*zero),float)),1.)
    history=[]
    def quantities(x):
        xx=np.asarray(x,np.longdouble);z=Dhi@xx+off;pos=np.maximum(z,0)
        gradient=Khi@xx+Dhi.T@(a*pos)-Fhi
        energy=.5*xx@(Khi@xx)+.5*np.dot(a,pos*pos-zero*zero)-Fhi@xx
        return z,gradient,energy
    for iteration in range(max_iter):
        z,g,E=quantities(q);res=float(np.linalg.norm(g)/scale);history.append(res)
        active=np.asarray(z>0);J=K+D.T@sparse.diags(np.asarray(a*active,float))@D
        if res<tol:return q,J,active,dict(iterations=iteration+1,residual=res,history=history,arithmetic='float64solve/longdouble_residual_and_incremental_potential',input_skew_relative=skew_relative)
        diag=J.diagonal()
        if min(diag)<=0:raise RuntimeError('Niedodatnia diagonala stycznej')
        S=1/np.sqrt(diag);Smat=sparse.diags(S);factor=splu((Smat@J@Smat).tocsc())
        step=S*factor.solve(-np.asarray(g,float)*S);Jhi=J.astype(np.longdouble)
        for _ in range(3):
            defect=-g-Jhi@np.asarray(step,np.longdouble)
            if np.linalg.norm(defect)<=1e-12*max(np.linalg.norm(g),1e-30):break
            step+=S*factor.solve(np.asarray(defect,float)*S)
        sh=np.asarray(step,np.longdouble);slope=np.dot(g,sh);alpha=1.
        quadratic=np.dot(sh,Khi@sh);dz=Dhi@sh
        for _ in range(45):
            delta=alpha*dz;zn=z+delta;oldpos=z>0;newpos=zn>0
            # Dokladny przyrost wypuklej energii na kazdej galezi,
            # bez odejmowania dwoch duzych energii q^T*K*q.
            bregman=np.zeros_like(z)
            both=oldpos&newpos;bregman[both]=.5*delta[both]**2
            entering=(~oldpos)&newpos;bregman[entering]=.5*zn[entering]**2
            leaving=oldpos&(~newpos);bregman[leaving]=-.5*z[leaving]**2-z[leaving]*delta[leaving]
            spring_delta=np.dot(a,bregman)
            increment=alpha*slope+.5*alpha*alpha*quadratic+spring_delta
            rounding=256*np.finfo(np.longdouble).eps*(abs(alpha*slope)+abs(.5*alpha*alpha*quadratic)+abs(spring_delta))
            if increment<=np.longdouble(1e-4)*alpha*slope+rounding:break
            alpha*=.5
        else:raise RuntimeError('Styk3D:brakspadku energii;reszta='+str(res))
        q+=alpha*step
    raise RuntimeError('Styk3D:brakzbieznosci;historia='+str(history[-8:]))
