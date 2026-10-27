# Design-depth evidence and review / 设计深度证据与评审

The four levels in `brief/design-depth.json` are connected tests of the same city. They do not impose four fixed map extents. The urban-design enlargement may coincide with part of the phase-one master area; select it for the spatial question, not an area target. Keep the existing three-node group choice.

## Fill the matrix / 填写矩阵

Copy `templates/design_depth_matrix.json` (the scaffolder does this). Rows are `whole_site`, `overall_layout`, `urban_design`, `nodes`, and `node:<ID>` for every selected node. Each row links:

- `drawings`: package-relative formal drawings or PDF paths. Identify page/figure and its claim in the linked proposal heading; the checker checks files, not their visual content.
- `geometry`: package-relative submitted geometry used for that decision.
- `metrics`: exact keys present in `metrics.json`, with scope/phase/basis explained in the proposal.
- `explanation`: package-relative text path and an existing `## ` heading prefix.
- `status`: `documented` or `partial`, an entrant declaration; neither means approved.
- `gaps`: missing evidence/data/design, next verification and responsible role. Empty evidence lists need a disclosed gap. Do not invent missing data to clear a check.

Paths must remain inside the submission, without symlink escapes. A combined drawing can support several rows. There is no required page count. A matrix of links to uninformative pictures may pass reference checks and still fail content review. Partial disclosure allows honest uncertainty; it is not a guarantee of design acceptance. The published gates still apply to all other required files and metrics.

## Three independent results / 三类结果

1. **Automatic compliance / 自动检查**: G1–G12 check encoded file, geometry, number, version and reference rules. The matrix subsection says `references_consistent` or `failed`; it does not say design passed.
2. **Content review / 内容评审**: always `not_assessed` in generated reports. A reviewer must judge whether the whole-site structure is reasonable, phase one can stand alone, the enlargement creates streets/public life, and nodes support the overall promise. No automated content score is generated.
3. **Further work / 待深化**: reports repeat entrant-declared gaps and next verification/responsibility. `none_declared_not_verified` means no gaps were declared, not that none exist.

`self_check.json.design_depth_assessment` preserves all three; CLI output distinguishes them. Reviewers should add their separate signed/dated review rather than changing an entrant's machine check into an approval. Missing organiser information itself is not an automatic elimination reason.

The two exact organiser-listed legacy entries are unchanged and retain their previous evidence requirements. They opt in to the matrix only by adding it. Presentation-index opt-in is independent; regenerating a booklet alone does not silently demand an invented matrix.

## Review questions / 评审时要问

- 全场地：选址与保留的取舍有什么依据？城镇、五类系统、交通与资源如何连接？容量情景是否对应资源约束？
- 首期：后续停止时，居住、公服、岗位、物流和市政是否仍然完整？第一批工程和资金/资源依赖在哪里？
- 城市设计：街区与建筑高度、入口、步行、阴影、公共空间和服务界面是否共同支持日常生活？
- 节点：谁在何时使用？平剖面和运行情景能否解释效果图？对总体方案的哪个承诺进行了检验？

Use the annotated examples in `reference-examples.md` as method prompts, never as a preferred urban form.

## Matrix v2 / 矩阵第二版

New scaffolds use schema_version 2. Add decision (the actual spatial judgment) and scope.extent / scope.phase (the relevant boundary and construction phase or scenario). Classify each gap as organiser_data, professional_verification or entrant_design. Each row still needs actual drawing and geometry references: missing organiser information can be treated through declared assumptions, but does not waive entrant-authored spatial evidence. Only the two exact organiser-listed legacy paths may retain v1 matrices; new directories must use v2. The two listed legacy entries remain exempt until opt-in. Neither documented nor partial means approved.

新版填写 decision（空间判断）和 scope.extent／scope.phase（范围、阶段或容量情景），缺口区分主办资料、专业核实、参赛设计遗漏。资料缺失不等于免交设计证据。第一版仅对主办方列明的两份旧投稿兼容，新目录必须第二版，不能自行声明旧规则绕过检查。旧投稿主动升级后再复算。

