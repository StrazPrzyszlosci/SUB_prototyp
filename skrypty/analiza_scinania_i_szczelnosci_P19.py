"""P19: częściowe zespolenie dwóch warstw, wymagania ścinania i otwarta szczelina.

Oddzielne modele1D; brak dowodu3D/fatigue i brak utożsamienia odkształcenia
wypełnionej spoiny z pustą szczeliną powietrzną.
"""
import csv
import json
from pathlib import Path
import numpy as np
import sympy as sp
from model_gazu import Medium
from model_szczeliny_P19 import slit_impedance

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def table(name,rows):
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with (OUT/name).open('w',newline='') as h:
        w=csv.DictWriter(h,fieldnames=fields);w.writeheader();w.writerows(rows)


def main():
    E,h,d,k,ks,W,U=sp.symbols('E h d k ks W U',positive=True)
    # Średnia energiaosiowa+ścinania dla wspólnego w=Wsin(kx),u1-u2=Ucos(kx).
    energy=E*h*k*k*U*U/8+ks*(U+d*k*W)**2/4
    optimum=-d*k*W/(1+E*h*k*k/(2*ks))
    assert sp.factor(sp.diff(energy,U).subs(U,optimum))==0
    equivalent=sp.factor(4*energy.subs(U,optimum)/(k**4*W**2))
    expected=E*h*d*d/2/(1+E*h*k*k/(2*ks))
    assert sp.factor(equivalent-expected)==0
    mu,L,width,gap,dp,z=sp.symbols('mu L width gap dp z',positive=True)
    velocity=dp/(2*mu*L)*(gap**2/4-z*z)
    flow=sp.integrate(velocity,(z,-gap/2,gap/2))*width
    assert sp.factor(flow-width*gap**3*dp/(12*mu*L))==0
    y=sp.symbols('y');low_series=sp.series((y*y/3)/(1-sp.tanh(y)/y),y,0,6)
    assert sp.expand(low_series.removeO()).coeff(y,2)==sp.Rational(2,5)
    data=json.loads((ROOT/'dane/materialy/kleje_P19_mechanika_v1.json').read_text());Efilm=data['EA9466']['tensile_modulus_pa']
    nu_assumed=.35;Gfilm=Efilm/(2*(1+nu_assumed));Ewood=2.2e9;twood=.018;composite=[]
    for length in [.3,.4,.5,.64]:
        for mode in [1,3,5]:
            wave=mode*np.pi/length
            for thickness in [.00005,.0002,.0005]:
                sep=twood+thickness;D0=Ewood*twood**3/6;Dfull=D0+Ewood*twood*sep**2/2
                eta_req=(.95*Dfull-D0)/(Dfull-D0)
                k_required=Ewood*twood*wave**2/(2*(1/eta_req-1));Greq=k_required*thickness
                for retained in [1.,.1,.01]:
                    actualG=Gfilm*retained;eta=1/(1+Ewood*twood*wave**2/(2*actualG/thickness));Deff=D0+(Dfull-D0)*eta
                    composite.append(dict(length_m=length,mode=mode,glue_gap_m=thickness,Ewood_pa=Ewood,glue_nu_assumed=nu_assumed,
                        Gfilm_from_typical_E_pa=Gfilm,modulus_retention_stress=retained,required_G_for_95pct_composite_pa=float(Greq),
                        nominal_G_to_required_ratio=float(actualG/Greq),effective_bending_rigidity_nm=float(Deff),
                        stiffness_to_full_composite=float(Deff/Dfull),frequency_to_full_composite=float(np.sqrt(Deff/Dfull)),
                        scope='DWIEPELNE_WARSTWY18MM_BEAMSTRIP_BEZOTWORU_RETENCJA_NIE_CZAS_PELZANIA'))
    table('p19a_zespolenie_i_wymagane_G.csv',composite)
    strengths=[]
    for pressure in [1000.,5000.]:
        for length in [.3,.4,.5,.64]:
            Vline=pressure*length/2;interface_shear=3*Vline/(4*twood)
            for f in [20.,80.]:
                strengths.append(dict(pressure_peak_pa=pressure,strip_span_m=length,ply_thickness_m=twood,
                    ideal_interface_shear_peak_pa=interface_shear,required_shear_strength_for_multiplier3_pa=3*interface_shear,
                    frequency_hz=f,cycles1000h_continuous=f*3600*1000,
                    scope='STATYCZNY_BELKOWY_PRZEPIS_QV_I_IDEALNEZESPOLENIE_NIE_ZNANA_WYTRZYMALOSC_MDF_GLUE'))
    table('p19a_wymagania_scinania_i_cykli.csv',strengths)
    medium=Medium();leaks=[]
    for gap_m in [10e-6,50e-6,100e-6,200e-6,500e-6]:
        for width_m in [.001,.005,.01]:
            for length in [.018,.022,.025]:
                R=12*medium.viscosity_pa_s*length/(width_m*gap_m**3)
                Ma=medium.rho*length/(width_m*gap_m)
                for pressure in [100.,1000.,5000.]:
                    volume_flow=pressure/R;speed=volume_flow/(width_m*gap_m);Dh=2*width_m*gap_m/(width_m+gap_m)
                    Re=medium.rho*speed*Dh/medium.viscosity_pa_s
                    for f in [20.,80.]:
                        Wo=gap_m/2*np.sqrt(2*np.pi*f*medium.rho/medium.viscosity_pa_s)
                        impedance=slit_impedance([f],gap_m,width_m,length,medium)[0]
                        ac_flow=pressure/abs(impedance);ac_speed=ac_flow/(width_m*gap_m);Re_ac=medium.rho*ac_speed*Dh/medium.viscosity_pa_s
                        admitted=Re_ac<=100 and ac_speed/medium.c<=.05 and gap_m/width_m<=.1 and pressure/medium.p0_pa<=.05
                        leaks.append(dict(open_gap_height_m=gap_m,width_m=width_m,path_length_m=length,pressure_amplitude_pa=pressure,f_hz=f,
                            DC_resistance_pa_s_m3=R,slug_inertance_kg_m4=Ma,DC_Poiseuille_volume_flow_m3_s=volume_flow,
                            mean_speed_m_s=speed,Re_hydraulic=Re,Mach=speed/medium.c,Wo_half_gap=Wo,
                            linear_Stokes_impedance_real=impedance.real,linear_Stokes_impedance_imag=impedance.imag,
                            AC_peak_flow_m3_s=ac_flow,AC_peak_mean_speed_m_s=ac_speed,AC_peak_Re=Re_ac,AC_peak_Mach=ac_speed/medium.c,
                            low_frequency_inertance_kg_m4=1.2*Ma,DC_approx_Wo_screen_passed=Wo<=.3,
                            relaxation_tau_iso_for100l_s=R*.1/medium.p0_pa,
                            in_declared_conservative_flow_domain=admitted,
                            scope='OTWARTA_PUSTA_SZCZELINA_NIE_GRUBOSC_WYPELNIONEJ_SPOINY;PozaDZIEDZINA_NIEPROGNOZUJ_JETNOISE'))
    table('p19a_otwarte_szczeliny_i_dziedzina.csv',leaks)
    process=[]
    for area_name,area in [('front_control_500x500mm',.25),('one_edge_500x22mm',.5*.022)]:
        for pressure in [.7e6,1e6]:
            process.append(dict(area_name=area_name,area_m2=area,reference_press_pressure_pa=pressure,force_if_applied_n=area*pressure,
                scope='TDS303dotyczyLamel/drewnaKlejonego_NIEprzepisCisnieniaNaFrontMDF'))
    table('p19a_docisk_procesowy_referencje.csv',process)
    # Odrębne granice dokładnegoZ,bez dopasowania parametrów.
    ztest=slit_impedance([0.,1e-4,20.,80.,1e7],100e-6,.005,.022,medium)
    dc=12*medium.viscosity_pa_s*.022/(.005*(100e-6)**3);inertia=1.2*medium.rho*.022/(.005*100e-6)
    assert abs(ztest[0]/dc-1)<1e-14 and abs(ztest[1].imag/(2*np.pi*1e-4)/inertia-1)<1e-8
    assert np.all(ztest.real>=0)
    result=dict(status='P19A_SHEAR_LEAK_AND_PROCESS_REQUIREMENTS_NOT_LIFETIME_QUALIFICATION',symbolic_identities=['AxialSlipEnergyStationary=0','CompositeD=0','SlitStokesFlow=0','LowFrequencyInertance6over5'],
        composite_rows=len(composite),shear_cycle_rows=len(strengths),open_slit_rows=len(leaks),flow_rows_outside_declared_domain=sum(not r['in_declared_conservative_flow_domain'] for r in leaks),
        full_to_unbonded_two_layer_static_stiffness_factor=4.,full_to_unbonded_two_layer_frequency_factor=2.,
        full_unbonded_factor_scope='Granica zerowej grubości spoiny dwóch jednakowych18mmwarstw,nie każda geometria frontu.',
        PVAc303_wet_layer_m_from100_130g_m2=[.1/1100,.13/1100],
        maximum_open_slit_Poiseuille_speed_m_s=max(r['mean_speed_m_s'] for r in leaks),
        scope='Hipotezy modułuretencji nie są zmierzonym J(t). WytrzymałościMDFfatigue/pełzania nie uzupełniono domysłem. Otwartej szczeliny nie utożsamiać z rozciągniętą,ale ciągłą spoiną.')
    (OUT/'p19a_scinanie_szczelnosc_podsumowanie.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False));print(json.dumps(result,indent=2,ensure_ascii=False));return result


if __name__=='__main__':main()
