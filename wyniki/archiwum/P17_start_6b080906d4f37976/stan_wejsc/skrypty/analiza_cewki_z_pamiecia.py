"""P12C: kalibracje skalaru, 24 bazy, liniowe porównania i pełne ODE."""
from concurrent.futures import ProcessPoolExecutor,as_completed
from dataclasses import replace
import csv
import hashlib
import json
from pathlib import Path
import shutil
import numpy as np
from model_subwoofera import Driver
from model_nieliniowy import Plant,Shape
from model_cewki_z_pamiecia import (FluxBranch,MemoryModel,calibrate_reference,
    blocked_impedance,generalized_inductance,linear_memory_response,simulate_memory_sine)

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def table(name,rows):
    fields=list(dict.fromkeys(k for row in rows for k in row))
    with (OUT/name).open('w',newline='') as handle:
        w=csv.DictWriter(handle,fieldnames=fields);w.writeheader();w.writerows(rows)


def dynamic_network(plant,profile,cfg):
    if profile=='SIMPLE':return plant.le0,[],'FLUX'
    loss=cfg['dynamic_extra_resistance_fraction']
    poles=cfg['dynamic_two_poles_hz'] if profile=='FLUX_TWO' else [cfg['dynamic_one_pole_hz']]
    branches=[];instant=plant.le0
    for pole in poles:
        calibrated,status=calibrate_reference(plant,pole,loss/len(poles),'REAL_LGEN',cfg['reference_hz'])
        if calibrated is None:raise ValueError(status)
        partial,bs=calibrated;instant-=plant.le0-partial
        branches.extend(replace(b,slope=cfg['dynamic_branch_slope']) for b in bs)
    if instant<0:raise ValueError('Niedodatni podział indukcyjności')
    return instant,branches,'NAIVE' if profile.startswith('NAIVE') else 'FLUX'


def dynamic_worker(job):
    index,entry,volume,f,level,profile,cfg=job
    plant=Plant.from_driver(Driver(**entry['model']))
    ref=linear_memory_response(plant,volume,[f],plant.le0,[])
    cap=min(cfg['amp_vrms'],cfg['amp_arms']/abs(ref['current'][0]),plant.xref/ref['x_peak_m'][0])
    voltage=float(level*cap)
    instant,bs,realization=dynamic_network(plant,profile,cfg)
    model=MemoryModel(plant,volume,instant,bs,Shape(**cfg['dynamic_shape']),cfg['thermal_tau_s'],
                      q_domain=cfg['dynamic_q_domain'],realization=realization)
    row=dict(case_id=index,candidate_id=entry['candidate_id'],driver=entry['model']['name'],volume_l=volume,
             f_hz=f,reference_envelope_fraction=level,profile=profile,voltage_rms_v=voltage,
             instantaneous_h=instant,memory_branches=len(bs),realization=realization,
             source_scope='ASSUMED_MEMORY_NOT_MEASURED_DRIVER_PARAMETERS')
    try:
        result=simulate_memory_sine(model,f,voltage,cycles=cfg['dynamic_initial_cycles'],max_cycles=cfg['dynamic_max_cycles'],
                                    samples_per_cycle=cfg['dynamic_samples_per_cycle'],method=cfg['dynamic_solver'],
                                    rtol=cfg['dynamic_rtol'],atol=cfg['dynamic_atol'],closure_tolerance=cfg['dynamic_closure_tolerance'])
        row.update(result)
        if 'x_peak_m' in result:row['actual_fraction_of_catalog_x']=result['x_peak_m']/plant.xref
    except (ValueError,RuntimeError,OverflowError,FloatingPointError) as error:
        row.update(status='NUMERICAL_OR_DOMAIN_FAILURE',error=str(error))
    return row