For v2, GFA, coverage and FAR are clipped to master_area; outside-master building floor area is reported separately. Neither is automatically the actual phase-one quantity: declare the real construction phase and external necessary works separately. V1 retains its historical whole-package building numerator for reproducibility. V2 land_use is a mutually exclusive partition of master_area; overlaps/omissions above max(100 m², 0.01% of master area) are bookkeeping errors. This tolerance is not survey accuracy or engineering clearance. The five whole-site systems can overlap; do not apply the land_use partition rule to system weights.

第二版建筑量及密度仅统计 master_area 内几何，区外建筑量另报；不能自动称为实际首期建成量。第一版原口径保留。用地分区须覆盖深化范围且不重叠，账面容差不代表测绘精度。五类全域系统的复合关系另行表达。


### Independent design extents and dispersed nodes

The overall plan covers the entire issued site. Distinguish (1) whole-site planning, (2) actual first-phase construction and associated facilities, (3) the urban-design enlargement, (4) each selected node and (5) rendering camera frames. These are not interchangeable boundaries. The enlargement may contain some or none of the three selected nodes. Nodes need not adjoin, share one district, fall within master_area.geojson, or all be built in the first phase. State each node’s location, phase, users and role in the whole-site plan. First-phase completeness means independently operable living and production systems, with evidenced transport, power, water, communications and other relevant connections; it does not mandate a single contiguous footprint. Keep local land-use/FAR/GFA statistics separate from off-area facilities and their indicators. Do not force a compute campus beside housing or a heat user just to group nodes; justify buffers, cooling and any actual heat network. Camera crops illustrate a design; they do not define its scope.

C01 includes the **main entrance and arrival sequence**. All schemes must locate and explain main access, regional connections and people/freight separation in the overall plan even when C01 is not selected; full entrance-node detailing is required only if C01 is selected. The ten topics are optional deepening choices within three groups, not a licence to omit essential city systems from the overall plan. A01/B03/C02 is one valid selection, not a mandatory selection or adjacency model. Use a whole-site locator plus separate, consistently labelled detail insets for dispersed nodes; never crop an outlying node out or draw a fictitious direct link.

### A0 construction phasing map and programme

The A0 board must show a legible, labelled Phase 1/2/3 zoning map and a matching programme table. Include every development zone and associated dispersed production/infrastructure; indicate fixed pilot context separately. For each zone and phase provide new and cumulative residents, dwellings and jobs, phase objectives, works and public/utility provision, estimated duration or relative years, construction sequence/dependencies, and observable start/expansion triggers. Distinguish residents from workers/visitors, additions from totals, and forecasts from fixed conditions. Capacity ranges are allowed with assumptions. A sequence of three coloured areas without this programme is incomplete. Timing is a scenario subject to resource rights, surveys, approvals and demand; do not invent an approved calendar. Totals must reconcile by phase and with metrics.json (including phase-one residents). Areas, phases and district IDs must match geometry/phasing.geojson; separate facilities may share a phase without being adjacent.

Provide `phasing_programme.json` using `templates/phasing_programme.json`; reference the map and A0 board. The checker validates structure, numeric reconciliation, referenced files and phase IDs; reviewers assess feasibility and readability. Automatic checks do not approve the construction programme.


### Complete city scope — 2026-10-27 clarification

Design the complete city layout across all proposed construction phases, not only Phase 1. Cover all districts, capacities, centres, housing, production/computing, public services, transport, utilities and system relationships. Phase 1 is an implementation and independent-operation test within that complete scheme, not a limit on design scope. Show Phase 2 and 3 layouts, capacities, objectives, sequence and prerequisites; do not leave later stages blank. Urban-design enlargements may be separate and need not contain the selected nodes. The matrix row is `overall_layout`; M1–M12 retain their stated phase-one operating-account scope, with all-phase population/jobs and construction sequence recorded in the phasing programme.
