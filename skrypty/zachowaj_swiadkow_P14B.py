"""Wydziel mały, samodzielny zbiór świadków z nieruszanych checkpointów."""
import hashlib
import json
from pathlib import Path
import numpy as np
from projekcja_P14B import ROOT,OUT,read_checkpoints


def main():
    ids={f'{k:06d}' for k in list(range(190,195))+list(range(220,225))+list(range(730,735))}
    rows,run_hash=read_checkpoints();selected=sorted([(r,a,d) for r,a,d in rows if r['case_id'] in ids],key=lambda a:a[0]['case_id'])
    if len(selected)!=len(ids):raise ValueError('Świadkowie jeszcze nie są zapisani')
    path=OUT/'p14b_swiadkowie_emisji.npz'
    arrays=np.stack([a for _,a,_ in selected]);texts=[json.dumps(r,ensure_ascii=False,sort_keys=True) for r,_,_ in selected]
    np.savez_compressed(path,spectrum=arrays,row_json=np.array(texts),case_id=np.array([r['case_id'] for r,_,_ in selected]))
    meta=dict(status='15_WITNESSES_FROM_PARTIAL_CAMPAIGN_NOT_FULL_RESULT',dynamic_run_sha256=run_hash,
              archive_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
              spectrum_sha256={r['case_id']:d for r,_,d in selected},
              scope='Dwie pary i pięć profili C02/100l oraz20+85Hz C06/100l,poziom1. Umowne krzywe, nie pomiary produktów.')
    (OUT/'p14b_swiadkowie_emisji.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False))
    print('Zachowano',len(selected),'niezależnych od trwających baz świadków; NPZ',path.stat().st_size,'bajtów')


if __name__=='__main__':main()
