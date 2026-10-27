# Design requirements · Open Agent Call

> Machine-readable version: `brief/requirements.json`. If the two disagree, the JSON wins.

---

## A. How to read this

| Class | Meaning | If not met |
|---|---|---|
| **Mandatory M1–M12** | Must be answered | Gate G6 fails; no scoring |
| **Scored metrics** | Affect the score | Not eliminated; shows up in the relevant dimension |
| **Prohibited** | Must not appear | Review ends |

Most figures have no pass mark. The gates check **whether you gave the number, with a correct unit and a stated basis** — not whether you hit a threshold. Missing required numeric fields fail automatic compliance. Supplying a number and basis does not establish a reasonable capacity, complete design or engineering feasibility. How good it is belongs to scoring.

---

## B. The site and its hard conditions

The land, the protected pilot area, water, earthquakes, the Zonda, dry channels and flash floods, dark sky, the missing road, the rule that phase one stands on its own, and what data is and is not supplied: **`brief/site-conditions.en.md`**, shared with the Design Practice Call.

For this call:

- All core construction geometry under geometry/ lies inside `brief/site-package/boundaries/scope_9_13.geojson` (50 m tolerance), and no new buildings may invade either fixed pilot part. Classify the agrivoltaic fields and living quarter separately. Optional external research belongs under context/, marked study_only / not_secured, and is excluded from construction accounts. The self-check tests encoded geometry and labels; it does not establish rights or suitability.
- Cite the matching `SRC-*` id in your `sources.json`. Indicative zoning is cited as `indicative` only.
- **You may assume — in `assumptions.json`, with the value, its source and the reason. An undeclared assumption counts as invention.**
- The hard conditions are design constraints, not background. A scheme that shows no trace of them scores low on D1. Mark the flood corridors in your geometry and state the basis for their width; draw the access corridor as phase-one works.

---


## C. Four connected levels of design depth

The organiser-defined whole-site boundary is fixed. The overall plan must address the entire supplied scope; a locally selected phase-one district or urban-design enlargement does not replace or reduce that overall planning obligation. Entrants design the complete city layout across all proposed phases, justify district locations and capacities, and then demonstrate that the first phase can operate independently.

Machine-readable twin: `requirements.json.design_depth` / `design-depth.json`. The existing three geometry tiers remain compatible; the urban-design enlargement tests one or more coherent parts of the complete city layout, not an additional mandatory geographic area.

| Level | Must explain | Spatial evidence |
|---|---|---|
| Whole-site structure | Settlements, production, protection, transport, resources and growth | Overall structure and system links; capacity scenarios and phasing |
| Complete city layout and implementation | All districts, capacities, systems and construction phases form one complete design | Complete layout, phase-by-district programme, networks, public facilities and first works |
| Urban design enlargement | How the master layout forms streets, blocks and public life | Block plan, building heights/massing, public space and decisive sections |
| Three detailed nodes | Location, users, spatial organisation and operation | Locator, detailed plan, necessary sections/elevations, massing and concept views |

Combine drawings where useful. Choose sections/elevations for the actual spatial or operational question; do not mechanically produce identical sets for every node. No fixed booklet length, minimum development footprint or additional render quota is introduced. The three-node selection and existing view requirements remain unchanged.

Each new entry supplies `design_depth_matrix.json` (v2; v1 is readable only for the two listed legacy paths) (template in `templates/`), identifying the actual decision, scope.extent and scope.phase, and linking each level and selected node to drawings, geometry, metric keys and proposal headings. A declared gap identifies organiser_data, professional_verification or entrant_design, with next verification and responsible role. Missing organiser data does not waive required entrant-authored drawing/geometry evidence. A missing organiser dataset is not itself a failing design claim; identify the gap honestly. File existence and reference consistency can be checked automatically; design adequacy remains unassessed until independent review.

## D. Mandatory M1–M12

Each one gets a status in `compliance_matrix.json` pointing at the section of `proposal.md` that answers it. Where a metric key is given, declare the value, unit and evidence tag (computed / sourced / assumed / indicative / declared) in `metrics.json` as well. **Unless stated otherwise, M1–M12 describe phase one at full build-out and occupancy.**

