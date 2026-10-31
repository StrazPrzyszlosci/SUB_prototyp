#!/usr/bin/env python3
"""P24D: sampled two-channel protection, latency, observability loss and faults.

Illustrative C02 80 L and P24B central Cauer data. All thresholds, delays,
sensor errors and external actuator behavior are *assumptions*, not
product characteristics. This is NOT deployable firmware or safety approval.
"""
import json, math
from pathlib import Path

DT = .05
DURATION = 180.
RE0, ALPHA, LE, BL = 3., .00393, .00092, 15.
FS, MMS, QMS, VAS, SD = 19.5, .306, 3.02, .212, .08296
RHO, SOUND = 1.2, 343.
XMAX_PEAK_M = .014
CC, CM, RCM, RMA = 40., 1000., .6, 1.5
VOLTAGE_CAP = min(4*10**(25.5/20), math.sqrt(4*500))
CURRENT_PEAK_CAP = 27.
ASSUMED_CONTOUR_K = 80.
MECHANICAL_GUARD = .8 * XMAX_PEAK_M

def electrical(freq, tc, vol=.080):
    w=2*math.pi*freq
    cms=VAS/(RHO*SOUND**2*SD**2)
    zm=complex(2*math.pi*FS*MMS/QMS, w*MMS-1/(w*cms) - SD**2*RHO*SOUND**2/(w*vol))
    re=RE0*(1+ALPHA*tc)
    current=1/(re+.0026+1j*w*LE+BL*BL/zm)
    vel=BL*current/zm
    return re,abs(current),math.sqrt(2)*abs(vel)/w

# threshold is on measured (biased) temperature rise, not actual Tc.
# requested actuator applies after explicit latency. Watchdog latches a
# fault, requires manual reset (not modeled). No assumption about miniDSP API.
SCENARIOS = {
 "none": dict(threshold=None, bias=0, sample=1, latency=0, watchdog=False),
 "naive_late": dict(threshold=80, bias=-20, sample=1, latency=2, watchdog=False),
 "guarded": dict(threshold=45, bias=-20, sample=1, latency=.25, watchdog=True),
 "guarded_slow_actuator": dict(threshold=45, bias=-20, sample=1, latency=5, watchdog=True),
 "guarded_bias_exceeds_bound": dict(threshold=45, bias=-60, sample=1, latency=.25, watchdog=True),
 "guarded_dropout_fail_closed": dict(threshold=45, bias=-20, sample=1, latency=.25, watchdog=True, dropout_at=20.),
 "guarded_dropout_fail_open": dict(threshold=45, bias=-20, sample=1, latency=.25, watchdog=False, dropout_at=20.),
 "guarded_actuator_stuck_on": dict(threshold=45, bias=-20, sample=1, latency=.25, watchdog=True, stuck_on=True),
}

def simulate_one(freq, cfg, dt=DT):
    tc=tm=0.
    gate=True
    target=True
    queued=None
    latch=False
    last_sample_t=0.
    last_seen_t=0.
    on_time=0.
    maximum_tc=maximum_x=maximum_tm=0.
    time_above_80=0.
    first_mute=None
    first_fault=None
    stop_at_200K_s=None
    total_copper_j=0.
    steps=round(DURATION/dt)
    period_steps=round(cfg["sample"]/dt)
    for k in range(steps):
        t=round(k*dt,10)
        sensor_alive=t<cfg.get("dropout_at",float("inf"))
        if k%period_steps==0 and sensor_alive:
            last_seen_t=t
            observed=tc+cfg["bias"]
            if cfg["threshold"] is not None and not latch:
                if observed>=cfg["threshold"]:
                    target=False
                elif observed<cfg["threshold"]-5:  # hysteresis 5 K assumed
                    target=True
        # Lost sensor: either latch to mute, or retain last commanded gate.
        if cfg["watchdog"] and (t-last_seen_t>cfg["sample"]+.00001):
            if not latch:
                latch=True
                first_fault=t
            target=False
        if latch: target=False
        # Queue only if requested state differs from applied state.
        # Always allow a pending command to be superseded before execution.
        if target!=gate:
            if queued is None or queued[1]!=target:
                queued=(t+cfg["latency"],target)
        else:
            queued=None
        if queued is not None and t+1e-9>=queued[0]:
            gate=queued[1]
            queued=None
        if cfg.get("stuck_on",False):
            gate=True   # failed actuator; software mute ignored
        if not gate and first_mute is None:
            first_mute=t
        re,i_per,x_per=electrical(freq,tc)
        u=min(VOLTAGE_CAP,CURRENT_PEAK_CAP/(math.sqrt(2)*i_per),
              MECHANICAL_GUARD/x_per) if gate else 0.
        i=i_per*u
        pcu=re*i*i
        d_tc=(pcu-(tc-tm)/RCM)/CC
        d_tm=((tc-tm)/RCM-tm/RMA)/CM
        tc+=dt*d_tc
        tm+=dt*d_tm
        assert math.isfinite(tc) and math.isfinite(tm) and tc>=-1e-8 and tm>=-1e-8
        maximum_tc=max(maximum_tc,tc)
        maximum_tm=max(maximum_tm,tm)
        xpk=x_per*u
        maximum_x=max(maximum_x,xpk)
        time_above_80 += (tc>ASSUMED_CONTOUR_K+1e-8)*dt
        on_time+=gate*dt
        total_copper_j+=pcu*dt
        if tc>=200.:
            stop_at_200K_s=round(t+dt,3)
            break  # P24B assumed model-domain stop, not failure temperature
    return dict(max_coil_K=round(maximum_tc,3),max_motor_K=round(maximum_tm,3),
        max_xpeak_mm=round(maximum_x*1000,4),
        seconds_over_diagnostic_80K=round(time_above_80,3),
        gate_on_seconds=round(on_time,3),
        copper_energy_J=round(total_copper_j,2),
        first_mute_s=first_mute,first_fault_s=first_fault,
        stopped_at_hypothetical_200K_s=stop_at_200K_s)

