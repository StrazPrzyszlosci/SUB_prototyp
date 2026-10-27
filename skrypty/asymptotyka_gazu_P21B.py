"""Niezależna asymptotyka swobodnej bryły w zadanym gradiencie ciśnienia.

Przy omega→0 stała amplituda siły daje ruch1/omega²;gradient gazu nie musi
zanikać. To granica transmitancji,wymaga skalowania amplitudy lub mocowania.
"""
from pathlib import Path
import csv,hashlib,json
import numpy as np
from analiza_wkladow_P20A import table

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def main():
    cp=ROOT/'dane/konfiguracje/p21b_gaz_przestrzenny_modulu.json';cfg=json.loads(cp.read_text());sp=ROOT/cfg['solid_config'];scfg=json.loads(sp.read_text())
    bp=ROOT/scfg['reference_insert_config'];base=json.loads(bp.read_text());status=json.loads((OUT/'p21b_podsumowanie.json').read_text());assert status['cases']==18
    with (OUT/'p21b_modele_i_geometria.csv').open() as f:models=list(csv.DictReader(f))
    with (OUT/'p21b_pola_i_energia.csv').open() as f:fields=list(csv.DictReader(f))
    with (OUT/'p21b_porownanie_z0D.csv').open() as f:comp=list(csv.DictReader(f))
    W,D,H=np.array(scfg['outer_width_depth_height_m']);inside=np.array([W,D,H])-2*scfg['wall_m'];force=W*D*H/W
    tie=base['internal_tie_reference'];ps=tie['pad_side_m'];pt=tie['pad_thickness_m'];rs=np.sqrt(tie['rod_area_m2']);g=scfg['glue_thickness_m_assumed']
    rows=[]
    for model in models:
        braced=model['braced']=='True';V=float(np.prod(inside));Ix=V*inside[0]**2/12
        if braced:
            pads=2*ps**2*(pt+g);rod=rs**2*(inside[1]-2*(pt+g));V-=pads+rod
            Ix-=pads*ps**2/12+rod*rs**2/12
        assert abs(V/(float(model['gas_volume_l'])*.001)-1)<1e-10
        sigma_x=np.sqrt(Ix/V);mdry=float(model['dry_solid_mass_kg']);mgas=float(model['gas_mass_kg']);rho=mgas/V
        predicted_std=rho*force/(mdry+mgas)*sigma_x;matrix_limit=mgas/(mdry+mgas)
        for freq in [20.,80.]:
            row=next(r for r in fields if r['case_id']==model['case_id'] and r['field']=='uniform_plus_x_gradient' and float(r['f_hz'])==freq)
            ratio=next(r for r in comp if r['case_id']==model['case_id'] and float(r['f_hz'])==freq)
            actual=float(row['pressure_deviation_volume_rms_pa']);actual_matrix=float(ratio['full_admittance_matrix_relative_change_to0D'])
            rows.append(dict(case_id=model['case_id'],f_hz=freq,gas_geometric_sigma_x_m=float(sigma_x),
                gas_mass_fraction_of_closed_module=float(matrix_limit),
                low_frequency_predicted_std_pa_per_modal_pa=float(predicted_std),computed_std_pa_per_modal_pa=actual,
                finite_frequency_std_relative_departure=float(actual/predicted_std-1),
                low_frequency_predicted_relative_matrix_error=float(matrix_limit),computed_relative_matrix_error=actual_matrix,
                finite_frequency_matrix_relative_departure=float(actual_matrix/matrix_limit-1),
                asymptotic_rigid_displacement_peak_m_per_modal_pa=float(np.sqrt(2)*force/((mdry+mgas)*(2*np.pi*freq)**2)),
                scope='Rigid-translation leading term as omega→0,positive fixed elastic stiffness,central force gradient,centred closed geometry;not exact finite-frequency solution.'))
    table('p21b_asymptotyka_swobodnego_ruchu.csv',rows)
    inputs=[cp,sp,bp,Path(__file__),OUT/'p21b_modele_i_geometria.csv',OUT/'p21b_pola_i_energia.csv',OUT/'p21b_porownanie_z0D.csv']
    j=dict(status='ANALYTIC_LOW_FREQUENCY_TRANSFER_LIMIT_NOT_FIXED_AMPLITUDE_PHYSICAL_OPERATION',rows=len(rows),
        derivation=['F=-Vouter*grad(Phi),through the centre;translation dominates elastic deformation as omega→0.',
            'a=F/(mdry+rho*Vgas),grad(p)=-rho*a;std(p)=rho*abs(F)*sigma_x/(mdry+mgas).',
            'For the force-carrying work port the scalar-Ci0D reference with DRY solid mass tends to relative matrix error mgas/(mdry+mgas),not to zero solely by lowering omega.'],
        max_std_departure_at20hz=max(abs(r['finite_frequency_std_relative_departure']) for r in rows if r['f_hz']==20.),
        max_matrix_departure_at20hz=max(abs(r['finite_frequency_matrix_relative_departure']) for r in rows if r['f_hz']==20.),
        input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        limitations=['At fixed forcing amplitude translation diverges as1/omega²;to remain in small-motion domain reduce amplitude with omega² or include supports.',
            'A reduced model can include a consistent rigid-fluid added-mass tensor;the limit is not a claim about every0Dmodel. Never add gas mass again to the full3Dfluid model.',
            'Finite20/80Hzdepartures are recorded,not forced to equal a zero-frequency asymptote.',
            'This does not claim the prescribed gradient is the actual main-cavity field.'])
    (OUT/'p21b_asymptotyka_podsumowanie.json').write_text(json.dumps(j,ensure_ascii=False,indent=2,allow_nan=False))
    print('P21B asymptote:',len(rows),'finite witnesses;maxstd departure20Hz',j['max_std_departure_at20hz'],flush=True)


if __name__=='__main__':main()
