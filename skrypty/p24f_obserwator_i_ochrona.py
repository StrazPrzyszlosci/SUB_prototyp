#!/usr/bin/env python3
"""P24F — synthetic multi-frequency U/I observation + thermal protection.

Educational/research-only. No real U/I, no physical validation, no approved safe
coil temperature. Model assumes availability of coherent diagnostic spectra.
"""
from __future__ import annotations
import csv
import hashlib
import json
import math
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'wyniki'
DT=0.05
DURATION=150.
SEED=20261031
FREQ_OBS=np.array([80.,150.,300.])
RE0=3.
ALPHA=.00393
LE0=.00092
BL0=15.
SD=.08296
MMS=.306
FS=19.5
QMS=3.02
VAS=.212
RHO=1.2
SPEED=343.
VOL=.080
CONTOUR=80. # DIAGNOSTIC only, not safe temperature limit
XMAX_PEAK=.014
XCUT=.8*XMAX_PEAK # arbitrary, not calibrated
GAIN=10**(25.5/20)
U_CAP=min(4*GAIN,math.sqrt(4*500))
I_CAP_PEAK=27.
R_SOURCE=.0026
THERMAL={
 'favorable': dict(cc=90.,rcm=.25,cm=1500.,rma=.8),
 'central': dict(cc=40.,rcm=.6,cm=1000.,rma=1.5),
 'adverse': dict(cc=20.,rcm=1.2,cm=500.,rma=2.5),
}
SENSORS={
 'nominal':dict(bl=1.,le=1.,cms=1.,wire=0.,availability='always'),
 'motor_drift':dict(bl=.97,le=1.1,cms=1.05,wire=0.,availability='always'),
 'cable_minus_0p1':dict(bl=.97,le=1.1,cms=1.,wire=-.1,availability='always'),
 'cable_plus_0p1':dict(bl=.97,le=1.1,cms=1.,wire=.1,availability='always'),
 'cable_minus_0p25':dict(bl=.97,le=1.1,cms=1.,wire=-.25,availability='always'),
 'dropout_20to45':dict(bl=.97,le=1.1,cms=1.05,wire=-.1,availability='dropout'),
 'sparse_every_5s':dict(bl=.97,le=1.1,cms=1.05,wire=0.,availability='sparse'),
 'no_excitation':dict(bl=.97,le=1.1,cms=1.05,wire=0.,availability='none'),
}
POLICIES=['no_thermal_guard','naive_measured_80','margin_measured_55','predicted_bound_15K_5Kps']

def zm(freq:float, cms_factor:float=1.):
    w=2*math.pi*freq
    cms=VAS/(RHO*SPEED**2*SD**2)*cms_factor
    return complex(2*math.pi*FS*MMS/QMS,w*MMS-1/(w*cms)-SD*SD*RHO*SPEED*SPEED/(w*VOL))

def impedance(freq:float, tc:float, sensor:dict|None=None):
    d=sensor or SENSORS['nominal']
    return (RE0*(1+ALPHA*tc)+d['wire']+1j*2*math.pi*freq*LE0*d['le']+
            (BL0*d['bl'])**2/zm(freq,d['cms']))

def true_response(freq:float,tc:float):
    w=2*math.pi*freq
    re=RE0*(1+ALPHA*tc)
    current=1/(re+R_SOURCE+1j*w*LE0+BL0**2/zm(freq))
    vel=BL0*current/zm(freq)
    return re,abs(current),math.sqrt(2)*abs(vel)/w

# Delta Z = Delta Re + Delta BL^2 / Zm + j omega Delta Le
# Estimator fixed mechanical Zm -- source of model misspecification.
DESIGN=np.vstack([
    np.column_stack([np.ones(3),np.array([1/zm(f) for f in FREQ_OBS]).real,np.zeros(3)]),
    np.column_stack([np.zeros(3),np.array([1/zm(f) for f in FREQ_OBS]).imag,2*math.pi*FREQ_OBS*.001]),
])
PINV=np.linalg.pinv(DESIGN)
assert np.linalg.matrix_rank(DESIGN)==3

def estimate_T(rng,tc,sensor,zcold):
    zs=np.array([impedance(f,tc,sensor) for f in FREQ_OBS])
    # Coherent complex phasor with hypothetical amplitude 0.5% / phase 0.2deg noise.
    epsamp=rng.normal(0.,.005,3)
    epsphase=rng.normal(0.,math.radians(.2),3)
    obs=zs*(1+epsamp)*np.exp(1j*epsphase)
    dz=obs-zcold
    delta=np.concatenate([dz.real,dz.imag])
    return float((PINV@delta)[0]/(RE0*ALPHA))

