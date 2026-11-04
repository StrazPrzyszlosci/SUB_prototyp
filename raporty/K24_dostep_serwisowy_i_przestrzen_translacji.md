# K24 — mechanical service accessibility and exhaustive fixed-orientation exit-space test

Date: 4 November 2026. **CNC HOLD**. Source-derived, reproducible numerical assessment. No manufacture-ready fitting has been designed.

## 1. Tool access beneath the reference lower supports

K15's complete 100 L nominal module arrangement gives 12 large modules with just 10 mm vertical clearance below their bottoms and four lowest large modules with 12 mm. A K17 original 4 mm supporting tongue leaves only 6 or 8 mm directly below it. A **hypothetical** straight tool 12 mm wide, with 1 mm clearance on each side, needs 14 mm. Therefore **16/16 large modules fail that particular underside approach**, not necessarily every alternative angular or remote drive.

K17 rear strips are 12 mm deep in Y and front strips only 8 mm. A trial 4.5 mm diameter hole through the 16 mm X-laminated width leaves nominal Y-edge ligaments of 3.75 and 1.75 mm. An intentionally conservative, **assumed** 1.5×diameter center-to-edge screen needs 6.75 mm; zero existing rails pass. This is not a certified MDF standard or evidence of actual joint failure: fasteners, effective substrate, allowable stresses, preload, adhesives and pull-out testing are absent.

Model-only load sensitivity assumes shell panel volume times a 730 kg/m³ density, +0.2 kg per box for unmeasured attachment, 5 g inertial demand and one surviving supporting contact. Reference single-contact demands are about 32.83 N (small rear), 39.36 N (large rear) and 44.41 N (large front). Ideal nominal original 16×4 mm cantilever root bending stress indicators are about 17.70, 17.53 and 12.49 MPa. No allowable or safety factor can be assigned from these numbers.

## 2. Configuration-space search for small rear boxes

The K24 program partitions 3D rigid translational centre-position space along every relevant expanded axis-aligned obstacle face, then traverses all open free cells using six-neighbour connectivity. It keeps K15 nominal wall/bracing solids, 11 K17 vertical rails, rear mat, and scenario-dependent retained module boxes. The K22 rail G17_COLUMN_10 is absent, and all lower and upper support tabs are removed from the obstacles to **favour** removal. The boundary at the front opening is also checked against the nominal Ø355.8 reference circular cutout.

| Other boxes retained | Number of small rear boxes 0–3 able to reach the front exit, at 1 mm reference clearance |
|---|---:|
| Full 100 L state (all other 19) | **0 / 4** |
| Twelve large modules making the original 120 L configuration | **0 / 4** |
| Only the other small rear modules | **4 / 4** |
| Twelve original 120 L modules except temporarily removed modules 12 and 14 | **4 / 4** |

The negative results hold at diagnostic zero and at 1 and 3 mm reference margins. This tests the **entire connected open free space for translations without changing box orientation**, not one suggested route. It is not a universal impossibility claim for arbitrary 6DOF rotations or deformable objects. The last row requires extra disassembly of modules that the target 120 L state is intended to keep, and their real extraction and remounting have not been proven.

## 3. Exact nominal volume combination arithmetic

Current reference box outer displacement volumes are small rear 1.80 L, rear large 2.52 L, and front large 3.15 L. The original 100→120 volume difference is precisely 19.80 L. Exhaustive integer enumeration (0–4 small, 0–8 rear large and 0–8 front large) yields only two exact removal count solutions:

- Four small rear + four front large = 19.80 L.
- Four small rear + five rear large = 19.80 L.

Both require removal of **all four geometrically trapped small rear modules**. The nearest candidate requiring no small modules is four rear large + three front large = 19.53 L, a −0.27 L step deviation before mounting-hardware displacement. No feasibility of removing these alternative modules is claimed.

## 4. Engineering decision

The immediate K24 recommendation is to stop treating K17/K18 tongues as a just-a-bolt retrofit. The combination of narrow 8/12 mm rails, 6/8 mm underside access under large modules, and topologically inaccessible small-rear displacement requires architectural redesign: physically accessible displacement cassettes, repositioned/resized modules or a structurally reinforced and gasketed service hatch. The next study must quantify actual reversible 100↔120↔150 movement, attachment strength, real driver/basket/tool envelopes, chamber leakage and acoustic response. Preserve historical DXF but forbid CNC cutting.

[Reproducible script](../skrypty/k24_serwis_CSPACE.js) · [K24 machine-readable results](../wyniki/k24_serwis_CSPACE_wyniki.json) · [CI](../.github/workflows/k24-service-access.yml).
