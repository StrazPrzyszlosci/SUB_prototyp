"""Wkłady jako dodatkowe porty gaz/ściany/przeciek, porównanie27konfiguracji.

Napięcie/prąd RMS, ruch peak, osobne sinusy ustalone, monopol2pi/1m.
Brak THD, temperatur cewek, room gain, ciągłego bezpiecznego czasu pracy.
"""
from pathlib import Path
from itertools import product
import hashlib,json
import numpy as np
from analiza_rozszerzenia_SB import candidates
from analiza_wkladow_P20A import table
from model_gazu import Medium,ThermalSpectrum,gas_response
from model_wypelnienia import CircularPores,response_with_acoustic_impedance
from model_wkladu_P20A import HollowModule
from geometria_wkladow_P20A import obstacles,liner_envelope_volume,packing

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki';CFG=ROOT/'dane/konfiguracje/p20a_regulacja_objetosci.json'


def main():
    cfg=json.loads(CFG.read_text());medium=Medium();f=np.array(cfg['probe_frequencies_hz']);s=2j*np.pi*f
    outer=tuple(cfg['selected_comparison_outer_width_length_height_m']);volume=float(np.prod(outer))
    nominal=packing(cfg,outer,.3052,1);assert nominal['accepted_modules']==16
    hard=obstacles(cfg,1);fixed=sum(b.volume for b in hard);Vhost=float(np.prod(cfg['inside_width_depth_height_m']))
    Vlining=liner_envelope_volume(cfg,hard);phi=cfg['lining_geometric_porosity_assumed']
    mat=CircularPores(cfg['lining_pore_radius_m_assumed'],phi,'rigid',cfg['lining_dry_density_kg_m3_assumed'])
    _,Bporous=mat.equivalent_properties(f,medium)
    modules={
        'H8_SSSS':HollowModule(outer,.008,'SSSS',cfg),
        'H8_CCCC':HollowModule(outer,.008,'CCCC',cfg),
        'H8_CCCC_TIE':HollowModule(outer,.008,'CCCC',cfg,braced=True),
        'H10_CCCC_TIE':HollowModule(outer,.010,'CCCC',cfg,braced=True),
        'H12_CCCC_TIE':HollowModule(outer,.012,'CCCC',cfg,braced=True)}
    lookup={cid:d for cid,pid,d,cat in candidates()};all_ids=list(lookup)
    selected=['C01','C02','C04','C25','C26P','C26S']
    lining_cases=['AIR_ONLY','LINER_GEOMETRY','LINER_THERMAL_ZK']
    scenarios=[]
    for vd,n,lining in product(cfg['driver_displacement_l_stress_cases'],[0,8,16],lining_cases):
        scenarios.append(('H8_CCCC_TIE',1.4,0.,vd,n,lining,all_ids))
    leaks=[np.inf if x=='inf' else x for x in cfg['module_leak_rigid_gas_corner_hz']]
    for name,kappa,leak,n,lining in product(modules,cfg['internal_gas_kappa_cases'],leaks,[8,16],lining_cases):
        scenarios.append((name,kappa,leak,4.,n,lining,selected))
    for vd,n,lining in product(cfg['driver_displacement_l_stress_cases'],[8,16],lining_cases):
        scenarios.append(('SOLID_MDF',1.4,0.,vd,n,lining,all_ids))
    rows={};max_energy=max_port=max_legacy=0.
    for name,kappa,leak,vd,n,lining,ids in scenarios:
        Vbefore=Vhost-fixed-vd*.001-n*volume;assert Vbefore>Vlining>0
        if lining=='AIR_ONLY':Cmain=np.full_like(s,Vbefore/(medium.gamma*medium.p0_pa));Vair=Vbefore
        elif lining=='LINER_GEOMETRY':
            Vair=Vbefore-(1-phi)*Vlining;Cmain=np.full_like(s,Vair/(medium.gamma*medium.p0_pa))
        else:
            Vair=Vbefore-(1-phi)*Vlining;Cmain=(Vbefore-Vlining)/(medium.gamma*medium.p0_pa)+Vlining/Bporous
        if n==0:
            actual_name='NONE';moduleY=np.zeros_like(s);kout=None;lout='n/a'
        elif name=='SOLID_MDF':
            actual_name=name;bulk=cfg['mdf_E_pa_assumed']/(3*(1-2*cfg['mdf_nu_assumed']))
            moduleY=s*volume/bulk;kout=None;lout='n/a'
        else:
            actual_name=name;moduleY=modules[name].port(f,kappa,leak,medium)['admittance'];kout=kappa;lout='inf' if np.isposinf(leak) else leak
        Y=s*Cmain+n*moduleY;Z=1/Y;Zideal=1/(s*Cmain)
        equivalent=medium.gamma*medium.p0_pa*Y/s*1000
        assert np.all(Y.real>=-1e-12)
        for cid in ids:
            d=lookup[cid];one=response_with_acoustic_impedance(d,f,Z,medium=medium)
            ideal=response_with_acoustic_impedance(d,f,Zideal,medium=medium)
            max_energy=max(max_energy,float(max(abs(one['energy_residual_w'])/one['p_input_w'])))
            p2=abs(one['p_inside_pa'])**2
            split_loss=p2*(np.real(s*Cmain)+n*np.real(moduleY))
            max_port=max(max_port,float(max(abs(one['p_porous_w']-split_loss)/np.maximum(one['p_input_w'],1e-30))))
            if n==0 and lining in ['AIR_ONLY','LINER_GEOMETRY']:
                ref=gas_response(d,Vair*1000,f,ThermalSpectrum((np.inf,),(1.,)),medium)
                max_legacy=max(max_legacy,float(max(abs(one['current_complex_a']/ref['current_complex_a']-1))))
            for vmax,imax in cfg['amplifier_scenarios_vrms_irms']:
                voltage=np.minimum(vmax,np.minimum(imax/one['i_rms_a'],d.xmax_mm*.001/one['x_peak_m']))
                vi=np.minimum(vmax,np.minimum(imax/ideal['i_rms_a'],d.xmax_mm*.001/ideal['x_peak_m']))
                for j,freq in enumerate(f):
                    key=(cid,actual_name,kout,lout,vd,n,lining,vmax,imax,float(freq))
                    limits=[vmax,imax/one['i_rms_a'][j],d.xmax_mm*.001/one['x_peak_m'][j]]
                    rows[key]=dict(configuration_id=cid,module_variant=actual_name,module_count=n,inner_kappa_assumed=kout,
                        leak_rigid_gas_corner_hz=lout,driver_displacement_l_stress_axis=vd,lining=lining,f_hz=float(freq),
                        amp_v_rms=vmax,amp_i_rms=imax,main_accessible_air_l=Vair*1000,
                        dynamic_equivalent_compliance_storage_l=float(equivalent[j].real),
                        dynamic_equivalent_compliance_loss_l=float(-equivalent[j].imag),
                        spl_rms_2pi_1m_db=float(one['spl_equivalent_db'][j]+20*np.log10(voltage[j])),
                        delta_same_voltage_vs_ideal_rigid_db=float(one['spl_equivalent_db'][j]-ideal['spl_equivalent_db'][j]),
                        delta_limited_vs_ideal_rigid_db=float(one['spl_equivalent_db'][j]+20*np.log10(voltage[j])-ideal['spl_equivalent_db'][j]-20*np.log10(vi[j])),
                        u_rms_v=float(voltage[j]),i_rms_a=float(one['i_rms_a'][j]*voltage[j]),x_peak_mm=float(one['x_peak_m'][j]*voltage[j]*1000),
                        cavity_pressure_rms_pa=float(abs(one['p_inside_pa'][j])*voltage[j]),
                        copper_w=float(one['p_copper_w'][j]*voltage[j]**2),cavity_port_loss_w=float(one['p_porous_w'][j]*voltage[j]**2),
                        active_limit=['voltage','current','catalog_x'][int(np.argmin(limits))])
    assert max(max_energy,max_port,max_legacy)<1e-10
    ordered=list(rows.values());table('p20a_naped_objetosc_i_wklady.csv',ordered)
    inputs=[CFG,Path(__file__),ROOT/'skrypty/model_wkladu_P20A.py',ROOT/'skrypty/geometria_wkladow_P20A.py',
        ROOT/'skrypty/model_plyty_MITC_P18.py',ROOT/'skrypty/model_wypelnienia.py',ROOT/'skrypty/model_gazu.py',ROOT/'skrypty/model_subwoofera.py',
        ROOT/'skrypty/analiza_rozszerzenia_SB.py',ROOT/'dane/przetworniki/pula_rozszerzona.json',ROOT/'dane/przetworniki/rozszerzenie_SB_20261025.json',ROOT/'brief_system_audio_DIY_v0.6.md']
    result=dict(status='CONDITIONAL_LINEAR_SYSTEM_WITH_INSERT_COMPLIANCE_NOT_DUT_THD_OR_THERMAL_RATING',date='2026-10-26',
        point_cases=len(ordered),electrical_configurations=len(lookup),physical_products=26,full_count=nominal['accepted_modules'],
        selected_outer_m=outer,unknown_driver_displacement_axis_l=cfg['driver_displacement_l_stress_cases'],
        checks=dict(max_electromechanical_power_residual=max_energy,max_cavity_loss_split_residual=max_port,empty_reference_relative_error=max_legacy),
        input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        limitations=['T/S frozen; no identified THD, thermal compression, amplifier dynamics or room.',
            'Driver displacement 2/4/6l are arbitrary stress cases, not estimates or manufacturer tolerances.',
            'Ideal rigid comparison uses the same geometric volume; hollow/solid module compliance counted separately.',
            'Liner model uses geometric pore loss/thermal compliance only; not spatial flow or identified product.',
            'Internal gas endpoints and leak g=2pi*fc*Ci are prescribed families; same fc at changed Ci does not mean same physical crack.',
            'Sinusoidal steady state; no declared permissible duration. Xcatalog is not a THD criterion.'])
    (OUT/'p20a_naped_podsumowanie.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print('P20A drive:',len(ordered),'points;',result['checks'],flush=True)


if __name__=='__main__':main()
