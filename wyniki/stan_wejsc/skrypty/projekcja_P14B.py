"""Niezależna warstwa emisji P14B; czyta checkpointy tylko do odczytu.

Może wykonać jawną migawkę w trakcie kampanii. Wtedy wynik NIE zamyka P14B.
Nie modyfikuje dzienników ani zamrożonych wejść integracji ODE.
"""
import csv
import hashlib
import json
from pathlib import Path
import sqlite3
import zlib
import numpy as np
from model_subwoofera import Driver
from model_nieliniowy import Plant
from model_cewki_z_pamiecia import linear_memory_response
from analiza_cewki_z_pamiecia import dynamic_network
from model_emisji_P14B import fixed_operators,moving_monopole,pressure_metrics

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'wyniki'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def read_checkpoints():
    """Szybko pobierz dane i zamknij połączenie PRZED kosztowną projekcją."""
    result=[];run_hashes=set()
    paths=sorted(OUT.glob('p14b_C*_*.sqlite3'))
    for path in paths:
        connection=sqlite3.connect(path.resolve().as_uri()+'?mode=ro',uri=True,timeout=10)
        try:
            meta=connection.execute("SELECT value FROM metadata WHERE key='run_sha256'").fetchone()
            run_hashes.add(meta[0]);stored=connection.execute('SELECT row_json,spectrum,spectrum_sha256 FROM cases ORDER BY case_id').fetchall()
        finally:connection.close()
        for row_json,blob,digest in stored:
            row=json.loads(row_json);arr=None
            if blob is not None:
                raw=zlib.decompress(blob)
                if hashlib.sha256(raw).hexdigest()!=digest:raise ValueError('Hash widma: '+row['case_id'])
                arr=np.frombuffer(raw,dtype='<c16').reshape(row['band_spectrum_shape']).copy()
                if not np.all(np.isfinite(arr)):raise ValueError('Nieskończone widmo')
            result.append((row,arr,digest))
    if len(run_hashes)!=1:raise ValueError('Wymagany jeden przebieg ODE; wybierz jawnie przy wielu rodzinach')
    if len({r['case_id'] for r,_,_ in result})!=len(result):raise ValueError('Powtórzony case_id')
    return result,run_hashes.pop()


def write_csv(path,rows):
    fields=list(dict.fromkeys(k for r in rows for k in r))
    temp=path.with_suffix('.tmp')
    with temp.open('w',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=fields);writer.writeheader();writer.writerows(rows)
    temp.replace(path)


def projected_rows(row,spectrum,plant,cfg,geometry_cfg,memory,hv):
    f=np.arange(spectrum.shape[1])*row['frequency_spacing_hz'];velocity=2j*np.pi*f*spectrum[0]
    profile={'NL_FLUX_ONE':'FLUX_ONE','NL_FLUX_TWO':'FLUX_TWO'}.get(row['profile'],'SIMPLE')
    instant,branches,_=dynamic_network(plant,profile,memory)
    linear=linear_memory_response(plant,row['volume_l'],row['frequencies_hz'],instant,branches,tau_s=cfg['tau_gas_s'])
    ids=[int(round(value/row['frequency_spacing_hz'])) for value in row['frequencies_hz']]
    volts=row['voltage_scale']*np.array(row['weights_rms'])*np.exp(1j*np.array([0.,row['phase2_rad']]))
    motion_reference=linear['velocity']/(2j*np.pi*np.array(row['frequencies_hz']))*volts
    base={k:row[k] for k in ['case_id','candidate_id','driver','volume_l','level','profile','group','initial_q','phase_class']}
    base.update(f_low_hz=row['frequencies_hz'][0],f_high_hz=row['frequencies_hz'][1],dynamic_status=row['status'],input_data_gate=row['input_data_gate'])
    base['x_product_2low_minus_high_rms_m']=float(abs(spectrum[0,int(round(abs(2*row['frequencies_hz'][0]-row['frequencies_hz'][1])/row['frequency_spacing_hz']))]))
    for k,index in enumerate(ids):
        ratio=spectrum[0,index]/motion_reference[k]
        base[f'fund{k+1}_motion_change_db']=float(20*np.log10(abs(ratio)))
        base[f'fund{k+1}_motion_phase_change_deg']=float(np.angle(ratio,deg=True))
    results=[];products=[]
    for geometry in geometry_cfg['geometry_ids']:
        diagnostic={}
        if geometry=='MOVING_MONOPOLE_AXIS':
            try:pressure,diagnostic=moving_monopole(spectrum[0],f,plant.sd,geometry_cfg)
            except (ValueError,RuntimeError) as error:
                results.append(dict(**base,geometry=geometry,projection_status='OUTSIDE_MOVING_CONTROL_DOMAIN',projection_error=str(error)));continue
        else:pressure=hv[geometry]*velocity
        metrics,lines=pressure_metrics(pressure,f,row,cfg)
        metrics['projection_status']=metrics.pop('status')
        results.append(dict(**base,geometry=geometry,**metrics,**diagnostic))
        if geometry in ('MONOPOLE_4PI','MOVING_MONOPOLE_AXIS'):
            products.extend(dict(**base,geometry=geometry,**line) for line in lines)
    return results,products


