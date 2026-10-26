"""P09C: geometria materiału oraz oddzielna warstwowa akustyka 1D.

Niezależne FV sieci p/Q sprawdza dokładne rozwiązanie warstwowe ZK.
Porównanie 27 konfiguracji obejmuje nowe SB. SI, fazory RMS, exp(+jwt).
"""
from pathlib import Path
import csv
import hashlib
import json
import os
import platform
os.environ.setdefault('MPLCONFIGDIR', '/tmp/sub-krystian-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import scipy
from scipy.linalg import solve_banded
from analiza_rozszerzenia_SB import candidates
from model_gazu import Medium
from model_wypelnienia import CircularPores, layer_impedance, response_with_acoustic_impedance

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'wyniki'
CFG=ROOT/'dane/konfiguracje/p09c_ilosc_i_rozmieszczenie_wypelnienia.json'


def layout(depth, thickness, position, material):
    if not 0<=thickness<=depth or position not in ['front','middle','back']:
        raise ValueError('Grubość warstwy w komorze i jawna pozycja')
    free=depth-thickness
    before,after={'front':(0.,free), 'middle':(free/2,free/2), 'back':(free,0.)}[position]
    return [(before,None), (thickness,material), (after,None)]


def ladder(f, area, layers, resolution, medium):
    """FV: masa między węzłami, po połowie podatności komórki na końcach.

    Bez funkcji cot i macierzy transferu. Neumann Q=1 na wejściu, Q=0 z tyłu.
    Całkowite p/Q, ze stratami lepkościowymi w rho i cieplnymi w 1/K.
    """
    depth=sum(d for d,m in layers)
    impedance=[]
    capacity=[]
    s=2j*np.pi*f
    for d,material in layers:
        if d<=0:continue
        cells=max(1,int(np.ceil(resolution*d/depth)))
        h=d/cells
        if material is None:rho,bulk=medium.rho,medium.gamma*medium.p0_pa
        else:
            rh,bu=material.equivalent_properties(np.array([f]),medium)
            rho,bulk=rh[0],bu[0]
        impedance.extend([s*rho*h/area]*cells)
        capacity.extend([area*h/bulk]*cells)
    z=np.array(impedance)
    cell_c=np.array(capacity)
    n=len(z)
    node_y=np.zeros(n+1,complex)
    node_y[:-1]+=s*cell_c/2
    node_y[1:]+=s*cell_c/2
    edge_y=1/z
    diagonal=node_y.copy()
    diagonal[:-1]+=edge_y
    diagonal[1:]+=edge_y
    ab=np.zeros((3,n+1),complex)
    ab[1]=diagonal
    ab[0,1:]=-edge_y
    ab[2,:-1]=-edge_y
    rhs=np.zeros(n+1,complex)
    rhs[0]=1.
    p=solve_banded((1,1),ab,rhs)
    flow=(p[:-1]-p[1:])/z
    loss=np.sum(z.real*abs(flow)**2)+np.sum(node_y.real*abs(p)**2)
    norm=max(abs(p[0]),abs(loss),1.)
    return p[0], float(abs(p[0].real-loss)/norm), n


def write(name, rows):
    with (OUT/name).open('w',newline='',encoding='utf-8') as h:
        w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def save(fig,name):
    fig.tight_layout()
    for ext in ['png','svg']:fig.savefig(OUT/f'{name}.{ext}',dpi=170)
    plt.close(fig)


def main():
    cfg=json.loads(CFG.read_text())
    medium=Medium()
    width,depth,height=cfg['inside_width_depth_height_m']
    reference=json.loads((ROOT/cfg['reference_geometry']).read_text())
    assert cfg['inside_width_depth_height_m']==reference['inside_m']
    area=width*height
    volume=area*depth
    phi=cfg['geometric_porosity_assumed']
    cp_s=cfg['solid_specific_heat_j_kg_k_assumed']
    geometry=[]
    for faces in cfg['liner_faces']:
        for t in cfg['liner_thickness_m']:
            assert 2*t<min(width,height) and (1 if faces==5 else 2)*t<depth
            # Odejmowanie rdzenia zachowuje naroża bez wielokrotnego liczenia.
            core=(width-2*t)*(height-2*t)*(depth-(1 if faces==5 else 2)*t)
            vp=volume-core
            for density in cfg['dry_bulk_density_kg_m3_assumed']:
                mass=density*vp
                pore_air=phi*vp
                cg=medium.p0_pa*pore_air/((medium.gamma-1)*medium.temperature_k)
                cs=mass*cp_s
                low_k_factor=1+(medium.gamma-1)*cg/(cg+cs)
                geometry.append(dict(faces=faces,thickness_mm=t*1000,dry_bulk_density_kg_m3=density,
                    geometry_before_material_l=volume*1000,porous_envelope_l=vp*1000,
                    free_core_l=core*1000,solid_displacement_l=(1-phi)*vp*1000,
                    accessible_gas_l=(core+pore_air)*1000,dry_mass_kg=mass,
                    assumed_solid_cp_j_kg_k=cp_s,local_Cs_Cg=cs/cg,
                    equivalent_adiabatic_volume_l=(core+pore_air)*1000,
                    equivalent_isothermal_pores_adiabatic_core_l=(core+medium.gamma*pore_air)*1000,
                    equivalent_finite_Cs_isolated_pores_adiabatic_core_l=(core+medium.gamma*pore_air/low_k_factor)*1000))
    write('p09c_geometria_masa_i_podatnosc.csv',geometry)
    freq=np.array(cfg['probe_frequencies_hz'])
    empty=layer_impedance(freq,area,[(depth,None)],medium)
    pool=candidates()
    base={cid:response_with_acoustic_impedance(d,freq,empty,medium=medium) for cid,pid,d,cat in pool}
    materials=[('EMPTY',None,0.,'back')]
    for radius in cfg['pore_radius_m']:
        for frame in cfg['frame_conditions']:
            mat=CircularPores(radius,phi,frame,cfg['dynamic_dry_density_kg_m3_assumed'])
            for t in cfg['layer_1d_depth_m']:
                for pos in cfg['layer_1d_positions']:
                    materials.append((f'{frame}_a{radius:g}_t{t:g}_{pos}',mat,t,pos))
    rows=[]
    acoustic=[]
    max_energy=max_low=0.
    min_real_z=np.inf
    for mid,mat,t,pos in materials:
        layers=layout(depth,t,pos,mat)
        z=layer_impedance(freq,area,layers,medium)
        eq=medium.gamma*medium.p0_pa/(2j*np.pi*freq*z)
        min_real_z=min(min_real_z,float(z.real.min()))
        if mat is not None:
            low=layer_impedance(np.array([1e-6]),area,layers,medium)[0]
            expected=(volume-area*t+medium.gamma*phi*area*t)/(medium.gamma*medium.p0_pa)
            max_low=max(max_low,float(abs(1/(2j*np.pi*1e-6*low)/expected-1)))
        for k,f in enumerate(freq):
            acoustic.append(dict(model_id=mid,f_hz=float(f),position=pos,
                layer_mm=t*1000,porous_envelope_l=area*t*1000,
                dry_mass_kg=area*t*cfg['dynamic_dry_density_kg_m3_assumed'],
                accessible_gas_l=(volume-(1-phi)*area*t)*1000,
                acoustic_R_pa_s_m3=float(z[k].real),acoustic_X_pa_s_m3=float(z[k].imag),
                equivalent_storage_l=float(eq[k].real*1000),equivalent_loss_l=float(-eq[k].imag*1000)))
        for cid,pid,d,cat in pool:
            one=response_with_acoustic_impedance(d,freq,z,medium=medium)
            max_energy=max(max_energy,float(np.max(abs(one['energy_residual_w'])/one['p_input_w'])))
            allowed_x=cfg['fraction_of_catalog_xmax']*d.xmax_mm*.001
            for vmax,imax in cfg['amplifier_scenarios_vrms_irms']:
                voltage=np.minimum(vmax,np.minimum(imax/one['i_rms_a'],allowed_x/one['x_peak_m']))
                bv=np.minimum(vmax,np.minimum(imax/base[cid]['i_rms_a'],allowed_x/base[cid]['x_peak_m']))
                for k,f in enumerate(freq):
                    limits=[vmax,imax/one['i_rms_a'][k],allowed_x/one['x_peak_m'][k]]
                    rows.append(dict(configuration_id=cid,product_id=pid,model_id=mid,
                        f_hz=float(f),amp_v_rms=vmax,amp_i_rms=imax,
                        spl_rms_2pi_1m_db=float(one['spl_equivalent_db'][k]+20*np.log10(voltage[k])),
                        delta_fixed_voltage_to_empty_1d_db=float(one['spl_equivalent_db'][k]-base[cid]['spl_equivalent_db'][k]),
                        delta_limited_to_empty_1d_db=float(one['spl_equivalent_db'][k]+20*np.log10(voltage[k])-base[cid]['spl_equivalent_db'][k]-20*np.log10(bv[k])),
                        u_rms_v=float(voltage[k]),i_rms_a=float(one['i_rms_a'][k]*voltage[k]),
                        x_peak_mm=float(one['x_peak_m'][k]*voltage[k]*1000),
                        copper_w=float(one['p_copper_w'][k]*voltage[k]**2),
                        acoustic_loss_w=float(one['p_porous_w'][k]*voltage[k]**2),
                        active_limit=['voltage','current','catalog_x'][int(np.argmin(limits))]))
    assert len(materials)==55 and len(rows)==17820 and len(acoustic)==330
    assert min_real_z>=-1e-8 and max_energy<1e-10 and max_low<2e-5
    write('p09c_warstwy_i_straty.csv',acoustic)
    write('p09c_naped_i_wypelnienie.csv',rows)
    witnesses=[]
    max_network_energy=0.
    for mid,mat,t,pos in [materials[0]]+[(pos,CircularPores(.0002,phi,'rigid',20.),.05,pos) for pos in ['front','middle','back']]:
        layers=layout(depth,t,pos,mat)
        for f in [20.,80.,125.,300.]:
            target=layer_impedance(np.array([f]),area,layers,medium)[0]
            for n in [32,64,128,256,512]:
                z,err,cells=ladder(f,area,layers,n,medium)
                max_network_energy=max(max_network_energy,err)
                witnesses.append(dict(model_id=mid,f_hz=f,resolution=n,cells=cells,
                    relative_complex_impedance_error=float(abs(z/target-1)),network_energy_error=err))
    last=[r for r in witnesses if r['resolution']==512]
    assert max(r['relative_complex_impedance_error'] for r in last)<3e-4
    assert max_network_energy<1e-8
    # Wzorzec braku materiału i pełna warstwa nie zależą od arbitralnej lokalizacji.
    mat=CircularPores(.0002,phi,'rigid',20.)
    degenerate_error=0.
    for t in [0.,depth]:
        target=layer_impedance(freq,area,[(depth,None if t==0 else mat)],medium)
        for pos in ['front','middle','back']:
            found=layer_impedance(freq,area,layout(depth,t,pos,mat),medium)
            degenerate_error=max(degenerate_error,float(np.max(abs(found/target-1))))
    assert degenerate_error<1e-12
    write('p09c_niezalezna_siec_i_zbieznosc.csv',witnesses)
    # Geometria wyklejenia: osobny eksperyment od poprzecznej warstwy 1D.
    fig,ax=plt.subplots(1,2,figsize=(12,4.8))
    for color,density in zip(['#258299','#cf7200','#6956a5'],cfg['dry_bulk_density_kg_m3_assumed']):
        for faces in cfg['liner_faces']:
            g=[r for r in geometry if r['faces']==faces and r['dry_bulk_density_kg_m3']==density]
            ax[0].plot([r['thickness_mm'] for r in g],[r['dry_mass_kg'] for r in g],
                       marker='o',color=color,linestyle='-' if faces==5 else '--',label=f'{density:g} kg/m³, {faces} ścian')
    ax[0].set(xlabel='Grubość wyklejenia [mm]',ylabel='Masa suchego materiału [kg]',title='Założone gęstości; naroża liczone jednokrotnie')
    ax[0].legend(fontsize=8,ncol=2)
    g=[r for r in geometry if r['faces']==5 and r['dry_bulk_density_kg_m3']==20]
    for field,label,color in [('accessible_gas_l','Rzeczywista objętość gazu','#258299'),
                              ('equivalent_isothermal_pores_adiabatic_core_l','Veq: pory izotermiczne','#cf7200'),
                              ('equivalent_finite_Cs_isolated_pores_adiabatic_core_l','Veq: skończone Cs, Cp umowne','#6956a5')]:
        ax[1].plot([r['thickness_mm'] for r in g],[r[field] for r in g],marker='o',label=label,color=color)
    ax[1].axhline(volume*1000,color='gray',ls=':',label='Pusta geometria')
    ax[1].set(xlabel='Grubość wyklejenia pięciu ścian [mm]',ylabel='Objętość lub Veq [l]',title='Phi=0,98; rdzeń adiabatyczny w tym modelu')
    ax[1].legend(fontsize=8)
    for a in ax:a.grid(alpha=.25)
    fig.suptitle('Komora 460 × 640 × 460 mm; przed odjęciem kosza/ściągów',fontsize=11)
    save(fig,'62_P09C_masa_materialu_i_objetosc_gazu')
    fig,ax=plt.subplots(1,2,figsize=(12,4.8))
    fplot=np.geomspace(10,300,350)
    fband=np.geomspace(20,120,250)
    d={cid:d for cid,pid,d,cat in pool}['C04']
    emptyband=layer_impedance(fband,area,[(depth,None)],medium)
    eb=response_with_acoustic_impedance(d,fband,emptyband,medium=medium)
    vb=np.minimum(40.,np.minimum(12/eb['i_rms_a'],d.xmax_mm*.001/eb['x_peak_m']))
    for pos,label,color in zip(['front','middle','back'],['Przy froncie','W środku','Przy tylnej ścianie'],['#cf7200','#6956a5','#258299']):
        layers=layout(depth,.05,pos,mat)
        z=layer_impedance(fplot,area,layers,medium)
        ax[0].semilogx(fplot,z.real,label=label,color=color)
        zband=layer_impedance(fband,area,layers,medium)
        o=response_with_acoustic_impedance(d,fband,zband,medium=medium)
        v=np.minimum(40.,np.minimum(12/o['i_rms_a'],d.xmax_mm*.001/o['x_peak_m']))
        delta=o['spl_equivalent_db']+20*np.log10(v)-eb['spl_equivalent_db']-20*np.log10(vb)
        ax[1].semilogx(fband,delta,label=label,color=color)
    ax[0].set(xlabel='Częstotliwość [Hz]',ylabel='Re(Zin) [Pa·s/m³]',title='Ta sama masa ≈0,212 kg; różne straty wejścia')
    ax[0].set_yscale('log')
    ax[1].set(xlabel='Częstotliwość [Hz]',ylabel='Zmiana granicy SPL względem pustej 1D [dB]',title='C04: 40 V RMS / 12 A RMS, katalogowe X peak')
    ax[1].axhline(0,color='gray',lw=.8)
    for a in ax:a.grid(True,which='both',alpha=.25);a.legend(fontsize=8)
    fig.suptitle('Warstwa 50 mm przez cały przekrój; szkielet rigid, a=200 µm, phi=0,98',fontsize=11)
    save(fig,'63_P09C_polozenie_warstwy_i_naped')
    paths=[CFG,ROOT/cfg['reference_geometry'],ROOT/'skrypty/model_wypelnienia.py',
           ROOT/'skrypty/model_gazu.py',ROOT/'skrypty/model_subwoofera.py',
           ROOT/'skrypty/analiza_rozszerzenia_SB.py',Path(__file__),
           ROOT/'dane/przetworniki/pula_rozszerzona.json',ROOT/'dane/przetworniki/rozszerzenie_SB_20261025.json',
           ROOT/'dane/zrodla/P09_P10_materialy_i_sorpcja.json',ROOT/'brief_system_audio_DIY_v0.6.md']
    result=dict(status='CONDITIONAL_FILL_GEOMETRY_AND_1D_PLACEMENT_NOT_PRODUCT_IDENTIFICATION',date='2026-10-26',
        cases=dict(geometries=len(geometry),acoustic_models=len(materials),acoustic_frequency_rows=len(acoustic),
                   drive_frequency_cases=len(rows),electrical_configurations=len(pool),independent_ladder_solves=len(witnesses)),
        checks=dict(max_driver_energy_relative_error=max_energy,min_real_acoustic_impedance=min_real_z,
                    low_frequency_compliance_max_relative_error=max_low,
                    max_last_mesh_relative_impedance_error=max(r['relative_complex_impedance_error'] for r in last),
                    network_max_normalized_energy_error=max_network_energy,zero_full_layer_error=degenerate_error),
        libraries=dict(Python=platform.python_version(),NumPy=np.__version__,SciPy=scipy.__version__,Matplotlib=matplotlib.__version__),
        input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
        limitations=cfg['gates'])
    (OUT/'p09c_podsumowanie.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print(json.dumps(dict(cases=result['cases'],checks=result['checks']),ensure_ascii=False))


if __name__=='__main__':main()
