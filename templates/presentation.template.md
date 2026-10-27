# Public presentation booklet — required content and reading order

This is the human-facing presentation for the **AI Agent track**. It is separate from the fourteen-section design statement (`proposal.md`) and the technical appendix. Use your own graphic layout, page sizes, colours and page counts; keep the order and information below. A cover and a short thesis may come first. Use the existing proposal-heading mapping in `docs/presentation-guide.md` to carry the complete argument within this reading spine; it is not permission to omit site analysis, complete phase one or urban-design enlargement. Additional explanatory pages may sit within a section. Do not replace the whole-site plan with a city render or a sequence of local views.

## 1. Whole-site plan

Show the fixed full competition boundary (1,656 km² nominal), both fixed pilot areas, settlement/centre hierarchy, the five systems and their approximate scales, primary transport, resource/infrastructure relationships, protection/reserves and how development phases connect. Use a legend, scale, orientation and a short explanation of why the structure fits this site. A coloured land-allocation layer without these relationships is insufficient. Distinguish proposed, indicative, preliminary screening and fixed information. Capacity can be a justified scenario/range; reserve land is not automatically built area, irrigated land or realised demand.

## 2. Node locations — whole site and independent node insets

Locate the urban-design enlargement and each selected node on the whole-site plan. Use independent detail insets at suitable scales; the enlargement need not contain the nodes. Distinguish the chosen master study area, phase-one construction and first works; do not imply nodes lie inside an extent when they do not. Use the **same node ID and title** here and on every node sheet. Show the streets, paths and service/system links between the nodes; explain their contribution to the wider city. Do not invent a direct connection where the design uses separate links through the wider network. Distant/combined nodes need legible insets or callouts, not a misleading crop. This locator is mandatory even if the whole-site plan already contains node symbols.

## 3. Three node sections — repeat once for each manifest.nodes entry

**Heading:** `[node ID] · [official node topic] · [scheme-specific place name]`

**Location:** where it sits in the whole city and relative to the master area, its extent, construction phase, access and relationship to the other nodes. Reuse the locator ID.

**Design explanation:** why this location, who arrives/stays/works here, how machines/services operate under normal and relevant abnormal conditions, necessary dimensions/interfaces, and which upper-level design promise this place tests.

**Presentation images:** at least one aerial and one eye-level view showing the proposed finished place. Finished concept images must agree with the geometry and be labelled as illustrations, not measurements or photographs of an existing city. Register AI images and their controls in `image_provenance.json`. If no image tool is available, keep the established massing-only exception, label it visibly and explain the limitation; do not rename a control render a finished image.

**Design evidence:** include the plan, section or movement diagram needed to explain this place. Decisive dimensions, sections/elevations and formal massing relationships remain here. Extended checks, raw massing iterations and repeated image/control comparisons belong in the technical appendix. A set of effect images without spatial design does not meet the requirement.

## 4. Phasing

Show what comes first and later, the facilities/services needed for each phase to operate, observable expansion triggers and key dependencies. Explain what happens if later phases are delayed. Use the same phase boundaries and numbers as the geometry and statement.

## 5. Key indicators

Present the main population/jobs, housing, land/density, water, energy and compute figures, with units, scope, phase and evidence tags. Distinguish whole-site, master-study-area and actual phase-one totals; identify the extent of any first-works account. Put full calculations and the complete compliance matrix in the appendix; do not turn the main presentation into a gate report.

## Caption and evidence check

For each map/diagram, identify its actual extent and phase, source/assumption status and the spatial question answered; add title, readable labels and useful legend/orientation/scale or dimensions. Show optional external context with `study_only` / `not_secured` status, separately from on-site development and resource totals. Disclose missing organiser evidence and next verification, and separately identify unfinished entrant work. Neither is resolved by copying an old PASS.

## Separate technical appendix

Include raw geometry/massing controls, extended technical sections and calculation detail, full land-use and resource accounts, image-to-control comparisons, requirement-to-evidence index, assumptions, sources, tool/model disclosure and automatic-check limitations. Keep the original controls in `renders/` and every checked figure on disk. Use `self_check.json` as the current machine report; do not copy an old PASS into the booklet as design approval.

Default commands produce `drawings/a3-booklet.pdf`, `drawings/a3-technical-appendix.pdf` and `drawings/presentation-index.json`. The index gives the page range of each required main section and the separate appendix. A custom layout must preserve those outputs and update the index truthfully. Presence/page-order checks do not assess the clarity or design quality of the pages.

## Design evidence belongs in the main story

The formal booklet is a complete design argument, not a fixed six-page abstract: site judgement → overall strategy → programme/capacity → movement/infrastructure → phase-one urban design → three nodes and use scenarios → implementation → indicators/trade-offs. Keep the established indexed whole-site/locator/node/phasing/indicator sequence, adding explanatory pages at its appropriate anchors. Page count follows the design.

