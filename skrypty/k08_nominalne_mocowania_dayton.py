#!/usr/bin/env python3
"""K08: manufacturer geometry + nominal standard fastener envelopes, NOT hardware qualification.

Inputs: Dayton RSS390HF-4 dimensional drawing (295-468), ISO 4762 screw
head nominal sizes, illustrative M6 washer 1.6mm and nut 5mm. The assembled
joint (threads, pad, glue, strength and tool swept envelope) is NOT verified.
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "wyniki" / "k08_nominalne_mocowania_dayton.json"
CUT_DIA = 355.8
PCD = 368.0
FLANGE_DIA = 388.4
BASKET_HOLE = 6.5
FLANGE_THICKNESS = 10.5
FRONT = 44.0
PAD_DEPTH = 20.0
WASHER_M6_THICKNESS = 1.6
NUT_M6_THICKNESS = 5.0

def r(v):
    return round(v, 3)

def compute():
    radial_inside = (PCD - CUT_DIA) / 2
    radial_outside = (FLANGE_DIA - PCD) / 2
    assert math.isclose(radial_inside, 6.1, abs_tol=1e-8)
    assert math.isclose(radial_outside, 10.2, abs_tol=1e-8)
    # ISO 4762 representative nominal heads; M6 washer thickness is a
    # separate ASSUMED example, not an assembly specification from Dayton.
    heads = {"M5": {"head_od_mm":8.5,"key_af_mm":4.0,"head_height_mm":5.0},
             "M6": {"head_od_mm":10.0,"key_af_mm":5.0,"head_height_mm":6.0}}
    radial = []
    for name,dia in (("head_M5_ISO4762",8.5),("head_M6_ISO4762",10.0),
                     ("nominal_M5_washer_OD10",10.0),("nominal_M6_washer_OD12",12.0),
                     ("hypothetical_washer_OD14",14.0)):
        radial.append({
            "item":name,"diameter_mm":dia,
            "radial_gap_to_cutout_mm":r(radial_inside-dia/2),
            "radial_gap_to_outer_flange_edge_mm":r(radial_outside-dia/2),
            "overlaps_nominal_cutout_radially":radial_inside-dia/2 < 0
        })
    assert [x["radial_gap_to_cutout_mm"] for x in radial]==[1.85,1.1,1.1,0.1,-0.9]
    wood = [{"mdf_hole_dia_mm":dia,
             "nominal_web_to_cutout_mm":r(radial_inside-dia/2)}
            for dia in (5.0,5.5,6.0,6.4,6.5,6.6)]
    assert wood[-2]["nominal_web_to_cutout_mm"]==2.85
    cases=[]
    for pad in (0.0,PAD_DEPTH):
        for shank in (38.1,60.,65.,75.,80.,85.,90.):
            # Shank lengths are specified BELOW the head. Head itself is NOT
            # part of the stack. Nut is assumed to START behind the MDF/pad.
            rear_face = FLANGE_THICKNESS + WASHER_M6_THICKNESS + FRONT + pad
            behind_front = shank - (FLANGE_THICKNESS + WASHER_M6_THICKNESS + FRONT)
            engagement = shank - rear_face
            cases.append({
                "rear_pad_thickness_mm":pad,
                "shank_under_head_mm":shank,
                "stack_to_rear_nut_face_mm":r(rear_face),
                "engagement_into_rear_nut_mm":r(max(0, engagement)),
                "reaches_rear_nut_face":engagement>=0,
                "illustrative_full_nut_5mm_engaged":engagement>=NUT_M6_THICKNESS,
                "shank_projection_beyond_MDF_front_back_mm":r(behind_front),
                "projection_beyond_nominal_nut_back_mm":r(max(0,engagement-NUT_M6_THICKNESS))
            })
    bypad={str(int(pad)):{"required_under_head_for_5mm_nut_engagement_mm":
        r(FLANGE_THICKNESS+WASHER_M6_THICKNESS+FRONT+pad+NUT_M6_THICKNESS)}
        for pad in (0.,PAD_DEPTH)}
    assert bypad["0"]["required_under_head_for_5mm_nut_engagement_mm"]==61.1
    assert bypad["20"]["required_under_head_for_5mm_nut_engagement_mm"]==81.1
    chosen=[x for x in cases if x["rear_pad_thickness_mm"]==20 and x["shank_under_head_mm"]==85.][0]
    assert chosen["engagement_into_rear_nut_mm"]==8.9
    assert chosen["shank_projection_beyond_MDF_front_back_mm"]==28.9
    assert chosen["projection_beyond_nominal_nut_back_mm"]==3.9
    return {
        "study":"K08",
        "design_status":"CONDITIONAL DIMENSIONAL SCREEN; NO PURCHASES; CNC HOLD",
        "sources":{
          "dayton_manufacturer":"https://www.daytonaudio.com/images/resources/295-468-dayton-audio-rss390hf-4-specifications-46176.pdf",
          "iso_4762_head_dimensions":"https://tengtoolsusa.com/blogs/news/socket-capscrews-dimensions-chart",
          "m6_nut_nominal":"https://hudsonfasteners.blob.core.windows.net/specs/MetDin934.pdf"
        },
        "manufacturer_data_mm":{
          "overall_flange_diameter":FLANGE_DIA,"cutout_diameter":CUT_DIA,
          "bolt_PCD":PCD,"basket_hole_diameter":BASKET_HOLE,
          "flange_thickness":FLANGE_THICKNESS,"overall_driver_depth":178.0,
          "number_of_basket_holes":8,
          "radial_inside_web_to_bolt_axis":r(radial_inside),
          "radial_outside_web_from_bolt_axis":r(radial_outside)
        },
        "hypotheses":{
          "front_MDF_mm":FRONT,
          "local_pad_mm":PAD_DEPTH,
          "illustrative_M6_washer_thickness_mm":WASHER_M6_THICKNESS,
          "illustrative_M6_rear_nut_thickness_mm":NUT_M6_THICKNESS,
          "note":"The nut starts BEHIND either the 44mm MDF or a 44+20mm front/pad stack. This assumes neither an embedded insert nor a thinner/hidden nut. Washer and nut sizes are not specified by Dayton."
        },
        "iso_4762_nominal_heads":heads,
        "head_and_washer_radial_margins":radial,
        "wood_web_examples":wood,
        "axial_M6_stacks":cases,
        "required_lengths_for_illustrative_full_nut_engagement":bypad,
        "illustrative_M6x85_rear_of_pad_projection":chosen,
        "not_verified":[
          "Face/head counterbore and overhanging washer tolerances",
          "Actual thread engagement requirements and bolt grip length",
          "Strength and creep of MDF, glue and retained T-nut",
          "Ability to place and capture the nut after 20 inserts",
          "Real basket ribs, terminals and tool envelope",
          "Real assembly depth or module-service outcome",
          "Any CNC or mounting torque signoff"
        ]
    }

def main():
    data=compute()
    OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("K08",json.dumps({
      "radial_web_to_axis_mm":data["manufacturer_data_mm"]["radial_inside_web_to_bolt_axis"],
      "M6_washer_OD12_gap_mm":0.1,
      "M6x85_at_rear_pad_projection_mm":data["illustrative_M6x85_rear_of_pad_projection"]["shank_projection_beyond_MDF_front_back_mm"],
      "no_pad_min_shank_mm":data["required_lengths_for_illustrative_full_nut_engagement"]["0"]["required_under_head_for_5mm_nut_engagement_mm"],
      "with_pad_min_shank_mm":data["required_lengths_for_illustrative_full_nut_engagement"]["20"]["required_under_head_for_5mm_nut_engagement_mm"],
      "cnc":"HOLD"
    },ensure_ascii=False))

if __name__=="__main__":
    main()
