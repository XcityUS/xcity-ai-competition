# Visual guide

> A brief that demands drawings must supply a way to make them.

The competition page asks for a city people can see, not a stack of data layers. Every key node needs **at least one aerial view and one eye-level view in which you can see how people use the place**, plus a plan or section. Sequences, day and night, video and interactive 3D are encouraged. Dense unedited text, unexplained debug diagrams or raw GIS layers alone do not establish the final design. Formal design analysis diagrams, plans, sections, service/flow diagrams and massing relationships belong in the main booklet when they explain decisions.

## 1. The image pipeline

Design the four connected levels first (`AGENTS.md`, `brief/design-depth.json`); then use this pipeline to communicate them. Caption the extent, phase, source/assumption status and the actual spatial question each drawing answers. Provide a title, readable labels and, where useful, legend, orientation and scale/dimensions. Add required access/resource context with its separate evidence status; it must not masquerade as on-site authorised development.

| Step | Tool | Output | Needs |
|---|---|---|---|
| 1. 3D scene | `scripts/make_scene.py` (run by step 2) | `visual/index.html`: an offline three.js scene of your geometry on the real terrain, with terrain, submitted geometry and sun; optional illustrative additions require explicit opt-in | Python only |
| 2. Massing renders | `scripts/render_views.py` | `renders/<view>.png` for the whole master area, the city, and each node (aerial, eye level by day, and evening or night); `renders/stamp.json` | Playwright + Chromium (software WebGL, no GPU) |
| 3. Finished images (expected) | `scripts/ai_render.py` | `media/<view>.jpg`, registered in `image_provenance.json` with model, full prompt and control image | The agent's own image tool first; otherwise any tool the human uses by hand (ChatGPT, Gemini, Midjourney, Stable Diffusion), XCITY Studio, or an API key of their own |
| 4. Drawings | `scripts/make_figures.py` | Required figures and shared locator, node sheets, main A3 booklet, technical appendix/page index and A0 board | Python only |

The drawings pick up the best image of each view automatically: a registered finished image, otherwise the massing render, otherwise make_figures' own massing drawing.

**Make finished images whenever you can.** The massing renders provide traceable controls from the submitted geometry; the finished images show the place to people, and the cover, the gallery card and the node sheets use them. If the agent can generate images itself, it does so without stopping to ask. An entrant with no image tool at all may use the established massing-only exception and disclose it. That exception does not establish that every other gate passed or excuse unclear spatial evidence; the tool’s absence itself is not penalised.

## Overall view and architectural views

The overall spatial view must communicate XCITY's photovoltaic-agriculture-led territorial structure: solar production integrated with forage/jojoba cultivation, modular industrial-hall compute campuses, energy/service infrastructure, access/logistics and compact living/civic areas in their actual relationships. A housing-only aerial cannot fulfil this role. Distinguish allocated territory, proposed installed works, commissioned works and future reserve; do not turn every production-zone polygon into installed panels. Derive the control from coordinated geometry before rendering; do not add token panels around a housing composition or move facilities to fit one camera. No universal land percentage or image-area quota is prescribed.

Housing images should explain architecture and daily use at an appropriate local scale, such as a low drone or eye-level view of buildings, courtyards, streets, shade and public ground. A separate large residential-district aerial is not a default deliverable. Required planning enlargements remain useful drawings, not an instruction to generate another residential hero image.

## 2. Cameras

`render_views.py` places the cameras itself: the master aerial frames everything you built, the local city views frame architectural/public-space relationships and do not replace the photovoltaic-agriculture-led overall view, and the node aerials frame the buildings in each node. To control them, add to a node in `nodes.geojson`:

| Property | |
|---|---|
| `aerial_from` | `[lon, lat]`: the aerial camera looks from this direction |
| `eye_from`, `eye_to` | `[lon, lat]`: an eye-level camera at 1.6 m and the point it looks at. Stand where people are, not inside a building and not on empty ground |
| `render_note` | One or two sentences on materials and life, used in the image prompt |

`manifest.json` may carry `render_note` (the whole city), `render_rules` (rules every image must keep, such as "no private cars") and `scene_seed` (an integer: another arrangement of trees, people and vehicles; the same package always gives the same scene on any machine). **Look at every render.** If a camera faces a wall or bare ground, move it and render again.

## 3. Finished images

```bash
python scripts/ai_render.py <package> prompts                    # renders/prompts.json: one prompt per view
python scripts/ai_render.py <package> run --provider xcity       # XCITY Studio (billed to your XCITY balance, once it opens)
python scripts/ai_render.py <package> run --provider openai      # your own OPENAI_API_KEY, at OpenAI's prices
python scripts/ai_render.py <package> register media/A03-eye-day.jpg --view A03-eye-day --model "..."   # made by hand
```

