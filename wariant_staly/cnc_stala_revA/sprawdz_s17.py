"""S17: digital geometry release gates, independent of physical measurements."""
import json
import math
import tempfile
from pathlib import Path
from generator import build,generate,driver_bolts

assert len(driver_bolts())==8
for t in (21.7,22.0,22.3):
    parts,meta=build(t)
    assert meta["part_types"]==15,meta["part_types"]
    assert 99<=meta["net_estimated_L"]<=105
    assert sum(parts[k]["qty_for_two"] for k in
               ("FR1","FR2","TYL","BOK_L","BOK_R","DNO_GORA","WREGA"))==16
    assert meta["inner_mm"][2] == 394-3*t
    assert math.isclose(meta["inner_mm"][0]-meta["brace_mm"][0],.4,abs_tol=1e-7)
    assert math.isclose(meta["inner_mm"][1]-meta["brace_mm"][1],.4,abs_tol=1e-7)
    assert "THRU_D5_6_FRONT" in parts["FR1"]["dxf"].layers
    assert "BLIND_D10_DEPTH18_FRONT" in parts["FR1"]["dxf"].layers
    assert "RELIEF_D6_5_AFTER_POCKET4" in parts["FR2"]["dxf"].layers
    assert "THRU_D30_CABLE_TO_BRACKET" in parts["BOK_R"]["dxf"].layers
    assert "BLIND_D10_DEPTH18_OUTSIDE" in parts["BOK_R"]["dxf"].layers
    assert "GLAND_M16_D16_5_THRU" in parts["OBUDOWA_BAZA_AL3"]["dxf"].layers
    assert "FACE_M3_SERVICE_D3_4" in parts["GNIAZDO_PANEL_AL3"]["dxf"].layers
    assert "DRILL_D4_2_TAP_M5x0_8" in parts["PIERSCIEN_STAL"]["dxf"].layers
    # Gland body no longer passes through 22mm stock: mounted in AL3 base.
    assert parts["OBUDOWA_BAZA_AL3"]["stock_mm"]==3
    assert parts["BOK_R"]["size_mm"][0]==round(394-3*t,4)
    assert meta["not_for_machine_release"] is True
    for key,p in parts.items():
        data=p["dxf"].serialise()
        assert data.startswith("0\nSECTION")
        assert data.endswith("EOF\n")
        if key == "DYSTANS_METAL_L24":
            assert "LATHE_OUTER_D16" in data
        else:
            assert "OUTER_CUT_THRU" in data
        assert not any(v in data for v in ("nan","inf"))
with tempfile.TemporaryDirectory() as temp:
    p=Path(temp)
    result=generate(p,22.0)
    assert len(list(p.glob("*.dxf")))==result["part_types"]
    assert len((p/"cutlist.csv").read_text().splitlines())==result["part_types"]+1
    saved=json.loads((p/"manifest.json").read_text())
    assert "dxf" not in saved["parts"]["FR1"]
    assert sum(v["qty_for_two"] for v in saved["parts"].values())==40
    for f in p.glob("*.dxf"):
        assert f.stat().st_size>130
print("S17/S18 OK: 15 DXF drawings, 16 MDF22 cuts for pair + six AL3 box panels per module")
