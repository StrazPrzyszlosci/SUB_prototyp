"""Linear 3D solid model of the assembled S01 reference cabinet. SI."""
from functools import lru_cache
from itertools import product
import json
import numpy as np
from scipy.sparse import coo_matrix, diags
from scipy.sparse.linalg import LinearOperator, eigsh, splu
from pathlib import Path

HERE = Path(__file__).resolve().parent

CORNERS=np.array(list(product((0,1),repeat=3)))
SIGNS=2*CORNERS-1


@lru_cache(None)
def hex8(lengths, poisson=.30):
    """Fully integrated trilinear stiffness for unit Young modulus."""
    lengths=np.array(lengths)
    stiffness=np.zeros((24,24))
    lam=poisson/((1+poisson)*(1-2*poisson))
    mu=1/(2*(1+poisson))
    elastic=np.diag([2*mu]*3+[mu]*3)
    elastic[:3,:3]+=lam
    for point in product((-1/np.sqrt(3),1/np.sqrt(3)),repeat=3):
        factors=1+SIGNS*point
        B=np.zeros((6,24))
        for n,s in enumerate(SIGNS):
            dx,dy,dz=s*np.prod(factors[n])/factors[n]/(4*lengths)
            B[:,3*n:3*n+3]=[[dx,0,0],[0,dy,0],[0,0,dz],[dy,dx,0],[0,dz,dy],[dz,0,dx]]
        stiffness+=B.T@elastic@B*lengths.prod()/8
    return stiffness


def grid(breaks,h):
    return np.concatenate([np.linspace(a,b,int(np.ceil((b-a)/h))+1)[:-1]
                           for a,b in zip(breaks,breaks[1:])]+[[breaks[-1]]])


