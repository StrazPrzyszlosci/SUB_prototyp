"""Symboliczna kontrola energii i granic wybranych rodzin P09/P10."""
import json
from pathlib import Path
import sympy as s

ROOT=Path(__file__).resolve().parents[1]


def main():
    j=s.I
    omega,tau,p0,gamma=s.symbols('omega tau p0 gamma',positive=True)
    z=s.symbols('z')
    bulk=p0*(1+gamma*z*tau)/(1+z*tau)
    sls=p0+p0*(gamma-1)*z*tau/(1+z*tau)
    assert s.cancel(bulk-sls)==0
    # Linearne równania temperatury i gęstości dla zadanej deformacji objętości.
    strain=s.symbols('strain')
    theta=-(gamma-1)*z*strain/(z+1/tau)
    pressure=p0*(-strain+theta)
    assert s.cancel(-pressure/strain-bulk)==0
    # Skończona pojemność cieplna materiału, bez przepływu do otoczenia.
    cg,cs,h=s.symbols('Cg Cs H',positive=True)
    two=p0*(gamma*cg*cs*z+h*(gamma*cg+cs))/(cg*cs*z+h*(cg+cs))
    k0=p0*(gamma*cg+cs)/(cg+cs)
    tau_eff=cg*cs/(h*(cg+cs))
    two_sls=k0+(gamma*p0-k0)*z*tau_eff/(1+z*tau_eff)
    assert s.cancel(two-two_sls)==0
    # E_dot liniowego układu z oddzielnymi: przeciekiem i relaksacją.
    ii,x,v,y,q,voltage=s.symbols('i x v y q voltage',real=True)
    le,m,re,r,ks,kzero,dk,g,sd,b=s.symbols('Le M Re R Ks K0 Dk G Sd B',positive=True)
    force=kzero*y+dk*(y-q)
    derivative=(le*ii*(voltage-re*ii-b*v)/le+
                m*v*(b*ii-r*v-ks*x-force)/m+ks*x*v+
                force*(v-g*force/sd**2)-dk*(y-q)**2/tau)
    losses=re*ii**2+r*v**2+g*force**2/sd**2+dk*(y-q)**2/tau
    assert s.expand(derivative-voltage*ii+losses)==0
    # Nieliniowa dostępność termodynamiczna (egzergia), nie sama energia U.
    t,t0,volume,v0,vdot,heat=s.symbols('T T0 volume V0 Vdot H0',positive=True)
    cvmass=p0*v0/((gamma-1)*t0)
    gas_pressure=p0*v0*t/(t0*volume)
    availability=cvmass*(t-t0-t0*s.log(t/t0))+p0*v0*(volume/v0-1-s.log(volume/v0))
    tdot=(-gas_pressure*vdot-heat*(t-t0))/cvmass
    d_av=s.diff(availability,t)*tdot+s.diff(availability,volume)*vdot
    assert s.simplify(d_av-(p0-gas_pressure)*vdot+heat*(t-t0)**2/t)==0
    # Transformacja okresowa Z=(T/T0)*(V/V0)^(gamma-1).
    a,vr,vr_dot,temp=s.symbols('a vr vr_dot temp',positive=True)
    temp_dot=-(gamma-1)*temp*vr_dot/vr-(temp-1)/a
    z_dot=temp_dot*vr**(gamma-1)+temp*(gamma-1)*vr**(gamma-2)*vr_dot
    assert s.simplify(a*z_dot+temp*vr**(gamma-1)-vr**(gamma-1))==0
    # Dodatnia admitancja założonego dodatkowego rezerwuaru sorpcji.
    delta_c,fast_c=s.symbols('DeltaC Cfast',positive=True)
    adm=j*omega*fast_c+j*omega*delta_c/(1+j*omega*tau)
    real_adm=s.simplify(s.re(adm))
    assert s.simplify(real_adm-delta_c*omega**2*tau/(1+omega**2*tau**2))==0
    result=dict(status='PASS_TOZSAMOSCI_W_ZADANYCH_MODELACH',
                checks=['K(s) z bilansu gazu równe dodatniemu modelowi SLS',
                        'Gaz+Cs izolowany od otoczenia: dokładny modelSLS z K0>p0',
                        'Bilans liniowej energii z odrębnymi stratami Ra i cieplnymi',
                        'Nieliniowy bilans dostępności gazu i dodatnia dyssypacja H*(T-T0)^2/T',
                        'Transformacja nieliniowej temperatury do liniowego filtra okresowego Z',
                        'Pasywność umownej dodatkowej podatności sorpcyjnej'],
                noncommuting_bulk_limits=dict(
                    first_zero_frequency_then_infinite_tau=str(s.limit(s.limit(bulk,z,0),tau,s.oo)),
                    first_infinite_tau_then_zero_frequency=str(s.limit(s.limit(bulk,tau,s.oo),z,0))),
                limitations='Tożsamości modeli idealnych. Brak identyfikacji H,Cs i izoterm sorpcji rzeczywistych materiałów.')
    (ROOT/'wyniki/p10_audyt_symboliczny.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print('P09/P10: 6 tożsamości i niezamienne granice sprawdzone w SymPy')
    return result


if __name__=='__main__':main()
