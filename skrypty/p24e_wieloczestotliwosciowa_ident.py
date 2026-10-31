#!/usr/bin/env python3
"""P24E: joint multi-frequency Re(T), BL² and Le inversion; synthetic U/I data.
Research-only: nominal Dayton C02/80 L and *assumed* measurement uncertainties.
"""
import json, math
from pathlib import Path
import numpy as np
RNG = np.random.default_rng(20261031)
N=5000
FSETS={
 "single_40":[40.],
 "single_80":[80.],
 "near_80_150":[80.,150.],
 "low_20_40_80":[20.,40.,80.],
 "upper_80_150_300":[80.,150.,300.],
 "full_20_40_80_150_300":[20.,40.,80.,150.,300.],
}
CASES={
 "fixed_motor":dict(bl_factor=1.,le_factor=1.,cms_factor=1.,wire_drift_ohm=0.),
 "motor_and_inductance_drift":dict(bl_factor=.97,le_factor=1.1,cms_factor=1.,wire_drift_ohm=0.),
 "unmodeled_compliance_drift":dict(bl_factor=.97,le_factor=1.1,cms_factor=1.05,wire_drift_ohm=0.),
 "series_resistance_drift":dict(bl_factor=.97,le_factor=1.1,cms_factor=1.,wire_drift_ohm=.10),
}

def mechanical(f,cms_factor=1.):
    rho,c,sd=1.2,343.,.08296
    cms=(.212)/(rho*c*c*sd*sd)*cms_factor
    w=2*math.pi*f
    mms=.306
    return complex(2*math.pi*19.5*mms/3.02,
       w*mms-1/(w*cms)-sd**2*rho*c*c/(w*.080))

def impedance(f,delta_K,bl_factor=1.,le_factor=1.,cms_factor=1.,
              wire_drift_ohm=0.):
    w=2*math.pi*f
    return (3*(1+.00393*delta_K)+wire_drift_ohm+
        1j*w*.00092*le_factor + (15*bl_factor)**2/mechanical(f,cms_factor))

def add_noise(z,n):
    return z*(1+RNG.normal(0,.005,(n,len(z))))*np.exp(
        1j*RNG.normal(0,math.radians(.2),(n,len(z))))

def invert(freqs,z_cold,z_hot):
    f=np.asarray(freqs)
    adm=np.array([1/mechanical(x) for x in f])
    if len(freqs)==1:
        # naive P24C estimator assumes unchanging motional impedance
        dr=np.real(z_hot-z_cold)[:,0]
        return dr/(3*.00393),None,None
    # ΔZ = ΔRe + Δ(BL²)/Zm + jωΔLe. Delta Le measured in mH.
    design=np.vstack([np.stack([np.ones(len(f)),adm.real,np.zeros(len(f))],axis=1),
                      np.stack([np.zeros(len(f)),adm.imag,2*np.pi*f*.001],axis=1)])
    observations=np.hstack([(z_hot-z_cold).real,(z_hot-z_cold).imag])
    assert np.linalg.matrix_rank(design)==3
    solution=observations@np.linalg.pinv(design).T
    return solution[:,0]/(3*.00393), float(np.linalg.cond(design)), solution

def main():
    rows=[]
    for case,cfg in CASES.items():
        for key,freqs in FSETS.items():
            cold=np.asarray([impedance(f,0) for f in freqs])
            hot=np.asarray([impedance(f,80,**cfg) for f in freqs])
            noisy_cold=add_noise(cold,N)
            noisy_hot=add_noise(hot,N)
            dt,cond,_=invert(freqs,noisy_cold,noisy_hot)
            exact,_,_=invert(freqs,cold[None,:],hot[None,:])
            errors=dt-80
            rows.append(dict(case=case,band=key,n_frequencies=len(freqs),
                exact_bias_K=round(float(exact[0]-80),3),
                mean_bias_K=round(float(np.mean(errors)),3),
                rmse_K=round(float(np.sqrt(np.mean(errors**2))),3),
                p95_absolute_error_K=round(float(np.quantile(abs(errors),.95)),3),
                condition_number=None if cond is None else round(cond,3)))
    # Separability theorem: a constant contact/cable ΔR shares the column
    # with ΔRe and thus is not distinguishable by this linear model.
    # Compute exact equality of the effect on all selected frequencies.
    v=np.array([impedance(f,80,**CASES["series_resistance_drift"])-
                impedance(f,80,**CASES["motor_and_inductance_drift"])
                for f in FSETS["full_20_40_80_150_300"]])
    assert np.max(np.abs(v-.1))<1e-12
    # Repeat deterministic noise experiments with fixed seed for review.
    out=dict(study="P24E",date="2026-10-31",model="Dayton C02 80L P24B nominal",
       n_per_case_and_band=N,noise_ratio_sigma=.005,noise_phase_sigma_deg=.2,
       assumed_true_delta_T_K=80,
       cases=CASES,bands_hz=FSETS,n_simulations=len(rows)*N,results=rows,
       proof_indistinguishable_wire_drift_ohm=.1,
       implied_temperature_bias_K=.1/(3*.00393),
       notes=[
          "Measurements are fabricated complex phasors, NOT U/I from a speaker.",
          "Analytical joint inversion assumes Zm(f) unchanged by heating.",
          "A constant added series resistance cannot be separated from Re rise.",
          "Observation at several frequencies may be impossible during a given music passage; injection needs a separate safety analysis.",
          "No temperature thresholds, DSP integrations or hardware parts are approved."
       ])
    p=Path(__file__).resolve().parents[1]/"wyniki"/"p24e_wieloczestotliwosciowa_ident_20261031.json"
    p.parent.mkdir(exist_ok=True)
    p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"n":out["n_simulations"],"results":rows},ensure_ascii=False,indent=2))
if __name__=="__main__": main()