**Any image tool works.** If your runtime generates images itself, that comes first: no handoff and no cost to your human. `run` automates two services; for every other tool, give it the control image and the prompt from `renders/prompts.json`, save the result under `media/`, and `register` it. When your human makes the images by hand, hand them each control image with a prompt ready to paste. The panel judges agreement with the geometry, not the tool. Reference packages do not prescribe a provider or workflow.

Each prompt asks the model to keep the control image's camera, footprints, heights, streets and trees, and to change only materials, light and life. An agent must ask its human before spending money (AGENTS.md, checkpoint 2). Keys stay in the environment or in `~/.xcity/`, never in the repository.

## 4. What make_figures.py draws

| File | Content |
|---|---|
| `fig-01-structure.png` | Whole site: five design systems plus reserve with their recomputed areas, pilot area, channels, master area, nodes |
| `fig-02-master-plan.png` | Master area: land use, figure-ground, networks, place names, overall dimensions, nodes |
| `fig-03-land-use-density.png` | Buildings by floors; land use areas; coverage, FAR, open space recomputed |
| `fig-04-movement.png` | People, machine and shared networks; every interface numbered |
| `fig-05-open-space-water.png` | Open space, shaded and unshaded walking, channels and flood corridors |
| `fig-06-phasing.png` | Phases 1–3 with areas and triggers |
| `fig-07-metrics.png` | Every declared metric, its evidence tag, and the recomputed value where there is one |
| `node-<id>-plan.png`, `-aerial.png`, `-eye.png` | For each node: the plan, and the best aerial and eye-level image |
| `fig-08-node-location.png` | Whole-site location of the master area and a shared enlarged locator for all three nodes and their network relationships |
| `drawings/a3-booklet.pdf` | Complete public design: cover/thesis; whole site; shared locator/master plan; formal density, movement and water/open-space diagrams; three named/located nodes with necessary plans/sections; phasing; key indicators; custom pages needed for the design argument |
| `drawings/a3-technical-appendix.pdf` | Full accounts, compliance/evidence index, raw geometry controls, repeated image comparisons, extended technical details, sources, assumptions and disclosure; retain decisive formal node sections/operations in the main booklet |
| `drawings/presentation-index.json` | Document page counts and one-based page ranges for the required public sections |
| `drawings/a0-board.pdf` | One A0 board |

Every sheet carries a title, sources, the script version and a hash of its inputs, which include the renders and the registered images. The generator visualises supplied data and some rendering conventions. Check its labels, default cameras/sections and semantic assumptions; a generated sheet is not an independent confirmation of design quality or measured conditions.

**Make the layout yours; preserve the reading order.** The required information is in `docs/presentation-guide.md` and `templates/presentation.template.md`. Controls and checks stay in the technical appendix. `manifest.booklet.cover` picks the cover; `manifest.booklet.pages` adds pages you draw yourself (see `docs/submission-guide.md` §5). In `nodes.geojson`, `section` / `section_b` place the cuts and `day` writes the day of use; a land use with `level_m` is drawn at its level. The example's identity page comes from its own `tools/make_pages.py`.

## 5. Registering media

Every file under `media/` is registered in `image_provenance.json` (template: `templates/image_provenance.example.json`). `ai_render.py` does this for you.

| Field | |
|---|---|
| `path` | `media/...` |
| `node_id`, `view` | e.g. `B03`, `aerial` / `eye_level` / `other` |
| `model` | Tool or model and version |
| `prompt` | The full prompt, not shortened |
| `generated_at` | Date |
| `post_processing` | `none`, `retouch` or `composite` (+ `post_processing_note`) |
| `reference_images` | `none_text_only_prompt`, `own_work` or `third_party`; the last two need `reference_images_note` |
| `control_image` | `renders/<view>.png` the image was made from; gate G10 checks it exists and is current |
| `caption` | Must make clear it is a concept image that explains the geometry, not evidence |

**Rules.** Generated material may not pass itself off as a photograph, a measurement, an official boundary, a resident's opinion or an approval. Video carries a poster, captions and a transcript; audio a transcript; nothing autoplays. A render is judged on agreement with the submitted geometry — heights, positions, orientation — not on how good it looks. A render that contradicts the geometry costs points rather than earning them. **The disclosed tool/model and provenance remain available for review; the choice of tool earns no points.**

## 6. Interactive pages

`visual/index.html` is written for you: open it in any browser to orbit the scene and switch views. Anything else interactive goes under `media/`. Pages must work offline (gate G5): no CDN, no map tiles, no web fonts, no API calls, no iframes. Bundle any library you use into the package.

## 7. Cost

Every required output is free and offline. Finished images need not cost anything either: an agent's built-in image tool, or a free tier used by hand, is enough. Paying earns no points, and an image that disagrees with the geometry costs points. Confirm availability and actual charges before using any hosted image service; never assume an account credit or spend without the human’s authorisation.

## Design evidence belongs in the main story

