"""P18A: prostokątna płyta Reissnera-Mindlina,3DOF/node,MITC4 shear.

SI, małe odkształcenia, izotropoweE/nu. To nie pełna powłokaMITC4+,
skrzynia3D,otwór frontu ani identyfikacja rzeczywistego MDF/połączenia.
"""
from dataclasses import dataclass
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve,eigsh
from scipy.linalg import eigh


@dataclass(frozen=True)
class PlateMaterial:
    E_pa:float
    nu:float
    density_kg_m3:float
    thickness_m:float
    shear_factor:float=5/6

    def __post_init__(self):
        if min(self.E_pa,self.density_kg_m3,self.thickness_m,self.shear_factor)<=0 or not -1<self.nu<.5:
            raise ValueError('E,rho,h,kappa>0, -1<nu<0.5')

    @property
    def rigidity_nm(self):return self.E_pa*self.thickness_m**3/(12*(1-self.nu**2))

    @property
    def bending(self):
        n=self.nu;return self.rigidity_nm*np.array([[1,n,0],[n,1,0],[0,0,(1-n)/2]])

    @property
    def shear_n_m(self):return self.shear_factor*self.E_pa*self.thickness_m/(2*(1+self.nu))


def shape(xi,eta,dx,dy):
    sx=np.array([-1.,1.,1.,-1.]);sy=np.array([-1.,-1.,1.,1.])
    N=(1+sx*xi)*(1+sy*eta)/4
    dnx=sx*(1+sy*eta)/(2*dx);dny=sy*(1+sx*xi)/(2*dy)
    return N,dnx,dny


def bending_B(xi,eta,dx,dy):
    N,nx,ny=shape(xi,eta,dx,dy);B=np.zeros((3,12))
    B[0,1::3]=nx;B[1,2::3]=ny;B[2,1::3]=ny;B[2,2::3]=nx
    return B


def shear_standard(xi,eta,dx,dy):
    N,nx,ny=shape(xi,eta,dx,dy);B=np.zeros((2,12))
    B[0,0::3]=nx;B[0,1::3]=-N;B[1,0::3]=ny;B[1,2::3]=-N
    return B


def shear_MITC(xi,eta,dx,dy):
    B=np.zeros((2,12))
    B[0]=.5*(1-eta)*shear_standard(0.,-1.,dx,dy)[0]+.5*(1+eta)*shear_standard(0.,1.,dx,dy)[0]
    B[1]=.5*(1-xi)*shear_standard(-1.,0.,dx,dy)[1]+.5*(1+xi)*shear_standard(1.,0.,dx,dy)[1]
    return B


def element_matrices(dx,dy,material,formulation='MITC'):
    K=np.zeros((12,12));M=np.zeros_like(K);F=np.zeros(12)
    D=material.bending;Gs=material.shear_n_m;rho=material.density_kg_m3;h=material.thickness_m
    jac=dx*dy/4
    for xi in (-1/np.sqrt(3),1/np.sqrt(3)):
        for eta in (-1/np.sqrt(3),1/np.sqrt(3)):
            N,_,_=shape(xi,eta,dx,dy);Bb=bending_B(xi,eta,dx,dy)
            Bs=shear_MITC(xi,eta,dx,dy) if formulation=='MITC' else shear_standard(xi,eta,dx,dy)
            K+=(Bb.T@D@Bb+Gs*(Bs.T@Bs))*jac
            for field,mass in [(0,rho*h),(1,rho*h**3/12),(2,rho*h**3/12)]:
                inds=np.arange(field,12,3);M[np.ix_(inds,inds)]+=mass*np.outer(N,N)*jac
            F[0::3]+=N*jac
    return K,M,F


