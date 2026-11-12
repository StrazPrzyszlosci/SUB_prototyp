"""S15 - pressure loading of one FIXED, nominal 102 L sealed loudspeaker box.
Ideal-gas limiting cases only; not transient FEA, measured SPL or CNC release.
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
P0_PA = 101325.0  # SI standard atmosphere, NIST
GAMMAS = {"izotermiczny": 1.0, "adiabatyczny": 1.4}  # NASA, air at standard day


def pressure_pa(volume_l, swept_l, gamma):
    """Return (compression gauge Pa, expansion gauge Pa) for ±swept volume."""
    v = volume_l / 1000.0
    dv = swept_l / 1000.0
    if not (0 < dv < v) or not (gamma > 0):
        raise ValueError("Invalid sealed-box volume, sweep or polytropic exponent")
    return (P0_PA * ((v / (v - dv))**gamma - 1.0),
            P0_PA * ((v / (v + dv))**gamma - 1.0))


def calculate(d, v_geom):
    driver = d["driver"]
    sd_m2 = driver["sd_cm2"] * 1e-4
    xpeak_mm = driver["xmax_one_way_mm"]
    # cm² * mm / 10000 = litres, nominal PEAK volume sweep, NOT RMS.
    swept_l = driver["sd_cm2"] * xpeak_mm / 10000.0
    if abs(v_geom["net_L"] - 102.0) > 0.1:
        raise ValueError("S15 is restricted to S06 fixed nominal ~102 L")
    rear_area_m2 = (816.8-44.0)*(473.3-44.0)/1e6
    scenarios = []
    for v_l in (99.0, 102.0, 105.0):
        entry = {"volume_net_l": v_l}
        for state, gamma in GAMMAS.items():
            plus, minus = pressure_pa(v_l, swept_l, gamma)
            entry[state] = {
                "compression_peak_Pa": round(plus, 3),
                "expansion_peak_Pa": round(minus, 3),
                "absolute_expansion_peak_Pa": round(abs(minus), 3),
                "driver_pressure_force_N": round(plus*sd_m2, 3),
                "rear_uniform_pressure_force_N": round(plus*rear_area_m2, 3),
                # S03 separate PLATE models, linearly scaled:
                "rear_plate_clamped_static_deflection_mm": round(.043*plus/1000.0, 6),
                "rear_plate_pinned_static_deflection_mm": round(.162*plus/1000.0, 6),
            }
        scenarios.append(entry)
    partial = []
    for x_mm in (5.0, 10.0, xpeak_mm):
        sweep = driver["sd_cm2"]*x_mm/10000.0
        plus_iso, _ = pressure_pa(102.0, sweep, 1.0)
        plus_adi, _ = pressure_pa(102.0, sweep, 1.4)
        partial.append({"x_peak_mm": x_mm, "swept_l": round(sweep,6),
                        "compression_isothermal_Pa": round(plus_iso,3),
                        "compression_adiabatic_Pa": round(plus_adi,3)})
    # No measured physical MDF, leak rate, stuffing model, time dependence or exact basket.
    return {
        "status": "HOLD_MODEL_BEZ_POMIARU",
        "p_atm_Pa": P0_PA,
        "air_gamma_adiabatic": GAMMAS["adiabatyczny"],
        "net_nominal_S06_l": v_geom["net_L"],
        "source_driver_SD_cm2": driver["sd_cm2"],
        "source_driver_Xmax_one_way_mm": xpeak_mm,
        "catalog_swept_Vd_cm3": 1161.4,  # primary Dayton datasheet
        "swept_from_Sd_times_Xpeak_cm3": round(swept_l*1000, 3),
        "volume_fraction_at_102_l": round(swept_l/102.0, 8),
        "rear_inside_face_m2": round(rear_area_m2, 8),
        "pressure_scenarios": scenarios,
        "partial_excursions": partial,
        "meaning": "Two ideal heat-transfer limits at fixed air volume, no leakage, "
                   "perfectly rigid wall. Pressure-force and plate deflection are "
                   "quasi-static loads, NOT measured peak SPL, resonance or material "
                   "strength acceptance.",
        "CNC": "HOLD"
    }


if __name__ == "__main__":
    d = json.loads((ROOT/"s11_parametry_zrodel.json").read_text(encoding="utf-8"))
    v = json.loads((ROOT/"s06_wyniki.json").read_text(encoding="utf-8"))
    print(json.dumps(calculate(d,v), ensure_ascii=False, indent=2))
