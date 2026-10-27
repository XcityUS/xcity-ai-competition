# AI Agent 成果展示结构 / Presentation structure

This is a required **information structure and reading order**, not a required graphic style. It applies to the Open Agent Call. It does not change the institution-track Design Brief, the design scope, the three node groups or the technical geometry requirements.

Agent-readable policy: `brief/presentation-requirements.json`. Copy/edit the content checklist in `templates/presentation.template.md` when planning your pages.

## Main booklet: the work people should read first

| Reading order | Required information |
|---|---|
| 1 · Whole-site plan / 全场地总图 | Full boundary, both pilots, settlements and centres, five systems with scale/relationships, principal traffic, resource links, protection/reserves and phase relationships. A colour-zoning layer alone is insufficient. |
| 2 · Node locator / 节点定位 | Locate the master area on the whole site; enlarge it to show the three node boundaries, matching IDs/names and their connections through the actual movement/system networks. Use insets if they are far apart; label their relationship to the master area rather than implying that the master area is the whole site or that a node is inside it when it is not. |
| 3 · Three nodes / 三个节点 | One section for each manifest.nodes entry: stable title and ID, city location/access, what happens here, finished aerial and eye-level concept views, and the plan/section needed to explain the design. Label any permitted massing-only fallback honestly. |
| 4 · Phasing / 分期 | First works, later phases, independently operating services, dependencies and observable triggers; same boundaries and quantities as the geometry. |
| 5 · Key indicators / 关键指标 | Main people/jobs/housing, land/density, water, energy and compute figures, with units, area scope, phase and evidence tags. Distinguish fixed whole-site framework, chosen master study area, actual phase-one construction and first works; reserves are not realised demand. |

A cover and short thesis may precede the sequence. The indexed order is an organising spine, not a complete page quota: site analysis, suitability, capacity scenarios, complete phase-one layout and urban-design enlargement must appear at the relevant anchors before the node claims that depend on them. Supporting presentation pages may be added within it. Page counts, typography, composition and visual identity remain free. Use titles, readable labels and appropriate orientation/scale/legend/source-status notation; do not add irrelevant graphic furniture. Do not scatter the nodes among calculation pages or use three unrelated perspectives without a shared locator. Finished images remain illustrations of the submitted geometry, not evidence of built conditions or measurements.

## Full argument within the existing fourteen headings

Use the existing statement headings and insertion anchors; this mapping adds no competing chapter numbering or page count.

| Main reading theme / 主线 | Existing proposal headings |
|---|---|
| City proposition and core question / 城市主张 | 1 |
| Site evidence and suitability / 场地解读与适建判断 | 2, 12, 14 |
| Whole-site structure and system relations / 全场地结构 | 3–7, 9 |
| Programme, land and capacity / 功能土地与容量 | 6, 7, 11 |
| Movement, resources and infrastructure / 交通资源基础设施 | 3–5, 9 |
| Independently operating phase one / 首期完整布局 | 6, 7, 9 |
| Blocks, interfaces and public life / 城市设计放大 | 5, 7 |
| Three nodes and experience / 三节点与使用体验 | 10, linked back to 7 and 9 |
| Operation, abnormal scenarios and governance / 运行与异常治理 | 4, 5, 8, 12 |
| Phasing, implementation and indicators / 分期实施与指标 | 9, 11 |
| Trade-offs and verification gaps / 取舍与待核实 | 12–14 |

Use combined drawings and cross-references when they communicate the same decision; do not repeat a diagram solely to fill every heading. Every formal sheet needs a named extent/phase and source/assumption status, plus readable titles/labels and appropriate legend, orientation and scale/dimensions. The content review asks whether those diagrams establish the design, not whether their files exist.

## Separate technical appendix

`drawings/a3-technical-appendix.pdf` contains the compliance index, extended land/resource calculations, raw control-render comparisons, model/debug material, assumptions, sources and image/tool disclosure. Formal design diagrams, necessary sections/dimensions and operational diagrams that explain spatial decisions remain in the main booklet. The original `renders/` controls, `figures/` and current `self_check.json` remain in the package. The main booklet need not repeat every check or every control image. Necessary plans and sections stay in the main presentation where they explain the proposal.

Default `make_figures.py` writes both PDFs and `drawings/presentation-index.json`. The main PDF is still named `a3-booklet.pdf`, so existing gallery/download routes remain usable. `figures/fig-08-node-location.png` is the new shared locator. A custom page design must preserve the named outputs and a truthful index with the mandatory sections in order. Page numbers are one-based physical PDF pages, including the cover.