**M1 · Hourly carbon-free energy match** (`hourly_cfe_match_pct`, %) — share of hours in a representative year whose use is covered by carbon-free power in the same hour. State the generation mix, storage duration, and whether the match is **physical** or **contractual**. Daytime solar is easy; this is about the night.

**M2 · Peak IT load in phase one** (`peak_it_load_mw`, MW) — with the grid capacity you assumed. For scale: 40 MW is roughly a 20,000–30,000 m² data hall.

**M3 · Annual water demand** (`annual_water_demand_m3`, m³/yr) — by use: `water_domestic_m3`, `water_compute_m3`, `water_agriculture_m3`, `water_landscape_m3`, `water_industry_m3`. **The five must add up to the total (2% tolerance)**; the self-check tests it. Say which line panel-cleaning water sits in.

**M4 · Cooling WUE** (`wue_l_per_kwh`, L/kWh) — with the cooling type (air / liquid / hybrid / dry) and the PUE that goes with it. Air saves water and costs power; liquid the reverse. Claiming both is not accepted.

**M5 · A 30% water shortfall** — 30% less water than your phase-one demand (M3). Which use stops first: a priority order, what happens in the city at each step, how many people are affected, and whether compute load comes down with it.

**M6 · Human-machine at-grade interfaces** (`human_machine_interfaces`, count) — where autonomous machines and pedestrians meet on the same level: road crossings, the ends of shared streets, kerbs or loading points shared by people and machines, driverless-shuttle stops on a machine route; grade-separated crossings do not count. **Mark each one in `geometry/movement.geojson` as a Point with `kind: "interface"`**; the self-check counts them and the declared value must match.

**M7 · Machine traffic rule** (`machine_traffic_rule`: `separated` / `mixed` / `time_shared` / `combined`) — where each rule applies and how it is enforced.

**M8 · Public audit mechanism** — who publishes power, water, generation and compute-load data, how often, and who can check it independently.

**M9 · Control and succession of the compute asset** — who owns and runs it, and what happens if that operator leaves.

**M10 · Triggers for phases two and three** — population, occupancy, grid capacity, water: **observable** conditions, not a timetable.

**M11 · Irreversible decisions** — at least three phase-one decisions that cannot be changed later, and why that is acceptable.

**M12 · Jobs, residents and dwellings reconcile** (`jobs_phase1`, `residents_phase1`, `dwellings_phase1`) — if residents far outnumber jobs, who the others are and what they live on.

---

## E. Scored metrics

| Metric | Key | Unit | Note |
|---|---|---|---|
| Waste-heat reuse | `waste_heat_reuse_pct` | % | Name the receiver |
| PUE | `pue` | ratio | Consistent with the cooling type in M4 |
| Water reuse | `water_reuse_pct` | % | Treatment level and reuse |
| Shaded share of the main pedestrian network | `shaded_pedestrian_pct` | % | Whether walking works at all in a desert |

### Recomputed from geometry (gate G4, 2% tolerance)

Declared with evidence tag `computed`; the self-check recomputes them:

| Metric | Key | How |
|---|---|---|
| Master design area | `master_area_km2` | Geodesic area of `master_area.geojson` |
| Site coverage | `site_coverage_pct` | Building footprint ÷ master area |
| Gross floor area | `gfa_m2` | Σ footprint × floors |
| Floor area ratio | `far` | GFA ÷ master area |
| Open space share | `open_space_pct` | `open_space` in `land_use` ÷ master area |
| Human-machine interfaces | `human_machine_interfaces` | Points with `kind: interface` in `movement.geojson` |
| Area per system | `structure_km2` | `structure.geojson` summed by `system` |

`master_area_km2`, `site_coverage_pct`, `far`, `open_space_pct`, `human_machine_interfaces` and `structure_km2` are required. **Do not enter a good-looking number; enter one that can be computed.**

---

## F. Prohibited

Any one ends the review:

1. Personal data, confidential material or non-public spatial data
2. A claimed official endorsement, approval or statutory conclusion
3. Discriminatory or harmful content
4. Off-topic material
5. Changes to any file outside your own submission directory

