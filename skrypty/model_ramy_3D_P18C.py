"""Pelna rama:6osobnych bryl,podatne spoiny3D,niezgodne siatki frontu.

BezCAD. Liniowe3D mala deformacja;moduly i spoiny sa referencjami/stresami,
nie identyfikacja partiiMDF. Front ma zbiezną wielokatna krawedz,nie voxele.
"""
from collections import Counter
from dataclasses import dataclass
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve,eigsh
from scipy.spatial import cKDTree
from element_brylowy_P18C import hex8,isotropic_D,transverse_stress_D,quad_shape,quad_quadrature,SIGNS
from model_frontu_z_otworem_P18B import FrontWithHole
from model_plyty_MITC_P18 import PlateMaterial

FACES=np.array([[0,3,7,4],[1,2,6,5],[0,1,5,4],[3,2,6,7],[0,1,2,3],[4,5,6,7]])


def skew(v):
    x,y,z=v;return np.array([[0,-z,y],[z,0,-x],[-y,x,0.]])


class Panel:
    def __init__(self,name,xyz,elements,D,density,enhanced=True):
        self.name=name;self.xyz=np.asarray(xyz);self.elements=np.asarray(elements);self.D=D;self.density=density
        self.ndof=3*len(xyz);self.dofs=(3*self.elements[:,:,None]+np.arange(3)[None,None,:]).reshape(-1,24)
        k=[];m=[];self.volume=0.;cache={}
        for ids in self.elements:
            points=self.xyz[ids];relative=np.round(points-points[0],12);key=relative.tobytes()
            if key not in cache:cache[key]=hex8(relative,D,density,enhanced)
            K,M,meta=cache[key];k.append(K.ravel());m.append(M.ravel());self.volume+=meta['volume_m3']
        rows=np.repeat(self.dofs,24,axis=1).ravel();cols=np.tile(self.dofs,(1,24)).ravel()
        self.K=sparse.coo_matrix((np.ravel(k),(rows,cols)),shape=(self.ndof,self.ndof)).tocsr()
        self.M=sparse.coo_matrix((np.ravel(m),(rows,cols)),shape=(self.ndof,self.ndof)).tocsr()
        allfaces=[tuple(ids[f]) for ids in self.elements for f in FACES];count=Counter(tuple(sorted(f)) for f in allfaces)
        self.boundary=np.array([f for f in allfaces if count[tuple(sorted(f))]==1]);self.offset=0

    def faces(self,axis,value):
        return self.boundary[np.all(np.isclose(self.xyz[self.boundary,axis],value,atol=1e-10),axis=1)]


def block_panel(name,axes,D,density,enhanced=True):
    x,y,z=axes;nx,ny,nz=len(x),len(y),len(z)
    xyz=np.array([(xx,yy,zz) for zz in z for yy in y for xx in x]);elements=[]
    for k in range(nz-1):
        for j in range(ny-1):
            for i in range(nx-1):
                a=k*nx*ny+j*nx+i;elements.append([a,a+1,a+nx+1,a+nx,a+nx*ny,a+nx*ny+1,a+nx*ny+nx+1,a+nx*ny+nx])
    return Panel(name,xyz,elements,D,density,enhanced)


def front_panel(width,height,thickness,radius,n,nr,nt,D,density,enhanced=True):
    mesh=FrontWithHole(width,height,radius,PlateMaterial(2.1e9,.3,density,thickness),n,nr)
    qxy=mesh.xy+np.array([width,height])/2;ys=np.linspace(thickness,0,nt+1);nn=len(qxy)
    xyz=np.array([(x,y,z) for y in ys for x,z in qxy]);elements=[]
    for layer in range(nt):
        for ids in mesh.elements:elements.append(np.r_[ids+layer*nn,ids+(layer+1)*nn])
    p=Panel('front',xyz,elements,D,density,enhanced);p.mesh2d=mesh;p.nn2d=nn;p.nt=nt
    return p


def inverse_quad(xy,point):
    z=np.zeros(2)
    for _ in range(16):
        N,d=quad_shape(*z);step=np.linalg.solve((d@xy).T,N@xy-point);z-=step
        if np.linalg.norm(step)<1e-12:break
    if max(abs(z))>1+1e-7:raise ValueError('Punkt poza wspolna komorka')
    return quad_shape(*z)[0]


