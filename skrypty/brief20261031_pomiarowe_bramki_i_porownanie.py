#!/usr/bin/env python3
"""Conditional first-pass sealed-box T/S driver and DSP/amplifier constraints.

No inferred THD/IMD, compression, coil temperature, room SPL or final limiter.
Full 26 historical entries + all newly producer-verified entries are considered.
RMS harmonic electrical quantities and on-axis HALF-SPACE POINT SOURCE model.
Output: wyniki/brief20261031_przeglad_modeli.csv,
wyniki/brief20261031_akustyka_moc.csv, wyniki/brief20261031_dsp_wzmacniacze.csv
"""
import csv,cmath,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];O=ROOT/'wyniki'
REG=ROOT/'dane/karty_producentow/2026-10-31_9_marek_weryfikacja.json'
BRIEF=ROOT/'dane/konfiguracje/brief_klienta_20261031_wzmacniacz_dsp.json'
OLD=ROOT/'dane/przetworniki/pula_rozszerzona.json'
RHO=1.2;SOUND=343.;PREF=2e-5

def load():
    known=json.loads(REG.read_text())['models']
    brief=json.loads(BRIEF.read_text());old=json.loads(OLD.read_text())['drivers']
    pool=[dict(model=x['model']['name'],brand='original_26',verification='existing_research_collection',
               t=x['model']) for x in old]
    pool.append(dict(model='Dayton RSS390HF-4 (brief)',brand='Dayton Audio',
        verification='client_brief_need_independent_maker_check',
        t=brief['reference_driver']['parameters_from_client_brief']))
    for z in known:
        pool.append(dict(model=z['model'],brand=z['brand'],
           verification=z['documentation_status'],t=z['spec'],url=z['official_product_url']))
    return pool,brief

def get(t,k,a=None):
    return t.get(k,t.get(a)) if a else t.get(k)

def build(t):
    try:
        fs=float(t['fs_hz']);vas=float(t['vas_l'])/1000;sd=float(t['sd_cm2'])/10000
        qms=float(t['qms']);qes=float(t['qes']);re=float(t['re_ohm'])
    except (TypeError,KeyError,ValueError):return None
    if min(fs,vas,sd,qms,qes,re)<=0:return None
    cms=vas/(RHO*SOUND**2*sd**2)
    m_by_tsp=1/((2*math.pi*fs)**2*cms)
    m_pub=get(t,'mms_g');mass=float(m_pub)/1000 if m_pub else m_by_tsp
    # Mmd field is intentionally NOT treated as Mms.
    omega=2*math.pi*fs
    rms=omega*mass/qms
    bl_pub=get(t,'bl_tm')
    bl= float(bl_pub) if bl_pub is not None else math.sqrt(omega*mass*re/qes)
    bl_equiv=math.sqrt(omega*mass*re/qes)
    return dict(sd=sd,cms=cms,mms=mass,rms=rms,bl=bl,fs=fs,re=re,
        le=float(get(t,'le_mh', 'le_mh_at_1khz') or 0)/1000,
        xmax=float(get(t,'xmax_one_way_mm','xmax_mm'))/1000 if
             get(t,'xmax_one_way_mm','xmax_mm') is not None else None,
        nominal_power=float(t['power_w']) if t.get('power_w') else None,
        missing_bl=bl_pub is None,mass_inferred=m_pub is None,
        bl_qes_discrepancy=bl/bl_equiv-1,
        mass_ts_discrepancy=mass/m_by_tsp-1)

def response(m,vb,f):
    omega=2*math.pi*f;s=1j*omega
    # air pressure stiffness is acting on the motor; no double radiation mass
    gas=(RHO*SOUND**2)/(s*(vb/1000))
    zm=m['rms']+s*m['mms']+1/(s*m['cms'])+m['sd']**2*gas
    ze=m['re']+s*m['le']
    i=1/(ze+m['bl']**2/zm)
    v=m['bl']*i/zm
    x=abs(v)/omega
    real_input=float(i.real)
    # RMS current and RMS membrane velocity; acoustic 2pi pressure is RMS.
    return dict(i=abs(i),v=abs(v),x=x,
       p1=float(RHO*omega*m['sd']*abs(v)/(2*math.pi)),
       thermal_rms_w=float(m['re']*abs(i)**2),
       input_active_w=real_input)

def vo_max(a,vin):
    gain=a.get('typ_gain_db');limit=a.get('rated_output_w_4ohm_1pct_thdn')
    if gain is None or limit is None:return None
    # Resistor equivalent at 4ohm only; this is a nominal voltage cap,
    # NEVER the full real load / frequency-dependent clipping model.
    return min(vin*10**(gain/20),math.sqrt(4*limit))

