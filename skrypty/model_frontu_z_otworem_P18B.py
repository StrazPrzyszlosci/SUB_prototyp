"""P18B: izoparametryczny MITC4, otwór i podatne zamocowanie sztywnego kosza.

SI. Małe odkształcenia, płyta izotropowa, brak naprężeń membranowych/3D.
Okrąg jest wielokątem z kontrolą zbieżności, nie schodkową wycinanką.
Sprężyny łączą skończone łaty z trzema DOF kosza, nie punktowe siły.
"""
import numpy as np
from scipy import sparse
from scipy.spatial import cKDTree
from scipy.sparse.linalg import spsolve, eigsh
from model_plyty_MITC_P18 import PlateMaterial


def natural_shape(xi, eta):
    sx=np.array([-1.,1.,1.,-1.]); sy=np.array([-1.,-1.,1.,1.])
    N=(1+sx*xi)*(1+sy*eta)/4
    dN=np.array([sx*(1+sy*eta)/4, sy*(1+sx*xi)/4])
    return N,dN


def geometry(xy, xi, eta):
    N,dN=natural_shape(xi,eta); J=dN@xy; det=np.linalg.det(J)
    if det<=0: raise ValueError('Odwrócony lub zdegenerowany element')
    return N,np.linalg.solve(J,dN),J,det


def covariant_shear(xy,xi,eta):
    N,dN=natural_shape(xi,eta); J=dN@xy; B=np.zeros((2,12))
    B[:,0::3]=dN
    B[:,1::3]=-J[:,0,None]*N
    B[:,2::3]=-J[:,1,None]*N
    return B


def operators(xy,xi,eta):
    N,der,J,det=geometry(xy,xi,eta); Bb=np.zeros((3,12))
    Bb[0,1::3]=der[0]; Bb[1,2::3]=der[1]
    Bb[2,1::3]=der[1]; Bb[2,2::3]=der[0]
    cov=np.empty((2,12))
    cov[0]=.5*(1-eta)*covariant_shear(xy,0,-1)[0]+.5*(1+eta)*covariant_shear(xy,0,1)[0]
    cov[1]=.5*(1-xi)*covariant_shear(xy,-1,0)[1]+.5*(1+xi)*covariant_shear(xy,1,0)[1]
    return N,Bb,np.linalg.solve(J,cov),det


def element(xy,material):
    K=np.zeros((12,12)); M=np.zeros((12,12)); F=np.zeros(12)
    for xi in [-1/np.sqrt(3),1/np.sqrt(3)]:
        for eta in [-1/np.sqrt(3),1/np.sqrt(3)]:
            N,Bb,Bs,det=operators(xy,xi,eta)
            K+=(Bb.T@material.bending@Bb+material.shear_n_m*Bs.T@Bs)*det
            for field,value in [(0,material.density_kg_m3*material.thickness_m),
                                (1,material.density_kg_m3*material.thickness_m**3/12),
                                (2,material.density_kg_m3*material.thickness_m**3/12)]:
                ids=np.arange(field,12,3); M[np.ix_(ids,ids)]+=value*np.outer(N,N)*det
            F[0::3]+=N*det
    return K,M,F


