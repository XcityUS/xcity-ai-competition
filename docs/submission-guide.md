# Submission guide

The complete, formal description of a submission package: what goes where, what each file must contain, the commands, and what the twelve gates check. `AGENTS.md` is the short version of this document.

---

## 1. Setup

```bash
git clone https://github.com/XcityUS/xcity-ai-competition.git
cd xcity-ai-competition
python -m pip install -r requirements.txt        # Python 3.10+; shapely, pyproj, numpy, matplotlib, Pillow, markdown
```

The required local geometry, drawing and checking tools run offline after dependencies and browser support are installed. No paid image service or API key is mandatory; finished-image options and the no-image-tool exception are in `docs/visual-guide.md`.
All final drawing annotations and legends must be in English.

---

## 2. The package

```
submissions/<github-login>/<proposal-slug>/
├── manifest.json            who, which agent, autonomy, nodes, trade-off, design depth
├── proposal.md              the design statement, fourteen numbered sections
├── metrics.json             every figure with unit and evidence tag
├── compliance_matrix.json   agent.1-agent.8 and M1-M12 -> the section that answers each
├── design_depth_matrix.json four levels and selected nodes -> evidence and disclosed gaps (new entries)
├── assumptions.json         every value you assumed, with its basis
├── sources.json             every source you cite
├── image_provenance.json    every image under media/ (can be an empty list)
├── changelog.md             every change after the first push
├── geometry/                GeoJSON, EPSG:4326 lon/lat
│   ├── structure.geojson    scale 1: the five systems across the whole site
│   ├── master_area.geojson  scale 2: the area you drew - exactly one feature
│   ├── land_use.geojson     scale 2: land-use polygons inside the master area
│   ├── buildings.geojson    scale 2-3: footprints with floors
│   ├── movement.geojson     people / machine / shared lines; interface points
│   ├── phasing.geojson      phases 1, 2, 3 with triggers
│   └── nodes.geojson        the three key nodes you chose
├── context/                 optional study-only off-site/context GeoJSON; excluded from on-site metrics
├── figures/                 made by scripts/make_figures.py - do not edit
├── drawings/                a3-booklet.pdf (public), a3-technical-appendix.pdf,
│                            presentation-index.json, a0-board.pdf
├── report/
│   ├── proposal.html        made by scripts/render_proposal_html.py
│   └── copyright_statement.md
├── visual/                  index.html: the offline 3D scene - made by scripts/make_scene.py
├── renders/                 <view>.png and stamp.json - made by scripts/render_views.py
├── media/                   finished images (expected), video, audio, interactive pages
└── self_check.json          made by scripts/self_check_submission.py
```

`<github-login>` is your GitHub login. `<proposal-slug>` is lowercase letters, digits and hyphens, 3–64 characters. One account may submit several schemes, one directory each.

---

## 3. Design workflow and supporting commands

Read and version-check the supplied evidence → analyse site conditions, restrictions and uncertainty → compare consequential spatial choices and explain trade-offs → establish the whole-site structure → resolve complete phase one and the urban-design enlargement → deepen three nodes → recompute indicators → organise the formal presentation → run automatic checks and content self-review → revise and submit. The commands below support these design decisions; they are not a substitute for them. Human checkpoints concern values, preferences, tools/budget and public identity/consent; ordinary spatial judgements remain the entrant agent’s work. Scheduling, external messages and account changes require their own user authorisation.

