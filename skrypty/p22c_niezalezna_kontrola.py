#!/usr/bin/env python3
"""P22C independent formula audit (no import of main P22C solver).
Run: python skrypty/p22c_niezalezna_kontrola.py
Checks power passivity and no Xmax/Ipeak/I²Re overlimit on 99900 scenarios.
"""
import cmath,json,math
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
C=json.loads((ROOT/'dane/konfiguracje/p22c_dsp_naped_impedancja_20261031.json').read_text())

def run():
    rho,cs=C['air']['density_kg_m3'],C['air']['velocity_m_s']
    count=0;maximum_err=0;active=Counter();witness={}
    for d in C['drivers']:
      fs,sd=d['fs_hz'],d['sd_cm2']/10000
      cm=d['vas_l']/1000/(rho*cs**2*sd**2)
      mass=d.get('mms_g_published',1000/((2*math.pi*fs)**2*cm))/1000
      bl=d.get('bl_tm_published',math.sqrt(2*math.pi*fs*mass*d['re_ohm']/d['qes']))
      rm=2*math.pi*fs*mass/d['qms']
      for vb in C['box_volumes_net_l']:
        for amp in C['amps']:
          for dsp in C['dsp']:
            for heat in C['hypothetical_voice_coil_copper_loss_budgets_w']:
              for freq in range(10,121):
                w=2*math.pi*freq
                Zmech=complex(rm,w*mass-1/(w*cm)-sd**2*rho*cs**2/(w*vb/1000))
                Zload=complex(d['re_ohm'],w*d['le_mh']/1000)+bl*bl/Zmech
                current=1/(Zload+amp['output_resistance_ohm'])
                vel=bl*current/Zmech
                i=abs(current);x_rms=abs(vel)/w
                possible={
                  'dsp_full_scale':dsp['vrms_max']*10**(amp['gain_db']/20),
                  'manufacturer_nominal_4ohm_voltage_reference':math.sqrt(4*amp['rated_4ohm_W_1pct']),
                  'manufacturer_peak_voltage':amp['voltage_peak_V']/math.sqrt(2) if amp['voltage_peak_V'] is not None else math.inf,
                  'manufacturer_peak_current':amp['current_peak_A']/math.sqrt(2)/i,
                  'Xmax_oneway_PEAK':d['xmax_oneway_mm']/1000/(math.sqrt(2)*x_rms),
                  'hypothetical_copper_I2R':math.sqrt(heat/d['re_ohm'])/i}
                stop=min(possible,key=possible.get);u=possible[stop]
                active[stop]+=1;count+=1
                err=abs(current.real-((d['re_ohm']+amp['output_resistance_ohm'])*i*i+rm*abs(vel)**2))/max(current.real,1e-14)
                maximum_err=max(maximum_err,err)
                assert err<2e-11
                assert u*math.sqrt(2)*x_rms<=d['xmax_oneway_mm']/1000*(1+1e-12)
                assert u*math.sqrt(2)*i<=amp['current_peak_A']*(1+1e-12)
                assert d['re_ohm']*(i*u)**2<=heat*(1+1e-12)
                if d['id']=='C02' and vb==80 and amp['id']=='NC500MP' and heat==250 and freq in (20,40,80) and dsp['id'] in ('eight_rca','htx_trs'):
                    witness[f"{dsp['id']}:{freq}"]=u
    assert count==99900
    expected={'eight_rca:20':32.612877,'eight_rca:40':37.672982,'eight_rca:80':31.769578,
              'htx_trs:20':32.612877,'htx_trs:40':43.472176,'htx_trs:80':31.769578}
    for key,value in expected.items():assert abs(witness[key]-value)<2e-5,(key,witness[key],value)
    print(json.dumps({'executed':count,'maximum_balance_residual':maximum_err,
                      'limit_counts':dict(active),'tested_witnesses':witness},indent=2))
if __name__=='__main__':run()
