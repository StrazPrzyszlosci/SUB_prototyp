#!/usr/bin/env python3
"""S17: CNC 2D source of one FIXED ~102 L cabinet, rev A0 digital engineering.
Manufacturer geometry and explicitly labeled design assumptions.
No G-code; no tool radius compensation; geometry is part-centred, not nested.
"""
import argparse
import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
W, H, D = 816.8, 473.3, 394.0
DRIVER_BORE = 355.8
PCD = 368.0
FRONT_CX, FRONT_CY = W/2, H/2

class DXF:
    def __init__(self):
        self.e=[]
        self.layers=set()
    def entity(self, kind, layer, pairs):
        self.layers.add(layer)
        self.e.extend(("0", kind, "8", layer))
        for code, value in pairs:
            self.e.extend((str(code), f"{value:.5f}" if isinstance(value, float) else str(value)))
    def line(self, x1,y1,x2,y2,layer):
        self.entity("LINE",layer,((10,x1),(20,y1),(11,x2),(21,y2)))
    def circle(self,x,y,r,layer):
        self.entity("CIRCLE",layer,((10,x),(20,y),(40,r)))
    def arc(self,x,y,r,start,end,layer):
        self.entity("ARC",layer,((10,x),(20,y),(40,r),(50,start),(51,end)))
    def rect(self,w,h,layer,x=0.0,y=0.0):
        assert w>0 and h>0
        x2=x+w; y2=y+h
        for xa,ya,xb,yb in ((x,y,x2,y),(x2,y,x2,y2),(x2,y2,x,y2),(x,y2,x,y)):
            self.line(xa,ya,xb,yb,layer)
    def round_rect(self,x,y,w,h,r,layer):
        assert 0 < 2*r < min(w,h)
        x2=x+w;y2=y+h
        self.line(x+r,y,x2-r,y,layer)
        self.arc(x2-r,y+r,r,270,360,layer)
        self.line(x2,y+r,x2,y2-r,layer)
        self.arc(x2-r,y2-r,r,0,90,layer)
        self.line(x2-r,y2,x+r,y2,layer)
        self.arc(x+r,y2-r,r,90,180,layer)
        self.line(x,y2-r,x,y+r,layer)
        self.arc(x+r,y+r,r,180,270,layer)
    def serialise(self):
        header=["0","SECTION","2","HEADER",
                "9","$ACADVER","1","AC1009",
                "0","ENDSEC","0","SECTION","2","ENTITIES"]
        return "\n".join(header + self.e + ["0","ENDSEC","0","EOF",""])


def driver_bolts(cx=FRONT_CX,cy=FRONT_CY):
    return [(cx+PCD/2*math.cos(math.radians(k*45)),
             cy+PCD/2*math.sin(math.radians(k*45))) for k in range(8)]


