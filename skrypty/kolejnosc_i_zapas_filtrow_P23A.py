"""Normy wyjść pośrednich12różnych kolejności4sekcji;software bez saturacji."""
from pathlib import Path
from itertools import permutations,product
import csv,json,hashlib
import numpy as np
from scipy import signal
from model_filtrow_dyskretnych_P23 import chain
from analiza_filtrow_dyskretnych_P23A import section_l1_bound

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def main():
    cfg=json.loads((ROOT/'dane/konfiguracje/p23a_filtry_dyskretne.json').read_text())
    summary=json.loads((OUT/'p23a_podsumowanie.json').read_text());case=cfg['software_time_case']
    fs=96000;sos=chain(*summary['reference_fc_q'],case['target_hz'],cfg['target_q'],
        cfg['highpass_hz_assumed'],cfg['lowpass_lr4_hz_assumed'],fs)
    section={'LT':sos[0],'HP':sos[1],'LP':sos[2]};n=fs;impulse=np.r_[1.,np.zeros(n-1)]
    reference=signal.sosfilt(sos,impulse);rows=[]
    for order in sorted(set(permutations(['LT','HP','LP','LP']))):
        full=np.array([section[t] for t in order]);values=[]
        for count in range(1,5):
            prefix=full[:count];h=signal.sosfilt(prefix,impulse)
            nlocal=(n-1)//count+1;local=[section_l1_bound(s,nlocal) for s in prefix]
            tail=sum(float(np.prod([local[k]['tail_upper_float'] if t else local[k]['finite_impulse_l1']
                for k,t in enumerate(mask)])) for mask in product([False,True],repeat=count) if any(mask))
            low=float(np.sum(abs(h)));upper=low+tail;values.append(upper)
            error=float(np.max(abs(h-reference))) if count==4 else 0.
            if count==4:assert error<2e-9
            rows.append(dict(order='-'.join(order),prefix_sections=count,prefix='-'.join(order[:count]),
                finite_l1_lower_float=low,tail_upper_float=tail,l1_upper_float=upper,
                gain_bound_db=float(20*np.log10(max(1.,upper))),same_full_transfer_impulse_absolute_error=error))
        for row in rows[-4:]:row['order_max_intermediate_gain_bound']=max(values)
    with (OUT/'p23a_kolejnosc_i_poziomy_posrednie.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    last=[r for r in rows if r['prefix_sections']==4];best=min(last,key=lambda r:r['order_max_intermediate_gain_bound'])
    worst=max(last,key=lambda r:r['order_max_intermediate_gain_bound'])
    record=dict(status='COMPLETE_SCOPED_PREFIX_L1_BOUND_ORDER_COMPARISON',sample_rate_hz=fs,
        orders=len(last),prefixes=len(rows),best_example=best,worst_example=worst,
        input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [
            Path(__file__).resolve(),ROOT/'skrypty/model_filtrow_dyskretnych_P23.py',
            ROOT/'skrypty/analiza_filtrow_dyskretnych_P23A.py',OUT/'p23a_podsumowanie.json']},
        limitations=['All section output limits assumed equal1;internal DF2T states not bounded by these port norms.',
            'Same linear transfer and zero states;actual processor block order,scaling,latency and accumulator unknown.',
            'Conservative tail inequality evaluated float,not certified interval;no optimum over arbitrary section factorisations.',
            'Best among12unique fixed-section permutations for one reference,not a hardware recommendation.'])
    (OUT/'p23a_kolejnosc_podsumowanie.json').write_text(json.dumps(record,ensure_ascii=False,indent=2,allow_nan=False))
    print('P23A prefix norms:',best['order'],best['order_max_intermediate_gain_bound'],
        'vs',worst['order'],worst['order_max_intermediate_gain_bound'])


if __name__=='__main__':main()
