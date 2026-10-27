"""Niezależny verifier P24A:stdlib,Fraction i eliminacjaSchura,bez CVXPY.

Nie importuje kodu wyszukującego lub jego funkcji certify(). Zapisane
parametry modelu są jawnymi danymi;nie są identyfikacją realnego produktu.
"""
from pathlib import Path
from fractions import Fraction as Q
import hashlib,json

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def transpose(a):return list(map(list,zip(*a)))


def multiply(a,b):
    return [[sum((a[i][k]*b[k][j] for k in range(3)),Q(0)) for j in range(3)] for i in range(3)]


def ldl_psd(a,strict=False):
    assert a==transpose(a)
    a=[row[:] for row in a];pivots=[]
    for k in range(3):
        pivot=a[k][k];assert pivot>0 if strict else pivot>=0
        pivots.append(str(pivot))
        if pivot==0:
            assert all(a[j][k]==0 for j in range(k+1,3))
            continue
        for i in range(k+1,3):
            for j in range(k+1,3):a[i][j]-=a[i][k]*a[k][j]/pivot
    return pivots


def main():
    summary=json.loads((OUT/'p24a_podsumowanie.json').read_text());assert summary['cases']==summary['expected_cases']==972
    for n,h in summary['input_sha256'].items():assert hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==h,n
    files=sorted((ROOT/summary['checkpoint_folder']).glob('*.json'));assert len(files)==972
    accepted=0;all_psd=0;min_voltage=None;max_voltage=Q(0);trial_count=0;failures=0
    for path in files:
        r=json.loads(path.read_text());assert r['run_sha256']==summary['run_sha256'] and r['input_sha256']==summary['input_sha256']
        trial_count+=len(r['trials']);failures+=sum(not t.get('candidate_accepted',False) for t in r['trials'])
        if not r['certificate']:continue
        cert=r['certificate'];p={k:Q(v) for k,v in cert['parameters'].items()}
        assert all(v>0 for k,v in p.items() if k!='Rs') and p['Rs']>=0
        x=[[Q(v) for v in row] for row in cert['X']];ldl_psd(x,strict=True)
        assert x[0][0]<=1 and x[2][2]<=1
        lam,gamma,voltage=[Q(cert[k]) for k in ['lambda_value','gamma','source_peak_voltage_v']]
        assert lam>0 and gamma>0 and 0<voltage*voltage<=lam*gamma
        assert 0<p['Icap']<=p['Ihardware']
        assert p['Re0']*(1+p['alpha']*p['theta_limit'])*p['Icap']**2<=p['theta_limit']/p['Rth']
        # Fizyczny A konstruowany oddzielnie,skalowany przez D=diag(Xref,1,Icap).
        scales=[p['Xref'],Q(1),p['Icap']]
        for temperature in [Q(0),p['theta_limit']]:
            A=[[Q(0),Q(1),Q(0)],[-p['K']/p['M'],-p['Rms']/p['M'],p['BL']/p['M']],
                [Q(0),-p['BL']/p['Le'],-(p['Re0']*(1+p['alpha']*temperature)+p['Rs'])/p['Le']]]
            A=[[A[i][j]*scales[j]/scales[i] for j in range(3)] for i in range(3)]
            b=[Q(0),Q(0),1/(p['Le']*p['Icap'])]
            left,right=multiply(A,x),multiply(x,transpose(A))
            neg=[[-left[i][j]-right[i][j]-lam*x[i][j]-gamma*b[i]*b[j] for j in range(3)] for i in range(3)]
            ldl_psd(neg);all_psd+=1
        accepted+=1;min_voltage=voltage if min_voltage is None else min(min_voltage,voltage);max_voltage=max(max_voltage,voltage)
    assert accepted==summary['accepted']==972
    result=dict(status='VERIFIED_EXACT_RATIONAL_MODEL_CERTIFICATES_WITH_INDEPENDENT_LDL',
        cases=len(files),accepted=accepted,endpoint_LMI_checks=all_psd,positive_X_checks=accepted,
        search_trials=trial_count,rejected_search_trials=failures,
        min_source_voltage_peak_v=str(min_voltage),max_source_voltage_peak_v=str(max_voltage),
        input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__).resolve(),OUT/'p24a_podsumowanie.json']},
        limitations=['Exact rational matrix verification proves a sufficient invariant region of the declared model,not real driver parameter fidelity.',
            'No global optimisation proof:seven selected lambda and solver candidates only;rejected trial does not prove impossibility.',
            'All-temperature statement uses affine endpoint convexity,not sampling of temperature;thermal model is copper-only one-pole with Cth>0.',
            'Voltage bound concerns the continuous physical source port,not merely digital sample peaks.'])
    (OUT/'p24a_weryfikacja_dokladna_LDL.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print('P24A independent Fraction/LDL:',accepted,'certificates;',all_psd,'endpoint LMIs;all temperatures in declared interval.')


if __name__=='__main__':main()
