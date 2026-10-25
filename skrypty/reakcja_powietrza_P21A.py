"""P21A: kontrolne sprzężenie elastycznej płyty z Rayleighem i gazem0D.

Nieskończona odgroda,identyczna para ścian,inne4sztywne. Nie pole3Dskrzyni
z otworem ani pokój. Słabą osobliwość urojonego jądra zastępuje lokalna
masa dysku o polu wagi kwadratury; sprawdzamy jej zbieżność niezależnie.
"""
import csv
import json
from pathlib import Path
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve
from scipy.spatial.distance import cdist
from model_gazu import Medium,ThermalSpectrum
from model_plyty_MITC_P18 import RectangularPlate,PlateMaterial,shape
from analiza_plyt_i_sciagow_P18A import jobs,build_case

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def surface(plate):
    g=np.array([-1.,1.])/np.sqrt(3);points=[];weights=[];rows=[];cols=[];values=[];idx=0
    inverse=np.full(len(plate.full_F),-1,int);inverse[plate.free]=np.arange(len(plate.free))
    transverse=np.flatnonzero(plate.free%3==0);winverse=np.full(len(plate.free),-1,int);winverse[transverse]=np.arange(len(transverse))
    for corners,dofs in zip(plate.elements,plate.dofs):
        x0,y0=plate.xy[corners[0]]
        for xi in g:
            for eta in g:
                N,_,_=shape(xi,eta,plate.dx,plate.dy)
                points.append([x0+(1+xi)*plate.dx/2,y0+(1+eta)*plate.dy/2]);weights.append(plate.dx*plate.dy/4)
                ids=inverse[dofs[0::3]];valid=ids>=0
                rows.extend([idx]*sum(valid));cols.extend(winverse[ids[valid]]);values.extend(N[valid]);idx+=1
    N=sparse.coo_matrix((values,(rows,cols)),shape=(idx,len(transverse))).tocsr()
    weights=np.array(weights);points=np.array(points)
    return dict(points=points,weights=weights,N=N,A=sparse.diags(weights)@N,distances=cdist(points,points),transverse=transverse)


def radiation_operator(f,geometry,medium=Medium()):
    w=2*np.pi*f;k=w/medium.c;distance=geometry['distances'];weights=geometry['weights']
    R=medium.rho*w/(2*np.pi)*k*np.sinc(k*distance/np.pi)
    inv=np.divide(1.,distance,out=np.zeros_like(distance),where=distance>0)
    X=medium.rho*w/(2*np.pi)*np.cos(k*distance)*inv
    # Efektywna urojona reakcja własna z niskoka masy tłokaP11/A.
    radius=np.sqrt(weights/np.pi)
    np.fill_diagonal(X,medium.rho*w/(2*np.pi)*(16*radius/(3*weights)))
    kernel=R+1j*X;A=geometry['A'];Z=A.T@(kernel@A);Z=np.asarray(Z)
    return (Z+Z.T)/2


def uniform_rectangular_added_mass(a,b,medium=Medium(),order=100):
    g,w=np.polynomial.legendre.leggauss(order);z=(g+1)/2;w=w/2
    integral=4*a*a*b*b*sum(w*(.5-z/6)*(1/np.sqrt(a*a+b*b*z*z)+1/np.sqrt(a*a*z*z+b*b)))
    return medium.rho/(2*np.pi)*integral


def mass_control():
    reference=uniform_rectangular_added_mass(.46,.64);rows=[];medium=Medium()
    for mesh in [4,8,12,16]:
        # FREEtu służy tylko reprezentacji stałej prędkości,nie rozwiązywaniu statyki.
        p=RectangularPlate(.46,.64,mesh,mesh,PlateMaterial(2.1e9,.3,730,.022),'FREE');g=surface(p);Z=radiation_operator(.01,g,medium)
        ones=np.ones(len(g['transverse']));mass=float(np.vdot(ones,Z.imag@ones).real/(2*np.pi*.01))
        error=float(abs(mass/reference-1));rows.append(dict(mesh=mesh,added_mass_kg=mass,relative_error=error))
    assert rows[-1]['relative_error']<.015 and rows[-1]['relative_error']<rows[0]['relative_error']
    return dict(reference_added_mass_kg=float(reference),mesh_convergence=rows)


