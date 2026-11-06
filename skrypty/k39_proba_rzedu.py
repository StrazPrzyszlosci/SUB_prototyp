"""Ocena jednego dystansu i jednej konfiguracji na podstawie próby warsztatowej."""
import json
import math
import sys
from pathlib import Path


def number(value):
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise ValueError("Wymagany pomiar lub parametr liczbowy >= 0")
    return value


def evaluate(card):
    for field in ("rzad_i_konfiguracja", "partia_i_wymiary_podkladek", "protokol", "podstawa_limitow_sily"):
        if not isinstance(card[field], str) or not card[field].strip():
            raise ValueError("Uzupełnij pole " + field)
    gmin, gmax, shim, es, eh, ef, fmin, fmax = [
        number(card[k]) for k in ("luz_min_mm", "luz_max_mm", "dystans_mm",
                                  "blad_dystansu_mm", "blad_wysokosci_mm", "blad_sily_N",
                                  "min_docisk_N", "max_docisk_N")]
    hmin, hmax = gmin - shim - es, gmax - shim + es
    if gmin > gmax or shim < es or hmin <= eh or not 0 < fmin < fmax:
        raise ValueError("Sprawdź granice luzu, dystansu i docisku")
    details = []
    for trial in card["proby"]:
        small, large, peak, end, hours_small, hours_large = [number(trial[k]) for k in
            ("wysokosc_mala_mm", "wysokosc_duza_mm", "maks_sila_mala_N",
             "min_sila_duza_N", "czas_mala_h", "czas_duza_h")]
        if small <= eh or small + eh > hmin + 1e-9 or large - eh < hmax - 1e-9 or min(hours_small, hours_large) < 24:
            raise ValueError("Próba musi objąć zakres wysokości z błędem i co najmniej 24 h")
        checks = [end - ef >= fmin, peak + ef <= fmax, end <= peak]
        for key in ("monotoniczna_charakterystyka", "pelne_podparcie", "blokada_doszla_do_oporu", "wyjeto_i_zalozono", "brak_uszkodzen"):
            if type(trial[key]) is not bool:
                raise ValueError("Wpisz wynik oględzin: " + key)
            checks.append(trial[key])
        details.append(all(checks))
    if not details:
        raise ValueError("Brak prób")
    return {"zakres_wysokosci_mm": [round(hmin, 5), round(hmax, 5)],
            "wyniki_prob": details, "wynik_rzedu": "SPEŁNIA KRYTERIA PRÓBY" if all(details) else "ODRZUĆ",
            "wydanie_cnc": "HOLD"}


if __name__ == "__main__":
    try:
        print(json.dumps(evaluate(json.loads(Path(sys.argv[1]).read_text())), ensure_ascii=False, indent=2))
    except (KeyError, ValueError, TypeError, IndexError, OSError) as exc:
        sys.exit("Brak oceny: " + str(exc))
