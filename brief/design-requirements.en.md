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

The organiser-defined whole-site boundary is fixed. The overall plan must address the entire supplied scope; a locally selected phase-one district or urban-design enlargement does not replace or reduce that overall planning obligation. Entrants justify the location and capacity of the first complete district within that structure.

Machine-readable twin: `requirements.json.design_depth` / `design-depth.json`. The existing three geometry tiers remain compatible; the urban-design enlargement is an explicit design test within the master area, not an additional mandatory geographic area.

| Level | Must explain | Spatial evidence |
|---|---|---|
| Whole-site structure | Settlements, production, protection, transport, resources and growth | Overall structure and system links; capacity scenarios and phasing |
| Complete phase-one district | Life and production remain complete if later phases never happen | Master plan; roads, public services, production, utilities and first works |
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