def clip_rectangle(poly,lo,hi):
    poly=[np.array(p) for p in poly]
    for axis,bound,sign in [(0,lo[0],1),(0,hi[0],-1),(1,lo[1],1),(1,hi[1],-1)]:
        result=[]
        if not poly:return np.empty((0,2))
        old=poly[-1];old_inside=sign*(old[axis]-bound)>=-1e-13
        for new in poly:
            inside=sign*(new[axis]-bound)>=-1e-13
            if inside!=old_inside:
                t=(bound-old[axis])/(new[axis]-old[axis]);result.append(old+t*(new-old))
            if inside:result.append(new)
            old=new;old_inside=inside
        poly=result
    if len(poly)<3:return np.empty((0,2))
    return np.array(poly)


def polygon_quadrature(poly,order=3):
    center=np.mean(poly,axis=0);z,w=np.polynomial.legendre.leggauss(order);z=(z+1)/2;w=w/2
    for a,b in zip(poly,np.roll(poly,-1,axis=0)):
        det=abs(np.linalg.det(np.stack([a-center,b-center])))
        if det<1e-20:continue
        for i,u in enumerate(z):
            for j,v in enumerate(z):
                point=center+u*(a-center)+(1-u)*v*(b-center)
                yield point,det*(1-u)*w[i]*w[j]


@dataclass
class BondPiece:
    name:str
    nodes:np.ndarray
    L:np.ndarray
    area:float
    normal_axis:int
    kn:float
    ks:float

    def matrix(self,ndof):
        rr=[];cc=[];vv=[]
        for axis,k in enumerate([self.kn if i==self.normal_axis else self.ks for i in range(3)]):
            ids=3*self.nodes+axis;rr.extend(np.repeat(ids,len(ids)));cc.extend(np.tile(ids,len(ids)));vv.extend((k*self.L).ravel())
        return sparse.coo_matrix((vv,(rr,cc)),shape=(ndof,ndof)).tocsr()


