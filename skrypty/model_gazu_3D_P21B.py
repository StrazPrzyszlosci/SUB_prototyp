"""Ciśnienie Q1/H8 na dopełnieniu bryłyP20C,granica pracy i pełny gaz3D.

SI, exp(+jwt), fazoryRMS. A=∫gradN.gradN/rho, C=∫NN/Kbulk.
Ds*u-B*p=Hext*po, (A+s²C)*p=-s²B.T*u. Nie usuwamy fizycznego
ruchu sztywnego bryły; gaz ma własną bezwładność w równaniu falowym.
"""
from collections import Counter
from itertools import product
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import eigsh,splu
from element_brylowy_P18C import SIGNS,shape,quad_quadrature
from model_ramy_3D_P18C import FACES,skew
from model_gazu import Medium


def scalar_hex(length,rho,bulk):
    xyz=(SIGNS+1)/2*np.asarray(length)
    A=np.zeros((8,8));C=np.zeros((8,8));G=np.zeros((3,8));L=np.zeros((3,8));points=[]
    for point in SIGNS/np.sqrt(3):
        N,dN=shape(point);J=dN@xyz;det=np.linalg.det(J);der=np.linalg.solve(J,dN);r=N@xyz
        A+=der.T@der*det/rho;C+=np.outer(N,N)*det/bulk
        G+=der*det;L+=skew(r)@der*det;points.append((N,der,det,r))
    corners=[np.linalg.solve(shape(point)[1]@xyz,shape(point)[1]) for point in SIGNS]
    return (A+A.T)/2,(C+C.T)/2,dict(volume=float(np.prod(length)),gradient_integral=G,angular_gradient_integral=L,points=points,corner_derivatives=corners)


