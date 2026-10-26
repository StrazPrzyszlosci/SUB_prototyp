"""Nowa fizyka modułu3D w porównaniu27konfiguracji przy wspólnych warunkach.

Geometria wyklejenia,VD4l i cztery liczby modułów,nie cała dawna kampania.
Osobne ustalone sinusy20–80Hz,2pi/1m,RMS,limityV/I/katalogowegoX.
"""
from pathlib import Path
from itertools import product
import csv,hashlib,json
import numpy as np
from scipy.linalg import eigh
from model_wkladu_P20A import HollowModule
from model_modulu_3D_P20C import gas_port
from model_gazu import Medium,conductance_from_reference
from model_wypelnienia import response_with_acoustic_impedance
from analiza_rozszerzenia_SB import candidates
from geometria_przegrody_P20B import matched_geometry
from analiza_wkladow_P20A import table

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def main():
    cp=ROOT/'dane/konfiguracje/p20c_modul_pelny_3D.json';cfg=json.loads(cp.read_text());bp=ROOT/cfg['reference_insert_config'];base=json.loads(bp.read_text())
    geo_path=ROOT/'dane/konfiguracje/p20b_przegroda_vs_moduly.json';geo_cfg=json.loads(geo_path.read_text())
    stage=json.loads((OUT/'p20c_podsumowanie.json').read_text());assert stage['status']=='COMPLETE_SCOPED_3D_MODULE_FAMILIES'
    with (OUT/'p20c_gaz_i_przeciek.csv').open() as stream:raw=list(csv.DictReader(stream))
    f=np.array(cfg['probe_frequencies_hz']);s=2j*np.pi*f;medium=Medium();nmax=max(cfg['mesh_resolution_cases']);records=[];delta_samples=[]
    thin=HollowModule(cfg['outer_width_depth_height_m'],cfg['wall_m'],'CCCC',base,braced=True)
    beta=2*cfg['material_loss_zeta_at_reference_assumed']/(2*np.pi*cfg['material_loss_reference_hz']);h=np.zeros(len(f),complex)
    for port in thin.faces:
        val,V=eigh(port.K.toarray(),port.M.toarray());a=V.T@port.plate.F
        h+=2*np.sum(a[:,None]**2/(val[:,None]*(1+s*beta)+s*s),axis=0)
    chi=np.empty((len(f),2,2),complex);chi[:,0,0]=h;chi[:,1,1]=h;chi[:,0,1]=-h;chi[:,1,0]=-h
    thin_Ci=thin.inner_volume/(medium.gamma*medium.p0_pa);targets=list(candidates());rows=[];max_energy=0.
    for corner in [0.,1.,10.]:
        G=conductance_from_reference(corner,medium);thinY=gas_port(f,chi,thin_Ci,G)['admittance']
        for eg in cfg['glue_E_pa_cases_assumed']:
            mid=f'TIED_E{eg:g}_N{nmax}'
            ports=[next(r for r in raw if r['case_id']==mid and float(r['f_hz'])==freq and float(r['gas_kappa'])==1.4 and float(r['leak_100l_reference_corner_hz'])==corner) for freq in f]
            Y=np.array([complex(float(r['admittance_re_m3_pa_s']),float(r['admittance_im_m3_pa_s'])) for r in ports])
            pi=np.array([complex(float(r['pressure_ratio_re']),float(r['pressure_ratio_im'])) for r in ports])
            motion=np.array([float(r['peak_relative_node_displacement_m_per_pa_rms']) for r in ports])
            for n in [4,8,12,16]:
                geometry=matched_geometry(base,geo_cfg,n,.018,'LINER_GEOMETRY');Ca=geometry['matched_active_air_l']*.001/(medium.gamma*medium.p0_pa)
                Z=1/(s*Ca+n*Y);Zthin=1/(s*Ca+n*thinY)
                records.append(dict(regulator_case=mid,number_of_modules=n,leak_100l_reference_corner_hz=corner,
                    maximum_cavity_impedance_relative_change_to_thin=float(max(abs(Z/Zthin-1)))))
                for cid,pid,d,category in targets:
                    out=response_with_acoustic_impedance(d,f,Z,medium=medium);old=response_with_acoustic_impedance(d,f,Zthin,medium=medium)
                    max_energy=max(max_energy,float(max(abs(out['energy_residual_w'])/out['p_input_w'])))
                    for vmax,imax in base['amplifier_scenarios_vrms_irms']:
                        U=np.minimum(vmax,np.minimum(imax/out['i_rms_a'],d.xmax_mm*.001/out['x_peak_m']))
                        oldU=np.minimum(vmax,np.minimum(imax/old['i_rms_a'],d.xmax_mm*.001/old['x_peak_m']))
                        spl=out['spl_equivalent_db']+20*np.log10(U);oldspl=old['spl_equivalent_db']+20*np.log10(oldU)
                        pa=abs(out['p_inside_pa'])*U
                        for j,freq in enumerate(f):
                            gas=float(np.sqrt(2)*pa[j]*max(1.,abs(pi[j]))/medium.p0_pa);bend=float(motion[j]*pa[j]/cfg['wall_m'])
                            rows.append(dict(configuration_id=cid,regulator_case=mid,number_of_modules=n,f_hz=float(freq),leak_100l_reference_corner_hz=corner,
                                active_geometric_air_l=geometry['matched_active_air_l'],driver_displacement_l_assumed=4.,amp_v_rms=vmax,amp_i_rms=imax,
                                front_spl_rms_2pi_1m_db=float(spl[j]),difference_vs_thin_same_G_db=float(spl[j]-oldspl[j]),
                                u_rms_v=float(U[j]),i_rms_a=float(out['i_rms_a'][j]*U[j]),x_peak_mm=float(out['x_peak_m'][j]*U[j]*1000),
                                active_gas_pressure_rms_pa=float(pa[j]),max_gas_pressure_peak_fraction=gas,module_peak_component_motion_over_wall=bend,
                                within_assumed_amplitude_screen=bool(gas<=.01 and bend<=.2),
                                scope='Separate steady sine,V/I/catalog-X envelope,no thermal duration or product THD qualification.'))
    assert max_energy<1e-8 and len(rows)==11664
    table('p20c_naped_27_konfiguracji.csv',rows);table('p20c_zmiana_obciazenia.csv',records)
    inputs=[cp,bp,geo_path,Path(__file__),ROOT/'skrypty/model_modulu_3D_P20C.py',ROOT/'skrypty/model_wkladu_P20A.py',ROOT/'skrypty/model_wypelnienia.py',
        ROOT/'skrypty/model_gazu.py',ROOT/'skrypty/model_subwoofera.py',ROOT/'skrypty/analiza_rozszerzenia_SB.py',ROOT/'skrypty/geometria_przegrody_P20B.py',
        ROOT/'dane/przetworniki/pula_rozszerzona.json',ROOT/'dane/przetworniki/rozszerzenie_SB_20261025.json',OUT/'p20c_gaz_i_przeciek.csv']
    result=dict(status='SCOPED_3D_REGULATOR_DRIVER_COMPARISON_NOT_FINAL_DRIVER_CHOICE',cases=len(rows),electrical_configurations=27,
        max_driver_power_residual=max_energy,max_abs_envelope_difference_db=max(abs(r['difference_vs_thin_same_G_db']) for r in rows),
        flagged_amplitude_rows=sum(not r['within_assumed_amplitude_screen'] for r in rows),
        input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        limitations=['Same physical leak G,not same label of a corner frequency tied to different gas volumes.',
            'LINER_GEOMETRY only,VD4l assumption and four module counts; no full new nonlinear/thermal campaign.',
            'Maximum component of relative node motion/wall is only an assumed screen,not exact bending or a glue strain limit.',
            'Constant-beta*K plate reference differs from constant modal-zeta P20A; original outputs unchanged.'])
    (OUT/'p20c_naped_podsumowanie.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print('P20C drive:',len(rows),'points; max delta',result['max_abs_envelope_difference_db'],'dB; flags',result['flagged_amplitude_rows'],flush=True)


if __name__=='__main__':main()