def available(t,sensor):
    a=sensor['availability']
    if a=='always':return True
    if a=='dropout':return not (20 <= t <45)
    if a=='sparse':return abs(t/5-round(t/5))<1e-8
    if a=='none':return False
    raise ValueError(a)

def run(freq, thermal_name, sensor_name,policy, seed):
    th=THERMAL[thermal_name];sensor=SENSORS[sensor_name]
    rng=np.random.default_rng(seed)
    # fixed, noisy cold complex impedance at t=0 - calibration uncertainty persists
    z0=np.array([impedance(f,0,SENSORS['nominal']) for f in FREQ_OBS]);
    zcold=z0*(1+rng.normal(0.,.005,3))*np.exp(1j*rng.normal(0.,math.radians(.2),3))
    tc=tm=0.
    gate=True
    target=True
    pending=None
    last_measured=None
    last_obs=None
    fault_latch=False
    first_fault=None
    first_mute=None
    maximum_tc=0.
    max_motor=0.
    over_s=0.
    ever_unsafe_assumed=False
    max_x=0.
    gate_on=0.
    nobs=0
    errors=[]
    toggles=0
    time_without_fresh=0.
    fail_bound=0
    time_guard_active=0.
    step_count=int(DURATION/DT)
    for k in range(step_count):
        t=k*DT
        # Periodic coherent measurement once per 0.5 seconds if three frequencies exist.
        if k%round(.5/DT)==0 and available(t,sensor):
            last_measured=estimate_T(rng,tc,sensor,zcold)
            last_obs=t
            nobs+=1
            errors.append(last_measured-tc)
            if abs(last_measured-tc)>15:fail_bound+=1
        fresh_age = float('inf') if last_obs is None else t-last_obs
        time_without_fresh += (fresh_age>2.0)*DT
        if policy!='no_thermal_guard':
            if fresh_age>2.0 and not fault_latch:
                fault_latch=True
                first_fault=t
            if fault_latch:
                target=False
            elif last_measured is not None:
                if policy=='naive_measured_80':
                    thresh=80.;hyst=5.
                    measured=last_measured
                elif policy=='margin_measured_55':
                    thresh=55.;hyst=8.
                    measured=last_measured
                elif policy=='predicted_bound_15K_5Kps':
                    thresh=80.;hyst=8.
                    # ASSUMED bound, not derived from physical or instrument specs.
                    measured=last_measured+15+5*(fresh_age+.25)
                else:raise ValueError(policy)
                if measured>=thresh:target=False
                elif measured<thresh-hyst:target=True
        # Naive/margin/predicted commands take an assumed 0.25 s to actuate.
        # No actuator fault simulated here (P24D studied a stuck-on actuator).
        if target!=gate:
            if pending is None or pending[1]!=target: pending=(t+.25,target)
        else:
            pending=None
        if pending and t+1e-9>=pending[0]:
            gate=pending[1]
            pending=None
            toggles+=1
            if not gate and first_mute is None:first_mute=t
        re,iu,xu=true_response(freq,tc)
        u=min(U_CAP,I_CAP_PEAK/(math.sqrt(2)*iu),XCUT/xu) if gate else 0.
        pcu=re*(iu*u)**2
        new_tc=tc+DT*(pcu-(tc-tm)/th['rcm'])/th['cc']
        new_tm=tm+DT*((tc-tm)/th['rcm']-tm/th['rma'])/th['cm']
        assert min(new_tc,new_tm)>-1e-9 and math.isfinite(new_tc)
        tc,tm=new_tc,new_tm
        maximum_tc=max(maximum_tc,tc)
        max_motor=max(max_motor,tm)
        max_x=max(max_x,xu*u)
        gate_on+=gate*DT
        over_s+=(tc>CONTOUR+1e-9)*DT
        if tc>=200:
            # Stop at an arbitrary numerical model-domain boundary.
            break
    max_abs_error=max((abs(x) for x in errors),default=None)
    err_p95=float(np.quantile(abs(np.array(errors)),.95)) if errors else None
    return dict(frequency_hz=freq,thermal=thermal_name,sensor=sensor_name,policy=policy,
        steps=k+1, stopped_at_model_200K=tc>=200,
        max_true_coil_rise_K=round(maximum_tc,3),max_true_motor_rise_K=round(max_motor,3),
        time_true_above_diagnostic_80K_s=round(over_s,3),
        max_peak_excursion_mm=round(max_x*1000,3),
        on_time_s=round(gate_on,3),first_mute_s=first_mute,
        fault_latched=fault_latch,first_fault_s=first_fault,
        observations=nobs,measurement_p95_abs_error_K=None if err_p95 is None else round(err_p95,3),
        measurement_max_abs_error_K=None if max_abs_error is None else round(max_abs_error,3),
        observations_exceed_assumed_15K=fail_bound,
        time_stale_over_2s_s=round(time_without_fresh,3),gate_transitions=toggles)