These **do not count as answers**: an adjective without a number; a reduction claim with no baseline; waste-heat reuse with no named receiver; a water-shortage response with no priority order; a jobs figure with no skills mix and no named trainer.

---

## F2. What the panel looks for at scales 2 and 3

- **The master area comes from the site.** Its edge follows what the terrain, the channels, the pilot area and the way out tell you, and the statement says why it is here and why it has this shape. A rectangle drawn for convenience reads as an unexamined site.
- **A node is designed in full.** Buildings, planting, paths, water and shade are in the geometry, so that the massing renders already show how people use the place. A node with a few boxes on bare ground is not a detailed design.

---

## G. Deliverables

Format and commands: `docs/submission-guide.md`. Drawings and renders: `docs/visual-guide.md`.


### Node selection: one per group (26 October 2026)

New submissions choose exactly one node from each group, three nodes total:

| Group | Available nodes |
|---|---|
| Living and public space | A01 Future housing; A02 Art and culture; A03 Public space in heat and Zonda wind |
| Production and infrastructure | B01 Drone port; B02 Logistics and international gateway; B03 Compute campus and waste heat |
| Urban interfaces and environment | C01 Entrance and arrival; C02 Agrivoltaic/city edge; C03 Seasonal river park; C04 Street shared with driverless vehicles |

A combined design is welcome, but each selected node needs its own distinct ID and the required design evidence. Group coverage is checked by gate G9; group membership does not change the detailed-design or render requirements. All submissions must cover groups A, B and C; there is no earlier-node-number or any-three exception.

## Whole-site structure: minimum design questions

The whole-site study must answer all six items: (1) settlements and a hierarchy of centres, including the role of land not urbanised; (2) the location, approximate scale and relationship of all five systems; (3) primary external and internal transport and human/machine connections; (4) resource infrastructure for power, compute, water, reuse, waste and communications, with declared assumptions where data is missing; (5) connections to both fixed pilot parts and the two parcels; (6) the relationship between phases, access, services and observable expansion triggers. Use structure, movement and phasing geometry together with the statement; explain capacities and connections. A site-covering coloured zoning diagram alone is insufficient. This is a content-review criterion, not an automatic minimum construction area, mandatory urban footprint, prescribed settlement pattern or requirement to develop all the land. Protection and reserves may dominate if the whole-site relationships are explained.

Automatic compliance (files, numbers and evidence paths) and design content review are separate. PASS 12/12 means the encoded automatic checks passed. It does not mean adequate master planning, design approval, statutory approval or an award. `ready_for_review` means ready to be reviewed. G12 checks evidence existence, not whether the evidence convincingly answers these questions.

## Flood data: screening versus verified restrictions

- **Seasonal channels:** `water/channels_dem.geojson` contains DEM-derived channel lines, not surveyed banks. Permanent construction on an actual dry channel is prohibited. The checker uses indicative line buffers to flag possible conflicts for review; those buffers are not statutory setbacks. Smaller washes are not comprehensively mapped.
- **Flood-sensitive screening:** `water/flood_sensitive_dem.geojson` is a terrain screening model (within 1.5 km of a mapped channel and HAND less than 3 m, using a 60 m DEM), approximately 503 km². It is not a surveyed design-flood extent, a verified hazard zoning instrument, or a blanket permanent no-build area. “Outside the screening band” does not establish flood safety.
- **Verified restrictions:** no surveyed design-flood boundary, design discharge/return period or verified flood setback is supplied. Do not invent one. State assumptions and explain proposed avoidance, conveyance and protection; identify the hydraulic and field verification needed before implementation. Buildings in the screening layer are reported for content review, not failed merely for being in that layer.

## Metric scope and version

For matrix v2, master_area_km2 is the supplied master polygon, while GFA, coverage and FAR use building portions clipped to it. Outside-master GFA is reported separately; neither value is automatically phase-one built capacity. Declare actual construction phases, first works, external infrastructure and future scenarios separately. Version-one metrics retain their historical whole-package-building numerator so existing records remain reproducible. V2 land_use partitions master_area without material overlap or omission: bookkeeping tolerance is max(100 m², 0.01% of master area), not survey accuracy. The five whole-site systems may overlap and are not subject to that land_use partition rule.


