# K18 | CNC contour review — DO NOT MACHINE

All dimensions in **mm**. These three AutoCAD-2015 DXF files are **shape-reference drawings, not CNC orders or CAM toolpaths**. All cut profiles are on `REFERENCE_PROFILE_HOLD`; optional 3mm mounting recess envelopes are on `POCKET_3MM_CONCEPT_HOLD`; Ø355.8 factory reference cutouts use `FACTORY_CUTOUT_REFERENCE_NO_CAM`; labels are `LABEL_NO_CAM`. There are **no MDF screw holes** on the front; the Dayton factory flange uses 8×Ø6.5 on PCD Ø368 and must not be treated as wood drill diameters.

- [MDF22 cabinet and provisional ribs](K18_korpus_i_wregi_MDF22_NIE_CNC.dxf): 18 contours, 2 reference driver bores and 24 proposed 3mm grooves in top/bottom panels. The 10mm web is exceptionally slender.
- [MDF8 modular displacement boxes](K18_skrzynki_regulacji_MDF8_NIE_CNC.dxf): 120 faces for twenty six-panel boxes.
- [MDF8 hypothetical laminated rail profiles](K18_prowadnice_laminat_MDF8_NIE_CNC.dxf): 24 faces of 12 two-ply rails, with 3mm extra tongue at each end. Upper solid retainer lips are **NOT ASSEMBLY QUALIFIED** and should be redesigned.

Profiles are placed apart **for viewing only**, not on stock sheets; cutter diameter, radii, tool compensation, machine, part tabs, glue, material tolerances, sealing and fit are unselected. Mounting screws, locking clips, MDF inserts, terminals, grille, cable fixtures and gasket details do not exist in this package. Full [K18 report](../../raporty/K18_projekt_CNC_mocowania_wkladow.md) and [numerical audit](../../wyniki/k18_mocowania_i_CNC_podsumowanie.json). Regenerate from repo root: `node skrypty/k18_cnc_kontury.js`. **CNC HOLD.**


**K20 UPDATE / FABRICATION VETO:** Existing K18 guide profile DXF contains 40 *permanent integral* upper tongues; these are NOT the detachable keepers in the K20 geometry concept. Four K18 pocket sketches per TOP/BOTTOM panel are open at the forward edge (8 total), not enclosed blind sockets. Do not send K18 to manufacturing. See [K20 research and blockers](../../raporty/K20_serwisowe_rygle_i_analiza_montazu.md).


**K21 CRITICAL: verified assembly blockage.** Eight permanent full-height rear guide spines leave at most 130 mm unobstructed X gap at a mandatory simultaneous Y crossing; 12/12 rear K15 boxes (180/210 mm X width) cannot pass without rotation. For the 8 rear large boxes, 90° planar yaw (120mm X projection) plus 6mm per side needs 132mm; there is no proven alternate 3D route. K18/K20 DXF remains CNC HOLD. [K21 evidence](../../raporty/K21_przesmyk_i_weryfikacja_montazu_wkladow.md).


**K22 research option:** a single selected rear rail G17_COLUMN_10 might have to be temporarily absent to create a 259mm X service throat, later restored through a yet-unengineered two-piece structural splice. A 228mm segment fits the nominal loudspeaker cutout only in a centered front-plane projection; no post-installation path, tensile/bending load transfer or actual fastener has been proven. Current K18 DXF remain CNC HOLD. [Details](../../raporty/K22_dzielona_prowadnica_i_przejscie_montazowe.md).


**K23: dynamic candidate path FAIL for adjustable volume.** Explicit continuous swept-AABB nominal geometry with K22's one omitted spine and K15/17 obstacles: 12 of 20 isolated candidate entry routes pass when 36 integral lower lips remain; 20/20 exact axial assembly passes only with all 36 lips mathematically absent. The passing order is *not* a working 150→120→100 L nested state change. In the tested nested order the first 12 insert but the 13th small rear hits retained boxes; the four small-rear inverse candidate extraction paths from full100 fail. Front lateral passage only 2mm nominal symmetric Y clearance. Existing DXFs and joints remain CNC HOLD. [Full analysis](../../raporty/K23_analiza_ruchu_wkladow_i_regulacji.md).

**K24 MANUFACTURING BLOCK:** 16 large module undershelf tool-access regions are only 6–8 mm below nominal 4mm original lip; a hypothetical 14mm tool envelope fails. Ø4.5 mm hole on existing Y8/Y12 MDF spine leaves 1.75/3.75 mm nominal edge ligament and fails the assumed edge-distance screen. Exhaustive rectangular C-space graph under one removed rail and no lower/upper supports finds **no rigid-translation exit** for the four rear small boxes with twelve state-120 large boxes left; exact 19.8L volume step requires all four small. Rotations not tested. NO K18 DXF TO CNC. [K24](../../raporty/K24_dostep_serwisowy_i_przestrzen_translacji.md).
