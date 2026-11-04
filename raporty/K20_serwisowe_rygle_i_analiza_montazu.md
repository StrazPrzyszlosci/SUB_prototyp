# K20 — removable upper keepers, mechanical interface blockers and revised nominal air-volume states

**4 November 2026 · Computational research, not manufacturing authorization. Status: CNC HOLD.** Inputs: K15, K17 and K19. This report supersedes the integrated-top-tongue *assembly concept* of K18, but preserves its historical drawings for comparison.

## Design decision and what is actually modelled

The 12 K17 spines and 40 integral **bottom supports** remain fixed inside the cabinet. The 40 permanently integrated **top** tongues are replaced by 40 hypothetical **removable upper keeper envelopes**, two per removable volume box. Each keeper is moved 2 mm above the module top and begins at the spine's outward face, eliminating K17's 1 mm intentional solid root overlap. It is shown only if the associated box is present. **It is not anchored to the spine**: the 16×4 = 64 mm² nominal butt-contact face has no screw, retainer, positive lock or verified glue. Therefore the new upper parts are placement proposals only; the box is not secured against inversion or transport. The 2 mm nominal gap is not a working preload or anti-rattle seal.

[Parametric OpenSCAD K20 assembly](../dokumentacja/K20_p30e_rozbieralne_zabezpieczenia_NIE_CNC.scad) · [Generator](../skrypty/k20_rozbieralne_rygle_i_bilans.js) · [Result JSON](../wyniki/k20_rozbieralne_rygle_audyt.json).

## Static geometry (not full assembly route)

A strict-positive intersection-of-axis-aligned-boxes (AABB) audit against all 138 K15 solids, fixed K17 rails, 40 lower ledges, all other removable keepers and the rear 50 mm mat envelope found **0** modelled solid-volume clashes at the final positions. It does not check the actual keeper fastening hardware, hands, insertion sequence, installed loudspeaker basket or the 3D swept path of a rotated box. For isolated boxes centered in the nominal Ø355.8 aperture, a projected rectangle plus a **hypothetical** 6 mm clearance in X and Z fits (width 180 mm: radial margin 66.760448 mm; 210 mm: 53.573816 mm). That **does not** mean the module can reach its mounting location.

## Air-volume change when upper keepers are removed

K17's reference 1.020928 L of permanently present rails and lips divides into **0.977408 L** permanently retained spines/lower shelves and **0.043520 L** of old upper lips, now replaced by removable solids (without new real hardware).

| Nominal state | Boxes installed | Upper keepers installed | Reference fixture volume [L] | Nominal air volume [L] |
|---|---:|---:|---:|---:|
| 100 | 20 | 40 | 1.020928 | 99.098366 |
| 120 | 12 | 24 | 1.003008 | 118.916286 |
| 150 | 1 | 2 | 0.979840 | 149.179454 |

These are **derived** numbers for idealized non-intersecting solids with K15's assumed basket and hardware displacement. No real mounting screws, lock, glue, gaskets or measured volume are counted. The 100/120/150 L target is not yet certified.

## Critical correction of eight K18 top/bottom pockets

The four front-group spines start at the cabinet's inside front face Y=44 mm. K18's proposed nominal 3 mm pockets in the top and bottom panels start at the **front edge**, not inside a closed internal border. This gives **4 open-edge slots per panel, 8 in total**; they must not be labelled enclosed blind pockets. An edge-breaking 3 mm recess affects joint design, machining order, router breakout and the front-panel glue interface; it is **not** an approved attachment. The K18 DXF has permanently **integral upper lips**, so it does not represent the K20 detachable keeper solution. The old DXFs remain **DO NOT MACHINE**.

## Next discriminating engineering test

Before attempting a new fabrication DXF, a separate captive, positively locking keeper with adjustable compliant preload must be fully dimensioned: fastener diameter, bearing, pull-out, tool access, keeper height, tolerances and anti-inversion retention for all 20 boxes. Check the root under K19's corrected 12/19/23 mm cantilever lever arms. Then perform true sequential swept-volume routes with all permanent obstacles (including spines, rims, braces and cable). Prove changes 150↔120↔100 and upside-down operation. Dimension/qualify actual rail joints before releasing pocket profiles. A mechanical test coupon for the real selected material and connection is needed. **No CNC release.**
