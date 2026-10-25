"""P18A/P21kontrola: para podatnych ścian i osobna projekcja Rayleigha.

Wnętrze: modeljednorodnegociśnienia z biernym gazem,inne4ściany sztywne.
Zewnętrze: prędkośćsuchej płyty zadana w nieskończonej odgrodzie.
Nie łączymy tych projekcji w pełne3Drozwiązanie realnej obudowy.
"""
import csv
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy.spatial.distance import cdist
from model_gazu import Medium,ThermalSpectrum
from model_plyty_MITC_P18 import shape
from analiza_plyt_i_sciagow_P18A import jobs,build_case

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def quadrature(plate,q,order=2):
    nodes,weights=np.polynomial.legendre.leggauss(order);displacement=plate.expand(q)
    points=[];areas=[];values=[]
    for corners,dofs in zip(plate.elements,plate.dofs):
        x0,y0=plate.xy[corners[0]]
        for i,xi in enumerate(nodes):
            for j,eta in enumerate(nodes):
                N,_,_=shape(xi,eta,plate.dx,plate.dy)
                points.append([x0+(xi+1)*plate.dx/2,y0+(eta+1)*plate.dy/2])
                areas.append(weights[i]*weights[j]*plate.dx*plate.dy/4)
                values.append(N@displacement[dofs[0::3]])
    return np.array(points),np.array(areas),np.array(values)


def radiation_power(f,points,areas,velocity,medium=Medium(),distances=None,mu_order=20,azimuth_count=64):
    """RMS;halfspaceRayleigh. Dwie odrębne całki o tym samym źródle."""
    w=2*np.pi*f;k=w/medium.c
    distances=cdist(points,points) if distances is None else distances
    resistance=medium.rho*w/(2*np.pi)*k*np.sinc(k*distances/np.pi)
    volume_velocity=velocity*areas
    green=float(np.vdot(volume_velocity,resistance@volume_velocity).real)
    mu,weights=np.polynomial.legendre.leggauss(mu_order);mu=(mu+1)/2;weights=weights/2
    phi=2*np.pi*np.arange(azimuth_count)/azimuth_count
    angles=np.array([(np.sqrt(1-u*u)*np.cos(p),np.sqrt(1-u*u)*np.sin(p)) for u in mu for p in phi])
    angular_weights=np.repeat(weights,azimuth_count)*2*np.pi/azimuth_count
    far=np.exp(-1j*k*(angles@points.T))@volume_velocity
    power_far=float(medium.rho*medium.c*k*k/(4*np.pi*np.pi)*sum(angular_weights*abs(far)**2))
    on_axis=medium.rho*1j*w*np.exp(-1j*k)/(2*np.pi)*sum(volume_velocity)
    return dict(power_Green_w=green,power_far_integral_w=power_far,
        relative_power_method_difference=abs(green-power_far)/max(abs(green),abs(power_far),1e-30),
        diagnostic_on_axis_1m_pressure_rms_pa=float(abs(on_axis)))