class AcousticCavity:
    def __init__(self,solid,medium=Medium(),kappa=1.4):
        self.solid=solid;self.medium=medium;self.kappa=kappa;self.rho=medium.rho;self.bulk=kappa*medium.p0_pa;self.c=np.sqrt(self.bulk/self.rho)
        x,y,z=solid.axes;nx,ny,nz=len(x),len(y),len(z);all_xyz=np.array([(xx,yy,zz) for zz in z for yy in y for xx in x])
        cells=[];sizes=[];centers=[]
        for k,j,i in product(range(nz-1),range(ny-1),range(nx-1)):
            center=np.array([(x[i]+x[i+1])/2,(y[j]+y[j+1])/2,(z[k]+z[k+1])/2])
            if solid.material_at(center) is not None:continue
            a=k*nx*ny+j*nx+i
            cells.append([a,a+1,a+nx+1,a+nx,a+nx*ny,a+nx*ny+1,a+nx*ny+nx+1,a+nx*ny+nx])
            sizes.append([x[i+1]-x[i],y[j+1]-y[j],z[k+1]-z[k]]);centers.append(center)
        old=np.array(cells,int);used=np.unique(old);remap=np.full(len(all_xyz),-1,int);remap[used]=np.arange(len(used))
        self.xyz=all_xyz[used];self.full_ids=used;self.elements=remap[old];self.sizes=np.array(sizes);self.centers=np.array(centers);self.ndof=len(used)
        self.volume=float(np.sum(np.prod(self.sizes,axis=1)));self.Ci=self.volume/self.bulk
        assert abs(self.volume/solid.inner_volume-1)<1e-10
        self.cache={};aa=[];cc=[];self.G=np.zeros((6,self.ndof))
        for i,ids in enumerate(self.elements):
            key=tuple(np.round(self.sizes[i],12))
            if key not in self.cache:self.cache[key]=scalar_hex(key,self.rho,self.bulk)
            a,c,meta=self.cache[key];aa.append(a.ravel());cc.append(c.ravel())
            origin=self.xyz[ids[0]];self.G[:3,ids]+=meta['gradient_integral']
            self.G[3:,ids]+=skew(origin)@meta['gradient_integral']+meta['angular_gradient_integral']
        rr=np.repeat(self.elements,8,axis=1).ravel();cols=np.tile(self.elements,(1,8)).ravel()
        self.A=sparse.coo_matrix((np.ravel(aa),(rr,cols)),shape=(self.ndof,self.ndof)).tocsr()
        self.C=sparse.coo_matrix((np.ravel(cc),(rr,cols)),shape=(self.ndof,self.ndof)).tocsr()
        self.A.eliminate_zeros();self.C.eliminate_zeros();self.ones=np.ones(self.ndof)
        self.mean_weights=self.C@self.ones/self.Ci
        assert abs(self.ones@self.C@self.ones/self.Ci-1)<1e-10
        assert np.linalg.norm(self.A@self.ones)/np.linalg.norm(self.A.data)<1e-12
        # Zgodne globalne identyfikatory powierzchni; bez interpolacji między różnymi siatkami.
        indices=[np.searchsorted(axis,solid.xyz[:,a]) for a,axis in enumerate(solid.axes)]
        solid_full=indices[0]+nx*indices[1]+nx*ny*indices[2];assert np.array_equal(all_xyz[solid_full],solid.xyz)
        solid_lookup=np.full(len(all_xyz),-1,int);solid_lookup[solid_full]=np.arange(len(solid.xyz))
        inner_faces={tuple(sorted(solid_full[face])) for face,axis,val,port,sign in solid.boundary if port==0}
        faces=[tuple(ids[face]) for ids in self.elements for face in FACES];count=Counter(tuple(sorted(v)) for v in faces)
        owner={tuple(sorted(ids[face])):i for i,ids in enumerate(self.elements) for face in FACES}
        br=[];bc=[];bv=[];matched=set();self.boundary=[]
        for face in faces:
            key=tuple(sorted(face))
            if count[key]!=1:continue
            points=self.xyz[list(face)];axis=int(np.argmin(np.ptp(points,axis=0)));value=points[0,axis]
            sign=1 if value>self.centers[owner[key],axis] else -1
            global_ids=used[list(face)];shared=tuple(sorted(global_ids));assert shared in inner_faces
            matched.add(shared);sids=solid_lookup[global_ids];assert np.all(sids>=0)
            mass=np.zeros((4,4))
            for N,point,area in quad_quadrature(points,order=2):mass+=np.outer(N,N)*area
            br.extend(np.repeat(3*sids+axis,4));bc.extend(np.tile(face,4));bv.extend((sign*mass).ravel())
            self.boundary.append((np.array(face),axis,value,sign))
        assert matched==inner_faces
        self.B=sparse.coo_matrix((bv,(br,bc)),shape=(solid.ndof,self.ndof)).tocsr()
        self.boundary_work_error=float(np.linalg.norm(self.B@self.ones-solid.H[:,0])/np.linalg.norm(solid.H[:,0]));assert self.boundary_work_error<1e-10
        self.gradient_boundary_error=float(np.linalg.norm(solid.R.T@self.B-self.G)/np.linalg.norm(self.G));assert self.gradient_boundary_error<1e-10
        # Drugi port jest jawnym, niejednorodnym polem diagnostycznym.
        grad=np.zeros(solid.ndof);W=solid.outer[0]
        for face,axis,value,port,sign in solid.boundary:
            if port!=1:continue
            for N,point,area in quad_quadrature(solid.xyz[face],order=2):
                weights=N*sign*area*(point[0]-W/2)/W
                np.add.at(grad,3*face+axis,weights)
        self.Hext=np.column_stack([solid.H[:,1],solid.H[:,1]+grad])
        self.port_names=['uniform','uniform_plus_x_gradient']

    def modes(self,count=12):
        values,V=eigsh(self.A,k=count+1,M=self.C,sigma=-(2*np.pi)**2,which='LM',v0=np.sin(np.arange(self.ndof)+1))
        order=np.argsort(values);values=values[order];V=V[:,order]
        assert abs(values[0])<values[1]*1e-7 and values[1]>0
        return values[1:],V[:,1:],float(values[0])

    def solve(self,frequency,spatial_scale=1.,ports=None,split_mean=True):
        if frequency<=0 or spatial_scale<=0:raise ValueError('Dodatnie f i skala przestrzenna')
        m=self.solid;f=float(frequency);w=2*np.pi*f;s=1j*w;H=self.Hext if ports is None else np.asarray(ports)
        if H.ndim==1:H=H[:,None]
        Ds=(1+s*m.beta)*m.K+s*s*m.M;fluid=spatial_scale*self.A/(w*w)-self.C
        diag_s=m.K.diagonal()+w*w*m.M.diagonal();diag_p=spatial_scale*self.A.diagonal()/(w*w)+self.C.diagonal()
        if split_mean:
            # P=1*pbar+eta,1.T*C*eta=0. Osobny średni mod nie jest mnożony
            # przez duże A;lambda wymusza ograniczenie,bez gęstego projektora.
            hi=sparse.csr_matrix(m.H[:,0,None]);weights=sparse.csr_matrix(self.mean_weights[:,None])
            Z=sparse.bmat([[Ds,-self.B,-hi,None],[-self.B.T,fluid,None,weights],
                [-hi.T,None,sparse.csr_matrix([[-self.Ci]]),None],
                [None,weights.T,None,sparse.csr_matrix((1,1))]],format='csc')
            lambda_diagonal=float(np.sum(self.mean_weights**2/diag_p))
            diagonal=np.r_[diag_s,diag_p,self.Ci,lambda_diagonal]
            rhs=np.vstack([H,np.zeros((self.ndof+2,H.shape[1]))]).astype(complex)
        else:
            Z=sparse.bmat([[Ds,-self.B],[-self.B.T,fluid]],format='csc')
            diagonal=np.r_[diag_s,diag_p]
            rhs=np.vstack([H,np.zeros((self.ndof,H.shape[1]))]).astype(complex)
        assert np.all(diagonal>0);scale=1/np.sqrt(diagonal)
        S=sparse.diags(scale,format='csc')
        solution=scale[:,None]*splu(S@Z@S).solve(scale[:,None]*rhs)
        U=solution[:m.ndof]
        if split_mean:
            deviation=solution[m.ndof:m.ndof+self.ndof];explicit_mean=solution[-2]
            P=deviation+self.ones[:,None]*explicit_mean
            raw_mean_lagrange_error=solution[-1]+self.Ci*explicit_mean
        else:
            P=solution[m.ndof:];deviation=P-self.ones[:,None]*(self.mean_weights@P)
            raw_mean_lagrange_error=np.zeros(H.shape[1])
        chi=H.T@U;Y=s*chi
        # Projekcja wyłącznie w energii sprężystej,nie w ruchu/warunku granicznym.
        relative=U-m.R@np.linalg.solve(m.mass_rigid,m.R.T@(m.M@U))
        loss=w*w*(relative.conj().T@(m.C@relative));hermitian=(Y+Y.conj().T)/2
        energy_error=float(np.linalg.norm(hermitian-loss)/max(np.linalg.norm(Y),1e-30))
        mechanics=Ds@U-self.B@P-H
        acoustic=spatial_scale*self.A@deviation-w*w*self.C@P-w*w*self.B.T@U
        mech_error=float(np.linalg.norm(mechanics)/max(np.linalg.norm(H)+np.linalg.norm(self.B@P),1e-30))
        acoustic_norm=(np.linalg.norm(spatial_scale*self.A@deviation)+np.linalg.norm(w*w*self.C@P)+np.linalg.norm(w*w*self.B.T@U))
        acoustic_error=float(np.linalg.norm(acoustic)/max(acoustic_norm,1e-30))
        mean=self.mean_weights@P;deviation=P-self.ones[:,None]*mean
        variance=np.einsum('ij,ij->j',deviation.conj(),self.C@deviation).real/self.Ci
        norm=np.einsum('ij,ij->j',P.conj(),self.C@P).real/self.Ci
        volume_residual=self.Ci*mean+m.H[:,0]@U
        volume_scale=np.maximum(abs(self.Ci*mean)+abs(m.H[:,0]@U),1e-30)
        # Całkowity pęd bryły i gazu; nie projekcja zerująca ruch samej bryły.
        solid_momentum=m.R.T@(m.M@U);fluid_momentum=self.G@deviation/(w*w);external=m.R.T@H
        momentum=-w*w*(solid_momentum+fluid_momentum)-external
        units=np.r_[np.ones(3),np.ones(3)/max(m.outer)]
        momentum_error=float(np.max(np.linalg.norm(units[:,None]*momentum,axis=0)/np.maximum(np.linalg.norm(H,axis=0),1e-30)))
        return dict(f_hz=f,chi=chi,admittance=Y,solid_states=U,pressure_states=P,
            mean_pressure=mean,pressure_deviation_rms=np.sqrt(np.maximum(variance,0)),pressure_volume_rms=np.sqrt(np.maximum(norm,0)),
            maximum_nodal_pressure_rms=np.max(abs(P),axis=0),
            solid_loss_matrix=loss,fluid_average_power=np.real(np.sum(P.conj()*(s*self.B.T@U),axis=0)),
            solid_strain_energy_avg=.5*np.einsum('ij,ij->j',relative.conj(),m.K@relative).real,
            solid_kinetic_energy_avg=.5*w*w*np.einsum('ij,ij->j',U.conj(),m.M@U).real,
            fluid_potential_energy_avg=.5*np.einsum('ij,ij->j',P.conj(),self.C@P).real,
            fluid_kinetic_energy_avg=.5/(w*w)*np.einsum('ij,ij->j',deviation.conj(),spatial_scale*self.A@deviation).real,
            energy_residual=energy_error,mechanical_residual=mech_error,acoustic_residual=acoustic_error,
            mean_volume_residual=float(max(abs(volume_residual)/volume_scale)),momentum_residual=momentum_error,
            mean_lagrange_absolute_residual=float(max(abs(raw_mean_lagrange_error))),
            reciprocity_residual=float(np.linalg.norm(chi-chi.T)/max(np.linalg.norm(chi),1e-30)))
