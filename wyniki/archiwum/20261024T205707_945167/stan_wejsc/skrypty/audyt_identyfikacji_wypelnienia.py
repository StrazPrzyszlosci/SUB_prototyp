"""P09: co można odróżnić z impedancji w paśmie20–80Hz?"""
import csv
from dataclasses import replace
import json
from pathlib import Path
import numpy as np
from model_subwoofera import Driver
from model_gazu import Medium,ThermalSpectrum,gas_response

ROOT=Path(__file__).resolve().parents[1]


def main():
    raw=json.loads((ROOT/'dane/przetworniki/pula_rozszerzona.json').read_text())['drivers']
    frequencies=np.array([20.,25.,31.5,40.,63.,80.])
    medium=Medium();rows=[];max_gauge=0.
    for r in raw:
        d=Driver(**r['model'])
        for tau in [1e-7,.0005,.005,.05,.5,100.]:
            for leak in [.001,1.,3.]:
                nominal=np.log([100.,tau,leak,.5*d.rms])
                def impedance(theta):
                    v,t,g,extra=np.exp(theta)
                    out=gas_response(d,v,frequencies,ThermalSpectrum((t,),(1.,)),medium,g,extra_r_n_s_m=extra)
                    return 1/out['current_complex_a']
                z=impedance(nominal)
                matrices=[]
                for step in [1e-4,1e-5]:
                    columns=[]
                    for i in range(4):
                        a=nominal.copy();b=nominal.copy();a[i]+=step;b[i]-=step
                        derivative=(impedance(a)-impedance(b))/(2*step)/abs(z)
                        columns.append(np.concatenate([derivative.real,derivative.imag]))
                    matrices.append(np.stack(columns,axis=1))
                jac=matrices[-1]
                single=jac[[0,len(frequencies)],:]
                singular=np.linalg.svd(jac,compute_uv=False)
                rank_one=int(np.linalg.matrix_rank(single,tol=1e-8*np.linalg.norm(single,2)))
                rank_six=int(sum(singular>1e-8*singular[0]))
                rows.append(dict(candidate_id=r['candidate_id'],tau_s=tau,leak_ref_hz=leak,
                                 parameters='logV,logTau,logLeak,logRextra',rank_one_complex_frequency=rank_one,
                                 numerical_rank_six_frequencies=rank_six,
                                 singular_1=float(singular[0]),singular_2=float(singular[1]),
                                 singular_3=float(singular[2]),singular_4=float(singular[3]),
                                 relative_condition_number=float(singular[0]/max(singular[-1],1e-300)),
                                 derivative_step_difference=float(np.max(abs(matrices[0]-matrices[1]))),
                                 scope='LOKALNE_UWARUNKOWANIE_ZNANEGO_MODELU_NIE_PRZEDZIAL_UFNOSCI'))
        # Bez odrębnej identyfikacji Rms, dodatkowy opór materiału ma dokładną swobodę.
        baseline=gas_response(d,100,frequencies,extra_r_n_s_m=.5*d.rms)
        changed=replace(d,qms=d.qms/1.2)
        variant=gas_response(changed,100,frequencies,extra_r_n_s_m=.3*d.rms)
        max_gauge=max(max_gauge,float(max(abs(variant['current_complex_a']/baseline['current_complex_a']-1))))
    with (ROOT/'wyniki/p09_identyfikowalnosc_wypelnienia.csv').open('w',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    result=dict(status='IDENTYFIKOWALNOSC_MODELOWA_NIE_ZIDENTYFIKOWANY_MATERIAL',cases=len(rows),
                max_gauge_Rms_Rextra_relative_current_error=max_gauge,
                min_rank_one_frequency=min(r['rank_one_complex_frequency'] for r in rows),
                max_rank_one_frequency=max(r['rank_one_complex_frequency'] for r in rows),
                full_rank_six_frequency_cases=sum(r['numerical_rank_six_frequencies']==4 for r in rows),
                caveats=['Jeden punkt impedancji ma najwyżej2rzeczywiste obserwacje dla4niewiadomych.',
                         'Rządnumeryczny zależy od progu1e-8 i parametryzacji; nie jest dowodem globalnej identyfikowalności.',
                         'Rms i Rextra występują tylko jako suma, jeśli nie ma niezależnego pomiaru Rms.',
                         'Mały wpływ tau poza jego przejściem lub bardzo wolnego przecieku daje złe uwarunkowanie20–80Hz.'])
    assert max_gauge<1e-12
    (ROOT/'wyniki/p09_identyfikowalnosc_wypelnienia.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return result


if __name__=='__main__':main()
