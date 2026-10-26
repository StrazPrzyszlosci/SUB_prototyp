"""Zamknięta bryła3D: sześć ścian, rzeczywiste warstwy kleju i dwa porty.

H_i daje delta objętości gazu, H_o daje minus delta objętości obrysu.
Oba są portami pracy siły ciśnienia. Nie wolno z góry przyjąć H_i=-H_o.
Geometria parametryczna bez narzędzi CAD; małe odkształcenia, SI.
"""
from collections import Counter
from itertools import product
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import splu,eigsh
from scipy.linalg import qr
from element_brylowy_P18C import hex8,isotropic_D,quad_quadrature,gauss_stress
from model_ramy_3D_P18C import FACES,skew


def subdivide(breaks,max_step):
    breaks=np.unique(np.round(breaks,12));result=[breaks[0]]
    for a,b in zip(breaks[:-1],breaks[1:]):
        count=max(1,int(np.ceil((b-a)/max_step-1e-10)))
        result.extend(np.linspace(a,b,count+1)[1:])
    return np.array(result)


class SolidModule:
    def __init__(self,base,cfg,resolution=4,braced=True,glue_E=1.718e9,wall_elements=None,glue_elements=None,homogeneous=False):
        self.base=base;self.cfg=cfg;self.outer=np.array(cfg['outer_width_depth_height_m'],float);self.wall=t=cfg['wall_m']
        self.braced=braced;self.resolution=resolution;self.glue_E=glue_E;self.homogeneous=homogeneous
        self.g=g=cfg['glue_thickness_m_assumed'];A,D,H=self.outer
        self.inner=self.outer-2*t;self.outer_volume=float(np.prod(self.outer))
        self.E=E=base['mdf_E_pa_assumed'];self.nu=nu=base['mdf_nu_assumed'];self.rho=rho=base['mdf_density_kg_m3_assumed']
        self.glue_nu=nu if homogeneous else cfg['glue_nu_assumed'];self.glue_rho=rho if homogeneous else cfg['glue_density_kg_m3_assumed']
        self.glue_E=E if homogeneous else glue_E
        self.wall_elements=nt=cfg['wall_elements'] if wall_elements is None else wall_elements
        self.glue_elements=ng=cfg['glue_elements'] if glue_elements is None else glue_elements
        tie=base['internal_tie_reference'];self.pad_side=ps=tie['pad_side_m'];self.pad_t=pt=tie['pad_thickness_m']
        self.rod_side=rs=np.sqrt(tie['rod_area_m2'])
        if min(self.inner)<=2*g+2*pt or min(self.inner[[0,2]])<=ps:raise ValueError('Geometria dodatnia ze ściągiem')
        # Dwie warstwy y przy końcach: ściana-pad i pad-pręt.
        self.tie_y=np.array([t,t+g,t+g+pt,t+2*g+pt,D-t-2*g-pt,D-t-g-pt,D-t-g,D-t])
        breaks=[];max_step=min(self.outer)/resolution
        for axis,L in enumerate(self.outer):
            vals=[0.,t,L-t,L]
            vals.extend(np.linspace(0,t,nt+1));vals.extend(np.linspace(L-t,L,nt+1))
            if axis==1:
                for a,b in [(t,t+g),(L-t-g,L-t)]:vals.extend(np.linspace(a,b,ng+1))
                if braced:
                    vals.extend(self.tie_y)
                    for a,b in [(t+g,t+g+pt),(L-t-g-pt,L-t-g)]:vals.extend(np.linspace(a,b,nt+1))
                    for a,b in [(t+g+pt,t+2*g+pt),(L-t-2*g-pt,L-t-g-pt)]:vals.extend(np.linspace(a,b,ng+1))
            elif axis==2:
                for a,b in [(t,t+g),(L-t-g,L-t)]:vals.extend(np.linspace(a,b,ng+1))
            if braced and axis in [0,2]:vals.extend([L/2-ps/2,L/2-rs/2,L/2+rs/2,L/2+ps/2])
            breaks.append(subdivide(vals,max_step))
        self.axes=breaks;x,y,z=breaks;nx,ny,nz=[len(v) for v in breaks]
        all_xyz=np.array([(xx,yy,zz) for zz in z for yy in y for xx in x]);cells=[];labels=[];sizes=[];centers=[]
        for k,j,i in product(range(nz-1),range(ny-1),range(nx-1)):
            center=np.array([(x[i]+x[i+1])/2,(y[j]+y[j+1])/2,(z[k]+z[k+1])/2]);label=self.material_at(center)
            if label is None:continue
            q=k*nx*ny+j*nx+i
            cells.append([q,q+1,q+nx+1,q+nx,q+nx*ny,q+nx*ny+1,q+nx*ny+nx+1,q+nx*ny+nx])
            labels.append(label);sizes.append([x[i+1]-x[i],y[j+1]-y[j],z[k+1]-z[k]]);centers.append(center)
        old=np.array(cells,int);used=np.unique(old);remap=np.full(len(all_xyz),-1,int);remap[used]=np.arange(len(used))
        self.xyz=all_xyz[used];self.elements=remap[old];self.labels=np.array(labels);self.sizes=np.array(sizes);self.centers=np.array(centers)
        self.ndof=3*len(self.xyz);self.dofs=(3*self.elements[:,:,None]+np.arange(3)[None,None,:]).reshape(-1,24)
        self.volumes=np.prod(self.sizes,axis=1);self.densities=np.where(self.labels=='mdf',rho,self.glue_rho)
        self.dry_mass=float(self.volumes@self.densities);self.material_volume=float(sum(self.volumes));self.inner_volume=self.outer_volume-self.material_volume
        self.mdf_volume=float(sum(self.volumes[self.labels=='mdf']));self.glue_volume=float(sum(self.volumes[self.labels=='glue']))
        self.Kparts={};self.Mparts={};cache={};self.stress_cache={};self.material_tensors={}
        for label,modulus,poisson,density in [('mdf',E,nu,rho),('glue',self.glue_E,self.glue_nu,self.glue_rho)]:
            ids=np.flatnonzero(self.labels==label);ks=[];ms=[];Dmat=isotropic_D(modulus,poisson);self.material_tensors[label]=Dmat
            for idx in ids:
                length=np.round(self.sizes[idx],12);key=(label,tuple(length))
                if key not in cache:
                    pts=self.xyz[self.elements[idx]]-self.xyz[self.elements[idx,0]]
                    K,M,meta=hex8(pts,Dmat,density,True);cache[key]=(K.ravel(),M.ravel());self.stress_cache[key]=meta
                K,M=cache[key];ks.append(K);ms.append(M)
            dofs=self.dofs[ids];rr=np.repeat(dofs,24,axis=1).ravel();cc=np.tile(dofs,(1,24)).ravel()
            def matrix(v):
                a=sparse.coo_matrix((np.ravel(v),(rr,cc)),shape=(self.ndof,self.ndof)).tocsr();a.eliminate_zeros();return a
            self.Kparts[label]=matrix(ks);self.Mparts[label]=matrix(ms)
        self.K=self.Kparts['mdf']+self.Kparts['glue'];self.M=self.Mparts['mdf']+self.Mparts['glue']
        self.beta=2*cfg['material_loss_zeta_at_reference_assumed']/(2*np.pi*cfg['material_loss_reference_hz'])
        self.C=self.beta*self.K
        # Powierzchnie unii po odrzuceniu wszystkich wspólnych ścian komórek.
        faces=[tuple(ids[face]) for ids in self.elements for face in FACES];count=Counter(tuple(sorted(f)) for f in faces)
        exposed=[face for face in faces if count[tuple(sorted(face))]==1]
        self.H=np.zeros((self.ndof,2));self.surface_area=np.zeros(2);self.boundary=[]
        for face in exposed:
            points=self.xyz[list(face)];spread=np.ptp(points,axis=0);axis=int(np.argmin(spread));assert spread[axis]<1e-10
            value=points[0,axis];external=abs(value)<1e-10 or abs(value-self.outer[axis])<1e-10
            # H_i: normalna z gazu do ciała. H_o: normalna z otoczenia do ciała.
            if external:sign=1 if abs(value)<1e-10 else -1
            else:
                # Każda odsłonięta powierzchnia jest ścianą jednego sąsiedniego elementu.
                sign=None
            self.boundary.append([np.array(face),axis,value,1 if external else 0,sign])
        # Właściciel pozwala jednoznacznie wyznaczyć normalną także przy ściągu.
        owner={tuple(sorted(ids[face])):idx for idx,ids in enumerate(self.elements) for face in FACES}
        for face,axis,value,port,sign in self.boundary:
            points=self.xyz[face]
            if sign is None:sign=1 if value<self.centers[owner[tuple(sorted(face))],axis] else -1
            traction=np.eye(3)[axis]*sign
            for N,point,area in quad_quadrature(points,order=2):
                np.add.at(self.H[:,port],(3*face[:,None]+np.arange(3)).ravel(),np.outer(N,traction).ravel()*area)
                self.surface_area[port]+=area
        self.R=np.zeros((self.ndof,6))
        for i,r in enumerate(self.xyz):self.R[3*i:3*i+3,:3]=np.eye(3);self.R[3*i:3*i+3,3:]=-skew(r)
        self.mass_rigid=self.R.T@(self.M@self.R)
        _,_,pivot=qr(self.R.T,pivoting=True,mode='economic');self.fixed=pivot[:6];self.free=np.setdiff1d(np.arange(self.ndof),self.fixed)
        self._static=None

    def material_at(self,point):
        x,y,z=point;A,D,H=self.outer;t,g=self.wall,self.g
        # MDF endcaps, annular end bonds, horizontal side bonds and side panels.
        if y<t or y>D-t:return 'mdf'
        shell=x<t or x>A-t or z<t or z>H-t
        if shell:
            if y<t+g or y>D-t-g:return 'glue'
            if z<t or z>H-t:return 'mdf'
            if z<t+g or z>H-t-g:return 'glue'
            return 'mdf'
        if not self.braced:return None
        pad=abs(x-A/2)<self.pad_side/2 and abs(z-H/2)<self.pad_side/2
        rod=abs(x-A/2)<self.rod_side/2 and abs(z-H/2)<self.rod_side/2
        a,b,c,d,e,f,h,i=self.tie_y
        if pad and (a<y<b or h<y<i):return 'glue'
        if pad and (b<y<c or f<y<h):return 'mdf'
        if rod and (c<y<d or e<y<f):return 'glue'
        if rod and d<y<e:return 'mdf'
        return None

    def nominal_budgets(self):
        A,D,H=self.outer;t,g=self.wall,self.g;ps,pt,rs=self.pad_side,self.pad_t,self.rod_side
        empty=float(np.prod(self.inner));shell=self.outer_volume-empty
        glue_shell=2*g*(A*H-(A-2*t)*(H-2*t))+4*t*g*(D-2*t-2*g)
        tie_mdf=2*ps**2*pt+rs**2*(D-2*t-2*pt-4*g) if self.braced else 0.
        tie_glue=2*g*(ps**2+rs**2) if self.braced else 0.
        return dict(mdf_volume_m3=shell-glue_shell+tie_mdf,glue_volume_m3=glue_shell+tie_glue,
                    inner_air_m3=empty-tie_mdf-tie_glue,
                    dry_mass_kg=(shell-glue_shell+tie_mdf)*self.rho+(glue_shell+tie_glue)*self.glue_rho)

    def glue_group(self,point):
        x,y,z=point;A,D,H=self.outer;t,g=self.wall,self.g
        shell=x<t or x>A-t or z<t or z>H-t
        if shell:
            if y<t+g or y>D-t-g:
                end='front' if y<D/2 else 'back'
                side='bottom' if z<t else 'top' if z>H-t else 'left' if x<t else 'right'
                return end+'_'+side,1
            return ('left' if x<A/2 else 'right')+'_'+('bottom' if z<H/2 else 'top'),2
        a,b,c,d,e,f,h,i=self.tie_y
        wall=y<b or y>h
        return 'tie_'+('wall_' if wall else 'rod_')+('front' if y<D/2 else 'back'),1

    def static_glue_stress(self,q):
        """Przestrzenne RMS/wybrane maksima w punktach Gaussa, nie nośność."""
        groups={}
        for idx in np.flatnonzero(self.labels=='glue'):
            length=np.round(self.sizes[idx],12);key=('glue',tuple(length));meta=self.stress_cache[key]
            stress=gauss_stress(self.xyz[self.elements[idx]],self.material_tensors['glue'],q[self.dofs[idx]],meta)
            name,axis=self.glue_group(self.centers[idx]);normal=stress[:,axis]
            tangential=[3 if sorted((axis,j))==[0,1] else 4 if sorted((axis,j))==[1,2] else 5 for j in range(3) if j!=axis]
            weights=np.array([v[-1] for v in meta['points']]);item=groups.setdefault(name,dict(volume=0.,normal2=0.,positive2=0.,shear2=0.,gauss_positive_max=0.))
            item['volume']+=sum(weights);item['normal2']+=weights@(normal**2);item['positive2']+=weights@(np.maximum(normal,0)**2)
            item['shear2']+=weights@np.sum(stress[:,tangential]**2,axis=1)
            item['gauss_positive_max']=max(item['gauss_positive_max'],float(max(normal.max(),0.)))
        return [dict(joint=name,volume_m3=v['volume'],nominal_area_m2=v['volume']/self.g,
            spatial_normal_rms_pa=float(np.sqrt(v['normal2']/v['volume'])),spatial_positive_normal_rms_pa=float(np.sqrt(v['positive2']/v['volume'])),
            spatial_shear_rms_pa=float(np.sqrt(v['shear2']/v['volume'])),sampled_gauss_positive_normal_max_pa=v['gauss_positive_max']) for name,v in sorted(groups.items())]

    def static(self):
        if self._static is None:
            lu=splu(self.K[self.free][:,self.free].tocsc());q=np.zeros_like(self.H)
            q[self.free]=lu.solve(self.H[self.free]);q-=self.R@np.linalg.solve(self.mass_rigid,self.R.T@(self.M@q))
            self._static=q
        return self.H.T@self._static,self._static

    def direct(self,frequencies):
        chi=[];states=[];loss=[];res=[]
        for f in frequencies:
            s=2j*np.pi*f;D=((1+s*self.beta)*self.K+s*s*self.M).tocsc();q=splu(D).solve(self.H.astype(complex))
            c=self.H.T@q;chi.append(c);states.append(q)
            P=(2*np.pi*f)**2*(q.conj().T@(self.C@q));loss.append(P)
            target=(s*c+(s*c).conj().T)/2
            residual=float(np.linalg.norm(target-P)/max(np.linalg.norm(s*c),1e-30));res.append(residual)
        return dict(chi=np.array(chi),states=states,loss=np.array(loss),power_residual=max(res))

    def modes(self,count=24):
        values,V=eigsh(self.K,k=count+6,M=self.M,sigma=-(2*np.pi*5)**2,which='LM',v0=np.sin(np.arange(self.ndof)+1))
        order=np.argsort(values);values=values[order];V=V[:,order]
        scale=values[6];assert np.max(abs(values[:6]))<1e-5*scale and scale>0
        return values[6:],V[:,6:],values[:6]


def gas_port(f,chi,Ci,G=0.):
    """Redukcja gazu/przecieku z pełnej wzajemnej macierzy dwóch portów.

    Przy G→inf strumień G*(po-pi) może być skończony mimo pi/po→1.
    Pozostaje podatność gazu ORAZ ściskania całego materiału.
    """
    s=2j*np.pi*np.asarray(f,float);chi=np.asarray(chi);cii=chi[:,0,0];cio=chi[:,0,1];coi=chi[:,1,0];coo=chi[:,1,1]
    if np.isposinf(G):
        ratio=np.ones_like(s);difference=np.zeros_like(s)
        Y=s*(Ci+cii+cio+coi+coo)
    else:
        den=G+s*(Ci+cii);ratio=(G-s*cio)/den;difference=s*(Ci+cii+cio)/den
        Y=s*(coo+coi*ratio)+G*difference
    return dict(admittance=Y,inside_to_outer_pressure=ratio,pressure_difference=difference)