def main():
    cfg_path=ROOT/'dane/konfiguracje/p14b_IMD.json';gpath=ROOT/'dane/konfiguracje/p14b_emisja.json'
    mpath=ROOT/'dane/konfiguracje/p12c_pamiec_cewki.json';ppath=ROOT/'dane/przetworniki/pula_rozszerzona.json'
    cfg=json.loads(cfg_path.read_text());geometry_cfg=json.loads(gpath.read_text());memory=json.loads(mpath.read_text())
    pool=json.loads(ppath.read_text())['drivers'];plants={r['candidate_id']:Plant.from_driver(Driver(**r['model'])) for r in pool}
    rows,run_hash=read_checkpoints()
    raw_statuses={s:sum(r['status']==s for r,_,_ in rows) for s in sorted({r['status'] for r,_,_ in rows})}
    from rozstrzygnij_P14B import load_resolutions
    rows=load_resolutions(rows,run_hash)
    expected=len(pool)*len(cfg['volumes_l'])*len(cfg['tone_pairs_hz'])*len(cfg['levels'])*len(cfg['profiles'])
    # Dodatkowe studia dokładnie tak jak w zamrożonym koordynatorze.
    from analiza_P14B import jobs_list
    expected=len(jobs_list(pool,cfg));complete=len(rows)==expected
    inputs=[cfg_path,gpath,mpath,ppath,Path(__file__),ROOT/'skrypty/model_emisji_P14B.py',ROOT/'skrypty/model_promieniowania.py',ROOT/'skrypty/model_gazu.py']
    inputs.append(ROOT/'skrypty/rozstrzygnij_P14B.py')
    resolution_root=OUT/'p14b_rozstrzygniecia'/run_hash[:16]
    if resolution_root.exists():inputs.extend(sorted(p for p in resolution_root.iterdir() if p.suffix in ('.json','.npz')))
    hashes={str(p.relative_to(ROOT)):sha(p) for p in inputs}
    projection_hash=hashlib.sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest()
    root=OUT if complete else OUT/'archiwum'/f'P14B_migawka_{len(rows):04d}_{projection_hash[:12]}'
    root.mkdir(exist_ok=True,parents=True)
    snapshot=root/'stan_wejsc'
    for p in inputs:
        copy=snapshot/p.relative_to(ROOT);copy.parent.mkdir(parents=True,exist_ok=True)
        if not copy.exists():copy.write_bytes(p.read_bytes())
        if sha(copy)!=hashes[str(p.relative_to(ROOT))]:raise ValueError('Niezgodna migawka kodu projekcji')
    results=[];products=[];operators={}
    for k,(row,spectrum,digest) in enumerate(rows):
        if spectrum is None:continue
        key=(row['candidate_id'],row['volume_l']);plant=plants[key[0]]
        if key not in operators:
            f=np.arange(spectrum.shape[1])*row['frequency_spacing_hz']
            operators[key]=fixed_operators(plant,key[1],f,geometry_cfg)
        new,lines=projected_rows(row,spectrum,plant,cfg,geometry_cfg,memory,operators[key])
        results.extend(new);products.extend(lines)
        if (k+1)%200==0:print('ProjekcjaP14B:',k+1,'/',len(rows),flush=True)
    write_csv(root/'p14b_emisja.csv',results);write_csv(root/'p14b_fazory_produktow.csv',products)
    summary=dict(status='FULL_CHECKPOINT_SET_PROJECTED' if complete else 'PARTIAL_SNAPSHOT_NOT_FINAL_RESULT',
                 dynamic_run_sha256=run_hash,projection_sha256=projection_hash,input_sha256=hashes,
                 cases_checkpointed=len(rows),expected_cases=expected,projected_rows=len(results),product_rows=len(products),
                 raw_dynamic_status_counts=raw_statuses,resolved_cases=sum('resolution_method' in r for r,_,_ in rows),
                 dynamic_status_counts={s:sum(r['status']==s for r,_,_ in rows) for s in sorted({r['status'] for r,_,_ in rows})},
                 case_spectrum_sha256={r['case_id']:d for r,_,d in rows},
                 scope='Te same fazory ruchu; geometrie kontrolne bez nowego obciążenia zwrotnego. MOVING to odrębny model źródła, nie rzeczywisty ruchomy tłok. NOT_SETTLED wymaga osobnej interpretacji/weryfikacji.')
    (root/'p14b_projekcja.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,allow_nan=False))
    print(json.dumps({k:v for k,v in summary.items() if k not in ('input_sha256','case_spectrum_sha256')},ensure_ascii=False,indent=2))
    return summary


if __name__=='__main__':main()
