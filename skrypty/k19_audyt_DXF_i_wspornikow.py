#!/usr/bin/env python3
"""K19 independent K15/K17/K18 research-only DXF inspection; never an approval for CNC."""
import csv,json,math
from pathlib import Path
from collections import Counter
root=Path(__file__).resolve().parents[1]
def read(p):return json.loads((root/p).read_text(encoding="utf8"))
def close(x,y,eps=1.1e-5):assert math.isclose(x,y,rel_tol=0,abs_tol=eps),(x,y)
def parse(path):
    ls=(root/path).read_text(encoding="utf8").splitlines()
    assert len(ls)%2==0 and ls[-2:]==["0","EOF"]
    pairs=list(zip(ls[::2],ls[1::2]));count=Counter();i=0
    while i<len(pairs):
        key,val=pairs[i]
        if key=="0" and val in ("LWPOLYLINE","CIRCLE","TEXT"):
            i+=1; fields=[]
            while i<len(pairs) and pairs[i][0]!="0":fields.append(pairs[i]);i+=1
            layer=next((v for k,v in fields if k=="8"),"")
            count[(val,layer)]+=1
            if val=="LWPOLYLINE":
                n=int(next(v for k,v in fields if k=="90"))
                assert int(next(v for k,v in fields if k=="70"))&1
                x=[float(v) for k,v in fields if k=="10"]
                y=[float(v) for k,v in fields if k=="20"]
                assert len(x)==len(y)==n and n>=4
                points=list(zip(x,y))
                assert all(math.dist(points[j],points[(j+1)%n])>1e-7 for j in range(n))
                signed=sum(x[j]*y[(j+1)%n]-x[(j+1)%n]*y[j] for j in range(n))/2
                assert abs(signed)>0
        else:i+=1
    return count
def main():
    A=read("wyniki/k15_p30e_przed_CNC_zestawienie.json")
    B=read("wyniki/k17_prowadnice_boczne_wkladow.json")
    C=read("wyniki/k18_mocowania_i_CNC_podsumowanie.json")
    R=read("wyniki/k19_audyt_CNC_wysieg_rygora.json")
    assert len(A["parts"])==138 and len(A["module_positions"])==20
    assert len(B["spines"])==12 and len(B["contact_lips"])==80
    assert C["release"]=="CNC_HOLD_RESEARCH_CONTOURS_ONLY"
    parts=["dokumentacja/cnc/K18_korpus_i_wregi_MDF22_NIE_CNC.dxf","dokumentacja/cnc/K18_skrzynki_regulacji_MDF8_NIE_CNC.dxf","dokumentacja/cnc/K18_prowadnice_laminat_MDF8_NIE_CNC.dxf"]
    for p,n in zip(parts,[18,120,24]):
        c=parse(p)
        assert c[("LWPOLYLINE","REFERENCE_PROFILE_HOLD")]==n,(p,c)
        if n==18:
            assert c[("LWPOLYLINE","POCKET_3MM_CONCEPT_HOLD")]==24
            assert c[("CIRCLE","FACTORY_CUTOUT_REFERENCE_NO_CAM")]==2
    with (root/"wyniki/k18_lista_162_konturow_CNC_HOLD.csv").open(newline="",encoding="utf8") as f:
        bom=list(csv.DictReader(f))
    assert len(bom)==162 and len({b["id"] for b in bom})==162
    assert all(b["release"]=="CNC_HOLD" for b in bom)
    assert Counter(int(b["thickness_mm"]) for b in bom)=={22:18,8:144}
    assert Counter(p["module_index"] for p in A["parts"] if p["module_index"]>=0)=={i:6 for i in range(20)}
    count=Counter()
    for m in A["module_positions"]:
        tabs=[t for t in B["contact_lips"] if t["module_index"]==m["i"]]
        assert Counter(t["position"] for t in tabs)=={"shelf":2,"retainer":2}
        near=[];far=[]
        for t in tabs:
            s=next(r for r in B["spines"] if r["group"]==t["group"] and abs(r["o"][0]-t["o"][0])<1e-8)
            stop=s["o"][1]+s["s"][1]
            near.append(m["global_origin_xyz_mm"][1]-stop)
            far.append(t["o"][1]+t["s"][1]-stop)
            if t["position"]=="shelf":close(t["o"][2]+t["s"][2],m["global_origin_xyz_mm"][2])
            else:close(t["o"][2],m["global_origin_xyz_mm"][2]+m["dims_xyz_mm"][2])
        assert len(set(near))==len(set(far))==1
        family="small_rear" if m["dims_xyz_mm"][0]==180 else ("large_rear" if m["dims_xyz_mm"][1]==120 else "large_front")
        g=next(v for v in R["groups"] if v["family"]==family)
        count[family]+=1
        close(g["near_mm"],near[0]);close(g["far_tip_mm"],far[0])
        panel=[p for p in A["parts"] if p["module_index"]==m["i"]]
        mass=sum(math.prod(p["box_size_xyz_mm"]) for p in panel)*730/1e9
        F=mass*5*9.81/2;L=far[0]
        checks={"mass_kg":mass,"force_per_lip_N":F,
                "stress_nominal_4mm_MPa":6*F*L/(16*4**2),
                "deflection_nominal_4mm_mm":4*F*L**3/(2700*16*4**3),
                "stress_if_lip_3_5mm_MPa":6*F*L/(16*3.5**2),
                "deflection_if_lip_3_5mm_mm":4*F*L**3/(2700*16*3.5**3),
                "stress_multiplier_vs_K18_L12":L/12,
                "deflection_multiplier_vs_K18_L12":(L/12)**3}
        for key,value in checks.items():close(g[key],value)
    assert count=={"small_rear":4,"large_rear":8,"large_front":8}
    assert R["critical_fit_assumption"]["possible_clearance_mm"]==[-0.3,1.3]
    assert C["nominal_module_clearance_with_rigid_top_bottom_lips_mm"]==0
    print("PASS K19: 162 closed research DXF contours, 24 sockets, 20 modules, corrected 12/19/23mm levers, CNC HOLD")
if __name__=="__main__":main()
