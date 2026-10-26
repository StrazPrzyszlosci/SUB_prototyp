"""P20B: porównanie przy tej samej ilości gazu; wentylacja to osobna diagnostyka.

Osobne sinusy ustalone20–80Hz. Front2pi/1m i dwa monopole4pi nie są
jednym protokołem. Nie wskazuje THD,bezpiecznego czasu lub SPL w pokoju.
"""
from pathlib import Path
from itertools import product
import hashlib,json
import numpy as np
from scipy.linalg import eigh
from analiza_przegrod_P20B import structural_cases,active_compliance,conductance
from model_przegrody_P20B import two_chamber
from geometria_przegrody_P20B import matched_geometry
from model_wkladu_P20A import HollowModule
from model_wypelnienia import CircularPores,response_with_acoustic_impedance
from model_gazu import Medium
from analiza_rozszerzenia_SB import candidates
from analiza_wkladow_P20A import table

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki';CFG=ROOT/'dane/konfiguracje/p20b_przegroda_vs_moduly.json'


class ModuleReference:
    """Ten sam materiałowy beta*K co w przegrodzie; nie zmienia danych P20A."""
    def __init__(self,base,cfg,f):
        self.m=HollowModule(base['selected_comparison_outer_width_length_height_m'],.008,'CCCC',base,braced=True)
        beta=2*cfg['material_loss_zeta_at_reference_assumed']/(2*np.pi*cfg['material_loss_reference_hz'])
        s=2j*np.pi*np.asarray(f);chi=np.zeros(len(f),complex);peak=np.zeros(len(f))
        for port in self.m.faces:
            values,V=eigh(port.K.toarray(),port.M.toarray());a=V.T@port.plate.F
            q=V@(a[:,None]/(values[:,None]*(1+s*beta)+s*s))
            chi+=2*(port.plate.F@q)
            peak=np.maximum(peak,np.sqrt(2)*np.max(abs(port.plate.transverse_displacements(q)),axis=0))
        Ci=self.m.inner_volume/(1.4*101325.)
        self.pressure_ratio=chi/(chi+Ci)
        self.admittance=s*Ci*self.pressure_ratio
        self.peak_bending_per_front_pa=peak*abs(1-self.pressure_ratio)


def module_active_compliance(base,geometry,lining,driver_l,f,medium):
    Ca,air=active_compliance(base,geometry,'AIR_ONLY' if lining=='AIR_ONLY' else 'LINER_GEOMETRY',driver_l,f,medium)
    if lining=='LINER_THERMAL_LAYOUT':
        V=geometry['module_reference_liner_envelope_l']*.001;phi=base['lining_geometric_porosity_assumed']
        _,B=CircularPores(base['lining_pore_radius_m_assumed'],phi,'rigid',base['lining_dry_density_kg_m3_assumed']).equivalent_properties(f,medium)
        Ca=(air-phi*V)/(medium.gamma*medium.p0_pa)+V/B
    return Ca,air


