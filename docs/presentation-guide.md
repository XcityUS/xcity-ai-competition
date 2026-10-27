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

`manifest.booklet.a0_page` may point to an entrant-authored PNG/JPG board inside the package. The generator uses it for `drawings/a0-board.pdf`, while retaining all checked source figures and the separate technical appendix. Include the whole-site/first-district relationship, the selected node IDs, finished concept views and the diagrams needed to explain the design. Raw massing controls belong in the technical appendix. The board image is included in the figure-input hash; editing it requires regeneration. Paths outside the package are rejected. Omitting this option retains the default A0 layout.
