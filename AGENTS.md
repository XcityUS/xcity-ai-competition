# AGENTS.md — entering the XCITY Open Agent Call

You are an agent asked to enter this competition. This file is your procedure. Follow it in order.
The full specification is `docs/submission-guide.md`; where this file is brief, that one decides.

**The task:** design a city on 1,656 km² of real land in San Juan, Argentina, and submit it as a package under `submissions/<github-login>/<proposal-slug>/` by GitHub pull request. Everything you need is in this repository and runs offline.

---

## 0. Ground rules

- **Change only your own directory.** `submissions/<github-login>/<proposal-slug>/`. Touching any other file fails the review.
- **Never invent.** Every number has an evidence tag: `computed` (from your geometry), `sourced` (a cited source), `assumed` (declared in `assumptions.json`), `indicative` (the organiser's indicative zoning) or `declared` (a figure your scheme chooses, with a note saying how). An undeclared assumption counts as invention. A missing organiser dataset itself is not penalised: identify it, declare the scenario/basis and next verification. This does not excuse omitted required design, false source claims or unexplained numbers.
- **Never claim approval.** No official endorsement, permit or statutory conclusion.
- **Disclose truthfully** which agent and model did the work and what any human did.
- **The repository is public.** Put nothing in the package you would not publish.
- **Do not copy the example** (`submissions/EXAMPLE-agent/`). It shows the format; it is not a recommended scheme, and identical files fail gate G3.
- **Answer all three scales.** The fixed whole competition site (1,656 km² nominal), your justified master design area with complete phase-one operation and urban-design enlargement, and three key nodes. The study boundary is fixed; it is not the area you are free to shrink. The competition is a city, not one facility.
- **Make it yours.** The scripts give every entry a floor, not a ceiling. Your thesis, your three nodes, your own booklet pages and cover, the sources you find beyond this repository and the rounds of revision with your human are what make the entry different. A booklet of nothing but the default pages reads as a default scheme.
- **Show it to people, not only to the gates.** If your runtime can generate or edit images, use it: finished images of the city and of every key node, made over your massing renders, and a cover of your own. The massing renders prove that each view comes from your geometry; they are control images, not the presentation. Video, sound and interactive pages are welcome too.

## Checkpoints — stop and ask your human

Ask your human only what is theirs to decide: their own ideas, which places they want to see, their money and tools, and their name in public. Design decisions — where the city starts, its form, its trade-offs — are yours; make them and explain them in the statement. Between checkpoints, work on your own. Record each answer in `manifest.json` (`autonomy.human_role`).

1. **Before designing (step 3), two short questions.**
   - **Their ideas.** One open question: *"I've read the brief and will design a city for this site. Is there anything you want it to be, or care about most? If not, just say 'you decide' and I'll explain my thinking at the end."* Whatever they say becomes a starting point; "you decide" means you design on your own.
   - **Three places to see.** *"The competition asks me to design three places in detail, with images. Which one from each of the three groups would you most like to see?"* List the nodes under the three group names (names only, no codes), recommend one per group with a reason in a few words, and ask the human to choose one per group; accept "your choice". If their three do not fit your idea or the site, say why in one sentence and suggest a swap.
2. **Images (step 7) — ask only if you cannot make them yourself.** If your runtime has its own image tool (for example built-in image generation) and using it costs your human nothing extra, make the finished images yourself; do not stop here. Otherwise stop and ask, offering in this order:
   - an image tool they already use, by hand: ChatGPT, Gemini, Midjourney, a local Stable Diffusion or anything else. You give them, for each view, the control image and a prompt ready to paste, and you register what they bring back;
   - a paid service: XCITY Studio (the entrant's XCITY account includes a KWH balance) once it opens, or an image API under their own key, kept in the environment;
   - massing renders only: the last resort, when they have no image tool at all.
   Never spend money without this answer. If no human is available and you have no image tool of your own, submit the massing renders and say so in `autonomy.human_role`.
3. **Before submitting (step 8).** Show the cover, the three node sheets and the self-check result, and ask for consent to open a public pull request under their GitHub name.

**How to ask.** Your human has not read the brief. Write each question so that it can be answered without it:

- One question at a time. Each option: a short name, then one plain sentence on what living there is like, then where it starts, said as a place (beside the solar fields, on the flat ground by the river bed), not as a parcel number.
- No codes or jargon in the question: no node IDs (B03), no parcel numbers, no gate names, no "master area", no metric keys. Name each node by its `en` name in `brief/site-package/nodes/design_nodes.json` (B03 is "a compute campus and its waste heat", C03 "a seasonal river park"), put in the human's language. The details can follow once the human has chosen.
- Name places the way a visitor would: "the solar fields" (the pilot area), "the flat ground beside the solar fields", "the foot of the mountain" (the Pie de Palo range), "along the dry river beds" (the channels), "the whole site" (both parcels, 1,656 km²).
- Your recommendation first, with its reason in a few words.
- Keep each option under about 40 words. Answer in the human's language.

Not like this (a design choice put to a person who cannot judge it, in codes):

> A "Finite water city" (recommended): city size set by the redeemable water budget, starting on the buildable land next to the pilot area in the south-west parcel; B03 shows how compute and waste heat feed the city back, C03 a seasonal channel park that holds floodwater, A03 a shaded public space...

Like this:

> The competition asks for one place from each of three groups. Which would you most like to see?
> **Living and public space:** future housing (my suggestion: test daily life), art and culture, or public space in heat and wind.
> **Production and infrastructure:** a compute campus and its waste heat (my suggestion: test the energy promise), a drone port, or a logistics hub and international gateway.
> **Urban interfaces and environment:** a seasonal river park (my suggestion: test the dry landscape), entrance and arrival, the edge between solar fields and the city, or a street shared with driverless vehicles.
> Reply with one per group, or "your choice".

If the human writes "co-create" in their first message, ask more — but about life and values, not design: who the city should look after first, a busy street or a quiet courtyard, what a good evening there looks like. Turn the answers into design yourself. A human who answers nothing still gets a complete, valid entry.

**After the first submission, keep going.** The brief, the site data, the Issues and other entrants' schemes change. Check again only within the human’s continuing authorisation; do not create a scheduled task, message others or change account settings merely because your runtime can. Without that authorisation, leave a dated next step for the human. On each return: pull `main`, re-read what changed, look at the merged schemes in `submissions/` and the gallery (https://xcityus.github.io/xcity-ai-competition/gallery.html) (borrow only with credit), revise, log the change in `changelog.md`, run `finalize_submission.py` again and push. Every round your human asked for counts: record it in `autonomy.human_role`. **Stop at the deadline:** the version in the repository then is the one reviewed, and nothing pushed after it is. Credit any idea, text, drawing or data you take from another entry.

## 1. Set up

```bash
python -m pip install -r requirements.txt     # Python 3.10+
```

## 2. Read, in this order

1. `brief/site-conditions.en.md` — the land, the protected pilot area, water, terrain and hazards: the facts every design shares.
2. `brief/public-brief.en.md` — this call: the five systems, the three scales, the ten nodes, review.
3. `brief/design-requirements.en.md` — M1–M12 and the metrics; `brief/requirements.json` is the machine version.
4. `brief/agent_taskbook.json` — the eight tasks and which proposal section answers each.
5. `brief/site-package/README.md` — then load the data you need (boundaries, pilot area, channels, terrain, indicative systems, nodes).
6. `brief/evaluation.json` — the twelve gates, the four criteria and the seven dimensions; `brief/scenarios.json` — situations the panel will raise.
7. `docs/submission-guide.md` — the package format. `docs/visual-guide.md` — drawings and renders.
8. **`docs/presentation-guide.md` and `templates/presentation.template.md` — required public reading order and the separate technical appendix. Plan the presentation before rendering.**

## Design workflow — complete the design, then check its delivery

Read and version-check the supplied evidence → analyse site conditions, restrictions and uncertainty → compare consequential spatial choices and explain trade-offs → establish the whole-site structure → resolve complete phase one and the urban-design enlargement → deepen three nodes → recompute indicators → organise the formal presentation → run automatic checks and content self-review → revise and submit. Iterate when drawings reveal conflicts. Compare choices that affect the actual design; do not manufacture meaningless alternatives. The following commands support this workflow; generating a default booklet and passing gates never establishes design completion.

**Scope discipline.** The whole-site framework uses the fixed boundary; `master_area` is the entrant-defined detailed study extent; phase-one construction is the initial independently operable settlement/facility programme (shown in phasing), not the design-scope limit; first works are its enabling projects. They can overlap but their areas, capacities and evidence must be named separately. Urban-design enlargement tests at least a complete block or spatial unit without imposing a standard housing product or minimum area. Reserve land is not automatically built land, irrigated land or realised demand.

Read `brief/design-depth.json`, `docs/design-depth-guide.md` and the annotated method examples in `docs/reference-examples.md`. Fill `design_depth_matrix.json` as the design develops, with actual evidence and remaining verification.

## 3. Create your package

```bash
python scripts/scaffold_submission.py --login <github-login> --slug <proposal-slug> \
    --title "<title>" --nodes <A..> <B..> <C..>
```

Choose exactly one node from each of the three groups (C01–A03, `brief/site-package/nodes/design_nodes.json`) deliberately — the choice says where you think this city is hard.

## 4. Design — geometry first

Write the seven checked GeoJSON files (EPSG:4326 lon/lat) into `geometry/`, inside `brief/site-package/boundaries/scope_9_13.geojson`. Neither fixed pilot part may receive new buildings or be redesigned; sourced fixed-context labels are allowed and differ by pilot type. No permanent construction on actual dry channels. Optional `context/` resource/access GeoJSON is study-only / not-secured evidence, excluded from core on-site statistics. External links are context studies, not out-of-boundary checked development or acquired construction rights; follow `docs/submission-guide.md` §4.

| File | What |
|---|---|
| `structure.geojson` | Scale 1 — the five systems (`system`) over the whole site |
| `master_area.geojson` | Scale 2 — the justified master design study area; distinguish its boundary from phase-one construction and first works |
| `land_use.geojson` | Land use (`use`) inside the master area |
| `buildings.geojson` | Footprints with `floors` and `use` |
| `movement.geojson` | `people` / `machine` / `shared` lines (`shaded` true/false); a Point with `kind: interface` at **every** at-grade human-machine crossing |
| `phasing.geojson` | Phases 1–3; `trigger` (observable) for 2 and 3 |
| `nodes.geojson` | Your three nodes, `node_id`, `name`, `why`; optional `section`, `section_b` (two lon/lat points each: where the section cuts), `day` (a day of use: a list of `{time, people, machines}`), cameras and `render_note` (step 7) |

**The master area grows out of the site.** Draw its edge from what you read in the terrain: along a channel, at the foot of a slope, against the pilot area, toward the way out. Not a rectangle of convenience. Say in the statement why it is here and why it has this shape.

**Each node is designed, not marked.** Put in its buildings, trees, paths, water and shade, so that the massing renders already show how people use the place. A node with a few boxes on bare ground is not a detailed design.

A land-use polygon may carry `level_m` (a sunken court at `-3`, a raised terrace at `1.5`); sections draw it. Property vocabularies are in `docs/submission-guide.md` §4. Generating the geometry with a script of your own is normal and expected; keep that script out of the package or put it in the package as documentation.

## 5. Numbers

Get the recomputed values (it also reports geometry problems):

```bash
python scripts/compute_metrics.py submissions/<login>/<slug>
```

Fill `metrics.json` (computed values exactly as printed; every other figure with its evidence tag), `assumptions.json`, `sources.json`. Unless a requirement says otherwise, M1–M12 describe **phase one at full build-out and occupancy**.

## 6. Write the statement

Fill `proposal.md` from the template: fourteen machine-linked numbered sections, written as an urban design statement a professional would sign. Answer every task and M1–M12, then point each at its section in `compliance_matrix.json`. Fill `manifest.json`: `thesis` (the one sentence), summary, responsible party, agent, model, runtime, autonomy, nodes and why, the declared trade-off (one objective you did not optimise, why, the consequence, who bears it). Autonomy classes are defined in `brief/rules.en.md` §4. Name the responsible party in `report/copyright_statement.md` too. Set each item in `compliance_matrix.json` to `answered` (or `partial` with a note) once it really is.

## 7. Render, draw and check

Every key node needs at least an aerial view and an eye-level view in which you can see how people use the place. These views are made from your own geometry:

```bash
python -m playwright install chromium                            # once
python scripts/render_views.py submissions/<login>/<slug>        # visual/index.html (3D, offline) + renders/*.png
```

Each node may set `aerial_from`, `eye_from` and `eye_to` (lon/lat) and a `render_note` (materials and life) in `nodes.geojson`. Look at every image in `renders/`. If an eye-level camera faces a wall or empty ground, move it and render again.

The massing renders are your control images: they show that each view comes from your geometry. They are not the presentation. Turn them into finished images, at least the city views and every node's eye-level views, with an image model that takes each render as its control image (**checkpoint 2** says when to ask your human). Then make a cover of your own: a finished image, or a page you design.

```bash
python scripts/ai_render.py submissions/<login>/<slug> prompts                 # one prompt per view
python scripts/ai_render.py submissions/<login>/<slug> run --provider xcity    # or openai, or manual
python scripts/ai_render.py submissions/<login>/<slug> register media/<view>.jpg --view <view> --model "<model>"
```

Every image in `media/` is registered in `image_provenance.json` with its model, its full prompt and its control image (gate G10). Images illustrate the geometry; they are never evidence, and each caption says it is a concept image. The drawings use them automatically, in this order: a registered image, then the massing render, then make_figures' own massing drawing.

The booklet's graphic layout is yours; its **information structure is required**: whole-site plan → shared node locator (whole site to master area to all three nodes and their connections) → three node sections in manifest order → phasing → key indicators. A cover/thesis may precede this sequence. Each node uses the same ID and official topic, a place name, location/access explanation, finished aerial and eye-level views, and necessary design plans/sections. Mark the existing no-image-tool massing fallback visibly; never call a control a finished image. See `templates/presentation.template.md`.

Keep raw controls, repetitive image/control comparisons, full accounts, compliance tables, raw model screenshots, program logs, assumptions and disclosure in **`drawings/a3-technical-appendix.pdf`**. Keep formal design diagrams, plans, decisive sections and massing relationships in the main booklet when they explain spatial decisions. The technical appendix must not hide the actual design. Keep the original checked files on disk. `make_figures.py` produces the main booklet, this appendix and a page index. G12 checks the index/PDF ranges, not visual quality or planning adequacy.

`manifest.booklet.cover` selects a cover. `booklet.pages` adds your own pages; presentation and technical insertion anchors are listed in `docs/presentation-guide.md`. Custom pages preserve the reading order and the separation of controls from presentation. To replace default public section layouts, set `booklet.section_pages` as described in the presentation guide; the generator retains checked figures and updates the page index.

```bash
python scripts/make_figures.py submissions/<login>/<slug>        # checked figures, public A3 booklet, technical appendix, page index and A0 board
python scripts/finalize_submission.py submissions/<login>/<slug> # HTML, ready_for_review, the twelve gates
```

Read every message, fix, run again (`finalize_submission.py --redraw` forces a full redraw). **Open the pull request only when it prints PASS 12/12.** Open both PDFs. Verify the main reading order, shared locator, node titles/locations and image quality, and compare the finished views with their controls in the appendix. A wrong view may be a geometry, camera or image-editing problem; diagnose it. Passing the gates does not establish that the presentation or city is adequate.

## 8. Submit

This is **checkpoint 3**: get the human's consent first. Then fork, branch, commit only your directory (including `self_check.json`), open a pull request and fill in the template. CI re-runs the path check and the gates.

---

Questions: open an Issue. Status of the call and dates: `README.md` and `CHANGELOG.md`.


### Node selection: one per group (26 October 2026)

New submissions choose exactly one node from each group, three nodes total:

| Group | Available nodes |
|---|---|
| Living and public space | A01 Future housing; A02 Art and culture; A03 Public space in heat and Zonda wind |
| Production and infrastructure | B01 Drone port; B02 Logistics and international gateway; B03 Compute campus and waste heat |
| Urban interfaces and environment | C01 Entrance and arrival; C02 Agrivoltaic/city edge; C03 Seasonal river park; C04 Street shared with driverless vehicles |

A combined design is welcome, but each selected node needs its own distinct ID and the required design evidence. Group coverage is checked by gate G9; group membership does not change the detailed-design or render requirements. All submissions must use exactly one node from each group A, B and C. There is no earlier node-number alias or selection exemption.

## Whole-site structure: minimum design questions

The whole-site study must answer all six items: (1) settlements and a hierarchy of centres, including the role of land not urbanised; (2) the location, approximate scale and relationship of all five systems; (3) primary external and internal transport and human/machine connections; (4) resource infrastructure for power, compute, water, reuse, waste and communications, with declared assumptions where data is missing; (5) connections to both fixed pilot parts and the two parcels; (6) the relationship between phases, access, services and observable expansion triggers. Use structure, movement and phasing geometry together with the statement; explain capacities and connections. A site-covering coloured zoning diagram alone is insufficient. This is a content-review criterion, not an automatic minimum construction area, mandatory urban footprint, prescribed settlement pattern or requirement to develop all the land. Protection and reserves may dominate if the whole-site relationships are explained.

Automatic compliance (files, numbers and evidence paths) and design content review are separate. PASS 12/12 means the encoded automatic checks passed. It does not mean adequate master planning, design approval, statutory approval or an award. `ready_for_review` means ready to be reviewed. G12 checks evidence references and packaging, not whether the evidence convincingly answers these questions. Read automatic compliance, independent content review and further-work disclosures separately.


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
