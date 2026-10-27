"""Symboliczna kontrola domknięcia kwadratu i termicznego porównania."""
from pathlib import Path
import hashlib,json
import sympy as sp

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def main():
    a,u,gamma,lam,W=sp.symbols('a u gamma lambda W',real=True);assert sp.simplify(-gamma*a*a+2*a*u-u*u/gamma+gamma*(a-u/gamma)**2)==0
    theta0,cth,t,Re,I,alpha,Rth=sp.symbols('theta0 Cth t Re I alpha Rth',positive=True)
    A=Re*I**2;b=1/Rth-alpha*A;equilibrium=A/b
    upper=equilibrium+(theta0-equilibrium)*sp.exp(-b*t/cth)
    assert sp.simplify(cth*sp.diff(upper,t)-(A-b*upper))==0
    assert sp.simplify(upper.subs(t,0)-theta0)==0
    theta_limit=sp.symbols('theta_limit',positive=True)
    exact_cap=theta_limit/(Rth*Re*(1+alpha*theta_limit))
    assert sp.simplify((A/b).subs(I**2,exact_cap)-theta_limit)==0
    assert sp.simplify(b.subs(I**2,exact_cap)-1/(Rth*(1+alpha*theta_limit)))==0
    result=dict(status='EXACT_SYMBOLIC_IDENTITIES_OF_CONDITIONAL_MODEL',identities=[
        'Complete square yields Wdot<=-lambda*W+u^2/gamma',
        'Thermal comparison exponential solves Cth*theta_dot=A-b*theta',
        'Thermal comparison initial condition',
        'At exact instantaneous current cap equilibrium=theta_limit',
        'At cap b=1/(Rth*(1+alpha*theta_limit))>0'],
        input_sha256={str(Path(__file__).resolve().relative_to(ROOT)):hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
        limitations=['Identities alone do not prove matrix inequalities;use the independent rational LDL verifier.',
            'X/I projection bounds also use Cauchy-Schwarz for the positive definite ellipsoid.',
            'The comparison model contains only copper heating and the stated positive one-pole cooling.'])
    (OUT/'p24a_tozsamosci_symboliczne.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print('P24A symbolic:5identities;model scope unchanged.')


if __name__=='__main__':main()
