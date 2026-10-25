"""Dokładna tożsamość ratio i stres przedziałów digitalizacji, nie produktu."""
import csv
from decimal import Decimal
from fractions import Fraction
from itertools import combinations
import json
from pathlib import Path
import sympy as s
from analiza_ident_Le_i_dopasowania import exact_one_pole_exclusion

ROOT=Path(__file__).resolve().parents[1]


def main():
    a,b,t,fi,fj,fk=s.symbols('a b t fi fj fk',positive=True)
    def magnitude_squared(f):return a+b/(1+f*f/t)
    ratio=(magnitude_squared(fi)-magnitude_squared(fj))/(magnitude_squared(fj)-magnitude_squared(fk))
    expected=(fj*fj-fi*fi)/(fk*fk-fj*fj)*(t+fk*fk)/(t+fi*fi)
    assert s.cancel(ratio-expected)==0
    with (ROOT/'dane/zrodla/digitalizacja/Purifi_NAB01_Lgen_fig4.csv').open() as handle:
        data=sorted([r for r in csv.DictReader(handle) if float(r['position_mm'])==0],key=lambda r:float(r['f_hz']))
    exact=exact_one_pole_exclusion(data)
    assert Fraction(exact['required_fc2_lower_rational'])>Fraction(exact['required_fc2_upper_rational'])
    stresses=[]
    for extra in ['0','0.01','0.02','0.05','0.10','0.15','0.20']:
        amount=Decimal(extra);modified=[]
        for row in data:
            copy=row.copy()
            copy['digitization_lower_h']=str(Decimal(row['digitization_lower_h'])*(1-amount))
            copy['digitization_upper_h']=str(Decimal(row['digitization_upper_h'])*(1+amount));modified.append(copy)
        witness=None
        for size in range(len(data),2,-1):
            for ids in combinations(range(len(data)),size):
                subset=[modified[k] for k in ids]
                if not all(Decimal(subset[k]['digitization_lower_h'])>Decimal(subset[k+1]['digitization_upper_h']) for k in range(size-1)):continue
                test=exact_one_pole_exclusion(subset)
                if test['excluded']:
                    witness=dict(frequencies_hz=[r['f_hz'] for r in subset],proof=test);break
            if witness:break
        stresses.append(dict(extra_relative_widening=extra,exclusion_proved_by_test=witness is not None,
                             witness=witness,
                             meaning_if_false='Brak wykluczenia tym testem nie dowodzi istnienia dopasowania.'))
    result=dict(status='PASS_SYMBOLICZNEJ_TOZSAMOSCI_I_DOKLADNYCH_NIEROWNOSCI',base=exact,stress_boxes=stresses,
                scope='Wszystkie dodatnie bieguny jednej gałęzi, ale tylko zapisane/poszerzone przedziały wykresu. Nie są to deklarowane tolerancje producenta.')
    (ROOT/'wyniki/p12c_wykluczenie_1_bieguna_audyt.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print(json.dumps({k:v for k,v in result.items() if k!='stress_boxes'},ensure_ascii=False,indent=2))
    print('Poszerzenia:',[(x['extra_relative_widening'],x['exclusion_proved_by_test']) for x in stresses])
    return result


if __name__=='__main__':main()