def main():
    cfg=json.loads((ROOT/'dane/konfiguracje/p18a_plyty_i_sciagi.json').read_text());data=json.loads((ROOT/'dane/materialy/mdf_i_kleje_P18_P19.json').read_text())
    cases=jobs(cfg);rows=[];medium=Medium();cache_geom={};eigenR=[]
    for case in cases:
        if not(case['geometry']['id']=='K2_side' and case['material']['id']=='REFERENCE' and case['thickness_mm']==22 and case['zeta']==.03
            and case['boundary'] in ['SSSS','CCCC'] and 'joint_factor' not in case and 'edge_beta' not in case):continue
        p,K,M,ties,prop=build_case(case,cfg,data);freq,modes,_=p.modes(8,K,M)
        fstatic=p.F@p.static(K);participation=(p.F@modes)**2/(2*np.pi*freq)**2/fstatic
        selected_mode=int(np.argmax(participation));fdominant=float(freq[selected_mode]);w1=2*np.pi*freq[0];w2=5*w1
        zeta=.03;C=2*zeta*w1*w2/(w1+w2)*M+2*zeta/(w1+w2)*K
        if case['boundary'] not in cache_geom:cache_geom[case['boundary']]=surface(p)
        geom=cache_geom[case['boundary']];index=geom['transverse']
        frequencies=np.unique(np.r_[20.,40.,80.,np.linspace(.85*fdominant,1.15*fdominant,9)])
        for f in frequencies:
            w=2*np.pi*f;Z=radiation_operator(f,geom,medium)
            # Ogólna zasadaR>=0 i wzajemność; nie tylko dodatnia moc jednej odpowiedzi.
            ev=np.linalg.eigvalsh(Z.real);ratio=float(ev[0]/max(ev[-1],1e-30));assert ratio>-1e-9
            eigenR.append(ratio)
            rr=np.repeat(index,len(index));cc=np.tile(index,len(index))
            R=sparse.coo_matrix((Z.ravel(),(rr,cc)),shape=K.shape).tocsr()
            dry=spsolve(K-w*w*M+1j*w*C,p.F)
            q=spsolve(K-w*w*M+1j*w*C+1j*w*R,p.F)
            compliance=p.F@q;structural=float(w*w*np.vdot(q,C@q).real)
            velocity=1j*w*q[index];rad=float(np.vdot(velocity,Z.real@velocity).real)
            supplied=float(-w*compliance.imag)
            error=abs(supplied-structural-rad)/max(abs(supplied),1e-30);assert error<1e-8 and rad>=-1e-12
            # Samouzgodniony wymuszony ruch stożka95dB/4pi1m w komorze100l.
            s=1j*w;bulk=ThermalSpectrum((.005,),(1.,)).bulk_modulus(np.array([f]),medium)[0];Cab=.1/bulk
            ext=20e-6*10**(95/20);Q=-ext*4*np.pi*np.exp(s/medium.c)/(medium.rho*s)
            pressure=Q/(s*(Cab+2*compliance));cone_power=float((pressure*np.conj(Q)).real)
            gas=float(-w*Cab.imag*abs(pressure)**2);walls=2*(structural+rad)*abs(pressure)**2
            coupled_error=abs(cone_power-gas-walls)/max(abs(cone_power),1e-30);assert coupled_error<1e-8
            rows.append(dict(case_id=case['case_id'],boundary=case['boundary'],tie_count=case['tie_count'],f_hz=float(f),
                dry_pressure_dominant_mode_hz=fdominant,mode_uniform_compliance_fraction=float(participation[selected_mode]),
                minimum_normalized_radiation_resistance_eigenvalue=ratio,
                maximum_node_displacement_ratio_with_to_without_air=float(max(abs(p.transverse_displacements(q)))/max(abs(p.transverse_displacements(dry)))),
                panel_structural_power_per_Pa2_w=structural,panel_radiation_power_per_Pa2_w=rad,panel_supplied_power_per_Pa2_w=supplied,
                panel_power_relative_residual=float(error),inner_pressure_rms_at_reference_pa=float(abs(pressure)),
                cone_supplied_power_at_reference_w=cone_power,gas_heat_at_reference_w=gas,
                pair_structural_plus_radiation_at_reference_w=walls,coupled_power_relative_residual=float(coupled_error),
                gas_spatial_scope='LOWBAND_CONTROL' if f<=80 else '0D_CAVITY_EXTRAPOLATION_NOT_FULL_SPATIAL_FIELD'))
        print('P21Acoupled:',case['case_id'],flush=True)
    checks=mass_control()
    with (OUT/'p21a_para_scian_z_reakcja_powietrza.csv').open('w',newline='') as h:
        writer=csv.DictWriter(h,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    summary=dict(status='P21A_COUPLED_REFERENCE_BAFFLE_AND_0D_CAVITY_NOT_REAL_BOX',rows=len(rows),added_mass_control=checks,
        max_panel_power_residual=max(r['panel_power_relative_residual'] for r in rows),
        max_coupled_power_residual=max(r['coupled_power_relative_residual'] for r in rows),
        min_normalized_R_eigenvalue=min(eigenR),
        scope='Uwzględniono dodatnią radiacyjną rezystancję i przybliżoną reakcję masową z kontrolą siatki. Nie ma geometrii3D,kosza,otworów,pola przestrzennego komory i pokoju. Brak globalnego certyfikatu całego pasma/mocy.')
    (OUT/'p21a_sprzezenie_podsumowanie.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False,allow_nan=False));print(json.dumps(summary,indent=2,ensure_ascii=False));return summary


if __name__=='__main__':main()
