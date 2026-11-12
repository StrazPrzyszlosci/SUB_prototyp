"""S16 - independent 2nd-order closed-box sanity check and hypothetical T/S screening.
No guessed T/S variation is claimed as manufacturer tolerance.
"""
import itertools
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def sealed_box(fs_hz, qts, vas_l, volume_l):
    if min(fs_hz, qts, vas_l, volume_l) <= 0:
        raise ValueError("All sealed-box inputs must be positive")
    ratio = math.sqrt(1.0 + vas_l / volume_l)
    fc = fs_hz * ratio
    qtc = qts * ratio
    a = 2.0 - 1.0/(qtc*qtc)
    # Analytic -3 dB frequency for the normalized second-order acoustic high pass.
    t = (-a + math.sqrt(a*a + 4.0))/2.0
    return {"Fc_Hz": fc, "Qtc": qtc, "F3_Hz": fc*math.sqrt(t)}


def calculate(driver, geom):
    nominal_v = 102.0
    if abs(geom["net_L"]-nominal_v)>0.1:
        raise ValueError("Not the nominal fixed-volume variant A")
    nominal = sealed_box(driver["fs_hz"],driver["qts"],driver["vas_l"],nominal_v)
    volume_only = [{"Vb_l": vb, **sealed_box(driver["fs_hz"],driver["qts"],driver["vas_l"],vb)}
                   for vb in (99.0,102.0,105.0)]
    # Fictitious bounding study, NOT factory spreads or confidence limits.
    scenarios = []
    for f_factor, v_factor, q_offset, vb in itertools.product(
        (.95,1.05),(.90,1.10),(-.05,.05),(99.0,105.0)
    ):
        r=sealed_box(driver["fs_hz"]*f_factor,driver["qts"]+q_offset,
                     driver["vas_l"]*v_factor,vb)
        scenarios.append(r)
    return {
        "status": "HOLD_MODEL_SENSITIVITY_ONLY",
        "model": "Ideal lumped second-order SEALED high pass WITHOUT Le, stuffing, DSP, "
                 "leakage, heating, nonlinear distortion or room response",
        "fixed_target_net_l": nominal_v,
        "nominal": {k:round(v,6) for k,v in nominal.items()},
        "volume_only": [{k:round(v,6) for k,v in row.items()} for row in volume_only],
        "hypothetical_not_factory_tolerances": {
            "Fs_factors":[.95,1.05],
            "Vas_factors":[.9,1.1],
            "Qts_absolute_offsets":[-.05,.05],
            "Vb_l":[99,105]
        },
        "sensitivity_box": {
            k:[round(min(r[k] for r in scenarios),6),
               round(max(r[k] for r in scenarios),6)] for k in ("Fc_Hz","Qtc","F3_Hz")
        },
        "why": "Sensitivity to unknown physical T/S can be more important than 3 L "
               "of volume, but this does not establish actual tolerances.",
        "CNC":"HOLD"
    }


if __name__ == "__main__":
    d = json.loads((ROOT/"s11_parametry_zrodel.json").read_text(encoding="utf-8"))
    g = json.loads((ROOT/"s06_wyniki.json").read_text(encoding="utf-8"))
    print(json.dumps(calculate(d["driver"], g), ensure_ascii=False, indent=2))