class RectangularPlate:
    def __init__(self,a_m,b_m,nx,ny,material,boundary='SSSS',rotational_edge_n=0.,formulation='MITC'):
        if min(a_m,b_m,nx,ny)<=0 or boundary not in ['SSSS','CCCC','ELASTIC','FREE']:raise ValueError('Geometria/BC')
        if formulation not in ['MITC','Q4_FULL']:raise ValueError('Nieznana interpolacja ścinania')
        if rotational_edge_n<0:raise ValueError('Nieujemna sztywność kątowa')
        self.a=a_m;self.b=b_m;self.nx=nx;self.ny=ny;self.material=material;self.boundary=boundary
        self.dx=a_m/nx;self.dy=b_m/ny
        self.xy=np.array([(i*self.dx,j*self.dy) for j in range(ny+1) for i in range(nx+1)])
        self.elements=np.array([[j*(nx+1)+i,j*(nx+1)+i+1,(j+1)*(nx+1)+i+1,(j+1)*(nx+1)+i] for j in range(ny) for i in range(nx)])
        self.dofs=(3*self.elements[:,:,None]+np.arange(3)[None,None,:]).reshape(-1,12)
        ndof=3*len(self.xy);ke,me,fe=element_matrices(self.dx,self.dy,material,formulation)
        rows=np.repeat(self.dofs,12,axis=1).ravel();cols=np.tile(self.dofs,(1,12)).ravel()
        K=sparse.coo_matrix((np.tile(ke.ravel(),len(self.elements)),(rows,cols)),shape=(ndof,ndof)).tocsr()
        M=sparse.coo_matrix((np.tile(me.ravel(),len(self.elements)),(rows,cols)),shape=(ndof,ndof)).tocsr()
        F=np.zeros(ndof);np.add.at(F,self.dofs.ravel(),np.tile(fe,len(self.elements)))
        fixed=set();x=self.xy[:,0];y=self.xy[:,1]
        xedge=np.isclose(x,0)|np.isclose(x,a_m);yedge=np.isclose(y,0)|np.isclose(y,b_m)
        if boundary!='FREE':
            fixed.update((3*np.flatnonzero(xedge|yedge)).tolist())
            fixed.update((3*np.flatnonzero(xedge)+2).tolist());fixed.update((3*np.flatnonzero(yedge)+1).tolist())
            if boundary=='CCCC' or np.isposinf(rotational_edge_n):
                fixed.update((3*np.flatnonzero(xedge)+1).tolist());fixed.update((3*np.flatnonzero(yedge)+2).tolist())
            elif boundary=='ELASTIC' and rotational_edge_n>0:
                kr=[];kc=[];kv=[]
                for nodes,field,length in [
                    *[(np.array([j*(nx+1),(j+1)*(nx+1)]),1,self.dy) for j in range(ny)],
                    *[(np.array([j*(nx+1)+nx,(j+1)*(nx+1)+nx]),1,self.dy) for j in range(ny)],
                    *[(np.array([i,i+1]),2,self.dx) for i in range(nx)],
                    *[(np.array([ny*(nx+1)+i,ny*(nx+1)+i+1]),2,self.dx) for i in range(nx)]]:
                    ids=3*nodes+field;block=rotational_edge_n*length/6*np.array([[2.,1.],[1.,2.]])
                    kr.extend(np.repeat(ids,2));kc.extend(np.tile(ids,2));kv.extend(block.ravel())
                K+=sparse.coo_matrix((kv,(kr,kc)),shape=K.shape).tocsr()
        self.full_K=K;self.full_M=M;self.full_F=F
        self.free=np.setdiff1d(np.arange(ndof),np.array(sorted(fixed),int));self.K=K[self.free][:,self.free];self.M=M[self.free][:,self.free];self.F=F[self.free]
        self.stress_operator=self._stress_operator()
        self.edge_moment_operator=self._edge_moment_operator()

    def _stress_operator(self):
        rr=[];cc=[];vv=[];D=self.material.bending
        for k,dofs in enumerate(self.dofs):
            for corner,(xi,eta) in enumerate([(-1,-1),(1,-1),(1,1),(-1,1)]):
                B=6/self.material.thickness_m**2*(D@bending_B(xi,eta,self.dx,self.dy))
                inds=np.arange(12*k+3*corner,12*k+3*corner+3)
                rr.extend(np.repeat(inds,12));cc.extend(np.tile(dofs,3));vv.extend(B.ravel())
        op=sparse.coo_matrix((vv,(rr,cc)),shape=(12*len(self.elements),len(self.full_F))).tocsr()
        return op[:,self.free]

    def patch_average(self,center_m,size_m):
        cx,cy=center_m;sx,sy=size_m
        if min(sx,sy)<=0 or cx-sx/2<0 or cy-sy/2<0 or cx+sx/2>self.a or cy+sy/2>self.b:raise ValueError('Łata poza płytą')
        vector=np.zeros(len(self.full_F))
        for nodes,dofs in zip(self.elements,self.dofs):
            x0,y0=self.xy[nodes[0]];xl=max(x0,cx-sx/2);xr=min(x0+self.dx,cx+sx/2)
            yl=max(y0,cy-sy/2);yr=min(y0+self.dy,cy+sy/2)
            if xr<=xl or yr<=yl:continue
            xi=2*((xl+xr)/2-x0)/self.dx-1;eta=2*((yl+yr)/2-y0)/self.dy-1
            N,_,_=shape(xi,eta,self.dx,self.dy)
            vector[dofs[0::3]]+=N*(xr-xl)*(yr-yl)/(sx*sy)
        assert abs(sum(vector)-1)<1e-10
        return vector[self.free]

    def _edge_moment_operator(self):
        rows=[];cols=[];values=[];index=0;D=self.material.bending
        for j in range(self.ny):
            for i,xi in [(0,-1.),(self.nx-1,1.)]:
                dofs=self.dofs[j*self.nx+i]
                for eta in (-1.,1.):
                    v=(D@bending_B(xi,eta,self.dx,self.dy))[0]
                    rows.extend([index]*12);cols.extend(dofs);values.extend(v);index+=1
        for i in range(self.nx):
            for j,eta in [(0,-1.),(self.ny-1,1.)]:
                dofs=self.dofs[j*self.nx+i]
                for xi in (-1.,1.):
                    v=(D@bending_B(xi,eta,self.dx,self.dy))[1]
                    rows.extend([index]*12);cols.extend(dofs);values.extend(v);index+=1
        return sparse.coo_matrix((values,(rows,cols)),shape=(index,len(self.full_F))).tocsr()[:,self.free]

    def edge_moment_peak(self,q,rms=False):
        return float(max(abs(self.edge_moment_operator@q)))*(np.sqrt(2) if rms else 1.)

    def tied_pair(self,patch,axial_stiffness_n_m,rod_mass_kg,parity='symmetric',pad_mass_each_kg=0.):
        """Dwie jednakowe płyty; znaki przemieszczeń dodatnie na zewnątrz.

        Symmetric: obie ściany na zewnątrz. Antisymmetric: wspólna translacja
        nie wydłuża pręta. M pręta to zgodna macierz1D, nie podwojona masa.
        """
        if min(axial_stiffness_n_m,rod_mass_kg,pad_mass_each_kg)<0 or parity not in ['symmetric','antisymmetric']:raise ValueError('Parametry ściągu')
        b=sparse.csr_matrix(np.asarray(patch)[:,None]);outer=(b@b.T).tocsr()
        if parity=='symmetric':return self.K+2*axial_stiffness_n_m*outer,self.M+(rod_mass_kg/6+pad_mass_each_kg)*outer
        return self.K.copy(),self.M+(rod_mass_kg/2+pad_mass_each_kg)*outer

    def static(self,K=None,force=None):
        if self.boundary=='FREE':raise ValueError('Swobodna płyta pod niezrównoważonym p nie ma jednoznacznego statycznego ugięcia')
        return spsolve(self.K if K is None else K,self.F if force is None else force)

    def modes(self,count=10,K=None,M=None):
        K=self.K if K is None else K;M=self.M if M is None else M
        if K.shape[0]<40:values,vectors=eigh(K.toarray(),M.toarray());values=values[:count];vectors=vectors[:,:count]
        else:values,vectors=eigsh(K,k=min(count,K.shape[0]-2),M=M,sigma=0.,which='LM')
        order=np.argsort(values);values=values[order];vectors=vectors[:,order]
        return np.sqrt(np.maximum(values,0))/(2*np.pi),vectors,values

    def expand(self,q):
        q=np.asarray(q);out=np.zeros((len(self.full_F),)+q.shape[1:],dtype=q.dtype);out[self.free]=q;return out

    def transverse_displacements(self,q):return self.expand(q)[0::3]

    def peak_principal_bound(self,q,rms=False):
        values=np.asarray(self.stress_operator@q).reshape(-1,3)
        sx,sy,t=values.T;average=(sx+sy)/2;difference=(sx-sy)/2
        bound=abs(average)+np.sqrt(abs(difference)**2+abs(t)**2)
        return float(max(bound))*(np.sqrt(2) if rms else 1.)

    def frequency_response(self,frequencies_hz,zeta=.03,K=None,M=None):
        if self.boundary=='FREE':raise ValueError('Ta procedura zakłada zamocowane krawędzie')
        K=self.K if K is None else K;M=self.M if M is None else M
        f1=self.modes(1,K,M)[0][0];w1=2*np.pi*f1;w2=5*w1
        alpha=2*zeta*w1*w2/(w1+w2);beta=2*zeta/(w1+w2);C=alpha*M+beta*K
        rows=[];states=[]
        for f in frequencies_hz:
            if f<=0:raise ValueError('RMS dynamiki wymaga f>0; DC licz osobno')
            w=2*np.pi*f;q=spsolve(K-w*w*M+1j*w*C,self.F)
            compliance=np.dot(self.F,q);damping=float(w*w*np.vdot(q,C@q).real)
            input_power=float(-w*compliance.imag)
            residual=abs(input_power-damping)/max(input_power,1e-30)
            rows.append(dict(f_hz=float(f),wall_volume_compliance_m3_pa_real=float(compliance.real),wall_volume_compliance_m3_pa_imag=float(compliance.imag),
                maximum_node_peak_per_PaRMS_m=float(np.sqrt(2)*max(abs(self.transverse_displacements(q)))),
                principal_stress_peak_bound_per_PaRMS=float(self.peak_principal_bound(q,True)),
                edge_moment_peak_per_PaRMS_n=float(self.edge_moment_peak(q,True)),
                input_power_per_PaRMS_squared_w=input_power,viscous_power_per_PaRMS_squared_w=damping,relative_power_residual=float(residual)))
            states.append(q)
        return rows,np.asarray(states).T,dict(first_mode_hz=float(f1),Rayleigh_alpha_per_s=float(alpha),Rayleigh_beta_s=float(beta),zeta_at_f1_and_5f1=zeta)