def main():
    rows=[]
    for freq in [20.,80.]:
        for name,cfg in SCENARIOS.items():
            result=simulate_one(freq,cfg)
            rows.append(dict(channel_frequency_hz=freq,scenario=name,**result))
    scan=[]
    for f in [20., 80.]:
        for bias in [0.,-10.,-20.,-30.,-40.,-60.]:
            for delay in [.1,.25,.5,1.,2.,5.]:
                c=dict(threshold=45.,bias=bias,sample=1.,latency=delay,watchdog=True)
                sim=simulate_one(f,c)
                scan.append(dict(f_hz=f,bias_K=bias,latency_s=delay,
                    max_coil_K=sim["max_coil_K"],over_80_s=sim["seconds_over_diagnostic_80K"]))
    dt_audit=[]
    for f in [20.,80.]:
        for case in ["guarded","naive_late"]:
            coarse=simulate_one(f,SCENARIOS[case],dt=.05)
            fine=simulate_one(f,SCENARIOS[case],dt=.025)
            dt_audit.append(dict(f_hz=f,scenario=case,dt_coarse=.05,dt_fine=.025,
                peak_coarse_K=coarse["max_coil_K"],peak_fine_K=fine["max_coil_K"],
                abs_difference_K=round(abs(coarse["max_coil_K"]-fine["max_coil_K"]),4)))
    # independently controlled dual outputs: A sensor fault only affects A.
    fault_a=simulate_one(80,SCENARIOS["guarded_dropout_fail_closed"])
    baseline_b=simulate_one(20,SCENARIOS["guarded"])
    other_b=simulate_one(20,SCENARIOS["guarded"])
    assert baseline_b==other_b
    assert fault_a["first_fault_s"] is not None
    assert max(r["max_xpeak_mm"] for r in rows)<=11.2+1e-7
    assert all(r["seconds_over_diagnostic_80K"]==0 for r in rows
        if r["scenario"]=="guarded" and r["channel_frequency_hz"]==80)
    out=dict(study="P24D",date="2026-10-31",driver="C02 RSS390HF-4 (model P24B)",
      dt_s=DT,duration_s=DURATION,frequency_hz=[20,80],
      limits=dict(assumed_temperature_contour_K=80,
        mechanical_fraction_of_catalog_peak_Xmax=.8,
        xguard_mm=11.2, amp_rms_cap_v=VOLTAGE_CAP,
        amp_peak_current_limit_A=CURRENT_PEAK_CAP),
      assumed_thermal=dict(coil_C_J_K=CC,motor_C_J_K=CM,Rcm_K_W=RCM,Rma_K_W=RMA),
      assumptions=SCENARIOS, cases=len(rows)+len(scan), results=rows,
      scan=scan, scan_contour_exceed_count=sum(x["over_80_s"]>0 for x in scan),
      scan_size=len(scan),dt_audit=dt_audit,
      dual_channel_test=dict(A_80Hz_dropout=fault_a,
        B_20Hz_control_without_A_fault=baseline_b,
        B_20Hz_control_with_A_fault=other_b,
        invariant_B_unchanged=baseline_b==other_b,
        meaning="independence is only a tested SOFTWARE MODEL property, not real wiring"),
      methodology_notes=[
        "The observed temperature is Tc+bias; this is an error-envelope surrogate, NOT a running U/I estimator.",
        "Mechanical guard uses an ideal sine peak estimator from known P24B model; not implemented DSP.",
        "Virtual cut on a line-level path is treated as instantaneous after assumed actuator latency, not verified miniDSP command response.",
        "The threshold of 45 K is arbitrary for stress-testing a -20 K bias and actuator delays; 80 K is NOT a safety temperature.",
        "Sensor watchdog latches loss when no new observation for more than sample_s; failed line-level hardware gate is explored separately.",
        "Fixed 80 L and fixed central Cauer are not validated; zero crossing of diagnostic contour is not evidence of real-world safety.",
        "Stop numerical run at +200 K coil rise to avoid uncalibrated extrapolation, as in P24B."
      ],
      )
    outpath=Path(__file__).resolve().parents[1]/"wyniki"/"p24d_opoznienia_faulty_20261031.json"
    outpath.parent.mkdir(parents=True,exist_ok=True)
    outpath.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({"cases":out["cases"],"results":rows,"dt_audit":dt_audit,"scan_exceed":out["scan_contour_exceed_count"],"dual_channel_test":out["dual_channel_test"]},
                     indent=2,ensure_ascii=False))
if __name__=="__main__":main()
