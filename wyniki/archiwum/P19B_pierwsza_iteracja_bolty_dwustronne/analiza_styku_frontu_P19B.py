"""P19B: jednostronny styk uszczelki i zachowany docisk śrub, bez prawa tarcia.

Wypukła energia dyskretna; aktywny styk z liniowaniem i wyszukiwaniem kroku.
Nie utożsamiamy zadanej zmiany długości sprężyny ze zmierzonym momentem śruby.
"""
import csv
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve
from model_frontu_z_otworem_P18B import PlateMaterial,FrontWithHole,MountedFront

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def contact_quadrature(plate,r0,r1,nr=4,nt=128):
    if not plate.r<=r0<r1<min(plate.a,plate.b)/2:raise ValueError('Pierścień styku poza frontem')
    z,w=np.polynomial.legendre.leggauss(nr);rad=np.sqrt((r0*r0+r1*r1)/2+(r1*r1-r0*r0)*z/2)
    matrices=[];weights=[];positions=[]
    for r,wr in zip(rad,w):
        for phi in (np.arange(nt)+.5)*2*np.pi/nt:
            x,y=r*np.cos(phi),r*np.sin(phi)
            v=plate.interpolate(x,y)[plate.free]
            matrices.append(sparse.csr_matrix(np.r_[v,[-1.,-x,-y]][None,:]))
            weights.append(wr*(r1*r1-r0*r0)*np.pi/(2*nt));positions.append([x,y])
    D=sparse.vstack(matrices,format='csr');weights=np.array(weights)
    assert abs(weights.sum()-np.pi*(r1*r1-r0*r0))<1e-12
    return D,weights,np.array(positions)


def solve_contact(K,D,weights,kn,F,tol=1e-9,max_iter=80):
    def energy(q):
        gap=np.maximum(np.asarray(D@q),0)
        return float(.5*q@(K@q)+.5*kn*np.dot(weights,gap*gap)-F@q)
    q=spsolve(K,F);iterations=[]
    for it in range(max_iter):
        d=np.asarray(D@q);active=d>0
        gradient=K@q+kn*(D.T@(weights*np.maximum(d,0)))-F
        residual=float(np.linalg.norm(gradient)/max(np.linalg.norm(F),1e-30))
        J=K+kn*(D.T@sparse.diags(weights*active)@D)
        iterations.append(residual)
        if residual<tol:return q,J,active,dict(iterations=it+1,residual=residual,history=iterations)
        step=spsolve(J,-gradient);alpha=1.;current=energy(q);slope=float(gradient@step)
        for _ in range(35):
            if energy(q+alpha*step)<=current+1e-4*alpha*slope+1e-20:break
            alpha*=.5
        else:raise RuntimeError('Nie uzyskano spadku wypukłej energii')
        q+=alpha*step
    raise RuntimeError('Brak zbieżności styku; nie publikować jako wynik ustalony')


def reference_checks():
    scalar=[]
    for force in [-5.,1.,5.]:
        q,J,a,meta=solve_contact(sparse.csr_matrix([[2.]]),sparse.csr_matrix([[1.]]),np.array([1.]),3.,np.array([force]))
        exact=force/(5 if force>0 else 2)
        assert abs(q[0]-exact)<1e-12;scalar.append(dict(force=force,q=float(q[0]),exact=exact))
    # Odrębne wyliczenie wszystkich czterech stanów styku w2DOF.
    K=np.array([[3.,-.4],[-.4,2.]]);D=np.array([[1.,-.3],[-.2,1.]])
    weight=np.array([.7,.4]);kn=4.;enumerations=[]
    for F in [np.array([2.,-1.]),np.array([1.,3.]),np.array([-3.,-2.])]:
        valid=[]
        for bits in range(4):
            active=np.array([bool(bits&1),bool(bits&2)])
            q=np.linalg.solve(K+kn*D.T@np.diag(weight*active)@D,F)
            if np.array_equal(D@q>0,active):valid.append(q)
        assert len(valid)==1
        q,J,a,m=solve_contact(sparse.csr_matrix(K),sparse.csr_matrix(D),weight,kn,F)
        err=float(max(abs(q-valid[0])));assert err<1e-10;enumerations.append(err)
    return dict(scalar=scalar,independent_active_enumeration_errors=enumerations)