class FrontWithHole:
    def __init__(self,a_m,b_m,hole_radius_m,material,angular_per_side=16,
                 radial_layers=8,boundary='CCCC',outer_circle=False):
        if not 0<hole_radius_m<min(a_m,b_m)/2: raise ValueError('Otwór musi mieścić się w płycie')
        if boundary not in ['CCCC','SSSS_HARD']: raise ValueError('Nieznany brzeg')
        if angular_per_side<2 or radial_layers<2: raise ValueError('Zbyt rzadka siatka')
        self.a=a_m;self.b=b_m;self.r=hole_radius_m;self.material=material;self.boundary=boundary
        self.nt=4*int(angular_per_side);self.nr=int(radial_layers);self.outer_circle=outer_circle
        if outer_circle:
            if abs(a_m-b_m)>1e-12:raise ValueError('Kołowa kontrola wymaga a=b')
            theta=np.arange(self.nt)*2*np.pi/self.nt
        else:
            # Każdy narożnik należy do siatki, również dla prostokąta a!=b.
            corner=np.arctan2(b_m,a_m)
            cuts=np.array([-corner,corner,np.pi-corner,np.pi+corner,2*np.pi-corner])
            theta=np.concatenate([np.linspace(cuts[i],cuts[i+1],angular_per_side,endpoint=False) for i in range(4)])
        self.theta=theta
        c=np.cos(theta);s=np.sin(theta)
        rout=np.full(self.nt,a_m/2) if outer_circle else np.minimum(a_m/(2*np.maximum(abs(c),1e-16)),b_m/(2*np.maximum(abs(s),1e-16)))
        radii=hole_radius_m+(rout-hole_radius_m)*np.linspace(0,1,self.nr+1)[:,None]
        self.xy=np.stack([radii*c,radii*s],axis=-1).reshape(-1,2)
        self.elements=np.array([[i*self.nt+j,(i+1)*self.nt+j,(i+1)*self.nt+(j+1)%self.nt,i*self.nt+(j+1)%self.nt]
                                for i in range(self.nr) for j in range(self.nt)])
        self.dofs=(3*self.elements[:,:,None]+np.arange(3)[None,None,:]).reshape(-1,12)
        ndof=3*len(self.xy); ke=[];me=[];F=np.zeros(ndof)
        for nodes,ids in zip(self.elements,self.dofs):
            k,m,f=element(self.xy[nodes],material);ke.append(k.ravel());me.append(m.ravel());np.add.at(F,ids,f)
        rows=np.repeat(self.dofs,12,axis=1).ravel();cols=np.tile(self.dofs,(1,12)).ravel()
        self.full_K=sparse.coo_matrix((np.ravel(ke),(rows,cols)),shape=(ndof,ndof)).tocsr()
        self.full_M=sparse.coo_matrix((np.ravel(me),(rows,cols)),shape=(ndof,ndof)).tocsr();self.full_F=F
        fixed=set();outer=np.arange(self.nr*self.nt,(self.nr+1)*self.nt)
        fixed.update(3*outer)
        if boundary=='CCCC':fixed.update(3*outer+1);fixed.update(3*outer+2)
        elif not outer_circle:
            for node in outer:
                x,y=self.xy[node]
                if np.isclose(abs(x),a_m/2):fixed.add(3*node+2)
                if np.isclose(abs(y),b_m/2):fixed.add(3*node+1)
        self.fixed=np.array(sorted(fixed),int);self.free=np.setdiff1d(np.arange(ndof),self.fixed)
        self.K=self.full_K[self.free][:,self.free];self.M=self.full_M[self.free][:,self.free];self.F=F[self.free]
        self.tree=cKDTree(self.xy[self.elements].mean(axis=1))
        self.actual_solid_area_m2=float(F.sum())
        inner=self.xy[:self.nt];self.hole_polygon_area_m2=float(.5*abs(np.sum(inner[:,0]*np.roll(inner[:,1],-1)-inner[:,1]*np.roll(inner[:,0],-1))))

    def interpolate(self,x,y):
        _,near=self.tree.query([x,y],k=min(16,len(self.elements)))
        for e in np.atleast_1d(near):
            xy=self.xy[self.elements[e]];z=np.zeros(2)
            for _ in range(12):
                N,dN=natural_shape(*z);res=N@xy-np.array([x,y]);step=np.linalg.solve((dN@xy).T,res);z-=step
                if np.linalg.norm(step)<1e-12:break
            if max(abs(z))<=1+1e-9:
                N,_=natural_shape(*z);v=np.zeros(len(self.full_F));v[self.dofs[e,0::3]]=N
                return v
        raise ValueError('Punkt poza siatką: '+str((x,y)))

    def disk_patch(self,x,y,radius_m,radial_order=4,angular_order=16):
        if radius_m<=0:raise ValueError('Łata musi mieć skończony dodatni promień')
        # Całkowanie po t=r²/a² daje jednostajną miarę pola, suma wag=1.
        z,w=np.polynomial.legendre.leggauss(radial_order);t=(z+1)/2;w=w/2
        v=np.zeros(len(self.full_F))
        for ti,wi in zip(t,w):
            for phi in np.arange(angular_order)*2*np.pi/angular_order:
                r=radius_m*np.sqrt(ti);v+=wi/angular_order*self.interpolate(x+r*np.cos(phi),y+r*np.sin(phi))
        if abs(v.sum()-1)>1e-10:raise ArithmeticError('Brak jedności rozkładu obciążenia')
        return v[self.free]

    def continuous_inner(self,payload_mass_kg=0,rotary_inertia_kg_m2=0):
        """Odrębna kontrola: ciągłe sztywne zamocowanie na całym brzegu otworu."""
        inner_ids=np.arange(3*self.nt);rest=np.setdiff1d(self.free,inner_ids)
        rr=list(rest);cc=list(range(len(rest)));vv=[1.]*len(rest)
        for n,(x,y) in enumerate(self.xy[:self.nt]):
            for d,c,v in [(3*n,0,1),(3*n,1,x),(3*n,2,y),(3*n+1,1,1),(3*n+2,2,1)]:
                rr.append(d);cc.append(len(rest)+c);vv.append(v)
        T=sparse.coo_matrix((vv,(rr,cc)),shape=(len(self.full_F),len(rest)+3)).tocsr()
        K=(T.T@self.full_K@T).tocsr();M=(T.T@self.full_M@T).tocsr()
        extra=np.zeros(K.shape[0]);extra[-3:]=[payload_mass_kg,rotary_inertia_kg_m2,rotary_inertia_kg_m2]
        M+=sparse.diags(extra)
        F=np.asarray(T.T@self.full_F);return K,M,F,T

    def mounted(self,bolt_circle_radius_m,bolt_count,payload_mass_kg,rotary_inertia_kg_m2,
                spring_each_n_m,patch_radius_m=.004,phase_rad=0.):
        if bolt_count<3 or min(payload_mass_kg,rotary_inertia_kg_m2,spring_each_n_m)<=0:
            raise ValueError('Dodatnie masa/bezwładność/sztywność, >=3mocowania')
        positions=bolt_circle_radius_m*np.stack([np.cos(phase_rad+np.arange(bolt_count)*2*np.pi/bolt_count),
                                               np.sin(phase_rad+np.arange(bolt_count)*2*np.pi/bolt_count)],axis=1)
        B=np.stack([self.disk_patch(x,y,patch_radius_m) for x,y in positions],axis=1)
        G=np.column_stack([np.ones(bolt_count),positions])
        D=sparse.csr_matrix(np.column_stack([B.T,-G]));n=len(self.F)
        K=sparse.block_diag([self.K,sparse.csr_matrix((3,3))],format='csr')+spring_each_n_m*(D.T@D)
        M=sparse.block_diag([self.M,sparse.diags([payload_mass_kg,rotary_inertia_kg_m2,rotary_inertia_kg_m2])],format='csr')
        return MountedFront(self,K,M,B,G,D,spring_each_n_m,payload_mass_kg,positions)

    def bending_stress_bound(self,q):
        if not hasattr(self,'stress_operator'):
            rr=[];cc=[];vv=[];row=0
            for nodes,ids in zip(self.elements,self.dofs):
                for xi in [-1/np.sqrt(3),1/np.sqrt(3)]:
                    for eta in [-1/np.sqrt(3),1/np.sqrt(3)]:
                        _,Bb,_,_=operators(self.xy[nodes],xi,eta)
                        block=6/self.material.thickness_m**2*self.material.bending@Bb
                        rr.extend(np.repeat(np.arange(row,row+3),12));cc.extend(np.tile(ids,3));vv.extend(block.ravel());row+=3
            op=sparse.coo_matrix((vv,(rr,cc)),shape=(row,len(self.full_F))).tocsr()
            self.stress_operator=op[:,self.free]
        stress=np.asarray(self.stress_operator@q).reshape(-1,3)
        sx,sy,t=stress.T
        return float(max(abs((sx+sy)/2)+np.sqrt(abs((sx-sy)/2)**2+abs(t)**2)))


