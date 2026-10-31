#!/usr/bin/env python3
"""P24B: reproducible two-node Cauer voice-coil thermal transient, coupled
to the small-signal impedance and voltage/current envelope from P22C.

All Rth, Cth, coil rise and mechanical headroom values are HYPOTHETICAL.
The 'oracle' protection reads actual internal states; NOT deployable in miniDSP.
Usage: python skrypty/p24b_czasowa_termika_cewki.py
"""
import csv,hashlib,json,math,platform
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CFG=ROOT/"dane/konfiguracje/p24b_czasowa_termika_20261031.json"
OUT=ROOT/"wyniki"

def thermal_transfer(m,vol,f,amp,tc):
    """RMS one-volt terminal I and mechanical velocity for Re(Tcoil)."""
    sd=m["sd_cm2"]*1e-4
    rho,c=m["rho_kg_m3"],m["sound_m_s"]
    cms=m["vas_l"]*.001/(rho*c*c*sd*sd)
    w=2*math.pi*f
    zm=complex(2*math.pi*m["fs_hz"]*(m["mms_g"]*.001)/m["qms"],
        w*(m["mms_g"]*.001)-1/(w*cms)-sd*sd*rho*c*c/(w*vol*.001))
    re=m["re_25_ohm"]*(1+m["alpha_copper_per_K"]*tc)
    zs=complex(re+amp["series_output_resistance_ohm"],w*m["le_mh"]*.001)
    current=1/(zs+m["bl_tm"]**2/zm)
    vel=m["bl_tm"]*current/zm
    assert re>0
    power_balance=abs(current.real-((re+amp["series_output_resistance_ohm"])*abs(current)**2+
                    zm.real*abs(vel)**2))/max(current.real,1e-14)
    assert power_balance<1e-10
    return re,abs(current),math.sqrt(2)*abs(vel)/w,power_balance

def run_scenario(cfg,vol,f,amp,thermal,signal,guard,dt):
    m=cfg["model"]
    n=round(cfg["duration_s"]/dt)
    tc=tm=0.0;maximum_tc=maximum_tm=maximum_x=0.0;step_count=0;exceed_x_s=exceed_T80_s=0.0
    first_80_s=None;total_power_J=0.0;thermal_residual=0.0
    req_energy=delivered_energy=0.0;on_time=limiting_time=0.0;stop_time=None
    trace=[]
    fixed_cap=min(
        amp["max_dsp_input_vrms"]*10**(amp["gain_db"]/20),
        math.sqrt(4*amp["rated_4ohm_w_reference"]),
        amp["peak_output_voltage_V"]/math.sqrt(2) if amp["peak_output_voltage_V"] is not None else math.inf)
    for k in range(n):
        t=k*dt
        on=(t+1e-9)%signal["period_s"]<signal["on_s"]
        re,i_per,xpk_per,balance=thermal_transfer(m,vol,f,amp,tc)
        request=fixed_cap if on else 0.0
        u=min(request,amp["peak_output_current_A"]/(math.sqrt(2)*i_per))
        if guard["xmax_guard_fraction"] is not None:
            u=min(u,m["xmax_oneway_peak_mm"]*.001*guard["xmax_guard_fraction"]/xpk_per)
        if guard["temperature_guard_rise_K"] is not None:
            # Exact one-step forward-Euler upper bound for the chosen ODE;
            # NOT a certified robust observer, no sensor delay considered.
            needed= (guard["temperature_guard_rise_K"]-tc)*thermal["Ccoil_J_K"]/dt + (
                tc-tm)/thermal["Rcoil_motor_K_W"]
            upper=max(0.0,needed)
            u=min(u,math.sqrt(upper/(re*i_per*i_per)))
        if on:
            on_time+=dt;req_energy+=request*request*dt
            delivered_energy+=u*u*dt
            if u<request-1e-7:limiting_time+=dt
        coil_i=i_per*u
        pcu=re*coil_i*coil_i
        old_energy=thermal["Ccoil_J_K"]*tc+thermal["Cmotor_J_K"]*tm
        newtc=tc+dt*(pcu-(tc-tm)/thermal["Rcoil_motor_K_W"])/thermal["Ccoil_J_K"]
        newtm=tm+dt*((tc-tm)/thermal["Rcoil_motor_K_W"]-
               tm/thermal["Rmotor_ambient_K_W"])/thermal["Cmotor_J_K"]
        if min(newtc,newtm)<-1e-10:raise AssertionError("negative temperature state")
        newenergy=thermal["Ccoil_J_K"]*newtc+thermal["Cmotor_J_K"]*newtm
        expected=old_energy+dt*(pcu-tm/thermal["Rmotor_ambient_K_W"])
        thermal_residual=max(thermal_residual,abs(newenergy-expected)/max(1,abs(expected)))
        xpk_mm=xpk_per*u*1000
        if xpk_mm>m["xmax_oneway_peak_mm"]*(1+1e-10):exceed_x_s+=dt
        if newtc>=80:
            exceed_T80_s+=dt
            if first_80_s is None:first_80_s=t+dt
        maximum_tc=max(maximum_tc,newtc);maximum_tm=max(maximum_tm,newtm)
        maximum_x=max(maximum_x,xpk_mm)
        total_power_J+=pcu*dt
        step_count+=1
        tc,tm=newtc,newtm
        if (k+1)*dt % 1 <dt*0.5 and (abs(vol-80)<1e-10 and f==40 and
           amp["id"]=="NC500_RCA2" and thermal["id"]=="central_ASSUMED"
           and signal["id"]=="sustained"):
            trace.append(dict(time_s=round((k+1)*dt,4),coil_rise_K=tc,
                              motor_rise_K=tm,source_vrms=u))
        if tc>=cfg["numerical_stop_rise_K"]:
            stop_time=t+dt
            break
    if thermal_residual>1e-10:raise AssertionError(("energy",thermal_residual))
    if guard["temperature_guard_rise_K"] is not None and maximum_tc>guard["temperature_guard_rise_K"]+1e-8:
        raise AssertionError(("thermal_guard_failed",maximum_tc))
    return dict(volume_l=vol,frequency_hz=f,amp=amp["id"],thermal=thermal["id"],
        program=signal["id"],protection=guard["id"],dt_s=dt,
        executed_steps=step_count,stopped_at_200K_s=stop_time,
        maximum_coil_rise_K=maximum_tc,maximum_motor_rise_K=maximum_tm,
        final_coil_rise_K=tc,maximum_xpeak_mm=maximum_x,
        time_over_xmax_s=exceed_x_s,time_over_hypothetical_80K_s=exceed_T80_s,
        first_time_over_80K_s=first_80_s,on_s=on_time,
        limited_on_s=limiting_time,energy_copper_J=total_power_J,
        source_energy_ratio=delivered_energy/max(req_energy,1e-18),
        average_level_reduction_on_db=10*math.log10(max(1e-20,delivered_energy/max(req_energy,1e-18))),
        maximum_thermal_energy_residual=thermal_residual),trace

