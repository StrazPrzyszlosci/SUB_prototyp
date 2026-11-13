"""S19: static SCAD dimension/reference consistency with S17/S18 CNC generator."""
import math
import re
from pathlib import Path
from generator import build
P=Path(__file__).resolve().parent
txt=(P/"S19_zlozenie_revA0.scad").read_text(encoding="utf-8")
p,m=build(22.0)
def get(n):
    hit=re.search("^"+re.escape(n)+r"\s*=\s*([0-9.]+)\s*;",txt,re.M)
    assert hit,n
    return float(hit.group(1))
assert [get(v) for v in ("W","H","D")]==m["outer_mm"]
assert get("T")==22.0
assert math.isclose(get("ring_outer_d"),400)
assert math.isclose(get("ring_inner_d"),358)
assert math.isclose(get("ring_pocket_d"),400.4)
assert math.isclose(get("driver_d"),355.8)
assert math.isclose(get("driver_flange_d"),388.4)
assert get("pcd")==368
for pattern in ("cube([3,80,72])","cube([64,3,66])","cube([784,12,436])","cylinder_x(W-T-eps,330,Cz,30"):
    assert pattern in txt,pattern
assert m["term_hardware_position"].startswith("EXTERNAL")
assert m["side_port_void_L"]>0.01
assert 102.16<m["net_estimated_L"]<102.19,m["net_estimated_L"]
assert m["not_for_machine_release"] is True
print("S19 OK: 3D assembly nominally consistent with S17/S18 and corrected external-terminal volume")
