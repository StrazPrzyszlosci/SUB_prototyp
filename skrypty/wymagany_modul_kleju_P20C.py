"""Ciągła wymagana sztywność spoin modułu, przy stałej geometrii i nu.

Porównawcze kryterium Ceff<=1.01/1.05/1.10*Ceff(E_ref), nie próg briefu.
Analitycznie dCeff/dE=-q.T Kglue_unit q<=0. Nie jest to nośność/wybór kleju.
"""
from pathlib import Path
import gc,hashlib,json,resource
import numpy as np
from scipy.sparse.linalg import splu
from scipy.optimize import brentq
from model_modulu_3D_P20C import SolidModule
from analiza_wkladow_P20A import table

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def main():
    cp=ROOT/'dane/konfiguracje/p20c_modul_pelny_3D.json';cfg=json.loads(cp.read_text());bp=ROOT/cfg['reference_insert_config'];base=json.loads(bp.read_text())
    rows=[];derivatives=[];curves=[];reference=max(cfg['glue_E_pa_cases_assumed']);lower=min(cfg['glue_E_pa_cases_assumed'])
    # Dwie najdrobniejsze siatki; nie przyjmujemy 5% za wymaganie użytkownika.
    for n in cfg['mesh_resolution_cases'][-2:]:
        m=SolidModule(base,cfg,n,braced=True,glue_E=reference);H=m.H;free=m.free
        K0=m.Kparts['mdf'][free][:,free];K1=m.Kparts['glue'][free][:,free]/reference
        F=H[free];Ci=m.inner_volume/101325.;cache={}
        def evaluate(E):
            key=float(E)
            if key not in cache:
                qs=splu((K0+E*K1).tocsc()).solve(F);c=F.T@qs;r=-c[0,1]/(Ci+c[0,0]);q=qs@np.array([r,1.])
                value=float(F[:,1]@q);slope=float(-q@(K1@q));assert value>0 and slope<0
                cache[key]=(value,slope)
            return cache[key]
        c_ref=evaluate(reference)[0]
        for E in np.geomspace(lower,reference,15):
            val,slope=evaluate(E);curves.append(dict(mesh_resolution=n,glue_E_pa=float(E),static_outer_closed_compliance_m3_pa=val,relative_to_stiff_reference=val/c_ref,
                storage_equivalent_l=val*1.4*101325.*1000,dc_isothermal_gas_compliance_m3_pa=Ci))
        for E in [lower*1.1,1e8,reference*.9]:
            h=E*1e-3;val,slope=evaluate(E);fd=(evaluate(E+h)[0]-evaluate(E-h)[0])/(2*h)
            error=abs(fd/slope-1);assert error<1e-4
            derivatives.append(dict(mesh_resolution=n,glue_E_pa=E,analytic_derivative_m3_pa2=slope,finite_difference_m3_pa2=fd,relative_error=error))
        for margin in [.01,.05,.10]:
            target=(1+margin)*c_ref
            root=np.exp(brentq(lambda x:evaluate(np.exp(x))[0]/target-1,np.log(lower),np.log(reference),xtol=1e-10))
            left,right=root*(1-1e-5),root*(1+1e-5);vl=evaluate(left)[0];vr=evaluate(right)[0]
            assert vl>target>vr
            rows.append(dict(mesh_resolution=n,relative_allowance_vs_reference=margin,reference_glue_E_pa=reference,
                required_glue_E_pa=float(root),target_compliance_m3_pa=target,reference_compliance_m3_pa=c_ref,
                lower_witness_E_pa=float(left),upper_witness_E_pa=float(right),
                lower_witness_relative_excess=float(vl/target-1),upper_witness_relative_excess=float(vr/target-1),
                scope='Continuous linear static family,constant nu and geometry; bracket witnesses in floating point,not interval certificate or strength.'))
        print('P20C glue modulus: mesh',n,'unique sparse solves',len(cache),flush=True);del m;gc.collect()
    table('p20c_wymagany_modul_kleju.csv',rows);table('p20c_klej_ciagla_krzywa.csv',curves)
    inputs=[cp,bp,Path(__file__),ROOT/'skrypty/model_modulu_3D_P20C.py',ROOT/'skrypty/element_brylowy_P18C.py',ROOT/'skrypty/model_ramy_3D_P18C.py']
    j=dict(status='CONTINUOUS_STATIC_STIFFNESS_REQUIREMENT_NOT_GLUE_QUALIFICATION',root_cases=len(rows),derivative_checks=derivatives,
        reference='Adhesive stiffness reference only,not approved product or brief threshold.',
        monotonicity='For Keff=Kmdf+E*Kglue_unit+Hi*Hi.T/Ci on the quotient by rigid motions, d(Ho.T inv(Keff) Ho)/dE=-q.T Kglue_unit q<=0.',
        peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,
        input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        limitations=['Isothermal static gas. This derivative does not prove monotonicity of dynamic compliance near resonances.',
            'No identified creep law or relaxed modulus,surface adhesion,peel strength,S-N or Gc.',
            'Fixed Poisson ratio,thickness,material law and a comparison criterion,not manufacturer tolerances.'])
    (OUT/'p20c_klej_podsumowanie.json').write_text(json.dumps(j,ensure_ascii=False,indent=2,allow_nan=False))


if __name__=='__main__':main()
