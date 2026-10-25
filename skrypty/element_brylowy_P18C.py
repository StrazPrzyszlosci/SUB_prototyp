"""3D H8 z9 wewnetrznymi modami odksztalcenia i kondensacja statyczna.

To wlasna jawna rodzina EAS9,nie implementacja C3D8I z13modami.
Mody maja zerowa srednia objetosciowa;masa pozostaje nodalna zgodna.
SI, liniowa mala deformacja,konwencja Voigta xx,yy,zz,xy,yz,xz.
"""
import numpy as np

SIGNS=np.array([[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],
                [-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]],float)


def isotropic_D(E,nu):
    if not E>0 or not -1<nu<.5:raise ValueError('E>0,-1<nu<0.5')
    G=E/(2*(1+nu));lam=E*nu/((1+nu)*(1-2*nu))
    D=np.zeros((6,6));D[:3,:3]=lam;np.fill_diagonal(D[:3,:3],lam+2*G);D[3:,3:]=G*np.eye(3)
    return D


def transverse_stress_D(E,nu,normal_axis,E_normal_ratio=1.,G_normal_ratio=1.):
    if min(E,E_normal_ratio,G_normal_ratio)<=0:raise ValueError('Dodatnie moduly')
    if E_normal_ratio==G_normal_ratio==1.:return isotropic_D(E,nu)
    S=np.zeros((6,6));young=np.full(3,E);young[normal_axis]*=E_normal_ratio
    for i in range(3):S[i,i]=1/young[i]
    for i in range(3):
        for j in range(i):S[i,j]=S[j,i]=-nu/E
    for index,pair in enumerate([(0,1),(1,2),(0,2)],3):
        G=E/(2*(1+nu))*(G_normal_ratio if normal_axis in pair else 1.)
        S[index,index]=1/G
    if np.linalg.eigvalsh(S).min()<=0:raise ValueError('Niedodatnia podatnosc ortotropowa')
    return np.linalg.inv(S)


def shape(xi):
    xi=np.asarray(xi);terms=1+SIGNS*xi
    N=np.prod(terms,axis=1)/8;der=np.empty((3,8))
    for a in range(3):der[a]=SIGNS[:,a]*np.prod(terms[:,[j for j in range(3) if j!=a]],axis=1)/8
    return N,der


def strain_operator(der):
    B=np.zeros((6,3*der.shape[1]))
    B[0,0::3]=der[0];B[1,1::3]=der[1];B[2,2::3]=der[2]
    B[3,0::3]=der[1];B[3,1::3]=der[0]
    B[4,1::3]=der[2];B[4,2::3]=der[1]
    B[5,0::3]=der[2];B[5,2::3]=der[0]
    return B


def hex8(xyz,D,density,enhanced=True):
    if xyz.shape!=(8,3) or density<=0:raise ValueError('8wezlow3D,rho>0')
    points=[];volume=0.;mean=np.zeros((6,9))
    for point in SIGNS/np.sqrt(3):
        N,dN=shape(point);J=dN@xyz;det=np.linalg.det(J)
        if det<=0:raise ValueError('Niedodatni JacobianH8')
        deriv=np.linalg.solve(J,dN);B=strain_operator(deriv)
        bubble_deriv=np.linalg.solve(J,np.diag(2*point));Ba=strain_operator(bubble_deriv)
        mean+=Ba*det;volume+=det;points.append((N,B,Ba,det))
    mean/=volume;Kqq=np.zeros((24,24));Kqa=np.zeros((24,9));Kaa=np.zeros((9,9));M=np.zeros((24,24))
    for N,B,Ba,jac in points:
        Ba=Ba-mean
        Kqq+=B.T@D@B*jac;Kqa+=B.T@D@Ba*jac;Kaa+=Ba.T@D@Ba*jac
        M+=density*np.kron(np.outer(N,N),np.eye(3))*jac
    recovery=-np.linalg.solve(Kaa,Kqa.T)
    K=Kqq+Kqa@recovery if enhanced else Kqq
    return (K+K.T)/2,M,dict(volume_m3=float(volume),recovery=recovery,mean_bubble_strain=mean,
                           points=points,Kqq=Kqq,Kqa=Kqa,Kaa=Kaa)


def gauss_stress(xyz,D,q,meta,enhanced=True):
    a=meta['recovery']@q if enhanced else np.zeros(9)
    return np.array([D@(B@q+(Ba-meta['mean_bubble_strain'])@a) for N,B,Ba,det in meta['points']])


def quad_shape(xi,eta):
    s=SIGNS[:4,:2];N=(1+s[:,0]*xi)*(1+s[:,1]*eta)/4
    derivative=np.array([s[:,0]*(1+s[:,1]*eta),s[:,1]*(1+s[:,0]*xi)])/4
    return N,derivative


def quad_quadrature(xyz,order=3):
    z,w=np.polynomial.legendre.leggauss(order)
    for i,xi in enumerate(z):
        for j,eta in enumerate(z):
            N,d=quad_shape(xi,eta);t=d@xyz;area=np.linalg.norm(np.cross(t[0],t[1]))*w[i]*w[j]
            yield N,N@xyz,area