def build(t):
    if not (21.7 <= t <= 22.3) or not math.isfinite(t):
        raise ValueError("This revision is parameterised only for 21.7..22.3 mm MDF")
    side_depth=D-3*t
    clear_w=W-2*t;clear_h=H-2*t
    brace_clearance=.4  # total nominal oversize room; CNC-to-supplier thickness reparametrisation
    brace_w=clear_w-brace_clearance;brace_h=clear_h-brace_clearance
    opening_w=brace_w-60;opening_h=brace_h-60
    brace_y=2*t+(side_depth-t)/2
    driver_displacement=5.000 # DESIGN ASSUMPTION, not a producer quote
    terminal_displacement=.175
    wiring_glue=.150
    brace_vol=(brace_w*brace_h-(opening_w*opening_h-(4-math.pi)*3**2))*t/1e6
    gross=clear_w*clear_h*side_depth/1e6
    net=gross-brace_vol-driver_displacement-terminal_displacement-wiring_glue

    parts={}
    def add(name, material, thk, qty, size, operations, drawing):
        if name in parts: raise RuntimeError(name)
        parts[name]=dict(name=name,material=material,stock_mm=thk,qty_for_two=qty,
                         size_mm=[round(float(x),4) for x in size],operations=operations,
                         dxf=drawing)
    def panel(name,width,height,n,ops,details):
        d=DXF()
        d.rect(width,height,"OUTER_CUT_THRU")
        for action in ops: action(d)
        add(name,"EGGER_REFERENCE_MDF",t,n,(width,height),details,d)
    def full_bore(d):
        d.circle(FRONT_CX,FRONT_CY,DRIVER_BORE/2,"INNER_CUT_THRU")
    def fr1_add(d):
        full_bore(d)
        for x,y in driver_bolts(): d.circle(x,y,5.6/2,"THRU_D5_6_FRONT")
        for x in (26.4,W-26.4):
            for y in (28.65,H-28.65):
                d.circle(x,y,10/2,"BLIND_D10_DEPTH18_FRONT")
    panel("FR1",W,H,2,[fr1_add],
          ["Ø355.8 full cut", "8x Ø5.6 through on PCD368",
           "4x Ø10 blind depth18 from FRONT for RAMPA M6x18",
           "only one FINISHED face with depths from front"])
    def fr2_add(d):
        full_bore(d)
        d.circle(FRONT_CX,FRONT_CY,400.4/2,"POCKET_D400_4_DEPTH6_2")
        for x,y in driver_bolts(): d.circle(x,y,6.5/2,"RELIEF_D6_5_AFTER_POCKET4")
        for y in (FRONT_CY-194,FRONT_CY+194):
            d.circle(FRONT_CX,y,4.2/2,"PIN_D4_2_AFTER_POCKET5")
    panel("FR2",W,H,2,[fr2_add],
          ["Ø355.8 through","Ø400.4 pocket 6.2 from face contacting FR1",
           "8x Ø6.5 relief additional depth 4 from pocket floor",
           "2x Ø4.2 blind additional depth 5 from pocket floor (K42 pins)",
           "MACHINE FROM FR1 CONTACT FACE, do not mirror 8-axis system"])
    panel("TYL",W,H,2,[],["fully sealed back, no amplifier cutout"])
    panel("BOK_L",side_depth,H,2,[],["local X = depth Y, local Y = assembly Z"])
    def side_r_add(d):
        # Local x is Y_global - front stack 2*t; local y is Z_global.
        x=330.0-2*t;y=FRONT_CY
        d.circle(x,y,16.5/2,"THRU_D16_5_GLAND_M16")
        d.circle(x,y,36/2,"POCKET_INNER_D36_DEPTH17")
    panel("BOK_R",side_depth,H,2,[side_r_add],
          ["right-side gland LAPP ST-M16 on side (manufacturer thread length 8mm)",
           "Ø16.5 through; from inside Ø36 recess depth17 leaving ~5mm outer skin",
           "source coordinate Y_global330, Z_global236.65",
           "external NL4 bracket is separate mechanical subassembly"])
    panel("DNO_GORA",clear_w,side_depth,4,[],["fits between sides"])
    def brace_add(d):
        d.round_rect(30,30,opening_w,opening_h,3,"INNER_WINDOW_THRU_R3")
    panel("WREGA",brace_w,brace_h,2,[brace_add],
          ["window border 30mm each side", "centred in chamber along Y",
           "brace Y from %.3f to %.3f"%(brace_y,brace_y+t),
           "profile recomputed from chosen MDF t; no adjustable chamber"])
    # Steel ring, exact K42 geometry, CNC/laser blanks followed by threading.
    ring=DXF()
    ring.circle(200,200,200,"OUTER_CUT_THRU")
    ring.circle(200,200,179,"INNER_CUT_THRU")
    for x,y in driver_bolts(200,200):
        ring.circle(x,y,2.1,"DRILL_D4_2_TAP_M5x0_8")
    for y in (200-194,200+194):
        ring.circle(200,y,2.0,"PIN_LOC_D4_FINISH_SPEC")
    add("PIERSCIEN_STAL", "S235JR_DESIGN_SPEC", 6,2,(400,400),
        ["Ø400/Ø358 x6", "8x drill Ø4.2 then tap M5x0.8",
         "2x locating holes Ø4; actual pin fit and metal finish specified by supplier",
         "deburr, corrosion protection, protect threads during FR1/FR2 lamination"],ring)
    # Fabric OR protective grille: shared 12mm perimeter frame. Attachment via 4 screws.
    grille=DXF()
    grille.rect(784,436,"OUTER_CUT_THRU")
    grille.rect(744,396,"INNER_CUT_THRU",20,20)
    for x in (10,774):
        for y in (10,426):
            grille.circle(x,y,6.6/2,"THRU_D6_6_M6")
    add("RAMKA_KASETY_MDF12","MDF12_DESIGN_CHOICE",12,2,(784,436),
        ["one of two finishing options, cloth or separate metal grille",
         "no crossbars across driver", "4x Ø6.6 for M6 screw/standoff",
         "24mm stand-offs + 12mm frame + finish ≤2mm = total ≤38mm"],grille)
    # Neutrik faceplate, SIDE terminal. Other protective pieces remain unfinished.
    term=DXF()
    term.rect(70,72,"OUTER_CUT_THRU")
    term.circle(35,36,12,"NEUTRIK_REAR_CUT_D24")
    for x in (35-14.6,35+14.6):
        for y in (36-14.6,36+14.6):
            term.circle(x,y,3.4/2,"NEUTRIK_4x_D3_4")
    add("GNIAZDO_PANEL_AL3","ALUMINIUM_3_DESIGN_CHOICE",3,2,(70,72),
        ["Neutrik NL4MPRXX 4x Ø3.4 on 29.2 square",
         "centre through Ø24: manufacturer minimum cutout; may require more after CAD STEP",
         "need external housing and insulated strain relief"],term)
    # Four cylindrical spacers per enclosure, from metal stock 24mm, lathe processing.
    spacer=DXF()
    spacer.circle(10,10,8,"LATHE_OUTER_D16")
    spacer.circle(10,10,3.3,"LATHE_INNER_D6_6")
    add("DYSTANS_METAL_L24","ALUMINIUM_DESIGN_CHOICE",24,8,(16,16),
        ["round standoff Ø16/Ø6.6 x24 axial, M6x50 bolt passes through"],spacer)
    return parts,{
        "version":"S17 A0 CNC DIGITAL STUDY", "units":"mm",
        "repo_branch":"badania/stala-obudowa-2-2",
        "not_for_machine_release":True,
        "no_gcode":True,
        "material_thickness_mdf_mm":t,
        "outer_mm":[W,H,D],
        "inner_mm":[clear_w,clear_h,side_depth],
        "brace_mm":[brace_w,brace_h],
        "brace_start_Y_global":round(brace_y,4),
        "volume_geometry_L":round(gross,6),
        "brace_solid_L":round(brace_vol,6),
        "assumed_other_displacements_L":[driver_displacement,terminal_displacement,wiring_glue],
        "net_estimated_L":round(net,6),
        "part_types":len(parts),
        "quantities_for_pair":{k:v["qty_for_two"] for k,v in parts.items()},
        "drawing_basis":"CAD part contours; no kerf, tool compensation, nesting, CAM feeds",
        "unresolved_digital_design":[
          "Bracket housing/walls, protective contacts and attachment to cabinet",
          "Final driver gasket cross-section and front relief/terminal harness routing",
          "Face finish grille-perforated insert and fabric fixture detail",
          "Material supplier confirmation, e.g. 22mm MDF EGGER batch grade and actual t",
          "Equipment-specific CAM: cutter diameters/dogbones, tabs, feeds and fixtures",
          "M5 ring dowel pin fit, bolt countersinks, screw engagement and backing support",
          "Foot orientation and attachment, anti-tilt fixation in final furniture",
          "Full 3D interference inspection against Dayton STEP, Neutrik STEP, LAPP gland CAD"
        ]
    }


def generate(outdir,t=22.0):
    outdir=Path(outdir);outdir.mkdir(parents=True,exist_ok=True)
    parts,manifest=build(t)
    for key,part in parts.items():
        (outdir/(key+".dxf")).write_text(part["dxf"].serialise(),encoding="ascii")
        del part["dxf"]
    manifest["parts"]=parts
    (outdir/"manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    with (outdir/"cutlist.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.writer(f,delimiter=";")
        w.writerow(["part","material","thickness_mm","length_mm","width_mm","qty_for_pair","file"])
        for key,p in parts.items():
            w.writerow([key,p["material"],p["stock_mm"],*p["size_mm"],p["qty_for_two"],key+".dxf"])
    return manifest


if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--t",type=float,default=22.0,help="Nominal MDF thickness by selected supplier, 21.7-22.3mm")
    a.add_argument("--out",type=Path,default=ROOT/"generated")
    x=a.parse_args()
    print(json.dumps({k:v for k,v in generate(x.out,x.t).items() if k!="parts"},indent=2,ensure_ascii=False))
