"""Odrębne KCL/KVL,port stanu,granice i dowód straty przez R źródła."""
from pathlib import Path
import csv,hashlib,json
import numpy as np
import sympy as sp
from analiza_rozszerzenia_SB import candidates
from model_subwoofera import response,RHO,C
from model_portu_wzmacniacza_P22 import port_response

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def main():
    cfg=json.loads((ROOT/'dane/konfiguracje/p22a_port_wzmacniacza.json').read_text());pool=candidates();lookup={c:d for c,p,d,x in pool}
    r,x,rs=sp.symbols('r x rs',positive=True)
    assert sp.simplify(sp.diff((r+rs)**2+x*x,rs)-2*(r+rs))==0
    m,k,b,R,rm=sp.symbols('m k b R rm',positive=True)
    q=sp.sqrt(m*k)/(rm+b*b/R)
    assert sp.simplify(sp.diff(q,R)-sp.sqrt(m*k)*b*b/(R*R*(rm+b*b/R)**2))==0
    X,V,I,Is,Vt,Vs,Le,Ls,Cp=sp.symbols('X V I Is Vt Vs Le Ls Cp',real=True)
    dE=k*X*V+V*(b*I-rm*V-k*X)+I*(Vt-R*I-b*V)+Is*(Vs-rs*Is-Vt)+Vt*(Is-I)
    assert sp.expand(dE-(Vs*Is-R*I*I-rs*Is*Is-rm*V*V))==0
    maxerr=0.;count=0;worst=None
    with (OUT/'p22a_naped_z_portem.csv').open() as f:rows=list(csv.DictReader(f))
    networks={n['id']:n for n in cfg['passive_output_networks_assumed']}
    # Każdy opublikowany punkt:niezależny układ czterech równań z niewiadomymi I,v,Vt,Is.
    for row in rows:
        d=lookup[row['configuration']];f=float(row['f_hz']);vb=float(row['volume_l']);Rsource=float(row['rs_ohm'])
        net=networks[row['network']];s=2j*np.pi*f;K=1/d.cms+RHO*C*C*d.sd*d.sd/(vb*.001)
        ze=d.re_ohm+s*d.le_mh*.001;zm=d.rms+s*d.mms+K/s;zs=Rsource+s*net['series_h']
        A=np.array([[ze,d.bl,-1,0],[-d.bl,zm,0,0],[-1,0,-s*net['shunt_f'],1],[0,0,1,zs]],complex)
        direct=np.linalg.solve(A,[0,0,0,1]);expected=port_response(d,vb,np.array([f]),Rsource,net['series_h'],net['shunt_f'])
        reference=np.array([expected['driver_current'][0],expected['velocity'][0],expected['terminal_voltage'][0],expected['source_current'][0]])
        error=float(np.max(abs(direct-reference)/np.maximum(abs(reference),1e-25)));count+=1
        if error>maxerr:maxerr=error;worst=dict(configuration=row['configuration'],f_hz=f,volume_l=vb,rs_ohm=Rsource,network=row['network'])
    assert maxerr<1e-10
    baseline=0.;state_error=0.;state_count=0;limit_rows=[]
    for cid,pid,d,cat in pool:
        for vb in [30.,150.]:
            f=np.array([20.,40.,80.]);a=port_response(d,vb,f);old=response(d,vb,f)
            baseline=max(baseline,float(np.max(abs(abs(a['driver_current'])/old['i_rms']-1))),
                float(np.max(abs(np.sqrt(2)*abs(a['x'])/old['x_peak_m']-1))))
            if d.le_mh>0:
                Rsource=.1;ls=30e-6;cp=1e-6;K=1/d.cms+RHO*C*C*d.sd*d.sd/(vb*.001);le=d.le_mh*.001
                A=np.zeros((5,5));A[0,1]=1;A[1]=[-K/d.mms,-d.rms/d.mms,d.bl/d.mms,0,0]
                A[2]=[0,-d.bl/le,-d.re_ohm/le,0,1/le];A[3,3:]=[-Rsource/ls,-1/ls];A[4,2:]=[-1/cp,1/cp,0]
                B=np.array([0,0,0,1/ls,0]);eigs=np.linalg.eigvals(A);assert np.max(eigs.real)<0
                # Energia stanu: A.T*P+P*A=-2*diag(strat).
                P=np.diag([K,d.mms,le,ls,cp]);D=np.diag([0,d.rms,d.re_ohm,Rsource,0])
                assert np.max(abs(A.T@P+P@A+2*D))<1e-9
                test=port_response(d,vb,f,Rsource,ls,cp)
                for i,hz in enumerate(f):
                    state=np.linalg.solve(2j*np.pi*hz*np.eye(5)-A,B)
                    target=np.array([test['x'][i],test['velocity'][i],test['driver_current'][i],test['source_current'][i],test['terminal_voltage'][i]])
                    error=float(np.max(abs(state-target)/np.maximum(abs(target),1e-25)))
                    state_error=max(state_error,error);state_count+=1
            # R→∞ przy ustalonym V i f:prąd źródła i ruch dążą do0,nie do idealnego prądu.
            for resistance in [1e4,1e8]:
                far=port_response(d,vb,np.array([40.]),resistance,30e-6,1e-6)
                limit_rows.append(dict(configuration=cid,volume_l=vb,rs_ohm=resistance,
                    abs_source_current=float(abs(far['source_current'][0])),
                    scaled_current_R=float(abs(far['source_current'][0])*resistance)))
    assert baseline<1e-10 and state_error<1e-10
    assert max(abs(r['scaled_current_R']-1) for r in limit_rows if r['rs_ohm']==1e8)<1e-5
    # Cała siatka punktów z samym R:obwiednia nie rośnie przy zwiększaniu R.
    pure=[r for r in rows if r['network']=='RL0_C0'];groups={}
    for row in pure:groups.setdefault((row['configuration'],row['volume_l'],row['f_hz']),[]).append(row)
    max_gain=0.
    for key,group in groups.items():
        a=sorted(group,key=lambda r:float(r['rs_ohm']));values=np.array([float(r['spl_rms_2pi_1m_db']) for r in a])
        max_gain=max(max_gain,float(np.max(np.diff(values))));assert np.max(np.diff(values))<1e-9
    record=dict(status='COMPLETE_SCOPED_PASSIVE_SOURCE_CHECKS',independent_KCL_KVL_points=count,
        max_relative_direct_system_error=maxerr,direct_system_worst=worst,baseline_vs_existing_model_error=baseline,
        independent_state_space_points=state_count,max_relative_state_space_error=state_error,
        symbolic_identities=['d|Z+Rs|^2/dRs=2*(ReZ+Rs)>0','dQ/dRtotal>0','passive total state energy balance'],
        resistance_limit_witnesses=limit_rows,monotonic_envelope_groups=len(groups),max_adjacent_gain_db=max_gain,
        input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__).resolve(),
            ROOT/'skrypty/model_portu_wzmacniacza_P22.py',OUT/'p22a_naped_z_portem.csv']},
        limitations=['Pure-R monotonicity theorem uses fixed Vsource/Isource/X budgets and a passive fixed linear driver at each positive frequency.',
            'Do not transfer this to arbitrary RLC active feedback,current control,thermal limits or all frequency-dependent amplifiers.',
            'KCL/KVL and state-space checks verify the numerical model,not measured amplifier output impedance.'])
    (OUT/'p22a_kontrole_niezalezne.json').write_text(json.dumps(record,ensure_ascii=False,indent=2,allow_nan=False))
    print('P22A checks:',count,'KCL/KVL,',state_count,'state points;',len(groups),'monotone envelopes')


if __name__=='__main__':main()
