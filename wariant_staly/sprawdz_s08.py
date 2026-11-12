"""S08 regression: numerical closure, worst-case fit veto and missing-data HOLD."""
import json
from pathlib import Path
from s08 import evaluate, net

HERE = Path(__file__).resolve().parent
example = json.loads((HERE/"s08_scenariusz.json").read_text(encoding="utf-8"))
blank = json.loads((HERE/"s08_karta.json").read_text(encoding="utf-8"))
reference = json.loads((HERE/"s06_wyniki.json").read_text(encoding="utf-8"))
r = evaluate(example)
assert r["CNC"] == "HOLD"
assert r["status"] == "HOLD_DO_POMIAROW_I_KWALIFIKACJI"
assert abs(r["netto_nominal_l"]-reference["net_L"]) < 0.0001
assert abs(net(example["wartosci"])-101.9860631553454) < 1e-9
assert abs(r["netto_najgorszy_przedzial_l"][0]-99.976089) < 1e-5
assert abs(r["netto_najgorszy_przedzial_l"][1]-103.998258) < 1e-5
assert r["czy_modelowy_litraz_w_zakresie"] is True
assert r["czy_wrega_pasuje_w_calej_obwiedni"] is False
assert r["wrega_luz_minimum_mm"] == [-0.8, -0.8]
assert evaluate(blank)["status"] == "HOLD_BRAK_DANYCH"
# Independent guard: too uncertain a displacement invalidates the volume envelope.
bad = json.loads(json.dumps(example))
bad["niepewnosci_pm"]["driver_L"] = 4.0
assert evaluate(bad)["czy_modelowy_litraz_w_zakresie"] is False
# Avoid treating 102L after nominal rounding as exact fabrication or a pass.
assert r["CNC"] == "HOLD"
print("S08 OK: 102 L nominal, robust interval and dimensional HOLD")
