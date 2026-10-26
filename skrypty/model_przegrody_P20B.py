"""P20B: płyta/przesuw ramy albo4łaty,pełna masa i dodatnie tłumienie.

W perymetrycznym modelu rama+ugięcie są współrzędnymi tego samego ciała:
uwzględniamy masę krzyżową,nie sumę dwóch niezależnych oscylatorów.
"""
import numpy as np
from scipy.linalg import eigh
from scipy import sparse
from model_plyty_MITC_P18 import RectangularPlate,PlateMaterial


def edge_average(plate):
    v=np.zeros(len(plate.full_F));nx,ny=plate.nx,plate.ny;perimeter=2*(plate.a+plate.b)
    pairs=[]
    for j in range(ny):pairs += [(j*(nx+1),(j+1)*(nx+1),plate.dy),
                                 (j*(nx+1)+nx,(j+1)*(nx+1)+nx,plate.dy)]
    for i in range(nx):pairs += [(i,i+1,plate.dx),(ny*(nx+1)+i,ny*(nx+1)+i+1,plate.dx)]
    for a,b,length in pairs:v[3*a]+=length/(2*perimeter);v[3*b]+=length/(2*perimeter)
    assert abs(sum(v)-1)<1e-12
    return v[plate.free]


class Partition:
    def __init__(self,base,cfg,thickness,kind='PERIM',boundary='CCCC',support_each=np.inf,n=None):
        W,D,H=base['inside_width_depth_height_m'];gap=cfg['panel_edge_clearance_m_assumed']
        self.a=W-2*gap;self.b=H-2*gap;self.area=W*H;self.thickness=thickness
        self.kind=kind;self.boundary=boundary;self.k_each=support_each;self.cfg=cfg;self.base=base
        rho,E,nu=base['mdf_density_kg_m3_assumed'],base['mdf_E_pa_assumed'],base['mdf_nu_assumed']
        self.plate_mass=rho*self.a*self.b*thickness
        self.seal_volume=(self.area-self.a*self.b)*thickness
        self.seal_mass=cfg['seal_density_kg_m3_assumed']*self.seal_volume
        self.carriage_mass=cfg['moving_carriage_mass_kg_assumed']
        self.total_mass=self.plate_mass+self.seal_mass+self.carriage_mass
        mesh=cfg['plate_mesh_intervals'] if n is None else n
        p=RectangularPlate(self.a,self.b,mesh,mesh,PlateMaterial(E,nu,rho,thickness),boundary='FREE' if kind=='PATCH4' else boundary)
        self.p=p;self.beta=2*cfg['material_loss_zeta_at_reference_assumed']/(2*np.pi*cfg['material_loss_reference_hz'])
        self.edge=edge_average(p);self.mass_cross_error=0.;self.rigid_mass_error=0.
        if kind=='PATCH4':
            if not np.isfinite(support_each):raise ValueError('Cztery łaty wymagają skończonej sztywności')
            dx,dz=cfg['support_offset_from_center_m'];size=cfg['support_patch_side_m_assumed']
            patches=np.array([p.patch_average((p.a/2+ix*dx,p.b/2+iz*dz),(size,size)) for ix,iz in [(-1,-1),(1,-1),(-1,1),(1,1)]])
            mean=patches.mean(axis=0)
            self.Kplate=p.K.toarray();self.M=p.M.toarray()+self.seal_mass*np.outer(self.edge,self.edge)+self.carriage_mass*np.outer(mean,mean)
            self.support_vectors=np.sqrt(support_each)*patches.T
            self.Ksupport=self.support_vectors@self.support_vectors.T;self.K=self.Kplate+self.Ksupport
            self.F=p.F+(self.area-p.a*p.b)*self.edge
            rigid=np.zeros(len(p.full_F));rigid[0::3]=1
            self.rigid_mass_error=abs(rigid@self.M@rigid/self.total_mass-1)
            assert self.rigid_mass_error<1e-11
            self.patches=patches;self.moving_frame=False
        elif kind=='PERIM' and np.isfinite(support_each):
            N=p.K.shape[0];self.Kplate=np.zeros((N+1,N+1));self.Kplate[1:,1:]=p.K.toarray()
            self.Ksupport=np.zeros_like(self.Kplate);self.Ksupport[0,0]=4*support_each;self.K=self.Kplate+self.Ksupport
            self.support_vectors=np.zeros((N+1,1));self.support_vectors[0,0]=np.sqrt(4*support_each)
            self.M=np.zeros_like(self.Kplate);self.M[0,0]=self.total_mass
            self.M[1:,1:]=p.M.toarray();self.M[0,1:]=self.M[1:,0]=rho*thickness*p.F
            # Niezależna transformacja pełnej masy nodalnej płyty.
            T=np.zeros((len(p.full_F),N+1));T[0::3,0]=1;T[p.free,np.arange(1,N+1)]=1
            expected=T.T@p.full_M@T;expected[0,0]+=self.seal_mass+self.carriage_mass
            self.mass_cross_error=float(np.linalg.norm(self.M-expected)/np.linalg.norm(expected));assert self.mass_cross_error<1e-12
            self.F=np.r_[self.area,p.F];self.moving_frame=True
        elif kind=='PERIM':
            self.Kplate=p.K.toarray();self.Ksupport=np.zeros_like(self.Kplate);self.K=self.Kplate.copy();self.M=p.M.toarray();self.F=p.F.copy()
            self.support_vectors=np.empty((len(self.F),0));self.moving_frame=False
        else:raise ValueError('PERIM/PATCH4')
        if np.isfinite(support_each):
            w_mount=np.sqrt(4*support_each/self.total_mass)
            self.gamma=2*cfg['support_damping_ratio_assumed']/w_mount
        else:self.gamma=0.
        self.C=self.beta*self.Kplate+self.gamma*self.Ksupport
        values,V=eigh(self.K,self.M);assert values.min()>0
        self.values=values;self.V=V;self.modal_force=V.T@self.F;self.modal_support=V.T@self.support_vectors
        self.static_compliance=float(self.F@np.linalg.solve(self.K,self.F))
        assert abs(np.sum(self.modal_force**2/self.values)/self.static_compliance-1)<1e-7

    def modal_states(self,f):
        f=np.asarray(f,float);states=[]
        for frequency in f:
            s=2j*np.pi*frequency;diagonal=(1+s*self.beta)*self.values+s*s
            base=self.modal_force/diagonal
            W=self.modal_support
            coefficient=s*(self.gamma-self.beta)
            if W.shape[1]:
                U=W/diagonal[:,None];small=np.eye(W.shape[1])+coefficient*(W.T@U)
                base-=coefficient*(U@np.linalg.solve(small,W.T@base))
            states.append(base)
        return np.array(states).T

    def compliance(self,f):
        return self.modal_force@self.modal_states(f)

    def response(self,f):
        q=self.V@self.modal_states(f);chi=self.F@q
        omega=2*np.pi*np.asarray(f);loss=omega**2*np.einsum('ij,ij->j',q.conj(),self.C@q).real
        material_loss=omega**2*np.einsum('ij,ij->j',q.conj(),self.beta*self.Kplate@q).real
        support_loss=omega**2*np.einsum('ij,ij->j',q.conj(),self.gamma*self.Ksupport@q).real
        input_power=np.real(1j*omega*chi)
        error=float(np.max(abs(input_power-loss)/np.maximum(abs(1j*omega*chi),1e-30)));assert error<1e-8
        if self.kind=='PATCH4':
            absolute=self.p.transverse_displacements(q)
            # Dla kwadratowej płyty i symetrycznych łatek pole jest symetryczne.
            # Usuwamy dopasowaną płaszczyznę,aby nie nazwać przesuwu ugięciem.
            A=np.column_stack([np.ones(len(self.p.xy)),self.p.xy])
            relative=absolute-A@np.linalg.lstsq(A,absolute,rcond=None)[0]
            reactions=self.k_each*(1+1j*omega*self.gamma)[None,:]*(self.patches@q)
        elif self.moving_frame:
            absolute=self.p.transverse_displacements(q[1:])+q[0][None,:]
            relative=self.p.transverse_displacements(q[1:])
            reactions=np.tile((self.k_each*(1+1j*omega*self.gamma)*q[0])[None,:],(4,1))
        else:
            absolute=self.p.transverse_displacements(q);relative=absolute
            # Wypadkowa do idealnego obwodu; nie cztery lokalne reakcje.
            mass_motion=self.base['mdf_density_kg_m3_assumed']*self.thickness*(self.p.F@q)
            reactions=(self.area+omega**2*mass_motion)[None,:]/4
        return dict(compliance=chi,states=q,wall_loss_w_per_dp_rms2=loss,power_residual=error,
                    material_loss_w_per_dp_rms2=material_loss,support_loss_w_per_dp_rms2=support_loss,
                    peak_absolute_y_per_pa=np.sqrt(2)*np.max(abs(absolute),axis=0),
                    peak_bending_y_per_pa=np.sqrt(2)*np.max(abs(relative),axis=0),
                    support_force_rms_per_dp=reactions)


