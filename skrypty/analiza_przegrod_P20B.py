"""P20B: geometria rzeczywistego gazu,56rodzin mechaniki i dwie komory.

Nie kwalifikacja uszczelki lub nośności. Brak objętości niezaprojektowanego
osprzętu pozostaje jawną bramką,nie ukrytą estymacją.
"""
from pathlib import Path
from itertools import product
import hashlib,json,platform
import numpy as np
import scipy
from model_przegrody_P20B import Partition,two_chamber
from geometria_przegrody_P20B import matched_geometry
from analiza_wkladow_P20A import table
from model_gazu import Medium,conductance_from_reference
from model_wypelnienia import CircularPores

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki';CFG=ROOT/'dane/konfiguracje/p20b_przegroda_vs_moduly.json'


def structural_cases(base,cfg,n=None):
    for thickness in cfg['partition_thickness_m']:
        t=int(round(thickness*1000))
        for bc in ['SSSS','CCCC']:
            yield f'T{t}_PERIM_{bc}_RIGID',Partition(base,cfg,thickness,'PERIM',bc,np.inf,n)
            for k in cfg['support_stiffness_each_n_m_cases']:
                yield f'T{t}_PERIM_{bc}_K{k:g}',Partition(base,cfg,thickness,'PERIM',bc,k,n)
        for k in cfg['support_stiffness_each_n_m_cases']:
            yield f'T{t}_PATCH4_K{k:g}',Partition(base,cfg,thickness,'PATCH4','FREE',k,n)


def active_compliance(base,geometry,lining,driver_l,f,medium):
    air=(geometry['matched_active_air_l']-(driver_l-geometry['driver_displacement_l_stress_axis']))*.001
    if lining in ['AIR_ONLY','LINER_GEOMETRY']:return np.full_like(np.asarray(f),air/(medium.gamma*medium.p0_pa),dtype=complex),air
    V=geometry['front_liner_envelope_l']*.001;phi=base['lining_geometric_porosity_assumed']
    material=CircularPores(base['lining_pore_radius_m_assumed'],phi,'rigid',base['lining_dry_density_kg_m3_assumed'])
    _,bulk=material.equivalent_properties(f,medium)
    C=(air-phi*V)/(medium.gamma*medium.p0_pa)+V/bulk
    return C,air


def conductance(value,medium):
    return conductance_from_reference(np.inf if value=='inf' else value,medium)


