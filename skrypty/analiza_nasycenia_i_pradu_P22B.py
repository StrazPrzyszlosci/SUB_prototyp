"""648trajektorii liniowych głośników przy saturacji i skończonym feedbackI.

Sterownik nieliniowy,zachowany stan Le i dyskretna tożsamość energii.
Nie jest gwarantowanym limiterem wychylenia/temperatury lub modelem hardware.
"""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from itertools import product
import csv,hashlib,json,platform,time
import numpy as np
from analiza_rozszerzenia_SB import candidates
from model_nasycenia_P22B import linear_state,midpoint_maps,midpoint_voltage,command,current_feedback

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'
CFG=ROOT/'dane/konfiguracje/p22b_nasycenie_i_prad.json'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def inputs():
    names=['brief_system_audio_DIY_v0.6.md','dane/konfiguracje/p22b_nasycenie_i_prad.json',
        'dane/przetworniki/pula_rozszerzona.json','dane/przetworniki/rozszerzenie_SB_20261025.json',
        'skrypty/model_subwoofera.py','skrypty/analiza_rozszerzenia_SB.py',
        'skrypty/model_nasycenia_P22B.py','skrypty/analiza_nasycenia_i_pradu_P22B.py']
    return {n:sha(ROOT/n) for n in names}


def specifications(cfg):
    rows=[]
    for cid,pid,d,cat in candidates():
        for volume,scale,kind,gain in product(cfg['volumes_l'],cfg['command_rms_scale'],cfg['signals'],cfg['current_feedback_gain_ohm_assumed']):
            rows.append(dict(configuration=cid,product=pid,driver=d,volume_l=volume,scale=scale,signal=kind,gain=gain,
                case_id=f'{cid}_V{volume:g}_{kind}_A{scale:g}_G{gain:g}'))
    return rows


def simulate(specs,cfg,rate,retain=()):
    start=time.monotonic();h=1/rate;steps=round(cfg['duration_s']*rate);count=len(specs)
    A=[];B=[];P=[]
    for row in specs:
        a,b,p=linear_state(row['driver'],row['volume_l'],cfg['source_series_resistance_ohm_assumed']);A.append(a);B.append(b);P.append(p)
    A,B,P=np.array(A),np.array(B),np.array(P);inverse,feed=midpoint_maps(A,B,h)
    z=np.zeros((count,3));gain=np.array([r['gain'] for r in specs]);scale=np.array([r['scale'] for r in specs])
    kind_index=np.array([cfg['signals'].index(r['signal']) for r in specs]);threshold=cfg['current_threshold_peak_a_assumed'];rail=cfg['source_rail_peak_v_assumed']
    rs=cfg['source_series_resistance_ohm_assumed'];resistance=np.array([r['driver'].re_ohm for r in specs]);rms=np.array([r['driver'].rms for r in specs])
    input_j=np.zeros(count);coil_j=np.zeros(count);source_j=np.zeros(count);mechanical_j=np.zeros(count);returned_j=np.zeros(count)
    peak=np.zeros((count,3));upeak=np.zeros(count);command_peak=np.zeros(count);rail_samples=np.zeros(count,int);current_over=np.zeros(count,int)
    feedback_samples=np.zeros(count,int);last_squares=np.zeros((count,5));last_count=0;control_error=np.zeros(count)
    retained={int(i):np.empty((steps,8)) for i in retain}
    for step in range(steps):
        t=(step+.5)*h
        waves=np.array([command(t,kind,cfg['source_voltage_rms_reference_v'],1.,cfg['ramp_s']) for kind in cfg['signals']])
        cmd=scale*waves[kind_index]
        free=np.einsum('nij,nj->ni',inverse,z)
        u=midpoint_voltage(free[:,2],feed[:,2],cmd,gain,threshold,rail)
        mid=free+feed*u[:,None];new=2*mid-z
        peak=np.maximum(peak,np.maximum(abs(new),abs(mid)));upeak=np.maximum(upeak,abs(u));command_peak=np.maximum(command_peak,abs(cmd))
        i=mid[:,2];v=mid[:,1]
        input_j+=h*u*i;coil_j+=h*resistance*i*i;source_j+=h*rs*i*i;mechanical_j+=h*rms*v*v
        returned_j+=h*np.maximum(-u*i,0.)
        rail_samples+=abs(u)>=rail*(1-1e-12)
        current_over+=np.maximum(abs(mid[:,2]),abs(new[:,2]))>threshold*(1+1e-10)
        feedback_samples+=abs(i)>threshold
        expected=np.clip(cmd-gain*current_feedback(i,threshold),-rail,rail)
        control_error=np.maximum(control_error,abs(u-expected))
        if t>=cfg['duration_s']-cfg['last_window_s']:
            last_squares+=np.column_stack([mid[:,0]**2,v*v,i*i,u*u,cmd*cmd]);last_count+=1
        for index,history in retained.items():
            acc=A[index,1]@mid[index]
            history[step]=[t,cmd[index],u[index],*mid[index],acc,.5*np.dot(P[index]*new[index],new[index])]
        z=new
    energy=.5*np.sum(P*z*z,axis=1)
    residual=energy-input_j+coil_j+source_j+mechanical_j
    normalizer=np.maximum(energy+abs(input_j)+coil_j+source_j+mechanical_j,1e-30)
    assert np.max(abs(residual)/normalizer)<1e-8 and np.max(control_error)<1e-8
    records=[]
    for k,spec in enumerate(specs):
        rms_last=np.sqrt(last_squares[k]/last_count)
        records.append(dict(case_id=spec['case_id'],configuration=spec['configuration'],driver_name=spec['driver'].name,
            volume_l=spec['volume_l'],signal=spec['signal'],command_rms_scale=spec['scale'],feedback_gain_ohm=spec['gain'],
            integration_rate_hz=rate,duration_s=cfg['duration_s'],initial_state='zero',
            peak_sampled_x_mm=float(peak[k,0]*1000),peak_sampled_velocity_m_s=float(peak[k,1]),
            peak_sampled_current_a=float(peak[k,2]),peak_source_voltage_v=float(upeak[k]),
            peak_command_voltage_v=float(command_peak[k]),catalog_xmax_reference_mm=spec['driver'].xmax_mm,
            x_to_catalog_reference=float(peak[k,0]*1000/spec['driver'].xmax_mm),
            current_to_assumed_peak_threshold=float(peak[k,2]/threshold),
            current_threshold_exceeded_fraction=float(current_over[k]/steps),
            source_on_voltage_rail_fraction=float(rail_samples[k]/steps),
            feedback_active_fraction=float(feedback_samples[k]/steps),
            last_window_x_rms_mm=float(rms_last[0]*1000),last_window_current_rms_a=float(rms_last[2]),
            last_window_source_voltage_rms_v=float(rms_last[3]),last_window_command_rms_v=float(rms_last[4]),
            net_source_energy_j=float(input_j[k]),returned_to_ideal_source_energy_j=float(returned_j[k]),
            copper_heat_j=float(coil_j[k]),series_R_heat_j=float(source_j[k]),mechanical_dissipation_j=float(mechanical_j[k]),
            final_stored_energy_j=float(energy[k]),energy_relative_residual=float(abs(residual[k])/normalizer[k]),
            controller_algebra_absolute_error_v=float(control_error[k])))
    return records,retained,dict(wall_time_s=time.monotonic()-start,max_energy_relative_residual=float(np.max(abs(residual)/normalizer)))


