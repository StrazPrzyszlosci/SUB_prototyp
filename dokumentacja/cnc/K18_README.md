# K18 | CNC contour review — DO NOT MACHINE

All dimensions in **mm**. These three AutoCAD-2015 DXF files are **shape-reference drawings, not CNC orders or CAM toolpaths**. All cut profiles are on `REFERENCE_PROFILE_HOLD`; optional 3mm mounting recess envelopes are on `POCKET_3MM_CONCEPT_HOLD`; Ø355.8 factory reference cutouts use `FACTORY_CUTOUT_REFERENCE_NO_CAM`; labels are `LABEL_NO_CAM`. There are **no MDF screw holes** on the front; the Dayton factory flange uses 8×Ø6.5 on PCD Ø368 and must not be treated as wood drill diameters.

- [MDF22 cabinet and provisional ribs](K18_korpus_i_wregi_MDF22_NIE_CNC.dxf): 18 contours, 2 reference driver bores and 24 proposed 3mm grooves in top/bottom panels. The 10mm web is exceptionally slender.
- [MDF8 modular displacement boxes](K18_skrzynki_regulacji_MDF8_NIE_CNC.dxf): 120 faces for twenty six-panel boxes.
- [MDF8 hypothetical laminated rail profiles](K18_prowadnice_laminat_MDF8_NIE_CNC.dxf): 24 faces of 12 two-ply rails, with 3mm extra tongue at each end. Upper solid retainer lips are **NOT ASSEMBLY QUALIFIED** and should be redesigned.

Profiles are placed apart **for viewing only**, not on stock sheets; cutter diameter, radii, tool compensation, machine, part tabs, glue, material tolerances, sealing and fit are unselected. Mounting screws, locking clips, MDF inserts, terminals, grille, cable fixtures and gasket details do not exist in this package. Full [K18 report](../../raporty/K18_projekt_CNC_mocowania_wkladow.md) and [numerical audit](../../wyniki/k18_mocowania_i_CNC_podsumowanie.json). Regenerate from repo root: `node skrypty/k18_cnc_kontury.js`. **CNC HOLD.**