def main():
    cfg=json.loads(CFG.read_text());basepath=ROOT/cfg['reference_insert_config'];base=json.loads(basepath.read_text())
    medium=Medium();f=np.array(base['probe_frequencies_hz']);s=2j*np.pi*f
    geometries=[]
    for n,t,lining,host in product(cfg['equivalent_removed_module_counts'],cfg['partition_thickness_m'],['AIR_ONLY','LINER_GEOMETRY'],['FIXED','EXTENDED_FOR_BASELINE']):
        geometries.append(matched_geometry(base,cfg,n,t,lining,host=host))
    table('p20b_pozycje_i_dostep.csv',geometries)
    models=[];structural_ports=[];network_rows={};amplitude=[];max_energy=0.
    for mid,m in structural_cases(base,cfg):
        response=m.response(f);chi=response['compliance'];max_energy=max(max_energy,response['power_residual'])
        models.append(dict(model_id=mid,thickness_mm=m.thickness*1000,kind=m.kind,boundary=m.boundary,
            support_each_n_m='inf' if np.isposinf(m.k_each) else m.k_each,
            plate_mass_kg=m.plate_mass,seal_mass_assumed_kg=m.seal_mass,carriage_mass_assumed_kg=m.carriage_mass,
            total_moving_mass_kg=m.total_mass,panel_a_m=m.a,panel_b_m=m.b,static_compliance_m3_pa=m.static_compliance,
            lowest_dry_supported_eigenfrequency_hz=float(np.sqrt(m.values[0])/(2*np.pi)),mass_cross_relative_error=m.mass_cross_error,
            rigid_mass_relative_error=m.rigid_mass_error,beta_material_s=m.beta,gamma_support_s=m.gamma))
        for j,freq in enumerate(f):
            structural_ports.append(dict(model_id=mid,f_hz=float(freq),compliance_re_m3_pa=float(chi[j].real),compliance_im_m3_pa=float(chi[j].imag),
                max_absolute_y_peak_per_pa_rms=float(response['peak_absolute_y_per_pa'][j]),
                max_bending_y_peak_per_pa_rms=float(response['peak_bending_y_per_pa'][j]),
                max_support_force_rms_per_pa=float(max(abs(response['support_force_rms_per_dp'][:,j]))),
                material_loss_per_dp_rms2_w=float(response['material_loss_w_per_dp_rms2'][j]),
                support_loss_per_dp_rms2_w=float(response['support_loss_w_per_dp_rms2'][j])))
        cases=[]
        for geometry in geometries:
            if abs(geometry['thickness_m']-m.thickness)>1e-12 or not geometry['feasible_with_rear_gap']:continue
            for lining in (['AIR_ONLY'] if geometry['lining']=='AIR_ONLY' else ['LINER_GEOMETRY','LINER_THERMAL_LAYOUT']):
                cases.append((geometry,lining,1.4,0.,0.,True))
                if lining=='AIR_ONLY':cases.append((geometry,lining,1.,0.,0.,False))
        fault_ids={'T18_PERIM_CCCC_RIGID','T18_PERIM_CCCC_K10000','T18_PERIM_CCCC_K1e+06','T18_PATCH4_K1e+06','T18_PATCH4_K1e+07'}
        if mid in fault_ids:
            for n,gs,gv in product([8,16],cfg['perimeter_leak_100l_reference_corner_hz'],cfg['rear_vent_100l_reference_corner_hz']):
                geometry=next(g for g in geometries if g['module_count']==n and g['lining']=='LINER_GEOMETRY' and g['host']=='FIXED' and abs(g['thickness_m']-.018)<1e-12)
                cases.append((geometry,'LINER_GEOMETRY',1.4,gs,gv,False))
        for geometry,lining,kappa,seal_corner,vent_corner,screen in cases:
            Ca,air=active_compliance(base,geometry,lining,4.,f,medium)
            Cb=geometry['rear_geometric_air_l']*.001/(kappa*medium.p0_pa)
            Gs,Gv=conductance(seal_corner,medium),conductance(vent_corner,medium)
            r=two_chamber(f,Ca,Cb,chi,Gs,Gv);max_energy=max(max_energy,r['power_residual'])
            zin=r['input_impedance'];delta=r['partition_dp_per_input']
            for j,freq in enumerate(f):
                key=(mid,geometry['module_count'],geometry['host'],lining,kappa,str(seal_corner),str(vent_corner),float(freq))
                pressure_release=abs(zin[j])==0
                extra=None if pressure_release else medium.gamma*medium.p0_pa*(1/zin[j]-s[j]*Ca[j])/s[j]*1000
                network_rows[key]=dict(model_id=mid,module_count_equivalent=geometry['module_count'],host=geometry['host'],lining=lining,rear_kappa=kappa,
                    seal_100l_reference_corner_hz=seal_corner,vent_100l_reference_corner_hz=vent_corner,f_hz=float(freq),
                    front_air_l=air*1000,rear_air_l=geometry['rear_geometric_air_l'],position_m=geometry['matched_position_from_inner_front_m'],
                    input_impedance_re_pa_s_m3=float(zin[j].real),input_impedance_im_pa_s_m3=float(zin[j].imag),
                    added_equivalent_storage_l=None if extra is None else float(extra.real),added_equivalent_loss_l=None if extra is None else float(-extra.imag),
                    ideal_pressure_release=pressure_release,vent_flow_gain_abs=float(abs(r['vent_flow_per_input'][j])),
                    vent_flow_gain_phase_rad=float(np.angle(r['vent_flow_per_input'][j])),
                    reduced_power_residual=r['power_residual'])
                if screen:
                    # Znane ciśnienie komory przedniej; nie rzeczywisty poziom sterowania.
                    dp_over_pa=delta[j]/zin[j];pb_over_pa=r['rear_pressure_per_input'][j]/zin[j]
                    travel=min(geometry['rear_length_m'],geometry['matched_position_from_inner_front_m']-.392)
                    for pressure in cfg['amplitude_screen_main_pressure_rms_pa_cases']:
                        bending=float(response['peak_bending_y_per_pa'][j]*abs(dp_over_pa)*pressure)
                        motion=float(response['peak_absolute_y_per_pa'][j]*abs(dp_over_pa)*pressure)
                        gas_peak=np.sqrt(2)*pressure*max(1.,abs(pb_over_pa))/medium.p0_pa
                        amplitude.append(dict(model_id=mid,module_count_equivalent=geometry['module_count'],host=geometry['host'],lining=lining,f_hz=float(freq),
                            front_pressure_rms_pa=pressure,bending_peak_over_thickness=bending/m.thickness,
                            maximum_absolute_motion_peak_m=motion,minimum_axial_travel_clearance_m=travel,
                            maximum_gas_pressure_peak_fraction=float(gas_peak),
                            required_support_force_peak_n=float(np.sqrt(2)*pressure*abs(dp_over_pa)*max(abs(response['support_force_rms_per_dp'][:,j]))),
                            gravity_shear_mean_per_support_n=m.total_mass*9.80665/4,
                            within_assumed_domain=bool(bending/m.thickness<=cfg['small_bending_w_over_t_limit_assumed'] and motion<travel and gas_peak<=cfg['gas_peak_pressure_fraction_limit_assumed'])))
        print('P20B model:',mid,'C0',m.static_compliance,flush=True)
    assert len(models)==56 and len(geometries)==80
    table('p20b_modele_przegrody.csv',models);table('p20b_porty_mechaniczne.csv',structural_ports)
    table('p20b_dwie_komory_i_nieszczelnosc.csv',list(network_rows.values()));table('p20b_dziedzina_amplitudy.csv',amplitude)
    inputs=[CFG,basepath,Path(__file__),ROOT/'skrypty/model_przegrody_P20B.py',ROOT/'skrypty/geometria_przegrody_P20B.py',
            ROOT/'skrypty/geometria_wkladow_P20A.py',ROOT/'skrypty/model_plyty_MITC_P18.py',ROOT/'skrypty/model_wypelnienia.py',
            ROOT/'skrypty/model_gazu.py',ROOT/'skrypty/analiza_wkladow_P20A.py',ROOT/'brief_system_audio_DIY_v0.6.md']
    result=dict(status='PARTITION_AND_BACK_CHAMBER_FAMILIES_NOT_FINISHED_SERVICEABLE_ASSEMBLY',date='2026-10-26',
        cases=dict(structural_models=len(models),geometry_rows=len(geometries),mechanical_port_rows=len(structural_ports),network_rows=len(network_rows),amplitude_rows=len(amplitude)),
        checks=dict(max_normalized_power_residual=max_energy,infeasible_fixed_maximum_geometry_rows=sum(not g['feasible_with_rear_gap'] for g in geometries),
                    flagged_amplitude_rows=sum(not r['within_assumed_domain'] for r in amplitude)),
        libraries=dict(Python=platform.python_version(),NumPy=np.__version__,SciPy=scipy.__version__),
        input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},limitations=cfg['gates'])
    (OUT/'p20b_podsumowanie.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print('P20B COMPLETE:',result['cases'],result['checks'],flush=True)


if __name__=='__main__':main()