Formal diagrams, master/block/node plans, decisive sections and massing relationships stay in the main booklet. Raw model screenshots, repeated control comparisons, calculation detail and program logs go in the technical appendix. The default generator now keeps its spatial-design diagrams and node details in the main booklet as a baseline; they still need entrant editing, captions and independent visual review. Use `booklet.pages` / `booklet.section_pages` for the full argument.

See `brief/design-depth.json`, `docs/design-depth-guide.md` and `docs/reference-examples.md`. More pages, larger development areas and more renders do not substitute for design depth.

### Independent design extents and dispersed nodes

The overall plan covers the entire issued site. Distinguish (1) whole-site planning, (2) actual first-phase construction and associated facilities, (3) the urban-design enlargement, (4) each selected node and (5) rendering camera frames. These are not interchangeable boundaries. The enlargement may contain some or none of the three selected nodes. Nodes need not adjoin, share one district, fall within master_area.geojson, or all be built in the first phase. State each node’s location, phase, users and role in the whole-site plan. First-phase completeness means independently operable living and production systems, with evidenced transport, power, water, communications and other relevant connections; it does not mandate a single contiguous footprint. Keep local land-use/FAR/GFA statistics separate from off-area facilities and their indicators. Do not force a compute campus beside housing or a heat user just to group nodes; justify buffers, cooling and any actual heat network. Camera crops illustrate a design; they do not define its scope.

C01 includes the **main entrance and arrival sequence**. All schemes must locate and explain main access, regional connections and people/freight separation in the overall plan even when C01 is not selected; full entrance-node detailing is required only if C01 is selected. The ten topics are optional deepening choices within three groups, not a licence to omit essential city systems from the overall plan. A01/B03/C02 is one valid selection, not a mandatory selection or adjacency model. Use a whole-site locator plus separate, consistently labelled detail insets for dispersed nodes; never crop an outlying node out or draw a fictitious direct link.

### A0 construction phasing map and programme

The A0 board must show a legible, labelled Phase 1/2/3 zoning map and a matching programme table. Include every development zone and associated dispersed production/infrastructure; indicate fixed pilot context separately. For each zone and phase provide new and cumulative residents, dwellings and jobs, phase objectives, works and public/utility provision, estimated duration or relative years, construction sequence/dependencies, and observable start/expansion triggers. Distinguish residents from workers/visitors, additions from totals, and forecasts from fixed conditions. Capacity ranges are allowed with assumptions. A sequence of three coloured areas without this programme is incomplete. Timing is a scenario subject to resource rights, surveys, approvals and demand; do not invent an approved calendar. Totals must reconcile by phase and with metrics.json (including phase-one residents). Areas, phases and district IDs must match geometry/phasing.geojson; separate facilities may share a phase without being adjacent.

Provide `phasing_programme.json` using `templates/phasing_programme.json`; reference the map and A0 board. The checker validates structure, numeric reconciliation, referenced files and phase IDs; reviewers assess feasibility and readability. Automatic checks do not approve the construction programme.


### Complete city scope — 2026-10-27 clarification

Design the complete city layout across all proposed construction phases, not only Phase 1. Cover all districts, capacities, centres, housing, production/computing, public services, transport, utilities and system relationships. Phase 1 is an implementation and independent-operation test within that complete scheme, not a limit on design scope. Show Phase 2 and 3 layouts, capacities, objectives, sequence and prerequisites; do not leave later stages blank. Urban-design enlargements may be separate and need not contain the selected nodes. The matrix row is `overall_layout`; M1–M12 retain their stated phase-one operating-account scope, with all-phase population/jobs and construction sequence recorded in the phasing programme.

### Siting and view validity

Do not organise the city to fit the three selected nodes into one image. Justify adjacency or separation using the relevant terrain, access, utility, noise, risk, operations and public-life conditions; no universal distance or requirement to co-locate is imposed. Identify each image as whole-site diagram, complete-city view, district/detail view or node view. Register its geographic footprint, scale/extent and, for a physical perspective, position, target, height and lens/FOV (or explicitly identify a diagrammatic orthographic/axonometric projection). A matching geometry-derived control is required for each finished perspective; an eye-level scene inferred from an aerial alone is not a verified camera view. Keep geometry checks separate from visual judgement. The picture must not silently add, relocate or resize buildings, invent topography or replace the complete layout. A local neighbourhood aerial cannot serve as evidence for the entire 1,658.82 km² site.


## Coordinated city diagrams

## City-scale system diagrams and overall spatial view

