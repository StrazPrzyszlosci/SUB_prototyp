"""S17: digital geometry release gates, independent of physical measurements."""
import json
import math
import tempfile
from pathlib import Path
from generator import build,generate,driver_bolts

assert len(driver_bolts())==8
for t in (21.7,22.0,22.3):
    parts,meta=build(t)
    assert meta["part_types"]==11,meta["part_types"]
    assert 99<=meta["net_estimated_L"]<=105
    assert sum(parts[k]["qty_for_two"] for k in
               ("FR1","FR2","TYL","BOK_L","BOK_R","DNO_GORA","WREGA"))==16
    assert meta["inner_mm"][2] == 394-3*t
    assert math.isclose(meta["inner_mm"][0]-meta["brace_mm"][0],.4,abs_tol=1e-7)
    assert math.isclose(meta["inner_mm"][1]-meta["brace_mm"][1],.4,abs_tol=1e-7)
    assert "THRU_D5_6_FRONT" in parts["FR1"]["dxf"].layers
    assert "BLIND_D10_DEPTH18_FRONT" in parts["FR1"]["dxf"].layers
    assert "RELIEF_D6_5_AFTER_POCKET4" in parts["FR2"]["dxf"].layers
    assert "POCKET_INNER_D36_DEPTH17" in parts["BOK_R"]["dxf"].layers
    assert "DRILL_D4_2_TAP_M5x0_8" in parts["PIERSCIEN_STAL"]["dxf"].layers
    # Gland recess 17 deep in minimum 21.7mm stock leaves 4.7mm.
    assert t-17 >= 4.7-1e-8
    assert meta["not_for_machine_release"] is True
    for key,p in parts.items():
        data=p["dxf"].serialise()
        assert data.startswith("0\nSECTION")
        assert data.endswith("EOF\n")
        assert "OUTER_CUT_THRU" in data
        assert not any(v in data for v in ("nan","inf"))
with tempfile.TemporaryDirectory() as temp:
    p=Path(temp)
    result=generate(p,22.0)
    assert len(list(p.glob("*.dxf")))==result["part_types"]
    assert len((p/"cutlist.csv").read_text().splitlines())==result["part_types"]+1
    saved=json.loads((p/"manifest.json").read_text())
    assert "dxf" not in saved["parts"]["FR1"]
    assert sum(v["qty_for_two"] for v in saved["parts"].values())==30
    for f in p.glob("*.dxf"):
        assert f.stat().st_size>130
print("S17 OK: 11 separate DXF contours, 16 MDF22 parts for pair, t-sensitive brace, BOM, no G-code")
