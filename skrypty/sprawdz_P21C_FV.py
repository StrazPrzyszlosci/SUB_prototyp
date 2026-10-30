"""Independent cell-centred finite-volume Helmholtz check of finite piston.

No cosine modes in the FV solve. Rigid walls, imposed outward displacement.
Same empty-cavity mathematical problem as P21C0; not physical validation.
"""
from pathlib import Path
import hashlib,json
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import cg,LinearOperator
from pilot_P21C_geometria import response,transverse_tail_bound

ROOT=Path(__file__).resolve().parents[1]


def lap(n,step):
    diagonal=np.full(n,2.);diagonal[[0,-1]]=1.
    return sparse.diags([-np.ones(n-1),diagonal,-np.ones(n-1)],[-1,0,1],format='csr')/step**2


def main():
    lengths=(.6,.4,.4);side=.2;f=80.;c=343.;rho=1.2;omega=2*np.pi*f;k=omega/c;rows=[]
    for nx in [12,24,48,96]:
        ny=nz=nx*2//3;dx,dy,dz=np.array(lengths)/np.array([nx,ny,nz]);dv=dx*dy*dz
        ix,iy,iz=(sparse.eye(n,format='csr') for n in [nx,ny,nz])
        K=sparse.kron(iz,sparse.kron(iy,lap(nx,dx)))+sparse.kron(iz,sparse.kron(lap(ny,dy),ix))+sparse.kron(lap(nz,dz),sparse.kron(iy,ix))
        sources=[]
        for xc in [.3,.15]:
            xedges=np.arange(nx+1)*dx;zedges=np.arange(nz+1)*dz
            sx=np.maximum(0,np.minimum(xedges[1:],xc+side/2)-np.maximum(xedges[:-1],xc-side/2))
            sz=np.maximum(0,np.minimum(zedges[1:],.2+side/2)-np.maximum(zedges[:-1],.2-side/2))
            b=np.zeros((nz,ny,nx));b[:,0,:]=sz[:,None]*sx[None,:]/dv
            assert abs(b.sum()*dv-side**2)<1e-14
            sources.append(b.ravel())
        B=np.column_stack(sources)
        K=K.tocsr();count=nx*ny*nz
        # Separate known constant pressure; positive operator on the mean-zero
        # space below first mode. Positive rank-one extension permits CG.
        A=LinearOperator((count,count),matvec=lambda x:K@x-k*k*x+2*k*k*x.mean())
        pre=LinearOperator((count,count),matvec=lambda x:x/(K.diagonal()-k*k))
        P=np.empty_like(B)
        for j in range(2):
            rhs=rho*omega**2*B[:,j];mean=rhs.mean()
            q,info=cg(A,rhs-mean,M=pre,rtol=1e-10,atol=0,maxiter=4000)
            assert info==0
            P[:,j]=q-mean/(k*k)
        for j,xc in enumerate([.3,.15]):
            # Face pressure reconstructed from prescribed outward derivative.
            # All piston edges align with faces in these three grids.
            mean_source=B[:,j]@P[:,j]*dv/side**2+rho*omega**2*dy/2
            lumped=-rho*c*c*side**2/np.prod(lengths)
            ratio=mean_source/lumped
            modal=response(lengths,(xc,.2),(side,side),[f],160,c)[0]
            mean_volume=P[:,j].mean()
            assert abs(mean_volume/lumped-1)<1e-8
            rows.append(dict(nx=nx,ny=ny,nz=nz,source_x_m=xc,f_hz=f,finite_volume_ratio=ratio,modal_ratio=modal,
                absolute_difference=abs(ratio-modal),modal_tail_bound=transverse_tail_bound(lengths,(side,side),f,160,c),
                mean_volume_relative_error=abs(mean_volume/lumped-1)))
        print('FV grid',nx,ny,nz,'done',flush=True)
    for xc in [.3,.15]:
        errors=[r['absolute_difference'] for r in rows if r['source_x_m']==xc]
        assert all(b<a for a,b in zip(errors,errors[1:]))
        print('FV errors',xc,errors,flush=True)
        assert errors[-1]<.002
    result=dict(status='INDEPENDENT_FV_FINITE_PISTON_CONTROLS',rows=rows,
        input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'skrypty/pilot_P21C_geometria.py']},
        limitations=['Two source positions,one geometry and frequency;not a complete continuum certificate or measured validation.'])
    (ROOT/'wyniki/p21c0_niezalezna_FV.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(rows[-2:],indent=2))


if __name__=='__main__':main()
