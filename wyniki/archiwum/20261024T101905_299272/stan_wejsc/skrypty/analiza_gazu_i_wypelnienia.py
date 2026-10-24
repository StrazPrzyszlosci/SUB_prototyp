"""P09/P10: kampania dla24 modeli, porów, relaksacji i termodynamiki gazu."""
import csv
from dataclasses import replace
import json
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/sub-krystian-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import brentq
from model_subwoofera import Driver,P_REF
from model_gazu import Medium,ThermalSpectrum,gas_response,gas_state,conductance_from_reference
from model_wypelnienia import CircularPores,layer_impedance,response_with_acoustic_impedance,fit_thermal_spectrum,sorptive_impedance,two_temperature_modulus
from termodynamika_nieliniowa import periodic_gas,cycle_energy,static_offset

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def table(name,rows):
    with (OUT/name).open('w',newline='',encoding='utf-8') as handle:
        writer=csv.DictWriter(handle,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)


def plot_save(fig,name):
    fig.tight_layout()
    for ext in ['png','svg']:fig.savefig(OUT/f'{name}.{ext}',dpi=170)
    plt.close(fig)


def projected_f3(d,vb,spec,medium,leak):
    """F3 matematycznej projekcji Le=0 względem asymptoty, nie pole2.rzędu."""
    d0=replace(d,le_mh=0.)
    plateau=medium.rho*d.sd*d.bl/(2*np.pi*d.mms*d.re_ohm)
    grid=np.geomspace(.05,2000.,800)
    def residual(f):
        p=abs(gas_response(d0,vb,np.atleast_1d(f),spec,medium,leak)['pressure_equivalent_pa'])
        return (p/plateau)**2-.5
    values=residual(grid)
    brackets=np.flatnonzero(values[:-1]*values[1:]<0)
    roots=[brentq(lambda f:float(residual(f)[0]),grid[j],grid[j+1],xtol=1e-10) for j in brackets]
    upward=[r for r,j in zip(roots,brackets) if values[j]<0]
    return (upward[0] if upward else None),len(roots)


