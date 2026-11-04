# K25 — dimensioned splice keep-out analysis, access geometry and one-sided support loads

**4 November 2026 | CNC HOLD.** Based on the actual K15 and K17 coordinates and the independently checked two-stage K24 service graph. This analysis establishes **necessary design constraints**; it does not produce a working rail latch or authorize any CNC machining. [Machine-readable audit](../wyniki/k25_zlacza_prowadnic_i_dostep.json) · [reproducible script](../skrypty/k25_zlacza_prowadnic_dostep.js).

## Two different rail problems; identical threaded joint is not supported

K24 finds zero-clearance, purely translational candidate volume-state changes using **rail02 temporarily removed for 100→120 L** and **rail10 temporarily removed for 120→150 L**. Neither model includes attached keeper/shelf joints. A mechanically sensible concept must restore support after each change and retain every installed box in any orientation, including transport. To avoid concealing the difference between the two rail environments, K25 checks candidate split planes and access *separately*.

## Explicit parameters (not selected production hardware)

For numerical comparison only: each candidate rail has 16mm X width, 456mm overall height; test a 50mm-high face-mounted joint **keep-out region**, 2mm nominal steel-plate thickness on either Y face, at least 8mm Z clearance to existing lip geometry, and 6mm extra projected aperture clearance for presenting each half. The trial tool cylinder has an assumed 12mm diameter plus 1mm radial clearance = **14mm overall**. These are *hypothetical screening envelopes* and **do not define actual plates, holes or screws**. No supplier data or material strength is applied.

The split-position scan checks each integer global Z from inside [22,478], accepts only if the larger of the two straight portions fits the nominal Ø355.8 factory baffle hole as a centered **upright XZ rectangle**, and if the entire 50mm splice keep-out clears every original K17 upper/lower lip by at least 8mm.

| Subject | G17_COLUMN_02 (small-rear) | G17_COLUMN_10 (large-rear) |
|---|---|---|
| Reference split height Z, mm | **250** | **194** |
| Resulting segment heights, mm | 228 + 228 | 172 + 284 |
| Computed permissible integer Z split windows, mm | 199–301 | 177–211; 287–321 |
| 50mm plate keep-out Z interval, mm | 225–275 | 169–219 |
| Upright segment far-corner reference projected radius, mm | 120.813906 | 148.660687 |
| Nominal driver cutout radius, mm | 177.9 | 177.9 |
| Original K17 lip intersects selected plate zone | No | No |

**Guide10 split at Z250 is incorrect:** it coincides with an original load-bearing lip at Z250–254. Z194 is an alternative geometry screening value, **not** an approved splice or guaranteed assemblable location. The chosen Z194 plate zone lies inside the heights of large boxes and therefore has a very different service-access problem.

## Solid intersection and straight tool access tests

For each split, the K25 code constructs two independent 2mm-thick rectangular *keep-out* surfaces on the front and rear Y faces of the rail, with X16mm × Z50mm. Each candidate has zero positive-volume collisions with all reference K15 cabinet/box solids and other K17 rails/lips at its nominal final position (intentional face contact with its own rail is permitted). **No static intersection is not proof of clearance to a service tool.**

**Guide02, Z250**: the splice is in the substantial Z gap between its small box heights, so a hypothetical Ø14mm straight Y-axis tool cylinder centred at X183, Z250 can reach its *front* face without intersecting the K15/K17 fixed solids or any installed K15 box. The cutter/basket-opening reference Ø355.8 also fully contains this tool-cylinder projection. This is a *limited nominal tool approach* only; it does not prove M4 screw performance, actual fasteners, insertion of the rail halves or installer hand reach.

**Guide10, Z194**: the same plate on the *front Y face* leaves only **4mm** to nearby front-large boxes; the back-face plate leaves only **5mm** to the rear-large box. The chosen 14mm straight tool envelope cannot fit either local gap. Moreover its front-normal tool centre is at X669.5, whereas the loudspeaker reference centre is X231: its cylinder projects to **449.061365mm** from the cutout centre, substantially beyond the **177.9mm** radius. A straight longitudinal approach from the driver opening is therefore **impossible under this geometry**. Other angled/remote tools or a radically different access mechanism are untested.

The 2mm plate cuboids are **not load bearing** in this model. No bolt holes, welds, screw edge distances, threaded inserts, locking pins, keeper preload, bracket plasticity, MDF glue or safe rail anchoring exist.

## Consequence of temporarily removing one support

The original K17 nominal 4mm-thick tongue on the other side would have to carry the entire insert load while its companion rail is absent, *unless a real independently secured temporary support is installed*. A hypothetical worst-case sensitivity using K15 six-panel box shell mass, MDF density 730 kg/m³, +0.2kg assumed ancillary hardware, and 5g inertial loading gives the single remaining support:

| Case | Assumed total load at one contact N | Original lever mm | Ideal 16×4mm root stress MPa | Hypothetical weakened 16×3.5mm root stress MPa |
|---|---:|---:|---:|---:|
| G17_COLUMN_02, module 0 | 32.826991 | 23 | 17.6958 | 23.112881 |
| G17_COLUMN_10, module 12 | 39.358097 | 19 | 17.526652 | 22.891954 |

These bending estimates are **NOT allowable load ratings**. They omit thread strip-out, shear, creep, dynamic torsion, joint flexibility and the material batch's real tested properties. In a real service procedure no installed module may be left supported by an unqualified 4mm protrusion.

## Recommendation and hard gate for K26

**Keep the rail02 concept provisionally** for a dimensioned, coupon-tested connector because there is at least a nominal front-normal service approach at Z250. **Do NOT simply clone the same screw-and-plate connector on rail10.** There, a different remotely released keeper/carrier, a load-rated front-accessible subassembly, moved/shortened modules, or a separately gasketed structural service hatch must be compared against genuine service paths and enclosure rigidity/air leakage. Before choosing, test *actual physical connector and tool solids* in the complete K24 100↔120↔150 sequences and confirm that the metal connector can be inserted, locked and removed *after surrounding boxes are fitted*. Design load-rated second support for modules 0/1 and 12–15 while each guide is released. If a hatch is chosen, restore MDF panel stiffness, sealing and all air-volume/DSP assumptions.

**Engineering decision: guide02 is geometrically promising but unqualified; guide10 face-bolted plate approach is rejected as directly tool-inaccessible. All existing K18 DXF remain CNC HOLD.**