# Requirements reread: ac96714

Reviewed 27 October 2026 against upstream `ac967146488c9b1515f865d942009080c179b7d5`; previous V8 source snapshot was `307eca1`. This is a requirements/impact review, not a new design approval. Historical V8 drawings and source fingerprints are retained unchanged.

## Authoritative changes read

- AGENTS.md: complete all-phase city scope, siting/view validity, illustration evidence, six coordinated city themes and an overall spatial view.
- docs/city-system-diagrams.md and docs/city-design-method-basis.md: the six themes, distinct spatial accounts, principal/secondary streets and readable district/block structure. The references are method guidance, not Argentine statutory approvals.
- docs/design-feedback-loop.md: record design failures, fix the responsible layer, and avoid turning permission to disperse into separation as an objective.
- brief/design-depth.json, brief/requirements.json and templates/design_depth_matrix.json: `overall_layout` replaces `phase_one` as the city-layout matrix row. M1-M12 retain their phase-one operating scope.
- docs/visual-guide.md, docs/presentation-guide.md and renderer/fingerprint changes: view footprint/camera/projection and matching controls; no procedural plants, PV or entourage by default; renderer/policy changes invalidate controls.
- brief/site-conditions.en.md: the previously reported narrative seam/area conflict is corrected. Current geometric site area is 1,658.819819 km2; nominal project label remains 1,656 km2. Added-seam hydrology remains unclassified.

## Consequences for V8

| Requirement | Existing V8 evidence | Required work |
|---|---|---|
| Complete all-phase city | R/C/P structure and regional options only | Decide the complete proposed layout and later-stage district/capacity programme; do not leave Phases 2/3 as unnamed future options |
| Planning structure | Partial hierarchy and district roles | Resolve centres, district capacity and primary/secondary links on the complete layout |
| Functional programme | Partial separation of residential, centre and production | Test necessary adjacency, compatible mixtures, service links and competing choices; 3.4 km is an outcome of a draft, not proof or a required buffer |
| Streets/mobility | Corridor alternatives and a few residential backbone lines | Build a connected hierarchy, arrivals, public transport, walking/cycling and decisive freight/service crossings; distinguish study from secured access |
| Ecology/landscape | Terrain and flood/channel screening | Design connected open-space/landscape and shade/water relationships rather than treating screening alone as the landscape plan |
| Land use | Gross role envelopes | Allocate readable land units/blocks and uses, explain mixtures, and reconcile net land and capacity; district polygons alone cannot stand for all accounts |
| Public space/services | Candidate school and service reservations | Establish service hierarchy, capacity/catchments and accessible connections for residents and workers across all phases |
| Overall spatial view | None; V8 sheets are 2D diagrams | Create an overall axonometric or oblique birdseye from the same complete layout with extent, projection and phase; no local aerial as a city substitute |
| Phasing | Broad release-search extents | Deliver phase geometry plus zone-by-phase new/cumulative population, housing, jobs, services, works, timing, dependencies and triggers |
| Node imagery | Older controls/views are historical | Rebuild node design and geometry-linked control cameras after overall decisions; do not infer an eye-level view from an aerial or keep images after geometry changes |
| Matrix/results | Older submission evidence remains historical | Complete `overall_layout` evidence and rerun current checks after rebuilding; existence of files or a pass badge is not content approval |

## Working decision

V8 remains a **partial district-structure study**, not the full answer. Do not turn separation into a new fixed design recipe, fill six pages by recolouring one map, or impose a booklet page count. Re-establish site/programme and the complete city layout; coordinate the six themes using consistent geometry/IDs; test blocks, streets, capacities and services; deepen selected nodes; then derive the overall spatial view and reconcile implementation accounts. Required plans and diagrams remain necessary alongside renders.