def main():
    summary=json.loads((OUT/'p18a_podsumowanie.json').read_text())
    for name,h in summary['input_sha256'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,name
    cfg=json.loads((ROOT/'dane/konfiguracje/p18a_plyty_i_sciagi.json').read_text());data=json.loads((ROOT/'dane/materialy/mdf_i_kleje_P18_P19.json').read_text())
    cache=ROOT/summary['checkpoint_folder'];all_cases=jobs(cfg);medium=Medium();coupled=[];radiation=[]
    with (OUT/'p18a_dynamika.csv').open() as h:dynamic=list(csv.DictReader(h))
    for case in all_cases:
        if not (case['geometry']['id']=='K2_side' and case['material']['id']=='REFERENCE' and case['thickness_mm']==22 and
                case['zeta']==.03 and case['boundary'] in ['SSSS','CCCC'] and 'joint_factor' not in case and 'edge_beta' not in case):continue
        p,K,M,ties,prop=build_case(case,cfg,data);cid=case['case_id'];record=json.loads((cache/(cid+'.json')).read_text())
        rows=[r for r in dynamic if r['case_id']==cid]
        # Sterowanie ruchem stożka jako odniesienie pola4pi,nie rzeczywista cała skrzynia.
        for f in [20.,40.,80.]:
            r=next(r for r in rows if float(r['f_hz'])==f);s=2j*np.pi*f
            C=complex(float(r['wall_volume_compliance_m3_pa_real']),float(r['wall_volume_compliance_m3_pa_imag']))
            V=.100;bulk=ThermalSpectrum((.005,),(1.,)).bulk_modulus(np.array([f]),medium)[0];Cab=V/bulk
            for level in [90.,95.,100.]:
                exterior=20e-6*10**(level/20)
                cone_volume=exterior*4*np.pi*np.exp(s/medium.c)/(medium.rho*s*s)
                inflow=-s*cone_volume;rigid_pressure=bulk/V*(-cone_volume)
                pressure=inflow/(s*(Cab+2*C))
                supplied=float((pressure*np.conj(inflow)).real)
                gas_heat=float(-2*np.pi*f*Cab.imag*abs(pressure)**2)
                plate_loss=float(-2*np.pi*f*(2*C).imag*abs(pressure)**2)
                residual=abs(supplied-gas_heat-plate_loss)/max(abs(supplied),1e-30)
                assert min(supplied,gas_heat,plate_loss)>-1e-12 and residual<1e-10
                coupled.append(dict(case_id=cid,boundary=case['boundary'],tie_count=case['tie_count'],f_hz=f,reference_cone_SPL_4pi1m_rms_db=level,
                    air_volume_control_l=100.,wall_pair_compliance_to_air_abs=float(abs(2*C/Cab)),
                    rigid_inner_pressure_rms_pa=float(abs(rigid_pressure)),coupled_inner_pressure_rms_pa=float(abs(pressure)),
                    pressure_change_db=float(20*np.log10(abs(pressure/rigid_pressure))),
                    pair_dissipation_w=plate_loss,gas_relaxation_dissipation_w=gas_heat,supplied_acoustic_power_w=supplied,
                    relative_power_residual=float(residual),
                    maximum_panel_peak_m=float(r['maximum_node_peak_per_PaRMS_m'])*abs(pressure),
                    maximum_nominal_stress_peak_bound_pa=float(r['principal_stress_peak_bound_per_PaRMS'])*abs(pressure),
                    maximum_tie_force_peak_n=float(r['maximum_tie_force_peak_n'])*abs(pressure)/cfg['dynamic_pressure_rms_pa'],
                    scope='PARAELASTYCZNYCHSCIAN4POZOSTALESZTYWNE;JEDNORODNEp;KONTROLA_NIE_PELNASKRZYNIA'))
        arrays=np.load(cache/(cid+'.npz'),allow_pickle=False);distance=None
        for k,f in enumerate(arrays['frequency_hz']):
            points,areas,wfield=quadrature(p,arrays['dynamic'][:,k],2)
            if distance is None:distance=cdist(points,points)
            result=radiation_power(f,points,areas,2j*np.pi*f*wfield,medium,distance)
            dry=next(r for r in rows if abs(float(r['f_hz'])-f)<1e-8)
            dry_power=float(dry['viscous_power_per_PaRMS_squared_w'])
            result.update(case_id=cid,boundary=case['boundary'],tie_count=case['tie_count'],f_hz=float(f),
                dry_structural_dissipation_per_Pa2_w=dry_power,
                projected_radiation_to_dry_dissipation_ratio=result['power_Green_w']/max(dry_power,1e-30),
                scope='PREDKOSC_ZADANA_BEZ_ZWROTNEJ_MASY_I_TLUMIENIA_OD_POWIETRZA;NIESKONCZONA_ODGRODA_NIE_CALA_SKRZYNIA')
            assert result['power_Green_w']>=-1e-12 and result['relative_power_method_difference']<1e-5
            radiation.append(result)
        print('P18kontroleemisji:',cid,flush=True)
    def table(name,rows):
        with (OUT/name).open('w',newline='') as h:
            writer=csv.DictWriter(h,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    table('p18a_para_scian_i_gaz.csv',coupled);table('p18a_Rayleigh_panelu.csv',radiation)
    result=dict(status='P18A_P21_LUMPED_PAIR_AND_SEPARATE_EXTERIOR_PROJECTION',coupled_rows=len(coupled),radiation_rows=len(radiation),
        maximum_coupled_power_residual=max(r['relative_power_residual'] for r in coupled),
        max_power_methods_relative_difference=max(r['relative_power_method_difference'] for r in radiation),
        rows_exceeding_10percent_dry_power_reference=sum(r['projected_radiation_to_dry_dissipation_ratio']>.1 for r in radiation),
        scope='10%to bramka adekwatności projekcji,nie próg słyszalności ani przyjęte wymaganie. Jeśliudział promieniowania znaczący,trzeba dodać jego reakcję przed ilościową prognozą całej obudowy.')
    (OUT/'p18a_sprzezenie_i_emisja.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False));print(json.dumps(result,indent=2,ensure_ascii=False));return result


if __name__=='__main__':main()
