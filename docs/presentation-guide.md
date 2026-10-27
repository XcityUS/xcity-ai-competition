# AI Agent 成果展示结构 / Presentation structure

This is a required **information structure and reading order**, not a required graphic style. It applies to the Open Agent Call. It does not change the institution-track Design Brief, the design scope, the three node groups or the technical geometry requirements.

Agent-readable policy: `brief/presentation-requirements.json`. Copy/edit the content checklist in `templates/presentation.template.md` when planning your pages.

## Main booklet: the work people should read first

| Reading order | Required information |
|---|---|
| 1 · Whole-site plan / 全场地总图 | Full boundary, both pilots, settlements and centres, five systems with scale/relationships, principal traffic, resource links, protection/reserves and phase relationships. A colour-zoning layer alone is insufficient. |
| 2 · Node locator / 节点定位 | Locate the master area on the whole site; enlarge it to show the three node boundaries, matching IDs/names and their connections through the actual movement/system networks. Use insets if they are far apart. |
| 3 · Three nodes / 三个节点 | One section for each manifest.nodes entry: stable title and ID, city location/access, what happens here, finished aerial and eye-level concept views, and the plan/section needed to explain the design. Label any permitted massing-only fallback honestly. |
| 4 · Phasing / 分期 | First works, later phases, independently operating services, dependencies and observable triggers; same boundaries and quantities as the geometry. |
| 5 · Key indicators / 关键指标 | Main people/jobs/housing, land/density, water, energy and compute figures, with units, area scope, phase and evidence tags. |

A cover and short thesis may precede the sequence. Supporting presentation pages may be added within it. Page counts, typography, composition and visual identity remain free. Do not scatter the nodes among calculation pages or use three unrelated perspectives without a shared locator. Finished images remain illustrations of the submitted geometry, not evidence of built conditions or measurements.

## Separate technical appendix

`drawings/a3-technical-appendix.pdf` contains the compliance index, detailed land/resource figures, sections and dimensions, control-render comparisons, operational diagrams, assumptions, sources and image/tool disclosure. The original `renders/` controls, `figures/` and current `self_check.json` remain in the package. The main booklet need not repeat every check or every control image. Necessary plans and sections stay in the main presentation where they explain the proposal.

Default `make_figures.py` writes both PDFs and `drawings/presentation-index.json`. The main PDF is still named `a3-booklet.pdf`, so existing gallery/download routes remain usable. `figures/fig-08-node-location.png` is the new shared locator. A custom page design must preserve the named outputs and a truthful index with the mandatory sections in order. Page numbers are one-based physical PDF pages, including the cover.

`manifest.booklet.pages` still supports custom images. Main-document insertion anchors: `cover`, `idea` (before the whole-site plan), `whole_site`, `node_locator`, `views` (after the master-area plan), a selected node ID, `nodes`, `phasing`, `key_metrics`, `end`. Technical anchors: `brief`, `figures`, `day`. Put extra controls/checks at technical anchors rather than mixing them into the public story.

## What the checker can establish

G10 checks that indexed outputs exist, are current and match their recorded hashes. G12 verifies that the PDFs can be read, declared page counts match the PDFs, and required section ranges occur in order without overlap. These checks **do not** establish that a view is polished, a locator is clear, an image agrees with the geometry, or a city is adequately designed. Those are independent review questions. Keep the existing exception for entrants with no image tool; payment or a particular rendering service is never required.

The two organiser-listed existing packages retain the previous packaging rules. They opt into the new packaging if they regenerate with the current generator (which writes the new index); entrants cannot claim legacy status by backdating a manifest. The package names are in the organiser-maintained presentation policy. Existing submissions are not edited by this change.

## Freely designed replacement pages

To replace a default public section instead of merely adding pages, use `manifest.booklet.section_pages`, for example `{"node_locator": [{"path": "pages/my-locator.png", "title": "Where the three places belong"}]}`. Keys are `whole_site`, `node_locator`, `node:<selected ID>`, `phasing` and `key_metrics`. Each list can contain several PNG/JPG pages. The generator places them in the required reading sequence and records their page ranges automatically. All required information still applies; custom images cannot replace checked source geometry or controls. Image-model pages need provenance registration. Changing a custom page invalidates the drawing-input hash and requires a redraw. The automatic index does not prove the page actually contains the required content.
