"""P19C: niezalezna algebra energii,screening otwarcia i hipoteza tlumienia."""
import copy
import hashlib
import json
from pathlib import Path
import numpy as np
import sympy as sy
from model_styku_czasowego_P19C import FullContact,ReducedContact
from analiza_styku_czasowego_P19C import prepared_state,save_run
from model_gazu import Medium

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def symbolic():
    M,m,v,xd,xdd,c,U,h,S,K,gamma,xi,lag,tau=sy.symbols('M m v xd xdd c U h S K gamma xi lag tau',positive=True)
    p=-K*(gamma*xi-(gamma-1)*lag);ld=(xi-lag)/tau;vd=S*xd+h*v
    a=(-c*v-U+h*p-m*xdd)/M
    energy_dot=M*v*a+m*xdd*v+m*xd*a+m*xd*xdd+U*v+K*(xi*vd+(gamma-1)*(xi-lag)*(vd-ld))
    source=(m*(xdd+a)-S*p)*xd;loss=c*v*v+K*(gamma-1)/tau*(xi-lag)**2
    identity=sy.simplify(energy_dot-source+loss)
    gas_identity=sy.simplify(K*(xi*vd+(gamma-1)*(xi-lag)*(vd-ld))+p*vd+K*(gamma-1)/tau*(xi-lag)**2)
    kinetic=sy.simplify((M*v*v+2*m*v*xd+m*xd*xd)-((M-m)*v*v+m*(v+xd)**2))
    u=sy.symbols('u');ramp=10*u**3-15*u**4+6*u**5
    endpoints=[ramp.subs(u,0),(ramp-1).subs(u,1),sy.diff(ramp,u).subs(u,0),sy.diff(ramp,u).subs(u,1),sy.diff(ramp,u,2).subs(u,0),sy.diff(ramp,u,2).subs(u,1)]
    values=dict(total_energy=str(identity),gas_energy=str(gas_identity),positive_kinetic_completion=str(kinetic),smooth_ramp_endpoints=[str(x) for x in endpoints])
    assert identity==gas_identity==kinetic==0 and all(x==0 for x in endpoints)
    return values


def gap_screen(full,record):
    V=record['V'];Y=record['y'];n=V.shape[1];S=.001*np.sqrt(full.cfg['net_mass_kg'])
    Q=V@(S*Y[:n]);gap=full.z0[:full.ng,None]+full.Dg@Q
    actual_open=np.maximum(-gap,0);sample_max=float(actual_open.max())
    # Przy danym zapisanym stanie: N>=0,wiec ekstremum izoparametrycznego
    # pola wzglednego jest ograniczone przez wierzcholki obejmujacych komorek.
    xy=full.plate.xy;corners=xy[full.plate.elements];lo=corners.min(axis=1);hi=corners.max(axis=1)
    minimum_radius=np.linalg.norm(np.maximum(np.maximum(lo,-hi),0),axis=1)
    maximum_radius=np.linalg.norm(corners,axis=2).max(axis=1)
    r0,r1=full.cfg['gasket_radii_m'];intersects=(minimum_radius<=r1)&(maximum_radius>=r0)
    nodes=np.unique(full.plate.elements[intersects]);ndof=len(full.plate.full_F)
    allq=np.zeros((ndof,Q.shape[1]));allq[full.plate.free]=Q[:-3]
    local_gap=allq[3*nodes]-Q[-3]-xy[nodes,0,None]*Q[-2]-xy[nodes,1,None]*Q[-1]
    q0full=np.zeros(ndof);q0full[full.plate.free]=full.q0[:-3]
    local0=q0full[3*nodes]-full.q0[-3]-xy[nodes,0]*full.q0[-2]-xy[nodes,1]*full.q0[-1]
    maximum_height=max(0,float(np.max(-local0[:,None]-local_gap)))
    medium=Medium();mu=medium.viscosity_pa_s
    # Otwarty caly pierscien o stalej maksymalnej wysokosci:celowo wieksza
    # konduktancja niz dla zablokowanych/wezszych sciezek w modelu smarowania.
    conductance=np.pi*maximum_height**3/(6*mu*np.log(r1/r0))
    omega=full.omega;cab=full.cfg['cavity_m3']/(full.cfg['p0_pa']*(1+(full.gamma-1)*1j*omega*full.tau/(1+1j*omega*full.tau)))
    acoustic_ratio=float(conductance/abs(1j*omega*cab))
    volume_actual=full.area@actual_open;area=np.pi*(r1*r1-r0*r0)
    result=dict(sampled_gap_max_m=sample_max,cell_vertex_upper_height_at_recorded_times_m=maximum_height,
                lubrication_full_ring_conductance_upper_m3_pa_s=float(conductance),conductance_to_abs_sCab=acoustic_ratio,
                sampled_gap_void_max_m3=float(max(volume_actual)),cell_vertex_void_upper_m3=float(area*maximum_height),
                vertex_void_to_cone_volume_rms=float(area*maximum_height/(full.sd*full.cfg['cone_relative_rms_m'])),
                sampled_void_to_cone_volume_rms=float(max(volume_actual)/(full.sd*full.cfg['cone_relative_rms_m'])),
                reference_Womersley=float(maximum_height/2*np.sqrt(omega*medium.rho/mu)),
                assumptions=['Ograniczenie przestrzenne jest dla zapisanych stanow;nie certyfikat wszystkich chwil ODE.',
                             'Lubrykacja/Poiseuille,ustalone kanaly,nieidentyfikowana topologia rzeczywistego przecieku.',
                             'Ruch granic moze tworzyc dodatkowa objetosc/squeeze flow;dlatego raportujemy tez Vgap.',
                             'Brak predykcji szumu przeplywu lub szczelnosci rzeczywistego materialu.'])
    return result


def main():
    full=FullContact();npz=np.load(OUT/'p19c_E32.npz');gap=gap_screen(full,npz)
    cfg=copy.deepcopy(full.cfg);cfg['damping_model']='PLATE_MASS_RAYLEIGH'
    alternative=FullContact(cfg);r=ReducedContact(alternative,alternative.basis(32,True))
    init=prepared_state(alternative,r,npz['V'],npz['y'][:,-1]);start=int(round(npz['theta'][-1]/(2*np.pi)))
    result,trace=r.simulate(initial_state=init,start_cycle=start)
    save_run('E32_PLATE_DAMPING',r,result,trace)
    out=dict(status='CONDITIONAL_PHYSICAL_MODEL_AUDIT_NOT_HARDWARE_SEAL_CERTIFICATE',symbolic=symbolic(),gap_screening=gap,
             damping_control=result,
             damping_scope='BazoweC=alphaM+betaKt to zamrozona hipoteza strukturalna,nie lepki kontakt. Alternatywa usuwa betaKjoint;nie przypisuje tlumika otwartej uszczelce.',
             input_sha256={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in
                           ['skrypty/audyt_fizyki_P19C.py','skrypty/model_styku_czasowego_P19C.py','skrypty/analiza_styku_czasowego_P19C.py','dane/konfiguracje/p19c_styk_czasowy.json','wyniki/p19c_E32.npz']})
    (OUT/'p19c_audyt_fizyki.json').write_text(json.dumps(out,indent=2,ensure_ascii=False,allow_nan=False))
    print('P19C audit:gap',gap,'alternatepeak',result['basket_peak_m'],flush=True)


if __name__=='__main__':main()
