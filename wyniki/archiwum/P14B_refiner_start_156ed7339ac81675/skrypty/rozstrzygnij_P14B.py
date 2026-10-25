"""Odrębne przeliczenia flag P14B; zachowują pierwotne checkpointySQLite."""
from concurrent.futures import ProcessPoolExecutor,as_completed
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from analiza_P14B import create_model
from model_wymuszen_P14B import integrate_forcing
from sygnaly_P14 import TonePair
from projekcja_P14B import read_checkpoints,ROOT,OUT


def refinement_job(job):
    row,entry,cfg,memory,method=job
    model=create_model(entry,row['volume_l'],row['profile'],cfg,memory)
    pair=TonePair(tuple(row['frequencies_hz']),tuple(row['weights_rms']),(0.,row['phase2_rad']))
    result,spectrum=integrate_forcing(model,pair,row['voltage_scale'],cfg,method=method,initial_q=row['initial_q'],refine=True)
    return row,result,spectrum


def load_resolutions(rows,run_hash):
    """Przyjmij wyłącznie jawny, zgodny rekord ze spełnionym kryterium."""
    root=OUT/'p14b_rozstrzygniecia'/run_hash[:16];merged=[]
    for row,arr,digest in rows:
        path=root/(row['case_id']+'.json')
        if path.exists():
            resolution=json.loads(path.read_text())
            if resolution['raw_spectrum_sha256']!=digest or resolution['dynamic_run_sha256']!=run_hash:
                raise ValueError('Rozstrzygnięcie nie należy do tego surowego przypadku')
            if resolution['result']['status']=='PERIODIC_WITHIN_MODEL_TOLERANCE':
                target=root/resolution['spectrum_file']
                if hashlib.sha256(target.read_bytes()).hexdigest()!=resolution['spectrum_file_sha256']:
                    raise ValueError('Hash widma rozstrzygnięcia')
                arr=np.load(target,allow_pickle=False)['spectrum']
                if list(arr.shape)!=resolution['result']['band_spectrum_shape'] or not np.all(np.isfinite(arr)):
                    raise ValueError('Niepoprawny wymiar/wartości widma rozstrzygnięcia')
                row={**row,'raw_status':row['status'],'resolution_method':resolution['method'],**resolution['result']}
                # Pochodne wskaźniki nie mogą zachować szczytu z poprzedniego solvera.
                from model_subwoofera import Driver
                from model_nieliniowy import Plant
                entries=json.loads((ROOT/'dane/przetworniki/pula_rozszerzona.json').read_text())['drivers']
                entry=next(r for r in entries if r['candidate_id']==row['candidate_id'])
                p=Plant.from_driver(Driver(**entry['model']))
                cfg=json.loads((ROOT/'dane/konfiguracje/p14b_IMD.json').read_text())
                row['steady_catalog_x_fraction']=row['x_peak_sampled_m']/p.xref
                row['startup_catalog_x_fraction']=row['startup_x_observed_m']/p.xref
                row['current_rms_to_reference_budget']=row['current_rms_a']/cfg['amp_arms']
                digest=hashlib.sha256(np.ascontiguousarray(arr,dtype='<c16').tobytes()).hexdigest()
        merged.append((row,arr,digest))
    return merged


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--method',default='DOP853',choices=['DOP853','Radau'])
    parser.add_argument('--limit',type=int,default=0);parser.add_argument('--case',action='append',default=[])
    parser.add_argument('--workers',type=int,default=2);args=parser.parse_args()
    rows,run_hash=read_checkpoints();cfg=json.loads((ROOT/'dane/konfiguracje/p14b_IMD.json').read_text())
    snapshot=OUT/'archiwum'/f'P14B_start_{run_hash[:16]}'/'stan_wejsc'
    for original in snapshot.rglob('*'):
        if original.is_file():
            current=ROOT/original.relative_to(snapshot)
            if hashlib.sha256(original.read_bytes()).digest()!=hashlib.sha256(current.read_bytes()).digest():
                raise ValueError('Kod/wejścia ODE zmieniły się względem zamrożonego przebiegu')
    memory=json.loads((ROOT/'dane/konfiguracje/p12c_pamiec_cewki.json').read_text())
    pool={r['candidate_id']:r for r in json.loads((ROOT/'dane/przetworniki/pula_rozszerzona.json').read_text())['drivers']}
    target=OUT/'p14b_rozstrzygniecia'/run_hash[:16];target.mkdir(parents=True,exist_ok=True)
    jobs=[]
    for row,arr,digest in rows:
        if args.case and row['case_id'] not in args.case:continue
        if not args.case and row['status']!='NOT_SETTLED':continue
        path=target/(row['case_id']+'.json')
        if path.exists() and json.loads(path.read_text())['result']['status']=='PERIODIC_WITHIN_MODEL_TOLERANCE':continue
        jobs.append((row,digest))
    if args.limit:jobs=jobs[:args.limit]
    print('P14B rozstrzygnięcia:',len(jobs),args.method,flush=True)
    input_sha=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    archived=OUT/'archiwum'/f'P14B_refiner_start_{input_sha[:16]}'/'skrypty/rozstrzygnij_P14B.py'
    archived.parent.mkdir(parents=True,exist_ok=True)
    if not archived.exists():archived.write_bytes(Path(__file__).read_bytes())
    assert hashlib.sha256(archived.read_bytes()).hexdigest()==input_sha
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures={executor.submit(refinement_job,(r,pool[r['candidate_id']],cfg,memory,args.method)):digest for r,digest in jobs}
        for future in as_completed(futures):
            row,result,arr=future.result();file=None;digest=None
            if arr is not None:
                file=row['case_id']+'.npz';np.savez_compressed(target/file,spectrum=arr)
                digest=hashlib.sha256((target/file).read_bytes()).hexdigest()
            record=dict(dynamic_run_sha256=run_hash,raw_case_id=row['case_id'],raw_status=row['status'],
                        raw_spectrum_sha256=futures[future],method=args.method,refinement=True,
                        refinement_script_sha256=input_sha,result=result,spectrum_file=file,spectrum_file_sha256=digest)
            tmp=target/(row['case_id']+'.tmp');tmp.write_text(json.dumps(record,indent=2,ensure_ascii=False,allow_nan=False));tmp.replace(target/(row['case_id']+'.json'))
            print(row['case_id'],row['candidate_id'],result['status'],result.get('closure_error'),flush=True)


if __name__=='__main__':main()
