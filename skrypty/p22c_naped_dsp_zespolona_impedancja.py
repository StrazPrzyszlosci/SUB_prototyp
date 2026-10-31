#!/usr/bin/env python3
"""P22C — RMS/peak-consistent amplifier, DSP and sealed-driver envelope.

Run from repository root:
    python skrypty/p22c_naped_dsp_zespolona_impedancja.py
Generates full CSV, compressed CSV, JSON summary and source manifest.
No nonlinear distortion, thermal transient, room transfer or amplifier clip waveform.
"""
import csv, gzip, hashlib, json, math, platform
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / 'dane/konfiguracje/p22c_dsp_naped_impedancja_20261031.json'
OUT = ROOT / 'wyniki'

def motor(d, air):
    fs, sd = d['fs_hz'], d['sd_cm2'] * 1e-4
    cm = d['vas_l'] * .001 / (air['density_kg_m3']*air['velocity_m_s']**2*sd*sd)
    m_ts = 1 / ((2*math.pi*fs)**2*cm)
    mass = d.get('mms_g_published',m_ts*1000) / 1000
    rms = 2*math.pi*fs*mass/d['qms']
    bl_ts = math.sqrt(2*math.pi*fs*mass*d['re_ohm']/d['qes'])
    bl = d.get('bl_tm_published',bl_ts)
    return dict(sd=sd,cms=cm,m=mass,rms=rms,bl=bl,mass_rel_diff=mass/m_ts-1,
                bl_rel_diff=bl/bl_ts-1)

def one_volt(d, air, m, volume_l, f, amp):
    w = 2*math.pi*f; s=1j*w
    rho, c = air['density_kg_m3'],air['velocity_m_s']
    zair = rho*c*c / (s*(volume_l/1000))
    zm = m['rms']+s*m['m']+1/(s*m['cms'])+m['sd']**2*zair
    zs = d['re_ohm'] + amp['output_resistance_ohm'] + s*d['le_mh']*.001
    i = 1/(zs+m['bl']**2/zm)
    v = m['bl']*i/zm
    # I and x are RMS phasors for a 1V_rms sinusoidal source.
    xrms = abs(v)/w; xpk = math.sqrt(2)*xrms
    input_power=float(i.real)
    loss=(d['re_ohm']+amp['output_resistance_ohm'])*abs(i)**2+m['rms']*abs(v)**2
    error=abs(input_power-loss)/max(input_power,1e-12)
    if error>2e-11 or input_power<0:raise AssertionError(('power',d['id'],amp['id'],f,error))
    zload = d['re_ohm']+s*d['le_mh']*.001+m['bl']**2/zm
    return dict(iper=abs(i),vper=abs(v),xpkper=xpk,
         voltage_at_driver_per=abs(1-amp['output_resistance_ohm']*i),
         p1per=rho*w*m['sd']*abs(v)/(2*math.pi),
         load_z_real=zload.real,load_z_imag=zload.imag,
         power_error=error)

def case(d, air, m, volume_l, f, amp, dsp, heat_budget):
    q=one_volt(d,air,m,volume_l,f,amp)
    gain=10**(amp['gain_db']/20)
    amps={
     'dsp_full_scale':dsp['vrms_max']*gain,
     'manufacturer_nominal_4ohm_voltage_reference':math.sqrt(4*amp['rated_4ohm_W_1pct']),
     'manufacturer_peak_voltage':amp['voltage_peak_V']/math.sqrt(2)
                           if amp['voltage_peak_V'] is not None else float('inf'),
     'manufacturer_peak_current':amp['current_peak_A']/(math.sqrt(2)*q['iper']),
     'Xmax_oneway_PEAK':d['xmax_oneway_mm']*.001/q['xpkper'],
     'hypothetical_copper_I2R':math.sqrt(heat_budget/(d['re_ohm']*q['iper']**2))
    }
    reason=min(amps,key=amps.get)
    u=amps[reason]
    peak_x_mm=u*q['xpkper']*1000
    current_rms=u*q['iper']
    at_voicecoil_v=u*q['voltage_at_driver_per']
    spl=20*math.log10(q['p1per']*u/air['pressure_reference_pa'])
    return dict(driver=d['id'],box_l=volume_l,f_hz=f,amp=amp['id'],dsp=dsp['id'],
        copper_loss_budget_w=heat_budget,voltage_source_rms=u,
        terminal_voltage_rms=at_voicecoil_v,current_coil_rms=current_rms,
        current_coil_peak=current_rms*math.sqrt(2),
        nominal_input_power_W=u*u*q['iper']*q['voltage_at_driver_per'],
        copper_loss_W=d['re_ohm']*current_rms**2,
        xmax_peak_mm=peak_x_mm,
        active_limit=reason,amp_ideal_cap_vrms=amps['manufacturer_nominal_4ohm_voltage_reference'],
        amp_nominal_current_cap_vrms=amps['manufacturer_peak_current'],
        mechanical_cap_vrms=amps['Xmax_oneway_PEAK'],
        dsp_fullscale_cap_vrms=amps['dsp_full_scale'],
        notional_halfspace_spl_1m_dB=spl,
        source_power_balance_err=q['power_error'],
        load_Z_real_ohm=q['load_z_real'],load_Z_imag_ohm=q['load_z_imag'])

