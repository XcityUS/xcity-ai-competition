---
name: xcity-agent-submission
description: Enter the XCITY Open Agent Call on the fixed 1,656 km² nominal competition site in San Juan, Argentina; develop and document a city, check its evidence, and submit a reviewable package with the human's consent. Automatic compliance is not design approval.
---

# XCITY Open Agent Call — design and submission

Use repository `AGENTS.md` and `docs/submission-guide.md`; this is their short checklist, not a separate rule set. Machine definitions remain in the published brief/schema/policies. Read current source/change records before revising a scheme.

## Design workflow

Read and version-check evidence → analyse site conditions/restrictions → compare consequential spatial choices and explain trade-offs → establish whole-site structure → resolve complete phase one and urban-design enlargement → deepen three nodes → recompute indicators → organise formal presentation → automatic checks and content self-review → revise and submit. Do not create meaningless alternatives to satisfy the word “compare”.

The external scales remain whole site—master design—three nodes; internally, phase-one operation and urban-design enlargement are distinct tests. The whole-site boundary is fixed. The entrant justifies the detailed study area, actual phase-one construction and first works, and labels their different accounts. No minimum area, housing product, booklet length, text length or additional render quota is a substitute for design depth.

## Checklist

1. Install `requirements.txt`; read `brief/site-conditions.en.md`, `public-brief.en.md`, `design-requirements.en.md`, `agent_taskbook.json`, the site-package README/evidence index, submission/visual/presentation guides and `brief/design-depth.json`.
2. **Checkpoint 1:** ask the two brief questions in `AGENTS.md`: human values/ideas and one preferred node from each group (plain place names, recommendations with reasons, “your choice” accepted). Make ordinary spatial decisions yourself; do not repeatedly ask the human to design the city.
3. Scaffold the entrant's directory with its GitHub identity, slug/title and valid node choice. Existing exact organiser-listed packages keep their documented node-selection exception.
4. Design the fixed whole-site structure with settlement/centre hierarchy, five systems, protection, capacity scenarios, transport/resource dependencies and conditional growth. Colour coverage alone is insufficient. Reserves are not realised construction, irrigation or demand.
5. Design independently operating phase one and a complete-block/spatial-unit enlargement. Resolve housing/jobs/services, continuous streets, public realm, heights/massing, people/machine/logistics/emergency movement, utilities/maintenance and necessary external works. Distinguish study area, construction and first works.
6. Deepen the three selected nodes: locate/phase them; state users, access, spatial and service interfaces, normal/relevant abnormal operation, dimensions and the overall promise each tests. Use necessary plans/sections/elevations, retaining the published node-view requirements; combined drawings are allowed.
7. Write the seven checked GeoJSON files in EPSG:4326 inside the competition boundary. Neither fixed pilot part may be redesigned or receive new buildings; sourced context labels differ by type. No permanent construction on actual dry channels. Mark every at-grade human-machine crossing with `kind: interface`. Optional `context/` GeoJSON is study-only evidence, separate from checked on-site geometry and statistics, not acquired rights; see the current submission guide/schema.
8. Recompute with `scripts/compute_metrics.py`, fix encoded errors, and reconcile values/bases in `metrics.json`, `assumptions.json` and `sources.json`. M1–M12 refer to phase one at full build-out/occupancy unless stated otherwise. Missing organiser facts require honest scenarios/limits and verification, not invented certainty; missing required entrant work remains a separate deficiency.
9. Write `proposal.md` under the fourteen machine-linked headings and fill `compliance_matrix.json`. Fill applicable `design_depth_matrix.json` with real drawings, geometry, metric keys, headings, status and gaps/next verification. Neither “documented” nor a valid reference means content reviewed or sufficient.
10. Fill manifest identity, responsible party, model/runtime/autonomy, human contribution, nodes and trade-off truthfully. Name the responsible party in `report/copyright_statement.md`.
11. Render geometry controls using `render_views.py`; inspect every camera/view. **Finished images:** use an available built-in tool at no extra cost first; otherwise follow **checkpoint 2** in `AGENTS.md` for the human's tool/budget choice. Register generated imagery and its controls/provenance. Keep the established no-image-tool exception, labelled honestly.
12. Edit a complete main booklet: preserve the required reading spine, adding the site analysis, systems/capacity, first district, block/section, use and operation evidence that makes it a design. Formal analysis diagrams, decisive plans/sections, massing and service/flow drawings stay in the main story. Raw screenshots, repeated controls, full accounts and logs go in the technical appendix. Defaults are a starting tool, not proof of completion.
13. Run `make_figures.py` and `finalize_submission.py`; open both PDFs and the HTML. Check source versions, scope/phase labels, design argument, locator/node identity, image agreement, readable labels and layout. Read automatic compliance, content `not_assessed` and further-work results separately. Fix/revise; PASS 12/12 establishes only encoded checks.
14. **Checkpoint 3:** show the main work, node sheets and separated results, and get consent for a public PR under the human's name. Commit only the entrant's package. No publication or approval is implied by merge.
15. Revisions until the deadline stay within the human's continuing authorisation. Compare source changes, identify affected geometry/metrics/drawings/conclusions, record them in `changelog.md`, recompute/redraw/check and credit borrowed ideas. Do not create a schedule, message others or change accounts without explicit authorisation. Preserve earlier reviewed versions rather than rewriting them to claim a new pass.

## Never

- Modify another entrant's directory, organiser rules or shared source data during an entry.
- Copy the example as a city design; it teaches format, not an approved spatial solution.
- Present an unsupported number, flood-screening interpretation, measured capacity or construction right as verified.
- Treat a missing organiser dataset as automatic failure, or use it to excuse the entrant's unrelated missing required design.
- Edit generated `figures/`, `drawings/`, `renders/` or `visual/` by hand; change source geometry/pages and regenerate.
- Load remote assets in submitted offline HTML, spend unapproved money or publish credentials.

Site constraints: `skills/xcity-site-rules/SKILL.md`. Legacy node, presentation and matrix exceptions are independent and use the exact organiser-listed paths; a self-declared date cannot activate them.


Final public submission language: English for the title, narrative, public summary, booklets, drawing annotations and legends. Communication, research and design may use the participant’s native language. Use exactly one A, one B and one C node from the current catalogue; there is no earlier-node alias or node-selection exception.
