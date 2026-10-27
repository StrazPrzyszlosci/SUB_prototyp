"""Wpływ nowego gazu modułu na skalarne obciążenie głównej komory.

Granica po wszystkich Ca>=Ca_min i0<=N<=16,przy ReY/ImY>=0 w zapisanychf.
Nie jest to granica ciągłego pasma,pola niejednorodnego lub rankingu produktów.
"""
from pathlib import Path
import csv,hashlib,json
import numpy as np
import sympy as sp
from geometria_przegrody_P20B import matched_geometry
from analiza_wkladow_P20A import table

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def main():
    cp=ROOT/'dane/konfiguracje/p21b_gaz_przestrzenny_modulu.json';cfg=json.loads(cp.read_text());scp=ROOT/cfg['solid_config'];scfg=json.loads(scp.read_text())
    bp=ROOT/scfg['reference_insert_config'];base=json.loads(bp.read_text());gp=ROOT/'dane/konfiguracje/p20b_przegroda_vs_moduly.json';gcfg=json.loads(gp.read_text())
    status=json.loads((OUT/'p21b_podsumowanie.json').read_text());assert status['cases']==status['expected_cases']==18
    geometry=matched_geometry(base,gcfg,16,.018,'LINER_GEOMETRY',driver_l=max(base['driver_displacement_l_stress_cases']))
    vmin=geometry['matched_active_air_l']*.001;Cmin=vmin/(1.4*101325.);rows=[]
    with (OUT/'p21b_macierze_admitancji.csv').open() as f:source=list(csv.DictReader(f))
    for r in source:
        if int(r['output_port'])!=0 or int(r['input_port'])!=0 or float(r['f_hz']) not in cfg['probe_frequencies_hz']:continue
        frequency=float(r['f_hz']);s=2j*np.pi*frequency
        Y=complex(float(r['admittance_re_m3_pa_s']),float(r['admittance_im_m3_pa_s']))
        Y0=complex(float(r['zero_dimensional_re_m3_pa_s']),float(r['zero_dimensional_im_m3_pa_s']))
        assert Y.real>=0 and Y.imag>=0
        bound=16*abs(Y-Y0)/abs(s*Cmin+16*Y)
        # Odrębne punkty dziedziny,nie certyfikat po częstotliwości.
        maximum=0.
        for volume_l in [vmin*1000,80.,100.,130.,300.]:
            if volume_l<vmin*1000:continue
            for count in [0.,.5,1.,4.,8.,16.]:
                C=volume_l*.001/(1.4*101325.)
                direct=abs((s*C+count*Y0)/(s*C+count*Y)-1)
                assert direct<=bound*(1+1e-7)+1e-14
                maximum=max(maximum,direct)
        rows.append(dict(case_id=r['case_id'],f_hz=frequency,minimum_active_air_l=vmin*1000,maximum_module_count=16,
            upper_relative_change_of_scalar_cavity_impedance=bound,largest_checked_grid_value=maximum,
            positive_real_admittance=float(Y.real),positive_imag_admittance=float(Y.imag),
            domain='Uniform main pressure,identical independent modules,geometric liner only,Ca>=Cmin,N<=16;finite frequencies,no exterior mutual reaction.'))
    C,n,w,yr,yi,d=sp.symbols('C n w yr yi d',positive=True);den=(n*yr)**2+(w*C+n*yi)**2
    R2=n*n*d*d/den
    dc=sp.simplify(sp.diff(R2,C)+2*n*n*d*d*w*(w*C+n*yi)/den**2)
    dn=sp.simplify(sp.diff(R2,n)-2*n*d*d*w*C*(w*C+n*yi)/den**2)
    assert dc==dn==0 and sp.limit(R2,n,0)==0 and sp.limit(R2,C,sp.oo)==0
    table('p21b_granica_skalarnego_obciazenia.csv',rows)
    # Odrębny warunek siłowy:mała zmiana portu objętościowego nie usuwa
    # wypadkowej nacisku z gradientem. Nie jest to prognoza pola głównej skrzyni.
    models=list(csv.DictReader((OUT/'p21b_modele_i_geometria.csv').open()))
    reference=next(r for r in models if r['case_id']=='TIED_E1.718e+09_N12')
    state=ROOT/status['reference_state_file']
    with np.load(state,allow_pickle=False) as data:
        nodal=data['Hext'].reshape(-1,3,2);net=np.sum(nodal,axis=0)
        moment=np.sum(np.cross(data['solid_xyz'][:,:,None],nodal,axisa=1,axisb=1,axisc=1),axis=0)
    W,D,H=scfg['outer_width_depth_height_m'];volume=W*D*H;expected=np.array([-volume/W,0.,0.])
    assert np.linalg.norm(net[:,0])<1e-12 and np.linalg.norm(net[:,1]-expected)<1e-12
    assert np.linalg.norm(moment[:,1]-np.cross(np.array([W,D,H])/2,expected))<1e-12
    rho=float(reference['gas_mass_kg'])/(float(reference['gas_volume_l'])*.001)
    apparent_mass=float(reference['dry_solid_mass_kg'])+float(reference['gas_mass_kg'])-rho*volume
    weight=apparent_mass*9.80665;span=W-2*base['mount_support_inset_m'];lever=H/2;force_rows=[]
    pressure_screen=.01*101325/(np.sqrt(2)*1.5)
    for pressure in [1.,100.,300.,500.]:
        peak=np.sqrt(2)*abs(expected[0])*pressure;minimum=weight/4-peak*lever/(2*span)
        force_rows.append(dict(outer_modal_pressure_rms_pa=pressure,field='1+(x-W/2)/W',net_horizontal_force_peak_n=peak,
            apparent_weight_n=weight,minimum_quasistatic_normal_reaction_n=minimum,required_global_friction_coefficient=peak/weight,
            preserves_four_compression_only_contacts_quasistatically=bool(minimum>0),within_assumed_outer1pct_pressure_screen=bool(pressure<=pressure_screen),
            scope='Conditional field,4supports with specified span,gravity/buoyancy only,no fixed anchors;quasistatic necessary checks,not dynamic safety or actual main field.'))
    table('p21b_sily_przy_wymuszonym_gradiencie.csv',force_rows)
    inputs=[cp,scp,bp,gp,Path(__file__),ROOT/'skrypty/geometria_przegrody_P20B.py',OUT/'p21b_macierze_admitancji.csv',
        OUT/'p21b_modele_i_geometria.csv',state]
    result=dict(status='CONTINUOUS_Ca_N_BOUND_AT_FINITE_FREQUENCIES_NOT_FULL_SYSTEM_DOMINANCE',cases=len(rows),minimum_active_air_l=vmin*1000,
        maximum_relative_impedance_change=max(r['upper_relative_change_of_scalar_cavity_impedance'] for r in rows),
        prescribed_gradient_force_per_modal_pa_n=expected.tolist(),apparent_weight_n=weight,
        quasistatic_four_contact_pressure_threshold_rms_pa=weight*span/(2*lever*np.sqrt(2)*abs(expected[0])),
        assumed_outer1pct_pressure_screen_rms_pa=pressure_screen,
        algebra=dict(negative_C_derivative_identity=str(dc),positive_N_derivative_identity=str(dn)),
        input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        limitations=['Bound assumes ImY>=0;outside band/resonant inductive branches need a separate analysis.',
            'No conversion to room SPL,THD or probability of a product winning.',
            'Gradient force budget is a conditional quasistatic check with assumed support span/friction and buoyancy;it does not solve actual mounting dynamics.',
            'Nonuniform exterior forcing and actual mounting remain a distinct task;do not replace them by this scalar bound.'])
    (OUT/'p21b_granica_obciazenia_podsumowanie.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print('P21B scalar load bound:',len(rows),'rows,max',result['maximum_relative_impedance_change'],flush=True)


if __name__=='__main__':main()