def navier_reference(a,b,material,terms=101):
    """Odrębny szereg dokładnego rozwiązania Mindlina SSSS; p_static=1Pa."""
    odd=np.arange(1,terms+1,2);m,n=np.meshgrid(odd,odd,indexing='ij');kx=m*np.pi/a;ky=n*np.pi/b;k2=kx*kx+ky*ky
    pmodal=16/(np.pi*np.pi*m*n)
    wmodal=pmodal*(1/(material.rigidity_nm*k2*k2)+1/(material.shear_n_m*k2))
    center=float(np.sum(wmodal*np.sin(m*np.pi/2)*np.sin(n*np.pi/2)))
    compliance=float(np.sum(wmodal*4*a*b/(np.pi*np.pi*m*n)))
    k=np.sqrt((np.pi/a)**2+(np.pi/b)**2);Gs=material.shear_n_m;D=material.rigidity_nm
    smallK=np.array([[Gs*k*k,-Gs*k],[-Gs*k,D*k*k+Gs]])
    mass=np.diag([material.density_kg_m3*material.thickness_m,material.density_kg_m3*material.thickness_m**3/12])
    first=np.sqrt(eigh(smallK,mass,eigvals_only=True)[0])/(2*np.pi)
    return dict(center_static_m_per_pa=center,volume_compliance_m3_pa=compliance,first_mode_hz=float(first))
