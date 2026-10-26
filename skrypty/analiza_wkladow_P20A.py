"""P20A: droga montażu, masa, podatność zamkniętych wkładów i mocowania.

Modele warunkowe. Ciśnienie jednolite na całej zamkniętej bryle nie daje
siły p*A na jej mocowanie; siły poszczególnych paneli liczymy osobno.
"""
from pathlib import Path
from itertools import product
import csv,hashlib,json,platform
import numpy as np
import scipy
from geometria_wkladow_P20A import packing,obstacles,liner_envelope_volume
from model_wkladu_P20A import HollowModule
from model_gazu import Medium

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki';CFG=ROOT/'dane/konfiguracje/p20a_regulacja_objetosci.json'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def table(name,rows):
    keys=list(dict.fromkeys(k for r in rows for k in r))
    with (OUT/name).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)


def module_cases(cfg):
    for k,((a,b),c,h,bc) in enumerate(product(cfg['module_cross_sections_width_height_m'],cfg['module_lengths_m'],cfg['module_wall_thickness_m'],cfg['module_boundary_assumptions'])):
        yield f'M{k:03d}',(a,c,b),h,bc,False
    outer=tuple(cfg['selected_comparison_outer_width_length_height_m'])
    for h,bc in product(cfg['module_wall_thickness_m'],cfg['module_boundary_assumptions']):
        yield f'TIE_{int(h*1000)}_{bc}',outer,h,bc,True


def mount_rows(cid,outer,mass,cfg):
    a,c,b=outer;sx=a-2*cfg['mount_support_inset_m'];sy=c-2*cfg['mount_support_inset_m'];height=b/2
    assert min(sx,sy)>0
    rows=[]
    for ax,ay,az in cfg['mount_acceleration_xyz_m_s2']:
        normals=[mass*(9.80665+az)/4+ix*mass*ax*height/(2*sx)+iy*mass*ay*height/(2*sy) for ix,iy in product([-1,1],repeat=2)]
        rows.append(dict(module_id=cid,mass_kg=mass,ax_m_s2=ax,ay_m_s2=ay,az_m_s2=az,
            minimum_signed_normal_n=min(normals),maximum_normal_compression_n=max(max(normals),0),
            required_tensile_hold_per_point_n=max(-min(normals),0),equal_shear_per_point_n=mass*np.hypot(ax,ay)/4,
            mean_compression_patch_pa=max(max(normals),0)/cfg['mount_contact_patch_side_m_assumed']**2,
            contact_only_feasible=min(normals)>=0))
    dynamic=[];zeta=cfg['mount_damping_ratio_assumed'];acc=cfg['mount_base_acceleration_rms_m_s2']
    for k in cfg['mount_each_stiffness_n_m']:
        total=4*k;w0=np.sqrt(total/mass);damping=2*zeta*np.sqrt(total*mass)
        freqs=sorted(set(cfg['probe_frequencies_hz']+[float(w0/(2*np.pi))]))
        for f in freqs:
            w=2*np.pi*f;relative=mass*acc/abs(total-mass*w*w+1j*w*damping)
            reaction=abs(total+1j*w*damping)*relative
            dynamic.append(dict(module_id=cid,mass_kg=mass,support_each_n_m=k,mount_frequency_hz=w0/(2*np.pi),f_hz=f,
                base_acceleration_rms_m_s2=acc,relative_motion_rms_m=relative,transmitted_force_rms_n=reaction,
                normal_contact_change_flag=np.sqrt(2)*reaction>mass*9.80665,
                scope='Linear held base-excitation model; flag excludes loose contact-only interpretation.'))
    return rows,dynamic


