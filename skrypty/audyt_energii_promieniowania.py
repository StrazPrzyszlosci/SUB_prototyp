"""P11: dowód symboliczny bilansu motorów i modalnego portu akustycznego."""
import json
from pathlib import Path
import sympy as s

ROOT=Path(__file__).resolve().parents[1]


def main():
    k,sigma,wn,a0,omega=s.symbols('K sigma wn a0 omega',positive=True)
    q,w,z0=s.symbols('q w z0',real=True)
    total=0;expected=0;flow=0;power_coupling=0
    for j in [1,2]:
        ii,v,x,voltage,b,sd=s.symbols(f'i{j} v{j} x{j} V{j} b{j} Sd{j}',real=True)
        mass,le,re,rm,ks,bl=s.symbols(f'M{j} Le{j} Re{j} Rm{j} Ks{j} BL{j}',positive=True)
        pressure_force=k*b*sd*(w+z0)
        motor=(le*ii*(voltage-re*ii-bl*v)/le+
               mass*v*(bl*ii-rm*v-ks*x-pressure_force)/mass+ks*x*v)
        total+=motor;expected+=voltage*ii-re*ii**2-rm*v**2
        flow+=b*sd*v
    total+=k*w*(-wn**2*q-2*sigma*w+flow)+k*wn**2*q*w+k*z0*(-a0*z0+flow)
    expected-=2*sigma*k*w**2+a0*k*z0**2
    assert s.expand(total-expected)==0
    transfer=k*s.I*omega/((s.I*omega)**2+2*sigma*s.I*omega+wn**2)
    real=s.simplify(s.re(transfer))
    positive=2*k*sigma*omega**2/((wn**2-omega**2)**2+4*sigma**2*omega**2)
    assert s.simplify(real-positive)==0
    zero_real=s.simplify(s.re(k/(a0+s.I*omega)))
    assert s.simplify(zero_real-k*a0/(a0**2+omega**2))==0
    result=dict(status='PASS_SYMBOLICZNE_BILANS_I_DODATNIOSC_PORTOW',
                checks=['Dwa motory i modalny akustyczny port: siły/przepływy mają przeciwne moce sprzężenia',
                        'Część rzeczywista każdego niezerowego modu jest nieujemna dla wszystkichomega',
                        'Relaksujący mod jednorodny ma nieujemną część rzeczywistą'],
                scope='Dowód dla zadanej rodziny modalnej i dodatnich parametrów. Pasywność nie identyfikuje fizycznego pokoju.',
                stability_note='Przy dodatnim tłumieniu modów i motorów oraz dodatniej energii model ma rozpraszanie. Granica bez strat może mieć nierozpraszane mody; nie deklarować wówczas asymptotycznej stabilności.')
    (ROOT/'wyniki/p11_bilans_symboliczny.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print('P11: symboliczny bilans motorów/pokoju i dodatniość modalnej impedancji sprawdzone')
    return result


if __name__=='__main__':main()