def two_chamber(f,Ca,Cb,chi,gseal=0.,gvent=0.):
    """Jednostkowy dopływ do komory przedniej; s=jw,fazoryRMS.

    Dopływ ma znak przeciwny do zewnętrznej objętości membrany.
    Pvent/Qmem = -vent_flow_per_input. Promieniowanie jest osobną diagnostyką.
    """
    s=2j*np.pi*np.asarray(f,float);Ya=s*np.asarray(Ca);Yb=s*np.asarray(Cb)
    B=s*chi+gseal
    seal_inf=np.ndim(gseal)==0 and np.isreal(gseal) and np.isposinf(np.real(gseal))
    vent_inf=np.ndim(gvent)==0 and np.isreal(gvent) and np.isposinf(np.real(gvent))
    if seal_inf and vent_inf:
        z=np.zeros_like(s);pb=np.zeros_like(s);delta=np.zeros_like(s);vent=np.ones_like(s)
    elif seal_inf:
        z=1/(Ya+Yb+gvent);pb=z;delta=np.zeros_like(s);vent=gvent*z
    elif vent_inf:
        z=1/(Ya+B);pb=np.zeros_like(s);delta=z;vent=B*z
    else:
        Yr=Yb+gvent;den=Ya*Yr+B*(Ya+Yr)
        z=(Yr+B)/den;pb=B/den;delta=Yr/den;vent=gvent*pb
    wall_loss=np.real(s*chi)*abs(delta)**2
    seal_loss=np.zeros_like(s.real) if seal_inf else np.real(gseal)*abs(delta)**2
    vent_loss=np.zeros_like(s.real) if vent_inf else np.real(gvent)*abs(pb)**2
    active_loss=np.real(Ya)*abs(z)**2
    rear_loss=np.real(Yb)*abs(pb)**2
    residual=np.real(z)-wall_loss-seal_loss-vent_loss-active_loss-rear_loss
    error=float(np.max(abs(residual)/np.maximum(abs(z),1e-30)))
    assert error<1e-8 and np.min(z.real)>-1e-7
    return dict(input_impedance=z,rear_pressure_per_input=pb,partition_dp_per_input=delta,
                vent_flow_per_input=vent,power_residual=error,
                wall_loss_per_input2=wall_loss,seal_loss_per_input2=seal_loss,
                vent_loss_per_input2=vent_loss,active_loss_per_input2=active_loss,rear_loss_per_input2=rear_loss)
