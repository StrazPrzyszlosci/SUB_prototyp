"""Dokładne tożsamości termiki, niezależne od solvera macierzy numerycznych."""
import json
from pathlib import Path
import sympy as s

ROOT=Path(__file__).resolve().parents[1]


def main():
    cv,cm,rv,rm,ga,k=s.symbols('Cv Cm Rv Rm ga k',positive=True)
    z=s.symbols('z');gv=1/rv;gm=1/rm
    g=s.Matrix([[gv+ga,-gv],[-gv,gv+gm]]);cap=s.diag(cv,cm)
    port=(g+z*cap).inv()[0,0]
    expected=(cm*z+gv+gm)/((cv*z+gv+ga)*(cm*z+gv+gm)-gv**2)
    identities={}
    identities['Cauer_port']=s.factor(port-expected)
    no_direct=s.factor((g.subs(ga,0)+z*cap).det()*cv**-1*cm**-1)
    # Wielomian dla stałych czasowych: tau² - tau_sum*tau + tau_product.
    tau=s.symbols('tau');poly=s.Poly(s.expand(no_direct.subs(z,-1/tau)*tau**2*cv*cm*rv*rm),tau)
    identities['tau_sum']=s.factor(-poly.nth(1)/poly.nth(2)-(cm*rm+cv*(rv+rm)))
    identities['tau_product']=s.factor(poly.nth(0)/poly.nth(2)-cv*cm*rv*rm)
    loop=g-s.Matrix([[k,0],[0,0]])
    critical=ga+gv*gm/(gv+gm)
    identities['current_feedback_threshold']=s.factor(loop.det()-(gv+gm)*(critical-k))
    dc=g.subs(ga,0).inv();pc,pe=s.symbols('Pcu Peddy',nonnegative=True)
    identities['heat_partition_no_direct']=s.factor((dc*s.Matrix([pc,pe]))[0]-(pc*(rv+rm)+pe*rm))
    tv,tm,pv,pm=s.symbols('Tv Tm Pv Pm');state=s.Matrix([tv,tm]);power=s.Matrix([pv,pm])
    derivative=cap.inv()*(power-g*state)
    identities['physical_total_heat_balance']=s.factor(cv*derivative[0]+cm*derivative[1]-(pv+pm-ga*tv-gm*tm))
    a,D,E,b=s.symbols('a D E b',positive=True)
    family_port=s.factor(port.subs({rv:1/b,rm:1/(D*b*b/E-b),ga:a-b,cm:b*b/E}))
    same_port=(z+D)/(cv*z*z+(a+cv*D)*z+a*D-E)
    identities['direct_cooling_continuous_nonidentifiability']=s.factor(family_port-same_port)
    assert all(v==0 for v in identities.values())
    result=dict(status='EXACT_IDENTITIES_PASS',SymPy=s.__version__,identities={k:str(v) for k,v in identities.items()},
                Cauer_port=str(s.factor(expected)),current_feedback_critical_w_per_k=str(s.factor(critical)),
                scope='Tożsamości modeli skupionych przy dodatnich stałych parametrach; nie identyfikacja rzeczywistego chłodzenia.')
    (ROOT/'wyniki/p15a_tozsamosci_symboliczne.json').write_text(json.dumps(result,indent=2,ensure_ascii=False))
    print(json.dumps(result,indent=2,ensure_ascii=False));return result


if __name__=='__main__':main()
