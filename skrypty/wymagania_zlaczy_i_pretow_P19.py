"""P19: wynikowe obciążenia krawędzi i referencyjne granice pręta.

Naprężenia połączeń są wymaganiami określonego modelu/średniej długości,
nie dowodem maksymalnej lokalnej nośności lub trwałości kleju.
"""
import csv
import json
from pathlib import Path
import numpy as np
from analiza_plyt_i_sciagow_P18A import jobs,build_case,reference_E

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'wyniki'


def table(name,rows):
    with (OUT/name).open('w',newline='') as h:
        w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def maximum_force_average(coords,forces,length,window):
    if window>length:window=length
    starts=np.unique(np.clip(np.r_[0.,length-window,coords,coords-window],0.,length-window))
    # Reakcje węzłowe są rozkładem dyskretnym; wynik to zdefiniowana średnia,
    # nie nieskończony peak w punkcie/narożniku.
    values=[abs(sum(forces[(coords>=start-1e-10)&(coords<=start+window+1e-10)]))/window for start in starts]
    return float(max(values))


def main():
    cfg=json.loads((ROOT/'dane/konfiguracje/p18a_plyty_i_sciagi.json').read_text());data=json.loads((ROOT/'dane/materialy/mdf_i_kleje_P18_P19.json').read_text())
    summary=json.loads((OUT/'p18a_podsumowanie.json').read_text());cache=ROOT/summary['checkpoint_folder']
    with (OUT/'p18a_plyty_i_sciagi.csv').open() as h:rows=list(csv.DictReader(h))
    buckling=[]
    for r in rows:
        if int(r['tie_count'])==0:continue
        geom=next(g for g in cfg['geometries'] if g['id']==r['geometry_id']);profile=next(g for g in cfg['materials'] if g['id']==r['material_id'])
        E=reference_E(cfg['tie_thickness_m']*1000,data)['bending_modulus_pa']*profile['E_factor']
        t=cfg['tie_thickness_m'];b=cfg['tie_width_m'];I=min(b*t**3,t*b**3)/12
        for effective in [1.,2.]:
            Pcrit=np.pi*np.pi*E*I/(effective*geom['tie_length_m'])**2
            force=float(r['static_max_tie_axial_force_n']);dynamic=float(r.get('max_dynamic_tie_force_n') or 0.)
            buckling.append(dict(case_id=r['case_id'],geometry_id=r['geometry_id'],boundary=r['boundary'],tie_count=int(r['tie_count']),
                effective_length_factor=effective,E_bending_proxy_pa=E,Euler_reference_force_n=float(Pcrit),
                static_force_to_Euler_reference=float(force/Pcrit),dynamic_fixture_force_to_Euler_reference=float(dynamic/Pcrit),
                rod_area_m2=t*b,static_axial_stress_pa=float(force/(t*b)),
                scope='LINIOWY_IDEALNY_PRET_BEZ_IMPERFEKCJI_CREEP_SN;EFEKTYWNA_DLUGOSC_TO_STRES_NIE_IDENTYFIKACJA_MOCOWANIA'))
    table('p19a_pret_sily_i_odniesienie_Eulera.csv',buckling)
    edges=[];cases=jobs(cfg)
    for case in cases:
        if not(case['geometry']['id']=='K2_side' and case['thickness_mm']==22 and case['material']['id']=='REFERENCE' and
               case['boundary'] in ['SSSS','CCCC'] and case['zeta']==.03 and 'joint_factor' not in case and 'edge_beta' not in case):continue
        # Lokalne reakcje/momenty wymagają drobniejszej siatki niż samef1/w.
        refined_cfg=dict(cfg,mesh_short_n=40)
        p,K,M,ties,prop=build_case(case,refined_cfg,data);q=p.static(K);U=p.expand(q)
        rod=np.zeros_like(q)
        for tie in ties:rod+=2*tie['stiffness_n_m']*(tie['patch']@q)*tie['patch']
        residual=p.full_K@U-p.full_F+p.expand(rod)
        wres=residual[0::3];x=p.xy[:,0];y=p.xy[:,1]
        balance=abs(sum(wres)+p.a*p.b-sum(2*r['stiffness_n_m']*(r['patch']@q) for r in ties))/(p.a*p.b)
        assert balance<1e-8
        for name,mask,coord,length in [('x0',np.isclose(x,0),y,p.b),('x1',np.isclose(x,p.a),y,p.b),('y0',np.isclose(y,0),x,p.a),('y1',np.isclose(y,p.b),x,p.a)]:
            ids=np.flatnonzero(mask);forces=wres[ids].copy();coordinates=coord[ids]
            forces[np.isclose(coordinates,0)|np.isclose(coordinates,length)]*=.5
            for averaging in [.022,.05,.1]:
                Q=maximum_force_average(coordinates,forces,length,averaging)*cfg['static_pressure_peak_pa']
                for glue_width in [.012,.018,.022]:
                    # Mn=0 dla idealnegoSSSS jest warunkiemnaturalnym,
                    # nie wolno użyć reszty dyskretyzacji jako realnego odrywania.
                    moment=0. if case['boundary']=='SSSS' else p.edge_moment_peak(q)*cfg['static_pressure_peak_pa']
                    edges.append(dict(case_id=case['case_id'],boundary=case['boundary'],tie_count=case['tie_count'],edge=name,
                        averaging_length_m=averaging,glue_width_m=glue_width,
                        mesh_nx=p.nx,mesh_ny=p.ny,averaging_at_least_two_mesh_lengths=averaging>=2*max(p.dx,p.dy),
                        maximum_defined_average_transverse_force_n_m=Q,
                        average_shear_demand_pa=Q/glue_width,
                        nominal_peel_from_global_edge_moment_pa=6*moment/glue_width**2,
                        pressure_peak_pa=cfg['static_pressure_peak_pa'],force_balance_relative_error=float(balance),
                        scope='SREDNIA_REAKCJI_NA_ZADANEJ_DLUGOSCI_NIE_LOKALNY_PEAK_3D;ROZDZIAL_NAROZNIKA_PO_POLOWIE'))
    table('p19a_krawedzie_scinanie_odrywanie.csv',edges)
    result=dict(status='P19A_JOINT_DEMANDS_AND_IDEAL_ROD_LIMITS',edge_rows=len(edges),rod_reference_rows=len(buckling),
        fixture_rows_above_ideal_Euler_reference=sum(r['dynamic_fixture_force_to_Euler_reference']>1 for r in buckling),
        scope='Przekroczenie odniesieniaEulera sygnalizuje brak kwalifikacji liniowego modelu przy zadanej sztucznej sile,nie potwierdzoną awarię realnego subwoofera. Średnie krawędziowe nie są dowodem maksymalnych naprężeń naroża.')
    (OUT/'p19a_zlacza_i_prety_podsumowanie.json').write_text(json.dumps(result,indent=2,ensure_ascii=False));print(json.dumps(result,indent=2,ensure_ascii=False));return result


if __name__=='__main__':main()