def main():
    cfg_path=ROOT/'dane/konfiguracje/p12c_pamiec_cewki.json'
    pool_path=ROOT/'dane/przetworniki/pula_rozszerzona.json'
    cfg=json.loads(cfg_path.read_text());raw=json.loads(pool_path.read_text())['drivers']
    calibration=[];rows=[];max_descriptor_error=0.;max_power_error=0.
    f=np.array(cfg['frequencies_hz'])
    for entry in raw:
        cid=entry['candidate_id'];plant=Plant.from_driver(Driver(**entry['model']))
        scenarios=[('SIMPLE','NONE',0.,0.,plant.le0,[])]
        for descriptor in cfg['descriptor_hypotheses']:
            for pole in cfg['pole_frequencies_hz']:
                for loss in cfg['reference_extra_resistance_fractions_of_Re']:
                    cal,status=calibrate_reference(plant,pole,loss,descriptor,cfg['reference_hz'])
                    record=dict(candidate_id=cid,descriptor=descriptor,pole_hz=pole,extra_loss_fraction=loss,status=status,
                                nominal_catalogue_gate=None)
                    if cal is not None:
                        instant,bs=cal;z=blocked_impedance([cfg['reference_hz']],plant.re,instant,bs)[0]
                        lg=generalized_inductance([cfg['reference_hz']],instant,bs)[0]
                        observed=lg.real if descriptor=='REAL_LGEN' else abs(lg)
                        max_descriptor_error=max(max_descriptor_error,abs(observed/plant.le0-1))
                        gate=None
                        nominal=cfg['catalogue_nominal_consistency'].get(cid)
                        if nominal:
                            re_part=blocked_impedance([nominal['frequency_hz']],plant.re,instant,bs)[0].real
                            gate=bool(re_part<=nominal['Zmin_ohm'])
                            record.update(nominal_catalogue_gate=gate,real_blocked_at_Zmin_frequency_ohm=float(re_part))
                        record.update(instantaneous_h=instant,branch_h=bs[0].inductance_h,tau_s=bs[0].tau_s,
                                      real_Zblocked_reference_ohm=float(z.real),imag_Zblocked_reference_ohm=float(z.imag))
                        scenarios.append((descriptor+'_'+str(pole)+'_'+str(loss),descriptor,pole,loss,instant,bs))
                    calibration.append(record)
        for volume in cfg['volumes_l']:
            reference=linear_memory_response(plant,volume,f,plant.le0,[])
            for name,descriptor,pole,loss,instant,bs in scenarios:
                response=linear_memory_response(plant,volume,f,instant,bs)
                zb=response['z_blocked'];current=response['current'];velocity=response['velocity']
                # Odrębny bilans: cewkaDC + strata portu blokowanego + mechanika/gaz.
                pin=np.real(current)
                zm_real=np.real(plant.bl0*current/velocity)
                residual=pin-abs(current)**2*zb.real-abs(velocity)**2*zm_real
                max_power_error=max(max_power_error,float(max(abs(residual)/np.maximum(pin,1e-300))))
                damping=plant.bl0**2/blocked_impedance([entry['model']['fs_hz']],plant.re,instant,bs)[0]
                damping_ref=plant.bl0**2/blocked_impedance([entry['model']['fs_hz']],plant.re,plant.le0,[])[0]
                for k,frequency in enumerate(f):
                    p=abs(response['pressure_equivalent_pa'][k]);p0=abs(reference['pressure_equivalent_pa'][k])
                    row=dict(candidate_id=cid,volume_l=volume,scenario=name,descriptor=descriptor,pole_hz=pole,
                             extra_loss_fraction=loss,f_hz=float(frequency),
                             spl_equivalent_4pi_1m_1v_db=float(20*np.log10(p/20e-6)),
                             delta_1v_vs_simple_db=float(20*np.log10(p/p0)),
                             current_1v_rms_a=float(abs(current[k])),x_peak_1v_m=float(response['x_peak_m'][k]),
                             input_impedance_real=float(response['z_input'][k].real),
                             input_impedance_imag=float(response['z_input'][k].imag),
                             blocked_real_ohm=float(zb[k].real),blocked_imag_ohm=float(zb[k].imag),
                             electrical_damping_ratio_at_fs=float(damping.real/damping_ref.real),
                             scope='FROZEN_EFFECTIVE_PRIMITIVES_NOT_FULL_TS_FIT')
                    for fraction in cfg['x_fractions']:
                        scale=min(cfg['amp_vrms'],cfg['amp_arms']/abs(current[k]),fraction*plant.xref/response['x_peak_m'][k])
                        scale0=min(cfg['amp_vrms'],cfg['amp_arms']/abs(reference['current'][k]),fraction*plant.xref/reference['x_peak_m'][k])
                        row[f'capacity_X{fraction:g}_4pi_rms_db']=float(20*np.log10(p*scale/20e-6))
                        row[f'capacity_X{fraction:g}_delta_vs_simple_db']=float(20*np.log10(p*scale/(p0*scale0)))
                    rows.append(row)
    table('p12c_kalibracje_i_odrzucenia.csv',calibration);table('p12c_liniowy_naped.csv',rows)
    files=[cfg_path,pool_path,Path(__file__),ROOT/'skrypty/model_cewki_z_pamiecia.py',
           ROOT/'skrypty/model_nieliniowy.py',ROOT/'skrypty/model_subwoofera.py',ROOT/'skrypty/model_gazu.py']
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    run_hash=hashlib.sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest()
    snapshot=OUT/'archiwum'/f'P12C_start_{run_hash[:16]}'/'stan_wejsc'
    for source in files:
        target=snapshot/source.relative_to(ROOT)
        if not target.exists():target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
        assert hashlib.sha256(target.read_bytes()).hexdigest()==hashes[str(source.relative_to(ROOT))]
    journal=OUT/f'p12c_przebieg_{run_hash[:16]}.jsonl';completed={}
    if journal.exists():
        for line in journal.read_text().splitlines():
            r=json.loads(line);assert r['run_sha256']==run_hash;completed[r['row']['case_id']]=r['row']
    jobs=[];index=0
    for entry in raw:
        for volume in cfg['dynamic_volumes_l']:
            for frequency in cfg['dynamic_frequencies_hz']:
                for level in cfg['dynamic_reference_envelope_fractions']:
                    for profile in cfg['dynamic_profiles']:
                        cid=f'{index:06d}';index+=1
                        if cid not in completed:jobs.append((cid,entry,volume,frequency,level,profile,cfg))
    print('P12C ODE:',index,'przypadków;',len(completed),'z dziennika',flush=True)
    with journal.open('a') as handle:
        with ProcessPoolExecutor(max_workers=cfg['workers']) as executor:
            for future in as_completed([executor.submit(dynamic_worker,j) for j in jobs]):
                row=future.result();completed[row['case_id']]=row
                handle.write(json.dumps(dict(run_sha256=run_hash,row=row),ensure_ascii=False,allow_nan=False)+'\n');handle.flush()
                if len(completed)%100==0 or len(completed)==index:print('P12C',len(completed),'/',index,row['status'],flush=True)
    dynamic=[completed[f'{k:06d}'] for k in range(index)];table('p12c_nieliniowa_pamiec.csv',dynamic)
    states={status:sum(r['status']==status for r in dynamic) for status in sorted({r['status'] for r in dynamic})}
    valid=[r for r in dynamic if r['status']=='PERIODIC_WITHIN_MODEL_TOLERANCE']
    result=dict(status='RODZINY_P12C_NIE_IDENTYFIKACJA_PRODUKTOW',run_sha256=run_hash,input_sha256=hashes,
                calibration_rows=len(calibration),calibrations_valid=sum(r['status']=='VALID' for r in calibration),
                calibrations_rejected=sum(r['status']!='VALID' for r in calibration),
                nominal_C18_inconsistent=sum(r.get('nominal_catalogue_gate') is False for r in calibration),
                linear_rows=len(rows),max_reference_descriptor_error=max_descriptor_error,max_linear_relative_power_error=max_power_error,
                dynamic_rows=len(dynamic),dynamic_status_counts=states,max_dynamic_relative_energy_error=max(r['energy_relative_residual'] for r in valid),
                scope='Pełne obliczenia zadanych rodzin. Parametry ukryte nie są tolerancją producentów, NAIVE jest kontrolą interpretacji. Nie utożsamiać średniej straty gałęzi z grzaniem samej cewki.')
    (OUT/'p12c_podsumowanie.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
    if states.get('NUMERICAL_OR_DOMAIN_FAILURE'):raise RuntimeError('Są nierozstrzygnięte błędy; sprawdzić dziennik')
    return result


if __name__=='__main__':main()