| Step | Command |
|---|---|
| Create the package | `python scripts/scaffold_submission.py --login <login> --slug <slug> --title "..." --nodes B03 C03 A03` |
| Recompute metrics, check geometry | `python scripts/compute_metrics.py submissions/<login>/<slug>` |
| Render the views (3D scene, massing renders) | `python scripts/render_views.py submissions/<login>/<slug>` |
| Finished images (expected: your own image tool first, otherwise your human's) | `python scripts/ai_render.py submissions/<login>/<slug> prompts` — see `docs/visual-guide.md` |
| Draw everything | `python scripts/make_figures.py submissions/<login>/<slug>` |
| Render the HTML | `python scripts/render_proposal_html.py submissions/<login>/<slug>` |
| Check the gates | `python scripts/self_check_submission.py submissions/<login>/<slug>` |
| All of the above, then mark ready | `python scripts/finalize_submission.py submissions/<login>/<slug>` (add `--redraw` to force a full redraw) |

Run `render_views.py` again whenever the geometry changes, and `make_figures.py` whenever geometry, metrics, assumptions, sources, the manifest, the renders or the registered images change — gate G10 compares the drawings with everything they print. `--skip-a0` is for drafts only.

---

## 4. Geometry

The seven checked geometry files are GeoJSON FeatureCollections in **EPSG:4326 (longitude, latitude)**. Their submitted development/context coverage must lie inside `brief/site-package/boundaries/scope_9_13.geojson` (50 m tolerance). Areas and lengths are computed geodesically on WGS 84 by the scripts; you may analyse and compute alternatives yourself, then declare the values and evidence basis that the current checker recomputes.

| File | Geometry | Required properties | Notes |
|---|---|---|---|
| `structure.geojson` | Polygon / MultiPolygon | `system`: `energy_compute`, `agri_production`, `living`, `industry`, `port`, `reserve` | Scale 1. Cover the whole site at structural resolution (hundreds of metres to kilometres). Optional `name`, `phase`. |
| `master_area.geojson` | one Polygon / MultiPolygon | `name` | Scale 2. Your justified detailed study extent, not the whole-site boundary and not automatically phase-one construction or first works. Explain these extents separately. |
| `land_use.geojson` | Polygon / MultiPolygon | `use`: `residential`, `mixed_use`, `civic`, `compute`, `energy`, `industry`, `logistics`, `agriculture`, `open_space`, `infrastructure`, `reserve` | Inside the master area. `open_space` drives `open_space_pct`. Optional `level_m` (a sunken court `-3`, a raised terrace `1.5`), drawn in the node sections. |
| `buildings.geojson` | Polygon / MultiPolygon | `floors` (≥ 1), `use` | Footprints. GFA = Σ footprint × floors. Optional `height_m` (overrides 3.5 m per floor in the 3D views), `name`, and `form: "canopy"` for a roof on posts (shade structures, arcades): drawn in the views, excluded from footprint and GFA. |
| `movement.geojson` | LineString / MultiLineString | `network`: `people`, `machine`, `shared`; optional `shaded` (true/false), `name` | The two networks and their shared parts. `shaded` lines drive `shaded_pedestrian_pct`. |
| | Point | `kind`: `interface` | **Every at-grade point where people and machines meet (M6):** road crossings, the ends of shared streets, kerbs or loading points shared by people and machines, driverless-shuttle stops on a machine route. Grade-separated crossings do not count. The self-check counts them. |
| `phasing.geojson` | Polygon / MultiPolygon | `phase`: 1, 2 or 3; `name`; `trigger` for phases 2 and 3 | Triggers are observable conditions, not dates. |
| `nodes.geojson` | Polygon | `node_id` (C01–A03), `name`, `why` | Exactly three, matching `manifest.nodes`, one from each group in `brief/site-package/nodes/design_nodes.json` for new submissions. Optional camera hints for the 3D views: `eye_from` / `eye_to` [lon, lat], `aerial_from` [lon, lat], `aerial_height_m`, `render_note`. Optional `section`, `section_b` (two [lon, lat] points each: where the node's sections cut; otherwise one each way through the middle) and `day` (a list of `{"time", "people", "machines"}`: a day of use, drawn on the node's third sheet). |

The two pilot outlines are fixed context, not open to new construction or redesign. Keep them separate: the agrivoltaic fields count as `agri_production` in structure and may be labelled `agriculture` or `energy` in land use; the fixed living quarter counts as `living` in structure and may be labelled `residential`, `mixed_use`, `civic`, `open_space` or `infrastructure`. Do not use agriculture/energy labels to stand for the living outline or infer verified internal agriculture. Land-use labels only identify sourced fixed context; they do not authorise new buildings. Because only the living-quarter outline is published, it may be shown as a fixed outline without inventing interior plots or buildings. Document the source, inclusion/exclusion and area accounting; do not count an outline as measured building stock. The checker rejects submitted buildings in either pilot part, tests land-use labels against each part separately, and reports structure-label conflicts for content review. See `brief/site-package/pilot-area/README.md`. Structure areas are land areas; indicative system percentages are planning weight, not land share.

**Four extents, one proposal.** The whole-site structure covers the fixed competition boundary. `master_area.geojson` is the detailed study extent you justify; `phasing.geojson` identifies phase-one development and later conditional phases; first works are the initial access, resource and service projects needed for independent operation. The urban-design enlargement tests complete blocks or a coherent spatial unit within this argument. Do not silently give all four extents the same area/capacity. Land held in reserve is not automatically urbanised, irrigated or active demand. Explain whether fixed pilot context is included in each account; an outline is not measured building stock. Label every metric with the extent and phase it actually describes.

**External context.** Necessary links to regional roads, off-site water/power or communications may be shown as clearly labelled research/context evidence in the proposal and presentation, with source or assumption, proposed/existing status, uncertainty and required rights/approvals. They do not extend the competition boundary, establish construction rights or belong in checked on-site development totals. Do not insert an out-of-site corridor in the seven checked geometry files merely to show a necessary connection; use optional `context/*.geojson` FeatureCollections with the current context schema. Context features use `status: study_only` and `authority: not_secured`, declare source or assumption and required verification, and are excluded from core on-site geometry/metric computation. Reference them from the proposal/figures where needed; they are optional evidence, not another mandatory design area.

Geometry types must match the table exactly: clipping often leaves a GeometryCollection — keep only its polygon parts. `compute_metrics.py` and `make_figures.py` both stop on a wrong type and say how to fix it.

---

## 5. manifest.json

```json
{
  "schema_version": 1,
  "competition": "xcity-ai-competition",
  "title": "Scheme title",
  "slug": "<proposal-slug>",
  "thesis": "One sentence: what this city is built around. Printed large on the booklet's idea page.",
  "summary": "Two to four sentences, up to 700 characters.",
  "language": "en",
  "author": {"github": "<github-login>", "responsible_party": "Named person or organisation", "organisation": ""},
  "agent": {"name": "Claude Code", "model": "model and version", "runtime": "where it ran"},
  "autonomy": {"class": "human_supervised", "human_role": "what the human did"},
  "nodes": ["B03", "C03", "A03"],
  "nodes_reason": "why these three",
  "tradeoff": {"objective": "...", "why": "...", "consequence": "...", "who_bears": "..."},
  "render_note": "optional: materials and life for the city-wide image prompts",
  "render_rules": "optional: what every image must keep, e.g. no private cars",
  "scene_seed": 1,
  "booklet": {"cover": "media/<view>.jpg", "pages": [{"path": "pages/<file>.png", "after": "idea", "title": "...", "subtitle": "..."}]},
  "design_depth": {
    "tier1_structure": {"evidence": ["geometry/structure.geojson", "figures/fig-01-structure.png"]},
    "tier2_master": {"evidence": ["geometry/master_area.geojson", "geometry/buildings.geojson", "figures/fig-02-master-plan.png"]},
    "tier3_nodes": {
      "B03": {"plan": "figures/node-B03-plan.png", "aerial": "figures/node-B03-aerial.png", "eye_level": "figures/node-B03-eye.png"},
      "C03": {"plan": "figures/node-C03-plan.png", "aerial": "figures/node-C03-aerial.png", "eye_level": "figures/node-C03-eye.png"},
      "A03": {"plan": "figures/node-A03-plan.png", "aerial": "figures/node-A03-aerial.png", "eye_level": "figures/node-A03-eye.png"}
    }
  },
  "package_state": "draft",
  "created": "YYYY-MM-DD",
  "updated": "YYYY-MM-DD"
}
```

**Your booklet.** The required reading order is whole-site plan → shared node locator → three node sections in manifest order → phasing → key indicators. `drawings/a3-booklet.pdf` is the public presentation; controls, detailed checks and disclosure go in the separate `drawings/a3-technical-appendix.pdf`. The generator preserves all standalone checked figures and writes a page index. Read `docs/presentation-guide.md` and `templates/presentation.template.md`; they define the information that must be visible, while layout remains free.

`booklet.cover` selects the cover. `booklet.pages` adds PNG/JPG pages at the documented main or technical anchors. If you replace the default layout, keep a truthful `drawings/presentation-index.json`: document paths and physical page counts, and one main section each named `whole_site`, `node_locator`, `node:<id>` for each selected node, `phasing`, `key_metrics`, with one-based page lists in reading order. See the generated index for the format. A page made with an image model is registered in `image_provenance.json`.

Schema: `schema/manifest.schema.json`. A tier-3 view may point at your own render under `media/` instead of the script's view, provided it is registered in `image_provenance.json`.

**Autonomy classes.** `autonomous` — the agent made every design decision and wrote every file; a human at most gave the starting instruction and opened the PR. `human_supervised` — the agent made the decisions and wrote the files; a human set the task, reviewed or asked for changes, without writing design content. `human_directed` — a human made or dictated design decisions or edited the content. Entries are ranked within their class.

**Copyright statement.** Name the responsible party in `report/copyright_statement.md` (the scaffold leaves `(fill in)`; gate G1 checks it).

---

## 6. metrics.json

```json
{"metrics": [
  {"key": "master_area_km2", "value": 9.84, "unit": "km2", "evidence": "computed", "computed_from": "geometry/master_area.geojson"},
  {"key": "structure_km2", "value": {"agri_production": 812.4, "energy_compute": 96.1}, "unit": "km2", "evidence": "computed", "computed_from": "geometry/structure.geojson"},
  {"key": "peak_it_load_mw", "value": 120, "unit": "MW", "evidence": "assumed", "assumption": "A-03"},
  {"key": "wue_l_per_kwh", "value": 0.2, "unit": "L/kWh", "evidence": "sourced", "source": "S-04"}
]}
```

- **evidence** is one of `computed`, `sourced`, `assumed`, `indicative`, `declared` (`brief/requirements.json`).
- **Scope:** unless a requirement says otherwise, M1–M12 describe phase one at full build-out and occupancy; add long-term figures under keys of your own.
- **Computed-account scope:** for matrix v2, footprint/GFA include only building portions clipped to `master_area`, with that polygon as the coverage/FAR denominator; outside-master GFA is reported separately. Neither quantity automatically isolates phase one. Only the two organiser-listed historical directories may retain the v1 whole-package-building numerator for reproducibility. New directories must use v2 and cannot select historical calculations by self-declaring v1. If construction phases differ, provide separately labelled phase-one accounts and their geometry/evidence; do not relabel a study-area total as actual phase-one built capacity.
- `computed` → `computed_from` names the geometry file; the self-check recomputes the value (2% tolerance; counts exact).
- `sourced` → `source` is an id in your `sources.json`, or one of the site package ids (`SRC-KML`, `SRC-DEM`, `SRC-OSM`, `SRC-PILOT`, `SRC-XCITY-INDICATIVE`).
- `assumed` → `assumption` is an id in your `assumptions.json`.
- `indicative` → from the organiser's indicative material; name it in `source`.
- `declared` → a figure the scheme chooses (IT load, jobs programme, dwellings, the machine rule); `note` says how the scheme arrives at it, and any external rate behind it goes in `assumptions.json`.
- **Required keys:** `master_area_km2`, `site_coverage_pct`, `far`, `open_space_pct`, `human_machine_interfaces`, `structure_km2` (all computed), and `hourly_cfe_match_pct`, `peak_it_load_mw`, `annual_water_demand_m3` with its five parts (`water_domestic_m3`, `water_compute_m3`, `water_agriculture_m3`, `water_landscape_m3`, `water_industry_m3` — they must add up), `wue_l_per_kwh`, `machine_traffic_rule` (`separated` / `mixed` / `time_shared` / `combined`), `jobs_phase1`, `residents_phase1`, `dwellings_phase1`.
- Scored, recommended: `gfa_m2`, `pue`, `waste_heat_reuse_pct`, `water_reuse_pct`, `shaded_pedestrian_pct`.

To get the computed values, run `python scripts/compute_metrics.py submissions/<login>/<slug>`.

---

## 7. compliance_matrix.json

One item for each of `agent.1`–`agent.8` (`brief/agent_taskbook.json`) and `M1`–`M12` (`brief/requirements.json`):

```json
{"items": [{"id": "agent.2", "status": "answered", "section": "## 3.", "note": ""}]}
```

`status` is `answered` or `partial` (with a `note` saying what is missing); the template starts every item at `not_answered`, which fails G6. `section` is the number of a heading that exists in `proposal.md`.

---

## 8. proposal.md

Start from `templates/proposal.template.md`. Keep the fourteen numbered headings (`## 1.` … `## 14.`); add sub-headings freely; delete the guidance lines that start with `>`. Write a complete urban design argument that answers the required questions, not a description of your files. No fixed text length substitutes for evidence or design depth. Embed figures with package-relative paths (`![...](figures/fig-02-master-plan.png)`). Then render `report/proposal.html`.

---

## 9. assumptions.json and sources.json

```json
{"assumptions": [{"id": "A-03", "topic": "Grid connection", "value": "No import from the provincial grid; the city runs islanded", "basis": "Grid capacity is not supplied by the organiser; this is an explicit islanded scenario rather than an inferred fact about available transmission; test the storage and generation it needs, and identify operator verification"}]}
{"sources": [{"id": "S-04", "title": "...", "publisher": "...", "url": "https://...", "accessed": "YYYY-MM-DD", "used_for": "..."}]}
```

**An undeclared assumption counts as invention. A missing organiser dataset itself is not penalised.** Distinguish that gap from an entrant omitting required design evidence. Where a required number depends on unavailable data, state a supported scenario/range or explicitly disclosed limitation and next verification; do not claim a verified entitlement/capacity. A disclosure does not automatically establish design adequacy or excuse other mandatory files.

---

## 10. Images, video, interactive pages

See `docs/visual-guide.md`. In short: `render_views.py` draws the required node views for free; everything under `media/` is registered in `image_provenance.json`, with the render it was made from as `control_image`; any `.html` anywhere in the package must load nothing from the network (gate G5).

---

## 11. The twelve gates

| Gate | Checks |
|---|---|
| G1 Package | All required files exist; JSON parses; manifest fields filled; geometry types and properties valid; 14 machine-linked sections, no template text left; HTML rendered from the current proposal.md; no secrets; no file over 25 MB |
| G2 Path | `submissions/<login>/<slug>/`; manifest `author.github` and `slug` match; in a PR, nothing outside this directory changed |
| G3 Sample data | Nothing copied from the example; indicative material tagged `indicative` |
| G4 Reconcile | Computed metrics match the geometry within 2%; water parts add up; land use inside the master area |
| G5 Offline | No `.html` / `.svg` / `.js` / `.css` loads anything from the network |
| G6 Taskbook | agent.1–8 and M1–M12 answered and pointed at real headings |
| G7 Evidence | Every metric has a value, unit and evidence tag whose reference exists; every required key present |
| G8 Disclosure | Agent name, model, runtime; autonomy class; human role unless autonomous; responsible party named |
| G9 Boundaries | Checked geometry inside the site; no new buildings in either fixed pilot part; compatible fixed-context labels checked separately; three valid nodes matching the manifest and covering all three groups for new submissions; possible channel conflicts flagged. Actual channel restrictions and design responses require separate content review |
| G10 Figures | Required standalone figures, main booklet, technical appendix/page index where applicable, and A0 board exist, were drawn from the current inputs and not edited afterwards; the 3D scene and renders match the current geometry; every media file registered and its control image current |
| G11 Trade-off | `manifest.tradeoff` complete; section 13 present |
| G12 Depth | Manifest evidence paths and node views exist; applicable matrix paths/metric keys/headings/gap plans are consistent; applicable PDF/index page references are valid. This is reference/packaging verification, not design adequacy |

---

## 12. Pull request

Before public submission, open the main booklet, appendix and HTML, follow the design-depth review questions, check the new/old source versions and resolve discrepancies. Passing gates is necessary for the technical PR workflow; it is not a finding that the city is complete, readable, feasible or approved.

1. Fork the repository, create a branch, add only your directory.
2. Run `python scripts/finalize_submission.py submissions/<login>/<slug>` until it prints PASS.
3. Commit everything in the directory, including `self_check.json`, and open a pull request. Fill in the template.
4. CI re-runs the path check and the twelve gates. A PR that changes anything outside your directory fails.
5. After merge, the review team may add `FEEDBACK.md` by a separate pull request. **Merge is not publication**: a scheme enters the gallery when the review team records the sha256 of the reviewed version in `gallery/gallery-publication.json`.
6. You may keep improving the scheme until the deadline; log each change in `changelog.md`. **The version in the repository at the deadline is the one reviewed** (its package sha256); after the deadline, changes are not merged until results are announced.


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

Automatic compliance (files, numbers and evidence paths) and design content review are separate. PASS 12/12 means the encoded automatic checks passed. It does not mean adequate master planning, design approval, statutory approval or an award. `ready_for_review` means ready to be reviewed. G12 checks applicable evidence references and presentation packaging/page ranges, not whether the evidence convincingly answers these questions.

## Flood data: screening versus verified restrictions

- **Seasonal channels:** `water/channels_dem.geojson` contains DEM-derived channel lines, not surveyed banks. Permanent construction on an actual dry channel is prohibited. The checker uses indicative line buffers to flag possible conflicts for review; those buffers are not statutory setbacks. Smaller washes are not comprehensively mapped.
- **Flood-sensitive screening:** `water/flood_sensitive_dem.geojson` is a terrain screening model (within 1.5 km of a mapped channel and HAND less than 3 m, using a 60 m DEM), approximately 503 km². It is not a surveyed design-flood extent, a verified hazard zoning instrument, or a blanket permanent no-build area. “Outside the screening band” does not establish flood safety.
- **Verified restrictions:** no surveyed design-flood boundary, design discharge/return period or verified flood setback is supplied. Do not invent one. State assumptions and explain proposed avoidance, conveyance and protection; identify the hydraulic and field verification needed before implementation. Buildings in the screening layer are reported for content review, not failed merely for being in that layer.

## Design workflow, depth and review (26 October 2026)

Read `brief/design-depth.json` and `docs/design-depth-guide.md`: four connected levels (whole-site structure, complete phase one, urban-design enlargement, three detailed nodes). New entries link drawings, geometry, metric keys and explanation headings in `design_depth_matrix.json`, with explicit gaps and next verification. `templates/design_depth_matrix.json` is the editable starting point. G12 validates reference consistency only. Generated results separate automatic compliance, content review (`not_assessed`) and further work. The exact two legacy packages in the policy retain existing requirements until matrix opt-in. No fixed page count, minimum development area or additional render quota is introduced. Formal design diagrams and decisive plans/sections belong in the main booklet; raw controls, repetitive comparisons and logs belong in the technical appendix. Annotated teaching examples: `docs/reference-examples.md`.

## Compatibility and revision of existing schemes

The exact organiser-listed legacy paths are defined in the presentation and design-depth policies, not by a self-declared date. Their exceptions are separate: node selection has no legacy exception; producing a presentation index opts into current packaging; adding `design_depth_matrix.json` opts into matrix checks. V1 matrix reading and historical metric calculations are compatible only for these two listed directories, with a migration notice; all new directories require v2. A new directory cannot obtain an exception by writing schema_version 1. Do not assume one opt-in silently enables all the others. Never rewrite another entrant’s package to manufacture a pass.

When revising an existing scheme, pull current sources, read the source/boundary change records, compare the version actually used and identify affected geometry, metrics, drawings and conclusions. Recompute/redraw the affected outputs, update assumptions/source references and `changelog.md`, then run the current checker and visually inspect both PDFs/HTML. Preserve the prior review/version record; new checks do not retroactively certify or rewrite an old review. The retained legacy exceptions do not make changed source geometry, stale drawings or undisclosed assumptions current.


## Final public submission language

Participants may communicate, research and design in their native language. Final public submissions must be in English: proposal title, narrative, public summary, booklets, drawing annotations and legends. This is a submission requirement, not a restriction on the working language. Automated checks verify the declared language; independent review must also verify text embedded in drawings and raster images.


The public gallery preserves each submission in English in every website interface language. The organiser will prepare clearly labelled Chinese review translations for the review stage, retaining the English originals as the reference. Entrants need not submit a separate Chinese version.


### Independent design extents and dispersed nodes

The overall plan covers the entire issued site. Distinguish (1) whole-site planning, (2) actual first-phase construction and associated facilities, (3) the urban-design enlargement, (4) each selected node and (5) rendering camera frames. These are not interchangeable boundaries. The enlargement may contain some or none of the three selected nodes. Nodes need not adjoin, share one district, fall within master_area.geojson, or all be built in the first phase. State each node’s location, phase, users and role in the whole-site plan. First-phase completeness means independently operable living and production systems, with evidenced transport, power, water, communications and other relevant connections; it does not mandate a single contiguous footprint. Keep local land-use/FAR/GFA statistics separate from off-area facilities and their indicators. Do not force a compute campus beside housing or a heat user just to group nodes; justify buffers, cooling and any actual heat network. Camera crops illustrate a design; they do not define its scope.

C01 includes the **main entrance and arrival sequence**. All schemes must locate and explain main access, regional connections and people/freight separation in the overall plan even when C01 is not selected; full entrance-node detailing is required only if C01 is selected. The ten topics are optional deepening choices within three groups, not a licence to omit essential city systems from the overall plan. A01/B03/C02 is one valid selection, not a mandatory selection or adjacency model. Use a whole-site locator plus separate, consistently labelled detail insets for dispersed nodes; never crop an outlying node out or draw a fictitious direct link.

### A0 construction phasing map and programme

The A0 board must show a legible, labelled Phase 1/2/3 zoning map and a matching programme table. Include every development zone and associated dispersed production/infrastructure; indicate fixed pilot context separately. For each zone and phase provide new and cumulative residents, dwellings and jobs, phase objectives, works and public/utility provision, estimated duration or relative years, construction sequence/dependencies, and observable start/expansion triggers. Distinguish residents from workers/visitors, additions from totals, and forecasts from fixed conditions. Capacity ranges are allowed with assumptions. A sequence of three coloured areas without this programme is incomplete. Timing is a scenario subject to resource rights, surveys, approvals and demand; do not invent an approved calendar. Totals must reconcile by phase and with metrics.json (including phase-one residents). Areas, phases and district IDs must match geometry/phasing.geojson; separate facilities may share a phase without being adjacent.

Provide `phasing_programme.json` using `templates/phasing_programme.json`; reference the map and A0 board. The checker validates structure, numeric reconciliation, referenced files and phase IDs; reviewers assess feasibility and readability. Automatic checks do not approve the construction programme.


### Complete city scope — 2026-10-27 clarification

Design the complete city layout across all proposed construction phases, not only Phase 1. Cover all districts, capacities, centres, housing, production/computing, public services, transport, utilities and system relationships. Phase 1 is an implementation and independent-operation test within that complete scheme, not a limit on design scope. Show Phase 2 and 3 layouts, capacities, objectives, sequence and prerequisites; do not leave later stages blank. Urban-design enlargements may be separate and need not contain the selected nodes. The matrix row is `overall_layout`; M1–M12 retain their stated phase-one operating-account scope, with all-phase population/jobs and construction sequence recorded in the phasing programme.
