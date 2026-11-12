"""S08 - conservative volume and brace-fit screening for one FIXED 102 L enclosure.
Pure standard library, no CNC export or fabrication approval.
"""
import argparse
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
DIM = ("W", "H", "D", "t_left", "t_right", "t_top", "t_bottom",
       "t_fr1", "t_fr2", "t_back", "brace_w", "brace_h",
       "brace_open_w", "brace_open_h", "brace_t", "brace_r")
VOLS = ("driver_L", "terminal_L", "wire_glue_L")
FIELDS = DIM + VOLS


def gross(v):
    """Physical internal volume excluding reinforcement and displaced equipment, L."""
    a = v["W"] - v["t_left"] - v["t_right"]
    b = v["H"] - v["t_top"] - v["t_bottom"]
    c = v["D"] - v["t_fr1"] - v["t_fr2"] - v["t_back"]
    if min(a, b, c) <= 0:
        raise ValueError("Non-positive internal dimension")
    return a * b * c / 1e6


def brace(v):
    """Solid volume of one window brace, including rounded INTERNAL corners, L."""
    if min(v[k] for k in ("brace_w", "brace_h", "brace_open_w",
                         "brace_open_h", "brace_t")) <= 0:
        raise ValueError("Invalid brace geometry")
    if v["brace_open_w"] >= v["brace_w"] or v["brace_open_h"] >= v["brace_h"]:
        raise ValueError("Opening must be smaller than brace")
    if 2*v["brace_r"] > min(v["brace_open_w"], v["brace_open_h"]):
        raise ValueError("Corner radius exceeds the opening")
    opening = v["brace_open_w"]*v["brace_open_h"] - (4-math.pi)*v["brace_r"]**2
    return (v["brace_w"]*v["brace_h"]-opening)*v["brace_t"]/1e6


def net(v):
    return gross(v) - brace(v) - sum(v[k] for k in VOLS)


def evaluate(card):
    v = card.get("wartosci", {})
    u = card.get("niepewnosci_pm", {})
    missing = [k for k in FIELDS if v.get(k) is None or u.get(k) is None]
    if missing:
        return {"status": "HOLD_BRAK_DANYCH", "brak": missing, "CNC": "HOLD"}
    for k in FIELDS:
        if type(v[k]) not in (float, int) or type(u[k]) not in (float, int):
            raise ValueError("Numeric values required: " + k)
        if not math.isfinite(v[k]) or not math.isfinite(u[k]):
            raise ValueError("Non-finite number: " + k)
        if v[k] < 0 or u[k] < 0 or v[k]-u[k] < 0:
            raise ValueError("Negative physical bound: " + k)
    lower = {k: v[k]-u[k] for k in FIELDS}
    upper = {k: v[k]+u[k] for k in FIELDS}
    # Conservative independent worst-case interval, not a statistical confidence interval.
    min_shell = dict(v)
    max_shell = dict(v)
    for k in ("W", "H", "D"):
        min_shell[k], max_shell[k] = lower[k], upper[k]
    for k in ("t_left", "t_right", "t_top", "t_bottom", "t_fr1", "t_fr2", "t_back"):
        min_shell[k], max_shell[k] = upper[k], lower[k]
    max_brace = dict(v)
    min_brace = dict(v)
    for k in ("brace_w", "brace_h", "brace_t", "brace_r"):
        max_brace[k], min_brace[k] = upper[k], lower[k]
    for k in ("brace_open_w", "brace_open_h"):
        max_brace[k], min_brace[k] = lower[k], upper[k]

    nominal = net(v)
    net_min = gross(min_shell) - brace(max_brace) - sum(upper[k] for k in VOLS)
    net_max = gross(max_shell) - brace(min_brace) - sum(lower[k] for k in VOLS)
    gap_w = v["W"]-v["t_left"]-v["t_right"]-v["brace_w"]
    gap_h = v["H"]-v["t_top"]-v["t_bottom"]-v["brace_h"]
    gap_w_min = lower["W"]-upper["t_left"]-upper["t_right"]-upper["brace_w"]
    gap_h_min = lower["H"]-upper["t_top"]-upper["t_bottom"]-upper["brace_h"]
    target = 102.0
    allowed_min, allowed_max = target-3, target+3
    volume_ok = net_min >= allowed_min and net_max <= allowed_max
    fit_ok = min(gap_w_min, gap_h_min) >= 0
    return {
        "status": "HOLD_DO_POMIAROW_I_KWALIFIKACJI",
        "pochodzenie": card.get("pochodzenie", "nieokreslone"),
        "CNC": "HOLD",
        "netto_nominal_l": round(nominal, 6),
        "netto_najgorszy_przedzial_l": [round(net_min, 6), round(net_max, 6)],
        "zakres_kryterium_modelowego_l": [allowed_min, allowed_max],
        "czy_modelowy_litraz_w_zakresie": volume_ok,
        "wrega_luz_nominalny_mm": [round(gap_w, 4), round(gap_h, 4)],
        "wrega_luz_minimum_mm": [round(gap_w_min, 4), round(gap_h_min, 4)],
        "czy_wrega_pasuje_w_calej_obwiedni": fit_ok,
        "warunek_cnc": "Dodatkowe pomiary, proby kleju i polaczen, kosza, "
                       "terminala, szczelnosci, maskownicy, MES i CAM"
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--karta", type=Path, default=HERE/"s08_karta.json")
    args = p.parse_args()
    result = evaluate(json.loads(args.karta.read_text(encoding="utf-8")))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
