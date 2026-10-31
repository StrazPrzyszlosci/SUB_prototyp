#!/usr/bin/env python3
"""P24C: structural vs practical identifiability of voice-coil temperature
from coherent terminal voltage/current. All errors are assumed test scenarios.
Deterministic simulations; no hardware validation.
"""
import json, math
import numpy as np

M = dict(fs=19.5, qms=3.02, vas_l=212, mms_g=306,
         bl=15, sd_cm2=829.6, re0=3, le_mh=.92,
         alpha=.00393, rho=1.2, c=343)
FREQ = (20, 40, 80, 150, 300)
VOL_L=80.
N=10000
SEED=20261031

def impedance(f, dT=0, bl=None, qms=None, vol_l=VOL_L):
    sd=M['sd_cm2']*1e-4
    mms=M['mms_g']*1e-3
    bl=M['bl'] if bl is None else bl
    qms=M['qms'] if qms is None else qms
    cms=(M['vas_l']*.001)/(M['rho']*M['c']**2*sd**2)
    w=2*math.pi*f
    zm=complex(2*math.pi*M['fs']*mms/qms,
               w*mms-1/(w*cms)-sd*sd*M['rho']*M['c']**2/(w*vol_l*.001))
    return M['re0']*(1+M['alpha']*dT)+1j*w*M['le_mh']*.001+bl**2/zm

def estimate_delta_temperature(z_hot, z_cold):
    return (z_hot.real-z_cold.real)/(M['re0']*M['alpha'])

rng=np.random.default_rng(SEED)
rows=[]
for f in FREQ:
    z0=impedance(f)
    z80=impedance(f,80)
    dz=estimate_delta_temperature(z80,z0)
    a0=rng.normal(0,.005,N); a1=rng.normal(0,.005,N)
    p0=rng.normal(0,math.radians(.2),N)
    p1=rng.normal(0,math.radians(.2),N)
    noisy_z0=z0*(1+a0)*np.exp(1j*p0)
    noisy_z1=z80*(1+a1)*np.exp(1j*p1)
    estimated=(noisy_z1.real-noisy_z0.real)/(M['re0']*M['alpha'])
    rmse=math.sqrt(float(np.mean((estimated-80)**2)))
    p95=float(np.quantile(abs(estimated-80),.95))
    d_bl_1pct=estimate_delta_temperature(impedance(f,80,bl=M["bl"]*.99),z0)-80
    d_bl_3pct=estimate_delta_temperature(impedance(f,80,bl=M["bl"]*.97),z0)-80
    drift_1pct=estimate_delta_temperature(z80*1.01,z0)-80
    wire_0p1ohm=.1/(M['re0']*M['alpha'])
    rows.append(dict(f_hz=f,
        z_cold_ohm_abs=round(abs(z0),4),
        z_cold_ohm_real=round(z0.real,4),
        z_hot80_ohm_real=round(z80.real,4),
        ideal_delta_K=round(dz,5),
        rmse_K_noise_assumed=round(rmse,2),
        p95_abs_error_K_noise_assumed=round(p95,2),
        gain_drift_1pct_bias_K=round(drift_1pct,2),
        bl_drop_1pct_bias_K=round(d_bl_1pct,2),
        bl_drop_3pct_bias_K=round(d_bl_3pct,2),
        external_resistance_drift_0p1ohm_bias_K=round(wire_0p1ohm,2)))

Cc=40; Rcm=.6; Cm=1000; Rma=1.5
A=[[-1/(Cc*Rcm),1/(Cc*Rcm)],
   [1/(Cm*Rcm),-(1/Rcm+1/Rma)/Cm]]
det_observability=1/(Cc*Rcm)
out={
    'study':'P24C preliminary numerical observability, not an equipment measurement',
    'base_commit':'52ebf1de02f2211cf7c9238c65ec8ecd41d9dd67',
    'driver':'RSS390HF-4 C02 nominal as used in P24B',
    'volume_l':VOL_L,
    'assumptions':{
        'delta_T_true_K':80,'noise_rms_ratio_fraction':.005,
        'noise_phase_std_deg':.2,'cold_and_hot_noise':'independent',
        'samples_per_frequency':N,'rng_seed':SEED,
        'model':'P24B linear small-signal fixed BL Cms Le and simple motional impedance',
        'gain_drift_hot_vs_cold_fraction':.01,
        'BL_drop_hot_vs_cold_fraction':[.01,.03],
        'external_resistance_drift_ohm':.1,
        'error_terms':'hypothetical not instrument specifications or measured driver drifts'},
    're_ohm_per_K':M['re0']*M['alpha'],
    'state_matrix_A':A,
    'observability_determinant':det_observability,
    'rows':rows,
    'interpretation':[
        'With known Re0 and nonzero alpha, Tc is structurally identifiable from calibrated terminal impedance under fixed mechanical parameters.',
        'The 2-state coil/motor model is structurally observable from Tc(t) when Rcm and Cc are finite, but structural observability does not calibrate its Rth Cth or guarantee useful noise tolerance.',
        'Coherent U and I at the speaker terminals are required; a line-level DSP output meter is not a terminal-current sensor.',
        'These calculations do not validate operation of the proposed protection on miniDSP and do not authorize final T or X limits.'
    ]
}
if __name__=='__main__':
    print(json.dumps(out,ensure_ascii=False,indent=2))
