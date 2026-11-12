"""S10: compare CAD parametric constants with the independent S06 panel passport."""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
scad = (HERE/"S10_korpus_A_102L_NIE_CNC.scad").read_text(encoding="utf-8")
s06 = json.loads((HERE/"s06_wyniki.json").read_text(encoding="utf-8"))
def k(name):
    m = re.search(r"^"+re.escape(name)+r"\s*=\s*([0-9.]+)\s*;", scad, flags=re.M)
    assert m, "No numeric OpenSCAD constant: "+name
    return float(m.group(1))
assert [k("W"), k("H"), k("D")] == s06["outer_mm"]
assert k("T") == s06["nominal_t_mm"]
assert k("inner_depth") == s06["layout"]["clear_mm"][2]
assert abs(k("brace_w") - s06["layout"]["panels"][-1]["length_mm"]) < 1e-6
assert abs(k("brace_h") - s06["layout"]["panels"][-1]["width_mm"]) < 1e-6
assert all(abs(a-b) < 1e-6 for a,b in zip([k("brace_open_w"),k("brace_open_h")], s06["layout"]["opening_mm"]))
assert k("brace_y") == s06["layout"]["brace_start_y_mm"]
assert abs(k("brace_y")-178-19) < 1e-9
assert (k("D")-k("T"))-(k("T")*2)-k("inner_depth") == 0
assert "NOT A CNC DRAWING" in scad
assert "show_pair" in scad
print("S10 OK - OpenSCAD geometry consistent with S06/S07")