def main():
    O.mkdir(exist_ok=True)
    drivers,brief=load()
    overview=[];sweep=[];dsp=[]
    for a in brief['amplifier_variants']:
        for d in brief['dsp']:
            for connector,level in [('RCA',d['max_output_rca_vrms']),
                 ('TRS_balanced',d['max_output_balanced_vrms'])]:
                if level is None:continue
                for vi in [1.,2.,4.]:
                    if vi>level: continue
                    vmax=vo_max(a,vi)
                    dsp.append(dict(amplifier=a['name'],dsp=d['name'],connector=connector,
                         input_vrms=vi,output_vrms_resistive=vmax,
                         nominal_4ohm_power_w=(vmax*vmax/4) if vmax is not None else None,
                         declared_amp_limit_w=a.get('rated_output_w_4ohm_1pct_thdn'),
                         verification='voltage-gain nominal resistor only, time limited'))
    for obj in drivers:
        t=obj['t']; model=build(t)
        key=obj['brand']+' / '+obj['model']
        if model is None:
            overview.append(dict(model=key,source_status=obj['verification'],
                analysable=False,reason='Missing producer-verified T/S',vd_cm3=None))
            continue
        x=model['xmax'];vd=x*model['sd']*1e6 if x else None
        issue=[]
        if abs(model['mass_ts_discrepancy'])>.08:issue.append('Mms does not agree Fs+Vas at default rho/c')
        if abs(model['bl_qes_discrepancy'])>.20:issue.append('BL differs from Qes-derived value')
        if model['missing_bl']:issue.append('BL inferred from Qes, not manufacturer')
        if model['mass_inferred']:issue.append('Mms inferred Fs+Vas, not manufacturer')
        if x is None:issue.append('One-way Xmax unverified; SPL clean envelope NOT calculated')
        full_screen=(x is not None and vd>=700 and
                      model['nominal_power'] is not None and model['nominal_power']>=250)
        overview.append(dict(model=key,source_status=obj['verification'],analysable=True,
            nominal_impedance_ohm=t.get('nominal_impedance_ohm',t.get('nominal_ohm')),
            fs_hz=model['fs'],vas_l=t['vas_l'],sd_cm2=t['sd_cm2'],
            xmax_oneway_mm=x*1000 if x else None,vd_cm3=vd,
            recommended_screen=full_screen,mms_kg=model['mms'],
            mass_rel_error=model['mass_ts_discrepancy'],
            bl_rel_error=model['bl_qes_discrepancy'],
            qualifiers='; '.join(issue)))
        # All drivers over the same 75–150L objective scenarios, 10–120Hz.
        for vb in brief['sealed_volume_scenarios_l']:
            for f in range(10,121):
                q=response(model,vb,f)
                mech_v=x/q['x'] if x is not None else None
                # Thermal reference here is COIL I² Re only, using 100/300/500 W
                # scenarios, not a manufacturer's AES/IEC power equivalence.
                for heat_reference in [100,300,500]:
                    heat_v=math.sqrt(heat_reference/q['thermal_rms_w'])
                    for p_amp in [250,300,400,500,700]:
                        amp_v=math.sqrt(4*p_amp)
                        vmax=min(mech_v,heat_v,amp_v) if mech_v is not None else None
                        if vmax is None:
                            spl=None;mechanical_limited=None
                        else:
                            spl=20*math.log10(q['p1']*vmax/PREF)
                            mechanical_limited=mech_v<=min(heat_v,amp_v)
                        sweep.append(dict(model=key,volume_l=vb,frequency_hz=f,
                            coil_reference_w=heat_reference,
                            nominal_amp_4ohm_w=p_amp,
                            mech_limit_vrms=mech_v,heat_limit_vrms=heat_v,
                            amp_voltage_cap_vrms=amp_v,
                            selected_voltage_vrms=vmax,
                            model_freefield_halfspace_spl_db_1m=spl,
                            mechanical_limited=mechanical_limited,
                            coil_current_Arms=q['i']*vmax if vmax else None,
                            coil_power_w=q['thermal_rms_w']*vmax**2 if vmax else None,
                            active_input_w=q['input_active_w']*vmax**2 if vmax else None))
    for filename,rows in [
         ('brief20261031_przeglad_modeli.csv',overview),
         ('brief20261031_akustyka_moc.csv',sweep),
         ('brief20261031_dsp_wzmacniacze.csv',dsp)]:
        keys=list(dict.fromkeys(k for row in rows for k in row))
        with (O/filename).open('w',newline='') as h:
            w=csv.DictWriter(h,fieldnames=keys);w.writeheader();w.writerows(rows)
    summary=dict(drivers_total=len(drivers),drivers_analysable=sum(x['analysable'] for x in overview),
        new_manufacturer_models=9,complete_sweep_rows=len(sweep),
        electrical_match_rows=len(dsp),errors=[x for x in overview
             if x.get('qualifiers') and ('does not agree' in x['qualifiers'] or 'differs' in x['qualifiers'])],
        status='Simulated 0D linear, half-space 1 m pressure ONLY. Not full room SPL, THD, thermal time course or certified limiter')
    (O/'brief20261031_podsumowanie.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='errors'},indent=2))
if __name__=='__main__':main()