def main():
    frozen=inputs();cfg=json.loads(CFG.read_text());specs=specifications(cfg);retain=[]
    for wanted in cfg['retained_wave_cases']:
        retain.append(next(i for i,r in enumerate(specs) if r['configuration']==wanted['configuration'] and
            r['volume_l']==wanted['volume_l'] and r['signal']==wanted['signal'] and r['scale']==wanted['scale'] and r['gain']==wanted['feedback_ohm']))
    print('P22B starting',len(specs),'cases;step rate',cfg['integration_rate_hz'],flush=True)
    rows,waves,timing=simulate(specs,cfg,cfg['integration_rate_hz'],retain)
    assert inputs()==frozen,'Inputs changed during run'
    with (OUT/'p22b_trajektorie.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    np.savez_compressed(OUT/'p22b_przebiegi_reference.npz',**{specs[k]['case_id']:v for k,v in waves.items()})
    summary=dict(status='COMPLETE_SCOPED_MIDPOINT_SOURCE_SATURATION_FAMILIES_NEEDS_INDEPENDENT_CONTROLS',
        generated_at=datetime.now(ZoneInfo('Europe/Warsaw')).isoformat(),input_sha256=frozen,cases=len(rows),configurations=27,
        time_steps_per_case=round(cfg['duration_s']*cfg['integration_rate_hz']),
        retained_wave_columns=['time_midpoint_s','command_v','source_voltage_v','x_midpoint_m','velocity_midpoint_m_s','current_midpoint_a','acceleration_midpoint_m_s2','energy_at_step_end_j'],
        retained_cases=[specs[k]['case_id'] for k in retain],integration=timing,
        outside_catalog_x_reference=sum(r['x_to_catalog_reference']>1 for r in rows),
        over_current_threshold_cases=sum(r['current_to_assumed_peak_threshold']>1+1e-8 for r in rows),
        libraries=dict(Python=platform.python_version(),NumPy=np.__version__),limitations=cfg['limitations'],
        next='Independent continuous ODE and time-step convergence;then protection/physical-plant integration,not hardware qualification.')
    (OUT/'p22b_podsumowanie.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,allow_nan=False))
    print('P22B calculated',len(rows),'outsideX',summary['outside_catalog_x_reference'],'overI',summary['over_current_threshold_cases'],'energy',timing,flush=True)


if __name__=='__main__':main()