class MountedFront:
    def __init__(self,plate,K,M,B,G,D,k,mass,positions):
        self.plate=plate;self.K=K;self.M=M;self.B=B;self.G=G;self.D=D;self.k=k;self.mass=mass;self.positions=positions

    def load(self,pressure_pa=0.,basket_force_n=0.,moment_x_nm=0.,moment_y_nm=0.,pressure_cap=False):
        F=np.r_[self.plate.F*pressure_pa,[basket_force_n,moment_x_nm,moment_y_nm]]
        if pressure_cap:F[-3]+=pressure_pa*self.plate.hole_polygon_area_m2
        return F

    def static(self,F):return spsolve(self.K,F)

    def modes(self,count=12):
        val,vec=eigsh(self.K,k=count,M=self.M,sigma=0,which='LM')
        order=np.argsort(val);val=val[order];vec=vec[:,order]
        if val[0]<=0:raise ArithmeticError('Niedodatni mod zamocowanego układu')
        return np.sqrt(val)/(2*np.pi),vec

    def independent_static(self,F):
        # Odrębne równania zgodności sił mocowań + 3równania równowagi kosza.
        n=len(self.plate.F);H=spsolve(self.plate.K,self.B);u0=spsolve(self.plate.K,F[:n]);C=self.B.T@H
        small=np.block([[C+np.eye(len(C))/self.k,-self.G],[self.G.T,np.zeros((3,3))]])
        result=np.linalg.solve(small,np.r_[-self.B.T@u0,F[-3:]])
        forces=result[:-3];q=np.r_[u0+H@forces,result[-3:]]
        return q,forces

    def observe(self,q):
        n=len(self.plate.F);full=np.zeros(len(self.plate.full_F),dtype=q.dtype);full[self.plate.free]=q[:n]
        return dict(maximum_plate_w_m=float(max(abs(full[0::3]))),basket_translation_m=q[-3],
                    basket_rotation_x=q[-2],basket_rotation_y=q[-1],joint_forces_n=-self.k*(self.D@q))

    def prescribed_cone(self,f_hz,x_relative_rms_m,moving_mass_kg,sd_m2,
                        cavity_m3=.1,tau_s=.005,zeta=.03,p0_pa=101325.,gamma=1.4):
        """Stożek zadany względem kosza; komora0D, sztywne inne ściany.

        Masa całkowita kosz+stożek jest już w M. Mmoving*ddot(xrel) to
        sprzężenie kinetyczne, nie ponownie dodana masa do M.
        Brak zewnętrznej radiacji, napędu elektrycznego i samej podatności
        zawieszenia: liczymy wymaganą siłę netto portu wymuszenia xrel.
        """
        if min(f_hz,x_relative_rms_m,moving_mass_kg,sd_m2,cavity_m3,tau_s,zeta)<=0 or moving_mass_kg>=self.mass:
            raise ValueError('Dodatnie parametry, Mmoving<Mtotal')
        w=2*np.pi*f_hz;s=1j*w
        f1=self.modes(1)[0][0];w1=2*np.pi*f1;w2=5*w1
        alpha=2*zeta*w1*w2/(w1+w2);beta=2*zeta/(w1+w2)
        C=alpha*self.M+beta*self.K;Z=self.K-w*w*self.M+s*C
        H=self.load(pressure_pa=1,pressure_cap=True)
        cab=cavity_m3/(p0_pa*(1+(gamma-1)*s*tau_s/(1+s*tau_s)))
        e=np.zeros(len(H));e[-3]=1.
        inertial=e*moving_mass_kg*w*w*x_relative_rms_m
        # Rank1komora: bez tworzenia gęstego H*H.T.
        zi=spsolve(Z,inertial);zh=spsolve(Z,H)
        p=-(sd_m2*x_relative_rms_m+H@zi)/(cab+H@zh)
        q=zi+zh*p
        force_required=-moving_mass_kg*w*w*(x_relative_rms_m+q[-3])-sd_m2*p
        source_power=float((force_required*np.conj(s*x_relative_rms_m)).real)
        structural_power=float(w*w*np.vdot(q,C@q).real)
        gas_power=float((s*cab).real*abs(p)**2)
        residual=abs(source_power-structural_power-gas_power)/max(abs(source_power),structural_power+gas_power,1e-30)
        return q,dict(f_hz=f_hz,pressure_pa_real=float(p.real),pressure_pa_imag=float(p.imag),
                      pressure_pa_rms=float(abs(p)),source_power_w=source_power,structural_power_w=structural_power,
                      gas_power_w=gas_power,relative_power_residual=float(residual),
                      force_required_n_real=float(force_required.real),force_required_n_imag=float(force_required.imag),
                      cone_motion_rms_m=x_relative_rms_m,moving_mass_proxy_kg=moving_mass_kg,
                      scope='PRESCRIBED_RELATIVE_MOTION_0D_NO_EXTERIOR_RADIATION_NO_ELECTRICAL_MOTOR')


