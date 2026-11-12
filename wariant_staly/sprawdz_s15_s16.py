"""S15-S16 regression with independent numerical checks and safety holds."""
import json
import math
from pathlib import Path
from s15_cisnienie import pressure_pa, calculate as pressure
from s16_odpowiedz import sealed_box, calculate as response

HERE = Path(__file__).resolve().parent
d=json.loads((HERE/"s11_parametry_zrodel.json").read_text(encoding="utf-8"))
g=json.loads((HERE/"s06_wyniki.json").read_text(encoding="utf-8"))
p=pressure(d,g)
a=response(d["driver"],g)
assert p["CNC"]=="HOLD" and a["CNC"]=="HOLD"
assert abs(p["catalog_swept_Vd_cm3"]-p["swept_from_Sd_times_Xpeak_cm3"]) < .1
assert abs(p["volume_fraction_at_102_l"] - 1.16144/102.0) < 1e-7
nom=p["pressure_scenarios"][1]
iso=nom["izotermiczny"];adi=nom["adiabatyczny"]
assert 1160 < iso["compression_peak_Pa"] < 1180
assert 1630 < adi["compression_peak_Pa"] < 1650
assert 134 < adi["driver_pressure_force_N"] < 138
assert 542 < adi["rear_uniform_pressure_force_N"] < 545
assert .069 < adi["rear_plate_clamped_static_deflection_mm"] < .072
assert .263 < adi["rear_plate_pinned_static_deflection_mm"] < .268
for case in p["pressure_scenarios"]:
    assert case["adiabatyczny"]["compression_peak_Pa"] > case["izotermiczny"]["compression_peak_Pa"]
    assert case["izotermiczny"]["expansion_peak_Pa"] < 0
assert pressure_pa(102,1.16144,1.4)[0] > abs(pressure_pa(102,1.16144,1.4)[1])
try:
    pressure_pa(1,1.1,1.4)
except ValueError:
    pass
else:
    raise AssertionError("Invalid gas volume accepted")
assert 34.20 < a["nominal"]["Fc_Hz"] < 34.23
assert 0.75 < a["nominal"]["Qtc"] < 0.76
assert 32.18 < a["nominal"]["F3_Hz"] < 32.23
assert a["volume_only"][0]["Fc_Hz"] > a["volume_only"][-1]["Fc_Hz"]
assert a["volume_only"][0]["Qtc"] > a["volume_only"][-1]["Qtc"]
assert a["sensitivity_box"]["F3_Hz"][0] < a["nominal"]["F3_Hz"] < a["sensitivity_box"]["F3_Hz"][1]
assert sealed_box(19.5,.43,212,102)["Fc_Hz"] == a["nominal"]["Fc_Hz"] or math.isclose(
    sealed_box(19.5,.43,212,102)["Fc_Hz"],a["nominal"]["Fc_Hz"],rel_tol=1e-6
)
print("S15-S16 OK: pressure envelopes, force, independent closed-box HP and HOLD")
