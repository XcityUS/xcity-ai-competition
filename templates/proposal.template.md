# {{title}}

> XCITY AI Competition · San Juan, 1,656 km² · submissions/{{github}}/{{slug}}
> Write this as an urban design statement a professional would sign — not as a description of your files.
> Keep the fourteen numbered headings exactly as they are (`## 1.` … `## 14.`): compliance_matrix.json points at them and gate G6 checks they exist. You may add `###` sub-headings freely. Delete every line that starts with `>` before you submit.
> Embed figures with paths relative to the package, e.g. `![Structure](figures/fig-01-structure.png)`.

## 1. Position

> agent.1. The idea of this city in a paragraph. A naming system for the city, its settlements and districts; logo direction (described and shown); a visual standard — type, colour, signage logic. What you believe this city is for, in one sentence a resident could repeat.

## 2. Site reading

> Read the site before you design it: water, slope, the Pie de Palo range, the Zonda, seismic risk, the dry channels, the pilot area, the supplied approximately 27.6 km boundary-to-road distance (not route length, surveyed access or proof of utilities). Separate mapped seasonal channels, the DEM flood-sensitive screening band and any verified restrictions. The approximately 503 km² screening band is not a blanket permanent no-build zone. Distinguish fixed agrivoltaic and living pilot outlines; do not invent their interiors. Which of these decided your structure, and how? A scheme that would look the same on another site scores low on D1.

![Structure](figures/fig-01-structure.png)

## 3. Energy and compute

> agent.2 · M1 · M2 · M4. Where generation, storage, substation and compute sit, and why. Hourly carbon-free matching as a method (physical or contractual), what happens at night, the grid capacity you assumed, where the waste heat goes and who receives it. Cooling type, WUE and PUE together.

## 4. Water

> agent.3 · M3 · M4 · M5. A water balance: sources, uses (domestic, compute cooling, agriculture, landscape, industry — they add up to the total), losses, reuse. What is irrigated with what. What stops first when water is 30% short, in order, and what happens in the city at each step.

![Open space and water](figures/fig-05-open-space-water.png)

## 5. Human and machine

> agent.4 · M6 · M7. Two networks — people, and machines plus goods. Every at-grade interface is a Point in geometry/movement.geojson; say how each kind is made safe. Separated, mixed or time-shared, where, and who decides. Kerb, loading, charging, storage.

![Movement](figures/fig-04-movement.png)

## 6. Programme and production

> agent.5 · M12. Programme by use and share. Jobs by type and by phase, with the basis. Phase one: who is here, and do jobs, residents and dwellings reconcile? What is produced on site — including the agrivoltaic fields — and for whom. No jobs figure without a skills mix and a named trainer.

## 7. Urban form

> Start with functional programme and city structure. Supply coordinated planning-structure, functional-programme, street/mobility, ecology/landscape, land-use and public-space/service diagrams from the same city layout. Explain each decision; combine themes where legible. Resolve three nodes as tests of that layout, and supply an overall axonometric or birdseye view from the same geometry, with its extent, projection and scenario declared. Do not force separation or co-location, substitute a local aerial for the complete city, or recolour one map six times. See docs/city-system-diagrams.md. There is no fixed AI Agent booklet page count.

> agent.6. The public three-scale framework contains four connected design tasks. (1) The whole site: settlements and centre hierarchy, all five systems with locations and approximate scales, primary transport, resource infrastructure, connections to both fixed pilot parts, and phasing relationships. Explain how these form a city or settlement system; a coloured zoning diagram alone is insufficient. Capacity may be a justified scenario/range; reserve land is not automatically built, irrigated or active demand. No minimum construction footprint is imposed. (2) The complete city layout across every proposed construction phase: locate and size all settlements/districts, production, public services and utility connections. Do not leave later stages blank. Distinguish complete study areas, urban-design enlargements, phase-one construction and first works, with separate metrics; demonstrate independent first-phase operation if later phases never happen. Explain why the study area is there — write down how water, slope, wind, the way out and the pilot area pushed you there — and its blocks, massing, heights and density (recomputed from your geometry). (3) Urban-design enlargement: explain how complete streets and blocks (or another coherent spatial unit), building heights/massing, public centres, access, servicing/emergency routes, interfaces and decisive sections create public life under terrain, heat, wind and drainage conditions. (4) Three nodes test these overall decisions. Public realm under desert conditions: shade, wind, water, ground. How the scheme uses the main parcel (with the range and its eastern wing) and the south-west parcel (with the pilot area).

![Master plan](figures/fig-02-master-plan.png)

![Land use and density](figures/fig-03-land-use-density.png)

## 8. Governance and data

> agent.7 · M8 · M9. What data the city produces and who may read it. What the public can audit, through what instrument, how often, and who checks independently. Who controls the compute asset and what happens if that operator leaves. At least one named failure mode and its mitigation.

## 9. Phasing

> agent.8 · M10 · M11. Three phases on the site. Phase one stands on its own — housing, jobs, public services, production, people/machine movement, logistics/emergency, utilities/waste and maintenance; identify necessary external enabling works and their evidence/rights status. Observable triggers for phases two and three. At least three phase-one decisions that cannot be changed later, and why that is acceptable. The long-term size you propose, and how many settlements.

![Phasing](figures/fig-06-phasing.png)

## 10. Key nodes

