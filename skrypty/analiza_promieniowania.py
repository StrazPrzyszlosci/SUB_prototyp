"""P11: wszystkie24modele, konwencje masy, baffle i kontrolna skończona bryła."""
import csv
from dataclasses import replace
import json,os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/sub-krystian-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from model_subwoofera import Driver,P_REF
from model_gazu import Medium,ThermalSpectrum
from model_promieniowania import (piston_impedance,piston_added_mass_static,piston_on_axis_pressure,
    spherical_cap_impedance,spherical_cap_field,spherical_cavity_impedance,spherical_cap_added_mass_static)
from naped_z_promieniowaniem import Motor,reference_calibration,solve_motor_ports,common_drive_envelope

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def table(name,rows):
    with (OUT/name).open('w',newline='',encoding='utf-8') as handle:
        w=csv.DictWriter(handle,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def save(fig,name):
    fig.tight_layout()
    for ext in ['png','svg']:fig.savefig(OUT/f'{name}.{ext}',dpi=170)
    plt.close(fig)


def main():
    cfg=json.loads((ROOT/'dane/konfiguracje/p11_promieniowanie.json').read_text())
    raw=json.loads((ROOT/'dane/przetworniki/pula_rozszerzona.json').read_text())['drivers']
    medium=Medium();f=np.array(cfg['frequencies_hz']);s=2j*np.pi*f
    profiles={'ADIABATIC':ThermalSpectrum((np.inf,),(1.,)),'THERMAL_5MS':ThermalSpectrum((.005,),(1.,))}
    calibration_rows=[];rows=[];reference_rows=[];max_power=0.
    for entry in raw:
        d=Driver(**entry['model']);cid=entry['candidate_id'];print('P11 port:',cid,flush=True)
        calibrations={}
        for faces in cfg['reference_faces']:
            try:
                motor,cal=reference_calibration(d,faces,medium=medium)
                calibrations[faces]=motor
                calibration_rows.append(dict(candidate_id=cid,driver=d.name,**cal,
                                             valid=True,catalogue_mms_derived_kg=d.mms,catalogue_rms_derived=d.rms))
            except ValueError as exc:
                raise RuntimeError(f'Nieobsłużona kalibracja {cid}: {exc}') from exc
        zp=piston_impedance(f,d.sd,medium)
        for vb in cfg['volumes_l']:
            inside_radius=(3*vb*1e-3/(4*np.pi))**(1/3)
            outside_radius=inside_radius+cfg['sphere_shell_offset_m_assumed']
            zcap=spherical_cap_impedance(f,d.sd,outside_radius,cfg['sphere_radial_terms'],medium)
            pcap={distance:spherical_cap_field(f,d.sd,outside_radius,outside_radius+distance,[1.],cfg['sphere_radial_terms'],medium)[0][:,0]
                  for distance in cfg['observation_distances_from_front_m']}
            ppiston={distance:piston_on_axis_pressure(f,d.sd,distance,medium) for distance in cfg['observation_distances_from_front_m']}
            for profile in cfg['profiles']:
                bulk=profiles[profile].bulk_modulus(f,medium)
                zlumped=d.sd**2*bulk/(s*vb*1e-3)
                zcavity=spherical_cavity_impedance(f,d.sd,vb*1e-3,cfg['sphere_radial_terms'],medium,bulk)
                # Historyczny model Mms bez dodawania reakcji frontu: tylko odniesienie.
                legacy=Motor(d.mms,d.cms,d.rms,d.bl,d.re_ohm,d.le_mh*1e-3,d.sd,d.xmax_mm*1e-3)
                reference=solve_motor_ports(f,[legacy],zlumped[:,None],np.zeros((len(f),1,1),complex),[1.])
                reference_pressure=medium.rho*s*d.sd*reference['velocity'][:,0]/(2*np.pi)
                for j,frequency in enumerate(f):
                    reference_rows.append(dict(candidate_id=cid,volume_l=vb,profile=profile,f_hz=frequency,
                                               equivalent_2pi_1m_1v_db=float(20*np.log10(abs(reference_pressure[j])/P_REF)),
                                               equivalent_4pi_1m_1v_db=float(20*np.log10(abs(reference_pressure[j])/2/P_REF)),
                                               scope='NORMALIZACJE_ODNIESIENIA_NIE_DWA_ROZWIAZANIA_RZECZYWISTEJ_GEOMETRII'))
                geometries=[('INFINITE_BAFFLE_LUMPED',zp,zlumped,ppiston),
                            ('FINITE_SPHERE_LUMPED',zcap,zlumped,pcap),
                            ('FINITE_SPHERE_CAVITY',zcap,zcavity,pcap)]
                for geometry,front,rear,pressure_operator in geometries:
                    for faces,motor in calibrations.items():
                        out=solve_motor_ports(f,[motor],rear[:,None],front[:,None,None],[1.])
                        max_power=max(max_power,float(max(abs(out['energy_residual_w'])/out['input_w'])))
                        for j,frequency in enumerate(f):
                            p=pressure_operator[1.][j]*out['velocity'][j,0]
                            pfar=pressure_operator[2.75][j]*out['velocity'][j,0]
                            row=dict(candidate_id=cid,driver=d.name,volume_l=vb,profile=profile,
                                     geometry=geometry,reference_faces=faces,
                                     calibration_role='DOUBLE_COUNT_CONTROL' if faces==0 else 'REFERENCE_CONVENTION_HYPOTHESIS',
                                     f_hz=frequency,ka=float(2*np.pi*frequency*np.sqrt(d.sd/np.pi)/medium.c),
                                     front_added_mass_at_f_kg=float(front[j].imag/(2*np.pi*frequency)),
                                     front_resistance=float(front[j].real),rear_re=float(rear[j].real),rear_im=float(rear[j].imag),
                                     spl_1m_from_front_1v_rms_db=float(20*np.log10(abs(p)/P_REF)),
                                     spl_2_75m_from_front_1v_rms_db=float(20*np.log10(abs(pfar)/P_REF)),
                                     delta_to_old_2pi_model_db=float(20*np.log10(abs(p/reference_pressure[j]))),
                                     current_1v_rms_a=float(abs(out['current'][j,0])),
                                     x_peak_1v_mm=float(out['x_peak_m'][j,0]*1000),
                                     radiated_power_1v_w=float(out['radiation_w'][j]),
                                     copper_power_1v_w=float(out['copper_w'][j]),
                                     scope='MODEL_GEOMETRII_WZORCOWEJ_NIE_POMIAR_GLOSNIKA')
                            for vmax,imax in cfg['amplifier_scenarios']:
                                for fraction in cfg['x_fractions']:
                                    scale,limit=common_drive_envelope(out,[motor],vmax,imax,fraction)
                                    prefix=f'V{vmax:g}_X{fraction:g}'
                                    row[prefix+'_spl_1m_rms_db']=float(20*np.log10(abs(p)*scale[j]/P_REF))
                                    row[prefix+'_voltage_rms']=float(scale[j])
                                    row[prefix+'_limit']=['voltage','current','catalog_x'][int(limit[j])]
                            rows.append(row)
    table('p11_kalibracje_masy.csv',calibration_rows)
    table('p11_geometrie_i_naped.csv',rows)
    table('p11_normalizacje_odniesienia.csv',reference_rows)
    pilot=cfg['mass_pilot'];d=Driver(**next(e for e in raw if e['candidate_id']==pilot['candidate_id'])['model'])
    ma=piston_added_mass_static(d.sd,medium)
    pilot_result=dict(source_mms_g=pilot['manufacturer_mms_g'],source_mmd_g=pilot['manufacturer_mmd_g'],
                      source_difference_g=pilot['manufacturer_mms_g']-pilot['manufacturer_mmd_g'],
                      two_face_static_piston_air_g=2*ma*1000,
                      implied_density_if_two_face_static_formula=medium.rho*(pilot['manufacturer_mms_g']-pilot['manufacturer_mmd_g'])/(2*ma*1000),
                      internally_consistent_primitive_mms_g=d.mms*1000,
                      scope='ZGODNOSC_RZEDU_WIELKOSCI_NIE_DOWOD_PROTOKOLU_POMIAROWEGO_PRODUCENTA')
    # Odrębny zestaw katalogowy z podanym Mmd, nie mieszanie go z wyprowadzonymi T/S.
    pubmotor=Motor(pilot['manufacturer_mmd_g']*.001,pilot['manufacturer_cms_m_n'],
                   pilot['manufacturer_rms_n_s_m']-2*piston_impedance([d.fs_hz],d.sd,medium)[0].real,
                   pilot['manufacturer_bl_tm'],d.re_ohm,d.le_mh*1e-3,d.sd,d.xmax_mm*1e-3)
    pilot_rows=[]
    for vb in cfg['volumes_l']:
        b=(3*vb*.001/(4*np.pi))**(1/3)+cfg['sphere_shell_offset_m_assumed']
        front=spherical_cap_impedance(f,d.sd,b,512,medium)
        rear=spherical_cavity_impedance(f,d.sd,vb*.001,512,medium)
        out=solve_motor_ports(f,[pubmotor],rear[:,None],front[:,None,None],[1.])
        p=spherical_cap_field(f,d.sd,b,b+1,[1.],512,medium)[0][:,0]*out['velocity'][:,0]
        for j,frequency in enumerate(f):pilot_rows.append(dict(candidate_id='C15',volume_l=vb,f_hz=frequency,
            source='PUBLISHED_MMD_CMS_BL_RMS_SET',spl_1m_rms_1v_db=float(20*np.log10(abs(p[j])/P_REF)),
            x_peak_1v_mm=float(out['x_peak_m'][j,0]*1000),current_1v_rms_a=float(abs(out['current'][j,0]))))
    table('p11_pilot_Mmd_producenta.csv',pilot_rows)
    # Geometria i granice, oddzielone od rankingu kandydatów.
    freq=np.geomspace(1.,10000.,700);area=.0841;a=np.sqrt(area/np.pi)
    zp=piston_impedance(freq,area,medium);zs=spherical_cap_impedance(freq,area,.3,512,medium)
    fig,ax=plt.subplots(1,2,figsize=(12,5))
    ax[0].loglog(freq,zp.real,label='Płaska nieskończona odgroda')
    ax[0].loglog(freq,zs.real,label='Czasza na skończonej sferze R=0,3m')
    ax[0].set(xlabel='Hz',ylabel='Re(Z), N s/m',title='Opór promieniowania, Sd=841cm²')
    ax[1].semilogx(freq,zp.imag/(2*np.pi*freq)*1000,label='Odgroda nieskończona')
    ax[1].semilogx(freq,zs.imag/(2*np.pi*freq)*1000,label='Sfera kontrolna')
    ax[1].set(xlabel='Hz',ylabel='Im(Z)/omega [g]',title='Masa akustyczna zależy od geometrii i f')
    for aa in ax:aa.grid(alpha=.25);aa.legend(fontsize=8)
    save(fig,'17_promieniowanie_i_masa_powietrza')
    fig,ax=plt.subplots(1,2,figsize=(12,5));freq=np.geomspace(10.,120.,500)
    for b in [.2,.3,.4]:
        p=spherical_cap_field(freq,area,b,b+1,[1.],512,medium)[0][:,0]
        monopole=medium.rho*2j*np.pi*freq*area/(4*np.pi)
        ax[0].semilogx(freq,20*np.log10(abs(p/monopole)),label=f'Sfera R={b:g}m, 1m od frontu')
    p=piston_on_axis_pressure(freq,area,1.,medium)
    ax[0].semilogx(freq,20*np.log10(abs(p/(medium.rho*2j*np.pi*freq*area/(4*np.pi)))),label='Nieskończona odgroda, 1m')
    ax[0].set(xlabel='Hz',ylabel='Zmiana względem monopola4π [dB]',title='Ten sam przepływ; różne geometrie wzorcowe')
    chosen=[r for r in rows if r['candidate_id']=='C02' and r['volume_l']==100 and r['profile']=='ADIABATIC' and r['reference_faces']==2]
    for geometry in ['INFINITE_BAFFLE_LUMPED','FINITE_SPHERE_LUMPED','FINITE_SPHERE_CAVITY']:
        sub=[r for r in chosen if r['geometry']==geometry]
        ax[1].plot([r['f_hz'] for r in sub],[r['spl_1m_from_front_1v_rms_db'] for r in sub],'o-',label=geometry)
    ax[1].set(xlabel='Hz',ylabel='Modelowe SPL 1m/1Vrms [dB]',title='C02/100l, ta sama referencja powietrza')
    for aa in ax:aa.grid(alpha=.25);aa.legend(fontsize=7)
    save(fig,'18_skonczona_bryla_i_odgroda')
    result=dict(status='WZORCOWE_MODELE_P11_NIE_GEOMETRIA_FINALNEGO_PROTOTYPU',drivers=len(raw),
                calibration_rows=len(calibration_rows),motor_rows=len(rows),reference_rows=len(reference_rows),
                pilot_rows=len(pilot_rows),max_relative_motor_power_residual=max_power,mass_pilot=pilot_result,
                caveats=['Kształt czaszy i sfery nie jest płaskim koszem w skrzyniMDF.',
                         'Kalibracja wFs nie odtwarza całej impedancji i nie dowodzi rzeczywistegoMmd.',
                         '2π/4π normalizacji nie wolno utożsamiać z dokładną zmianą rzeczywistej odgrody.',
                         'Kontrola reference_faces=0 pokazuje podwójne liczenie powietrza; nie jest finalistą.'])
    (OUT/'p11_geometrie_podsumowanie.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps(result,ensure_ascii=False,indent=2));return result


if __name__=='__main__':main()