def axisymmetric_kirchhoff(ri,ro,D,nu,pressure_pa=1.,cap_force_n=0.,outer='CCCC'):
    """Dokładny niezależny ansatz r^4,r²logr,r²,logr,1; r w Laplace' daje siłę."""
    def basis(r):return np.array([r*r*np.log(r),r*r,np.log(r),1.])
    def first(r):return np.array([2*r*np.log(r)+r,2*r,1/r,0.])
    def second(r):return np.array([2*np.log(r)+3,2.,-1/r**2,0.])
    A=np.zeros((4,4));rhs=np.zeros(4)
    A[0]=basis(ro);rhs[0]=-pressure_pa*ro**4/(64*D)
    if outer=='CCCC':A[1]=first(ro);rhs[1]=-pressure_pa*ro**3/(16*D)
    elif outer=='SSSS_HARD':
        A[1]=second(ro)+nu/ro*first(ro);rhs[1]=-pressure_pa*(3+nu)*ro**2/(16*D)
    else:raise ValueError(outer)
    A[2]=first(ri);rhs[2]=-pressure_pa*ri**3/(16*D)
    A[3,0]=8*np.pi*D;rhs[3]=cap_force_n-np.pi*pressure_pa*ri**2
    coef=np.linalg.solve(A,rhs)
    def w(r):return pressure_pa*r**4/(64*D)+basis(r)@coef
    return dict(inner_displacement_m=float(w(ri)),coefficients=coef,
                evaluate=lambda r:pressure_pa*r**4/(64*D)+np.array([basis(t)@coef for t in np.atleast_1d(r)]))
