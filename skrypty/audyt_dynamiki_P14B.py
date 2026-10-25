"""Weryfikacja zapisanych fazorów P14B odrębnym wzorcem częstotliwościowym."""
import hashlib
import json
from pathlib import Path
import numpy as np
from projekcja_P14B import read_checkpoints,ROOT,OUT
from model_subwoofera import Driver
from model_nieliniowy import Plant
from model_cewki_z_pamiecia import linear_memory_response


def main():
    rows,run_hash=read_checkpoints()
    entries=json.loads((ROOT/'dane/przetworniki/pula_rozszerzona.json').read_text())['drivers']
    plants={r['candidate_id']:Plant.from_driver(Driver(**r['model'])) for r in entries}
    cfg=json.loads((ROOT/'dane/konfiguracje/p14b_IMD.json').read_text())
    linear=[];voltage_errors=[];parseval=[];hash_count=0
    for row,arr,digest in rows:
        if arr is None:continue
        hash_count+=1
        voltage_errors.append(abs(row['mean_voltage_identity_error_v']));parseval.append(row['current_Parseval_relative_error'])
        if row['profile']!='LINEAR':continue
        p=plants[row['candidate_id']];freq=np.array(row['frequencies_hz'],float)
        oracle=linear_memory_response(p,row['volume_l'],freq,p.le0,[],tau_s=cfg['tau_gas_s'])
        volts=row['voltage_scale']*np.array(row['weights_rms'])*np.exp(1j*np.array([0.,row['phase2_rad']]))
        expected=np.array([oracle['velocity']/(2j*np.pi*freq)*volts,oracle['current']*volts])
        ids=np.rint(freq/row['frequency_spacing_hz']).astype(int);actual=arr[:,ids]
        errors=abs(actual-expected)/np.maximum(abs(expected),1e-30)
        linear.append(dict(case_id=row['case_id'],candidate_id=row['candidate_id'],dynamic_status=row['status'],
                           max_X_complex_relative_error=float(max(errors[0])),max_I_complex_relative_error=float(max(errors[1]))))
    result=dict(status='PARTIAL_CHECKPOINT_AUDIT' if len(rows)<3312 else 'FULL_CHECKPOINT_AUDIT',
                dynamic_run_sha256=run_hash,cases_seen=len(rows),spectrum_hashes_checked=hash_count,linear_cases=len(linear),
                max_X_complex_relative_error=max(r['max_X_complex_relative_error'] for r in linear),
                max_I_complex_relative_error=max(r['max_I_complex_relative_error'] for r in linear),
                max_mean_voltage_identity_error_v=max(voltage_errors),max_current_Parseval_relative_error=max(parseval),
                linear_details=linear,scope='Fazor podstawowy kontra niezależna algebra LTI. To weryfikacja numeryczna warunkowego modelu, nie walidacja urządzenia.')
    assert result['max_X_complex_relative_error']<2e-7
    assert result['max_I_complex_relative_error']<2e-7
    assert result['max_mean_voltage_identity_error_v']<1e-5
    assert result['max_current_Parseval_relative_error']<1e-12
    target=OUT/'archiwum'/f'P14B_audyt_{len(rows):04d}_{run_hash[:12]}';target.mkdir(exist_ok=True,parents=True)
    result['audit_script_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (target/'p14b_audyt.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False))
    print(json.dumps({k:v for k,v in result.items() if k!='linear_details'},indent=2,ensure_ascii=False));return result


if __name__=='__main__':main()
