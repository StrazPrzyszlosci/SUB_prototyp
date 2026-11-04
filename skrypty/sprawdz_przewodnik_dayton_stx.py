#!/usr/bin/env python3
"""Test current editorial handbook chronology without changing research data.

Always select an individual driver from the 40-model screen, then cover the
cabinet, material, joints and variable-volume design; consider competing
two-STX/isobaric/economic research only as a subsequent supplementary chapter.
"""
from pathlib import Path
import re

readme = (Path(__file__).resolve().parents[1] / "README.md").read_text(encoding="utf-8")

required = [
    "## Głośniki: porównanie w tych samych warunkach",
    "### Jak spośród 40 kandydatów wyłoniliśmy Dayton RSS390HF-4?",
    "### Który głośnik wybrać do pierwszego prototypu?",
    "## Praktyczny przewodnik",
    "### 1. Wybór przetwornika",
    "### 2. Badania akustyczne",
    "### 3. Badania materiałów",
    "### 4. Dopiero po projekcie",
    "## Konstrukcja w obrazach",
    "## Objętość i wypełnienie",
    "## Konstrukcja obudowy",
    "## Regulacja objętości",
    "## Powietrze w skrzyni",
    "## Badania uzupełniające — dwa STX kontra Dayton",
    "### P43 — czy dwa mniejsze",
    "### B12-01 — czy dopłata",
    "## Krótki słownik",
    "## Aneks techniczny",
    "### A22. K17",
]
loc = []
for marker in required:
    assert readme.count(marker) == 1, f"Marker missing or duplicated: {marker!r}"
    loc.append(readme.index(marker))
assert loc == sorted(loc), "New chapters must be in selection → cabinet → STX → reference appendix order"

supp_start = readme.index("## Badania uzupełniające — dwa STX kontra Dayton")
supp_end = readme.index("## Krótki słownik", supp_start)
supp = readme[supp_start:supp_end]
research = [
    "### P43 —", "### B12-01 —", "### B12-02 —", "### B12-03 —",
    "### B12-04 —", "### B12-05 —", "### B12-06 —", "### B12-07 —",
    "### B12-08 —", "### P45 —"
]
for heading in research:
    assert supp.count(heading) == 1, f"Missing comparison study {heading}"
assert len(re.findall(r"^### B12-0[1-8] ", supp, flags=re.M)) == 8
assert "Dayton Audio RSS390HF-4" in readme[:readme.index("## Praktyczny przewodnik")]
assert "40 modeli głośników" in readme[:readme.index("## Wybierz temat")]
assert '<a id="glosniki"></a>' in readme
assert '<a id="badania-alternatywne"></a>' in readme
assert "(#badania-alternatywne)" in readme
assert readme.count("CNC HOLD") > 5, "Ongoing model must not be represented as released-to-CNC"

print("README order PASS: 40 candidates -> Dayton -> practical/cabinet -> additional STX comparisons; all 10 secondary studies retained")
