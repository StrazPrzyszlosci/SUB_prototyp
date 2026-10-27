"""972rodziny:wyszukaj LMI,przyjmij wyłącznie dokładny racjonalny świadek.

Odtworzenie świadków nie jest niezależnym ponownym rozwiązaniem SDP.
Weryfikator jest osobnym skryptem bez CVXPY i nie ufa statusowi solvera.
"""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from itertools import product
from fractions import Fraction as F
import csv,fcntl,hashlib,json,os,platform,time
import numpy as np
import cvxpy,clarabel
from analiza_rozszerzenia_SB import candidates
from model_subwoofera import RHO,C
from certyfikat_przedzialu_P24 import frac,lower_sqrt,certify
from szukaj_swiadka_LMI_P24 import find

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki';CFG=ROOT/'dane/konfiguracje/p24a_wspolny_obszar_niezmienniczy.json'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def inputs():
    names=['brief_system_audio_DIY_v0.6.md','dane/konfiguracje/p24a_wspolny_obszar_niezmienniczy.json',
        'dane/przetworniki/pula_rozszerzona.json','dane/przetworniki/rozszerzenie_SB_20261025.json',
        'skrypty/model_subwoofera.py','skrypty/analiza_rozszerzenia_SB.py','requirements_p24.txt',
        'skrypty/certyfikat_przedzialu_P24.py','skrypty/szukaj_swiadka_LMI_P24.py','skrypty/analiza_obszarow_P24A.py']
    return {n:sha(ROOT/n) for n in names}


def atomic(path,value):
    tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False));os.replace(tmp,path)


def main():
    cfg=json.loads(CFG.read_text());frozen=inputs();run=hashlib.sha256(json.dumps(frozen,sort_keys=True).encode()).hexdigest()
    folder=OUT/'p24a_przypadki'/run[:16];folder.mkdir(parents=True,exist_ok=True)
    locks=ROOT/'.p24a_locks';locks.mkdir(exist_ok=True)
    lock=(locks/(run[:16]+'.lock')).open('a+')
    try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError:raise RuntimeError('The same P24A campaign is active;do not start another copy.')
    started=time.monotonic();records=[];fresh=0
    combinations=list(product(cfg['volumes_l'],cfg['thermal_resistance_k_w_assumed'],cfg['temperature_rise_limit_k_assumed'],cfg['catalog_x_reference_fraction']))
    expected=27*len(combinations)
    for cid,pid,d,cat in candidates():
        for volume,rth,theta,xfrac in combinations:
            key=f'{cid}_V{volume:g}_Rth{rth:g}_T{theta:g}_X{xfrac:g}';path=folder/(key+'.json')
            if path.exists():
                record=json.loads(path.read_text());assert record['run_sha256']==run and record['input_sha256']==frozen
                if record['certificate']:
                    cert=record['certificate'];certify(cert['parameters'],cert['X'],cert['lambda_value'],cert['gamma'],cert['source_peak_voltage_v'])
            else:
                K=1/d.cms+RHO*C*C*d.sd*d.sd/(volume*.001)
                params={k:str(float(v)) for k,v in dict(M=d.mms,K=K,Le=d.le_mh*.001,BL=d.bl,Rms=d.rms,Re0=d.re_ohm,
                    Rs=cfg['series_source_R_ohm_assumed'],Ihardware=cfg['hardware_peak_current_a_assumed'],
                    Rth=rth,alpha=cfg['alpha_resistance_per_k_assumed'],theta_limit=theta).items()}
                params['Xref']=str(frac(d.xmax_mm)*F(1,1000)*frac(xfrac))
                current_square=frac(theta)/(frac(rth)*frac(d.re_ohm)*(1+frac(params['alpha'])*frac(theta)))
                params['Icap']=str(lower_sqrt(min(current_square,frac(params['Ihardware'])**2),6))
                cert,trials=find(params,cfg['lambda_search_fractions'])
                record=dict(case_id=key,configuration=cid,product=pid,driver_name=d.name,volume_l=volume,
                    Rth_assumed_k_w=rth,temperature_rise_limit_k=theta,X_catalog_reference_fraction=xfrac,
                    run_sha256=run,input_sha256=frozen,certificate=cert,trials=trials,
                    status='EXACT_RATIONAL_WITNESS_ACCEPTED' if cert else 'NO_WITNESS_FOUND_IN_SELECTED_SEARCH_NOT_IMPOSSIBILITY')
                atomic(path,record);fresh+=1
            records.append(record)
            if len(records)%27==0:
                print('P24A progress',len(records),'/',expected,'accepted',sum(r['certificate'] is not None for r in records),flush=True)
                summary=dict(status='PARTIAL_ACTIVE_DO_NOT_CLAIM_ALL_CASES',cases=len(records),expected_cases=expected,
                    accepted=sum(r['certificate'] is not None for r in records),run_sha256=run,input_sha256=frozen,checkpoint_folder=str(folder.relative_to(ROOT)))
                atomic(OUT/'p24a_podsumowanie.json',summary)
    assert inputs()==frozen
    rows=[]
    for r in records:
        cert=r['certificate'];rows.append(dict(case_id=r['case_id'],configuration=r['configuration'],driver_name=r['driver_name'],
            volume_l=r['volume_l'],Rth_assumed_k_w=r['Rth_assumed_k_w'],temperature_rise_limit_k=r['temperature_rise_limit_k'],
            X_catalog_reference_fraction=r['X_catalog_reference_fraction'],status=r['status'],
            source_peak_voltage_v=float(frac(cert['source_peak_voltage_v'])) if cert else '',
            current_peak_bound_a=float(frac(cert['parameters']['Icap'])) if cert else '',
            X_reference_mm=float(frac(cert['parameters']['Xref'])*1000) if cert else '',
            lambda_value_per_s=float(frac(cert['lambda_value'])) if cert else '',
            trial_count=len(r['trials']),accepted_lambda_witnesses=sum(v.get('candidate_accepted',False) for v in r['trials'])))
    with (OUT/'p24a_obszary_i_poziomy.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    summary=dict(status='COMPLETE_SCOPED_SEARCH_AND_EXACT_WITNESSES_NOT_PHYSICAL_DEVICE',
        generated_at=datetime.now(ZoneInfo('Europe/Warsaw')).isoformat(),cases=len(records),expected_cases=expected,
        accepted=sum(r['certificate'] is not None for r in records),without_witness=sum(r['certificate'] is None for r in records),
        fresh_solver_cases=fresh,run_sha256=run,input_sha256=frozen,checkpoint_folder=str(folder.relative_to(ROOT)),
        wall_time_s=time.monotonic()-started,libraries=dict(Python=platform.python_version(),NumPy=np.__version__,CVXPY=cvxpy.__version__,Clarabel=clarabel.__version__),
        limitations=cfg['limitations'],next='Independent rational verification,continuous coupled thermal trajectories and conservative performance cost;not hardware deployment.')
    atomic(OUT/'p24a_podsumowanie.json',summary)
    print('P24A completed',len(records),'accepted',summary['accepted'],'fresh',fresh,flush=True)


if __name__=='__main__':main()