Design a useful city before composing its node images. First organise the functional programme and city structure; then test the coordinated systems, resolve urban design and three nodes, and communicate the same complete layout through an overall axonometric or oblique birdseye view. Iterate when a diagram exposes a conflict. Neither co-location nor separation is a design objective: justify both through the city’s operation and site conditions.

The main booklet must explain the following six themes. They can share sheets or be combined where legible; six themes do not prescribe six pages. Use the same underlying city geometry, district names, orientation and comparable scales, with clearly identified insets where needed. Retain an issued-whole-site locator; a city-scale study does not shrink the overall planning obligation. The whole-site framework need not depict every building at the same detail as an urban-design enlargement.

| Theme | Question | Required spatial evidence |
|---|---|---|
| Planning structure | How the city is organised: centre hierarchy, district roles, principal axes, edges and relationships between districts. | Show named centres/districts, their scale or capacity and the connections that make them one settlement system. |
| Functional programme | Where housing, civic/commercial services, computing/production, agriculture and logistics go, and why uses adjoin or separate. | Locate functional areas and anchors; show necessary adjacencies, compatible mixtures, service links and reasoned conflicts or separations. |
| Streets and mobility | How the city is reached and works: main access, street hierarchy, public transport, walking/cycling, freight and decisive interfaces. | Draw connected routes, hierarchy, main arrivals, crossings and service/freight access; distinguish proposed external approaches from secured access. |
| Ecology and landscape | How terrain, seasonal channels, protection and open space form a connected landscape, and how planting/shade respond to water and climate. | Show linked corridors and open spaces, drainage/terrain relationships and evidence status; do not invent lakes, permanent green cover or surveyed flood limits. |
| Land use | How land is allocated by spatial unit, with use categories, mixed-use conventions, areas and capacities. | Show readable development blocks or appropriate land units, categories and legend; reconcile land areas and capacity assumptions without double counting. |
| Public space and services | Where residents and workers gather and obtain services, and how centres and neighbourhoods connect. | Locate civic anchors, schools/health/markets and public spaces; show service hierarchy, walking connections and declared capacity/catchment assumptions. |

Explain the decision each diagram tests and what changed because of it. A functional diagram explains programme and operating relationships; a land-use plan allocates spatial units and reconciles their areas. They may be combined only if both remain clear. Recolouring one undifferentiated map six times is insufficient. Use abstraction appropriate to the question; exhaustive building or parcel detail across the entire site is not required. Do not copy a reference city’s water, vegetation, street pattern, density or urban form.

The overall spatial view shows the complete proposed city layout or settlement system, including its district/centre hierarchy, principal streets, massing/height character, landscape and productive context at an appropriate level. State its geographic extent, projection/camera, phase or full-build-out scenario, and what is simplified. An axonometric may be diagrammatic; a finished perspective must match its geometry-derived camera control. If distant parts cannot be read in one physical view, use a clearly labelled overall axonometric plus consistent insets rather than a fictional camera or a collage pretending to be contiguous. Do not relocate facilities to put all three nodes into the frame. A local neighbourhood or node aerial cannot replace this overall view, and the overall view cannot replace the system diagrams.

Show the Phase 1/2/3 construction map and matching programme using the same district IDs and layout. Keep population, dwellings, jobs, public/utility services, sequence and dependencies consistent with the city diagrams. Detailed selected nodes test the city decisions; they do not determine the city’s extent. There is no fixed AI Agent booklet page count or requirement to pad the report. Additional detail, images or pages earn no credit by themselves.

Link these drawings in the existing `overall_layout` row of `design_depth_matrix.json`, with associated geometry, metrics and proposal sections. The six thematic questions and overall-view fidelity are content-review matters; file existence does not prove they are answered. No separate parallel form or additional pass badge is introduced.


Method and review basis: [docs/city-design-method-basis.md](https://github.com/XcityUS/xcity-ai-competition/blob/main/docs/city-design-method-basis.md). Define district boundaries/IDs, functional allocations, land-use units and construction phases distinctly; relate them through the same geometry and accounts. At city scale show principal/secondary streets and readable district/block structure, with local detail in appropriate enlargements. Required planning diagrams and plans cannot be replaced by renders.


### Full-site zoning and the road framework

Follow [the whole-site zoning workflow](https://github.com/XcityUS/xcity-ai-competition/blob/main/docs/whole-site-zoning-workflow.md). The entire issued site needs an explicit base zoning proposal, not a small city plan over an unexplained background. In structure.geojson, use plan_role=base_zoning with district_id, name, primary_use and basis_ref plus system; separate optional overlapping relations as system_overlay. Draw the primary and secondary road skeleton in movement.geojson using road_class; network denotes users, not hierarchy. Recompute the full-site area account. G12 checks coverage, overlap, identifiers and road-class records, not design quality. Local enlargements and node images do not replace these full-site plans.