`manifest.booklet.pages` still supports custom images. Main-document insertion anchors: `cover`, `idea` (before the whole-site plan), `whole_site`, `node_locator`, `views` (after the master-area plan), a selected node ID, `nodes`, `phasing`, `key_metrics`, `end`. Technical anchors: `brief`, `figures`, `day`. Put extra controls/checks at technical anchors rather than mixing them into the public story.

## What the checker can establish

G10 checks that indexed outputs exist, are current and match their recorded hashes. G12 verifies that the PDFs can be read, declared page counts match the PDFs, and required section ranges occur in order without overlap. These checks **do not** establish that a view is polished, a locator is clear, an image agrees with the geometry, or a city is adequately designed. Those are independent review questions. Keep the existing exception for entrants with no image tool; payment or a particular rendering service is never required.

The two organiser-listed existing packages retain the previous packaging rules. They opt into the new packaging if they regenerate with the current generator (which writes the new index); entrants cannot claim legacy status by backdating a manifest. The package names are in the organiser-maintained presentation policy. Existing submissions are not edited by this change. Matrix opt-in is separate (adding its matrix); node selection always requires one node from each of groups A, B and C, with no node-selection exception. When revising, read source/boundary change records, identify affected conclusions and regenerate current evidence rather than reusing an old PASS.

## Freely designed replacement pages

To replace a default public section instead of merely adding pages, use `manifest.booklet.section_pages`, for example `{"node_locator": [{"path": "pages/my-locator.png", "title": "Where the three places belong"}]}`. Keys are `whole_site`, `node_locator`, `node:<selected ID>`, `phasing` and `key_metrics`. Each list can contain several PNG/JPG pages. The generator places them in the required reading sequence and records their page ranges automatically. All required information still applies; custom images cannot replace checked source geometry or controls. Image-model pages need provenance registration. Changing a custom page invalidates the drawing-input hash and requires a redraw. The automatic index does not prove the page actually contains the required content.

## Design evidence belongs in the main story

The formal booklet is a complete design argument, not a fixed six-page abstract: site judgement → overall strategy → programme/capacity → movement/infrastructure → phase-one urban design → three nodes and use scenarios → implementation → indicators/trade-offs. Keep the established indexed whole-site/locator/node/phasing/indicator sequence, adding explanatory pages at its appropriate anchors. Page count follows the design.

Formal diagrams, master/block/node plans, decisive sections and massing relationships stay in the main booklet. Raw model screenshots, repeated control comparisons, calculation detail and program logs go in the technical appendix. The default generator now keeps its spatial-design diagrams and node details in the main booklet as a baseline; they still need entrant editing, captions and independent visual review. Use `booklet.pages` / `booklet.section_pages` for the full argument.

See `brief/design-depth.json`, `docs/design-depth-guide.md` and `docs/reference-examples.md`. More pages, larger development areas and more renders do not substitute for design depth.

## Authored A0 presentation board

`manifest.booklet.a0_page` may point to an entrant-authored PNG/JPG board inside the package. The generator uses it for `drawings/a0-board.pdf`, while retaining all checked source figures and the separate technical appendix. Include the whole-site/complete-city relationship and construction phasing map, the selected node IDs, finished concept views and the diagrams needed to explain the design. Raw massing controls belong in the technical appendix. The board image is included in the figure-input hash; editing it requires regeneration. Paths outside the package are rejected. Omitting this option retains the default A0 layout.

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

## Visual-first A0 / A0以空间设计为主

Use the A0 board to communicate the city: a dominant overall plan/axon, coordinated functional/road/landscape diagrams, legible district and centre relationships, necessary node evidence and a concise construction sequence. Keep only numbers that materially explain scale, capacity, a resource constraint or phase choice, clearly scoped and tagged. Full district-by-phase population/dwelling/job accounts, detailed metric grids, all source/evidence columns and logs remain in the technical appendix and machine files. The phase map is still required; a dense spreadsheet or dozens of numerical badges is not its replacement. There is no additional fixed number quota and fewer numbers do not excuse missing calculations. The default A0 now summarises the three stages visually rather than reproducing every district row.

A0是讲清空间方案的展板：以全域总图/轴测为主，配功能、路网、景观、中心关系和必要节点图，并说明建设顺序。只保留直接支持尺度、容量、资源约束或分期判断的关键数字，标清范围与依据。完整分区分期的人口、住房、岗位、指标及来源表和日志放技术附件与机器文件；A0仍须有分期图，不用密集Excel式表格，也不改成满板数字卡片。不新增固定数字数量限制，更不取消计算义务。
