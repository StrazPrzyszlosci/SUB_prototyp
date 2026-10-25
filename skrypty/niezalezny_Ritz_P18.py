"""Odrębna metoda energetyczna Kirchhoffa dla CCCC; nie kod elementu MITC."""
import json
from pathlib import Path
import numpy as np
from numpy.polynomial import Polynomial,Legendre
from scipy.linalg import eigh
from model_plyty_MITC_P18 import PlateMaterial,RectangularPlate

ROOT=Path(__file__).resolve().parents[1]


def ritz_clamped(a,b,material,order=6):
    # W,w_n=0 na wszystkich brzegach. Funkcje wielomianowe mają H2.
    x,weight=np.polynomial.legendre.leggauss(max(32,order*2+8));x=(x+1)/2;weight=weight/2
    boundary=Polynomial([0,0,1,-2,1]);functions=[]
    for k in range(order):
        poly=Legendre.basis(k).convert(kind=Polynomial)(Polynomial([-1,2]))*boundary
        scale=np.sqrt(np.sum(weight*poly(x)**2));functions.append(poly/scale)
    matrices={}
    for i in range(3):
        for j in range(3):
            left=np.array([f.deriv(i)(x) for f in functions]);right=np.array([f.deriv(j)(x) for f in functions])
            matrices[i,j]=(left*weight)@right.T
    g=matrices;D=material.rigidity_nm;n=material.nu
    K=D*(b/a**3*np.kron(g[2,2],g[0,0])+a/b**3*np.kron(g[0,0],g[2,2])+
        n/(a*b)*(np.kron(g[2,0],g[0,2])+np.kron(g[0,2],g[2,0]))+
        2*(1-n)/(a*b)*np.kron(g[1,1],g[1,1]))
    M=material.density_kg_m3*material.thickness_m*a*b*np.kron(g[0,0],g[0,0])
    integrals=np.array([np.sum(weight*f(x)) for f in functions]);F=a*b*np.outer(integrals,integrals).ravel()
    q=np.linalg.solve(K,F);center=np.array([f(.5) for f in functions]);wcenter=float(np.outer(center,center).ravel()@q)
    eigen=eigh(K,M,eigvals_only=True)
    return dict(first_mode_hz=float(np.sqrt(eigen[0])/(2*np.pi)),center_m_pa=wcenter,compliance_m3_pa=float(F@q))


def main():
    a=.46;b=.64;mat=PlateMaterial(2.1e9,.3,730,.001)
    refs=[dict(order=k,**ritz_clamped(a,b,mat,k)) for k in [2,4,6,8]]
    assert abs(refs[-1]['first_mode_hz']/refs[-2]['first_mode_hz']-1)<2e-4
    assert abs(refs[-1]['compliance_m3_pa']/refs[-2]['compliance_m3_pa']-1)<2e-4
    rows=[]
    for mesh in [8,16,24,32]:
        plate=RectangularPlate(a,b,mesh,mesh,mat,'CCCC');u=plate.static();f=plate.modes(1)[0][0]
        rows.append(dict(mesh=mesh,frequency_hz=float(f),compliance_m3_pa=float(plate.F@u),
            relative_frequency_difference_from_Kirchhoff=float(f/refs[-1]['first_mode_hz']-1),
            relative_compliance_difference_from_Kirchhoff=float(plate.F@u/refs[-1]['compliance_m3_pa']-1)))
    assert abs(rows[-1]['relative_frequency_difference_from_Kirchhoff'])<.01
    assert abs(rows[-1]['relative_compliance_difference_from_Kirchhoff'])<.02
    # Dla roboczej22mm: siatka i brzegowy moment,wymagany w P19.
    mat=PlateMaterial(2.1e9,.3,730,.022);edge=[]
    for boundary in ['SSSS','CCCC']:
        for mesh in [8,16,24,32,40]:
            p=RectangularPlate(a,b,mesh,mesh,mat,boundary);q=p.static()
            edge.append(dict(boundary=boundary,mesh=mesh,maximum_edge_moment_per_pa_n=p.edge_moment_peak(q),
                maximum_principal_stress_per_pa=p.peak_principal_bound(q),compliance_m3_pa=float(p.F@q)))
    result=dict(status='INDEPENDENT_RITZ_AND_MITC_CONVERGENCE',Kirchhoff_ritz=refs,thin_MITC_convergence=rows,edge_stress_convergence=edge,
        scope='RitzKirchhoff i MITCMindlin są różnymi teoriami dla skończonej grubości. Porównanie wykonano w granicy cienkiej płyty. Brzegowy momentSSSS powinien dążyć dozera; jego reszta nie jest rzeczywistym odrywaniem spoiny.')
    (ROOT/'wyniki/p18_niezalezny_Ritz_i_brzegi.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False));print(json.dumps(result,indent=2,ensure_ascii=False));return result


if __name__=='__main__':main()
