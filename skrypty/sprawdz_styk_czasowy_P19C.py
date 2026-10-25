"""Kontrole energii,J,granicy liniowej i portu zadanego ruchu P19C."""
import hashlib
import json
from pathlib import Path
import numpy as np
from model_styku_czasowego_P19C import FullContact,ReducedContact
from model_frontu_z_otworem_P18B import MountedFront

ROOT=Path(__file__).resolve().parents[1]


def main():
    full=FullContact();rows=[];linear=[]
    for n,enrich in [(8,False),(16,False),(32,False),(16,True),(32,True)]:
        V=full.basis(n,enrich);r=ReducedContact(full,V)
        qref,row=MountedFront(full.plate,full.Kt,full.M,full.base.B,full.base.G,full.base.D,full.base.k,full.base.mass,full.base.positions).prescribed_cone(
            full.cfg['frequency_hz'],.001,full.mm,full.sd)
        reference=r.linear_reference()
        error=float(abs(reference['basket']/qref[-3]-1))
        linear.append(dict(modal=n,enriched=enrich,dimension=r.n,basket_complex_relative_error=error,
                           pressure_complex_relative_error=float(abs(reference['pressure']/complex(row['pressure_pa_real'],row['pressure_pa_imag'])-1))))
        if n!=16 or not enrich:continue
        for theta in [4.7,31.,47.]:
            y=np.sin(np.arange(r.dim)+.31)*.013
            jac=r.jac(theta,y);eps=1e-7;I=np.eye(r.dim)
            finite=np.column_stack([(r.rhs(theta,y+eps*I[i])-r.rhs(theta,y-eps*I[i]))/(2*eps) for i in range(r.dim)])
            jacerr=float(np.linalg.norm(jac-finite)/np.linalg.norm(jac));assert jacerr<1e-7
            dy=r.rhs(theta,y);derivatives=[]
            for delta in [1e-3,1e-4,1e-5,1e-6]:
                plus=r.energy_rates(theta+delta,y+delta*dy)['energy'];minus=r.energy_rates(theta-delta,y-delta*dy)['energy']
                derivatives.append((plus-minus)/(2*delta)*full.omega)
            e=r.energy_rates(theta,y);balance=e['input_power']-e['structural_loss']-e['gas_loss']
            u,v,lag,x,xp,xpp,volume,p,acc=r.mechanics(theta,y)
            force=r.G.T@(full.weights*(np.maximum(full.z0+r.G@u,0)-full.spring0))
            xd=full.omega*xp;xdd=full.omega**2*xpp;vd=full.sd*xd+r.h@v;ld=(volume-lag)/full.tau
            direct=v@acc+full.mm*xdd*(r.e@v)+full.mm*xd*(r.e@acc)+full.mm*xd*xdd+v@(r.Ks@u+force)
            direct+=full.Kgas*(volume*vd+(full.gamma-1)*(volume-lag)*(vd-ld))
            energy_error=abs(direct-balance)/max(abs(direct),abs(balance),1e-12);assert energy_error<1e-8
            # Przedzial krokow ujawnia blad odejmowania prawie rownych energii.
            finite_errors=[abs(d-balance)/max(abs(d),abs(balance),1e-12) for d in derivatives]
            assert min(finite_errors)<1e-5
            assert e['structural_loss']>=0 and e['gas_loss']>=0
            rows.append(dict(theta=theta,jacobian_relative_error=jacerr,energy_derivative_relative_error=float(energy_error),
                             finite_difference_steps=[1e-3,1e-4,1e-5,1e-6],finite_difference_relative_errors=finite_errors))
        # Brak ruchu i zaburzenia oznacza identycznie zerowa pochodna.
        zero=ReducedContact(full,V,0.);assert np.max(abs(zero.rhs(40.,np.zeros(zero.dim))))==0
        # Dokladnie ta sama styczna,gdy wszystkie znaki szczelin sa zachowane.
        u=np.sin(np.arange(r.n))*.000000001;G=r.G
        actual=G.T@(full.weights*(np.maximum(full.z0+G@u,0)-full.spring0))
        expected=(r.Kt-r.Ks)@u
        small_error=float(np.linalg.norm(actual-expected)/np.linalg.norm(expected));assert small_error<1e-7
    assert linear[-1]['basket_complex_relative_error']<.005
    result=dict(status='SCOPED_MODEL_IDENTITY_AND_LINEAR_LIMIT_CHECKS_NOT_HARDWARE_VALIDATION',
                energy_and_jacobian=rows,linear_full_FE_comparison=linear,small_motion_force_relative_error=small_error,
                full_dof=full.M.shape[0],preload_residual=full.preload['residual'],
                input_sha256={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in
                              ['skrypty/model_styku_czasowego_P19C.py','skrypty/sprawdz_styk_czasowy_P19C.py','dane/konfiguracje/p19c_styk_czasowy.json']})
    (ROOT/'wyniki/p19c_kontrole.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print('P19C kontrole:',len(rows),'energia/J;pelneDOF',full.M.shape[0],'liniowa',linear[-1])


if __name__=='__main__':main()
