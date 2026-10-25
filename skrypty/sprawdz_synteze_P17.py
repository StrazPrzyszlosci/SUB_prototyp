"""P17: algebra dokładna, odrębny układ3równań i granice nierówności."""
import csv
from dataclasses import replace
import json
from pathlib import Path
import numpy as np
import sympy as sp
from model_gazu import Medium
from model_nieliniowy import Plant
from model_subwoofera import Driver
from analiza_cewki_z_pamiecia import dynamic_network
from model_cewki_z_pamiecia import blocked_impedance
from synteza_granic_P17 import requirements,feasible,complex_sublevel,at_volume

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def main():
    ar,ai,br,bi,u,L=sp.symbols('ar ai br bi u L',real=True)
    cross=ar*br+ai*bi;normb=br*br+bi*bi
    expanded=(ar+br*u)**2+(ai+bi*u)**2
    square=normb*(u+cross/normb)**2+(ai*br-ar*bi)**2/normb
    identities={'complex_quadratic':sp.factor(expanded-square)}
    theta,alpha,R0,Rth,I2,Pe,Red=sp.symbols('theta alpha R0 Rth I2 Peddy Reddy',positive=True)
    equilibrium=Rth*(I2*R0+Pe)/(1-alpha*Rth*I2*R0)
    identities['constant_output_thermal_equilibrium']=sp.factor(equilibrium-Rth*(I2*R0*(1+alpha*equilibrium)+Pe))
    # Warunek temperatury automatycznie pozostawia dodatni margines stabilności.
    current_limit=theta/(Rth*(R0*(1+alpha*theta)+Red))
    identities['positive_margin_at_thermal_current_limit']=sp.factor(1-alpha*Rth*R0*current_limit-(R0+Red)/(R0*(1+alpha*theta)+Red))
    assert all(x==0 for x in identities.values())
    assert not complex_sublevel(1,0,2).empty
    assert complex_sublevel(3,0,2).empty
    tangent=complex_sublevel(-2+1j,1,1);assert tangent.lower==tangent.upper==2 and not tangent.empty
    assert complex_sublevel(1j,1,1).empty  # Tylko u=0: Vb->inf, brak dodatniej skończonejV.
    assert not complex_sublevel(1+2j,3+4j,np.inf).empty
    cfg=json.loads((ROOT/'dane/konfiguracje/p17_synteza_V_I_X_cieplo.json').read_text());memory=json.loads((ROOT/'dane/konfiguracje/p12c_pamiec_cewki.json').read_text())
    entries={r['candidate_id']:r for r in json.loads((ROOT/'dane/przetworniki/pula_rozszerzona.json').read_text())['drivers']}
    p0=Plant.from_driver(Driver(**entries['C02']['model']))
    zero=requirements(p0,20.,0.,p0.le0,[],80.,.004)
    interval,status=feasible(zero,p0,40.,12.,80.,.6)
    assert not interval.empty and interval.lower==0 and np.isposinf(interval.upper)
    assert at_volume(zero,100.,p0,80.,.004)['Rth_max_all_heat_to_coil_k_w'] is None
    positive=requirements(p0,20.,1.,p0.le0,[],80.,.004)
    assert feasible(positive,p0,np.inf,np.inf,0.,.6)[0].empty
    assert feasible(positive,p0,np.inf,np.inf,80.,np.inf)[0].empty
    assert not feasible(positive,p0,np.inf,np.inf,80.,0.)[0].empty
    lossless=replace(p0,re=0.)
    lossless_req=requirements(lossless,20.,1.,lossless.le0,[],80.,.004)
    assert not feasible(lossless_req,lossless,np.inf,np.inf,80.,np.inf)[0].empty
    with (OUT/'p17_punkty_i_wymagania.csv').open() as h:points=list(csv.DictReader(h))
    medium=Medium();cache={};checked=0;max_pressure=0.;max_current=0.;max_budget=0.;max_temp=0.;grid_count=0
    grid=np.geomspace(1e-4,1e6,401)
    for row in points:
        key=(row['candidate_id'],row['profile'],float(row['target_sine_SPL_rms_db']),float(row['rise_scenario_k']),float(row['f_hz']))
        if key not in cache:
            cid,profile,level,rise,f=key;p=Plant.from_driver(Driver(**entries[cid]['model']));instant,branches,_=dynamic_network(p,profile,memory)
            pressure=20e-6*10**(level/20)
            req=requirements(p,f,pressure,instant,branches,rise,cfg['alpha_per_k'],cfg['distance_m'],cfg['gas_tau_s'])
            cache[key]=(p,instant,branches,pressure,req)
        p,instant,branches,pressure,req=cache[key];rise=key[3];f=key[4]
        vlim=float(row['amp_vrms']);ilim=float(row['amp_arms']);rth=float(row['thermal_Rth_test_k_w'])
        interval,status=feasible(req,p,vlim,ilim,rise,rth,1.)
        # Niezależna siatka: bez użycia wzoru pierwiastków.
        currents=req['current_offset']+req['current_slope']*grid
        volts=req['voltage_offset']+req['voltage_slope']*grid
        heat=abs(currents)**2*(req['Re_hot_ohm']+req['eddy_resistance_ohm'])
        actual=(abs(currents)<=ilim)&(abs(volts)<=vlim)&(rth*heat<=rise)&(req['x_required_peak_m']<=p.xref)
        predicted=np.zeros(len(grid),bool) if interval.empty else (grid>=interval.lower)&(grid<=interval.upper)
        assert np.array_equal(actual,predicted),(key,status)
        grid_count+=len(grid)
        if interval.empty:continue
        for boundary in (interval.lower,interval.upper):
            if boundary<=0 or not np.isfinite(boundary):continue
            volume=1/boundary;s=2j*np.pi*f
            # K z niezależnego jawnego równania relaksacji, nie ThermalSpectrum.
            bulk=medium.p0_pa*(1+medium.gamma*s*cfg['gas_tau_s'])/(1+s*cfg['gas_tau_s'])
            z0=p.resistance+s*p.mass+1/(s*p.cms)
            zb=blocked_impedance(np.array([f]),req['Re_hot_ohm'],instant,branches)[0]
            matrix=np.array([[zb,p.bl0,0.],[-p.bl0,z0,-p.sd],[0.,bulk*p.sd/(s*volume),1.]],complex)
            target_voltage=req['voltage_offset']+req['voltage_slope']*boundary
            solution=np.linalg.solve(matrix,np.array([target_voltage,0.,0.]))
            target_current=req['current_offset']+req['current_slope']*boundary
            pressure_actual=medium.rho*s*p.sd*np.exp(-s*cfg['distance_m']/medium.c)/(4*np.pi*cfg['distance_m'])*solution[1]
            ep=abs(pressure_actual-pressure)/pressure;ei=abs(solution[0]-target_current)/max(abs(target_current),1e-30)
            max_pressure=max(max_pressure,float(ep));max_current=max(max_current,float(ei))
            # Osobny steady solver2węzłów dla dwóch skrajnych przydziałówPeddy.
            current2=abs(solution[0])**2;cold=current2*p.re;eddy=current2*req['eddy_resistance_ohm']
            rv=.6*rth;rm=.4*rth;gv=1/rv;gm=1/rm
            g=np.array([[gv,-gv],[-gv,gv+gm]]);g[0,0]-=cold*cfg['alpha_per_k']
            for eta in (0.,1.):
                temperatures=np.linalg.solve(g,[cold+eta*eddy,(1-eta)*eddy])
                max_temp=max(max_temp,float(temperatures[0]/rise-1))
            violation=max(abs(solution[0])/ilim-1,abs(target_voltage)/vlim-1,rth*current2*(req['Re_hot_ohm']+req['eddy_resistance_ohm'])/rise-1)
            max_budget=max(max_budget,float(violation));checked+=1
    assert max_pressure<2e-8 and max_current<2e-8
    assert max_temp<2e-8 and max_budget<2e-8
    result=dict(status='ANALYTIC_INTERVALS_CHECKED_NOT_GLOBAL_PHYSICAL_CERTIFICATE',point_cases=len(points),grid_inequality_checks=grid_count,
        direct_complex_boundary_checks=checked,maximum_pressure_relative_error=max_pressure,maximum_current_relative_error=max_current,
        maximum_positive_budget_violation=max_budget,maximum_positive_temperature_bound_violation=max_temp,
        symbolic_identities={k:str(v) for k,v in identities.items()},
        boundary_controls=['slope=0,all/none','tangent_positive_u','u=0_only_infinite_volume','unlimited_amplifier',
            'zero_pressure_zero_heat','zero_temperature_budget','insulated_Rth_infinity','ideal_Rth_zero','lossless_coil_zero_heating'],
        domain='u=1/Vb>0,6wybranychf,zamrożonebierneparametry,staływyjściowySPL. Siatka nie jest dowodem całego pasma. Formułyanalityczne nie są certyfikacją arytmetyki zmiennoprzecinkowej.')
    (OUT/'p17_weryfikacja.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False));print(json.dumps(result,indent=2,ensure_ascii=False));return result


if __name__=='__main__':main()