def main():
    checks=reference_checks();rows=[];preloads=[];mesh=[];worst_energy=0.
    fields=['skrypty/analiza_styku_frontu_P19B.py','skrypty/model_frontu_z_otworem_P18B.py',
            'skrypty/model_plyty_MITC_P18.py','dane/zrodla/P18B_geometria_i_ograniczenia.json',
            'dane/konfiguracje/p18b_front_z_otworem.json','wyniki/p11_kalibracje_masy.csv']
    input_hashes={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in fields}
    for bc in ['CCCC','SSSS_HARD']:
        p=FrontWithHole(.46,.46,.1526,PlateMaterial(2.1e9,.3,730,.022),20,12,bc)
        base=p.mounted(.1621,8,7.68,7.68*.0164,1e6)
        Dg,area,positions=contact_quadrature(p,.1536,.1721)
        for kn in [1e8,1e9]:
            for initial_force_parameter in [25.,100.,400.]:
                # Energia śrub .5*k*(Db*q-delta0)^2, k*delta0=T0.
                Fpre=np.asarray(base.D.T@np.full(8,initial_force_parameter)).ravel()
                # Ciężar na pionowym froncie: moment od zakładanegoCG za płaszczyzną.
                gravity_moment=7.68*9.80665*.08
                Fpre+=base.load(moment_x_nm=gravity_moment)
                q0,Kt,active,meta=solve_contact(base.K,Dg,area,kn,Fpre)
                pressure0=kn*np.maximum(Dg@q0,0)
                retained=initial_force_parameter-base.k*(base.D@q0)
                gasket_force=kn*Dg.T@(area*np.maximum(Dg@q0,0))
                residual=float(np.linalg.norm(base.K@q0+gasket_force-Fpre)/np.linalg.norm(Fpre))
                assert residual<1e-8
                preload=dict(boundary=bc,contact_kn_pa_m=kn,initial_force_parameter_n=initial_force_parameter,
                             imposed_bolt_shortening_m=initial_force_parameter/base.k,gravity_moment_nm=gravity_moment,
                             retained_bolt_min_n=float(min(retained)),retained_bolt_max_n=float(max(retained)),
                             contact_area_fraction=float(np.sum(area*active)/sum(area)),
                             maximum_preload_contact_pressure_pa=float(max(pressure0)),
                             gasket_compression_max_m=float(max(np.maximum(Dg@q0,0))),
                             residual=residual,iterations=meta['iterations'])
                preloads.append(preload)
                lin=MountedFront(p,Kt,base.M,base.B,base.G,base.D,base.k,base.mass,base.positions)
                with (OUT/'p11_kalibracje_masy.csv').open() as f:
                    masses=[r for r in csv.DictReader(f) if r['candidate_id']=='C04' and r['reference']=='PISTON' and float(r['faces']) in [1.,2.]]
                for mass in masses:
                    for frequency in [20.,40.,80.]:
                        q,row=lin.prescribed_cone(frequency,.001,float(mass['effective_remaining_mass_kg']),.0458)
                        dynamic_gap=np.sqrt(2)*abs(Dg@q);static_gap=Dg@q0
                        opening=active & (static_gap-dynamic_gap<=0)
                        closing=(~active) & (static_gap+dynamic_gap>=0)
                        flagged=bool(np.any(opening)|np.any(closing))
                        worst_energy=max(worst_energy,row['relative_power_residual']);assert row['relative_power_residual']<1e-8
                        row.update(boundary=bc,contact_kn_pa_m=kn,initial_force_parameter_n=initial_force_parameter,
                                   reference_faces=float(mass['faces']),contact_status='SWITCHING_POSSIBLE_LINEARIZATION_NOT_QUALIFIED' if flagged else 'FIXED_CONTACT_AT_QUADRATURE_POINTS',
                                   opening_area_fraction=float(sum(area*opening)/sum(area)),closing_area_fraction=float(sum(area*closing)/sum(area)),
                                   maximum_dynamic_gasket_strain_peak=float(max(dynamic_gap)/.003),
                                   maximum_basket_motion_peak_m=float(np.sqrt(2)*abs(q[-3])),
                                   maximum_joint_increment_peak_n=float(np.sqrt(2)*max(abs(base.k*(base.D@q)))))
                        rows.append(row)
                print('P19B:',bc,kn,initial_force_parameter,'contactfraction',preload['contact_area_fraction'],flush=True)
            if bc=='CCCC' and kn==1e9:
                # Osobna kontrola całkowania,nie zmiana siatki samej płyty.
                for nr,nt in [(4,128),(6,256)]:
                    D,w,xy=contact_quadrature(p,.1536,.1721,nr,nt)
                    F=base.load(basket_force_n=-100.)
                    q,J,a,meta=solve_contact(base.K,D,w,kn,F)
                    mesh.append(dict(radial_quadrature=nr,angular_quadrature=nt,basket_m=float(q[-3]),
                                     strain_energy_work_j=float(F@q),contact_area_fraction=float(sum(w*a)/sum(w))))
    for name,data in [('p19b_docisk_i_styk.csv',preloads),('p19b_dynamika_i_bramki_styku.csv',rows)]:
        keys=list(dict.fromkeys(k for r in data for k in r))
        with (OUT/name).open('w',newline='') as f:
            writer=csv.DictWriter(f,keys);writer.writeheader();writer.writerows(data)
    result=dict(status='P19B_UNILATERAL_PRELOAD_AND_FROZEN_CONTACT_DIAGNOSTIC_NOT_CONTACT_TIME_ODE',
                static_cases=len(preloads),dynamic_cases=len(rows),input_sha256=input_hashes,reference_checks=checks,
                contact_quadrature_convergence=mesh,maximum_power_residual=worst_energy,
                switching_flagged=sum(r['contact_status'].startswith('SWITCHING') for r in rows),
                assumptions=['C04net7.68kg;CG80mm i J=m*(.1²+.08²) są hipotezami.',
                             'Uszczelka jako idealny pierścień153.6-172.1mm;kn1e8/1e9Pa/m umowne,nie konkretny produkt.',
                             'Grubość3mm tylko do diagnostyki odkształcenia,nie identyfikacja prawa materiału.',
                             'T0=k*delta0 jest parametrem skrócenia,nie końcową siłą/momentem dokręcania.',
                             'Brak tarcia,in-plane shear,otworówśrubowych,pełzania i lokalnej nośności3D.',
                             'Flagi otwierania/zamykania unieważniają użycie zamrożonego styku jako prognozy przebiegu.',
                             'Brak zewnętrznej radiacji i pełnej skrzyni;kontrole są w punktachkwadratury,nie ciągłym styku.'])
    (OUT/'p19b_podsumowanie.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False))
    print('P19B zakończone:',len(preloads),len(rows),'flagi',result['switching_flagged'])


if __name__=='__main__':main()
