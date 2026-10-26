"""Lokalny model3D ze zgodnymi siatkami spoin i polem globalnym Q1.

SI; jednostronny transfer global->lokalny, bez sprzężenia zwrotnego.
Nieruchome odcinki cięcia: przemieszczenia; stopy: znane trakcje globalne.
"""
from pathlib import Path
import numpy as np
from scipy import sparse
from scipy.interpolate import RegularGridInterpolator
from scipy.spatial import cKDTree
from element_brylowy_P18C import isotropic_D,quad_quadrature
from model_ramy_3D_P18C import block_panel,BondPiece,clip_rectangle,polygon_quadrature,inverse_quad,skew


def segmented_grid(points,step):
    return np.r_[points[0],np.concatenate([np.linspace(a,b,max(1,int(np.ceil((b-a)/step)))+1)[1:]
                                          for a,b in zip(points[:-1],points[1:])])]


class ParentField:
    def __init__(self,path,n,section,remove_rigid=True):
        with np.load(path,allow_pickle=False) as f:self.data={k:f[k] for k in f.files}
        self.n=n;self.section=section;self.h=.022;self.inside=(.46,.64,.46)
        self.raw_u=self.data['q_combined_m_rad'][:3*len(self.data['xyz_m'])].reshape(-1,3)
        self.shift=np.zeros(6)
        if remove_rigid:
            R=self.data['rigid_modes'][:self.raw_u.size]
            self.shift=np.linalg.lstsq(R,self.raw_u.ravel(),rcond=None)[0]
            self.u=self.raw_u-(R@self.shift).reshape(-1,3)
        else:self.u=self.raw_u.copy()
        self._prepare()

    def _prepare(self):
        self.panels={};self.interpolators={};self.raw_interpolators={}
        for name,offset,count in zip(self.data['panel_names'],self.data['panel_offsets'],self.data['panel_node_counts']):
            offset,count=int(offset),int(count);xyz=self.data['xyz_m'][offset:offset+count]
            self.panels[str(name)]=dict(xyz=xyz,offset=offset,count=count)
            if name in ['bottom','cleat']:
                axes=[np.unique(xyz[:,i]) for i in range(3)];x,y,z=axes
                expected=np.array([(xx,yy,zz) for zz in z for yy in y for xx in x])
                assert np.allclose(xyz,expected,rtol=0,atol=1e-12)
                shape=(len(z),len(y),len(x),3)
                self.interpolators[str(name)]=RegularGridInterpolator((z,y,x),self.u[offset:offset+count].reshape(shape),bounds_error=True)
                self.raw_interpolators[str(name)]=RegularGridInterpolator((z,y,x),self.raw_u[offset:offset+count].reshape(shape),bounds_error=True)
        p=self.panels['front'];self.nt=4*self.n;self.nr=max(3,self.n//2)
        nn=(self.nr+1)*self.nt;assert p['count']==3*nn
        self.front_nn=nn;self.front_xy=p['xyz'][:nn][:,[0,2]]
        self.front_quads=np.array([[i*self.nt+j,(i+1)*self.nt+j,(i+1)*self.nt+(j+1)%self.nt,i*self.nt+(j+1)%self.nt]
                                  for i in range(self.nr) for j in range(self.nt)])
        self.front_tree=cKDTree(self.front_xy[self.front_quads].mean(axis=1))
        offset=p['offset'];self.front_u=self.u[offset:offset+p['count']].reshape(3,nn,3)
        # Wyjściowy front ma warstwy y=h,h/2,0; odwracamy do porządku rosnącego.
        self.front_y=p['xyz'][::nn,1][::-1];self.front_u=self.front_u[::-1]

    def synthetic_affine(self,A,b):
        """Tylko kontrola interpolacji, bez zmiany plików źródłowych."""
        self.u=self.data['xyz_m']@np.asarray(A).T+np.asarray(b)
        self.raw_u=self.u.copy();self.shift=np.zeros(6);self._prepare()

    def evaluate(self,name,points,raw=False):
        points=np.asarray(points)
        if name in ['bottom','cleat']:
            return (self.raw_interpolators if raw else self.interpolators)[name](points[:,[2,1,0]])
        if name!='front' or raw:raise ValueError('Obsługiwane front/bottom/cleat; raw tylko prostokąty')
        values=[]
        for point in points:
            _,near=self.front_tree.query(point[[0,2]],k=16)
            for idx in np.atleast_1d(near):
                ids=self.front_quads[idx];xy=self.front_xy[ids]
                try:N=inverse_quad(xy,point[[0,2]])
                except ValueError:continue
                if np.linalg.norm(N@xy-point[[0,2]])>1e-10:continue
                if not -1e-12<=point[1]<=self.h+1e-12:raise ValueError('y poza grubością frontu')
                layer=min(1,max(0,int(np.searchsorted(self.front_y,point[1],side='right')-1)))
                r=(point[1]-self.front_y[layer])/(self.front_y[layer+1]-self.front_y[layer])
                values.append((1-r)*(N@self.front_u[layer,ids])+r*(N@self.front_u[layer+1,ids]));break
            else:raise ValueError(('Brak elementu frontu',point.tolist()))
        return np.asarray(values)

    def foot_tractions(self,k=(1e4,1e4,1e5),size=.04):
        W,D,H=self.inside;h=self.h;records=[]
        p=self.panels['bottom'];xx=np.unique(p['xyz'][:,0]);yy=np.unique(p['xyz'][:,1])
        z,w=np.polynomial.legendre.leggauss(2)
        for a in [.15,.85]:
            for b in [.15,.85]:
                center=np.array([h+W*a,h+D*b]);lo=center-size/2;hi=center+size/2
                x=np.r_[lo[0],xx[(xx>lo[0])&(xx<hi[0])],hi[0]]
                y=np.r_[lo[1],yy[(yy>lo[1])&(yy<hi[1])],hi[1]]
                integral=np.zeros(3)
                for x0,x1 in zip(x[:-1],x[1:]):
                    for y0,y1 in zip(y[:-1],y[1:]):
                        points=np.array([[(x0+x1)/2+zx*(x1-x0)/2,(y0+y1)/2+zy*(y1-y0)/2,0.] for zx in z for zy in z])
                        weights=np.array([wx*wy for wx in w for wy in w])*(x1-x0)*(y1-y0)/4
                        integral+=weights@self.evaluate('bottom',points,raw=True)
                traction=-np.array(k)*integral/size**4
                records.append(dict(lo=lo,hi=hi,traction=traction,force=traction*size**2))
        return records


class LocalJoint:
    def __init__(self,cfg,domain,section,step,nx=8):
        self.cfg=cfg;self.h=h=cfg['wall_thickness_m'];self.section=section;self.domain=domain
        center=cfg['center_x_m'];self.x0=center-domain['half_width_x_m'];self.x1=center+domain['half_width_x_m']
        self.ycut=domain['rear_y_m'];self.zcut=domain['top_z_m']
        # Obrzeża i miejsca mocowania kosza muszą pozostać poza podmodelem.
        nearest=np.clip([.252,.252],[self.x0,0],[self.x1,self.zcut])
        assert np.linalg.norm(np.array([.252,.252])-nearest)>.1526
        for phi in np.arange(8)*2*np.pi/8:
            point=np.array([.252,.252])+.1621*np.array([np.cos(phi),np.sin(phi)])
            nearest=np.clip(point,[self.x0,0],[self.x1,self.zcut]);assert np.linalg.norm(point-nearest)>.004
        x=np.linspace(self.x0,self.x1,nx+1)
        th=segmented_grid([0,h],step);arm=segmented_grid([h,h+section],step)
        y=segmented_grid([h,h+section,self.ycut],step);z=segmented_grid([0,h,h+section,self.zcut],step)
        D=isotropic_D(cfg['E_mdf_pa'],cfg['nu_mdf_assumed']);rho=cfg['rho_mdf_kg_m3']
        self.panels=[block_panel('front',[x,th,z],D,rho),block_panel('bottom',[x,y,th],D,rho),block_panel('cleat',[x,arm,arm],D,rho)]
        count=0
        for p in self.panels:p.offset=count;count+=len(p.xyz)
        self.nnode=count;self.ndof=3*count;self.xyz=np.vstack([p.xyz for p in self.panels]);self.byname={p.name:p for p in self.panels}
        self.K=sparse.block_diag([p.K for p in self.panels],format='csr');self.M=sparse.block_diag([p.M for p in self.panels],format='csr')
        E,t,nu=cfg['E_glue_pa'],cfg['glue_thickness_m'],cfg['nu_glue_assumed'];self.kn=E/t;self.ks=E/(2*(1+nu)*t)
        self.bonds=[]
        self.match('front','bottom',1,h,'front_bottom')
        self.match('front','cleat',1,h,'front_cleat')
        self.match('bottom','cleat',2,h,'bottom_cleat')
        self.K+=sum((p.matrix(self.ndof) for p in self.bonds),sparse.csr_matrix(self.K.shape))
        self.R=np.zeros((self.ndof,6))
        for i,r in enumerate(self.xyz):self.R[3*i:3*i+3,:3]=np.eye(3);self.R[3*i:3*i+3,3:]=-skew(r)
        self.rigid_error=float(np.linalg.norm(self.K@self.R)/np.linalg.norm(self.K.data))
        assert self.rigid_error<1e-12

    def match(self,a,b,axis,value,name):
        first,second=self.byname[a],self.byname[b]
        faces1=first.faces(axis,value);faces2=second.faces(axis,value)
        key=lambda pts:tuple(sorted(map(tuple,np.round(pts,12))))
        lookup={key(second.xyz[f]):f for f in faces2}
        for f in faces1:
            if key(first.xyz[f]) not in lookup:continue
            g=lookup[key(first.xyz[f])];pts=first.xyz[f]
            perm=np.argmin(np.linalg.norm(pts[:,None]-second.xyz[g][None,:],axis=2),axis=1)
            assert len(set(perm))==4 and np.max(abs(pts-second.xyz[g[perm]]))<1e-11
            L=np.zeros((8,8));area=0.
            for N,p,w in quad_quadrature(pts):
                d=np.r_[N,-N];L+=w*np.outer(d,d);area+=w
            self.bonds.append(BondPiece(name,np.r_[first.offset+f,second.offset+g[perm]],L,area,axis,self.kn,self.ks))
        expected=(self.x1-self.x0)*(self.h if name=='front_bottom' else self.section)
        found=sum(p.area for p in self.bonds if p.name==name);assert abs(found/expected-1)<1e-10

    def surface_load(self,p,faces,traction):
        F=np.zeros(self.ndof)
        for face in faces:
            for N,point,w in quad_quadrature(p.xyz[face]):
                ids=(3*(p.offset+face)[:,None]+np.arange(3)).ravel();np.add.at(F,ids,np.outer(N,traction).ravel()*w)
        return F

    def loads_and_boundary(self,parent):
        h,b=self.h,self.section;front,bottom,cleat=self.panels
        pressure=np.zeros(self.ndof)
        for panel,axis,value,other,minimum in [(front,1,h,2,h+b),(bottom,2,h,1,h+b),(cleat,1,h+b,None,None),(cleat,2,h+b,None,None)]:
            faces=panel.faces(axis,value)
            if other is not None:faces=faces[panel.xyz[faces].mean(axis=1)[:,other]>minimum-1e-12]
            pressure+=self.surface_load(panel,faces,-np.eye(3)[axis])*self.cfg['static_pressure_pa']
        F=self.M@np.tile([0.,0.,-9.80665],self.nnode)+pressure
        feet=parent.foot_tractions(self.cfg['floor_k_xyz_n_m'],self.cfg['floor_patch_size_m']);local_foot_force=np.zeros(3)
        for foot in feet:
            for face in bottom.faces(2,0):
                xy=bottom.xyz[face][:,:2];poly=clip_rectangle(xy,foot['lo'],foot['hi'])
                if len(poly)<3:continue
                for point,w in polygon_quadrature(poly,3):
                    N=inverse_quad(xy,point);ids=(3*(bottom.offset+face)[:,None]+np.arange(3)).ravel()
                    np.add.at(F,ids,np.outer(N,foot['traction']).ravel()*w);local_foot_force+=foot['traction']*w
        fixed=[];values=[];max_interpolation_error=0.
        for p in self.panels:
            cut=np.isclose(p.xyz[:,0],self.x0)|np.isclose(p.xyz[:,0],self.x1)
            if p.name=='front':cut|=np.isclose(p.xyz[:,2],self.zcut)
            if p.name=='bottom':cut|=np.isclose(p.xyz[:,1],self.ycut)
            nodes=np.flatnonzero(cut);fixed.extend((3*(p.offset+nodes)[:,None]+np.arange(3)).ravel())
            values.extend(parent.evaluate(p.name,p.xyz[nodes]).ravel())
        return F,np.array(fixed,int),np.array(values),local_foot_force,feet

    def observations(self,q):
        cfg=self.cfg;records=[]
        for name in ['front_bottom','front_cleat','bottom_cleat']:
            for trimmed in [False,True]:
                width=self.h if name=='front_bottom' else self.section
                start=0. if name=='front_bottom' else self.h
                trim=cfg['diagnostic_trim_m'] if trimmed else 0.
                lo=np.array([cfg['observation_window_x_m'][0],start+trim])
                hi=np.array([cfg['observation_window_x_m'][1],start+width-trim])
                area=positive=negative=shear=0.;peak=0.
                for piece in self.bonds:
                    if piece.name!=name:continue
                    axis=piece.normal_axis;other=[a for a in range(3) if a!=axis]
                    xy=self.xyz[piece.nodes[:4]][:,other];poly=clip_rectangle(xy,lo,hi)
                    if len(poly)<3:continue
                    uu=q[(3*piece.nodes[:,None]+np.arange(3)).ravel()].reshape(8,3)
                    for point,w in polygon_quadrature(poly,4):
                        N=inverse_quad(xy,point);jump=N@(uu[:4]-uu[4:]);traction=jump*self.ks;traction[axis]=jump[axis]*self.kn
                        normal=-traction[axis];area+=w;positive+=w*max(normal,0)**2;negative+=w*min(normal,0)**2
                        shear+=w*sum(traction[a]**2 for a in other);peak=max(peak,normal)
                assert abs(area/np.prod(hi-lo)-1)<1e-9
                records.append(dict(joint=name,window='TRIM5MM' if trimmed else 'FULL_STRIP',area_m2=area,
                    tension_rms_pa=np.sqrt(positive/area),compression_rms_pa=np.sqrt(negative/area),
                    shear_rms_pa=np.sqrt(shear/area),sampled_maximum_tension_pa=peak))
        return records
