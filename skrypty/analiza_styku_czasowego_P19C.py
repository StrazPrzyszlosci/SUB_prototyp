"""Rozstrzygniecie przypadku80Hz: redukcja,czas,energia i odrebny pelnyMES."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import numpy as np
from model_styku_czasowego_P19C import FullContact,ReducedContact
from pelny_MES_BDF2_P19C import full_bdf2

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def write_json(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False))


def prepared_state(full,reduced,Vold,Yold):
    oldn=Vold.shape[1];S=reduced.pos_scale;w=full.omega
    u=Vold@(S*Yold[:oldn]);v=Vold@(w*S*Yold[oldn:2*oldn])
    return np.r_[reduced.V.T@(full.M@u)/S,reduced.V.T@(full.M@v)/(w*S),Yold[-1]]


def save_run(label,model,result,trace):
    result['label']=label
    write_json(OUT/('p19c_'+label+'.json'),result)
    np.savez_compressed(OUT/('p19c_'+label+'.npz'),theta=trace['theta'],y=trace['y'],V=model.V)
    fields=list(trace['data'][0]);
    with (OUT/('p19c_'+label+'_przebieg.csv')).open('w',newline='') as f:
        writer=csv.DictWriter(f,['theta',*fields]);writer.writeheader()
        writer.writerows(dict(theta=float(t),**d) for t,d in zip(trace['theta'],trace['data']))


def residual_diagnostic(full,r,trace,count=64):
    indices=np.linspace(0,trace['y'].shape[1]-2,count,dtype=int);res=[];qs=[]
    for i in indices:
        theta=trace['theta'][i];y=trace['y'][:,i]
        u,v,lag,x,xp,xpp,volume,p,acc=r.mechanics(theta,y)
        q=r.V@u;vv=r.V@v;aa=r.V@acc;z=full.z0+full.D@q
        force=full.D.T@(full.weights*(np.maximum(z,0)-full.spring0))
        R=full.M@aa+full.C@vv+full.Ks@q+force-full.H*p+full.e*full.mm*full.omega**2*xpp
        res.append(R);qs.append(q)
    R=np.array(res).T;Q=np.array(qs).T;correction=full.factor.solve(R)
    ratio=float(np.sqrt(np.sum(R*correction)/np.sum(Q*(full.Kt@Q))))
    basket_ratio=float(np.sqrt(np.mean(correction[-3]**2))/np.sqrt(np.mean(Q[-3]**2)))
    return dict(samples=count,preload_K_dual_residual_to_displacement_energy_norm=ratio,
                static_residual_basket_correction_rms_ratio=basket_ratio,
                scope='Diagnostyka z Kt stanu docisku;nie gorna granica bledu po otwarciu styku.')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--full',action='store_true');parser.add_argument('--independent',action='store_true')
    args=parser.parse_args();full=FullContact();results=[]
    pilot=OUT/'archiwum/P19C_pilot_M08';meta=json.loads((pilot/'snapshot_sha256.json').read_text())
    for name,h in meta.items():assert hashlib.sha256((pilot/name).read_bytes()).hexdigest()==h,name
    assert json.loads((pilot/'p19c_styk_czasowy.json').read_text())==full.cfg
    last=np.load(pilot/'p19c_pilot_M08.npz');Vold=last['V'];Yold=last['y'][:,-1];start_cycle=int(round(last['theta'][-1]/(2*np.pi)))
    old=json.loads((pilot/'p19c_pilot_M08.json').read_text());old['label']='HISTORICAL_M08_COLD_START';results.append(old)
    last_model=None;last_trace=None
    for n,enrich,label in [(16,False,'M16'),(16,True,'E16'),(32,True,'E32')]:
        model=ReducedContact(full,full.basis(n,enrich));init=prepared_state(full,model,Vold,Yold)
        result,trace=model.simulate(initial_state=init,start_cycle=start_cycle)
        result['preparation']='Rzut z poprzedniego rozstrzygnietego przebiegu;nie niezalezny zimny rozruch.'
        result['full_FE_residual_diagnostic']=residual_diagnostic(full,model,trace)
        save_run(label,model,result,trace);results.append(result)
        print('P19C zakonczono',label,'dim',model.n,'basketpeak',result['basket_peak_m'],'open',result['max_open_area_fraction'],flush=True)
        Vold=model.V;Yold=trace['y'][:,-1];start_cycle=int(round(trace['theta'][-1]/(2*np.pi)));last_model=model;last_trace=trace
    # Maly sygnal przygotowany dokladnym liniowym fazorem;to kontrola czasu i granicy,nie rozruch.
    small=ReducedContact(full,full.basis(16,True),1e-6);lin=small.linear_reference();q=lin['state']
    lag=(full.sd*small.amplitude_rms+small.h@q)/(1+1j*full.omega*full.tau)
    init=np.r_[np.sqrt(2)*q.imag/small.pos_scale,np.sqrt(2)*q.real/small.pos_scale,np.sqrt(2)*lag.imag/small.vol_scale]
    result,trace=small.simulate(initial_state=init,start_cycle=4,atol=1e-13,max_cycles=24)
    save_run('SMALL',small,result,trace);results.append(result)
    if args.independent:
        # BDF od tego samego przygotowanego stanu:odrebna metoda integracji,nie dowod unikalnosci atraktora.
        init=last_trace['y'][:,-1]
        result,trace=last_model.simulate(method='BDF',initial_state=init,start_cycle=start_cycle,rtol=2e-8,atol=1e-12,max_cycles=40)
        save_run('E32_BDF',last_model,result,trace);results.append(result)
    full_results=[]
    if args.full:
        for steps in [256,512,1024]:
            result,data,state=full_bdf2(full,last_model,last_trace,steps,3)
            label='FULL_BDF2_'+str(steps);write_json(OUT/('p19c_'+label+'.json'),result)
            with (OUT/('p19c_'+label+'_przebieg.csv')).open('w',newline='') as f:
                writer=csv.DictWriter(f,list(data[0]));writer.writeheader();writer.writerows(data)
            np.savez_compressed(OUT/('p19c_'+label+'_stan.npz'),**state)
            full_results.append(result)
    sources=['dane/konfiguracje/p19c_styk_czasowy.json','skrypty/model_styku_czasowego_P19C.py',
             'skrypty/analiza_styku_czasowego_P19C.py','skrypty/pelny_MES_BDF2_P19C.py',
             'skrypty/model_frontu_z_otworem_P18B.py','skrypty/model_plyty_MITC_P18.py',
             'skrypty/analiza_styku_frontu_P19B.py','wyniki/p11_kalibracje_masy.csv','wyniki/p19b_dynamika_i_bramki_styku.csv']
    out=dict(status='EXECUTED_SCOPED_CONTACT_TIME_STUDY_NOT_FINAL_CABINET',full_dof=full.M.shape[0],results=results,full_time_comparison=full_results,
             input_sha256={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in sources},
             historical_pilot_snapshot_sha256=hashlib.sha256((pilot/'snapshot_sha256.json').read_bytes()).hexdigest(),
             limitations=full.cfg['scope'])
    write_json(OUT/'p19c_podsumowanie.json',out)
    print('P19C caly etap:przebiegi',len(results),'pelnyMES',len(full_results),flush=True)


if __name__=='__main__':main()
