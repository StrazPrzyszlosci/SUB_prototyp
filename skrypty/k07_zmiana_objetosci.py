"""K07: jedna zagnieżdżona sekwencja regulacji 150 → 120 → 100 l."""
import json

import k02_dostep_modulow_i_klocki as planner


def run():
    order = list(range(4, 16)) + list(range(4)) + list(range(16, 20))
    stages = [(150, 1), (120, 12), (100, 20)]
    rows = []
    for depth, inner in [(20.0, 178.9), (28.8, 178.0)]:
        pads = [[(x - 22, z - 22) for x, z in
                 planner.k.polygon(231, angle, inner, 205, 36)]
                for angle in range(0, 360, 45)]
        for clearance in (3.0, 6.0):
            trial = planner.check_state("K07", order, clearance, pads, depth)
            completed = trial["completed_modules"]
            failure = trial["failures"]
            rows.append({
                "glebokosc_mm": depth, "luz_mm": clearance,
                "wlozone_kolejno": completed,
                "osiagniete_stany_l": [litres for litres, count in stages if count <= completed],
                "pierwszy_problem": failure[0] if failure else None,
            })
    return {"kolejnosc_id_od_zera": order, "proby": rows, "proba_fizyczna": False}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))