def main():
    OUT.mkdir(exist_ok=True)
    results=[]
    for freq in (20.,80.):
      for thermal in THERMAL:
        for sensor in SENSORS:
          for policy in POLICIES:
            # same physical experiment seed per sensor/thermal/frequency, irrespective of policy
            s=SEED+int(freq)*1000+list(THERMAL).index(thermal)*100+list(SENSORS).index(sensor)
            results.append(run(freq,thermal,sensor,policy,s))
    assert len(results)==2*3*len(SENSORS)*len(POLICIES)
    assert all(x['max_peak_excursion_mm']<=11.2+1e-6 for x in results)
    # Structural sanity: even ideal observations cannot exist without excitation.
    assert all(x['observations']==0 for x in results if x['sensor']=='no_excitation')
    # Cross-channel separation: fault injected on A cannot affect B in this independent model
    a=run(80.,'central','dropout_20to45','predicted_bound_15K_5Kps',SEED+80)
    b_nominal=run(20.,'central','nominal','predicted_bound_15K_5Kps',SEED+20)
    b_with_a_fault=run(20.,'central','nominal','predicted_bound_15K_5Kps',SEED+20)
    assert b_nominal==b_with_a_fault
    def group(policy):
        rr=[x for x in results if x['policy']==policy]
        return dict(n=len(rr),above_80_cases=sum(x['time_true_above_diagnostic_80K_s']>0 for x in rr),
          no_excitation_cases=sum(x['sensor']=='no_excitation' for x in rr),
          max_coil_K=max(x['max_true_coil_rise_K'] for x in rr),
          min_on_s=min(x['on_time_s'] for x in rr),
          median_on_s=round(float(np.median([x['on_time_s'] for x in rr])),3),
          model_stops=sum(x['stopped_at_model_200K'] for x in rr))
    summary={policy:group(policy) for policy in POLICIES}
    # Sensor error > assumed envelope invalidates any advertised robustness theorem.
    exceed=sum(x['observations_exceed_assumed_15K']>0 for x in results if x['policy']=='predicted_bound_15K_5Kps')
    result=dict(study='P24F',date='2026-10-31',status='simulated NOT validated',
        seed=SEED,dt_s=DT,duration_s=DURATION,frequency_hz=[20,80],
        tested_cases=len(results),thermal_scenarios=THERMAL,sensor_scenarios=SENSORS,
        policies=POLICIES,diagnostic_contour_K=CONTOUR,
        results=results,policy_summary=summary,
        assumed_15K_error_bound_violated_in_scenarios=exceed,
        crosschannel_fault_test=dict(channel_A=a,channel_B=b_nominal,
           B_same_when_A_faults=b_nominal==b_with_a_fault),
        methodological_limits=[
          'No acoustic injection, music excitation, ADC, clipping or nonlinearity models.',
          'Temperature threshold 80 K is only a diagnostic contour; not a safe limit.',
          'Predicted 15K error envelope and 5K/s growth are assumed and tested, not certified bounds.',
          'The synthetic spectrogram supplies coherent 80/150/300Hz data even during music; outside the explicit dropout/sparse/no-excitation scenarios.',
          'Cold calibration is noisy and fixed; cable drift and unmodeled Cms are deliberately allowed.',
          'True plant, correction and guards share nominal electromechanical model; gross model mismatch remains untested.',
          'Gate is ideal command realized after assumed 0.25s; physical power stage and miniDSP API unverified.',
          'All 3 thermal scenarios hypothetical, no measured true temperatures.'
        ])
    (OUT/'p24f_192_trajektorii_20261031.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    with (OUT/'p24f_192_przypadkow.csv').open('w',newline='') as file:
        fields=list(results[0]);writer=csv.DictWriter(file,fieldnames=fields);writer.writeheader();writer.writerows(results)
    print(json.dumps(dict(tested_cases=len(results),policy_summary=summary,
        assumed_15K_error_bound_violated_in_scenarios=exceed,
        selected=[x for x in results if x['frequency_hz']==80 and x['thermal']=='central'
            and x['sensor'] in ('nominal','dropout_20to45','cable_minus_0p1')]),
        ensure_ascii=False,indent=2))

if __name__=='__main__':main()