## Final public submission language

Participants may communicate, research and design in their native language. Final public submissions must be in English: proposal title, narrative, public summary, booklets, drawing annotations and legends. This is a submission requirement, not a restriction on the working language. Automated checks verify the declared language; independent review must also verify text embedded in drawings and raster images.


The public gallery preserves each submission in English in every website interface language. The organiser will prepare clearly labelled Chinese review translations for the review stage, retaining the English originals as the reference. Entrants need not submit a separate Chinese version.


### Confirmed under-panel planting

The organiser confirms forage grass and jojoba as the fixed under-panel planting programme in the existing agrivoltaic fields. Retain both. Crop allocation, planting ratios, irrigation demand, yields and detailed agronomic parameters have not been supplied: state assumptions, design implications and verification needs. Do not present other crop or animal combinations as organiser-confirmed conditions.


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


### Geometry and illustrations

Automatic scene generation must not silently turn energy land into installed PV, shade routes into irrigation channels, or open space into established trees. Procedural planting, PV tables and entourage are off by default. Explicit roof-PV and water-channel properties describe submitted design assumptions, not verified installations. Illustrations cannot establish capacity, planting survival or water availability. Regenerate controls and dependent images after geometry, scene policy or renderer changes; visually compare the result with the submitted plan.


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

## Trace each district edge to a decision / 分区线要能追溯到设计决定

Read and apply `skills/xcity-city-design/SKILL.md` before geometry generation. For each meaningful district, explain its role/users, edge logic, source or declared assumption, access/service relationship, capacity basis and construction dependency in the existing proposal and account. Terrain/drainage, proposed corridors, centre/service relationships, operating interfaces and justified phase boundaries can inform edges. Where an edge is a design choice, say so. Rectangles, nearest-centre partitions or suitability pixels alone are not a functional zoning argument. Do not invent parcel boundaries, existing roads or detailed surveyed constraints.

At city scale show meaningful district and block relationships; resolve the selected urban enlargements without claiming that every hectare requires detailed parcels. Reserve and connect public-service sites before filling land with repeated housing modules. Overlay functions, roads, landscape and service access from the same geometry, inspect conflicts, and revise the organising layout before node views or finished renders. Keep a drawing when it tests a decision, required verification or clear communication, rather than adding sheets mechanically. No extra submission form or fixed site/population/page quota is introduced.

分区须在既有方案说明和土地账里讲清：用途与使用者、边界为何落在这里、资料或假设、交通和服务联系、容量依据、建设条件。地形水文、拟建路廊、中心与服务关系、生产运营和合理分期都可支持边界；设计选择应明说。不能只用矩形、最近中心自动分割或适宜性像元直接充当功能规划。先按使用与容量预留公服，再排街坊和住宅，叠合道路、功能、景观与服务并处理冲突，最后深化节点和渲染。不新增填表负担，不限定开发面积、人口或页数。

## Visual-first A0 / A0以空间设计为主

Use the A0 board to communicate the city: a dominant overall plan/axon, coordinated functional/road/landscape diagrams, legible district and centre relationships, necessary node evidence and a concise construction sequence. Keep only numbers that materially explain scale, capacity, a resource constraint or phase choice, clearly scoped and tagged. Full district-by-phase population/dwelling/job accounts, detailed metric grids, all source/evidence columns and logs remain in the technical appendix and machine files. The phase map is still required; a dense spreadsheet or dozens of numerical badges is not its replacement. There is no additional fixed number quota and fewer numbers do not excuse missing calculations. The default A0 now summarises the three stages visually rather than reproducing every district row.

A0是讲清空间方案的展板：以全域总图/轴测为主，配功能、路网、景观、中心关系和必要节点图，并说明建设顺序。只保留直接支持尺度、容量、资源约束或分期判断的关键数字，标清范围与依据。完整分区分期的人口、住房、岗位、指标及来源表和日志放技术附件与机器文件；A0仍须有分期图，不用密集Excel式表格，也不改成满板数字卡片。不新增固定数字数量限制，更不取消计算义务。
