#!/usr/bin/env python3
"""K10: component-level material register and comparative, NOMINAL geometry screens.

No unmeasured modulus, MDF bond strength, glue allowable, acoustic absorption,
thermal/fire rating, or catalogue bolt strength is assumed as *validated*.
The 22-mm plate proxy is isotropic; the WISA plywood values are two separate
directional 1D bending properties, NOT a calibrated orthotropic 2D plate.
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT/"dane"/"k10_rejestr_materialow_czesci_obudowy.json"
OUTPUT = ROOT/"wyniki"/"k10_wyniki_przesiewu_materialow.json"
W, DEPTH, H = 1020., 425., 500.
FRONT, WALL, T, R_CUT = 44., 22., 22., 355.8/2
BRACE_ORIGIN_X = (426.,701.)
BASE_RHO = 730.
MODEL_PAD_RHO = 700.  # deliberately unsourced wood scenario ONLY
PAD_RI,PAD_RO,PAD_W,PAD_D=178.9,205.,36.,20.

def liters(mm3):
    return mm3/1e6

def bending_D(E_gpa, h_mm, nu):
    h=h_mm/1000.
    return E_gpa*1e9*h**3/(12*(1-nu**2))

def areal_mass(rho, h_mm):
    return rho*(h_mm/1000)

def hollow_module_l(dims, wall):
    external = math.prod(dims)
    inner_dims=[v-2*wall for v in dims]
    assert min(inner_dims)>0
    return liters(external-math.prod(inner_dims))

def main():
    inp=json.loads(INPUT.read_text(encoding="utf-8"))
    parts=inp["parts"]
    ids=[p["id"] for p in parts]
    assert len(parts)==35 and len(set(ids))==35
    assert ids == [f"E{i:02d}" for i in range(1,36)]
    for part in parts:
        assert part["provisional_material"] and part["material_status"]=="CANDIDATE_NOT_QUALIFIED",part
        assert part["qualification_gate"] and part["quantitative_evidence"]
        assert part["evidence_paths"] and part["controlling_requirements"]
    mats=inp["raw_material_library"]
    p0=mats["MDF22_reference"]
    D0=bending_D(p0["E_bending_GPa"],p0["thickness_mm"],p0["nu_assumed"])
    areal0=areal_mass(p0["rho_kg_m3"],p0["thickness_mm"])
    comparison=[]
    for key,m in mats.items():
        D=bending_D(m["E_bending_GPa"],m["thickness_mm"],m["nu_assumed"])
        mu=areal_mass(m["rho_kg_m3"],m["thickness_mm"])
        ratio=D/D0
        comparison.append({
            "scenario":key,"E_bending_GPa":m["E_bending_GPa"],
            "thickness_mm":m["thickness_mm"],
            "rho_assumed_or_derived_kg_m3":round(m["rho_kg_m3"],3),
            "areal_mass_kg_m2":round(mu,4),
            "isotropic_D_for_screen_Nm":round(D,3),
            "relative_isotropic_D_to_MDF22":round(ratio,4),
            "same_geometry_static_deflection_proxy_um_at_1000Pa":round(45.0/ratio,3),
            "same_geometry_f11_proxy_Hz":round(235.4*math.sqrt(D/mu/(D0/areal0)),3),
            "limitation":"Plywood direction is NOT a plate solution; E and nu scenario, different thickness changes box geometry; SSSS unperforated bay ONLY"
        })
    assert comparison[0]["relative_isotropic_D_to_MDF22"] == 1
    assert comparison[1]["relative_isotropic_D_to_MDF22"]>1.4
    assert comparison[2]["relative_isotropic_D_to_MDF22"]>3
    # Reproduce ONLY P30E volumetric decomposition; panels not a full joinery CAD.
    inner = (W-2*WALL)*(DEPTH-FRONT-WALL)*(H-2*WALL)
    shell_l=liters(W*DEPTH*H-inner-math.pi*R_CUT**2*FRONT)
    # P30A/P30E uses 11 non-overlapping simplified brace AABBs.
    inside_depth=DEPTH-FRONT-WALL
    inside_height=H-2*WALL
    brace_boxes=[]
    for _ in BRACE_ORIGIN_X:
        brace_boxes.extend([
          T*inside_depth*T, T*inside_depth*T,
          T*10*(inside_height-2*T),
          T*T*(inside_height-2*T)
        ])
    brace_boxes.extend([
       T*(inside_depth-220)*T, T*(inside_depth-220)*T,
       T*T*(inside_height-2*T)
    ])
    brace_l=liters(sum(brace_boxes))
    assert abs(shell_l-52.6001338564)<1e-8 and abs(brace_l-1.60908)<1e-8
    pad_l=liters(8*(PAD_RO-PAD_RI)*PAD_W*PAD_D)
    assert abs(pad_l-0.150336)<1e-10
    dims={"rear_large":[210,120,100],"front_large":[210,150,100],"small":[180,100,100]}
    volumes={str(t):{k:hollow_module_l(v,t) for k,v in dims.items()} for t in (8,9)}
    states={"150":{"rear_large":1,"front_large":0,"small":0},
            "120":{"rear_large":8,"front_large":4,"small":0},
            "100":{"rear_large":8,"front_large":8,"small":4}}
    masses=[]
    for label,counts in states.items():
        mods_mdf = sum(volumes["8"][k]*counts[k] for k in dims)*BASE_RHO/1000
        mods_ply = sum(volumes["9"][k]*counts[k] for k in dims)*mats["WISA_birch21_weak_proxy"]["rho_kg_m3"]/1000
        const_mass=(shell_l+brace_l)*BASE_RHO/1000
        masses.append({
            "nominal_litre_state":int(label),"counts":counts,
            "insert_shell_MDF8_kg":round(mods_mdf,4),
            "insert_shell_birch9_kg_same_outer_dimensions":round(mods_ply,4),
            "insert_mass_delta_if_birch9_kg":round(mods_ply-mods_mdf,4),
            "P30E_shell_plus_braces_MDF22_kg":round(const_mass,4),
            "P30E_original_MDF_shell_braces_inserts_kg":round(const_mass+mods_mdf,4),
            "plus_hypothetical_8_glued_wood_pads_at_700kg_m3_kg":round(const_mass+mods_mdf+pad_l*MODEL_PAD_RHO/1000,4)
        })
    assert abs(masses[2]["insert_shell_MDF8_kg"]-12.34)<.05
    assert 51.8 < masses[2]["P30E_original_MDF_shell_braces_inserts_kg"]<52.
    assert 47.1 < masses[1]["P30E_original_MDF_shell_braces_inserts_kg"]<47.3
    assert 40.1 < masses[0]["P30E_original_MDF_shell_braces_inserts_kg"]<40.3
    # Equal baseline 22mm layers vs full-composite 44mm front, no hole.
    D_unbonded=2*D0
    D_bonded=bending_D(2.1,44,.3)
    assert abs(D_bonded/D_unbonded-4.)<1e-9
    outputs={
      "study":"K10",
      "status":"HYPOTHESES AND ANALYTICAL SCREENS ONLY — NO MATERIAL OR CNC QUALIFICATION",
      "register":"dane/k10_rejestr_materialow_czesci_obudowy.json",
      "part_count":len(parts),
      "parts_with_provisional_material":len(parts),
      "parts_physically_qualified":0,
      "P30E_reference_outer_mm":[1020,425,500],
      "selected_materials":"Not selected for fabrication; baseline E01–E09 MDF as P30E, other parts have provisional candidates",
      "plate_proxy":{"definition":"D=Eh^3/[12(1-nu^2)], mu=rho*h, deflection ratio D0/D, f ratio sqrt((D/mu)/(D0/mu0)). P30E SSSS unperforated 426x359mm 1000Pa reference w45um/f235.4Hz; plywood ONE-DIRECTION numbers NOT actual two-dimensional plate response.",
         "reference_E_GPa":2.1,"reference_nu_assumed":.3,
         "reference_rho_assumed_kg_m3":730,
         "reference_D_Nm":round(D0,3),
         "comparison":comparison},
      "front_2x22_hypothetical":{"two_separate_22mm_layers_D_Nm":round(D_unbonded,3),
           "perfectly_bonded_44mm_isotropic_D_Nm":round(D_bonded,3),
           "perfect_to_unbonded_D_ratio":4,
           "caveat":"Neither bound is perforated front 3D response; real adhesive rotational/composite action, cutout and 8 clamps need independent testing."},
      "geometry_p30e_decomposition":{"front_cutout_cylindrical_simplification_mm":355.8,
         "shell_wood_nominal_L":round(shell_l,6),"braces_nominal_L":round(brace_l,6),
         "8_pad_envelope_nominal_L_excluded_from_P30E_baseline":round(pad_l,6),
         "base_MDF_rho_kg_m3":730,"pad_rho_scenario_kg_m3_not_datasheet":MODEL_PAD_RHO,
         "note":"Shell & braces from P30A/P30E idealized 11-box geometry, not manufacturing CAD; previous P30E mass excludes pads, gasket, finish, grille, cables, hardware and driver."},
      "module_shell_volumes_L_by_wall_mm":{
         k:{id:round(v,6) for id,v in val.items()} for k,val in volumes.items()},
      "state_masses":masses,
      "unqualified_material_gates":[
          "MDF board source and actual properties for 8/22/44mm with thickness and density tolerances",
          "Plywood orthotropic EL/ET/GLT and actual manufactured thickness instead of scalar screen",
          "Panel/brace/insert geometry rerun whenever thickness, joint shape or material changes",
          "Glue creep/peel and delamination measurements, no generic bond allowable",
          "Klocki 20mm wood species and 8 real insert anchor pullout measurements",
          "Seals: compression curve and compression set, air leakage after repeated cycles",
          "Acoustic mat airflow resistivity/absorption and retention; 50mm thickness alone inadequate",
          "Feet: mass and tipping in both orientations; grille: strength and total depth <=500mm",
          "Full modal, pressure and contact FEM with P33C safeguards and prototype measurement"
      ]
    }
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(outputs,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("K10: %s candidate materials, 0 physically qualified; 5 plate scenarios, 3 volumes" %len(parts))
    print("shell %.6f l, braces %.6f l, 8 pads %.6f l"%(shell_l,brace_l,pad_l))
    print("mass 100l %.4f kg baseline + inserts"%(masses[2]["P30E_original_MDF_shell_braces_inserts_kg"]))

if __name__ == "__main__":
    main()
