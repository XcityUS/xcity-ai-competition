# Public presentation booklet — required content and reading order

This is the human-facing presentation for the **AI Agent track**. It is separate from the fourteen-section design statement (`proposal.md`) and the technical appendix. Use your own graphic layout, page sizes, colours and page counts; keep the order and information below. A cover and a short thesis may come first. Additional explanatory pages may sit within a section. Do not replace the whole-site plan with a city render or a sequence of local views.

## 1. Whole-site plan

Show the full 1,656 km² boundary, both fixed pilot areas, settlement/centre hierarchy, the five systems and their approximate scales, primary transport, resource/infrastructure relationships, protection/reserves and how development phases connect. Use a legend, scale, orientation and a short explanation of why the structure fits this site. A coloured land-allocation layer without these relationships is insufficient. Distinguish proposed, indicative and fixed information.

## 2. Node location — whole site → master design area → three nodes

Locate the master design area on the whole-site plan, then show all three selected nodes together on an enlarged master-area plan. Use the **same node ID and title** here and on every node sheet. Show the streets, paths and service/system links between the nodes; explain their contribution to the wider city. Do not invent a direct connection where the design uses separate links through the wider network. Distant/combined nodes need legible insets or callouts, not a misleading crop. This locator is mandatory even if the whole-site plan already contains node symbols.

## 3. Three node sections — repeat once for each manifest.nodes entry

**Heading:** `[node ID] · [official node topic] · [scheme-specific place name]`

**Location:** where it sits in the city/master area, its extent, access and relationship to the other nodes. Reuse the locator ID.

**Design explanation:** what people do here, how machines/services operate, and how this place tests the overall proposal.

**Presentation images:** at least one aerial and one eye-level view showing the proposed finished place. Finished concept images must agree with the geometry and be labelled as illustrations, not measurements or photographs of an existing city. Register AI images and their controls in `image_provenance.json`. If no image tool is available, keep the established massing-only exception, label it visibly and explain the limitation; do not rename a control render a finished image.

**Design evidence:** include the plan, section or movement diagram needed to explain this place. Detailed dimension checks, extra massing iterations and image/control comparisons belong in the technical appendix. A set of effect images without spatial design does not meet the requirement.

## 4. Phasing

Show what comes first and later, the facilities/services needed for each phase to operate, observable expansion triggers and key dependencies. Explain what happens if later phases are delayed. Use the same phase boundaries and numbers as the geometry and statement.

## 5. Key indicators

Present the main population/jobs, housing, land/density, water, energy and compute figures, with units, scope, phase and evidence tags. Distinguish whole-site and master-area totals. Put full calculations and the complete compliance matrix in the appendix; do not turn the main presentation into a gate report.

## Separate technical appendix

Include geometry/massing controls, additional sections and dimensions, land-use and resource accounts, image-to-control comparisons, requirement-to-evidence index, assumptions, sources, tool/model disclosure and automatic-check limitations. Keep the original controls in `renders/` and every checked figure on disk. Use `self_check.json` as the current machine report; do not copy an old PASS into the booklet as design approval.

Default commands produce `drawings/a3-booklet.pdf`, `drawings/a3-technical-appendix.pdf` and `drawings/presentation-index.json`. The index gives the page range of each required main section and the separate appendix. A custom layout must preserve those outputs and update the index truthfully. Presence/page-order checks do not assess the clarity or design quality of the pages.