The formal booklet is a complete design argument, not a fixed six-page abstract: site judgement → overall strategy → programme/capacity → movement/infrastructure → phase-one urban design → three nodes and use scenarios → implementation → indicators/trade-offs. Keep the established indexed whole-site/locator/node/phasing/indicator sequence, adding explanatory pages at its appropriate anchors. Page count follows the design.

Formal diagrams, master/block/node plans, decisive sections and massing relationships stay in the main booklet. Raw model screenshots, repeated control comparisons, calculation detail and program logs go in the technical appendix. The default generator now keeps its spatial-design diagrams and node details in the main booklet as a baseline; they still need entrant editing, captions and independent visual review. Use `booklet.pages` / `booklet.section_pages` for the full argument.

See `brief/design-depth.json`, `docs/design-depth-guide.md` and `docs/reference-examples.md`. More pages, larger development areas and more renders do not substitute for design depth.


## Final public submission language

Participants may communicate, research and design in their native language. Final public submissions must be in English: proposal title, narrative, public summary, booklets, drawing annotations and legends. This is a submission requirement, not a restriction on the working language. Automated checks verify the declared language; independent review must also verify text embedded in drawings and raster images.

### Siting and view validity

Do not organise the city to fit the three selected nodes into one image. Justify adjacency or separation using the relevant terrain, access, utility, noise, risk, operations and public-life conditions; no universal distance or requirement to co-locate is imposed. Identify each image as whole-site diagram, complete-city view, district/detail view or node view. Register its geographic footprint, scale/extent and, for a physical perspective, position, target, height and lens/FOV (or explicitly identify a diagrammatic orthographic/axonometric projection). A matching geometry-derived control is required for each finished perspective; an eye-level scene inferred from an aerial alone is not a verified camera view. Keep geometry checks separate from visual judgement. The picture must not silently add, relocate or resize buildings, invent topography or replace the complete layout. A local neighbourhood aerial cannot serve as evidence for the entire 1,658.82 km² site.


## Evidence-safe scene defaults

`scene_generation.procedural_planting`, `procedural_pv` and `illustrative_entourage` default to `false`. A land-use label, a shaded route or a building name is not a planting plan, installed PV layout or water design. Roof PV requires `roof_pv: true` on its building; a depicted water channel requires `water_channel_design: true` on its movement feature and an explained design basis. Opting into procedural illustrations does not add them to capacity or water accounts. Keep designed planting geometry, species, water allocation and maintenance assumptions explicit in the relevant drawings and proposal. Do not count automatically drawn trees as proof of shade or automatically drawn panels as installed generation.

After geometry, scene policy or renderer code changes, regenerate controls and every dependent finished image. Cache fingerprints include the scene policy and renderer source. Open the actual new images and compare them with the plan: a current fingerprint confirms version linkage, not geometric fidelity or design quality. Record the geographic extent and camera of each perspective; a local aerial is not a whole-city plan.


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

## Visual-first A0 / A0以空间设计为主

Use the A0 board to communicate the city: a dominant overall plan/axon, coordinated functional/road/landscape diagrams, legible district and centre relationships, necessary node evidence and a concise construction sequence. Keep only numbers that materially explain scale, capacity, a resource constraint or phase choice, clearly scoped and tagged. Full district-by-phase population/dwelling/job accounts, detailed metric grids, all source/evidence columns and logs remain in the technical appendix and machine files. The phase map is still required; a dense spreadsheet or dozens of numerical badges is not its replacement. There is no additional fixed number quota and fewer numbers do not excuse missing calculations. The default A0 now summarises the three stages visually rather than reproducing every district row.

A0是讲清空间方案的展板：以全域总图/轴测为主，配功能、路网、景观、中心关系和必要节点图，并说明建设顺序。只保留直接支持尺度、容量、资源约束或分期判断的关键数字，标清范围与依据。完整分区分期的人口、住房、岗位、指标及来源表和日志放技术附件与机器文件；A0仍须有分期图，不用密集Excel式表格，也不改成满板数字卡片。不新增固定数字数量限制，更不取消计算义务。

The default scene now supplies `whole-site-aerial`, framed from the issued site rather than the building cluster, with source boundary and seasonal-channel annotations. `master-aerial` and `city-aerial` are local views. Use the whole-site control for the overall spatial argument, or an equivalent source-based axon. Never erase channels or source terrain in a finished overview. Label annotated lines as source context, not constructed fences, engineered flood limits or permanent water. A local frame lying entirely inside the site need not invent a perimeter: provide a whole-site locator and its actual view footprint. Explain substantial unbuilt ground as terrain, drainage, operations or a resource-gated reserve; neither unexplained empty pads nor indiscriminate solar infill is a design.

For explicit future-field geometry, an entrant may set `manifest.scene_generation.territorial_field_geometry` to an existing GeoJSON inside their package. The scene displays these as planned ground footprints, not installed PV tables; the referenced file participates in the scene fingerprint. This is optional, adds no submission quota and provides no automatic design-quality credit.
