"""P23A: cyfrowa LT,kwantyzacja,stabilność,faza i software SOS.

Nie zmienia żadnego DSP. Nie uruchamia starych kampanii ani ciężkich MES.
"""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from collections import Counter
import csv,hashlib,json,platform
from itertools import product
import numpy as np
import scipy
from scipy import signal
from analiza_rozszerzenia_SB import candidates
from model_subwoofera import alignment
from model_filtrow_dyskretnych_P23 import (quadratic,bilinear_second_order,chain,
    represent,schur,frequency_response,analog_response,feedback_convention,from_feedback)

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'
CFG=ROOT/'dane/konfiguracje/p23a_filtry_dyskretne.json'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def inputs():
    names=['brief_system_audio_DIY_v0.6.md','dane/przetworniki/pula_rozszerzona.json',
        'dane/przetworniki/rozszerzenie_SB_20261025.json','dane/konfiguracje/p23a_filtry_dyskretne.json',
        'skrypty/analiza_rozszerzenia_SB.py','skrypty/model_subwoofera.py',
        'skrypty/model_filtrow_dyskretnych_P23.py','skrypty/analiza_filtrow_dyskretnych_P23A.py']
    return {n:sha(ROOT/n) for n in names}


def write(name,rows):
    with (OUT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def db(x):return 20*np.log10(np.maximum(np.abs(x),1e-300))


def metrics(actual,reference,tau,reference_tau):
    ratio=actual/reference;error=db(ratio)
    return dict(max_abs_gain_error_db=float(np.max(abs(error))),
        max_abs_phase_error_deg=float(np.max(abs(np.angle(ratio)))*180/np.pi),
        max_abs_group_delay_error_ms=float(1000*np.max(abs(tau-reference_tau))))


def section_l1_bound(section,n):
    """Algebraiczny ogon pary sprzężonych biegunów;ocena float,nie interwał.

    Dla h[k>=1]=r^(k-1)*(h1*cos((k-1)theta)+d*sin((k-1)theta)).
    Stąd sum_{k>=n}|h[k]| <= hypot(h1,d)*r^(n-1)/(1-r).
    """
    b,a=section[:3],section[3:];roots=np.roots(a)
    assert np.iscomplex(roots[0]) and abs(roots[0])<1
    r=float(abs(roots[0]));theta=float(abs(np.angle(roots[0])))
    h=signal.lfilter(b,a,np.r_[1.,np.zeros(n-1)])
    h1=b[1]-a[1]*b[0];h2=b[2]-a[1]*h1-a[2]*b[0]
    d=(h2/r-h1*np.cos(theta))/np.sin(theta)
    tail=float(np.hypot(h1,d)*r**(n-1)/(1-r))
    # Dodatkowa niezależna kontrola wzoru na wybranych wyrazach impulsu.
    k=np.array([1,2,3,17,min(n-1,1000)])
    expected=r**(k-1)*(h1*np.cos((k-1)*theta)+d*np.sin((k-1)*theta))
    err=float(np.max(abs(h[k]-expected)))
    assert err<2e-8
    return dict(finite_impulse_l1=float(np.sum(abs(h))),tail_upper_float=tail,
        section_l1_upper_float=float(np.sum(abs(h))+tail),recurrence_absolute_error=err)


def time_study(cfg,reference):
    rows=[];saved={};bounds=[];case=cfg['software_time_case']
    for fs in cfg['sample_rates_hz_assumed']:
        sos=chain(*reference,case['target_hz'],cfg['target_q'],
            cfg['highpass_hz_assumed'],cfg['lowpass_lr4_hz_assumed'],fs)
        n=int(case['duration_s']*fs);t=np.arange(n)/fs;tail=int(case['last_time_s']*fs)
        tones=np.array(case['record_tones_hz']);phases=np.array([0.,.3,1.1,2.4])
        signals={'four_tone':.05*np.sin(2*np.pi*t[:,None]*tones+phases).sum(axis=1),
                 'step_from_zero':np.full(n,case['input_step_amplitude']),
                 'impulse':np.r_[1.,np.zeros(n-1)]}
        for kind,x in signals.items():
            y64=signal.sosfilt(sos,x)
            coef=represent(sos,'float32');ycoef=signal.sosfilt(coef,x)
            # Ten sam input float32 i te same współczynniki:oddziela arytmetykę stanów.
            x32=x.astype(np.float32);same64=signal.sosfilt(coef,x32.astype(float))
            y32=signal.sosfilt(coef.astype(np.float32),x32).astype(float)
            norm=max(float(np.sqrt(np.mean(y64*y64))),1e-30)
            ynorm=max(float(np.sqrt(np.mean(same64*same64))),1e-30)
            rows.append(dict(sample_rate_hz=fs,signal=kind,duration_s=case['duration_s'],
                input_peak=float(np.max(abs(x))),output64_peak=float(np.max(abs(y64))),
                coefficient_only_error_rms_relative=float(np.sqrt(np.mean((ycoef-y64)**2))/norm),
                state_arithmetic_error_rms_relative=float(np.sqrt(np.mean((y32-same64)**2))/ynorm),
                state_arithmetic_error_last_second_rms=float(np.sqrt(np.mean((y32[-tail:]-same64[-tail:])**2))),
                all_finite=bool(np.all(np.isfinite(y32)))))
            stride=max(1,fs//4000)
            saved[f'{fs}_{kind}']=np.column_stack([t[::stride],x[::stride],y64[::stride],ycoef[::stride],y32[::stride]])
        # Iloczyn l1 sekcji ogranicza l1 całej kaskady (splot).
        nimp=int(fs);local=[section_l1_bound(s,nimp) for s in sos]
        cascade=signal.sosfilt(sos,np.r_[1.,np.zeros(nimp-1)])
        # Świadek:odwrócone znaki impulsu wymuszają dokładnie sumę |h| w próbce n-1.
        witness=np.sign(cascade[::-1]).copy();wout=signal.sosfilt(sos,witness)
        lower=float(np.sum(abs(cascade)));upper=float(np.prod([r['section_l1_upper_float'] for r in local]))
        assert abs(wout[-1]-lower)<2e-7*max(lower,1.) and lower<=upper*(1+1e-10)
        # Dokładniejsza nierówność dla OGONA KASKADY. Iloczyn czterech
        # impulsów obciętych do nlocal ma stopień <=nimp-1. Poza tym
        # zakresem pozostają wyłącznie sploty zawierające co najmniej jeden
        # ogon sekcji. Sumujemy dodatnie wyrazy zamiast odejmować bliskie liczby.
        nlocal=(nimp-1)//len(sos)+1
        short=[section_l1_bound(s,nlocal) for s in sos]
        assert len(sos)*(nlocal-1)<=nimp-1
        cascade_tail=sum(float(np.prod([short[k]['tail_upper_float'] if tail else
                    short[k]['finite_impulse_l1'] for k,tail in enumerate(mask)]))
                    for mask in product([False,True],repeat=len(sos)) if any(mask))
        fwide=np.unique(np.r_[np.geomspace(.01,min(10000,fs*.49),15000),20,80])
        h,_=frequency_response(sos,fwide,fs);peak=float(np.max(abs(h)))
        bounds.append(dict(sample_rate_hz=fs,finite_cascade_l1_lower_float=lower,
            product_section_l1_upper_float=upper,sine_grid_peak_gain=peak,
            truncated_convolution_cascade_tail_upper_float=cascade_tail,
            cascade_l1_upper_float=lower+cascade_tail,
            cascade_l1_sufficient_attenuation_db_float=float(20*np.log10(max(1.,lower+cascade_tail))),
            required_attenuation_for_arbitrary_bounded_input_upper_db=float(20*np.log10(max(1.,upper))),
            constructive_finite_witness_peak=float(wout[-1]),
            section_tail_upper_float=[r['tail_upper_float'] for r in local],
            interpretation='Analytic inequality evaluated in floating point;not interval certificate or identified DSP saturation.'))
    np.savez_compressed(OUT/'p23a_czas_software.npz',**saved)
    write('p23a_czas_i_arytmetyka.csv',rows)
    return bounds


def main():
    cfg=json.loads(CFG.read_text());pool=candidates();f=np.geomspace(*cfg['band_hz'],cfg['band_points'])
    f=np.unique(np.r_[f,20.,25.,31.5,40.,63.,80.]);rows=[];sections=[];warp=[]
    reference=None
    for cid,pid,d,cat in pool:
        for vb in cfg['net_air_volumes_l_assumed']:
            fc,qc,_=alignment(d,vb)
            if cid==cfg['software_time_case']['candidate'] and vb==cfg['software_time_case']['volume_l']:reference=(fc,qc)
            for ft in cfg['lt_target_hz_assumed']:
                args=(fc,qc,ft,cfg['target_q'],cfg['highpass_hz_assumed'],cfg['lowpass_lr4_hz_assumed'])
                analog,ta=analog_response(*args,f)
                for fs in cfg['sample_rates_hz_assumed']:
                    sos=chain(*args,fs);h64,t64=frequency_response(sos,f,fs)
                    base=dict(configuration=cid,product=pid,driver_name=d.name,volume_l=vb,fc_hz=fc,qtc=qc,target_hz=ft,sample_rate_hz=fs)
                    assert np.array_equal(from_feedback(feedback_convention(sos)),sos)
                    warp.append(dict(**base,**metrics(h64,analog,t64,ta)))
                    for representation in cfg['representations']:
                        c=represent(sos,representation);verdict=[schur(s) for s in c]
                        h,tau=frequency_response(c,f,fs)
                        rows.append(dict(**base,representation=representation,
                            all_sections_strict_schur=all(r['state']=='strict' for r in verdict),
                            min_exact_jury_margin=min(r['min_margin'] for r in verdict),
                            **metrics(h,h64,tau,t64),sampled_peak_filter_gain_db=float(np.max(db(h))),
                            gain_at20hz_db=float(db(h[0])),delay_at20hz_ms=float(tau[0]*1000)))
                        for k,(csec,v) in enumerate(zip(c,verdict)):
                            sections.append(dict(**base,representation=representation,section=['LT','HP2','LP2a','LP2b'][k],
                                b0=csec[0],b1=csec[1],b2=csec[2],a1=csec[4],a2=csec[5],
                                jury_state=v['state'],min_exact_margin=v['min_margin'],
                                exact_margins=';'.join(v['exact_margins'])))
    write('p23a_kaskady_i_kwantyzacja.csv',rows);write('p23a_wspolczynniki_i_Jury.csv',sections)
    write('p23a_blad_transformacji_vs_analog.csv',warp)
    stress=[]
    for fs in cfg['sample_rates_hz_assumed']:
        for fc in cfg['stress_cutoffs_hz']:
            for q in cfg['stress_q']:
                sos=bilinear_second_order([1.,0.,0.],quadratic(fc,q),fs)[None,:]
                for rep in cfg['representations']:
                    c=represent(sos,rep)[0];v=schur(c)
                    stress.append(dict(sample_rate_hz=fs,cutoff_hz=fc,q=q,representation=rep,
                        a1=c[4],a2=c[5],jury_state=v['state'],min_exact_margin=v['min_margin'],
                        exact_margins=';'.join(v['exact_margins']),
                        numerator_dc_exact=str(sum(__import__('fractions').Fraction.from_float(float(x)) for x in c[:3]))))
    write('p23a_granice_rozdzielczosci.csv',stress)
    assert reference is not None
    bounds=time_study(cfg,reference)
    case=cfg['software_time_case'];mismatch=[]
    for design in cfg['sample_rates_hz_assumed']:
        sos=chain(*reference,case['target_hz'],cfg['target_q'],cfg['highpass_hz_assumed'],cfg['lowpass_lr4_hz_assumed'],design)
        for actual in cfg['sample_rates_hz_assumed']:
            h,t=frequency_response(sos,f,actual)
            correct=chain(*reference,case['target_hz'],cfg['target_q'],cfg['highpass_hz_assumed'],cfg['lowpass_lr4_hz_assumed'],actual)
            hc,tc=frequency_response(correct,f,actual)
            mismatch.append(dict(design_fs_hz=design,actual_fs_hz_assumed=actual,
                intended_hp_hz=cfg['highpass_hz_assumed'],
                mapped_hp_significant_hz=float(actual/np.pi*np.arctan(np.pi*cfg['highpass_hz_assumed']/design)),
                **metrics(h,hc,t,tc)))
    write('p23a_niezgodnosc_Fs.csv',mismatch)
    summary=dict(status='COMPLETE_SCOPED_DIGITAL_FILTER_FAMILIES_NOT_HARDWARE',
        generated_at=datetime.now(ZoneInfo('Europe/Warsaw')).isoformat(),input_sha256=inputs(),
        libraries=dict(Python=platform.python_version(),NumPy=np.__version__,SciPy=scipy.__version__),
        electrical_configurations=len(pool),analog_designs=len(warp),quantized_chains=len(rows),
        sections=len(sections),stress_filters=len(stress),time_cases=9,fs_mismatch_cases=len(mismatch),
        non_strict_chains=dict(Counter(r['representation'] for r in rows if not r['all_sections_strict_schur'])),
        non_strict_stress=dict(Counter(r['representation']+'_'+r['jury_state'] for r in stress if r['jury_state']!='strict')),
        max_warp_gain_error_db=max(r['max_abs_gain_error_db'] for r in warp),
        max_warp_phase_error_deg=max(r['max_abs_phase_error_deg'] for r in warp),
        max_warp_group_delay_error_ms=max(r['max_abs_group_delay_error_ms'] for r in warp),
        headroom_bounds=bounds,reference_fc_q=list(reference),
        limitations=cfg['limitations']+['l1 product is conservative and evaluated with floating-point tails;finite constructive witness retained.',
            'No output-voltage scale,driver-excursion/temperature limiter,ADC/DAC latency,hardware-state format or acoustic room phase identified.'],
        next='P23B/P24:corrected physical plant,transients and protection;P21C main chamber continues independently.')
    (OUT/'p23a_podsumowanie.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,allow_nan=False))
    print('P23A:',summary['analog_designs'],'designs;',summary['quantized_chains'],'chains;',summary['non_strict_chains'])


if __name__=='__main__':main()