def main():
    c=json.loads(CFG.read_text());air=c['air']
    freqs=range(c['frequency_hz']['start'],c['frequency_hz']['stop']+1,c['frequency_hz']['step'])
    allrows=[];groups=[];stats=[];checks=[]
    for d in c['drivers']:
      m=motor(d,air);checks.append(dict(driver=d['id'],mms_rel_diff=m['mass_rel_diff'],
                                   bl_rel_diff=m['bl_rel_diff']))
      if abs(m['mass_rel_diff'])>.08 or abs(m['bl_rel_diff'])>.2:
        raise AssertionError(('inconsistent T/S',d['id'],m))
      for volume in c['box_volumes_net_l']:
       for amp in c['amps']:
        for dsp in c['dsp']:
         for heat in c['hypothetical_voice_coil_copper_loss_budgets_w']:
          selection=[]
          for freq in freqs:
           row=case(d,air,m,volume,freq,amp,dsp,heat)
           allrows.append(row);selection.append(row)
          selected=[next(x for x in selection if x['f_hz']==freq) for freq in [20,40,80]]
          groups.append(dict(driver=d['id'],box_l=volume,amp=amp['id'],dsp=dsp['id'],
            coil_budget_w=heat,
            active_limit_counts={name:sum(row['active_limit']==name for row in selection)
                                 for name in ['dsp_full_scale','manufacturer_nominal_4ohm_voltage_reference',
                                              'manufacturer_peak_voltage','manufacturer_peak_current',
                                              'Xmax_oneway_PEAK','hypothetical_copper_I2R']},
            min_ideal_spl_1m_db=min(x['notional_halfspace_spl_1m_dB'] for x in selection),
            max_ideal_spl_1m_db=max(x['notional_halfspace_spl_1m_dB'] for x in selection),
            witnesses=[{k:r[k] for k in ['f_hz','active_limit','voltage_source_rms',
              'current_coil_peak','xmax_peak_mm','copper_loss_W',
              'notional_halfspace_spl_1m_dB']} for r in selected]))
    OUT.mkdir(exist_ok=True)
    raw=OUT/'p22c_pelna_kampania.csv.gz'
    with gzip.open(raw,'wt',encoding='utf-8',newline='') as h:
      writer=csv.DictWriter(h,fieldnames=list(allrows[0]))
      writer.writeheader();writer.writerows(allrows)
    summary=dict(date=c['date'],model='linear_0D_harmonic_1Vrms_transfer_scaled_to_limit',
      n_rows=len(allrows),n_groups=len(groups),max_power_balance_err=max(x['source_power_balance_err'] for x in allrows),
      assumptions=c['notes'],ts_consistency=checks,groups=groups,
      caution='Mechanical xpk=√2*xrms; 4Ω 1kHz 1% power is not continuous wattage nor clean SPL; no BL(x), thermal RC, room or multitone DSP protection. Manufacturer peak current limit modeled as sine Ipeak, not hardware protection waveform.')
    (OUT/'p22c_podsumowanie.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    (OUT/'p22c_manifest.json').write_text(json.dumps(dict(python=platform.python_version(),
       sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
          for p in (CFG,Path(__file__),raw,OUT/'p22c_podsumowanie.json')}),indent=2)+'\n')
    print(json.dumps(dict(n_rows=len(allrows),n_groups=len(groups),
             max_power_balance_err=summary['max_power_balance_err'],
             checks=checks),indent=2))
if __name__=='__main__':main()