def main():
    cfg=json.loads(CFG.read_text());basepath=ROOT/cfg['reference_insert_config'];base=json.loads(basepath.read_text())
    medium=Medium();f=np.array(base['probe_frequencies_hz']);s=2j*np.pi*f
    models=dict(structural_cases(base,cfg));responses={mid:m.response(f) for mid,m in models.items()}
    module=ModuleReference(base,cfg,f);lookup={cid:d for cid,pid,d,cat in candidates()};ids=list(lookup)
    primary=['T18_PERIM_CCCC_RIGID','T18_PERIM_CCCC_K1e+06','T18_PATCH4_K1e+06','T25_PATCH4_K1e+07']
    faults=['T18_PERIM_CCCC_RIGID','T18_PERIM_CCCC_K10000','T18_PERIM_CCCC_K1e+06','T18_PATCH4_K1e+06','T18_PATCH4_K1e+07']
    lining_cases=['AIR_ONLY','LINER_GEOMETRY','LINER_THERMAL_LAYOUT'];scenarios=[]
    for mid,n,lining,vd in product(primary+['MODULE_REFERENCE'],cfg['primary_module_counts'],lining_cases,base['driver_displacement_l_stress_cases']):
        scenarios.append((mid,n,lining,vd,0.,0.,ids))
    for mid,n,gs,gv in product(faults,[8,16],cfg['perimeter_leak_100l_reference_corner_hz'],cfg['rear_vent_100l_reference_corner_hz']):
        scenarios.append((mid,n,'LINER_GEOMETRY',4.,gs,gv,['C02','C04','C25','C26S']))
    rows={};max_energy=max_split=0.;flagged=0
    for mid,n,lining,vd,gs_ref,gv_ref,driver_ids in scenarios:
        is_module=mid=='MODULE_REFERENCE';m=None if is_module else models[mid]
        thickness=.018 if is_module else m.thickness
        geometry=matched_geometry(base,cfg,n,thickness,'AIR_ONLY' if lining=='AIR_ONLY' else 'LINER_GEOMETRY')
        assert geometry['feasible_with_rear_gap']
        if is_module:
            Ca,air=module_active_compliance(base,geometry,lining,vd,f,medium)
            Z=1/(s*Ca+n*module.admittance);vent=np.zeros_like(s);pb=np.zeros_like(s);delta=np.zeros_like(s)
            regulator_mass=n*module.m.dry_mass;rear_air=0.
        else:
            Ca,air=active_compliance(base,geometry,lining,vd,f,medium);Cb=geometry['rear_geometric_air_l']*.001/(1.4*medium.p0_pa)
            r=two_chamber(f,Ca,Cb,responses[mid]['compliance'],conductance(gs_ref,medium),conductance(gv_ref,medium))
            Z=r['input_impedance'];vent=r['vent_flow_per_input'];pb=r['rear_pressure_per_input'];delta=r['partition_dp_per_input']
            regulator_mass=m.plate_mass+m.seal_mass;rear_air=geometry['rear_geometric_air_l']
        Zideal=1/(s*Ca)
        for cid in driver_ids:
            d=lookup[cid];out=response_with_acoustic_impedance(d,f,Z,medium=medium);ideal=response_with_acoustic_impedance(d,f,Zideal,medium=medium)
            Qmem=d.sd*out['velocity_complex_m_s'];pa=out['p_inside_pa'];dp=-delta*Qmem;prear=-pb*Qmem
            max_energy=max(max_energy,float(max(abs(out['energy_residual_w'])/out['p_input_w'])))
            if is_module:
                material=np.real(n*module.admittance)*abs(pa)**2;seal=np.zeros_like(f);ventloss=np.zeros_like(f)
                total=np.real(s*Ca)*abs(pa)**2+material
                bendunit=module.peak_bending_per_front_pa*abs(pa)/module.m.wall
                gasunit=np.sqrt(2)*abs(pa)*np.maximum(1.,abs(module.pressure_ratio))/medium.p0_pa
                travelunit=np.zeros_like(f);forceindicator=np.full_like(f,np.nan)
            else:
                total=(r['active_loss_per_input2']+r['rear_loss_per_input2']+r['wall_loss_per_input2']+r['seal_loss_per_input2']+r['vent_loss_per_input2'])*abs(Qmem)**2
                rr=responses[mid];bendunit=rr['peak_bending_y_per_pa']*abs(dp)/m.thickness
                gasunit=np.sqrt(2)*np.maximum(abs(pa),abs(prear))/medium.p0_pa
                clearance=min(geometry['rear_length_m'],geometry['matched_position_from_inner_front_m']-.392)
                travelunit=rr['peak_absolute_y_per_pa']*abs(dp)/clearance
                forceindicator=np.sqrt(2)*np.max(abs(rr['support_force_rms_per_dp']),axis=0)*abs(dp)
            max_split=max(max_split,float(max(abs(out['p_porous_w']-total)/np.maximum(out['p_input_w'],1e-30))))
            for vmax,imax in base['amplifier_scenarios_vrms_irms']:
                limits=np.array([np.full_like(f,vmax),imax/out['i_rms_a'],d.xmax_mm*.001/out['x_peak_m']])
                U=limits.min(axis=0);Ui=np.minimum(vmax,np.minimum(imax/ideal['i_rms_a'],d.xmax_mm*.001/ideal['x_peak_m']))
                for j,freq in enumerate(f):
                    actual_pa=abs(pa[j])*U[j];actual_pb=abs(prear[j])*U[j]
                    bend=bendunit[j]*U[j];gas=gasunit[j]*U[j];travel=travelunit[j]*U[j]
                    cap=min(U[j],cfg['small_bending_w_over_t_limit_assumed']/max(bendunit[j],1e-300),
                            cfg['gas_peak_pressure_fraction_limit_assumed']/max(gasunit[j],1e-300),1/max(travelunit[j],1e-300))
                    # Geometry of a diagnostic rear monopole,not a measured location.
                    distance=1+geometry['inside_depth_m']+2*base['host_wall_thickness_m']
                    ratio=1-vent[j]*np.exp(-s[j]*(distance-1)/medium.c)/distance
                    front_spl=float(out['spl_equivalent_db'][j]+20*np.log10(U[j]))
                    diagnostic=(front_spl-20*np.log10(2)+20*np.log10(abs(ratio))) if abs(ratio)>1e-30 else None
                    key=(cid,mid,n,lining,vd,str(gs_ref),str(gv_ref),float(freq),vmax,imax)
                    rows[key]=dict(configuration_id=cid,regulator_model=mid,module_count_equivalent=n,lining=lining,driver_displacement_l_stress_axis=vd,
                        seal_100l_reference_corner_hz=gs_ref,vent_100l_reference_corner_hz=gv_ref,f_hz=float(freq),amp_v_rms=vmax,amp_i_rms=imax,
                        active_air_l=air*1000,rear_air_l=rear_air,regulator_component_mass_kg=regulator_mass,
                        model_front_spl_rms_2pi_1m_db=front_spl,diagnostic_total_spl_rms_4pi_front1m_db=diagnostic,
                        coincident_exterior_flow_ratio_abs=float(abs(1-vent[j])),
                        delta_envelope_vs_own_rigid_active_db=float(front_spl-ideal['spl_equivalent_db'][j]-20*np.log10(Ui[j])),
                        u_rms_v=float(U[j]),i_rms_a=float(out['i_rms_a'][j]*U[j]),x_peak_mm=float(out['x_peak_m'][j]*U[j]*1000),
                        active_pressure_rms_pa=float(actual_pa),rear_pressure_rms_pa=float(actual_pb),
                        copper_loss_w=float(out['p_copper_w'][j]*U[j]**2),reduced_cavity_port_loss_w=float(out['p_porous_w'][j]*U[j]**2),
                        bending_peak_over_thickness=float(bend),gas_peak_pressure_fraction=float(gas),axial_travel_fraction=float(travel),
                        within_assumed_linear_domain=bool(bend<=cfg['small_bending_w_over_t_limit_assumed'] and gas<=cfg['gas_peak_pressure_fraction_limit_assumed'] and travel<1),
                        diagnostic_domain_voltage_rms_v=float(cap),pressure_support_peak_indicator_n=None if is_module else float(forceindicator[j]*U[j]),
                        support_indicator_kind='not_resolved_for_module' if is_module else ('patch4' if m.kind=='PATCH4' else 'frame_or_perimeter_mean'),
                        active_limit=['voltage','current','catalog_x'][int(np.argmin(limits[:,j]))])
    assert max(max_energy,max_split)<1e-8
    ordered=list(rows.values());table('p20b_naped_i_porownanie_regulatorow.csv',ordered)
    inputs=[CFG,basepath,Path(__file__),ROOT/'skrypty/model_przegrody_P20B.py',ROOT/'skrypty/geometria_przegrody_P20B.py',
        ROOT/'skrypty/model_plyty_MITC_P18.py',ROOT/'skrypty/model_wkladu_P20A.py',ROOT/'skrypty/model_wypelnienia.py',ROOT/'skrypty/model_gazu.py',ROOT/'skrypty/model_subwoofera.py',
        ROOT/'skrypty/analiza_przegrod_P20B.py',ROOT/'skrypty/analiza_rozszerzenia_SB.py',ROOT/'dane/przetworniki/pula_rozszerzona.json',ROOT/'dane/przetworniki/rozszerzenie_SB_20261025.json',ROOT/'brief_system_audio_DIY_v0.6.md']
    result=dict(status='LINEAR_REGULATOR_COMPARISON_WITH_DOMAIN_FLAGS_AND_SEPARATE_VENT_DIAGNOSTICS',date='2026-10-26',point_cases=len(ordered),electrical_configurations=len(lookup),
        checks=dict(max_driver_reduced_power_residual=max_energy,max_split_cavity_power_residual=max_split),
        flagged_domain_rows=sum(not r['within_assumed_linear_domain'] for r in ordered),
        input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        limitations=['Same geometric active gas,not necessarily same amount of lining in thermal layout cases.',
            'Common material beta*K for modules and partition; does not overwrite modal-zeta P20A.',
            'Port volume,hardware,damping and stiffness are hypotheses; no THD or structural strength qualification.',
            'Rear two-source4pi is a diagnostic projection without full exterior radiation feedback or room; not compare directly to2pi front SPL.',
            'Domain voltage is an assumed model screen,not a safe operating rating.',
            'Force indicator for perimeter/frame is a mean equilibrium estimate,not local bolt peak.',
            'Module local self-equilibrated mount forces and cabinet acceleration are not resolved by uniform pressure.'])
    (OUT/'p20b_naped_podsumowanie.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print('P20B drive:',len(ordered),'points;',result['checks'],'domain flags',result['flagged_domain_rows'],flush=True)


if __name__=='__main__':main()