def main():
    c=json.loads(CFG.read_text());OUT.mkdir(exist_ok=True)
    rows=[];profiles=[]
    for vol in c["box_volumes_l"]:
      for f in c["frequency_hz"]:
       for amp in c["amps"]:
        for th in c["thermal_scenarios"]:
         for sig in c["signal_programs"]:
          for protect in c["protection"]:
           row,trace=run_scenario(c,vol,f,amp,th,sig,protect,c["dt_s"])
           rows.append(row)
           profiles.extend([dict(strategy=protect["id"],**p) for p in trace])
    assert len(rows)==729,len(rows)
    with (OUT/"p24b_wyniki_729.csv").open("w",newline="") as h:
        writer=csv.DictWriter(h,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)
    with (OUT/"p24b_profile_termiczne.csv").open("w",newline="") as h:
        writer=csv.DictWriter(h,fieldnames=list(profiles[0]))
        writer.writeheader();writer.writerows(profiles)
    independent=[]
    for p in c["protection"]:
      a=c["amps"][1];th=c["thermal_scenarios"][1]
      sig=c["signal_programs"][0]
      A,_=run_scenario(c,80,40,a,th,sig,p,.2)
      B,_=run_scenario(c,80,40,a,th,sig,p,.1)
      independent.append(dict(protection=p["id"],
        max_coil_rise_at_dt_0_2_K=A["maximum_coil_rise_K"],
        max_coil_rise_at_dt_0_1_K=B["maximum_coil_rise_K"],
        difference_K=A["maximum_coil_rise_K"]-B["maximum_coil_rise_K"],
        relative_change_percent=100*(A["maximum_coil_rise_K"]-B["maximum_coil_rise_K"])/max(B["maximum_coil_rise_K"],1e-12)))
    summary=dict(phase="P24B - no factory thermal calibration",scenarios=len(rows),
       profiles=len(profiles),stopped=sum(x["stopped_at_200K_s"] is not None for x in rows),
       unprotected_exceed_X=sum(x["time_over_xmax_s"]>0 for x in rows if x["protection"]=="no_speaker_protection"),
       coil_rise_80_contour_crossings=sum(x["time_over_hypothetical_80K_s"]>0 for x in rows),
       max_thermal_energy_residual=max(x["maximum_thermal_energy_residual"] for x in rows),
       dt_audit=independent,
       requested_observations=[x for x in rows if x["volume_l"]==80 and x["frequency_hz"]==40 and
         x["amp"]=="NC500_RCA2" and x["thermal"]=="central_ASSUMED" and x["program"]=="sustained"],
       warnings=c["warnings"])
    (OUT/"p24b_podsumowanie.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n")
    (OUT/"p24b_manifest.json").write_text(json.dumps(dict(python=platform.python_version(),
       sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in
         [CFG,Path(__file__),OUT/"p24b_wyniki_729.csv",OUT/"p24b_profile_termiczne.csv",OUT/"p24b_podsumowanie.json"]}),
            indent=2)+"\n")
    print(json.dumps({k:v for k,v in summary.items() if k not in ("warnings","requested_observations")},indent=2))
if __name__=="__main__":main()