def main():
    cfg=json.loads(CFG.read_text());medium=Medium()
    parent=json.loads((ROOT/'dane/konfiguracje/p18c_rama_3D.json').read_text())
    assert cfg['inside_width_depth_height_m']==parent['inside_m']
    layouts=[];geometry=[];mount=[];mount_dynamic=[]
    for index,((a,b),c) in enumerate(product(cfg['module_cross_sections_width_height_m'],cfg['module_lengths_m'])):
        outer=(a,c,b);V=float(np.prod(outer));solid_mass=cfg['mdf_density_kg_m3_assumed']*V
        geometry.append(dict(geometry_id=f'G{index:02d}',outer_a_m=a,outer_depth_m=c,outer_b_m=b,volume_l=V*1000,solid_mdf_mass_kg=solid_mass))
        ms,md=mount_rows(f'SOLID_G{index:02d}',outer,solid_mass,cfg);mount+=ms;mount_dynamic+=md
        for aperture,ties in product(cfg['nominal_opening_diameters_m'],cfg['brace_counts']):layouts.append(packing(cfg,outer,aperture,ties))
    table('p20a_geometria_masywu.csv',geometry)
    table('p20a_dostep_i_uklad.csv',[{k:v for k,v in r.items() if k not in ['paths','final_boxes','scope']} for r in layouts])
    (OUT/'p20a_tory_montazu.json').write_text(json.dumps(dict(status='CONSTRUCTIVE_AXIS_ALIGNED_PATHS_NOT_GLOBAL_PACKING_OPTIMUM',layouts=layouts),ensure_ascii=False,indent=2))
    hard=obstacles(cfg,1);liner=liner_envelope_volume(cfg,hard)
    balance=dict(host_geometry_l=np.prod(cfg['inside_width_depth_height_m'])*1000,
        fixed_explicit_solids_l=sum(b.volume for b in hard)*1000,
        liner_envelope_after_hard_intersections_l=liner*1000,
        liner_solid_volume_l=(1-cfg['lining_geometric_porosity_assumed'])*liner*1000,
        liner_dry_mass_kg=cfg['lining_dry_density_kg_m3_assumed']*liner,
        note='Explicit nonoverlapping P20 brace envelope differs from older lumped rod/pad representation; no driver displacement guessed.')
    rows=[];ports=[];temperatures=[];max_power=0.;min_real_y=np.inf
    f=np.array(cfg['probe_frequencies_hz']);leaks=[np.inf if x=='inf' else x for x in cfg['module_leak_rigid_gas_corner_hz']]
    for cid,outer,h,bc,braced in module_cases(cfg):
        m=HollowModule(outer,h,bc,cfg,braced=braced)
        row=dict(module_id=cid,outer_a_m=outer[0],outer_depth_m=outer[1],outer_b_m=outer[2],wall_mm=h*1000,boundary=bc,
            braced=braced,outer_volume_l=m.outer_volume*1000,inner_gas_volume_l=m.inner_volume*1000,
            dry_mass_kg=m.dry_mass,mass_with_sealed_air_kg=m.mass_with_sealed_air,
            static_wall_compliance_m3_pa=m.chi_static,lowest_active_panel_hz=float(min(np.sqrt(p.eigenvalues[0])/(2*np.pi) for p in m.faces)),
            pressure_coupled_frequency_kappa14_hz=m.pressure_mode_frequency(),
            max_static_modal_relative_error=max(p.static_modal_relative_error for p in m.faces),
            peak_wall_unit_pressure_m=m.peak_w_per_pa,
            volume_occupied_by_inner_tie_l=0. if m.tie is None else m.tie['occupied_volume_m3']*1000)
        rows.append(row)
        for kappa,corner in product(cfg['internal_gas_kappa_cases'],leaks):
            r=m.port(f,kappa,corner,medium);y=r['admittance'];min_real_y=min(min_real_y,float(y.real.min()))
            denom=np.maximum(abs(y),1e-30);max_power=max(max_power,float(max(abs(r['power_residual_per_outer_pa2_w'])/denom)))
            for j,freq in enumerate(f):
                returned=medium.gamma*medium.p0_pa*r['effective_compliance'][j]*1000
                ports.append(dict(module_id=cid,kappa_inside=kappa,rigid_gas_leak_corner_hz='inf' if np.isposinf(corner) else corner,
                    f_hz=float(freq),returned_compliance_storage_l=float(returned.real),returned_compliance_loss_l=float(-returned.imag),
                    effective_excluded_storage_l=float(m.outer_volume*1000-returned.real),
                    admittance_real_m3_pa_s=float(y[j].real),admittance_imag_m3_pa_s=float(y[j].imag),
                    wall_loss_w_per_outer_pa_rms2=float(r['wall_loss_per_outer_pa2_w'][j]),leak_loss_w_per_outer_pa_rms2=float(r['leak_loss_per_outer_pa2_w'][j])))
        for dT,dp in product(cfg['temperature_inside_shifts_k'],cfg['outer_module_pressure_shifts_pa']):
            r=m.sealed_temperature_equilibrium(dT,dp,medium);delta=r['pressure_difference_pa']
            # Biaxial SSSS diagnostic Nx=Ny=p*normal_span/2, not a closed-box buckling capacity.
            proxy=min(2*p.plate.material.rigidity_nm*np.pi**2*(1/p.plate.a**2+1/p.plate.b**2)/m.inside[axis] for axis,p in enumerate(m.faces))
            temperatures.append(dict(module_id=cid,delta_inside_temperature_k=dT,delta_outer_pressure_pa=dp,**r,
                within_assumed_small_deflection_domain=r['w_over_t']<=cfg['linear_plate_w_over_t_limit_assumed'],
                sampled_bending_stress_bound_pa=abs(delta)*max(p.bending_stress_per_pa for p in m.faces),
                sampled_edge_moment_peak_n=abs(delta)*max(p.edge_moment_per_pa for p in m.faces),
                maximum_active_face_pressure_force_n=abs(delta)*max(p.plate.a*p.plate.b for p in m.faces),
                biaxial_ssss_pressure_proxy_pa=proxy,abs_pressure_to_biaxial_proxy=abs(delta)/proxy))
        ms,md=mount_rows(cid,outer,m.mass_with_sealed_air,cfg);mount+=ms;mount_dynamic+=md
        print('P20A module:',cid,bc,'wall',h,'mass',m.dry_mass,flush=True)
    assert len(rows)==78 and len(layouts)==108 and len(ports)==5616 and len(temperatures)==702
    assert min_real_y>=-1e-15 and max_power<1e-10
    table('p20a_moduly_i_sciany.csv',rows);table('p20a_porty_modulow.csv',ports);table('p20a_temperatura_i_cisnienie.csv',temperatures)
    table('p20a_wymagania_mocowan.csv',mount);table('p20a_dynamika_mocowan.csv',mount_dynamic)
    inputs=[CFG,Path(__file__),ROOT/'skrypty/geometria_wkladow_P20A.py',ROOT/'skrypty/model_wkladu_P20A.py',ROOT/'skrypty/model_plyty_MITC_P18.py',
            ROOT/'skrypty/model_gazu.py',ROOT/'skrypty/model_subwoofera.py',ROOT/'dane/konfiguracje/p18c_rama_3D.json',ROOT/'dane/zrodla/P18B_geometria_i_ograniczenia.json',ROOT/'brief_system_audio_DIY_v0.6.md']
    result=dict(status='INSERT_GEOMETRY_FLEXIBLE_SHELL_LEAK_AND_MOUNT_FAMILIES_NOT_FINAL_CNC_OR_STRENGTH',date='2026-10-26',
        cases=dict(layouts=len(layouts),module_models=len(rows),port_rows=len(ports),thermal_states=len(temperatures),mount_static_rows=len(mount),mount_dynamic_rows=len(mount_dynamic)),
        balances=balance,checks=dict(max_module_power_normalized_residual=max_power,min_real_module_admittance=min_real_y,
        flagged_temperature_domain_rows=sum(not r['within_assumed_small_deflection_domain'] for r in temperatures)),
        libraries=dict(Python=platform.python_version(),NumPy=np.__version__,SciPy=scipy.__version__),
        input_sha256={str(p.relative_to(ROOT)):sha(p) for p in inputs},limitations=cfg['gates'])
    (OUT/'p20a_podsumowanie.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print('P20A COMPLETE:',result['cases'],result['checks'],flush=True)


if __name__=='__main__':main()
