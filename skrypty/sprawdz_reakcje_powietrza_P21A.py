"""Zakres aproksymacji własnego jądra,siatka i wzajemność operatora."""
import json
from pathlib import Path
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve
from model_gazu import Medium
from model_plyty_MITC_P18 import RectangularPlate,PlateMaterial
from reakcja_powietrza_P21A import surface,radiation_operator

ROOT=Path(__file__).resolve().parents[1]


def main():
    med=Medium();rows=[];self_sensitivity=[];reciprocity=[]
    for nx,ny in [(12,18),(16,24),(20,28)]:
        p=RectangularPlate(.46,.64,nx,ny,PlateMaterial(2.1e9,.3,730,.022),'SSSS');geom=surface(p);idx=geom['transverse']
        f1=p.modes(1)[0][0];w1=2*np.pi*f1;w2=5*w1;C=2*.03*w1*w2/(w1+w2)*p.M+2*.03/(w1+w2)*p.K
        for f in [20.,80.]:
            w=2*np.pi*f;Z=radiation_operator(f,geom,med);rr=np.repeat(idx,len(idx));cc=np.tile(idx,len(idx))
            op=sparse.coo_matrix((Z.ravel(),(rr,cc)),shape=p.K.shape).tocsr();dry=p.K-w*w*p.M+1j*w*C
            q=spsolve(dry+1j*w*op,p.F);comp=p.F@q
            rows.append(dict(nx=nx,ny=ny,f_hz=f,compliance_real=float(comp.real),compliance_imag=float(comp.imag)))
            if nx==16:
                patch=p.patch_average((.23,.32),(.08,.08));other=spsolve(dry+1j*w*op,patch)
                error=abs(patch@q-p.F@other)/max(abs(patch@q),1e-30);assert error<1e-10
                reciprocity.append(dict(f_hz=f,relative_error=float(error)))
                # Alternatywna własna masa w punkcie środka dysku; oba są przybliżeniami.
                weights=geom['weights'];a=np.sqrt(weights/np.pi)
                self_kernel=med.rho*w/(2*np.pi)*16*a/(3*weights)
                difference=(3*np.pi/8-1)*self_kernel
                delta=geom['A'].T@(sparse.diags(difference)@geom['A'])
                extra=sparse.coo_matrix((delta.toarray().ravel(),(rr,cc)),shape=p.K.shape).tocsr()
                alternate=spsolve(dry+1j*w*op-w*extra,p.F)
                change=abs((p.F@alternate)/comp-1)
                assert change<.02
                self_sensitivity.append(dict(f_hz=f,relative_compliance_change=float(change)))
                none=spsolve(dry+0.*op,p.F);direct=spsolve(dry,p.F);assert np.linalg.norm(none-direct)==0
    convergence=[]
    for f in [20.,80.]:
        values=[complex(r['compliance_real'],r['compliance_imag']) for r in rows if r['f_hz']==f]
        delta=abs(values[-1]/values[-2]-1);assert delta<.03
        convergence.append(dict(f_hz=f,last_relative_change=float(delta)))
    result=dict(status='P21A_MESH_SELF_TERM_AND_RECIPROCITY_CONTROLS',mesh_rows=rows,last_mesh_changes=convergence,self_term_sensitivity=self_sensitivity,
        reciprocity=reciprocity,scope='20/80Hz i prostokątSSSS. Nie certyfikat całego widma. Czułość dwóch aproksymacji nie zastępuje niezależnej kontroli masyDuffy z głównego badania.')
    (ROOT/'wyniki/p21a_kontrole_siatki_i_wzajemnosci.json').write_text(json.dumps(result,indent=2,ensure_ascii=False));print(json.dumps(result,indent=2,ensure_ascii=False));return result


if __name__=='__main__':main()
