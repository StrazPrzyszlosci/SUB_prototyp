"""Odrębne granice analityczne redukcji liczby fizycznych węzłów cieplnych."""
import json
from pathlib import Path
import numpy as np
from model_termiczny_P15 import ThermalCauer

ROOT=Path(__file__).resolve().parents[1]


def main():
    t=np.array([.1,1.,10.]);power=4.;results={}
    def check(name,models,expected):
        errors=[float(np.max(abs(model.step(t,[power,0.])-expected))) for model in models]
        assert errors[-1]<errors[0]*1e-3,(name,errors)
        assert errors[-1]<5e-5,(name,errors)
        results[name]=errors
    merged=power*1.2*(-np.expm1(-t/(1.2*5.)))
    check('Rvm_to_zero_merged_Cv_plus_Cm',[ThermalCauer(2.,3.,v,1.2) for v in np.logspace(-1,-6,6)],np.column_stack([merged,merged]))
    isolated=power*2.1*(-np.expm1(-t/(2.1*2.)))
    check('Rvm_to_infinity_isolated_coil',[ThermalCauer(2.,3.,v,1.2,2.1) for v in np.logspace(1,7,7)],np.column_stack([isolated,np.zeros(len(t))]))
    fixed=power*.7*(-np.expm1(-t/(.7*2.)))
    check('Cm_to_infinity_frozen_magnet',[ThermalCauer(2.,v,.7,1.2) for v in np.logspace(2,7,6)],np.column_stack([fixed,np.zeros(len(t))]))
    slow=power*1.2*(-np.expm1(-t/(1.2*3.)))
    check('Cv_to_zero_algebraic_coil',[ThermalCauer(v,3.,.7,1.2) for v in np.logspace(-1,-6,6)],np.column_stack([slow+power*.7,slow]))
    # Kolejność granic Cv->0 i t->0 jest niezamienna: skok4*Rvm kontra0.
    result=dict(status='FOUR_REDUCTION_LIMITS_PASS',times_s=t.tolist(),absolute_errors_k=results,
                number_of_controls=25,scope='Granice dla stałych parametrów i P=4W; wartości umowne. Cv->0 badano dla t>0, nie jako ciągłość temperatury w t=0. Nie fizyczny produkt ani globalne ekstremum.')
    (ROOT/'wyniki/p15a_granice.json').write_text(json.dumps(result,indent=2,ensure_ascii=False))
    print(json.dumps(result,indent=2,ensure_ascii=False));return result


if __name__=='__main__':main()