> Locate all three on a whole-site locator before the detailed sections; use separate insets for dispersed nodes. For each: identify location/phase and users, explain arrival/staying/service/emergency movement, spatial organisation and normal/abnormal operation, necessary dimensions and how it tests the overall city promise. Select necessary sections/elevations for its question; combined drawings are welcome. Three nodes, exactly one from each group (brief/site-package/nodes/design_nodes.json), each to detailed design: a plan or section, an aerial view, an eye-level view. Say why these three. make_figures.py renders massing views from your geometry; add your own renders in media/ if you can, and register each in image_provenance.json.

### {{node_1}}

![Plan](figures/node-{{node_1}}-plan.png)
![Aerial](figures/node-{{node_1}}-aerial.png)
![Eye level](figures/node-{{node_1}}-eye.png)

### {{node_2}}

![Plan](figures/node-{{node_2}}-plan.png)
![Aerial](figures/node-{{node_2}}-aerial.png)
![Eye level](figures/node-{{node_2}}-eye.png)

### {{node_3}}

![Plan](figures/node-{{node_3}}-plan.png)
![Aerial](figures/node-{{node_3}}-aerial.png)
![Eye level](figures/node-{{node_3}}-eye.png)

## 11. Metrics and evidence

> The numbers that carry the scheme, each with its evidence tag (computed / sourced / assumed / indicative). Computed ones must match your geometry within 2% — the self-check recomputes them.

![Metrics](figures/fig-07-metrics.png)

## 12. Risks and failure modes

> Not a list of risks. Which failure is actually likely here — flood, quake, Zonda, water shortfall, the operator leaving — what the plan does when it happens, and who decides.

## 13. Declared trade-off

> One objective this scheme deliberately did not optimise, why, what follows from it, and who bears the cost. The same four answers go in manifest.json → tradeoff.

## 14. Sources, assumptions and AI disclosure

> Where the numbers came from (sources.json, assumptions.json). Separate organiser data gaps from unfinished entrant work: disclose scenarios, next verification and responsible role instead of inventing facts or excusing missing mandatory design. Which agent and model did what, and what any human did (manifest.json → agent, autonomy). Which images were generated and how (image_provenance.json).

> Reading outline: site judgement → overall strategy → programme/capacity → movement/infrastructure → phase-one urban design → three nodes/use scenarios → implementation → indicators/trade-offs. Retain the machine-linked fourteen headings, using cross-references and freely added subheadings/figures for a continuous argument. There is no fixed page count.


## Final public submission language

Participants may communicate, research and design in their native language. Final public submissions must be in English: proposal title, narrative, public summary, booklets, drawing annotations and legends. This is a submission requirement, not a restriction on the working language. Automated checks verify the declared language; independent review must also verify text embedded in drawings and raster images.


### Independent design extents and dispersed nodes

The overall plan covers the entire issued site. Distinguish (1) whole-site planning, (2) actual first-phase construction and associated facilities, (3) the urban-design enlargement, (4) each selected node and (5) rendering camera frames. These are not interchangeable boundaries. The enlargement may contain some or none of the three selected nodes. Nodes need not adjoin, share one district, fall within master_area.geojson, or all be built in the first phase. State each node’s location, phase, users and role in the whole-site plan. First-phase completeness means independently operable living and production systems, with evidenced transport, power, water, communications and other relevant connections; it does not mandate a single contiguous footprint. Keep local land-use/FAR/GFA statistics separate from off-area facilities and their indicators. Do not force a compute campus beside housing or a heat user just to group nodes; justify buffers, cooling and any actual heat network. Camera crops illustrate a design; they do not define its scope.

C01 includes the **main entrance and arrival sequence**. All schemes must locate and explain main access, regional connections and people/freight separation in the overall plan even when C01 is not selected; full entrance-node detailing is required only if C01 is selected. The ten topics are optional deepening choices within three groups, not a licence to omit essential city systems from the overall plan. A01/B03/C02 is one valid selection, not a mandatory selection or adjacency model. Use a whole-site locator plus separate, consistently labelled detail insets for dispersed nodes; never crop an outlying node out or draw a fictitious direct link.

### A0 construction phasing map and programme

The A0 board must show a legible, labelled Phase 1/2/3 zoning map and a matching programme table. Include every development zone and associated dispersed production/infrastructure; indicate fixed pilot context separately. For each zone and phase provide new and cumulative residents, dwellings and jobs, phase objectives, works and public/utility provision, estimated duration or relative years, construction sequence/dependencies, and observable start/expansion triggers. Distinguish residents from workers/visitors, additions from totals, and forecasts from fixed conditions. Capacity ranges are allowed with assumptions. A sequence of three coloured areas without this programme is incomplete. Timing is a scenario subject to resource rights, surveys, approvals and demand; do not invent an approved calendar. Totals must reconcile by phase and with metrics.json (including phase-one residents). Areas, phases and district IDs must match geometry/phasing.geojson; separate facilities may share a phase without being adjacent.

Provide `phasing_programme.json` using `templates/phasing_programme.json`; reference the map and A0 board. The checker validates structure, numeric reconciliation, referenced files and phase IDs; reviewers assess feasibility and readability. Automatic checks do not approve the construction programme.


### Complete city scope — 2026-10-27 clarification

Design the complete city layout across all proposed construction phases, not only Phase 1. Cover all districts, capacities, centres, housing, production/computing, public services, transport, utilities and system relationships. Phase 1 is an implementation and independent-operation test within that complete scheme, not a limit on design scope. Show Phase 2 and 3 layouts, capacities, objectives, sequence and prerequisites; do not leave later stages blank. Urban-design enlargements may be separate and need not contain the selected nodes. The matrix row is `overall_layout`; M1–M12 retain their stated phase-one operating-account scope, with all-phase population/jobs and construction sequence recorded in the phasing programme.