def solve(shape,h,vertical=False,bond=2e11):
    W,H=np.array([shape['W'],shape['H']])*.001
    D=.394
    xs=grid([0,.022,.052,W-.052,W-.022,W],h)
    ys=grid([0,.022,.028,.044,.197,.219,.372,D],h)
    zs=grid([0,.022,.052,H-.052,H-.022,H],h)
    ids={}; positions=[]; masses=[]; pressure=[]; rows=[];cols=[];values=[]
    nodes_by_part={}
    def node(key,part):
        tag=(key,part)
        if tag not in ids:
            ids[tag]=len(ids);positions.append([xs[key[0]],ys[key[1]],zs[key[2]]])
            masses.append(0.);pressure.append(np.zeros(3))
        return ids[tag]
    def add(dof,K):
        rows.append(np.repeat(dof,len(dof)));cols.append(np.tile(dof,len(dof)));values.append(K.ravel())
    cells={}
    step=[np.diff(g) for g in (xs,ys,zs)]
    for key in product(*(range(len(s)) for s in step)):
        i,j,k=key
        size=np.array([s[n] for s,n in zip(step,key)])
        x,y,z=np.array([xs[i],ys[j],zs[k]])+size/2
        frac=1.;steel=0
        if y<.044:
            part='front1' if y<.022 else 'front2'
            t=(np.arange(8)+.5)/8
            radius=np.hypot(xs[i]+t[:,None]*size[0]-W/2,zs[k]+t*size[2]-H/2)
            frac=np.mean(radius>=.1779)
            if frac==0:continue
            if .022<y<.028:steel=np.mean((radius>=.179)&(radius<.2))
        elif y>.372:part='rear'
        elif x<.022 or x>W-.022:part='side'
        elif z<.022 or z>H-.022:part='base'
        elif .197<y<.219 and min(x,W-x,z,H-z)<.052:part='brace'
        else:continue
        corners=[tuple(np.array(key)+off) for off in CORNERS]
        nn=np.array([node(c,part) for c in corners])
        nodes_by_part.setdefault(part,set()).update(nn)
        cells[key]=(part,nn,frac)
        dofs=(3*nn[:,None]+np.arange(3)).ravel()
        add(dofs,hex8(tuple(np.round(size,12)))*((frac-steel)*2e9+steel*200e9))
        mass=size.prod()*((frac-steel)*800+steel*7850)
        for n in nn:masses[n]+=mass/8
    for key,(part,nn,frac) in cells.items():
        for axis in range(3):
            nxt=list(key);nxt[axis]+=1
            other=cells.get(tuple(nxt))
            area=np.prod([step[a][key[a]] for a in range(3) if a!=axis])
            if other and other[0]!=part:
                for n,m in zip(nn[CORNERS[:,axis]==1],other[1][CORNERS[:,axis]==0]):
                    dofs=(3*np.array([n,m])[:,None]+np.arange(3)).ravel()
                    add(dofs,bond*area*min(frac,other[2])/4*np.kron([[1,-1],[-1,1]],np.eye(3)))
            # Uniform pressure on projected interior of enclosing faces.
            for end in (0,1):
                idx=key[axis]+end
                plane=(xs,ys,zs)[axis][idx]
                lo,hi=((.022,W-.022),(.044,.372),(.022,H-.022))[axis]
                target=(lo if end else hi)
                if abs(plane-target)>1e-9:continue
                center=[g[n]+step[a][n]/2 for a,(g,n) in enumerate(zip((xs,ys,zs),key))]
                if any(not (l<center[a]<u) for a,(l,u) in enumerate(((.022,W-.022),(.044,.372),(.022,H-.022))) if a!=axis):continue
                for n in nn[CORNERS[:,axis]==end]:pressure[n][axis]+=(1-2*end)*1000*area*frac/4
    pos=np.array(positions);m=np.array(masses);f=np.array(pressure)
    front=np.array(sorted(nodes_by_part['front1']))
    rim=front[(pos[front,1]==0)&(abs(np.hypot(pos[front,0]-W/2,pos[front,2]-H/2)-.184)<h*.65)]
    assert len(rim)>=8
    m[rim]+=15/len(rim)
    f[rim,1]-=f[:,1].sum()/len(rim)  # missing pressure resultant of the sealed driver opening
    assert np.linalg.norm(f.sum(axis=0))<1e-7
    up=0 if vertical else 2
    feet=[]
    for a,b in product((.12,.88),repeat=2):
        target=np.array([W*a,D*b,0]) if not vertical else np.array([0,D*b,H*a])
        candidates=np.array(sorted(nodes_by_part['side' if vertical else 'base']))
        feet.append(candidates[np.argmin(np.linalg.norm(pos[candidates]-target,axis=1))])
    assert len(set(feet))==4
    springs=np.full(3,16000.);springs[up]=31600
    for n in feet:add(3*n+np.arange(3),np.diag(springs))
    K=coo_matrix((np.concatenate(values),(np.concatenate(rows),np.concatenate(cols))),shape=(3*len(m),)*2).tocsc()
    gravity=np.zeros_like(f);gravity[:,up]=-9.81*m
    lu=splu(K)
    u=lu.solve(f.ravel()).reshape(-1,3)
    sag=lu.solve(gravity.ravel()).reshape(-1,3)
    reactions=-sag[feet,up]*springs[up]
    assert abs(reactions.sum()-9.81*m.sum())<1e-4
    rear=np.array(sorted(nodes_by_part['rear']))
    rear=rear[np.isclose(pos[rear,1],D)]
    # Remove rigid translation/rotation using rear corner displacements.
    corners=[rear[np.argmin(np.linalg.norm(pos[rear][:,[0,2]]-[a,b],axis=1))] for a,b in product((0,W),(0,H))]
    plane=np.c_[np.ones(len(m)),pos[:,0],pos[:,2]]
    rear_bow=u[rear,1]-plane[rear]@np.linalg.lstsq(plane[corners],u[corners,1],rcond=None)[0]
    modes=[]
    if h <= .045 and bond == 2e11:
        weights=np.repeat(m,3)
        centered=pos-np.average(pos,axis=0,weights=m)
        translations=[np.tile(axis,(len(m),1)) for axis in np.eye(3)]
        rotations=[np.cross(axis,centered) for axis in np.eye(3)]
        rigid=np.column_stack([a.ravel() for a in translations+rotations])
        basis,_=np.linalg.qr(np.sqrt(weights)[:,None]*rigid)
        eigenvalues,vectors=eigsh(K,k=9,M=diags(weights),sigma=0,
            OPinv=LinearOperator(K.shape,matvec=lu.solve),
            v0=np.random.default_rng(12).standard_normal(len(weights)))
        for value,vector in zip(eigenvalues,vectors.T):
            weighted=np.sqrt(weights)*vector
            flexible=np.linalg.norm(weighted-basis@(basis.T@weighted))**2/np.dot(weighted,weighted)
            modes.append(dict(Hz=np.sqrt(value)/(2*np.pi),flexible_mass_fraction=flexible))
    return dict(modes=modes,foot_positions_m=pos[feet].tolist(),h_mm=1000*h,vertical=vertical,bond_N_m3=bond,mass_kg=m.sum(),nodes=len(m),
                rear_bow_mm=max(abs(rear_bow))*1000,compliance_cm3_kPa=np.sum(f*u)*1000,
                foot_N=reactions.tolist(),foot_sag_mm=(-sag[feet,up]*1000).tolist())


if __name__=='__main__':
    shapes=json.loads((HERE/'s01_wyniki.json').read_text())['shapes']
    out={name:[solve(shape,h) for h in (.070,.045,.030)] for name,shape in shapes.items()}
    out['A_sensitivity']=[solve(shapes['A'],.045,vertical,bond) for vertical,bond in
                          [(True,2e11),(False,2e10),(False,2e12)]]
    (HERE/'s02_wyniki.json').write_text(json.dumps(out,indent=2)+'\n')