def main():
    cfg=json.loads((ROOT/'dane/konfiguracje/p09_p10_gaz_i_wypelnienie.json').read_text())
    raw=json.loads((ROOT/'dane/przetworniki/pula_rozszerzona.json').read_text())['drivers']
    drivers=[Driver(**r['model']) for r in raw]
    medium=Medium(p0_pa=cfg['p0_pa'],temperature_k=293.15,gamma=cfg['gamma'],gas_constant_j_kg_k=cfg['gas_constant_j_kg_k'],
                  viscosity_pa_s=cfg['viscosity_pa_s_at_reference'],thermal_conductivity_w_m_k=cfg['thermal_conductivity_gas_w_m_k_at_reference'])
    profiles={r['id']:ThermalSpectrum(tuple(np.inf if x=='inf' else x for x in r['times_s']),tuple(r['weights'])) for r in cfg['thermal_profiles']}
    f=np.array(cfg['probe_frequencies_hz'])
    thermal,alignments=[],[]
    max_energy=0.
    for r,d in zip(raw,drivers):
        print('P09 termika i napęd:',r['candidate_id'],flush=True)
        for vb in cfg['volumes_before_filling_l']:
            for leak in cfg['leak_reference_hz']:
                base=gas_response(d,vb,f,profiles['ADIABATIC'],medium,leak)
                for pid,spec in profiles.items():
                    out=gas_response(d,vb,f,spec,medium,leak)
                    max_energy=max(max_energy,float(max(abs(out['energy_residual_w'])/out['p_input_w'])))
                    f3,crossings=projected_f3(d,vb,spec,medium,leak)
                    alignments.append(dict(candidate_id=r['candidate_id'],volume_l=vb,profile=pid,leak_ref_hz=leak,
                                           f3_projected_Le0_first_upward_hz=f3,number_of_3db_crossings=crossings,
                                           scope='PROJEKCJA_WZGLEDEM_ASYMPTOTY_BEZ_Le_NIE_FC_QTC_WIELOPOLOWEGO_MODELU'))
                    for j,freq in enumerate(f):
                        compliance_volume=medium.gamma*medium.p0_pa*vb/out['bulk_modulus_pa'][j]
                        row=dict(candidate_id=r['candidate_id'],driver=d.name,volume_l=vb,profile=pid,
                                 leak_ref_hz=leak,f_hz=freq,bulk_re_pa=float(out['bulk_modulus_pa'][j].real),
                                 bulk_im_pa=float(out['bulk_modulus_pa'][j].imag),
                                 equivalent_compliance_storage_l=float(compliance_volume.real),
                                 equivalent_compliance_loss_l=float(-compliance_volume.imag),
                                 spl_equivalent_1v_db=float(out['spl_equivalent_db'][j]),
                                 delta_to_adiabatic_same_Ra_db=float(out['spl_equivalent_db'][j]-base['spl_equivalent_db'][j]),
                                 x_peak_1v_mm=float(out['x_peak_m'][j]*1000),current_1v_rms_a=float(out['i_rms_a'][j]),
                                 p_inside_1v_rms_pa=float(abs(out['p_inside_pa'][j])),
                                 p_inside_1v_phase_rad=float(np.angle(out['p_inside_pa'][j])),
                                 thermal_loss_1v_w=float(out['p_thermal_w'][j]),leak_loss_1v_w=float(out['p_leak_w'][j]))
                        for vmax,imax in [(40.,12.),(60.,20.)]:
                            for fraction in [.7,1.]:
                                limits=[vmax,imax/out['i_rms_a'][j],fraction*d.xmax_mm*1e-3/out['x_peak_m'][j]]
                                voltage=min(limits)
                                key=f'V{int(vmax)}_X{fraction:g}'
                                row[key+'_spl_db']=float(out['spl_equivalent_db'][j]+20*np.log10(voltage))
                                row[key+'_voltage_rms']=float(voltage)
                                row[key+'_active_limit']=['voltage','current','catalog_x'][int(np.argmin(limits))]
                        thermal.append(row)
    table('p09_relaksacja_i_naped.csv',thermal)
    table('p09_projekcja_F3.csv',alignments)
    # Porównanie modeli porów z przejrzystymi parametrami, bez przypisania produktu.
    material_rows=[];fit_records=[];materials={}
    dense_f=np.geomspace(.01,10000.,600)
    for radius in cfg['porous_radii_m']:
        pores=CircularPores(radius,cfg['porous_reference_porosity'])
        for terms in [1,4,16]:
            spec,error=fit_thermal_spectrum(pores,dense_f,terms,medium)
            fit_records.append(dict(pore_radius_m=radius,terms_requested=terms,
                                    weights=list(spec.weights),times_s=list(spec.times_s),
                                    max_relative_bulk_modulus_error=error,
                                    scope='DOPASOWANIE_DO_ZK_NIE_DO_POMIARU_WLOKNINY'))
    (OUT/'p09_dopasowania_widm.json').write_text(json.dumps(fit_records,ensure_ascii=False,indent=2,allow_nan=False))
    for vb in cfg['volumes_before_filling_l']:
        depth=cfg['porous_depth_total_m'];area=vb*1e-3/depth
        empty_1d=layer_impedance(f,area,[(depth,None)],medium)
        models=[]
        for radius in cfg['porous_radii_m']:
            for frame in cfg['porous_frames']:
                mat=CircularPores(radius,cfg['porous_reference_porosity'],frame,cfg['dry_frame_density_kg_m3_assumed'])
                for filled in cfg['porous_layer_depths_m']:
                    pid=f'ZK_{radius:g}_{frame}_{filled:g}'
                    z=layer_impedance(f,area,[(depth-filled,None),(filled,mat)],medium)
                    gas_volume=(vb*1e-3-area*filled*(1-mat.porosity))*1000
                    models.append((pid,'ZK_'+frame,z,empty_1d,gas_volume,mat.flow_resistivity(medium)))
                    if vb==100:materials[pid]=z
        zempty=1/(2j*np.pi*f*(vb*1e-3/(medium.gamma*medium.p0_pa)))
        for ratio in cfg['two_temperature_capacity_ratios']:
            for t_env in cfg['two_temperature_environment_times_s']:
                env=np.inf if t_env=='inf' else t_env
                z=two_temperature_modulus(f,vb,ratio,.005,env,medium)['bulk_modulus_pa']/(2j*np.pi*f*vb*1e-3)
                models.append((f'2T_CsCg{ratio:g}_env{t_env}','TWO_TEMPERATURE',z,zempty,vb,None))
        sorp=cfg['sorptive_example']
        for tau in sorp['relaxation_times_s_assumed']:
            z=sorptive_impedance(f,vb,sorp['filling_fraction'],sorp['geometric_porosity_assumed'],sorp['apparent_porosity_from_venegas2023_example'],tau,medium)
            gas_volume=vb*(1-sorp['filling_fraction']*(1-sorp['geometric_porosity_assumed']))
            models.append((f'ADSORPTION_T{tau:g}','SORPTIVE_ASSUMED',z,zempty,gas_volume,None))
        for r,d in zip(raw,drivers):
            base_1d=response_with_acoustic_impedance(d,f,empty_1d,medium=medium)
            base_lumped=response_with_acoustic_impedance(d,f,zempty,medium=medium)
            for pid,kind,z,_,gas_volume,resistivity in models:
                out=response_with_acoustic_impedance(d,f,z,medium=medium)
                ref=base_1d if kind.startswith('ZK') else base_lumped
                max_energy=max(max_energy,float(max(abs(out['energy_residual_w'])/out['p_input_w'])))
                equiv=medium.gamma*medium.p0_pa/(2j*np.pi*f*z)*1000
                for j,freq in enumerate(f):
                    material_rows.append(dict(candidate_id=r['candidate_id'],volume_before_fill_l=vb,
                                              gas_volume_after_solid_displacement_l=gas_volume,
                                              model_id=pid,model_class=kind,f_hz=freq,
                                              flow_resistivity_pa_s_m2=resistivity,
                                              reference='EMPTY_1D' if kind.startswith('ZK') else 'EMPTY_LUMPED',
                                              acoustic_impedance_re=float(z[j].real),acoustic_impedance_im=float(z[j].imag),
                                              equivalent_storage_l=float(equiv[j].real),equivalent_loss_l=float(-equiv[j].imag),
                                              delta_same_voltage_db=float(out['spl_equivalent_db'][j]-ref['spl_equivalent_db'][j]),
                                              x_ratio_same_voltage=float(out['x_peak_m'][j]/ref['x_peak_m'][j]),
                                              current_ratio_same_voltage=float(out['i_rms_a'][j]/ref['i_rms_a'][j]),
                                              p_inside_1v_rms_pa=float(abs(out['p_inside_pa'][j])),
                                              internal_loss_1v_w=float(out['p_porous_w'][j]),
                                              geometry_scope='PORT_USREDNIONY_1D_NIE_WERYFIKACJA_MONTAZU_GLOSNIKA'))
    table('p09_modele_wypelnienia.csv',material_rows)
    # Bezwymiarowa nieliniowa termodynamika: nowe końce tau, nie powtórka gamma=1.4 bez ciepła.
    nonlinear=[];max_fft=0.
    dimensionless_cases=[(a,'finite') for a in cfg['nonlinear_omega_tau_grid']]
    dimensionless_cases += [(np.inf,'initial_entropy'),(np.inf,'periodic_limit')]
    for epsilon in cfg['nonlinear_epsilon_grid']:
        for a,mode in dimensionless_cases:
            datum=periodic_gas(epsilon,a,4096,medium,mode if np.isposinf(a) else 'initial_entropy')
            refined=periodic_gas(epsilon,a,8192,medium,mode if np.isposinf(a) else 'initial_entropy')
            max_fft=max(max_fft,abs(datum['h2_to_h1_pct']-refined['h2_to_h1_pct']),abs(datum['h3_to_h1_pct']-refined['h3_to_h1_pct']))
            nonlinear.append(dict(epsilon=epsilon,omega_tau=a,adiabatic_mode=mode,
                                  **{k:v for k,v in datum.items() if not isinstance(v,np.ndarray)}))
    table('p10_gaz_bezwymiarowy.csv',nonlinear)
    gas_rows=[]
    for r,d in zip(raw,drivers):
        print('P10 amplituda/temperatura:',r['candidate_id'],flush=True)
        for vb in cfg['volumes_before_filling_l']:
            for fraction in cfg['nonlinear_driver_x_fractions']:
                epsilon=d.sd*d.xmax_mm*1e-3*fraction/(vb*1e-3)
                endpoint_iso=periodic_gas(epsilon,0.,2048,medium)
                endpoint_ad=periodic_gas(epsilon,np.inf,2048,medium)
                for temp in cfg['ambient_temperature_k']:
                    # Ten sam założony H co przy100l/293.15K, nie ten sam czas tau.
                    tau=cfg['nonlinear_reference_tau_s']*(vb/100)*(medium.temperature_k/temp)
                    for freq in f:
                        finite=periodic_gas(epsilon,2*np.pi*freq*tau,2048,medium)
                        for pid,datum in [('ISOTHERMAL',endpoint_iso),('NEWTON_H_FIXED',finite),('ADIABATIC_INITIAL_ENTROPY',endpoint_ad)]:
                            gas_rows.append(dict(candidate_id=r['candidate_id'],volume_l=vb,
                                                 x_fraction_of_catalog=fraction,epsilon=epsilon,f_hz=freq,
                                                 initial_ambient_temperature_k=temp,model=pid,
                                                 tau_s=tau if pid=='NEWTON_H_FIXED' else None,
                                                 gas_pressure_h2_pct=datum['h2_to_h1_pct'],gas_pressure_h3_pct=datum['h3_to_h1_pct'],
                                                 gas_pressure_thd_h2_h10_pct=datum['thd_pressure_h2_h10_pct'],
                                                 gas_force_fundamental_peak_n=d.sd*datum['fundamental_peak_pa'],
                                                 gas_force_dc_on_diaphragm_n=d.sd*datum['pressure_dc_relative_pa'],
                                                 pressure_max_above_ambient_pa=datum['pressure_max_pa']-medium.p0_pa,
                                                 pressure_min_above_ambient_pa=datum['pressure_min_pa']-medium.p0_pa,
                                                 gas_temperature_mean_k=datum['temperature_mean_k']*temp/medium.temperature_k,
                                                 gas_temperature_max_k=datum['temperature_max_k']*temp/medium.temperature_k,
                                                 gas_temperature_min_k=datum['temperature_min_k']*temp/medium.temperature_k,
                                                 scope='ZADANY_RUCH_NIE_THD_AKUSTYCZNE_GLOSNIKA'))
    table('p10_gaz_dla_przetwornikow.csv',gas_rows)
    energy_rows=[]
    for epsilon in cfg['nonlinear_epsilon_grid']:
        for freq in [20.,80.]:
            for tau in [.0005,.005,.05]:
                energy_rows.append(dict(epsilon=epsilon,f_hz=freq,volume_l=100.,tau_s=tau,
                                       **cycle_energy(epsilon,freq,100.,tau,medium)))
    table('p10_bilans_energii.csv',energy_rows)
    static=[];slow=[]
    for r,d in zip(raw,drivers):
        for vb in cfg['volumes_before_filling_l']:
            for dt in cfg['static_temperature_shifts_k']:
                for dp in cfg['static_external_pressure_shifts_pa']:
                    out=static_offset(d,vb,medium.temperature_k+dt,medium.p0_pa+dp,medium)
                    static.append(dict(candidate_id=r['candidate_id'],volume_l=vb,ambient_delta_k=dt,
                                       external_delta_pa=dp,**out,
                                       beyond_catalog_motion=out['fraction_of_catalog_xmax']>1,
                                       scope='HERMETYCZNA_MASA_LINIOWE_ZAWIESZENIE_NIE_PROGNOZA_PO_ZDERZENIU'))
            lo,hi,points=cfg['dc_audio_probe_grid_hz']
            audio_f=np.linspace(lo,hi,int(points))
            audio_base=gas_response(d,vb,audio_f,profiles['T005'],medium)
            for fl in cfg['dc_reference_leak_hz']:
                g=conductance_from_reference(fl,medium)
                predicted=(vb*1e-3/medium.p0_pa+d.sd*d.sd*d.cms)/g
                a,_,_,_=gas_state(d,vb,profiles['T005'],medium,fl)
                actual=-1/max(np.linalg.eigvals(a).real)
                audio=gas_response(d,vb,audio_f,profiles['T005'],medium,fl)
                delta=audio['spl_equivalent_db']-audio_base['spl_equivalent_db']
                slow.append(dict(candidate_id=r['candidate_id'],volume_l=vb,leak_ref_hz=fl,
                                 quasistatic_isothermal_tau_s=predicted,slowest_state_pole_tau_s=actual,
                                 relative_difference=actual/predicted-1,
                                 max_abs_audio_delta_20_80_db=float(max(abs(delta))),
                                 min_audio_delta_20_80_db=float(min(delta)),max_audio_delta_20_80_db=float(max(delta)),
                                 scope='TAU_DC_UWZGLEDNIA_CMS_NIE_SAMO_Ra_Cab'))
    table('p10_offset_cieplny_i_barometryczny.csv',static)
    table('p10_wyrownanie_DC.csv',slow)
    # Wykresy zawsze opisują model i wskazane jednostki.
    fplot=np.geomspace(1,1000,700)
    fig,axes=plt.subplots(2,2,figsize=(12,8))
    for pid in ['ADIABATIC','ISOTHERMAL','T0005','T005','T05','MIX3']:
        k=profiles[pid].bulk_modulus(fplot,medium)
        axes[0,0].semilogx(fplot,k.real/medium.p0_pa,label=pid)
        axes[0,1].semilogx(fplot,k.imag/medium.p0_pa,label=pid)
    d=drivers[next(i for i,r in enumerate(raw) if r['candidate_id']=='C02')]
    base=gas_response(d,100,fplot,profiles['ADIABATIC'],medium)
    for pid in ['ISOTHERMAL','T0005','T005','T05','MIX3']:
        out=gas_response(d,100,fplot,profiles[pid],medium)
        axes[1,0].semilogx(fplot,out['spl_equivalent_db']-base['spl_equivalent_db'],label=pid)
        axes[1,1].semilogx(fplot,out['p_thermal_w']/out['p_input_w'],label=pid)
    axes[0,0].set(ylabel='Re(K) / p0',title='Sztywność gazu i częstotliwość')
    axes[0,1].set(ylabel='Im(K) / p0',title='Cieplna część stratna')
    axes[1,0].set(ylabel='Zmiana przy tym samym V [dB]',title='C02, 100 l, szczelna; względem adiabatycznej')
    axes[1,1].set(ylabel='P_ciepło / P_wejście',title='Strata cieplna gazu, model liniowy')
    for ax in axes.flat:ax.set(xlabel='Hz');ax.grid(alpha=.25);ax.legend(fontsize=7)
    plot_save(fig,'13_relaksacja_cieplna_gazu')
    fig,axes=plt.subplots(1,2,figsize=(13,5))
    fill_f=np.geomspace(1.,120.,600)
    area=.2;z0=layer_impedance(fill_f,area,[(.5,None)],medium)
    for frame in ['rigid','limp']:
        mat=CircularPores(.0002,.98,frame,20.)
        for filled in [.1,.5]:
            z=layer_impedance(fill_f,area,[(.5-filled,None),(filled,mat)],medium)
            equiv=medium.gamma*medium.p0_pa/(2j*np.pi*fill_f*z)*1000
            axes[0].semilogx(fill_f,equiv.real,label=f'{frame}, warstwa {filled:g} m')
            response_case=response_with_acoustic_impedance(d,fill_f,z,medium=medium)
            base_case=response_with_acoustic_impedance(d,fill_f,z0,medium=medium)
            axes[1].semilogx(fill_f,response_case['spl_equivalent_db']-base_case['spl_equivalent_db'],label=f'{frame}, {filled:g} m')
    axes[0].set(ylabel='Re(V równoważnego) [l]',title='100 l przed wypełnieniem; model 1D')
    axes[1].set(ylabel='Zmiana przy tym samym V [dB]',title='C02, 100 l; względem pustej komory 1D')
    for ax in axes:ax.set(xlabel='Hz',xlim=(1,120));ax.grid(alpha=.25);ax.legend(fontsize=8)
    plot_save(fig,'14_pory_i_mocowanie_wypelnienia')
    fig,axes=plt.subplots(1,2,figsize=(12,5))
    for a in [0.,.1,1.,10.,np.inf]:
        selected=[r for r in nonlinear if r['omega_tau']==a and r['adiabatic_mode']!='periodic_limit']
        axes[0].loglog([r['epsilon'] for r in selected],[r['h2_to_h1_pct'] for r in selected],label=f'ωτ={a:g}')
    epsilon=.2
    for mode in ['initial_entropy','periodic_limit']:
        datum=periodic_gas(epsilon,np.inf,4096,medium,mode)
        axes[1].plot(datum['phase']/(2*np.pi),datum['pressure_pa']-medium.p0_pa,label=mode)
    axes[0].set(xlabel='ε = Sd X / V',ylabel='H2/H1 ciśnienia wewnątrz [%]',title='Zadany ruch; nie THD na zewnątrz')
    axes[1].set(xlabel='Okres',ylabel='p − p0 [Pa]',title='H→0 i stan okresowy: różne granice, ε=0,2')
    for ax in axes:ax.grid(alpha=.25);ax.legend(fontsize=8)
    plot_save(fig,'15_nieliniowy_gaz_i_granice')
    fig,axes=plt.subplots(1,2,figsize=(12,5))
    for cid in ['C02','C06','C11']:
        rows=[r for r in static if r['candidate_id']==cid and r['volume_l']==100 and r['external_delta_pa']==0]
        axes[0].plot([r['ambient_delta_k'] for r in rows],[r['x_bias_m']*1000 for r in rows],'o-',label=cid)
        rows=[r for r in slow if r['candidate_id']==cid and r['volume_l']==100]
        axes[1].loglog([r['leak_ref_hz'] for r in rows],[r['slowest_state_pole_tau_s'] for r in rows],'o-',label=cid)
    axes[0].set(xlabel='Zmiana temperatury [K]',ylabel='Offset membrany [mm]',title='Hermetyczna masa 100 l, liniowe Cms; scenariusz')
    axes[1].set(xlabel='fleak przy 100 l [Hz]',ylabel='Najwolniejszy czas stanu [s]',title='Wyrównanie DC uwzględnia podatność zawieszenia')
    for ax in axes:ax.grid(alpha=.25);ax.legend()
    plot_save(fig,'16_hermetycznosc_i_wyrownanie_DC')
    result=dict(status='RODZINY_P09_P10_BEZ_IDENTYFIKACJI_MATERIALU',drivers=len(drivers),
                thermal_band_rows=len(thermal),projected_f3_cases=len(alignments),material_rows=len(material_rows),
                nonlinear_dimensionless_cases=len(nonlinear),nonlinear_driver_rows=len(gas_rows),
                static_offset_rows=len(static),dc_relaxation_rows=len(slow),energy_cycle_cases=len(energy_rows),
                max_relative_linear_energy_residual=max_energy,
                max_fft_harmonic_difference_pct=max_fft,
                medium=dict(vars(medium),rho_kg_m3=medium.rho,c_m_s=medium.c),
                limits=['Pełna nieliniowa dynamika silnika/zawieszenia pozostaje P12/P13.',
                        'Pory ZK i rezerwuar cieplny nie są zidentyfikowanym produktem.',
                        'Porowatość pozorna sorpcji nie jest geometryczną porowatością.',
                        'Masy powietrza w modelu1D wymagają uzgodnienia Mmd/Mms z P11.',
                        'Geometria portu1D nie potwierdza montażu głośnika ani miejsca w pokoju.'])
    (OUT/'p09_p10_podsumowanie.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return result


if __name__=='__main__':main()
