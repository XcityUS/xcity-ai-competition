# Public presentation booklet — required content and reading order

This is the human-facing presentation for the **AI Agent track**. It is separate from the fourteen-section design statement (`proposal.md`) and the technical appendix. Use your own graphic layout, page sizes, colours and page counts; keep the order and information below. A cover and a short thesis may come first. Use the existing proposal-heading mapping in `docs/presentation-guide.md` to carry the complete argument within this reading spine; it is not permission to omit site analysis, complete phase one or urban-design enlargement. Additional explanatory pages may sit within a section. Do not replace the whole-site plan with a city render or a sequence of local views.

## 1. Whole-site plan

Show the fixed full competition boundary (1,656 km² nominal), both fixed pilot areas, settlement/centre hierarchy, the five systems and their approximate scales, primary transport, resource/infrastructure relationships, protection/reserves and how development phases connect. Use a legend, scale, orientation and a short explanation of why the structure fits this site. A coloured land-allocation layer without these relationships is insufficient. Distinguish proposed, indicative, preliminary screening and fixed information. Capacity can be a justified scenario/range; reserve land is not automatically built area, irrigated land or realised demand.

## 2. Node location — whole site → master design area → three nodes

Locate the master design area on the whole-site plan, then locate all three selected nodes on a legible enlarged plan, using insets where needed. Distinguish the chosen master study area, phase-one construction and first works; do not imply nodes lie inside an extent when they do not. Use the **same node ID and title** here and on every node sheet. Show the streets, paths and service/system links between the nodes; explain their contribution to the wider city. Do not invent a direct connection where the design uses separate links through the wider network. Distant/combined nodes need legible insets or callouts, not a misleading crop. This locator is mandatory even if the whole-site plan already contains node symbols.

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
