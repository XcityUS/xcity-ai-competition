# Node IDs and final submission language — 27 October 2026

## Current organiser decisions

- Every submission uses exactly one node from A (living/public space), B (production/infrastructure), and C (urban interfaces/environment). A and B each have three choices; C has four.
- The only valid node IDs are A01, A02, A03, B01, B02, B03, C01, C02, C03 and C04. There is no earlier numbering alias, fallback lookup or node-selection exemption.
- The Finite Water City selection is A03 (public space in heat and wind), B03 (compute campus and waste heat), and C03 (seasonal river park).
- Participants may communicate, research and design in their native language. Final public titles, narrative, summaries, booklets, drawing annotations and legends must be English. Official organiser instructions remain bilingual.

## Sources and verification

The authoritative node catalogue is `brief/site-package/nodes/design_nodes.json`. Manifest validation and `scripts/node_selection.py` use that catalogue. The schema rejects unknown IDs; the selector enforces one per group for every package. The gallery provides both IDs and readable names. English declaration is machine checked; language in raster drawings also needs human review.

Existing source assets, references, filenames, node properties and generated public deliverables are migrated together. No spatial redesign is inferred from a new label. Current boundaries use the issued open-seam closure: only the authorised parcel-junction slit is filled; the remaining exterior is retained. The exact geometry area and revision are recorded in the boundary package.

## Example status and next step

Terrace Oasis is an organiser example, not an entrant. Its existing selection has two A nodes and no B node. It has been withdrawn from the active examples pending redesign, rather than being granted a pass or relabelled as a different design. `gallery/example-status.json` records this status. Aggregate checks explicitly report it as inactive; an explicit check still enforces every current gate and rejects its selection. This is not a node-rule exception or compatibility mode.

The first priority is publishing clear and consistent rules and tools. Only after that will the organiser example be reread and redesigned against them. Automated compliance never certifies design quality.