class Cabinet3D:
    def __init__(self,inside=(.46,.64,.46),h=.022,n=8,nt=2,front_radius=.1526,
                 bond_kn=8.59e12,bond_ks=3.181481481e12,enhanced=True,with_basket=True,
                 E_pa=2.1e9,nu=.3,density=730.,normal_E_ratio=1.,transverse_G_ratio=1.,
                 basket_normal_stiffness=1e6,basket_tangential_stiffness=1e6):
        W,Dp,H=inside;Wout=W+2*h;Hout=H+2*h;self.inside=inside;self.h=h;self.n=n
        self.enhanced=enhanced;self.radius=front_radius;self.with_basket=with_basket
        self.bond_kn=bond_kn;self.bond_ks=bond_ks
        mats=[transverse_stress_D(E_pa,nu,i,normal_E_ratio,transverse_G_ratio) for i in range(3)];rho=density;th=np.linspace(0,h,nt+1)
        x=np.r_[th,np.linspace(h,W+h,n+1)[1:],W+h+th[1:]]
        z=np.r_[th,np.linspace(h,H+h,n+1)[1:],H+h+th[1:]];y=np.linspace(h,Dp+h,n+1)
        self.panels=[front_panel(Wout,Hout,h,front_radius,n,max(3,n//2),nt,mats[1],rho,enhanced),
                     block_panel('back',[x,np.linspace(Dp+h,Dp+2*h,nt+1),z],mats[1],rho,enhanced),
                     block_panel('left',[th,y,np.linspace(h,H+h,n+1)],mats[0],rho,enhanced),
                     block_panel('right',[W+h+th,y,np.linspace(h,H+h,n+1)],mats[0],rho,enhanced),
                     block_panel('bottom',[x,y,th],mats[2],rho,enhanced),
                     block_panel('top',[x,y,H+h+th],mats[2],rho,enhanced)]
        self.byname={p.name:p for p in self.panels};offset=0
        for p in self.panels:p.offset=offset;offset+=len(p.xyz)
        self.xyz=np.vstack([p.xyz for p in self.panels]);self.nnode=offset;self.ndof=3*offset+(6 if with_basket else 0)
        self.Kmaterial=sparse.block_diag([p.K for p in self.panels]+([sparse.csr_matrix((6,6))] if with_basket else []),format='csr')
        self.M=sparse.block_diag([p.M for p in self.panels]+([sparse.csr_matrix((6,6))] if with_basket else []),format='csr')
        self.bonds=[];self.pressure=np.zeros(self.ndof);self.area_records={}
        # Wszystkie wewnetrzne powierzchnie plus odejmowanie zakrytych spoin.
        definitions=[('front',1,h,-1),('back',1,Dp+h,1),('left',0,h,-1),('right',0,W+h,1),('bottom',2,h,-1),('top',2,H+h,1)]
        for name,axis,value,sign in definitions:
            self.pressure+=self.surface_load(self.byname[name],self.byname[name].faces(axis,value),np.eye(3)[axis]*sign)
        front=self.byname['front']
        # Cisnienie na wielokatnym boku otworu zamknietego przez port kosza.
        for face in front.boundary:
            pts=front.xyz[face];r=np.linalg.norm(pts[:,[0,2]]-np.array([Wout,Hout])/2,axis=1)
            if np.allclose(r,front_radius):
                vector=pts.mean(axis=0)-np.array([Wout/2,pts[:,1].mean(),Hout/2]);vector/=np.linalg.norm(vector)
                self.pressure+=self.surface_load(front,np.array([face]),vector)
        for backname,yvalue,sign in [('front',h,-1),('back',Dp+h,1)]:
            target=self.byname[backname]
            for bodyname in ['left','right','bottom','top']:
                body=self.byname[bodyname];faces=body.faces(1,yvalue)
                if backname=='front':self._front_mortar(target,body,faces,sign)
                else:self._flat_mortar(target,target.faces(1,yvalue),body,faces,1,sign)
        for sidename in ['left','right']:
            side=self.byname[sidename]
            for name,zvalue,sign in [('bottom',h,-1),('top',H+h,1)]:
                top=self.byname[name]
                self._flat_mortar(top,top.faces(2,zvalue),side,side.faces(2,zvalue),2,sign)
        self.Kbond=sum((b.matrix(self.ndof) for b in self.bonds),sparse.csr_matrix((self.ndof,self.ndof)))
        self.K=self.Kmaterial+self.Kbond;self.basket_reference=np.array([Wout/2,0,Hout/2])
        self.basket_mass=0.;self.basket_D=None
        if with_basket:self._add_basket(normal_stiffness=basket_normal_stiffness,tangential_stiffness=basket_tangential_stiffness)
        self.R=self.rigid_modes();self.mass_rigid=self.R.T@(self.M@self.R)
        self.floor_K=sparse.csr_matrix((self.ndof,self.ndof))

    def surface_load(self,p,faces,traction):
        F=np.zeros(self.ndof)
        for face in faces:
            for N,point,area in quad_quadrature(p.xyz[face]):
                ids=(3*(p.offset+face)[:,None]+np.arange(3)).ravel();np.add.at(F,ids,np.outer(N,traction).ravel()*area)
        return F

    def _front_mortar(self,front,body,faces,sign):
        # Dokladna wspolna geometria:przeciecia quadow frontu z prostokatami konca korpusu.
        coords=front.xyz[front.nn2d*0:front.nn2d][:,[0,2]];quads=front.mesh2d.elements
        minq=coords[quads].min(axis=1);maxq=coords[quads].max(axis=1)
        for face in faces:
            bp=body.xyz[face][:,[0,2]];lo=bp.min(axis=0);hi=bp.max(axis=0)
            candidates=np.flatnonzero(np.all(maxq>=lo-1e-12,axis=1)&np.all(minq<=hi+1e-12,axis=1))
            for idx in candidates:
                fq=quads[idx];fp=coords[fq];poly=clip_rectangle(fp,lo,hi)
                if len(poly)<3:continue
                L=np.zeros((8,8));fweight=np.zeros(4);area=0.
                for point,weight in polygon_quadrature(poly):
                    Nf=inverse_quad(fp,point);Nb=inverse_quad(bp,point);d=np.r_[Nf,-Nb]
                    L+=np.outer(d,d)*weight;fweight+=Nf*weight;area+=weight
                if area<1e-18:continue
                nodes=np.r_[front.offset+fq,body.offset+face]
                self.bonds.append(BondPiece('front_'+body.name,nodes,L,area,1,self.bond_kn,self.bond_ks))
                # Warstwa0frontu ma y=h:odejmujemy zakryta powierzchnie z cisnienia.
                self.pressure[3*(front.offset+fq)+1]-=sign*fweight

    def _flat_mortar(self,target,target_faces,body,body_faces,axis,sign):
        other=[a for a in range(3) if a!=axis]
        minq=target.xyz[target_faces][:,:,other].min(axis=1);maxq=target.xyz[target_faces][:,:,other].max(axis=1)
        for bf in body_faces:
            bp=body.xyz[bf][:,other];lo=bp.min(axis=0);hi=bp.max(axis=0)
            for idx in np.flatnonzero(np.all(maxq>=lo-1e-12,axis=1)&np.all(minq<=hi+1e-12,axis=1)):
                tf=target_faces[idx];tp=target.xyz[tf][:,other];poly=clip_rectangle(tp,lo,hi)
                if len(poly)<3:continue
                L=np.zeros((8,8));fw=np.zeros(4);area=0.
                for point,weight in polygon_quadrature(poly):
                    Nt=inverse_quad(tp,point);Nb=inverse_quad(bp,point);d=np.r_[Nt,-Nb]
                    L+=np.outer(d,d)*weight;fw+=Nt*weight;area+=weight
                if area<1e-18:continue
                nodes=np.r_[target.offset+tf,body.offset+bf]
                self.bonds.append(BondPiece(target.name+'_'+body.name,nodes,L,area,axis,self.bond_kn,self.bond_ks))
                self.pressure[3*(target.offset+tf)+axis]-=sign*fw

    def _front_patch(self,center,radius=.004,order=4):
        front=self.byname['front'];v=np.zeros(self.nnode);z,w=np.polynomial.legendre.leggauss(order)
        W,Dp,H=self.inside;Wout=W+2*self.h;Hout=H+2*self.h
        for a,wa in zip((z+1)/2,w/2):
            for phi in np.arange(16)*2*np.pi/16:
                point=np.array(center)+radius*np.sqrt(a)*np.array([np.cos(phi),np.sin(phi)])
                N=front.mesh2d.interpolate(*(point-np.array([Wout,Hout])/2))[0::3]
                nodes=front.offset+front.nt*front.nn2d+np.arange(front.nn2d)
                v[nodes]+=N*wa/16
        return v

    def _add_basket(self,mass=7.68,normal_stiffness=1e6,tangential_stiffness=1e6):
        rb=self.basket_reference;W,Dp,H=self.inside;front=self.byname['front'];rows=[]
        for phi in np.arange(8)*2*np.pi/8:
            location=rb+np.array([.1621*np.cos(phi),0,.1621*np.sin(phi)])
            patch=self._front_patch(location[[0,2]])
            body=np.hstack([np.eye(3),-skew(location-rb)])
            D=np.zeros((3,self.ndof))
            for axis in range(3):D[axis,axis:3*self.nnode:3]=patch
            D[:,-6:]=-body;rows.append(sparse.csr_matrix(D))
        DD=sparse.vstack(rows,format='csr');stiff=np.tile([tangential_stiffness,normal_stiffness,tangential_stiffness],8)
        self.basket_K=DD.T@sparse.diags(stiff)@DD;self.K+=self.basket_K;self.basket_D=DD
        offset=np.array([0,.08,0]);S=skew(offset);T=np.hstack([np.eye(3),-S])
        mb=mass*T.T@T;mb[3:,3:]+=np.eye(3)*mass*.1**2
        self.M+=sparse.block_diag([sparse.csr_matrix((3*self.nnode,3*self.nnode)),sparse.csr_matrix(mb)],format='csr')
        self.basket_mass=mass;self.pressure[-5]-=front.mesh2d.hole_polygon_area_m2

    def rigid_modes(self):
        R=np.zeros((self.ndof,6))
        for i,r in enumerate(self.xyz):R[3*i:3*i+3,:3]=np.eye(3);R[3*i:3*i+3,3:]=-skew(r)
        if self.with_basket:R[-6:-3,:3]=np.eye(3);R[-6:-3,3:]=-skew(self.basket_reference);R[-3:,3:]=np.eye(3)
        return R

    def free_modes(self,count=12):
        val,vec=eigsh(self.K,k=count+6,M=self.M,sigma=-(2*np.pi*5)**2,which='LM',v0=np.sin(np.arange(self.ndof)+1))
        order=np.argsort(val);val=val[order];vec=vec[:,order]
        return val,vec

    def balanced_static(self,F):
        # Odprezenie inercyjne,po czym6wiezow tylko jako wybor reprezentanta.
        acc=np.linalg.solve(self.mass_rigid,self.R.T@F);balanced=F-self.M@(self.R@acc)
        # Baza6rigidwybiera niezalezne DOF przez QRz pivotem.
        from scipy.linalg import qr
        _,_,pivot=qr(self.R.T,pivoting=True,mode='economic');fixed=pivot[:6];free=np.setdiff1d(np.arange(self.ndof),fixed)
        q=np.zeros(self.ndof);q[free]=spsolve(self.K[free][:,free],balanced[free])
        q-=self.R@np.linalg.solve(self.mass_rigid,self.R.T@(self.M@q))
        return q,balanced,acc

    def surface_patch(self,panel,axis,value,center,size):
        other=[i for i in range(3) if i!=axis];lo=np.array(center)-np.array(size)/2;hi=np.array(center)+np.array(size)/2
        weights=np.zeros(self.nnode);area=0.
        for face in panel.faces(axis,value):
            xy=panel.xyz[face][:,other];poly=clip_rectangle(xy,lo,hi)
            if len(poly)<3:continue
            for point,w in polygon_quadrature(poly):
                N=inverse_quad(xy,point);weights[panel.offset+face]+=N*w;area+=w
        expected=np.prod(size)
        if abs(area/expected-1)>1e-9:raise ValueError('Lata nie jest cala na materialnej powierzchni')
        weights/=area;P=np.zeros((3,self.ndof))
        for i in range(3):P[i,i:3*self.nnode:3]=weights
        return sparse.csr_matrix(P)

    def add_ties(self,count=1,joint_factor=np.inf):
        W,Dp,H=self.inside;h=self.h
        locations=[.55] if count==1 else [.4,.7] if count==2 else []
        if count not in [0,1,2]:raise ValueError('0/1/2sciagi')
        mass=730*.022*.04*W;pad=730*.08*.08*.018;k=2.1e9*.022*.04/W
        if not np.isposinf(joint_factor):k/=1+2/joint_factor
        self.ties=[]
        for y in locations:
            P1=self.surface_patch(self.byname['left'],0,h,[h+Dp*y,h+H/2],[.08,.08])
            P2=self.surface_patch(self.byname['right'],0,h+W,[h+Dp*y,h+H/2],[.08,.08])
            B=P2[0]-P1[0];K=k*(B.T@B)
            M=mass/6*(2*P1.T@P1+P1.T@P2+P2.T@P1+2*P2.T@P2)+pad*(P1.T@P1+P2.T@P2)
            self.K+=K;self.M+=M;self.ties.append(dict(K=K,M=M,P1=P1,P2=P2,stiffness_n_m=k,mass_kg=mass+2*pad))
        self.mass_rigid=self.R.T@(self.M@self.R)

    def set_floor(self,normal_each_n_m=1e5,tangential_each_n_m=1e4):
        W,Dp,H=self.inside;h=self.h;self.feet=[];K=sparse.csr_matrix((self.ndof,self.ndof))
        for x,y in [(a,b) for a in [.15,.85] for b in [.15,.85]]:
            P=self.surface_patch(self.byname['bottom'],2,0,[h+W*x,h+Dp*y],[.04,.04])
            k=np.array([tangential_each_n_m,tangential_each_n_m,normal_each_n_m]);K+=P.T@sparse.diags(k)@P
            self.feet.append(dict(P=P,k=k))
        self.floor_K=K;return K

    def joint_summary(self,q):
        accum={}
        for piece in self.bonds:
            u=np.asarray(q.reshape(-1)[(3*piece.nodes[:,None]+np.arange(3)).ravel()]).reshape(-1,3)
            energies=np.array([np.vdot(u[:,i],piece.L@u[:,i]).real for i in range(3)])
            forces=np.array([(piece.L@u[:,i])[:4].sum()*(piece.kn if i==piece.normal_axis else piece.ks) for i in range(3)])
            item=accum.setdefault(piece.name,dict(area=0.,normal_integral=0.,tangent_integral=0.,force=np.zeros(3,dtype=forces.dtype)))
            item['area']+=piece.area;item['normal_integral']+=energies[piece.normal_axis]*piece.kn**2
            item['tangent_integral']+=sum(energies[i] for i in range(3) if i!=piece.normal_axis)*piece.ks**2;item['force']+=forces
        return [dict(joint=name,area_m2=v['area'],rms_spatial_normal_traction_pa=float(np.sqrt(max(v['normal_integral'],0)/v['area'])),
                     rms_spatial_tangent_traction_pa=float(np.sqrt(max(v['tangent_integral'],0)/v['area'])),
                     resultant_force_norm_n=float(np.linalg.norm(v['force']))) for name,v in accum.items()]
