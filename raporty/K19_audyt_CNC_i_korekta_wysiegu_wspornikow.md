# K19 — independent geometrical and mechanical audit before real CNC

**4 November 2026. CNC HOLD.** This is a new independent computational check of existing [K15](K15_parametryczne_zlozenie_i_zestawienie_przed_CNC.md), [K17](K17_prowadnice_nośne_bez_kolizji_z_mata.md) and [K18](K18_projekt_CNC_mocowania_wkladow.md); no manufacturing or physically measured cabinet has been approved.

## Critical correction: K18 omitted the unsupported gap

K18 computed all hypothetical 4-mm-thick MDF tabs with the same ideal 12-mm cantilever length, which is **the overlap under each insert**, not necessarily the distance from the rail's outer face to the tab's far tip. The real nominal K17 coordinates give:

| Insert family | Installed boxes | Rail-to-box gap [mm] | Rail-to-far-tip cantilever [mm] |
|---|---:|---:|---:|
| small_rear | 4 | 11 | **23** |
| large_rear | 8 | 7 | **19** |
| large_front | 8 | 0 | **12** |

**A critical qualification:** the force resultant could act anywhere across the 12mm contact patch; far-tip loading is intentionally conservative, not a known real load point. The short unsupported span is between rail and near edge of box; full far-tip span is an upper-bound lever arm. The real bearing pressure and local deformations are unknown.

## Corrected idealized cantilever demand

Box shell mass comes from summing its six actual K15 MDF8 panels. The explicitly hypothetical 5g inertial force is shared by two lips; b=16mm, t=4mm, E=2700MPa, density=730kg/m³. For a point load at far tip L: `sigma=6 F L/(b t²)`, `delta=4 F L³/(E b t³)`. NO MDF strength, joint strength, fatigue or real stress concentration has been calibrated.

| Type | Shell mass kg | Load per lip N | Far-tip stress MPa | Far-tip deflection mm | Stress at hypothetical 3.5mm lip height MPa |
|---|---:|---:|---:|---:|---:|
| small_rear | 0.469 | 11.51 | **6.20** | **0.2026** | 8.10 |
| large_rear | 0.602 | 14.77 | **6.58** | **0.1466** | 8.59 |
| large_front | 0.705 | 17.30 | **4.87** | **0.0433** | 6.36 |

Relative to K18's assumed 12mm, the small-rear far-tip screen increases stress **1.92×** and deflection **7.04×**; large-rear becomes **1.58×** and **3.97×** respectively. These are *ratios within one ideal beam model*, not measurements.

## CNC quality audit

The independent [Python QA program](../skrypty/k19_audyt_DXF_i_wspornikow.py) checks the number of closed DXF reference profiles (18 MDF22 + 120 MDF8 box panels + 24 rail laminates = **162**), the 24 hypothetical 3mm pockets, the two factory-reference speaker bores, BOM uniqueness and CNC HOLD labels. It reconstructs all 20 box masses from six MDF8 shell panels each and verifies all 80 K17 upper/lower support contacts and the corrected 12/19/23mm reach groupings. [Data JSON](../wyniki/k19_audyt_CNC_wysieg_rygora.json). [Regression CI](../.github/workflows/k19-cnc-hold-geometry-audit.yml).

**Tolerance sensitivity, not a supplied tolerance:** nominally two MDF8 laminates (2×8mm) enter a 16.5mm pocket. If each stock ply were 7.7–8.3mm and the pocket were 16.3–16.7mm, simple signed clearance would vary from **−0.3mm interference** to **+1.3mm play**. These ranges are arbitrary stress tests; actual stock, glue line, end-mill geometry and clamping are NOT known.

The K17 fixed lower and upper lips touch insert surfaces with **zero nominal vertical insertion clearance**. A physical installation route with cutter radii, an accessible positive removable retainer and anti-rattle seal does not exist. Even the 3mm rail pockets are only a geometry concept, not a certified attachment or proof of pull-out load path. No strength or adhesive coupon tests were performed.

## Next actual engineering tasks, in order

1. **Mechanically design and dimension a removable upper positive keeper**, with real bolt/anchor, compliant anti-rattle preload, insertion clearance, orientation, tool access, captive parts and service release. Recompute stress at the roots with a true contact force model, not tip assumptions alone.
2. **Verify swept 3D assembly and disassembly paths for all 20 boxes** through the nominal Ø355.8 opening with all 12 rails, 11 braces, actual Dayton basket, mounting hardware and wiring; check 100→120→150→100 states without violating the permanent mat.
3. **Qualify MDF stock and joints physically**: sample thickness, two-ply bond, bending and peel, pocket and rail pull-out, 4mm root/fillet fracture, vibrations, impact, humidity, creep and cycling. Compute strength with measured properties and appropriate safety factors.
4. **Finalize machining specification:** tool diameter, internal fillets/dog-bones, blind pocket machining face, zero reference, glue thickness and fit, 10mm brace webs, tolerances per operation, kerf, tabs and nesting, terminal, grille, device max depth 500mm.
5. **Recalculate measured air volumes** including all permanent rails, seals, real basket, fasteners, adhesive, selected box geometry, mat properties and tolerances; then redo electroacoustic verification at all three states.

**Decision: no K18 DXF is released for milling.** Avoid handing raw preview contours to a shop without explicit CNC engineering release.
